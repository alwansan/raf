#!/usr/bin/env python3
"""Read-only, aggregate-only comparison of Unity YAML material references.

Pairs materials by identical relative path in two independently verified trees.
A difference is evidence of a changed serialized reference, NOT missing asset,
shader import failure, or Android visual correctness.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024
SHADER = re.compile(r"(?m)^\s*m_Shader:\s*\{([^{}]*)\}")
GUID = re.compile(r"\bguid:\s*([0-9a-fA-F]{32})\b")
REF_FIELD = re.compile(r"\b(fileID|guid|type):\s*([^,}\s]+)")
TEXENV = re.compile(r"^([ \t]*)m_TexEnvs:\s*$")
NEXT_FIELD = re.compile(r"^([ \t]*)([A-Za-z_][\w]*):")
TEXTURE = re.compile(r"\bm_Texture:\s*\{([^{}]*)\}")
SLOT = re.compile(r"^([ \t]*)(?:-\s*)?([A-Za-z_][\w]*):\s*(?:\{\s*\})?\s*$")

def snapshot(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    shader = SHADER.search(text)
    shader_ref = shader.group(1).replace(" ", "") if shader else None
    # Count only texture bindings inside m_TexEnvs, never unrelated GUID fields.
    active = False
    base_indent = -1
    refs = []
    current_slot = None
    slot_indent = -1
    for line in text.splitlines():
        head = TEXENV.match(line)
        if head:
            active = True
            base_indent = len(head.group(1).expandtabs(4))
            current_slot = None
            slot_indent = -1
            continue
        if not active:
            continue
        field = NEXT_FIELD.match(line)
        if field and len(field.group(1).expandtabs(4)) <= base_indent:
            active = False
            continue
        slot = SLOT.match(line)
        if slot:
            indent = len(slot.group(1).expandtabs(4))
            if indent >= base_indent and (current_slot is None or indent <= slot_indent):
                current_slot = slot.group(2)
                slot_indent = indent
        match = TEXTURE.search(line)
        if match:
            # Unity references may share a GUID but point to different subassets.
            # Preserve fileID/type as well as GUID; canonicalize field order.
            fields = {key: value.lower() if key == "guid" else value
                      for key, value in REF_FIELD.findall(match.group(1))}
            identity = tuple(fields.get(key, "<missing>") for key in ("fileID", "guid", "type"))
            refs.append((current_slot or "<unassigned-slot>", identity))
    return shader_ref, Counter(refs)

def inventory(root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("expected_directory")
    result = {}
    skipped = 0
    for path in root.rglob("*.mat"):
        item = snapshot(path)
        if item is None:
            skipped += 1
        else:
            result[path.relative_to(root).as_posix()] = item
    return result, skipped

def compare(original, exported):
    a, skip_a = inventory(original)
    b, skip_b = inventory(exported)
    common = a.keys() & b.keys()
    counts = Counter({
        "original_materials": len(a),
        "export_materials": len(b),
        "paired_materials": len(common),
        "original_only_materials": len(a.keys() - b.keys()),
        "export_only_materials": len(b.keys() - a.keys()),
        "skipped_original": skip_a,
        "skipped_export": skip_b,
    })
    for name in common:
        sa, ta = a[name]
        sb, tb = b[name]
        if sa != sb:
            counts["changed_shader_reference_materials"] += 1
        if ta != tb:
            counts["changed_texture_reference_materials"] += 1
        if sa == sb and ta == tb:
            counts["unchanged_reference_materials"] += 1
        if sa is None or sb is None:
            counts["pair_missing_shader_field"] += 1
    return {
        "status": "STATIC_SERIALIZED_REFERENCE_COMPARISON_ONLY",
        "counts": dict(sorted(counts.items())),
        "limitations": "Same-relative-path materials only; renamed materials are unpaired. References are compared as serialized, not resolved to assets. Texture slot names and fileID/guid/type subasset identities are compared when parseable; duplicate slot occurrences, ordering, material property values, alpha, blend, keywords, shader variants, Unity import, and GPU output are not validated. No game paths, GUIDs, or raw materials are emitted."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True)
    p.add_argument("--exported", required=True)
    args = p.parse_args()
    print(json.dumps(compare(args.original, args.exported), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
