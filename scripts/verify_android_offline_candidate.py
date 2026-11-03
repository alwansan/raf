"""Create private original-source compile and RPC/identity test projects in CI."""
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
import shutil

from scripts.adapt_android_offline_startup import PINS, adapt, fingerprint
from scripts.adapt_original_save_paths import adapt as adapt_paths
from scripts.instrument_android_runtime_operations import instrument


def _csharp_code_mask(text):
    """Mask comments and quoted literals, retaining exact C# source offsets."""
    code = list(text)
    i = 0
    while i < len(text):
        if text.startswith('//', i):
            end = text.find('\n', i)
            if end < 0:
                end = len(text)
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end < 0:
                raise ValueError('Unclosed C# block comment')
            end += 2
        elif text[i] in ('"', "'"):
            quote = text[i]
            verbatim = quote == '"' and (
                (i > 0 and text[i - 1] == '@') or text[max(0, i - 2):i] == '@$'
            )
            end = i + 1
            while end < len(text):
                if verbatim and text.startswith('""', end):
                    end += 2
                elif not verbatim and text[end] == '\\':
                    end += 2
                elif text[end] == quote:
                    end += 1
                    break
                else:
                    end += 1
            else:
                raise ValueError('Unclosed C# quoted literal')
        else:
            i += 1
            continue
        for offset in range(i, end):
            code[offset] = ' '
        i = end
    return ''.join(code)


def _original_method_start(code, signature):
    start = code.find(signature)
    if start < 0:
        raise ValueError('Missing original method signature: ' + signature)
    if code.find(signature, start + len(signature)) >= 0:
        raise ValueError('Ambiguous original method signature: ' + signature)
    return start


def method(text, signature):
    code = _csharp_code_mask(text)
    start = _original_method_start(code, signature)
    opening = code.find('{', start + len(signature))
    semicolon = code.find(';', start + len(signature))
    if opening < 0 or (semicolon >= 0 and semicolon < opening):
        raise ValueError('Original method has no body: ' + signature)
    depth = 0
    for pos in range(opening, len(code)):
        if code[pos] == '{':
            depth += 1
        elif code[pos] == '}':
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise ValueError('Unclosed original method: ' + signature)


def select_original_source(source: Path, name: str, expected_sha256: str):
    """Choose the unique SHA-pinned original source, ignoring SDK homonyms."""
    found = []
    for path in source.rglob(name + '.cs'):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            original = path.read_text(encoding='utf-8-sig')
        except UnicodeError:
            continue
        if fingerprint(original) == expected_sha256:
            found.append((path, original))
    if len(found) != 1:
        raise ValueError('Require exactly one SHA-pinned original source: ' + name)
    return found[0]


def install_adapted_originals(changed, traces):
    """Preflight all adapted originals before altering any private ILSpy C#.

    Undo attempted original-source writes if I/O fails mid-install. This does
    not promise atomic recovery against concurrent filesystem mutations or
    failures in later harness-generation steps.
    """
    plans = []
    for name, (path, text) in changed.items():
        if path.is_symlink() or not path.is_file():
            raise ValueError('Require regular original source before instrumentation: ' + name)
        before = path.read_bytes()
        if fingerprint(before.decode('utf-8-sig')) != PINS[name]:
            raise ValueError('Original source changed after SHA selection: ' + name)
        result = instrument(name, text, traces) if name in traces['sources'] else text
        plans.append((path, before, result.encode('utf-8')))

    attempted = []
    try:
        for path, before, result in plans:
            attempted.append((path, before))
            path.write_bytes(result)
            if path.read_bytes() != result:
                raise ValueError('Private adapted source write mismatch: ' + path.name)
    except Exception:
        for path, before in reversed(attempted):
            path.write_bytes(before)
        raise


def prepare(source, managed, runtime, output):
    changed = {}
    for name in PINS:
        path, text = select_original_source(source, name, PINS[name])
        if name == 'SaveAndLoad': text = adapt_paths(text)
        changed[name] = (path, adapt(name, text))
    traces = json.loads(Path('config/runtime-operation-traces.json').read_text())
    output.mkdir(parents=True, exist_ok=True)
    refs = '\n'.join('<Reference Include="' + html.escape(p.stem) + '"><HintPath>' + html.escape(str(p.resolve())) + '</HintPath><Private>false</Private></Reference>'
                     for p in sorted(managed.glob('*.dll')) if p.name != 'Assembly-CSharp.dll')
    # This mirrors the established original managed compatibility diagnostic.
    project = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion><DefineConstants>UNITY_ANDROID;UNITY_5_3_OR_NEWER</DefineConstants><GenerateAssemblyInfo>false</GenerateAssemblyInfo><AllowUnsafeBlocks>true</AllowUnsafeBlocks><Nullable>disable</Nullable><NoWarn>0168;0649;0618;0672;SYSLIB0011</NoWarn></PropertyGroup><ItemGroup>' + refs + '</ItemGroup></Project>'
    for name in ('AndroidStreamingAssets.cs', 'TouchPointerGesture.cs', 'TouchPointerButtons.cs', 'AndroidTouchPointer.cs', 'AndroidTouchUiPanel.cs', 'LocalPlayerIdentity.cs', 'LocalProfileStore.cs', 'AndroidTestDiagnostics.cs', 'AndroidTouchGamepadOverlay.cs', 'PersistentDiagnosticLog.cs', 'AndroidRuntimeLog.cs'):
        shutil.copy2(runtime / name, source / ('RaftAndroid-' + name))
    (source / 'Candidate.csproj').write_text(project)
    harness = output / 'harness'
    harness.mkdir()
    for name in ('LocalPlayerIdentity.cs', 'LocalProfileStore.cs'):
        shutil.copy2(runtime / name, harness / name)
    network = changed['Raft_Network'][1]
    rpc = method(network, 'public void RPC(Message message,')
    send = method(network, 'public void SendP2P(Network_UserId steamID, Message message,')
    common = '''using System; using System.Collections.Generic; using System.IO;
enum Target { All, Other } enum EP2PSend { k_EP2PSendReliable, Unreliable } enum NetworkChannel { Session }
enum DeliveryOption { Guaranteed, BestEffort } enum PlayFabMultiplayerManagerState { ConnectedToNetwork }
class Message {} class EntityKey { public ulong Id; } class PlayFabPlayer { public EntityKey EntityKey; }
class PlayFabMultiplayerManager { public PlayFabMultiplayerManagerState State; public IList<PlayFabPlayer> RemotePlayers;
 public static PlayFabMultiplayerManager Get() { throw new Exception("Cloud transport was accessed"); } }
class NetworkUnderTest {
 public ulong localSteamID = 123; public ulong LocalSteamID => localSteamID; public int LocalDeliveries;
 void ParseLocalMessage(Message message, ulong id) { if (id != localSteamID) throw new Exception("Local identity mismatch"); LocalDeliveries++; }
 void SendP2PInternal(Message message, IEnumerable<PlayFabPlayer> players, DeliveryOption option) { throw new Exception("Remote send attempted"); }
'''
    # Use ulong here: original Network_UserId defines this exact implicit ID boundary.
    methods = (rpc + '\n' + send).replace('Network_UserId', 'ulong')
    save_source = changed['SaveAndLoad'][1]
    save_signature = 'private void Save(string filename, RGD raftgamedata)'
    save_start = _original_method_start(_csharp_code_mask(save_source), save_signature)
    attributes = re.findall(r'\[Conditional\("[^"]+"\)\]', save_source[max(0,save_start-200):save_start])
    if len(attributes) != 2 or '[Conditional("UNITY_ANDROID")]' not in attributes:
        raise ValueError('Original save call is not enabled for Android')
    save_harness = '''
namespace SaveHarness {
 class RGD {} class FileStream { public void Close() { FileManager.Closed++; } }
 class FileManager { public static int Calls, Closed, Serialized; public static string Name;
 public static FileStream CreateFile(string name) { Calls++; Name = name; return new FileStream(); } }
 class BinaryFormatter { public void Serialize(FileStream file, RGD value) { FileManager.Serialized++; } }
 class OriginalSaveUnderTest {
''' + '\n'.join(attributes).replace('[Conditional(', '[System.Diagnostics.Conditional(') + '\n' + method(save_source, save_signature) + '''
 public void Execute() { Save("fixture-world", new RGD()); }
 }
 public static class SaveCallTest { public static void Run() {
  new OriginalSaveUnderTest().Execute();
  if (FileManager.Calls != 1 || FileManager.Serialized != 1 || FileManager.Closed != 1 || FileManager.Name != "fixture-world.rgd")
   throw new System.Exception("Android compiler omitted original RGD save call");
 } }
}
'''
    checks = '''}
class Program { static void Main() {
 if (!RaftAndroid.Platform.LocalPlayerIdentity.Enabled) throw new Exception("Android branch not enabled");
 SaveHarness.SaveCallTest.Run();
 var n = new NetworkUnderTest(); var m = new Message();
 n.RPC(m, Target.All, EP2PSend.k_EP2PSendReliable, NetworkChannel.Session);
 if (n.LocalDeliveries != 1) throw new Exception("All RPC lost local delivery");
 n.RPC(m, Target.Other, EP2PSend.k_EP2PSendReliable, NetworkChannel.Session);
 if (n.LocalDeliveries != 1) throw new Exception("Other RPC incorrectly delivered locally");
 n.SendP2P(n.LocalSteamID, m, EP2PSend.k_EP2PSendReliable, NetworkChannel.Session);
 if (n.LocalDeliveries != 2) throw new Exception("Direct local delivery lost");
 n.SendP2P(999, m, EP2PSend.k_EP2PSendReliable, NetworkChannel.Session);
 if (n.LocalDeliveries != 2) throw new Exception("Remote target incorrectly delivered locally");
 string root = Path.Combine(Path.GetTempPath(), "raft-identity-" + Guid.NewGuid().ToString("N"));
 try {
  ulong a = RaftAndroid.Platform.LocalPlayerIdentity.GetOrCreate(root);
  ulong b = RaftAndroid.Platform.LocalPlayerIdentity.GetOrCreate(root);
  if (a == 0 || a > long.MaxValue || a != b) throw new Exception("Stable save identity failed");
  string profile = new RaftAndroid.Platform.LocalProfileStore(root).GetOrCreateProfileId();
  if (a != RaftAndroid.Platform.LocalPlayerIdentity.FromProfile(profile)) throw new Exception("Profile derivation changed");
  string[] files = Directory.GetFiles(root, "profile.id", SearchOption.AllDirectories);
  File.WriteAllText(files[0], "corrupt");
  bool refused = false; try { RaftAndroid.Platform.LocalPlayerIdentity.GetOrCreate(root); } catch (InvalidDataException) { refused = true; }
  if (!refused || File.ReadAllText(files[0]) != "corrupt") throw new Exception("Corrupt identity replaced");
 } finally { Directory.Delete(root, true); }
 Console.WriteLine("RAFT_OFFLINE_ORIGINAL_RPC_TEST localAll=1 localOther=0 directLocal=1 remoteNoCloud=true stableSaveIdentity=true corruptProfilePreserved=true unityRuntimeVerified=false");
} }
'''
    (harness / 'Program.cs').write_text(common + methods + checks + save_harness)
    (harness / 'Harness.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion><DefineConstants>UNITY_ANDROID</DefineConstants></PropertyGroup></Project>')
    # Every private managed fixture and method must be valid before any
    # SHA-pinned original C# is mutated. Failed source installation rolls back.
    install_adapted_originals(changed, traces)
    print('RAFT_OFFLINE_PRIVATE_PREPARE originalSources=' + str(len(changed)) + ' sourceBodiesPublished=false nativeCallsExecuted=false')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('source', 'managed', 'runtime', 'output'): p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    prepare(args.source, args.managed, args.runtime, args.output)

