#!/usr/bin/env python3
"""GFX-MULTI-022: bounded exhaustive Shader48 variant reflection/parameter sweep.

Inspects all authentic source variant rows linked from the pinned Shader48,
including legacy and Unity 2021 player subprogram records. DXBC and typed
metadata remain private to the ephemeral runner. Only aggregate counts and
booleans are emitted; this does not prove Material semantics or Android pixels.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_feasibility import _find_subprogram_rows
from gfxlab.tools.multi_shader_one_pass_spirv import (
    compiled_programs, code_from_ref, exact_pairs,
)
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary

EXPECTED_VARIANT_LINKS = 1435
EXPECTED_EXACT_PAIRS = 524


def _validate_blob_index_shapes(value):
    """Reject malformed typed blob-index fields before counting variant rows."""
    if isinstance(value, list):
        for item in value:
            if item is None:
                raise ValueError("NULL_ORIGINAL_VARIANT_ROW")
            _validate_blob_index_shapes(item)
    elif isinstance(value, dict):
        if "m_BlobIndex" in value and type(value["m_BlobIndex"]) is not int:
            raise ValueError("MALFORMED_ORIGINAL_BLOB_INDEX")
        for field in ("m_SubPrograms", "m_PlayerSubPrograms"):
            if field in value:
                _validate_blob_index_shapes(value[field])


def collect_stage_variant_rows(stage_tree):
    """Collect both legacy and Unity player rows without leaking their contents."""
    if not isinstance(stage_tree, dict):
        raise ValueError("MISSING_TYPED_ORIGINAL_SHADER_STAGE")
    rows = []
    for field in ("m_SubPrograms", "m_PlayerSubPrograms"):
        raw = stage_tree.get(field)
        if raw is None:
            continue
        if not isinstance(raw, list):
            raise ValueError("ORIGINAL_VARIANT_CONTAINER_NOT_ARRAY")
        _validate_blob_index_shapes(raw)
        rows.extend(_find_subprogram_rows(raw))
    return rows


def parameter_shape(row):
    """Return safe presence/count diagnostics for one serialized program row."""
    if not isinstance(row, dict):
        raise ValueError("ORIGINAL_VARIANT_ROW_NOT_OBJECT")
    out = Counter()
    if "m_Samplers" in row:
        out["top_level_sampler_metadata_rows"] += 1
    if "m_ConstantBuffers" in row:
        out["top_level_constant_buffer_metadata_rows"] += 1
    if "m_Parameters" not in row:
        return dict(out)
    params = row["m_Parameters"]
    if params is None:
        out["null_parameter_blocks"] += 1
        return dict(out)
    if not isinstance(params, dict):
        raise ValueError("ORIGINAL_PARAMETER_BLOCK_NOT_OBJECT")
    out["parameter_blocks_present"] += 1
    for field, counter in (
        ("m_TextureParams", "texture_parameter"),
        ("m_ConstantBufferBindings", "constant_buffer_binding"),
    ):
        if field not in params:
            continue
        values = params[field]
        if not isinstance(values, list):
            raise ValueError("ORIGINAL_PARAMETER_ARRAY_MALFORMED_" + field.upper())
        out[counter + "_arrays_present"] += 1
        out[counter + "_entries"] += len(values)
    return dict(out)


def _locate_shader(entries, typed):
    if len(entries) != 6 or [e["id"] for e in entries] != [
        "M00", "M01", "M02", "M03", "M04", "M05"
    ]:
        raise ValueError("SOURCE_MODEL_SELECTION_DRIFT")
    if sum(len(e["materials"]) for e in entries) != 7:
        raise ValueError("SOURCE_MATERIAL_SLOT_COUNT_DRIFT")
    identities = {
        (m["shader_owner"], m["shader_pid"])
        for entry in entries for m in entry["materials"]
    }
    if len(identities) != 1:
        raise ValueError("ORIGINAL_SHADER48_IDENTITY_DRIFT")
    owner, path_id = next(iter(identities))
    obj = typed[owner].get(path_id)
    if obj is None or obj.type.name != "Shader":
        raise ValueError("ORIGINAL_TYPED_SHADER48_MISSING")
    return obj


def audit(stage):
    entries, typed, _ = all_model_entries(stage)
    shader_obj = _locate_shader(entries, typed)
    tree = shader_obj.read_typetree(check_read=False)
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict):
        raise ValueError("ORIGINAL_SHADER_PARSED_FORM_MISSING")
    subshaders = parsed.get("m_SubShaders")
    if not isinstance(subshaders, list) or [len(s.get("m_Passes", [])) for s in subshaders] != [4, 3]:
        raise ValueError("ORIGINAL_SHADER48_PASS_TOPOLOGY_DRIFT")

    programs = compiled_programs(shader_obj)
    if len(programs) != 1656:
        raise ValueError("ORIGINAL_COMPILED_PROGRAM_TABLE_DRIFT")

    totals = Counter()
    unique_programs = {}
    exact_pairs_total = 0
    per_pass_links = 0

    for subshader in subshaders:
        for pass_tree in subshader["m_Passes"]:
            exact_pairs_total += len(exact_pairs(pass_tree))
            for field, expected in (("progVertex", "Vertex"), ("progFragment", "Pixel")):
                rows = collect_stage_variant_rows(pass_tree.get(field))
                per_pass_links += len(rows)
                for row in rows:
                    idx = row.get("m_BlobIndex")
                    declared_type = row.get("m_GpuProgramType")
                    if type(idx) is not int or not 0 <= idx < len(programs):
                        raise ValueError("ORIGINAL_VARIANT_BLOB_LINK_OUT_OF_RANGE")
                    if type(declared_type) is not int:
                        raise ValueError("ORIGINAL_VARIANT_PROGRAM_TYPE_MISSING")
                    program = programs[idx]
                    if program is None or int(program.m_ProgramType) != declared_type:
                        raise ValueError("ORIGINAL_VARIANT_PROGRAM_TYPE_MISMATCH")
                    label = program.m_ProgramType.name
                    if expected not in label or "DX11" not in label:
                        raise ValueError("ORIGINAL_VARIANT_NOT_EXPECTED_DX11_STAGE")

                    totals["variant_link_rows"] += 1
                    totals.update(parameter_shape(row))
                    if (idx, expected) not in unique_programs:
                        dxbc = code_from_ref(row, programs, expected)
                        reflection = rdef_summary(dxbc)
                        unique_programs[(idx, expected)] = reflection
                        totals["unique_referenced_stage_programs"] += 1
                        totals["dxbc_stage_programs_bounds_validated"] += 1
                        if reflection.get("rdef_missing_in_source", False):
                            totals["rdef_absent_stage_programs"] += 1
                        else:
                            totals["rdef_present_stage_programs"] += 1
                            totals["rdef_constant_buffer_descriptors"] += reflection["constant_buffers"]
                            totals["rdef_resource_binding_descriptors"] += reflection["resource_binding_descriptors"]

    if per_pass_links != EXPECTED_VARIANT_LINKS:
        raise ValueError("ORIGINAL_SHADER48_VARIANT_LINK_TOTAL_CHANGED")
    if exact_pairs_total != EXPECTED_EXACT_PAIRS:
        raise ValueError("ORIGINAL_SHADER48_EXACT_MATCHED_PAIR_TOTAL_CHANGED")
    if totals["variant_link_rows"] != EXPECTED_VARIANT_LINKS:
        raise ValueError("ORIGINAL_SHADER48_VARIANT_ROW_CENSUS_MISMATCH")
    if totals["rdef_present_stage_programs"] + totals["rdef_absent_stage_programs"] != totals["unique_referenced_stage_programs"]:
        raise ValueError("ORIGINAL_SHADER48_RDEF_COVERAGE_INCOMPLETE")

    metadata_found = bool(
        totals["parameter_blocks_present"]
        or totals["null_parameter_blocks"]
        or totals["top_level_sampler_metadata_rows"]
        or totals["top_level_constant_buffer_metadata_rows"]
        or totals["rdef_present_stage_programs"]
    )
    bridge_state = (
        "ALTERNATE_SOURCE_METADATA_FOUND_REQUIRES_PROPERTY_REGISTER_LINK"
        if metadata_found else
        "SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS"
    )
    return {
        "experiment": "GFX-MULTI-022",
        "source_sha": ZIP2_SHA,
        "source_models": 6,
        "material_slots": 7,
        "distinct_original_shader48": 1,
        "subshader_count": 2,
        "pass_count": 7,
        "all_original_variant_link_rows": dict(totals),
        "exact_keyword_tier_matched_pairs": exact_pairs_total,
        "unique_referenced_stage_programs": len(unique_programs),
        "all_referenced_stage_programs_are_bounded_dxbc": True,
        "all_original_variant_links_and_types_valid": True,
        "source_embedded_script_field_present": "m_Script" in tree,
        "source_property_to_DX11_register_map_verified": False,
        "source_property_register_bridge_state": bridge_state,
        "original_android_shader_restored": False,
        "actual_android_original_shader_pixels_verified": False,
        "proprietary_shader_bytes_names_or_indices_exported": False,
        "phase_closed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip2", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(stage_originals(args.zip2, args.stage))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("GFX_MULTI022_SAFE_VARIANT_REFLECTION_SWEEP " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
