"""Inspect scene-owned Mesh descriptors without loading LFS or exporting game data."""
from collections import Counter
import gc
import json
from pathlib import Path
import re
import sys


def root_objects(environment):
    # Environment.objects can include dependency files; serialize/audit one owner.
    return list(environment.file.objects.values())


def audit(root):
    import UnityPy
    counts, providers, errors = Counter(), Counter(), Counter()
    for path in sorted(root.iterdir()):
        if not re.fullmatch(r'level\d+', path.name) or not path.is_file():
            continue
        with path.open('rb') as source:
            if source.read(43).startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise ValueError('Scene header must be ordinary Git data')
        environment = UnityPy.load(str(path))
        counts['scene_headers'] += 1
        owned = root_objects(environment)
        counts['root_objects'] += len(owned)
        counts['environment_meshes_before_decode'] += sum(obj.type.name == 'Mesh' for obj in environment.objects)
        for obj in owned:
            if obj.type.name != 'Mesh':
                continue
            counts['root_meshes'] += 1
            try:
                tree = obj.read_typetree()
                stream = tree.get('m_StreamData') or {}
                name, size = stream.get('path', ''), stream.get('size', 0)
                if name and size:
                    if not re.fullmatch(r'level\d+\.resS', name):
                        raise ValueError('Unexpected scene stream provider')
                    providers[name] += 1
                    counts['streamed_root_meshes'] += 1
                    counts['referenced_mesh_bytes_with_duplicates'] += size
            except Exception as exc:
                errors[type(exc).__name__] += 1
        counts['environment_meshes_after_decode'] += sum(obj.type.name == 'Mesh' for obj in environment.objects)
        del environment, owned
        gc.collect()
    report = {'counts': dict(counts), 'streamed_meshes_by_provider': dict(providers),
              'parse_errors': dict(errors), 'limitations': 'Original scene descriptors only; no LFS bytes, finite-position validation or Unity cooking.'}
    print('RAFT_SCENE_MESH_COVERAGE ' + json.dumps(report, sort_keys=True))
    if counts['scene_headers'] != 40 or errors:
        raise SystemExit('Incomplete original scene coverage')


if __name__ == '__main__':
    audit(Path(sys.argv[1]))
