#!/usr/bin/env python3
"""Read-only finite-position gate for staged original Mesh objects, not Unity cooking."""
import argparse
from collections import Counter
import gc
import json
import math
from pathlib import Path
from scripts.mesh_source_files import serialized_sources, owned_objects


def position_metrics(vertices, expected):
    if not vertices and expected == 0:
        return 'empty-original'
    if not vertices or len(vertices) != expected:
        return 'vertex-count-mismatch'
    if any(len(vertex) != 3 or not all(math.isfinite(v) for v in vertex) for vertex in vertices):
        return 'nonfinite-or-invalid-position'
    return 'finite'


def audit(root, expected_meshes=None):
    import UnityPy
    from UnityPy.helpers.MeshHelper import MeshHandler
    counts, errors, per_file = Counter(), Counter(), {}
    for path in serialized_sources(root):
        environment = UnityPy.load(str(path))
        per_file[path.name] = sum(obj.type.name == 'Mesh' for obj in owned_objects(environment))
        for obj in owned_objects(environment):
            if obj.type.name != 'Mesh':
                continue
            counts['meshes'] += 1
            try:
                mesh = obj.read()
                compressed = mesh.m_CompressedMesh.m_Vertices.m_NumItems
                expected = compressed // 3 if compressed else mesh.m_VertexData.m_VertexCount
                if expected == 0:
                    counts['empty-original'] += 1
                    continue
                handler = MeshHandler(mesh)
                handler.process()
                counts[position_metrics(handler.m_Vertices, expected)] += 1
            except Exception as exc:
                errors[type(exc).__name__] += 1
        print('Position audit header completed:', path.name, flush=True)
        del environment
        gc.collect()
    report = {'position_status': dict(counts), 'parse_errors': dict(errors), 'mesh_counts_by_serialized_owner': per_file,
              'limitations': 'Original Mesh positions only; Unity import/collider cooking/gameplay unverified.'}
    print('RAFT_ORIGINAL_MESH_POSITION_AUDIT ' + json.dumps(report, sort_keys=True), flush=True)
    if (errors or not counts['meshes'] or counts['vertex-count-mismatch'] or
            counts['nonfinite-or-invalid-position'] or
            (expected_meshes is not None and counts['meshes'] != expected_meshes)):
        raise SystemExit('Original geometry gate failed; refusing downstream Unity build')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    expected = json.loads(args.manifest.read_text())['statistics']['source_meshes'] if args.manifest else None
    audit(args.root, expected)

