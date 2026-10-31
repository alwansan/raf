"""Add a narrowly pinned Editor lifetime guard; never ship replacement game source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ORIGINAL = 'fe9a12ef6ab19b988b571793111c1a37bbd0986188bc2ec2a0cb2afd57bc9680'
GUARD = '''
#if UNITY_EDITOR
        // RAFT_EDITOR_MESH_LIFETIME_V1: asset files are not collector-owned.
        if (!UnityEngine.Application.isPlaying)
        {
            if (mesh != null && !SkipGC && !UnityEditor.EditorUtility.IsPersistent(mesh))
                UnityEngine.Object.DestroyImmediate(mesh);
            return;
        }
#endif
'''


def fingerprint(text):
    return hashlib.sha256(re.sub(r'\s+', '', text).encode()).hexdigest()


def adapt(text, expected=ORIGINAL):
    """Preserve original source exactly outside one conditional insertion."""
    already = GUARD in text
    original = text.replace(GUARD, '', 1) if already else text
    if fingerprint(original) != expected:
        raise ValueError('Unknown collector source revision; no mutation permitted')
    matches = list(re.finditer(r'\bprivate\s+void\s+OnDestroy\s*\(\s*\)\s*\{', original))
    if len(matches) != 1:
        raise ValueError('Expected one original collector lifetime callback')
    position = matches[0].end()
    result = original[:position] + GUARD + original[position:]
    if already and result != text:
        raise ValueError('Unexpected existing guard location')
    return result


def apply(project, backup, write=False):
    paths = list((project / 'Assets').rglob('GarbageCollectMesh.cs'))
    if len(paths) != 1:
        raise ValueError('Require exactly one original collector source')
    path = paths[0]
    meta = path.with_suffix('.cs.meta')
    if not meta.is_file():
        raise ValueError('Original collector meta required; never manufacture it')
    raw, metadata = path.read_bytes(), meta.read_bytes()
    text = raw.decode('utf-8-sig')
    result = adapt(text)
    changed = result != text
    if write and changed:
        if backup.resolve().is_relative_to(project.resolve()):
            raise ValueError('Backup must remain outside imported project')
        backup.mkdir(parents=True, exist_ok=True)
        for source in (path, meta):
            destination = backup / source.name
            if destination.exists():
                raise ValueError('Refuse overwriting original backup')
        shutil.copy2(path, backup / path.name)
        shutil.copy2(meta, backup / meta.name)
        encoded = result.encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            encoded = b'\xef\xbb\xbf' + encoded
        path.write_bytes(encoded)
        if meta.read_bytes() != metadata:
            raise ValueError('Original meta changed')
        if path.read_bytes().decode('utf-8-sig').replace(GUARD, '', 1) != text:
            raise ValueError('Original runtime source changed')
    print('RAFT_EDITOR_MESH_LIFETIME ' + json.dumps(dict(
        applied=bool(write), changed=changed, originalSourceFingerprint=ORIGINAL,
        originalMetaUnchanged=meta.read_bytes() == metadata,
        runtimeSourceUnchanged=True, persistentAssetsDestroyed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    apply(args.project, args.backup, args.apply)
