#!/usr/bin/env python3
"""T3: compare SHA-pinned original Material tint RGBA to one genuine export.

Reuses B44's strict full-source RGB value verifier with an exact B05 source
owner selection and a single AssetRipper Material21 lineage instance. This
is a bounded original/export color property test, NOT a GPU/image/phone test.
Never serialize private per-Material identifiers, original values, or names.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import b44_verify_material_colors as b44
from scripts import t3_same_export_material_texenv as t3

OWNER = "sharedassets6.assets"
COUNT = 41
SAFE_COUNTS = (
    "source_materials_verified", "yaml_materials_compared",
    "engine_material_redirects_excluded", "font_importer_materials_excluded",
    "materials_with_original_nonidentity_colors", "color_slots_compared",
    "missing_color_slots", "unexpected_color_slots", "changed_color_values",
    "mismatched_materials",
)
SAFE_FLAGS = ("original_material_color_values_preserved",
              "shader_program_or_device_fidelity_verified")


def select_same_export_materials(w1: dict, texture: dict) -> dict:
    # Reject cross-run or zero-texture object traces using the already proven
    # T3 W1+B02 invariant; never synthesize export GUIDs from source names.
    joined = t3.combine_same_export(w1, texture)
    selected = []
    for row in w1["objects"]:
        if row["class_id"] != 21:
            continue
        source = row.get("source", {})
        name = source.get("owner")
        if not isinstance(name, str) or not name:
            raise ValueError("Missing traced Material owner")
        if Path(name.replace("\\", "/")).name == OWNER:
            selected.append(row)
    if len(selected) != COUNT:
        raise ValueError("Exact selected Material trace population absent")
    return {"schema_version": 1,
            "export_instance": joined["export_instance"],
            "objects": selected}


def aggregate(report: dict) -> dict:
    if not isinstance(report, dict):
        raise ValueError("Invalid real-source Material color comparison")
    result = {
        "experiment": "T3-authentic-same-export-material-color",
        "schema_version": 1,
        "source_owner": OWNER,
        "source_commit": t3.SOURCE_SHA,
        "same_export_color_values_compared": True,
        "device_color_pixels_proven": False,
        "shader_variants_or_lighting_proven": False,
        "external_texture_targets_proven": False,
        "full_game_scope_proven": False,
    }
    for key in SAFE_COUNTS:
        if type(report.get(key)) is not int or report[key] < 0:
            raise ValueError("Missing safe original/export color counter")
        result[key] = report[key]
    for key in SAFE_FLAGS:
        if type(report.get(key)) is not bool:
            raise ValueError("Missing verified color fidelity flag")
        result[key] = report[key]
    if (result["source_materials_verified"] != COUNT
            or result["yaml_materials_compared"] != COUNT):
        raise ValueError("Selected source/export Material color population incomplete")
    result["status"] = ("SCOPED_COLOR_RGBA_MATCH"
                        if result["original_material_color_values_preserved"]
                        and result["mismatched_materials"] == 0
                        and result["missing_color_slots"] == 0
                        and result["unexpected_color_slots"] == 0
                        and result["changed_color_values"] == 0
                        else "SCOPED_COLOR_RGBA_MISMATCH")
    return result


def run(original: Path, project: Path, w1_trace: Path, b02_trace: Path) -> dict:
    if any(p.is_symlink() for p in (original, project, w1_trace, b02_trace)):
        raise ValueError("Unsafe selected source path or private trace")
    w1 = json.loads(w1_trace.read_text(encoding="utf8"))
    b02 = json.loads(b02_trace.read_text(encoding="utf8"))
    limited = select_same_export_materials(w1, b02)
    source = b44.original_colors(original, selected_owners={OWNER})
    if len(source) != COUNT:
        raise ValueError("Original SHA-pinned Material color scope incomplete")
    exported = b44.exported_colors(project)
    return aggregate(b44.compare(limited, source, exported))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--w1-trace", type=Path, required=True)
    parser.add_argument("--b02-trace", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("Private source or export report destination refused")
    stage = "private_traces_and_exact_material_scope"
    try:
        w1 = json.loads(a.w1_trace.read_text(encoding="utf8"))
        b02 = json.loads(a.b02_trace.read_text(encoding="utf8"))
        limited = select_same_export_materials(w1, b02)
        stage = "sha_pinned_original_color_records"
        source = b44.original_colors(a.original, selected_owners={OWNER})
        if len(source) != COUNT:
            raise ValueError("Original SHA-pinned Material color scope incomplete")
        stage = "actual_export_color_yaml"
        exported = b44.exported_colors(a.project)
        stage = "same_export_value_comparison"
        output = aggregate(b44.compare(limited, source, exported))
    except Exception as e:
        # Third-party errors can contain original paths/properties. Only show
        # our predefined phase and exception class in public artifact/logs.
        output = {
            "schema_version": 1,
            "experiment": "T3-authentic-same-export-material-color",
            "status": "INCONCLUSIVE", "phase": stage,
            "error_type": type(e).__name__,
            "device_color_pixels_proven": False,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_SAME_EXPORT_COLOR_AGGREGATE "+json.dumps(output,sort_keys=True))
    return 0 if output["status"]=="SCOPED_COLOR_RGBA_MATCH" else 2


if __name__=="__main__":
    raise SystemExit(main())
