#!/usr/bin/env python3
"""Read-only Unity YAML Material->Shader GUID resolver; aggregate counts only."""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GUID = re.compile(r'(?m)^guid:\s*([0-9a-fA-F]{32})\s*$')
SHADER = re.compile(r'(?m)^\s*m_Shader:\s*\{([^{}]*)\}')
REF = re.compile(r'(?:^|,)\s*guid:\s*([0-9a-fA-F]{32})\s*(?:,|$)')
FID = re.compile(r'(?:^|,)\s*fileID:\s*(-?\d+)\s*(?:,|$)')
MAX = 32 * 1024 * 1024

def audit(root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root_must_be_directory')
    owners = defaultdict(set)
    counts = Counter()
    for path in root.rglob('*.meta'):
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX:
            counts['oversized_meta'] += 1
            continue
        m = GUID.search(path.read_text(encoding='utf-8', errors='replace'))
        if m:
            owners[m.group(1).lower()].add(path.relative_to(root).as_posix())
    for path in root.rglob('*.mat'):
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX:
            counts['oversized_material'] += 1
            continue
        counts['materials_scanned'] += 1
        content = path.read_text(encoding='utf-8', errors='replace')
        m = SHADER.search(content)
        if not m:
            counts['shader_reference_missing'] += 1
            continue
        fid = FID.search(m.group(1))
        guid = REF.search(m.group(1))
        if not fid:
            counts['shader_fileid_missing'] += 1
        elif fid.group(1) == '0':
            counts['shader_null_reference'] += 1
        elif not guid:
            counts['shader_builtin_or_local_reference'] += 1
        else:
            n = len(owners.get(guid.group(1).lower(), ()))
            if n == 0:
                counts['shader_guid_not_in_supplied_tree'] += 1
            elif n == 1:
                counts['shader_guid_unique_in_supplied_tree'] += 1
            else:
                counts['shader_guid_ambiguous_duplicate_meta'] += 1
    return {'status':'STATIC_PARTIAL_TREE_ONLY', 'counts':dict(sorted(counts.items())),
            'limitations':'Absent GUID may be a package/builtin/unsupplied dependency; unique meta does not prove import, variant, visual correctness. No raw paths or GUIDs output.'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    args = ap.parse_args()
    print(json.dumps(audit(args.root), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
