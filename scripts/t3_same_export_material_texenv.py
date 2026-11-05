#!/usr/bin/env python3
"""T3: genuine SHA-pinned ZIP2 Material/TexEnv vs SAME AssetRipper export.

Only aggregate counters leave the private runner. Source PPtrs, material property
names, exporter instance GUID and original game bytes never enter artifacts/logs.
The bounded source owner is sharedassets6.assets, not the entire game.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts import b05_verify_material_texenv_bindings as b05

INSTANCE = re.compile(r"[0-9a-fA-F]{32}\Z")
SOURCE_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
OWNER = "sharedassets6.assets"
SOURCE_MATERIALS = 41
SOURCE_SLOTS = 227
# Explicitly vetted aggregate-only fields. Do not serialize a raw future
# comparator result that might include proprietary property/object identities.
COUNTERS = (
    "materials_compared", "source_texture_slots", "slots_compared",
    "missing_slots", "extra_slots", "null_to_bound", "bound_to_null",
    "exact_internal_targets_compared", "wrong_internal_targets",
    "unresolved_internal_targets", "external_targets_not_proven",
    "source_null_bindings", "uv_transform_slots_compared",
    "uv_transform_missing_or_unproven", "uv_transform_value_mismatches",
    "outside_scope_export_materials", "outside_scope_trace_materials",
    "excluded_engine_materials", "excluded_font_materials",
)
FLAGS = (
    "source_slots_faithful_with_resolved_scope",
    "all_uv_transforms_verified", "selected_texture_targets_proven",
    "full_game_source_coverage_verified",
    "unity_shader_or_android_pixels_proven",
)
RESULT_TEMPLATE = {
    "schema_version": 1,
    "experiment": "T3-authentic-sharedassets6-same-export-TexEnv",
    "zip2_source_commit": SOURCE_SHA,
    "authenticated_original_scope": "sharedassets6.assets",
    "same_export_instance_compared": False,
    "android_device_or_pixel_proven": False,
}


def combine_same_export(w1: dict, b02: dict) -> dict:
    """Identity-safe join; mixing exports would make every comparison invalid."""
    for trace in (w1, b02):
        if (not isinstance(trace, dict) or trace.get("schema_version") != 1
            or not isinstance(trace.get("export_instance"), str)
            or not INSTANCE.fullmatch(trace["export_instance"])
            or not isinstance(trace.get("objects"), list)):
            raise ValueError("Malformed private source/export trace")
    if w1["export_instance"].lower() != b02["export_instance"].lower():
        raise ValueError("Different exporter instances cannot be compared")
    if not any(isinstance(row, dict) and row.get("class_id") == 21
               for row in w1["objects"]):
        raise ValueError("Missing native Material21 same-instance lineage")
    if any(not isinstance(row, dict) or row.get("class_id") not in (21, 48)
           for row in w1["objects"]):
        raise ValueError("W1 trace contains unexpected asset classes")
    if any(not isinstance(row, dict) or row.get("class_id") != 28
           for row in b02["objects"]) or not b02["objects"]:
        raise ValueError("Texture trace lacks real Texture2D28 lineage")
    # B05 checks all original identities, material pointers, texture source
    # aliases, and UV slots after this stage. Do not match by filename/name.
    return dict(schema_version=1,
                export_instance=w1["export_instance"].lower(),
                objects=w1["objects"] + b02["objects"])


def aggregate(result: dict) -> dict:
    """Allow-list fields so a future private comparator change cannot leak IDs."""
    if not isinstance(result, dict):
        raise ValueError("Missing actual Material comparator result")
    safe = dict(RESULT_TEMPLATE)
    for field in COUNTERS:
        value = result.get(field)
        if type(value) is not int or value < 0:
            raise ValueError("Missing/invalid aggregate Material counter")
        safe[field] = value
    for field in FLAGS:
        if type(result.get(field)) is not bool:
            raise ValueError("Missing Material verification boolean")
        safe[field] = result[field]
    if (safe["materials_compared"] != SOURCE_MATERIALS
            or safe["source_texture_slots"] != SOURCE_SLOTS):
        raise ValueError("Actual exported Material source scope incomplete")
    safe["same_export_instance_compared"] = True
    safe["status"] = ("SCOPED_TEXTURE_UV_MATCH"
                      if safe["source_slots_faithful_with_resolved_scope"]
                      and safe["all_uv_transforms_verified"]
                      and safe["slots_compared"] == SOURCE_SLOTS
                      else "SCOPED_TEXTURE_UV_MISMATCH")
    # Even a match leaves original external-owner texture pointers, shader,
    # sRGB, GPU/water pixels and other game assets unverified.
    safe["all_external_texture_targets_proven"] = False
    return safe


def run(source: Path, project: Path, w1_path: Path, b02_path: Path) -> dict:
    if any(p.is_symlink() for p in (source, project, w1_path, b02_path)):
        raise ValueError("Linked source/export/trace path")
    w1 = json.loads(w1_path.read_text(encoding="utf-8"))
    b02 = json.loads(b02_path.read_text(encoding="utf-8"))
    joined = combine_same_export(w1, b02)
    original = b05.original_texenvs(source, owner_names={OWNER})
    if len(original) != SOURCE_MATERIALS or sum(len(v) for v in original.values()) != SOURCE_SLOTS:
        raise ValueError("Source owner is not authenticated B05 sample")
    exported = b05.exported_texenvs(project)
    return aggregate(b05.compare(joined, original, exported, selected_owners={OWNER}))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--w1-trace", type=Path, required=True)
    ap.add_argument("--b02-trace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
            or a.out.resolve().is_relative_to(a.project.resolve())
            or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("Unsafe aggregate report destination")
    try:
        result = run(a.original, a.project, a.w1_trace, a.b02_trace)
    except Exception as error:
        # Never output raw error messages: private YAML names and paths can
        # appear in third-party exceptions. Preserve only the exception TYPE.
        result = dict(RESULT_TEMPLATE, status="INCONCLUSIVE",
                      exception_type=type(error).__name__)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("T3_SAME_EXPORT_MATERIAL_AGGREGATE " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "SCOPED_TEXTURE_UV_MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
