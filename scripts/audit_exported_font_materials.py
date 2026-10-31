"""Read-only aggregate TMP font/material GUID fidelity check before Unity import."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

GUID = re.compile(r'(?m)^guid:\s*([0-9a-fA-F]{32})\s*$')
MATERIAL = re.compile(r'(?m)^  material:\s*\{([^}\r\n]*)\}')


def audit(project, manifest):
    assets = project / 'Assets'
    targets = {}
    for meta in assets.rglob('*.meta'):
        match = GUID.search(meta.read_text(encoding='utf-8-sig', errors='replace'))
        if match:
            targets.setdefault(match[1].lower(), []).append(meta.with_suffix(''))
    counts = Counter()
    paths = {path for row in manifest['scripts'] if row['fullTypeName'] == 'TMPro.TMP_FontAsset'
             for path in row['usagePaths']}
    for name in sorted(paths):
        path = (assets / name).resolve()
        if not path.is_relative_to(assets.resolve()):
            raise ValueError('Unsafe original font usage path')
        counts['font_assets'] += 1
        text = path.read_text(encoding='utf-8-sig')
        refs = MATERIAL.findall(text)
        if len(refs) != 1:
            counts['missing_or_ambiguous_original_material_field'] += 1
            continue
        file_id = re.search(r'\bfileID:\s*(-?\d+)', refs[0])
        guid = re.search(r'\bguid:\s*([a-fA-F0-9]{32})', refs[0])
        if not file_id or int(file_id[1]) == 0:
            counts['null_material_reference'] += 1
            continue
        candidates = targets.get(guid[1].lower(), []) if guid else []
        if len(candidates) != 1 or not candidates[0].is_file():
            counts['unresolved_or_ambiguous_material_guid'] += 1
        elif not re.search(r'(?m)^--- !u!21 &', candidates[0].read_text(encoding='utf-8-sig', errors='replace')):
            counts['reference_target_is_not_material'] += 1
        else:
            counts['resolved_material_assets'] += 1
    report = {'counts': dict(counts), 'limitations': 'Serialized export GUID targets only; SDK rebinding, Unity font initialization and atlas texture bytes require separate validation.'}
    print('RAFT_EXPORTED_FONT_MATERIAL_AUDIT ' + json.dumps(report, sort_keys=True))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.project, json.loads(args.manifest.read_text()))
    if not result['counts'].get('font_assets'):
        raise SystemExit('No original TMP font identities found')
