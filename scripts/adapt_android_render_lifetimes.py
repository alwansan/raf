"""Pinned original-source resource lifetime repair and honest Android offline Party boundary."""
import argparse
import hashlib
from pathlib import Path
import re

from scripts.instrument_android_runtime_operations import body_bounds

PINS={
'MyInput':('66517cd6df549991014002acdfd462e0d883ee76da81193920a31362385e9b6c',0),
'HapticAudio':('ac0ac86f62d05c774cb8b24cc8454df2b5356e50c6720395137df1730430fe9c',0),
'SoundManager':('fe5378c4375e9609c3f9bf9c35f51abecff266148f35588a5df2eb358a745d38',0),
'PersonController':('7889e538712b1dc992b6364248ed9c51a8b1dacc8ce2b5c19656e4d80105ce2e',0),
'GraphicsSettingsBox':('e1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300',0),
'Dx11FFT':('8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0',1),
'WavesRendererFFT':('e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9',3),
'PlayFabMultiplayerManager':('e71cd10249c028c7ae0b13e06e4cbe8826ec87d39a1c54778d6e288e97ca6087',0)}
DECL=r'(?P<indent>[ \t]*)TemporaryRenderTexture (?P<name>temporary\d*) = [\w.]+\.GetTemporary\(\);\n'


def protect_temporaries(text,expected):
    declaration=re.compile(DECL)
    groups=[];cursor=0;count=0
    while True:
        first=declaration.search(text,cursor)
        if not first: break
        rows=[first];end=first.end()
        while True:
            more=declaration.match(text,end)
            if not more: break
            rows.append(more);end=more.end()
        indent=first['indent'];names=[r['name'] for r in rows]
        cleanup=''.join(indent+n+'.Dispose();\n' for n in names)
        stop=text.find(cleanup,end)
        if stop<0: raise ValueError('Original temporary cleanup sequence changed')
        body=text[end:stop]
        replacement=''
        for depth,row in enumerate(rows):
            replacement+='\t'*depth+row[0]+indent+'\t'*depth+'try\n'+indent+'\t'*depth+'{\n'
        replacement+=''.join('\t'*len(rows)+line if line.strip() else line for line in body.splitlines(keepends=True))
        for depth in reversed(range(len(rows))):
            prefix=indent+'\t'*depth
            replacement+=prefix+'}\n'+prefix+'finally\n'+prefix+'{\n'+prefix+'\t'+names[depth]+'.Dispose();\n'+prefix+'}\n'
        groups.append((first.start(),stop+len(cleanup),replacement));cursor=stop+len(cleanup);count+=len(rows)
    if count!=expected: raise ValueError('Unexpected temporary acquisition coverage')
    for start,end,replacement in reversed(groups):text=text[:start]+replacement+text[end:]
    return text



def isolate_player_start_fmod(normalized):
    """Keep original player init order, but treat ONLY absent FMOD events as optional.

    Source SHA is authenticated in adapt(). Refuse unexpected assignments rather
    than using a broad catch across Start or setting world-completion flags.
    """
    declaration = re.compile(
        r"(?m)^\s*(?:public|private|protected|internal)\s+"
        r"(?:(?:static|virtual|override|sealed|new|async)\s+)*"
        r"void\s+Start\s*\([^;{}]*\)\s*\{"
    )
    matches = list(declaration.finditer(normalized))
    if len(matches) != 1:
        raise ValueError("Original player Start declaration drift")
    signature = matches[0].group(0).rsplit("{", 1)[0].strip()
    start, end = body_bounds(normalized, signature)
    body = normalized[start:end]
    create_calls = list(re.finditer(r"\bRuntimeManager\s*\.\s*CreateInstance\s*\(", body))
    settings = re.search(r"\bsettings\s*=", body)
    movement = re.search(r"\bactionMove\s*=", body)
    if (len(create_calls) != 2 or settings is None or movement is None
            or any(call.start() >= min(settings.start(), movement.start()) for call in create_calls)):
        raise ValueError("Original player audio-before-settings contract changed")

    original_lines = body.splitlines(keepends=True)
    changed = []
    guarded = 0
    assignment = re.compile(
        r"(?P<indent>[ \t]*)(?P<statement>(?:this\.)?[A-Za-z_]\w*"
        r"(?:\.[A-Za-z_]\w*)*\s*=\s*"
        r"(?:FMODUnity\.)?RuntimeManager\s*\.\s*CreateInstance"
        r"\s*\([^;\r\n]*\)\s*;)[ \t]*$"
    )
    for line in original_lines:
        without_newline = line.rstrip("\r\n")
        if "RuntimeManager.CreateInstance(" not in without_newline:
            changed.append(line)
            continue
        match = assignment.fullmatch(without_newline)
        if match is None:
            raise ValueError("Unrecognized player FMOD event assignment")
        indent = match["indent"]
        # Keep the original statement itself unchanged. No fallback event
        # objects, fake FMOD events, or swapped assignment target.
        changed.append(
            indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n" +
            indent + "try\n" + indent + "{\n" +
            indent + "#endif\n" +
            line +
            indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n" +
            indent + "}\n" +
            indent + "catch (FMODUnity.EventNotFoundException __raftMissingPlayerSound)\n" +
            indent + "{\n" +
            indent + '    RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("audio", "player_start_missing_fmod_event",\n' +
            indent + "        __raftMissingPlayerSound.ToString(), true);\n" +
            indent + "}\n" + indent + "#endif\n"
        )
        guarded += 1
    if guarded != 2:
        raise ValueError("Original player FMOD statement count drift")
    result = normalized[:start] + "".join(changed) + normalized[end:]
    # The extra statements are exclusively Android-scoped. Removing the exact
    # authored guards must reproduce original source byte-for-byte.
    if result.count("player_start_missing_fmod_event") != 2:
        raise ValueError("Missing explicit diagnostic on isolated original player events")
    return result


def adapt(stem,text):
    digest,expected=PINS[stem]
    normalized=text.replace('\r\n','\n')
    if hashlib.sha256(normalized.encode()).hexdigest()!=digest: raise ValueError('Unknown original source revision: '+stem)
    if expected: normalized=protect_temporaries(normalized,expected)
    elif stem == 'MyInput':
        marker='public class MyInput : MonoBehaviour'
        if normalized.count(marker)!=1 or tuple(normalized.count('Input.'+name+'(') for name in ('GetKey', 'GetKeyDown', 'GetKeyUp'))!=(4,2,2):
            raise ValueError('Original legacy key input contract changed')
        alias='''#if UNITY_ANDROID && !UNITY_EDITOR
using RaftAndroidLegacyInput = RaftAndroid.Platform.AndroidRightTouchPointer;
#else
using RaftAndroidLegacyInput = UnityEngine.Input;
#endif

'''
        normalized=normalized.replace(marker,alias+marker,1)
        normalized=re.sub(r'\bInput\.(GetKey(?:Down|Up)?)\(',r'RaftAndroidLegacyInput.\1(',normalized)
    elif stem == 'HapticAudio':
        if normalized.count('File.ReadAllBytes(')!=1: raise ValueError('Original haptic reader changed')
        normalized=normalized.replace('File.ReadAllBytes(', 'RaftAndroid.Platform.AndroidStreamingAssets.ReadAllBytes(',1)
    elif stem == 'PersonController':
        normalized = isolate_player_start_fmod(normalized)
    elif stem == 'SoundManager':
        # Original scene JoinGame is broadcast before WorldHasBeenRecieved.
        # Missing FMOD events must remain visible, but cannot terminate this
        # unrelated gameplay/world handoff. Do not swallow other exceptions,
        # spoof event success, or change original local host state.
        # Use the same exact declaration grammar as the read-only probe.
        declaration = re.compile(
            r"(?m)^\s*(?:public|private|protected|internal)\s+"
            r"(?:(?:static|virtual|override|sealed|new|async)\s+)*"
            r"(?P<return>[\w<>\[\],.?]+)\s+OnSceneEvent"
            r"\s*\([^;{}]*\)\s*\{"
        )
        declarations = list(declaration.finditer(normalized))
        if len(declarations) != 1:
            raise ValueError('Ambiguous original audio scene callback')
        signature = declarations[0].group(0).rsplit('{', 1)[0].strip()
        start, end = body_bounds(normalized, signature)
        body = normalized[start:end]
        if 'StudioEventEmitter' not in body or not re.search(r'\bPlay\s*\(', body):
            raise ValueError('Original FMOD scene callback contract changed')
        opening = '''\n#if UNITY_ANDROID && !UNITY_EDITOR
        try
        {
#endif
'''
        closing = '''\n#if UNITY_ANDROID && !UNITY_EDITOR
        }
        catch (FMODUnity.EventNotFoundException __raftMissingSceneSound)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("audio", "scene_event_missing_fmod_event",
                __raftMissingSceneSound.ToString(), true);
        }
#endif
'''
        normalized = normalized[:start] + opening + body + closing + normalized[end:]
        if normalized[:start] + normalized[start:].replace(opening, '', 1).replace(closing, '', 1) != text.replace('\r\n', '\n'):
            raise ValueError('Original scene callback body changed')
    elif stem == 'GraphicsSettingsBox':
        signature='\tpublic void ApplyCurrentResolutionAndFullscreenMode()\n\t{\n'
        if normalized.count(signature)!=1: raise ValueError('Ambiguous original resolution setter')
        normalized=normalized.replace(signature,signature+"""#if UNITY_ANDROID && !UNITY_EDITOR
        // Android owns the landscape surface. Desktop display modes may be
        // portrait and must not replace the initial Android render dimensions.
        return;
#endif
""",1)
    else:
        signature='\t\tprivate void InitializeImpl()\n\t\t{\n'
        if normalized.count(signature)!=1: raise ValueError('Ambiguous original Party initialization boundary')
        normalized=normalized.replace(signature,signature+'''#if UNITY_ANDROID && !UNITY_EDITOR
            // Solo adapter: no Windows Party backend or fabricated remote initialization.
            enabled = false;
            return;
#endif
''',1)
    return normalized.replace('\n','\r\n') if '\r\n' in text else normalized


def apply(root,backup):
    if backup.resolve().is_relative_to(root.resolve()):raise ValueError('Backup must be outside original source/project')
    plan=[]
    for stem in PINS:
        candidates=[p for p in root.rglob(stem+'.cs') if 'Assembly-CSharp' in str(p) or not (root/'Assets').exists()]
        if len(candidates)!=1:raise ValueError('Original source identity ambiguous: '+stem)
        p=candidates[0];raw=p.read_bytes();text=raw.decode('utf-8-sig');changed=adapt(stem,text)
        meta=Path(str(p)+'.meta');meta_bytes=meta.read_bytes() if meta.exists() else None
        plan.append((p,raw,(b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+changed.encode(),meta,meta_bytes))
    backup.mkdir(parents=True,exist_ok=False)
    for p,raw,changed,meta,meta_bytes in plan:
        q=backup/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
        if meta_bytes is not None:Path(str(q)+'.meta').write_bytes(meta_bytes)
    try:
        for p,raw,changed,meta,meta_bytes in plan:
            p.write_bytes(changed)
            if meta_bytes is not None and meta.read_bytes()!=meta_bytes:raise ValueError('Original source GUID changed')
    except BaseException:
        for p,raw,changed,meta,meta_bytes in plan:p.write_bytes(raw)
        raise
    print('RAFT_ANDROID_RENDER_LIFETIMES temporaryResources=4 exceptionSafe=true androidDesktopResolutionBypassed=true windowsPartyInitializationBypassed=true originalMetasUnchanged=true')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--backup',type=Path,required=True);args=p.parse_args();apply(args.source,args.backup)
