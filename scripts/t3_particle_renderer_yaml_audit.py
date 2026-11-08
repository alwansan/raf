#!/usr/bin/env python3
"""Aggregate read-only Unity text ParticleSystemRenderer material PPtr audit."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

DOC = re.compile(r"(?m)^--- !u!(\d+) &[-\d]+(?:\s.*)?$")
FIELD = re.compile(r"(?m)^  m_Materials:[ \t]*(.*)$")
ITEM = re.compile(r"^\s*-\s*\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([0-9a-fA-F]{32}),\s*type:\s*\d+)?\s*\}\s*$")

def audit(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("scan root must be a directory")
    c = Counter()
    for p in root.rglob("*"):
        if p.suffix not in (".prefab", ".unity", ".asset") or not p.is_file():
            continue
        c["files_seen"] += 1
        if p.is_symlink():
            c["symlink_skipped"] += 1
            continue
        try:
            data = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            c["unreadable"] += 1
            continue
        docs = list(DOC.finditer(data))
        anchors = {}
        for doc in docs:
            anchors.setdefault(int(doc.group(2)), []).append(int(doc.group(1)))
        for i, d in enumerate(docs):
            if d.group(1) != "199":
                continue
            c["particle_renderers"] += 1
            body = data[d.end():docs[i+1].start() if i+1 < len(docs) else len(data)]
            fields = list(FIELD.finditer(body))
            if len(fields) != 1:
                c["material_list_missing_or_duplicate"] += 1
                continue
            field = fields[0]
            if field.group(1).strip() == "[]":
                c["empty_material_lists"] += 1
                continue
            if field.group(1).strip():
                c["unsupported_inline_material_lists"] += 1
                continue
            for line in body[field.end():].splitlines():
                if not line.strip():
                    continue
                if not line.startswith("  - "):
                    break
                m = ITEM.fullmatch(line)
                if not m:
                    c["unparsed_material_slots"] += 1
                    continue
                c["material_slots"] += 1
                fid, guid = int(m.group(1)), m.group(2)
                if fid < 0:
                    c["invalid_negative_fileid_slots"] += 1
                elif fid == 0 and guid and guid.lower() != "0"*32:
                    c["invalid_null_fileid_with_guid_slots"] += 1
                elif fid == 0:
                    c["null_material_slots"] += 1
                elif guid and guid.lower() != "0"*32:
                    c["external_material_slots"] += 1
                elif not guid:
                    c["local_material_slots"] += 1
                    targets = anchors.get(fid, [])
                    if not targets:
                        c["local_material_target_missing"] += 1
                    elif len(targets) != 1:
                        c["local_material_target_ambiguous"] += 1
                    elif targets[0] != 21:
                        c["local_material_target_wrong_class"] += 1
                    else:
                        c["local_material_target_valid"] += 1
                else:
                    c["ambiguous_zero_guid_slots"] += 1
    return dict(sorted(c.items()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_root")
    args = parser.parse_args()
    print(json.dumps(audit(args.scan_root), sort_keys=True))
