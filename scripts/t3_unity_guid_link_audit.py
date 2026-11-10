#!/usr/bin/env python3
"""Read-only Unity YAML GUID reference inventory (no proprietary content emitted).

Only report counts and hashed identities; unresolved != missing in the complete game.
Usage: python3 scripts/t3_unity_guid_link_audit.py --root /private/export --json /tmp/audit.json
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GUID = re.compile(r"(?<![0-9a-fA-F])guid:\s*([0-9a-fA-F]{32})(?![0-9a-fA-F])")
REF_BLOCK = re.compile(r"\{([^{}]*)\}")
REF_FILE_ID = re.compile(r"(?:^|,)\s*fileID:\s*(-?\d+)\s*(?=,|$)")
REF_GUID = re.compile(r"(?:^|,)\s*guid:\s*([0-9a-fA-F]{32})\s*(?=,|$)")
EXTENSIONS = {".mat", ".prefab", ".unity", ".asset", ".controller", ".overridecontroller", ".playable", ".rendertexture"}
MAX_BYTES = 32 * 1024 * 1024

def inspect(root):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root_must_be_directory")
    known = set()
    duplicates = Counter()
    scanned_meta = 0
    for path in root.rglob("*.meta"):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            continue
        matches = GUID.findall(path.read_text(encoding="utf-8", errors="replace"))
        if matches:
            key = matches[0].lower()
            duplicates[key] += 1
            known.add(key)
            scanned_meta += 1
    refs = Counter()
    files = 0
    unresolved_by_extension = Counter()
    for path in root.rglob("*"):
        if path.suffix.lower() not in EXTENSIONS or path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX_BYTES:
            continue
        files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for block in REF_BLOCK.findall(text):
            file_match = REF_FILE_ID.search(block)
            guid_match = REF_GUID.search(block)
            if not file_match or not guid_match:
                continue
            guid = guid_match.group(1).lower()
            if guid == "0" * 32:
                refs["builtin_or_null"] += 1
            elif guid in known:
                refs["resolved_in_supplied_tree"] += 1
            else:
                refs["unresolved_in_supplied_tree"] += 1
                unresolved_by_extension[path.suffix.lower()] += 1
    return {
        "status": "STATIC_PARTIAL_TREE_ONLY",
        "meta_files_indexed": scanned_meta,
        "yaml_files_scanned": files,
        "duplicate_guid_groups": sum(v > 1 for v in duplicates.values()),
        "reference_counts": dict(sorted(refs.items())),
        "unresolved_by_source_extension": dict(sorted(unresolved_by_extension.items())),
        "limitations": "External packages, built-in resources, binary assets and omitted source trees are not checked; no device or shader compilation proof."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = inspect(args.root)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json:
        args.json.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

if __name__ == "__main__":
    main()
