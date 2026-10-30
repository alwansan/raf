#!/usr/bin/env python3
"""Bounded aggregate comparison of existing Unity logs; no game payload reads."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

MESH = re.compile(r'Mesh asset path "Assets/Mesh/([^"\\/]+)\.asset"')
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def inspect_log(lines):
    broad, nonfinite, compiler = set(), set(), set()
    counts = Counter()
    result, apk, bindings, links = None, None, None, None
    for raw in lines:
        line = ANSI.sub('', raw).strip('\ufeff\r\n ')
        line = re.sub(r'^\d{4}-\d\d-\d\dT\S+Z\s*', '', line)
        if line.startswith(('##[', 'echo ', 'print(', 'out.write(', 'f.write(')):
            continue
        mesh = MESH.search(line)
        if mesh:
            broad.add(mesh.group(1))
            counts['mesh_error_path_lines'] += 1
        if 'contains a non-finite value' in line:
            counts['nonfinite_lines'] += 1
            if mesh:
                nonfinite.add(mesh.group(1))
        if 'Quickhull' in line and ('fail' in line.lower() or 'error' in line.lower()):
            counts['quickhull_failure_lines'] += 1
        if 'CollisionMeshData couldn' in line:
            counts['nonaccessible_collision_lines'] += 1
        if 'NullReferenceException' in line:
            counts['null_reference_lines'] += 1
        cs = re.search(r'(Assets/.*?error CS\d+.*)', line)
        if cs:
            compiler.add(cs.group(1))
        if line.startswith('RAFT_ANDROID_NATIVE_RESULT '):
            match = re.search(r'result=(\w+) errors=(\d+) bytes=(\d+)', line)
            if match:
                result = {'result': match[1], 'reported_errors': int(match[2]), 'build_report_bytes': int(match[3])}
        if line.startswith('RAFT_ANDROID_APK_STRUCTURE '):
            payload = json.loads(line.split(' ', 1)[1])
            apk = {key: payload[key] for key in ('apk_bytes', 'apk_sha256', 'abis',
                'arm64_il2cpp', 'fmod_native_library_present', 'unity_data_files')}
        if line.startswith('RAFT_SDK_BINDINGS '):
            bindings = dict(re.findall(r'(\w+)=([\w]+)', line))
        if line.startswith('Scene script GUID matched:'):
            match = re.search(r'(\d+)\s*/\s*(\d+)', line)
            if match:
                links = {'matched': int(match[1]), 'total': int(match[2])}
    public = {'counts': dict(counts), 'distinct_mesh_error_names': len(broad),
              'distinct_nonfinite_names': len(nonfinite), 'distinct_csharp_diagnostics': len(compiler),
              'native_result': result, 'apk_structure': apk, 'sdk_bindings': bindings,
              'scene_script_links': links}
    return public, broad, nonfinite


def compare(before, after, targeted):
    old, old_broad, old_nonfinite = before
    new, new_broad, new_nonfinite = after
    return {'before': old, 'after': new,
            'removed_nonfinite_names': len(old_nonfinite - new_nonfinite),
            'new_nonfinite_names': len(new_nonfinite - old_nonfinite),
            'new_nonfinite_names_already_failed_other_categories': len((new_nonfinite - old_nonfinite) & old_broad),
            'removed_broad_error_names': len(old_broad - new_broad),
            'new_broad_error_names': len(new_broad - old_broad),
            'targeted_original_names': len(targeted),
            'targeted_nonfinite_names_before': len(targeted & old_nonfinite),
            'targeted_nonfinite_names_after': len(targeted & new_nonfinite)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    with args.before.open(encoding='utf-8-sig', errors='replace') as source:
        before = inspect_log(source)
    with args.after.open(encoding='utf-8-sig', errors='replace') as source:
        after = inspect_log(source)
    from scripts.trace_collision_mesh_sources import scan_original_headers
    matches, metadata = scan_original_headers(args.root, before[2] | after[2])
    targeted = {name for name, rows in matches.items() if any(
        row['source'] == 'sharedassets29.assets' and
        row['stream_file'] == 'sharedassets29.assets.resS' for row in rows)}
    if not targeted or not before[0]['native_result'] or not after[0]['native_result']:
        raise SystemExit('Missing target metadata or native build result; refusing incomplete comparison')
    report = compare(before, after, targeted)
    remaining = {name: matches[name] for name in after[2] if matches.get(name)}
    report['remaining_nonfinite_matched_names'] = len(remaining)
    report['remaining_nonfinite_unmatched_names'] = len(after[2] - set(remaining))
    report['remaining_nonfinite_source_headers'] = dict(Counter(
        source for name, rows in remaining.items() for source in {r['source'] for r in rows}))
    report['remaining_nonfinite_new_category_source_headers'] = dict(Counter(
        source for name in after[2] - before[2] for source in
        {r['source'] for r in matches.get(name, [])}))
    from scripts.trace_collision_mesh_sources import summary
    if after[2]:
        report['remaining_stream_priorities'] = summary(Counter({name: 1 for name in after[2]}),
            matches, metadata, args.root)['stream_lfs_priorities']
    report['source_header_parse_errors'] = metadata['parse_errors']
    print('RAFT_NATIVE_GEOMETRY_DIFF ' + json.dumps(report, sort_keys=True))
