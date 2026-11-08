#!/usr/bin/env python3
"""Read-only aggregate audit of Unity text Material -> Shader GUID links.

Scan a complete Unity Assets/Packages snapshot for meaningful coverage.
Unresolved means absent from the *scanned tree*, not proven missing in game.
No material names, GUIDs, paths or proprietary content are printed.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import re

GUID = re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})\s*$")
SHADER = re.compile(r"(?m)^\s*m_Shader:\s*\{\s*fileID:\s*(-?\d+)\s*,\s*guid:\s*([0-9a-fA-F]{32})\s*,\s*type:\s*\d+\s*\}")
SHADER_FIELD = re.compile(r"(?m)^\s*m_Shader\s*:")
ZERO = "0" * 32

def audit(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("scan root must be a directory")
    shader_guid_counts = Counter()
    counters = Counter()
    for meta in root.rglob("*.shader.meta"):
        counters["shader_meta_seen"] += 1
        if meta.is_symlink():
            counters["shader_meta_symlink_skipped"] += 1
            continue
        try:
            text = meta.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            counters["shader_meta_unreadable"] += 1
            continue
        match = GUID.search(text)
        if match:
            # A dangling .shader.meta is not evidence that the Shader source survived export.
            # Reject symlink targets as well: this audit must not follow external source trees.
            shader_source = meta.with_suffix("")
            if shader_source.is_file() and not shader_source.is_symlink():
                shader_guid_counts[match.group(1).lower()] += 1
            else:
                counters["shader_meta_without_source"] += 1
        else:
            counters["shader_meta_without_guid"] += 1
    counters["duplicate_shader_guid_entries"] = sum(n - 1 for n in shader_guid_counts.values() if n > 1)
    for mat in root.rglob("*.mat"):
        counters["material_seen"] += 1
        if mat.is_symlink():
            counters["material_symlink_skipped"] += 1
            continue
        try:
            content = mat.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            counters["material_unreadable"] += 1
            continue
        matches = SHADER.findall(content)
        if len(matches) != 1 or len(SHADER_FIELD.findall(content)) != 1:
            counters["material_shader_pointer_unparsed"] += 1
            continue
        file_id, guid = matches[0]
        guid = guid.lower()
        if guid == ZERO:
            counters["shader_pointer_builtin_or_null"] += 1 if int(file_id) else 0
            counters["shader_pointer_null"] += 1 if not int(file_id) else 0
        elif shader_guid_counts[guid] > 1:
            counters["shader_guid_ambiguous_in_scan"] += 1
        elif shader_guid_counts[guid] == 1:
            counters["shader_guid_resolved_in_scan"] += 1
        else:
            counters["shader_guid_unresolved_in_scan"] += 1
    return {key: counters[key] for key in (
        "material_seen", "material_unreadable", "material_symlink_skipped", "material_shader_pointer_unparsed",
        "shader_pointer_builtin_or_null", "shader_pointer_null",
        "shader_guid_resolved_in_scan", "shader_guid_ambiguous_in_scan", "shader_guid_unresolved_in_scan",
        "shader_meta_seen", "shader_meta_unreadable", "shader_meta_symlink_skipped", "shader_meta_without_guid",
        "shader_meta_without_source", "duplicate_shader_guid_entries")}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_root")
    args = parser.parse_args()
    print(json.dumps(audit(args.scan_root), sort_keys=True))

if __name__ == "__main__":
    main()
