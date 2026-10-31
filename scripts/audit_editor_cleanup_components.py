"""Read original scene component identities without LFS, export or mutation."""
from collections import Counter
import gc
import json
from pathlib import Path
import re
import sys

TARGETS = {
    'MeshCombineStudio.GarbageCollectMesh',
    'MeshCombineStudio.MeshCombineJobManager',
    'MeshCombineStudio.MeshCombiner',
    'UltimateWater.UnderwaterIME',
    'UltimateWater.WaterCamera',
    'UltimateWater.WaterVolumeBase',
}


def audit(root):
    import UnityPy
    counts, selected, failures = Counter(), Counter(), Counter()
    for path in sorted(root.iterdir()):
        if not re.fullmatch(r'level\d+', path.name) or not path.is_file():
            continue
        with path.open('rb') as source:
            if source.read(48).startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise ValueError('LFS scene pointer refused')
        env = UnityPy.load(str(path))
        counts['scenes'] += 1
        cache = {}
        # Environment.objects includes dependencies; count only this scene owner.
        for obj in env.file.objects.values():
            if obj.type.name != 'MonoBehaviour':
                continue
            counts['scene_monobehaviours'] += 1
            try:
                component = obj.read(check_read=False)
                pointer = component.m_Script
                if pointer.m_PathID == 0:
                    counts['null_script_components'] += 1
                    continue
                key = (pointer.m_FileID, pointer.m_PathID)
                if key not in cache:
                    script = pointer.read()
                    cache[key] = '.'.join(filter(None, [script.m_Namespace, script.m_ClassName]))
                identity = cache[key]
                counts['resolved_monobehaviours'] += 1
                if identity in TARGETS:
                    selected[identity] += 1
                if identity == 'MeshCombineStudio.GarbageCollectMesh':
                    try:
                        tree = obj.read_typetree()
                        mesh = tree.get('mesh')
                        if not isinstance(mesh, dict) or 'm_PathID' not in mesh:
                            counts['collector_mesh_schema_unavailable'] += 1
                        else:
                            counts['collector_mesh_schema_available'] += 1
                            if mesh['m_PathID'] == 0:
                                counts['collector_null_mesh'] += 1
                            elif mesh['m_FileID'] == 0:
                                counts['collector_scene_local_mesh_pointer'] += 1
                            else:
                                counts['collector_external_mesh_pointer'] += 1
                    except Exception:
                        counts['collector_mesh_schema_unavailable'] += 1
            except Exception as exc:
                failures[type(exc).__name__] += 1
        del env
        gc.collect()
    report = dict(counts= dict(counts), selected_components=dict(selected),
                  identity_failures=dict(failures),
                  limitations='Counts are original scene instances, not proven error attribution or persistent mesh ownership. Null scripts and unavailable custom schemas are explicit, not repaired. No assets modified or exported; no LFS fetched.')
    print('RAFT_EDITOR_CLEANUP_COMPONENTS ' + json.dumps(report, sort_keys=True))
    if counts['scenes'] != 40 or failures:
        raise SystemExit('Incomplete scene identity inspection; do not infer absent components')


if __name__ == '__main__':
    audit(Path(sys.argv[1]))
