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
    # Only the authenticated original Save method receives the extra
    # read-only, post-body snapshot. Original FileManager may return normally
    # from a caught File.Create failure; EndOperation(exceptionEscaped=false)
    # alone cannot prove that a file was created or made durable. Observe the
    # exact original filename argument, without printing it or reading bytes.
    # A missing argument-path file is NOT proof the game save failed: it is
    # a bounded diagnostic to interpret alongside the original runtime logs.
    after_save_snapshot = ''
    if signature == 'private void Save(string filename, RGD raftgamedata)' and area == 'save':
        after_save_snapshot = (
            '\ntry {\n'
            'bool __raftArgumentFileExists = System.IO.File.Exists(filename);\n'
            'string __raftArgumentLengthClass = __raftArgumentFileExists '
            '? (new System.IO.FileInfo(filename).Length == 0L ? "zero" : "nonzero") '
            ': "not_checked";\n'
            'try { RaftAndroid.Diagnostics.AndroidRuntimeLog.Write('
            '"save", "Save.argumentFileSnapshot", '
            '"exists_at_filename_argument=" + __raftArgumentFileExists '
            '+ "; length_class=" + __raftArgumentLengthClass '
            '+ "; durable_RGD_unverified=true", true); } '
            'catch (System.Exception) { }\n'
            '} catch (System.Exception __raftFileProbeError) {\n'
            'try { RaftAndroid.Diagnostics.AndroidRuntimeLog.Write('
            '"save", "Save.argumentFileSnapshot.unavailable", '
            '"probe_error_type=" + __raftFileProbeError.GetType().Name '
            '+ "; durable_RGD_unverified=true", true); } '
            'catch (System.Exception) { }\n'
            '}\n'
        )
    suffix = '\n#if UNITY_ANDROID && !UNITY_EDITOR\n' + (
        '} catch (System.Exception __raftOperationError) {\n' +
        '__raftOperationFailed = true;\nRaftAndroid.Diagnostics.AndroidRuntimeLog.Write(' +
        json.dumps(area) + ', ' + json.dumps(name + '.exception') + ', __raftOperationError.ToString(), true);\nthrow;\n' +
        '} finally { ' + after_save_snapshot +
        'RaftAndroid.Diagnostics.AndroidRuntimeLog.EndOperation(' +
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




def trace_caught_original_load_error(text):
    """Log the original Load<T> catch boundary, without changing its handling.

    The outer operation wrapper only observes uncaught exceptions; genuine
    original Load<T> contains one internal catch. Record that catch separately
    so a returned default cannot be mistaken for a clean load on the phone.
    """
    signature = 'public static T Load<T>(string filename)'
    begin, end = body_bounds(text, signature)
    code = executable_only(text[begin:end])
    if len(re.findall(r'\bDeserialize\s*\(', code)) != 1:
        raise ValueError('Require one authenticated Load<T> deserialization call')
    catches = list(re.finditer(r'\bcatch\s*(?:\([^{}]*\))?\s*\{', code))
    if len(catches) != 1:
        raise ValueError('Require one original Load<T> catch handler')
    if 'Load.caughtException' in text:
        raise ValueError('Refuse duplicate Load<T> caught exception diagnostic')
    insertion = begin + catches[0].end()
    snippet = ('\n#if UNITY_ANDROID && !UNITY_EDITOR\n'
               'RaftAndroid.Diagnostics.AndroidRuntimeLog.Write('
               '"save", "Load.caughtException", '
               '"Original Load<T> entered its error handler; no world/save success implied", true);'
               '\n#endif\n')
    result = text[:insertion] + snippet + text[insertion:]
    if result.replace(snippet, '', 1) != text:
        raise ValueError('Original Load<T> error handler modified outside diagnostic')
    return result


def trace_original_world_completion(text):
    """Observe the genuine original coroutine assignment, never set a ready flag.

    Called only after the full offline-adapted Raft_Network SHA gate. The
    preceding B07 first-MoveNext trace does not prove this assignment ran.
    A scoped statement block is necessary: a bare log after an unbraced
    conditional could falsely report completion on the opposite branch.
    """
    from scripts.b07_probe_original_world_callbacks import method_body, _executable_positions
    from scripts.b07_world_coroutine_trace import ENTRY

    return_type, body = method_body(text, 'WorldHasBeenLoaded')
    if return_type != 'IEnumerator' or not body.startswith(ENTRY):
        raise ValueError('Expected B07 authenticated original coroutine entry')
    if 'WorldHasBeenLoaded.originalCompletionAssigned' in text:
        raise ValueError('Refuse duplicate world completion diagnostic')
    executable = _executable_positions(body)
    calls = list(re.finditer(r'\bHelper\s*\.\s*BroadCastToScene\s*\(', executable))
    assignments = list(re.finditer(r'\bWorldHasBeenRecieved\s*=\s*true\s*;', executable))
    if len(assignments) != 1 or not any(c.start() < assignments[0].start() for c in calls):
        raise ValueError('Expected one original world assignment following scene broadcast')
    start, end = assignments[0].span()
    statement = body[start:end]
    block = ('{ ' + statement + '\n'
             '#if UNITY_ANDROID && !UNITY_EDITOR\n'
             'RaftAndroid.Diagnostics.AndroidRuntimeLog.Write('
             '"world", "WorldHasBeenLoaded.originalCompletionAssigned", '
             '"Original ready assignment executed; playability and save not yet proven", false);\n'
             '#endif\n}')
    updated_body = body[:start] + block + body[end:]
    if text.count(body) != 1:
        raise ValueError('Ambiguous original world coroutine body')
    result = text.replace(body, updated_body, 1)
    if result.replace(block, statement, 1) != text:
        raise ValueError('World completion diagnostic altered other statements')
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
    # Only original SaveAndLoad manifests containing the real Load<T> operation
    # receive this diagnostic; synthetic SaveGame-only manifests are unchanged.
    if (name == 'SaveAndLoad' and any(
            method['signature'] == 'public static T Load<T>(string filename)'
            for method in row['methods'])):
        result = trace_caught_original_load_error(result)
    if name == 'Raft_Network':
        result = trace_original_world_completion(result)
    for method in row['methods']:
        if name == 'GameManager' and method.get('name') == 'OnWorldRecieved':
            result = wrap_original_world_callback(result, method['name'], method['body_sha256'], row['area'])
        else:
            result = wrap(result, method['signature'], row['area'], method.get('detail', '""'))
    return result


def _reject_linked_ancestors(path, kind):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Linked operation ' + kind + ' refused')


def apply(project, backup, manifest, write=False):
    # Do not silently resolve symlinks into an unrelated source/backup tree.
    _reject_linked_ancestors(project, 'project')
    _reject_linked_ancestors(backup, 'backup')
    if backup.resolve().is_relative_to(project.resolve()):
        raise ValueError('Backup must be outside imported project')
    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Missing or redirected Unity Assets')
    if backup.exists() and not backup.is_dir():
        raise ValueError('Invalid operation backup directory')
    plans = []
    for name in manifest['sources']:
        matches = [p for p in assets.rglob(name + '.cs') if 'Assembly-CSharp' in p.parts]
        if len(matches) != 1:
            raise ValueError('Original operation source is ambiguous')
        path = matches[0]
        meta = path.with_suffix('.cs.meta')
        _reject_linked_ancestors(path, 'source')
        _reject_linked_ancestors(meta, 'meta')
        if not path.is_file() or (meta.exists() and not meta.is_file()):
            raise ValueError('Original operation source/meta must be regular')
        raw = path.read_bytes()
        text = instrument(name, raw.decode('utf-8-sig'), manifest)
        data = (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.encode()
        if any(p.exists() or p.is_symlink() for p in (backup / path.name, backup / meta.name)):
            raise ValueError('Original operation backup already exists')
        plans.append((path, meta, raw, meta.read_bytes() if meta.exists() else None, data))
    if write:
        prior_backup = backup.exists()
        backup.mkdir(parents=True, exist_ok=True)
        targets = [backup / n for path, meta, raw, metadata, data in plans
                   for n in ((path.name, meta.name) if metadata is not None else (path.name,))]
        mutations_started = False
        try:
            for path, meta, raw, metadata, data in plans:
                shutil.copy2(path, backup / path.name)
                if metadata is not None:
                    shutil.copy2(meta, backup / meta.name)
            for path, meta, raw, metadata, data in plans:
                if ((backup / path.name).read_bytes() != raw
                    or (metadata is not None and (backup / meta.name).read_bytes() != metadata)):
                    raise ValueError('Original operation backup is not byte-identical')
            mutations_started = True
            for path, meta, raw, metadata, data in plans:
                path.write_bytes(data)
                if (path.read_bytes() != data
                    or (meta.read_bytes() if meta.exists() else None) != metadata):
                    raise ValueError('Installed operation/meta changed')
        except BaseException as error:
            if mutations_started:
                # Preserve all original backups if rollback itself fails.
                try:
                    for path, meta, raw, metadata, data in plans:
                        path.write_bytes(raw)
                    for path, meta, raw, metadata, data in plans:
                        if (path.read_bytes() != raw
                            or (meta.read_bytes() if meta.exists() else None) != metadata):
                            raise ValueError('Original operation restoration mismatch')
                except BaseException:
                    raise ValueError('Original operation rollback failed; backups retained') from error
            for target in targets:
                if target.is_symlink():
                    raise ValueError('Unsafe backup appeared; backups retained') from error
                if target.exists():
                    target.unlink()
            if not prior_backup:
                backup.rmdir()
            raise
    return dict(applied=write, sourceFiles=len(plans),
                operations=sum(len(x['methods']) for x in manifest['sources'].values()),
                originalMetasUnchanged=True, perFrameLoopsInstrumented=False)



if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('project', 'backup', 'manifest'): p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    print('RAFT_RUNTIME_OPERATION_TRACING ' + json.dumps(apply(a.project,a.backup,json.loads(a.manifest.read_text()),a.apply),sort_keys=True))
