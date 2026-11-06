#!/usr/bin/env python3
"""Fail-closed, source-selected 108-use Particle Shader48 same-export vendor delta.

Only safe aggregate classification leaves the runner. The Shader PPtr identity
is selected afresh from SHA-verified original scenes and the *same* W1/B02
export trace before and after the bounded official vendor restorers. This
cannot prove original authored programs, Unity compile, or Android pixels.
"""
# One-shot authentic original experiment: six scenes, twelve SHA-pinned owners,
# W1/B02 same-instance exporter; TMP/PostFX/Volumetric bounded restorer delta.
from __future__ import annotations

import argparse
import json
from pathlib import Path

SELECTED_STATUS = "T3_ORIGINAL_PARTICLE108_REAL_SAMEEXPORT_SHADERLAB_CLASSIFIED"
DUMMY = "ACTUAL_DUMMY_SHADER_TEXT_EXPORTER"
STATUS = "T3_AUTHENTIC_PARTICLE108_POSTVENDOR_DELTA_CLASSIFIED"
POST_STATES = frozenset((
    DUMMY,
    "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE",
    "NO_PROGRAM_SUBPROGRAMS_EXPORTED",
    "INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER",
    "CUSTOM_PASS_COUNT_DIFFERS_FROM_ORIGINAL",
    "CUSTOM_SHADER_META_MISSING",
    "CUSTOM_SHADER_TEXT_MISSING",
))
REQUIRED_TRUE = (
    "source_original_one_Pass",
    "same_export_instance_W1_B02_verified",
    "source_to_export_Shader48_trace_verified",
    "original_six_scene_SHA_verified",
    "original_four_shader_owner_SHA_verified",
    "exported_shader_custom_reference",
    "original_private_Shader48_name_owner_id_export_guid_not_published",
)
REQUIRED_FALSE = (
    "exported_shader_builtin_reference",
    "original_program_vs_output_bytecode_equivalence_proven",
    "native_Unity_Android_GPU_pixels_verified",
    "source_particle108_is_phone_square_emitter_verified",
)


def _verified(report):
    if (type(report) is not dict or report.get("schema_version") != 1
        or report.get("status") != SELECTED_STATUS
        or type(report.get("original_particle_use_slots")) is not int
        or report["original_particle_use_slots"] != 108
        or any(report.get(key) is not True for key in REQUIRED_TRUE)
        or any(report.get(key) is not False for key in REQUIRED_FALSE)
        or report.get("exported_ShaderLab_source_status") not in POST_STATES
        or type(report.get("selected_shaderlab_dummy_exporter_marker")) is not bool
        or report["selected_shaderlab_dummy_exporter_marker"] !=
           (report["exported_ShaderLab_source_status"] == DUMMY)):
        raise ValueError("untrusted_original_particle108_same_export_report")
    return report["exported_ShaderLab_source_status"]


def compare(before, after):
    previous = _verified(before)
    current = _verified(after)
    if previous != DUMMY:
        raise ValueError("unproven_original_particle108_dummy_prevendor_baseline")
    if not before.get("selected_shader_meta_found") or not before.get("selected_shaderlab_file_present"):
        raise ValueError("missing_private_original_particle108_prevendor_ShaderLab")
    if current == DUMMY:
        interpretation = "DUMMY_PERSISTS_AFTER_VENDOR_RESTORERS"
    elif current == "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE":
        interpretation = "DUMMY_MARKER_REMOVED_PROGRAM_STRUCTURE_ONLY"
    else:
        interpretation = "DUMMY_MARKER_REMOVED_BUT_EXPORT_NOT_PROVEN_USABLE"
    return {
        "schema_version": 1, "status": STATUS, "source_original_particle_renderer_slots": 108,
        "original_six_scene_and_four_owner_SHA_verified": True,
        "same_original_Shader48_selected_from_same_export_W1_B02": True,
        "pre_vendor_dummy": True,
        "post_vendor_dummy": current == DUMMY,
        "post_vendor_structural_one_pass_program": current ==
            "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE",
        "interpretation": interpretation,
        "vendor_restorer_output_original_compiled_program_equivalence_proven": False,
        "android_device_square_smoke_emitter_identity_proven": False,
        "Unity_GPU_pixels_or_game_readiness_proven": False,
        "private_shader_ids_names_guids_original_programs_or_HLSL_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("before", "after", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve() in (args.before.resolve(), args.after.resolve()) or
        args.before.is_symlink() or args.after.is_symlink() or
        not args.before.is_file() or not args.after.is_file() or
        any(p.stat().st_size > 65536 for p in (args.before, args.after))):
        raise ValueError("unsafe_private_particle108_delta_input_or_output")
    try:
        report = compare(json.loads(args.before.read_text("utf-8")),
                         json.loads(args.after.read_text("utf-8")))
    except Exception as exc:
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_type": type(exc).__name__,
                  "Unity_GPU_pixels_or_game_readiness_proven": False,
                  "private_shader_ids_names_guids_original_programs_or_HLSL_published": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("T3_PARTICLE108_SAMEEXPORT_POSTVENDOR_SAFE=" + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
