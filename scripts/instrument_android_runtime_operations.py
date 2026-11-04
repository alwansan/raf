"""Instrument pinned operation boundaries; never log per-frame game loops or payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

LITERALS = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


def executable_only(text):
    """Mask C# comments/strings/char literals without moving original offsets.

    This is a deliberately bounded C#9 lexical check, not a full parser.
    Original bytes and SHA-pinned bodies remain untouched for instrumentation.
    """
    return LITERALS.sub(
        lambda match: ''.join(ch if ch in '\r\n' else ' ' for ch in match.group()),
        text,
    )


def body_bounds(text, signature):
    executable = executable_only(text)
    matches = list(re.finditer(re.escape(signature), executable))
    if len(matches) != 1:
        raise ValueError('Operation signature must be unique in executable source: ' + signature)

    # A declaration followed by a semicolon, arrow expression or another method
    # is NOT a block body. Never steal the next method's opening brace.
    after_signature = matches[0].end()
    opener = re.match(r'\s*\{', executable[after_signature:])
    if opener is None:
        raise ValueError('Operation signature must immediately precede a block body: ' + signature)
    opening = after_signature + opener.end() - 1

    depth = 1
    for i in range(opening + 1, len(executable)):
        if executable[i] == '{':
            depth += 1
        elif executable[i] == '}':
            depth -= 1
            if depth == 0:
                return opening + 1, i
    raise ValueError('Unbalanced original operation')


def wrap(text, signature, area, detail='""'):
    start, end = body_bounds(text, signature)
    original = text[start:end]
    if '__raftOperation' in executable_only(original):
        raise ValueError('Refuse duplicate operation instrumentation')
    name = signature.split('(')[0].split()[-1]
    prefix = '\n#if UNITY_ANDROID && !UNITY_EDITOR\n' + (
        'long __raftOperationStart = RaftAndroid.Diagnostics.AndroidRuntimeLog.BeginOperation(' +
        json.dumps(area) + ', ' + json.dumps(name) + ', ' + detail + ');\n' +
        'bool __raftOperationFailed = false;\ntry {\n#endif\n')
    suffix = '\n#if UNITY_ANDROID && !UNITY_EDITOR\n' + (
        '} catch (System.Exception __raftOperationError) {\n' +
        '__raftOperationFailed = true;\nRaftAndroid.Diagnostics.AndroidRuntimeLog.Write(' +
        json.dumps(area) + ', ' + json.dumps(name + '.exception') + ', __raftOperationError.ToString(), true);\nthrow;\n' +
        '} finally { RaftAndroid.Diagnostics.AndroidRuntimeLog.EndOperation(' +
        json.dumps(area) + ', ' + json.dumps(name) + ', __raftOperationStart, __raftOperationFailed); }\n#endif\n')
    result = text[:start] + prefix + original + suffix + text[end:]
    if result[:start] + result[start:].replace(prefix, '', 1).replace(suffix, '', 1) != text:
        raise ValueError('Original body preservation failed')
    return result


# The APK86 stack proves the Windows-only Steam stats upload is reached from
# SaveGame after the real local scene load. Keep every original save/RGD call,
# but do not load steam_api64 for the Android offline profile.
def guard_android_local_savegame_stats(text):
    signature = 'public void SaveGame(bool sendRemoteMessage)'
    start, end = body_bounds(text, signature)
    executable = executable_only(text)
    call = re.compile(r'\bSteamUserStats\s*\.\s*StoreStats\s*\(\s*\)\s*;')
    found = list(call.finditer(executable[start:end]))
    if len(found) != 1:
        raise ValueError('Require exactly one executable original SaveGame StoreStats call')
    before, after = start + found[0].start(), start + found[0].end()
    statement = text[before:after]
    guard = 'if (!RaftAndroid.Platform.LocalPlayerIdentity.Enabled) { ' + statement + ' }'
    result = text[:before] + guard + text[after:]
    if result.replace(guard, statement, 1) != text:
        raise ValueError('SaveGame Steam stats isolation changed original source')
    return result



def wrap_original_world_callback(text, method_name, expected_body_sha, area):
    """Wrap an authenticated original void callback without changing its body.

    Do not wrap IEnumerator WorldHasBeenLoaded: a C# yield method cannot
    legally place its yield instructions inside a catch-bearing try block.
    """
    from scripts.b07_probe_original_world_callbacks import (
        fingerprint, method_body, _executable_positions
    )
    return_type, body = method_body(text, method_name)
    if return_type != 'void' or fingerprint(body) != expected_body_sha:
        raise ValueError('Unrecognized original GameManager callback body')
    executable = _executable_positions(text)
    declaration = re.compile(
        r'(?m)^\s*(?:public|private|protected|internal)\s+'
        r'(?:(?:static|virtual|override|sealed|new|async)\s+)*'
        r'void\s+' + re.escape(method_name) + r'\s*\([^;{}]*\)\s*\{'
    )
    matches = list(declaration.finditer(executable))
    if len(matches) != 1:
        raise ValueError('Ambiguous original GameManager callback declaration')
    signature = text[matches[0].start():matches[0].end() - 1].strip()
    return wrap(text, signature, area)



def instrument(name, text, manifest):
    row = manifest['sources'][name]
    digest = hashlib.sha256(text.replace('\r\n', '\n').encode()).hexdigest()
    if digest != row['sha256']:
        raise ValueError('Unknown adapted original revision: ' + name)
    result = guard_android_local_savegame_stats(text) if name == 'SaveAndLoad' else text
    for method in row['methods']:
        if name == 'GameManager' and method.get('name') == 'OnWorldRecieved':
            result = wrap_original_world_callback(result, method['name'], method['body_sha256'], row['area'])
        else:
            result = wrap(result, method['signature'], row['area'], method.get('detail', '""'))
    return result


def apply(project, backup, manifest, write=False):
    if backup.resolve().is_relative_to(project.resolve()):
        raise ValueError('Backup must be outside imported project')
    plans = []
    for name in manifest['sources']:
        matches = [p for p in (project / 'Assets').rglob(name + '.cs') if 'Assembly-CSharp' in p.parts]
        if len(matches) != 1: raise ValueError('Original operation source is ambiguous')
        path = matches[0]
        meta = path.with_suffix('.cs.meta')
        if path.is_symlink() or meta.is_symlink(): raise ValueError('No linked operation sources')
        raw = path.read_bytes()
        text = instrument(name, raw.decode('utf-8-sig'), manifest)
        data = (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.encode()
        if (backup / path.name).exists() or (backup / meta.name).exists():
            raise ValueError('Original operation backup already exists')
        plans.append((path, meta, raw, meta.read_bytes() if meta.exists() else None, data))
    if write:
        backup.mkdir(parents=True, exist_ok=True)
        for p,m,r,metadata,d in plans:
            shutil.copy2(p, backup / p.name)
            if metadata is not None: shutil.copy2(m, backup / m.name)
        try:
            for p,m,r,metadata,d in plans:
                p.write_bytes(d)
                if p.read_bytes() != d or (m.read_bytes() if m.exists() else None) != metadata:
                    raise ValueError('Installed operation/meta changed')
        except Exception:
            for p,m,r,metadata,d in plans: p.write_bytes(r)
            raise
    return dict(applied=write, sourceFiles=len(plans), operations=sum(len(x['methods']) for x in manifest['sources'].values()), originalMetasUnchanged=True, perFrameLoopsInstrumented=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('project', 'backup', 'manifest'): p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    print('RAFT_RUNTIME_OPERATION_TRACING ' + json.dumps(apply(a.project,a.backup,json.loads(a.manifest.read_text()),a.apply),sort_keys=True))
