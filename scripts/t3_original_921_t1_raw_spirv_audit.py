#!/usr/bin/env python3
"""T3: independent T1 binary SPIR-V stage-component audit on original Shader48.

Original SHA-pinned DXBC pairs and intermediate SPIR-V/HLSL remain runner-private.
T1's source-free direct OpEntryPoint/OpDecorate validator is reused unchanged.
This does not map private original DXBC semantics to numeric SPIR-V locations.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile

from scripts import t3_original_921_dxbc_semantic_join as sem
from scripts import t3_original_921_dxbc_readmask_spirv as previous
from scripts import t1_spirv_interface_component_audit as t1
from scripts.w1_recover_graphics_programs import translate as translate_original

STATUS = "ORIGINAL_921_FOURPASS_DIRECT_SPIRV_NUMERIC_INTERFACE_MEASURED"
SHAPE = frozenset((
    "vertex_components", "fragment_components", "missing_components",
    "scalar_type_mismatches", "unused_vertex_components", "compatible_numeric_coverage",
))
COUNTS = (
    "passes_examined",
    "original_DXBC_read_component_lanes",
    "original_DXBC_declared_fragment_component_lanes",
    "source_spirv_vertex_components", "source_spirv_fragment_components",
    "roundtrip_spirv_vertex_components", "roundtrip_spirv_fragment_components",
    "source_spirv_missing_fragment_components",
    "roundtrip_spirv_missing_fragment_components",
    "source_spirv_type_mismatches", "roundtrip_spirv_type_mismatches",
    "source_spirv_unused_vertex_components", "roundtrip_spirv_unused_vertex_components",
    "source_passes_numeric_compatible", "roundtrip_passes_numeric_compatible",
    "source_passes_readmask_equals_direct_fragment_components",
    "roundtrip_passes_readmask_equals_direct_fragment_components",
    "source_and_roundtrip_passes_direct_fragment_count_equal",
    "source_vs_roundtrip_fragment_component_abs_difference",
    "source_vs_DXBC_read_component_abs_difference",
    "roundtrip_vs_DXBC_read_component_abs_difference",
)


def private_module_disassemble(path: Path):
    if (type(path) is not Path or path.is_symlink() or not path.is_file() or
            not 20 <= path.stat().st_size <= 1024 * 1024):
        raise ValueError("invalid_private_original_SPIRV_stage_size")
    subprocess.run(["spirv-val", "--target-env", "vulkan1.1", str(path)],
                   check=True, capture_output=True, timeout=25)
    program = subprocess.run(["spirv-dis", "--raw-id", str(path)],
                             check=True, capture_output=True, text=True, timeout=25)
    if not (0 < len(program.stdout) <= 8 * 1024 * 1024):
        raise ValueError("invalid_private_original_SPIRV_disassembly_size")
    # Never print or return outside this local private runner.
    return program.stdout


def safe_numeric_audit(raw_vertex: str, raw_fragment: str, checker=t1.audit):
    if not (type(raw_vertex) is str and type(raw_fragment) is str
            and 0 < len(raw_vertex) <= 8 * 1024 * 1024
            and 0 < len(raw_fragment) <= 8 * 1024 * 1024):
        raise ValueError("untrusted_private_original_SPIRV_input_text")
    result = checker(raw_vertex, raw_fragment)
    if type(result) is not dict or set(result) != SHAPE:
        raise ValueError("invalid_T1_private_SPIRV_numeric_contract_shape")
    if type(result["compatible_numeric_coverage"]) is not bool:
        raise ValueError("invalid_T1_private_SPIRV_compatibility_type")
    for name in SHAPE - {"compatible_numeric_coverage"}:
        if type(result[name]) is not int or not 0 <= result[name] <= 1024:
            raise ValueError("invalid_T1_private_SPIRV_numeric_count")
    if (result["missing_components"] > result["fragment_components"] or
        result["scalar_type_mismatches"] > result["fragment_components"] or
        result["unused_vertex_components"] > result["vertex_components"] or
        result["compatible_numeric_coverage"] !=
        (result["missing_components"] == result["scalar_type_mismatches"] == 0)):
        raise ValueError("contradictory_T1_private_SPIRV_numeric_result")
    return result


def original_fourpass_private(pairs: list, root: Path, *,
                              translator=translate_original,
                              disassembler=private_module_disassemble,
                              numeric_checker=safe_numeric_audit,
                              original_parser=sem.read_original_dxbc_signatures):
    if (type(pairs) is not list or
        len(pairs) != sem.fourpass.SOURCE_NORMAL_PASSES or
        not root.is_dir() or root.is_symlink()):
        raise ValueError("not_four_SHA_original_Shader48_Pass_pairs")
    count = Counter()
    for index, pair in enumerate(pairs):
        if (type(pair) is not tuple or len(pair) != 2 or
            any(type(code) is not bytes or not code for code in pair)):
            raise ValueError("invalid_private_original_DXBC_compiled_stage_pair")
        vcode, fcode = pair
        vs, ps = original_parser(vcode), original_parser(fcode)
        contracted = sem.compare_original_vf(vs, ps)
        if (contracted["original_unmatched_fragment_semantic_records"] or
            contracted["original_matched_semantic_type_mismatches"] or
            contracted["original_matched_semantic_missing_output_component_lanes"]):
            raise ValueError("original_DXBC_semantic_baseline_has_deficit")
        ps_mask = previous.private_fragment_readmask(ps["input"])
        count["original_DXBC_read_component_lanes"] += ps_mask["source_ps_read_component_lanes"]
        count["original_DXBC_declared_fragment_component_lanes"] += ps_mask["source_ps_declared_component_lanes"]
        stage_paths = {}
        for stage, code in ((1, vcode), (0, fcode)):
            destination = root / ("source-pass-" + str(index) + "-stage-" + str(stage))
            destination.mkdir(exist_ok=False)
            converted = translator(code, stage, destination)
            if (type(converted) is not dict or
                    any(converted.get(flag) is not True for flag in
                        ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid"))):
                raise ValueError("original_SPIRV_stage_compiler_incomplete")
            stage_paths[stage] = destination
        per = {}
        for label, rel in (("source", "original.spv"), ("roundtrip", "roundtrip.spv")):
            vtext = disassembler(stage_paths[1] / rel)
            ftext = disassembler(stage_paths[0] / rel)
            approved = numeric_checker(vtext, ftext)
            per[label] = approved
            for target, key in (
                ("vertex_components", "vertex_components"),
                ("fragment_components", "fragment_components"),
                ("missing_fragment_components", "missing_components"),
                ("type_mismatches", "scalar_type_mismatches"),
                ("unused_vertex_components", "unused_vertex_components"),
            ):
                count[label + "_spirv_" + target] += approved[key]
            count[label + "_passes_numeric_compatible"] += int(approved["compatible_numeric_coverage"])
            count[label + "_passes_readmask_equals_direct_fragment_components"] += (
                ps_mask["source_ps_read_component_lanes"] == approved["fragment_components"])
            count[label + "_vs_DXBC_read_component_abs_difference"] += abs(
                approved["fragment_components"] - ps_mask["source_ps_read_component_lanes"])
        count["source_and_roundtrip_passes_direct_fragment_count_equal"] += (
            per["source"]["fragment_components"] == per["roundtrip"]["fragment_components"])
        count["source_vs_roundtrip_fragment_component_abs_difference"] += abs(
            per["source"]["fragment_components"] - per["roundtrip"]["fragment_components"])
        count["passes_examined"] += 1
    if count["passes_examined"] != sem.fourpass.SOURCE_NORMAL_PASSES:
        raise ValueError("partial_original_Shader48_SPIRV_stage_pair_coverage")
    return {
        "schema_version": 1,
        "status": STATUS,
        "source_scope": "original_SHA_pinned_921_use_Shader48_4_original_compiled_DXBC_VF_Pass_pairs",
        "counts": {name: int(count[name]) for name in COUNTS},
        "original_DXBC_semantic_name_index_to_SPIRV_Location_mapping_proven": False,
        "original_interpolation_and_pixel_equivalence_proven": False,
        "original_Android_Adreno_device_pixels_verified": False,
        "original_sources_assets_modified": False,
        "private_names_compiled_programs_source_or_SPIRV_published": False,
    }


def probe(source: Path, manifest: Path):
    graph_slots = {}
    graph = sem.prior.original.load_original(
        source, manifest, private_slot_counts=graph_slots)
    owner, obj_id = sem.prior.feasibility.selected_high_use(graph_slots, graph)
    owner_path = source / "Raft_Data" / owner
    if owner_path.is_symlink() or sem.prior.fingerprint(owner_path) != sem.prior.SHADER_OWNERS[owner]:
        raise ValueError("original_source_Shader48_owner_SHA_mismatch")
    import UnityPy
    objects = [o for o in UnityPy.load(str(owner_path)).file.objects.values()
               if o.path_id == obj_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_Shader48_selected_object_changed")
    tree = objects[0].read_typetree()
    versions = [sem.prior.records(segments)
                for platform, segments in sem.prior.decoded_platforms(tree) if platform == 4]
    if len(versions) != 1:
        raise ValueError("original_D3D11_platform_not_unique")
    parsed, table = tree["m_ParsedForm"], versions[0]
    v = sem.prior.feasibility.summarize(parsed, table)
    if (v["original_source_Shader48_pass_count"] != sem.fourpass.SOURCE_NORMAL_PASSES or
        v["non_normal_passes_not_stage_linked"] != 0 or
        v["matched_vertex_fragment_permutation_pairs"] != sem.fourpass.SOURCE_TOTAL_MATCHED_VARIANTS or
        v["unmatched_vertex_permutations"] != sem.fourpass.SOURCE_UNMATCHED_VERTEX or
        v["unmatched_fragment_permutations"] != sem.fourpass.SOURCE_UNMATCHED_FRAGMENT):
        raise ValueError("original_Shader48_permutation_scope_changed")
    with tempfile.TemporaryDirectory(prefix="t3-private-original-T1-raw-SPIRV-") as root:
        value = original_fourpass_private(
            sem.fourpass.exact_pass_samples(parsed, table), Path(root))
    value.update({
        "original_source_scenes_SHA_verified": 6,
        "original_source_owners_SHA_verified": 4,
        "original_renderer_material_slot_uses": 921,
        "source_exact_matched_variant_pairs_total": sem.fourpass.SOURCE_TOTAL_MATCHED_VARIANTS,
        "original_unpaired_vertex_variants_untranslated": sem.fourpass.SOURCE_UNMATCHED_VERTEX,
    })
    return value


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("invalid_original_private_SPIRV_audit_report_path")
    try:
        result = probe(args.original, args.manifest)
    except Exception as err:
        # Suppress original shader compiler/semantic error details.
        result = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "failure_exception_type": type(err).__name__,
            "original_Android_Adreno_device_pixels_verified": False,
            "private_names_compiled_programs_source_or_SPIRV_published": False,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("T3_ORIGINAL_921_T1_DIRECT_SPIRV " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
