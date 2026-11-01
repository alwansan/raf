"""Instrument pinned operation boundaries; never log per-frame game loops or payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

LITERALS = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


def body_bounds(text, signature):
    if text.count(signature) != 1:
        raise ValueError('Operation signature must be unique: ' + signature)
    opening = text.index('{', text.index(signature) + len(signature))
    literals = {m.start(): m.end() for m in LITERALS.finditer(text, opening)}
    depth, i = 1, opening + 1
    while i < len(text):
        if i in literals:
            i = literals[i]
            continue
        if text[i] == '{': depth += 1
        if text[i] == '}': depth -= 1
        if depth == 0: return opening + 1, i
        i += 1
    raise ValueError('Unbalanced original operation')


def wrap(text, signature, area, detail='""'):
    start, end = body_bounds(text, signature)
    original = text[start:end]
    if '__raftOperation' in original:
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


def instrument(name, text, manifest):
    row = manifest['sources'][name]
    digest = hashlib.sha256(text.replace('\r\n', '\n').encode()).hexdigest()
    if digest != row['sha256']:
        raise ValueError('Unknown adapted original revision: ' + name)
    result = text
    for method in row['methods']:
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
