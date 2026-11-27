#!/usr/bin/env python3
"""Check authored CI fixture's actual HLSL with cpp, not a Unity/runtime result."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def check(project):
    shader = (project / 'Assets/GTNext23b.shader').read_bytes()
    manifest = (project / 'Next23bEngineRoutes.json').read_bytes()
    packet = json.loads(manifest)
    if packet['candidate_sha256'] != hashlib.sha256(shader).hexdigest():
        raise ValueError('candidate_sha_mismatch')
    blocks = re.findall(r'^HLSLPROGRAM\n(.*?)^ENDHLSL$', shader.decode('utf-8'), re.M | re.S)
    counts = [512, 4, 128, 512]
    if len(blocks) != len(packet['passes']) or len(blocks) != 4:
        raise ValueError('pass_population_mismatch')
    rows = []
    for i, (block, pass_row, expected) in enumerate(zip(blocks, packet['passes'], counts)):
        keys = [v['keywords'] for v in pass_row['variants']]
        if len(keys) != expected or not keys[0] or sum(not k for k in keys) != 1:
            raise ValueError('authored_route_population_or_order_mismatch')
        if len({frozenset(k) for k in keys}) != expected:
            raise ValueError('duplicate_route')
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'actual_hlsl.h'
            file.write_text(block, encoding='utf-8')
            source = []
            for idx, names in enumerate(keys):
                source.extend(f'#define {name} 1' for name in names)
                source.append(f'GT_CHECK_BEGIN_{idx}')
                source.append('#include "actual_hlsl.h"')
                source.append(f'GT_CHECK_END_{idx}')
                source.extend(f'#undef {name}' for name in names)
                source.append('#undef GT_PROBE_ROUTE')
            result = subprocess.run(['cpp', '-P', '-undef', '-nostdinc', '-I', d, '-x', 'c', '-'],
                                    input='\n'.join(source)+'\n', text=True, capture_output=True, check=True, timeout=45)
        out = re.findall(r'GT_CHECK_BEGIN_(\d+)\n(.*?)GT_CHECK_END_\1', result.stdout, re.S)
        if len(out) != expected:
            raise ValueError('preprocessor_output_population_mismatch')
        for idx, (label, body) in enumerate(out):
            if int(label) != idx:
                raise ValueError('route_marker_order_mismatch')
            vertex = re.findall(r'p\.x\s*\+=\s*(\d+)\.0\s*/\s*4096\.0', body)
            fragment = re.findall(r'return\s+float4\(\s*(\d+)\.0\s*/\s*1024\.0,\s*(\d+)\.0\s*/\s*4\.0,', body)
            if vertex != [str(idx+1)] or fragment != [(str(idx+1), str(i))]:
                raise ValueError('route_specific_vs_fs_marker_mismatch')
        rows.append({'pass_index': i, 'pass_type': pass_row['passType'],
                     'routes_checked': expected, 'unique_vertex_markers': expected,
                     'unique_fragment_markers': expected, 'empty_route_index': keys.index([]),
                     'route_zero_nonempty': True})
    return {'status': 'AUTHORED_STAGED_HLSL_MARKERS_MATCHED_BY_CPP',
            'shader_sha256': hashlib.sha256(shader).hexdigest(),
            'engine_manifest_sha256': hashlib.sha256(manifest).hexdigest(),
            'route_checks': sum(r['routes_checked'] for r in rows),
            'stage_marker_checks': 2 * sum(r['routes_checked'] for r in rows),
            'passes': rows, 'cpp_version': subprocess.check_output(['cpp','--version'],text=True).splitlines()[0],
            'Unity_compilation_verified': False, 'compiled_bundle_route_identity_verified': False,
            'original_game_or_device_pixels_verified': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise ValueError('fresh_output_required')
    proof = check(a.project)
    a.out.write_text(json.dumps(proof, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(proof, sort_keys=True))
