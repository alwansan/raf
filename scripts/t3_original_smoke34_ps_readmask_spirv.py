#!/usr/bin/env python3
"""SHA-original smoke34 PS DXBC ReadWriteMask vs source/roundtrip SPIR-V inputs.

Use ONLY both exact source keyword-matched genuine DXBC VS/FS pairs from the
17-emitter / 34-slot smoke-linked Shader48. Original semantic names, registers,
compiled shaders, SPIR-V/HLSL and private paths never leave the ephemeral CI
runner. Aggregate lane equality is not a semantic-to-Location mapping proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from scripts import t3_original_smoke34_dxbc_semantic_join as smoke_semantics
from scripts import t3_original_921_dxbc_readmask_spirv as inherited
from scripts import t3_original_921_dxbc_semantic_join as dxbc
from scripts.w1_recover_graphics_programs import translate
from scripts.w1_recover_depth_passes import reflection

STATUS = "SHA_ORIGINAL_SMOKE34_PS_READMASK_VS_SOURCE_ROUNDTRIP_SPV_LANES_CLASSIFIED"
PAIRS = 2
MAX_PROGRAM_BYTES = 8 * 1024 * 1024
FIELDS = inherited.FIELDS
MASK_FIELDS = (
    "source_ps_user_semantic_records", "source_ps_system_value_records",
    "source_ps_declared_component_lanes", "source_ps_read_component_lanes",
    "source_ps_declared_but_unread_component_lanes",
    "source_ps_completely_unread_user_semantic_records",
    "source_ps_partly_unread_user_semantic_records",
)
COUNTER_LIMIT = 4096
UNPROVEN = {
    "DXBC_semantic_to_SPIRV_Location_Component_mapping_verified": False,
    "original_DXBC_readmask_equals_SPIRV_component_identity_verified": False,
    "interpolation_texture_alpha_ShaderLab_or_pixels_verified": False,
    "Unity_Android_Adreno_device_smoke_verified": False,
    "original_compiled_shaders_names_registers_or_paths_published": False,
    "game_assets_modified": False,
}


def checked_private_reflection(raw: dict):
    """Require strictly located, nonduplicated, typed source-safe inputs."""
    if type(raw) is not dict or set(raw) != {"inputs", "outputs", "resource_slots"}:
        raise ValueError("smoke34_invalid_private_SPIRV_reflection_schema")
    rows = raw.get("inputs")
    if (type(rows) is not list or len(rows) > 256 or
        type(raw["outputs"]) is not list or
        type(raw["resource_slots"]) is not dict):
        raise ValueError("smoke34_unbounded_private_SPIRV_reflection")
    seen = set()
    for row in rows:
        if (type(row) is not dict or set(row) != {"location", "type"} or
            type(row["location"]) is not int or
            not 0 <= row["location"] <= 65535 or
            row["location"] in seen):
            raise ValueError("smoke34_invalid_or_duplicate_SPIRV_input_location")
        seen.add(row["location"])
    return inherited.safe_reflected_fragment_input_counts(raw)


def evaluate(pairs: list, temporary: Path, *,
             translator=translate, reflector=reflection,
             parser=dxbc.read_original_dxbc_signatures,
             checker=dxbc.compare_original_vf,
             mask_reader=inherited.private_fragment_readmask,
             spv_counter=checked_private_reflection):
    """Two exact original pairs, private DXBC semantics, aggregate-only output."""
    if (type(pairs) is not list or len(pairs) != PAIRS or
        not isinstance(temporary, Path) or not temporary.is_dir() or
        temporary.is_symlink() or
        any(type(p) is not tuple or len(p) != 2 or
            any(type(code) is not bytes or
                not 0 < len(code) <= MAX_PROGRAM_BYTES for code in p)
            for p in pairs)):
        raise ValueError("smoke34_invalid_original_two_pair_readmask_scope")
    counts = Counter()
    for i, (vs, fs) in enumerate(pairs):
        vertex = parser(vs)
        fragment = parser(fs)
        if (type(vertex) is not dict or type(fragment) is not dict or
            vertex.get("output_tag") not in ("OSGN", "OSG1", "OSG5") or
            fragment.get("input_tag") not in ("ISGN", "ISG1")):
            raise ValueError("smoke34_nonoriginal_DXBC_signature_tags")
        linkage = checker(vertex, fragment)
        if (type(linkage) is not dict or set(linkage) != set(dxbc.COUNTER_FIELDS) or
            any(type(v) is not int or not 0 <= v <= COUNTER_LIMIT
                for v in linkage.values()) or
            linkage["original_programs_read"] != 2 or
            linkage["original_unmatched_fragment_semantic_records"] != 0 or
            linkage["original_matched_semantic_missing_output_component_lanes"] != 0 or
            linkage["original_matched_semantic_type_mismatches"] != 0):
            raise ValueError("smoke34_original_DXBC_VS_FS_semantic_baseline_changed")
        row = mask_reader(fragment["input"])
        if (type(row) is not dict or set(row) != set(MASK_FIELDS) or
            any(type(v) is not int or not 0 <= v <= COUNTER_LIMIT
                for v in row.values()) or
            row["source_ps_user_semantic_records"] !=
                linkage["original_user_fragment_inputs"] or
            row["source_ps_declared_component_lanes"] !=
                linkage["original_fragment_input_mask_components"] or
            row["source_ps_read_component_lanes"] >
                row["source_ps_declared_component_lanes"] or
            row["source_ps_declared_but_unread_component_lanes"] !=
                row["source_ps_declared_component_lanes"] -
                row["source_ps_read_component_lanes"]):
            raise ValueError("smoke34_private_DXBC_readmask_disagrees_with_signed_source")
        # Even a matched semantic might read lanes not present on VS output.
        by_semantic = {(r["semantic"], r["index"]): r
                       for r in vertex["output"] if not r["system_value"]}
        missing_semantics = missing_lanes = 0
        for r in fragment["input"]:
            if r["system_value"]:
                continue
            src = by_semantic.get((r["semantic"], r["index"]))
            if src is None:
                missing_semantics += 1
                missing_lanes += r["used_mask"].bit_count()
            else:
                missing_lanes += (r["used_mask"] & ~src["mask"]).bit_count()
        counts["source_ps_unmatched_vertex_output_semantics"] += missing_semantics
        counts["source_ps_read_component_lanes_not_covered_by_original_vertex_output"] += missing_lanes
        for field in MASK_FIELDS:
            counts[field] += row[field]

        private_dir = temporary / ("source-keyword-" + str(i) + "-ps")
        private_dir.mkdir(exist_ok=False)
        flags = translator(fs, 0, private_dir)
        if (type(flags) is not dict or
            any(flags.get(k) is not True for k in (
                "vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")) or
            ("stage" in flags and flags["stage"] != 0)):
            raise ValueError("smoke34_incomplete_private_DXBC_PS_SPV_roundtrip")
        original = spv_counter(reflector(private_dir / "original.spv"))
        derived = spv_counter(reflector(private_dir / "roundtrip.spv"))
        for values in (original, derived):
            if (type(values) is not dict or set(values) != {"records", "lanes"} or
                any(type(v) is not int or not 0 <= v <= 1024
                    for v in values.values())):
                raise ValueError("smoke34_untrusted_private_SPIRV_input_lane_counts")
        read = row["source_ps_read_component_lanes"]
        counts["passes_examined"] += 1
        counts["source_spirv_fragment_input_records"] += original["records"]
        counts["roundtrip_spirv_fragment_input_records"] += derived["records"]
        counts["source_spirv_fragment_input_component_lanes"] += original["lanes"]
        counts["roundtrip_spirv_fragment_input_component_lanes"] += derived["lanes"]
        counts["passes_readmask_equals_source_spirv_input_lane_count"] += (read == original["lanes"])
        counts["passes_readmask_equals_roundtrip_spirv_input_lane_count"] += (read == derived["lanes"])
        counts["passes_source_spirv_equals_roundtrip_spirv_input_lane_count"] += (
            original["lanes"] == derived["lanes"])
        counts["source_to_spirv_absolute_component_lane_count_difference"] += abs(
            read - original["lanes"])
        counts["roundtrip_to_spirv_absolute_component_lane_count_difference"] += abs(
            read - derived["lanes"])
    if (counts["passes_examined"] != PAIRS or
        counts["source_ps_user_semantic_records"] != 7 or
        counts["source_ps_declared_component_lanes"] != 28 or
        counts["source_ps_unmatched_vertex_output_semantics"] != 0 or
        counts["source_ps_read_component_lanes_not_covered_by_original_vertex_output"] != 0):
        raise ValueError("smoke34_original_signature_source_baseline_changed")
    return {
        "schema_version": 1,
        "status": STATUS,
        "source": "SHA_original_smoke_named_17_renderers_34_slots",
        "source_SHA_scene_count": 6,
        "source_SHA_owner_count": 4,
        "original_exact_keyword_matched_pairs": PAIRS,
        "counts": {field: int(counts[field]) for field in FIELDS},
        "original_DXBC_VS_FS_semantic_identity_checked": True,
        **UNPROVEN,
    }


def probe(source_root: Path, manifest: Path, *,
          translator=translate, reflector=reflection):
    # SHA original smoke selector is independent of the 921-use and 108-use
    # different shaders; add no guessed new selector.
    from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
    from scripts.t3_original_renderer_shader_impact import SHADER_OWNERS_SELECTED
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts import t3_original_smoke34_dxbc_program_inventory as inventory
    from scripts import t3_original_smoke34_spirv_translation as stages
    import UnityPy
    selected, state = original_private_smoke_target(source_root, manifest)
    if (type(state) is not dict or
        state.get("original_pass_color_mask_shaderlab_channels") != "RGB" or
        state.get("original_pass_color_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("smoke34_original_RGB_alpha_blend_pass_identity_changed")
    owner, private_path_id = selected
    if owner not in SHADER_OWNERS_SELECTED:
        raise ValueError("smoke34_wrong_original_source_owner")
    path = source_root / "Raft_Data" / owner
    if path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("smoke34_original_source_owner_SHA_changed")
    objects = [o for o in UnityPy.load(str(path)).file.objects.values()
               if o.path_id == private_path_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("smoke34_original_shader_object_identity_changed")
    shader = objects[0].read_typetree()
    tables = [records(rows) for p, rows in decoded_platforms(shader) if p == 4]
    if len(tables) != 1:
        raise ValueError("smoke34_original_d3d11_platform_table_ambiguous")
    baseline = inventory.classify(tables[0], shader.get("m_ParsedForm"))
    if (baseline.get("status") != inventory.STATUS or
        baseline.get("original_D3D11_platform_table_records") != 8 or
        baseline.get("matched_vertex_fragment_permutation_pairs") != PAIRS or
        baseline.get("unmatched_vertex_permutations") != 0 or
        baseline.get("unmatched_fragment_permutations") != 0):
        raise ValueError("smoke34_original_two_pair_source_baseline_changed")
    private_pairs = stages.exact_two_pairs(shader.get("m_ParsedForm"), tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-smoke34-ps-readmask-private-") as td:
        return evaluate(private_pairs, Path(td), translator=translator,
                        reflector=reflector)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original", "manifest", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("smoke34_unsafe_private_report_destination")
    try:
        report = probe(args.original, args.manifest)
    except Exception as err:
        # Only the exception type; private parser values and tool stdout
        # must never escape the disposable private runner.
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "exception_type": type(err).__name__, **UNPROVEN}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("T3_SMOKE34_ORIGINAL_PS_READMASK_SPV " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
