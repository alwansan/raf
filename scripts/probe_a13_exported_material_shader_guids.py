#!/usr/bin/env python3
"""A13 read-only exported Material->Shader GUID structural guard.

Local Unity YAML only: no original source/AssetRipper export completeness,
ShaderLab authenticity, GPU or Android gameplay is implied. No GUIDs, paths
or proprietary asset contents are printed.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re

BUILTIN = {"0000000000000000e000000000000000",
           "0000000000000000f000000000000000",
           "00000000000000000000000000000000"}
GUID = re.compile(r"(?m)^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$")
HEADER = re.compile(r"(?m)^---[ \t]+!u!(\d+)[ \t]+&-?\d+[ \t]*$")
FIELD = re.compile(r"(?m)^  m_Shader:[ \t]*(\{[^\r\n}]*\})[ \t]*$")


class GuardError(ValueError):
    pass


def bound_text(path, maximum):
    if path.stat().st_size > maximum:
        raise GuardError("oversized_export_record")
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise GuardError("invalid_export_utf8") from exc


def pointer(raw):
    if not raw.startswith("{") or not raw.endswith("}"):
        raise GuardError("bad_shader_pointer")
    parts = [p.strip().split(":", 1) for p in raw[1:-1].split(",")]
    if any(len(p) != 2 for p in parts):
        raise GuardError("bad_shader_pointer")
    fields = {k.strip(): v.strip() for k, v in parts}
    if len(parts) != 3 or set(fields) != {"fileID", "guid", "type"}:
        raise GuardError("bad_shader_pointer")
    if not re.fullmatch(r"-?\d+", fields["fileID"]) or not re.fullmatch(r"\d+", fields["type"]) or not re.fullmatch(r"[0-9a-fA-F]{32}", fields["guid"]):
        raise GuardError("bad_shader_pointer")
    fid, kind = int(fields["fileID"]), int(fields["type"])
    if fid <= 0:
        raise GuardError("null_or_negative_shader_reference")
    return fid, fields["guid"].lower(), kind


def material_pointers(text):
    headers = list(HEADER.finditer(text))
    result = []
    for i, h in enumerate(headers):
        if h.group(1) != "21":
            continue
        end = headers[i+1].start() if i+1 < len(headers) else len(text)
        fields = FIELD.findall(text[h.end():end])
        if len(fields) != 1:
            raise GuardError("missing_or_duplicate_m_Shader")
        result.append(pointer(fields[0]))
    if not result:
        raise GuardError("no_material_yaml_object")
    return result


def audit(project, expected_materials=None):
    root = Path(os.path.abspath(project))
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise GuardError("symlinked_project_ancestor")
    assets = root / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise GuardError("missing_assets_root")
    all_entries = list(assets.rglob("*"))
    if any(p.is_symlink() for p in all_entries):
        raise GuardError("symlinked_export_entry")
    metas = [p for p in all_entries if p.is_file() and p.name.endswith(".meta")]
    shaders = {p for p in all_entries if p.is_file() and p.suffix == ".shader"}
    mats = [p for p in all_entries if p.is_file() and p.suffix == ".mat"]
    if not mats:
        raise GuardError("no_exported_materials")
    registered = set()
    shader_guids = set()
    for meta in metas:
        hits = GUID.findall(bound_text(meta, 65536))
        if len(hits) != 1:
            if meta.name.endswith(".shader.meta"):
                raise GuardError("invalid_shader_meta_guid")
            continue
        guid = hits[0].lower()
        if guid in registered:
            raise GuardError("duplicate_meta_guid")
        registered.add(guid)
        if meta.name.endswith(".shader.meta"):
            if meta.with_suffix("") not in shaders:
                raise GuardError("orphan_shader_meta")
            if guid in BUILTIN:
                raise GuardError("reserved_builtin_guid")
            shader_guids.add(guid)
    if any(source.with_name(source.name + ".meta") not in metas for source in shaders):
        raise GuardError("missing_shader_meta")
    counts = Counter()
    distinct = set()
    for mat in mats:
        for _, guid, kind in material_pointers(bound_text(mat, 4 * 1024 * 1024)):
            counts["materials"] += 1
            if guid in BUILTIN:
                if kind != 0:
                    raise GuardError("invalid_builtin_pointer_type")
                counts["builtin_transport_unresolved"] += 1
            else:
                if kind != 3:
                    raise GuardError("invalid_custom_pointer_type")
                if guid not in shader_guids:
                    raise GuardError("missing_or_wrong_type_shader_guid")
                counts["resolved_local_shader"] += 1
                distinct.add(guid)
    if expected_materials is not None and (expected_materials <= 0 or counts["materials"] != expected_materials):
        raise GuardError("expected_material_count_mismatch")
    return {
        "material_files": len(mats), "material_objects": counts["materials"],
        "shader_files": len(shaders), "shader_meta_guids": len(shader_guids),
        "resolved_shader_guids": counts["resolved_local_shader"],
        "builtin_transport_unresolved": counts["builtin_transport_unresolved"],
        "distinct_target_shader_guids": len(distinct),
        "original_export_provenance_verified": False,
        "full_export_scope_verified": False,
        "original_material_link_equivalence_verified": False,
        "shader_visual_or_gpu_verified": False,
        "ready_for_build": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--expected-materials", type=int)
    args = p.parse_args(argv)
    try:
        result = audit(args.project, args.expected_materials)
    except (GuardError, OSError) as exc:
        code = str(exc) if isinstance(exc, GuardError) else "unsafe_or_unreadable_export"
        print("RAFT_A13_EXPORT_GUID " + json.dumps({"status": "REJECTED", "error_code": code, "ready_for_build": False}, sort_keys=True))
        return 2
    print("RAFT_A13_EXPORT_GUID " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
