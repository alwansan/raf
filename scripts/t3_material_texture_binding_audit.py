#!/usr/bin/env python3
"""Static, aggregate-only Unity Material TexEnv -> texture .meta audit.

This does not establish Unity import or rendered pixels. No asset paths/GUIDs printed.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GUID = re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})\s*$")
TEXENV = re.compile(r"(?m)^\s{0,20}(?:-\s*)?(_[A-Za-z0-9]+):\s*$")
TEXTURE = re.compile(r"(?m)^\s*m_Texture:\s*\{([^{}]*)\}")
FIELD = re.compile(r"(?:^|,)\s*(fileID|guid):\s*([^,}\s]+)")
MAX_BYTES = 32 * 1024 * 1024
TEXTURE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tga", ".dds", ".psd",
                    ".tif", ".tiff", ".exr", ".hdr", ".ktx", ".asset")

def reference(body):
    fields = dict(FIELD.findall(body))
    fid = fields.get("fileID")
    if fid is None:
        return "malformed", None
    if fid == "0":
        return "null", None
    guid = fields.get("guid")
    if guid is None:
        return "builtin_or_local", None
    if not re.fullmatch(r"[0-9a-fA-F]{32}", guid):
        return "malformed", None
    return "external", guid.lower()

def audit(root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root_must_be_directory")
    counts = Counter()
    owners = defaultdict(set)
    for path in root.rglob("*.meta"):
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX_BYTES:
            counts["oversized_meta"] += 1
            continue
        match = GUID.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            suffix = Path(path.name[:-5]).suffix.lower()
            owners[match.group(1).lower()].add((path.relative_to(root).as_posix(), suffix in TEXTURE_SUFFIXES))
    for path in root.rglob("*.mat"):
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX_BYTES:
            counts["oversized_material"] += 1
            continue
        counts["materials_scanned"] += 1
        content = path.read_text(encoding="utf-8", errors="replace")
        # Constrain to the m_TexEnvs YAML block; avoid treating arbitrary references as texture slots.
        block = re.search(r"(?m)^\s*m_TexEnvs:\s*(?:\r?\n|$)", content)
        if not block:
            counts["materials_without_texenv_block"] += 1
            continue
        indent = len(block.group(0).splitlines()[0]) - len(block.group(0).splitlines()[0].lstrip(" "))
        lines = content[block.end():].splitlines()
        slot = False
        for line in lines:
            if line.strip():
                line_indent = len(line) - len(line.lstrip(" "))
                if line_indent < indent or (line_indent == indent and not line.lstrip().startswith("- ")):
                    break
            if TEXENV.match(line) and "m_Texture" not in line:
                if slot:
                    counts["texenv_slots_without_texture_line"] += 1
                slot = True
                counts["texenv_slots_seen"] += 1
            m = TEXTURE.match(line)
            if m and slot:
                slot = False
                kind, guid = reference(m.group(1))
                if kind != "external":
                    counts["texture_" + kind] += 1
                    continue
                matches = owners.get(guid, set())
                if not matches:
                    counts["texture_guid_absent_from_supplied_tree"] += 1
                elif len(matches) > 1:
                    counts["texture_guid_duplicate_meta"] += 1
                elif next(iter(matches))[1]:
                    counts["texture_guid_unique_texture_meta"] += 1
                else:
                    counts["texture_guid_points_to_nontexture_meta"] += 1
        if slot:
            counts["texenv_slots_without_texture_line"] += 1
    return {"status": "STATIC_PARTIAL_TREE_ONLY", "counts": dict(sorted(counts.items())),
            "limitations": "Missing GUID may be in packages or unsupplied files. File extensions are heuristics. Does not prove importer, sampler, alpha, shader variant, or device pixels."}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    print(json.dumps(audit(args.root), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
