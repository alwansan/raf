#!/usr/bin/env python3
"""GFX-MULTI-032: bounded original Shader48 *unreferenced* compiled table census.

Read only exact SHA-locked ZIP2 source in a disposable runner. No original
DXBC, GLSL, HLSL, property names, PPtrs or binary payload is ever exported.
Even RDEF in an unreferenced program is NOT a Material/register bridge.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import (
    _locate_shader, collect_stage_variant_rows,
)
from gfxlab.tools.multi_shader_one_pass_spirv import (
    compiled_programs, dxbc_containers, exact_pairs,
)
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary

EXPECTED_COMPILED = 1656
EXPECTED_LINKS = 1435
EXPECTED_REFERENCED = 1275
EXPECTED_UNUSED = EXPECTED_COMPILED - EXPECTED_REFERENCED


def collect_linked_indices(subshaders, programs):
    if not isinstance(subshaders, list) or [
            len(x.get("m_Passes", [])) for x in subshaders] != [4, 3]:
        raise ValueError("SOURCE_SHADER48_SEVEN_PASS_TOPOLOGY_DRIFT")
    refs = set()
    rows = 0
    pairs = 0
    for sub in subshaders:
        for original_pass in sub["m_Passes"]:
            pairs += len(exact_pairs(original_pass))
            for name, label in (("progVertex", "Vertex"),
                                ("progFragment", "Pixel")):
                for row in collect_stage_variant_rows(original_pass.get(name)):
                    idx = row.get("m_BlobIndex")
                    typ = row.get("m_GpuProgramType")
                    if type(idx) is not int or not 0 <= idx < len(programs):
                        raise ValueError("SOURCE_LINKED_STAGE_INDEX_DRIFT")
                    source = programs[idx]
                    if (source is None or type(typ) is not int
                            or int(source.m_ProgramType) != typ):
                        raise ValueError("SOURCE_LINKED_STAGE_TYPE_DRIFT")
                    declared = source.m_ProgramType.name
                    if "DX11" not in declared or label not in declared:
                        raise ValueError("SOURCE_LINKED_STAGE_FAMILY_DRIFT")
                    refs.add(idx)
                    rows += 1
    if rows != EXPECTED_LINKS or pairs != 524 or len(refs) != EXPECTED_REFERENCED:
        raise ValueError("SOURCE_SHADER48_REFERENCE_COUNT_DRIFT")
    return refs


def inspect_unused_programs(programs, linked, parse_containers=dxbc_containers,
                            inspect_rdef=rdef_summary):
    """Publish only bounded count totals; fail closed on malformed DX11 DXBC."""
    if len(programs) != EXPECTED_COMPILED:
        raise ValueError("SOURCE_COMPILED_TABLE_SIZE_DRIFT")
    if any(type(i) is not int or not 0 <= i < len(programs) for i in linked):
        raise ValueError("SOURCE_REFERENCED_INDEX_INVALID")
    if len(linked) != EXPECTED_REFERENCED:
        raise ValueError("SOURCE_REFERENCED_UNIQUE_COUNT_DRIFT")
    totals = Counter({
        "unused_entries": 0,
        "unused_empty_code": 0,
        "unused_non_dx11_type": 0,
        "unused_dx11_no_valid_dxbc": 0,
        "unused_dx11_with_one_valid_dxbc": 0,
        "unused_dxbc_rdef_present": 0,
        "unused_dxbc_rdef_absent": 0,
        "unused_rdef_constant_buffer_descriptors": 0,
        "unused_rdef_resource_binding_descriptors": 0,
    })
    for index, program in enumerate(programs):
        if index in linked:
            continue
        totals["unused_entries"] += 1
        if program is None or not hasattr(program, "m_ProgramType"):
            raise ValueError("SOURCE_UNUSED_PROGRAM_MISSING_TYPE")
        label = program.m_ProgramType.name
        if not isinstance(label, str) or not label:
            raise ValueError("SOURCE_UNUSED_PROGRAM_TYPE_INVALID")
        code = bytes(program.m_ProgramCode)
        if len(code) > 16 * 1024 * 1024:
            raise ValueError("SOURCE_UNUSED_PROGRAM_CODE_UNBOUNDED")
        if not code:
            totals["unused_empty_code"] += 1
            continue
        if "DX11" not in label:
            totals["unused_non_dx11_type"] += 1
            continue
        containers = parse_containers(code)
        if not containers:
            totals["unused_dx11_no_valid_dxbc"] += 1
            continue
        if len(containers) != 1:
            raise ValueError("SOURCE_UNUSED_DXBC_AMBIGUOUS")
        totals["unused_dx11_with_one_valid_dxbc"] += 1
        ref = inspect_rdef(containers[0])
        if ref.get("rdef_missing_in_source", False):
            totals["unused_dxbc_rdef_absent"] += 1
        else:
            if not ref.get("rdef_structures_bounds_checked", False):
                raise ValueError("SOURCE_UNUSED_RDEF_UNBOUNDED")
            totals["unused_dxbc_rdef_present"] += 1
            totals["unused_rdef_constant_buffer_descriptors"] += ref["constant_buffers"]
            totals["unused_rdef_resource_binding_descriptors"] += ref["resource_binding_descriptors"]
    if totals["unused_entries"] != EXPECTED_UNUSED:
        raise ValueError("SOURCE_UNUSED_PROGRAM_COUNT_DRIFT")
    return dict(totals)


def audit(stage):
    entries, typed, _ = all_model_entries(stage)
    obj = _locate_shader(entries, typed)
    tree = obj.read_typetree(check_read=False)
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict):
        raise ValueError("SOURCE_PARSED_SHADER48_MISSING")
    programs = compiled_programs(obj)
    refs = collect_linked_indices(parsed.get("m_SubShaders"), programs)
    counts = inspect_unused_programs(programs, refs)
    has_candidate = counts["unused_dxbc_rdef_present"] > 0
    return {
        "experiment": "GFX-MULTI-032",
        "source_sha": ZIP2_SHA,
        "source_shader_family_count": 1,
        "compiled_program_entries": EXPECTED_COMPILED,
        "referenced_unique_entries": len(refs),
        "unreferenced_program_entries": EXPECTED_UNUSED,
        "unreferenced_safe_counts": counts,
        "unreferenced_rdef_candidate_exists": has_candidate,
        "unreferenced_candidate_proves_linked_source_property_register_mapping": False,
        "original_material_to_DX11_register_offsets_verified": False,
        "authentic_shader48_android_runtime_verified": False,
        "original_shader48_restored": False,
        "android_game_pixel_parity_verified": False,
        "raw_shaders_names_ids_values_exported": False,
        "phase_closed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip2", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = audit(stage_originals(args.zip2, args.stage))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("GFX_MULTI032_SAFE_UNREFERENCED_CENSUS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
