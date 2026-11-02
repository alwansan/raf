"""Create private original-source compile and RPC/identity test projects in CI."""
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
import shutil

from scripts.adapt_android_offline_startup import PINS, adapt
from scripts.adapt_original_save_paths import adapt as adapt_paths
from scripts.instrument_android_runtime_operations import instrument


def method(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 0
    for pos in range(opening, len(text)):
        if text[pos] == '{': depth += 1
        if text[pos] == '}': depth -= 1
        if depth == 0:
            return text[start:pos + 1]
    raise ValueError('Unclosed original method')


def prepare(source, managed, runtime, output):
    changed = {}
    for name in PINS:
        matches = list(source.rglob(name + '.cs'))
        if len(matches) != 1:
            raise ValueError('Require unique original source: ' + name)
        path = matches[0]
        text = path.read_text(encoding='utf-8-sig')
        if name == 'SaveAndLoad': text = adapt_paths(text)
        changed[name] = (path, adapt(name, text))
    output.mkdir(parents=True, exist_ok=True)
    traces = json.loads(Path('config/runtime-operation-traces.json').read_text())
    for name, (path, text) in changed.items():
        path.write_text(instrument(name, text, traces) if name in traces['sources'] else text)
    refs = '\n'.join('<Reference Include="' + html.escape(p.stem) + '"><HintPath>' + html.escape(str(p.resolve())) + '</HintPath><Private>false</Private></Reference>'
                     for p in sorted(managed.glob('*.dll')) if p.name != 'Assembly-CSharp.dll')
    # This mirrors the established original managed compatibility diagnostic.
    project = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion><DefineConstants>UNITY_ANDROID;UNITY_5_3_OR_NEWER</DefineConstants><GenerateAssemblyInfo>false</GenerateAssemblyInfo><AllowUnsafeBlocks>true</AllowUnsafeBlocks><Nullable>disable</Nullable><NoWarn>0168;0649;0618;0672;SYSLIB0011</NoWarn></PropertyGroup><ItemGroup>' + refs + '</ItemGroup></Project>'
    for name in ('LocalPlayerIdentity.cs', 'LocalProfileStore.cs', 'AndroidTestDiagnostics.cs', 'AndroidTouchGamepadOverlay.cs', 'PersistentDiagnosticLog.cs', 'AndroidRuntimeLog.cs'):
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
    save_start = save_source.index(save_signature)
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
    print('RAFT_OFFLINE_PRIVATE_PREPARE originalSources=' + str(len(changed)) + ' sourceBodiesPublished=false nativeCallsExecuted=false')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('source', 'managed', 'runtime', 'output'): p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    prepare(args.source, args.managed, args.runtime, args.output)

