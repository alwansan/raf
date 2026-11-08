#!/usr/bin/env python3
"""Aggregate external ParticleSystemRenderer material GUID metadata coverage; no identities emitted."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

DOC = re.compile(r"(?m)^--- !u!(\d+) &-?\d+(?:\s.*)?$")
FIELD = re.compile(r"(?m)^  m_Materials:\s*$")
SLOT = re.compile(r"^  - \{fileID: (\d+), guid: ([0-9a-fA-F]{32}), type: \d+\}\s*$")
META = re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})\s*$")

def audit(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("root must be directory")
    owners, counts = Counter(), Counter()
    for p in root.rglob("*.mat.meta"):
        if p.is_symlink() or not p.is_file():
            counts["meta_skipped"] += 1
            continue
        try:
            m = META.search(p.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError):
            counts["meta_unreadable"] += 1
            continue
        if m:
            material = p.with_suffix("")
            if material.is_symlink() or not material.is_file():
                counts["orphan_mat_meta"] += 1
                continue
            owners[m.group(1).lower()] += 1
        else:
            counts["meta_without_guid"] += 1
    for p in root.rglob("*"):
        if p.suffix not in (".prefab", ".unity", ".asset") or p.is_symlink() or not p.is_file():
            continue
        try:
            data = p.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            counts["yaml_unreadable"] += 1
            continue
        docs = list(DOC.finditer(data))
        for i, d in enumerate(docs):
            if d.group(1) != "199":
                continue
            body = data[d.end():docs[i+1].start() if i+1 < len(docs) else len(data)]
            fields = list(FIELD.finditer(body))
            if len(fields) != 1:
                counts["renderer_material_list_unsupported"] += 1
                continue
            for line in body[fields[0].end():].splitlines():
                if not line.strip():
                    continue
                if not line.startswith("  - "):
                    break
                m = SLOT.fullmatch(line)
                if not m:
                    counts["slots_not_external_simple"] += 1
                    continue
                fid, guid = int(m.group(1)), m.group(2).lower()
                if fid == 0 or guid == "0"*32:
                    counts["slots_not_external_simple"] += 1
                    continue
                counts["external_slots"] += 1
                n = owners[guid]
                if n == 1:
                    counts["external_guid_unique_mat_meta"] += 1
                elif n > 1:
                    counts["external_guid_duplicate_mat_meta"] += 1
                else:
                    counts["external_guid_not_in_mat_meta_tree"] += 1
    return dict(sorted(counts.items()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    print(json.dumps(audit(parser.parse_args().root), sort_keys=True))
