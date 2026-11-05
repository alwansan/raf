#!/usr/bin/env python3
"""Authenticated Shader48 original PixelShader DXBC read-mask ↔ SPIR-V input counts.

Comparisons are per exactly matched source Pass, then aggregate counts ONLY.
Equality of cardinalities cannot link DXBC SemanticName/Index/Register to
SPIR-V Location/Component, prove interpolation, ShaderLab or Android pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from scripts import t3_original_921_dxbc_semantic_join as sem
from scripts.t3_vf_spirv_component_coverage import _type_components
from scripts.w1_recover_graphics_programs import translate as translate_original
from scripts.w1_recover_depth_passes import reflection as safe_reflection

STATUS = "ORIGINAL_921_DXBC_PS_READ_MASK_VS_SPIRV_INPUT_COUNTS_MEASURED"
FIELDS = (
    "passes_examined",
    "source_ps_user_semantic_records",
    "source_ps_system_value_records",
    "source_ps_declared_component_lanes",
    "source_ps_read_component_lanes",
    "source_ps_declared_but_unread_component_lanes",
    "source_ps_completely_unread_user_semantic_records",
    "source_ps_partly_unread_user_semantic_records",
    "source_ps_read_component_lanes_not_covered_by_original_vertex_output",
    "source_ps_unmatched_vertex_output_semantics",
    "source_spirv_fragment_input_records",
    "source_spirv_fragment_input_component_lanes",
    "roundtrip_spirv_fragment_input_records",
    "roundtrip_spirv_fragment_input_component_lanes",
    "passes_readmask_equals_source_spirv_input_lane_count",
    "passes_readmask_equals_roundtrip_spirv_input_lane_count",
    "passes_source_spirv_equals_roundtrip_spirv_input_lane_count",
    "source_to_spirv_absolute_component_lane_count_difference",
    "roundtrip_to_spirv_absolute_component_lane_count_difference",
)

_PRIVATE_ROW_FIELDS = frozenset((
    "semantic", "index", "system_value", "type", "register",
    "mask", "used_mask", "stream",
))


def private_fragment_readmask(rows: list):
    """Use DXBC ISGN/ISG1 read-mask only. Never invert output OSGN bits here.

    DXBC signature ReadWriteMask for INPUT is a bitmask of actually read
    channels, while Mask is declared/allocated channels. The low nibble of
    both is bounded and documented by vkd3d's DXBC signature parser.
    """
    if type(rows) is not list or len(rows) > 256:
        raise ValueError("untrusted_private_fragment_input_signature_list")
    out = Counter()
    for row in rows:
        if type(row) is not dict or set(row) != _PRIVATE_ROW_FIELDS:
            raise ValueError("untrusted_private_DXBC_signature_record_shape")
        if (type(row["system_value"]) is not int or
            type(row["mask"]) is not int or
            type(row["used_mask"]) is not int or
            type(row["register"]) is not int or
            type(row["type"]) is not int or
            type(row["stream"]) is not int or
            type(row["index"]) is not int or
            type(row["semantic"]) is not str):
            raise ValueError("invalid_private_fragment_DXBC_signature_field")
        if row["system_value"] != 0:
            out["source_ps_system_value_records"] += 1
            continue
        declared, read = row["mask"], row["used_mask"]
        if (not 1 <= declared <= 15 or not 0 <= read <= 15
                or read & ~declared):
            raise ValueError("invalid_private_fragment_read_mask_subset")
        out["source_ps_user_semantic_records"] += 1
        out["source_ps_declared_component_lanes"] += declared.bit_count()
        out["source_ps_read_component_lanes"] += read.bit_count()
        out["source_ps_declared_but_unread_component_lanes"] += (
            declared & ~read).bit_count()
        out["source_ps_completely_unread_user_semantic_records"] += (read == 0)
        out["source_ps_partly_unread_user_semantic_records"] += (read != declared and read != 0)
    return {name: int(out[name]) for name in (
        "source_ps_user_semantic_records",
        "source_ps_system_value_records",
        "source_ps_declared_component_lanes",
        "source_ps_read_component_lanes",
        "source_ps_declared_but_unread_component_lanes",
        "source_ps_completely_unread_user_semantic_records",
        "source_ps_partly_unread_user_semantic_records",
    )}


def safe_reflected_fragment_input_counts(reflect: dict):
    """Count validated SPIRV-Cross user input vectors, *not* semantic identities."""
    if type(reflect) is not dict or set(reflect) != {
            "inputs", "outputs", "resource_slots"}:
        raise ValueError("unexpected_private_SPIRV_safe_reflection_contract")
    rows = reflect["inputs"]
    if type(rows) is not list or len(rows) > 256 or type(reflect["resource_slots"]) is not dict:
        raise ValueError("unbounded_private_SPIRV_input_rows")
    lanes = 0
    for row in rows:
        if (type(row) is not dict or set(row) != {"location", "type"} or
            type(row["location"]) is not int or
            not 0 <= row["location"] <= 65535):
            raise ValueError("untrusted_private_SPIRV_input_row")
        family = _type_components(row["type"])
        if family is None:
            raise ValueError("unsupported_SPIRV_fragment_input_type")
        lanes += family[1]
        if lanes > 1024:
            raise ValueError("unbounded_SPIRV_input_lane_count")
    return {"records": len(rows), "lanes": lanes}


def evaluate_private_fourpass(private_code_pairs: list, private_root: Path, *,
                              translator=translate_original,
                              reflector=safe_reflection,
                              parser=sem.read_original_dxbc_signatures,
                              match_checker=sem.compare_original_vf):
    """Four real matched source pair samples; no original names escape result."""
    if (type(private_code_pairs) is not list or
        len(private_code_pairs) != sem.fourpass.SOURCE_NORMAL_PASSES or
        not private_root.is_dir() or private_root.is_symlink()):
        raise ValueError("not_original_fourpass_private_mask_scope")
    counts = Counter()
    for i, pair in enumerate(private_code_pairs):
        if (type(pair) is not tuple or len(pair) != 2 or
                any(type(c) is not bytes or not c for c in pair)):
            raise ValueError("not_compiled_original_fourpass_pair")
        vertex, fragment = pair
        orig_vertex = parser(vertex)
        orig_fragment = parser(fragment)
        if (orig_fragment.get("input_tag") not in ("ISGN", "ISG1") or
                orig_vertex.get("output_tag") not in ("OSGN", "OSG1", "OSG5")):
            raise ValueError("not_original_shader_signature_input_output")
        baseline = match_checker(orig_vertex, orig_fragment)
        if type(baseline) is not dict or (
            baseline.get("original_unmatched_fragment_semantic_records") or
            baseline.get("original_matched_semantic_missing_output_component_lanes") or
            baseline.get("original_matched_semantic_type_mismatches")):
            raise ValueError("source_original_DXBC_semantic_linkage_baseline_changed")
        private_mask = private_fragment_readmask(orig_fragment["input"])
        counts.update(private_mask)
        # A matched DXBC semantic can still have an unavailable read component
        # on the vertex output: compare the *read* channel mask in private.
        v_by_semantic = {
            (r["semantic"], r["index"]): r for r in orig_vertex["output"]
            if not r["system_value"]
        }
        for row in orig_fragment["input"]:
            if row["system_value"]:
                continue
            vertex_row = v_by_semantic.get((row["semantic"], row["index"]))
            if vertex_row is None:
                counts["source_ps_unmatched_vertex_output_semantics"] += 1
                counts["source_ps_read_component_lanes_not_covered_by_original_vertex_output"] += (
                    row["used_mask"].bit_count())
            else:
                counts["source_ps_read_component_lanes_not_covered_by_original_vertex_output"] += (
                    row["used_mask"] & ~vertex_row["mask"]).bit_count()
        dst = private_root / ("source-pass-" + str(i) + "-original-ps")
        dst.mkdir(exist_ok=False)
        translator_report = translator(fragment, 0, dst)
        if (type(translator_report) is not dict or
                translator_report.get("vulkan11_valid") is not True or
                translator_report.get("hlsl_recovered") is not True or
                translator_report.get("roundtrip_vulkan11_valid") is not True):
            raise ValueError("partial_original_PS_SPIRV_HLSL_roundtrip")
        original_spv = safe_reflected_fragment_input_counts(reflector(dst / "original.spv"))
        roundtrip_spv = safe_reflected_fragment_input_counts(reflector(dst / "roundtrip.spv"))
        declared_read = private_mask["source_ps_read_component_lanes"]
        counts["passes_examined"] += 1
        counts["source_spirv_fragment_input_records"] += original_spv["records"]
        counts["source_spirv_fragment_input_component_lanes"] += original_spv["lanes"]
        counts["roundtrip_spirv_fragment_input_records"] += roundtrip_spv["records"]
        counts["roundtrip_spirv_fragment_input_component_lanes"] += roundtrip_spv["lanes"]
        counts["passes_readmask_equals_source_spirv_input_lane_count"] += (
            declared_read == original_spv["lanes"])
        counts["passes_readmask_equals_roundtrip_spirv_input_lane_count"] += (
            declared_read == roundtrip_spv["lanes"])
        counts["passes_source_spirv_equals_roundtrip_spirv_input_lane_count"] += (
            original_spv["lanes"] == roundtrip_spv["lanes"])
        counts["source_to_spirv_absolute_component_lane_count_difference"] += (
            abs(declared_read - original_spv["lanes"]))
        counts["roundtrip_to_spirv_absolute_component_lane_count_difference"] += (
            abs(declared_read - roundtrip_spv["lanes"]))
    if counts["passes_examined"] != sem.fourpass.SOURCE_NORMAL_PASSES:
        raise ValueError("incomplete_original_fragment_readmask_scope")
    # Public report names are immutable, no semantics or private row keys.
    return {
        "schema_version": 1,
        "status": STATUS,
        "scope": "same_exact_original_4_Pass_pairs_PS_DXBC_ISGN_and_source_roundtrip_SPIRV",
        "counts": {k: int(counts[k]) for k in FIELDS},
        "SPIRV_name_Location_to_original_DXBC_semantic_mapping_proven": False,
        "original_DXBC_register_readmask_vs_SPIRV_same_component_identity_proven": False,
        "interpolation_ShaderLab_color_or_pixel_fidelity_proven": False,
        "Unity_Android_Adreno_pixels_verified": False,
        "private_names_bytecode_or_compiler_code_published": False,
        "original_assets_changed": False,
    }


def probe(source: Path, manifest: Path):
    # Reuse SHA-authenticated 6-scene/4-owner Shader48 selection; it must pick
    # the same exact original DXBC pair samples as earlier source experiments.
    original_counts = {}
    graph = sem.prior.original.load_original(
        source, manifest, private_slot_counts=original_counts)
    owner, object_id = sem.prior.feasibility.selected_high_use(original_counts, graph)
    candidate = source / "Raft_Data" / owner
    if (candidate.is_symlink() or
            sem.prior.fingerprint(candidate) != sem.prior.SHADER_OWNERS[owner]):
        raise ValueError("source_SHA_authenticated_Shader48_owner_changed")
    import UnityPy
    originals = [obj for obj in UnityPy.load(str(candidate)).file.objects.values()
                 if obj.path_id == object_id]
    if len(originals) != 1 or originals[0].type.name != "Shader":
        raise ValueError("original_Shader48_exact_object_not_found")
    tree = originals[0].read_typetree()
    versions = [sem.prior.records(rows)
                for platform, rows in sem.prior.decoded_platforms(tree) if platform == 4]
    if len(versions) != 1:
        raise ValueError("original_D3D11_platform_not_unique")
    parsed, table = tree["m_ParsedForm"], versions[0]
    baseline = sem.prior.feasibility.summarize(parsed, table)
    if (baseline["original_source_Shader48_pass_count"] !=
            sem.fourpass.SOURCE_NORMAL_PASSES or
            baseline["non_normal_passes_not_stage_linked"] != 0 or
            baseline["matched_vertex_fragment_permutation_pairs"] !=
            sem.fourpass.SOURCE_TOTAL_MATCHED_VARIANTS or
            baseline["unmatched_vertex_permutations"] !=
            sem.fourpass.SOURCE_UNMATCHED_VERTEX or
            baseline["unmatched_fragment_permutations"] !=
            sem.fourpass.SOURCE_UNMATCHED_FRAGMENT):
        raise ValueError("source_Shader48_original_permutation_baseline_changed")
    original_pairs = sem.fourpass.exact_pass_samples(parsed, table)
    with tempfile.TemporaryDirectory(prefix="t3-921-original-ps-readmask-private-") as t:
        result = evaluate_private_fourpass(original_pairs, Path(t))
    result.update({
        "source_original_scenes_SHA_authenticated": 6,
        "source_original_owners_SHA_authenticated": 4,
        "original_renderer_material_slot_uses": 921,
        "original_exact_matched_permutation_pairs_total":
            sem.fourpass.SOURCE_TOTAL_MATCHED_VARIANTS,
        "source_unpaired_vertex_permutations_untranslated":
            sem.fourpass.SOURCE_UNMATCHED_VERTEX,
    })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
            args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_private_PS_readmask_output_path")
    try:
        result = probe(args.original, args.manifest)
    except Exception as err:
        # The error string may be sourced from private bytecode/parsers, so
        # never log it. Publish only its Python exception category.
        result = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "failure_exception_type": type(err).__name__,
            "private_names_bytecode_or_compiler_code_published": False,
            "Unity_Android_Adreno_pixels_verified": False,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("T3_ORIGINAL_921_PS_READMASK_SPIRV " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
