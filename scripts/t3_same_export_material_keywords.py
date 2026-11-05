#!/usr/bin/env python3
"""T3: actual SHA-pinned selected original Material keywords vs SAME export.

Run only on private, independently SHA-authenticated original ZIP2 bytes and
one AssetRipper W1+B02 trace pair. Never emit keywords, IDs, GUIDs, filenames
of original objects, shader source, or private third-party error strings.
Success proves serialized Material keyword/pass parity only, NOT compiled
ShaderLab/variant parity, Unity runtime correctness, or Android pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import b43_material_keyword_fidelity as b43
from scripts import t3_same_export_material_colors as t3colors
from scripts import t3_same_export_material_texenv as t3texenv

OWNER = t3colors.OWNER
COUNT = t3colors.COUNT
SAFE_COUNTS = ("source_objects", "export_documents",
               "predefined_redirects", "implicit_font_exclusions")
SAFE_FLAGS = ("keyword_state_equal",
              "shader_program_or_variant_equivalence_verified",
              "unity_or_device_verified", "ready_for_build")
BASE = {
    "schema_version": 1,
    "experiment": "T3-authentic-same-export-material-keyword-pass",
    "source_commit": t3texenv.SOURCE_SHA,
    "source_owner": OWNER,
    "original_material_shader_keyword_or_pass_fidelity_proven": False,
    "shader_program_or_variant_equivalence_verified": False,
    "android_device_pixels_verified": False,
    "full_game_shader_coverage_verified": False,
}


def aggregate(raw: dict) -> dict:
    """Copy only audited numeric/boolean fields from the private comparator."""
    if not isinstance(raw, dict) or raw.get("status") != "MATCH":
        raise ValueError("B43 keyword/pass same-export comparison not accepted")
    result = dict(BASE)
    for key in SAFE_COUNTS:
        value = raw.get(key)
        if type(value) is not int or value < 0:
            raise ValueError("Missing safe B43 Material keyword count")
        result[key] = value
    for key in SAFE_FLAGS:
        if type(raw.get(key)) is not bool:
            raise ValueError("Missing safe B43 verification flag")
        result[key] = raw[key]
    if (result["source_objects"] != COUNT
            or result["export_documents"] != COUNT
            or not result["keyword_state_equal"]
            or result["shader_program_or_variant_equivalence_verified"]
            or result["unity_or_device_verified"]
            or result["ready_for_build"]):
        raise ValueError("Incomplete selected original Material keyword parity")
    result["original_material_shader_keyword_or_pass_fidelity_proven"] = True
    result["status"] = "SCOPED_KEYWORD_PASS_MATCH"
    return result


def run(original: Path, project: Path, w1_trace: Path, b02_trace: Path) -> dict:
    # Authentication is performed inside B43 with exact B05 source byte pins.
    if any(p.is_symlink() for p in (original, project, w1_trace, b02_trace)):
        raise ValueError("Unsafe original/export private input")
    w1 = json.loads(w1_trace.read_text(encoding="utf-8"))
    b02 = json.loads(b02_trace.read_text(encoding="utf-8"))
    limited = t3colors.select_same_export_materials(w1, b02)
    source = b43.source_materials(original, selected_owners={OWNER})
    if len(source) != COUNT:
        raise ValueError("Unverified scoped Material count")
    exported = b43.exported_materials(project)
    return aggregate(b43.compare(limited, source, exported))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original", "project", "w1-trace", "b02-trace", "out"):
        ap.add_argument("--" + flag, type=Path, required=True)
    a = ap.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
            or a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("Unsafe private original/export result destination")
    phase = "same_export_lineage"
    try:
        phase = "source_and_export_comparison"
        result = run(a.original, a.project, a.w1_trace, a.b02_trace)
    except Exception as exc:
        # Third-party error messages can expose original per-object asset data.
        result = dict(BASE, status="INCONCLUSIVE", phase=phase,
                      error_type=type(exc).__name__)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                     encoding="utf-8")
    print("T3_SAME_EXPORT_KEYWORDS_AGGREGATE " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "SCOPED_KEYWORD_PASS_MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
