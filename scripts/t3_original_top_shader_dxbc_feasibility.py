#!/usr/bin/env python3
"""Source-authentic original highest-use six-scene Shader48 D3D11 stage feasibility.

Selects the *source* Shader48 with exactly 921 original Renderer Material-slot
references using SHA-pinned six-scene/4-owner graph; never name-match or output
private source identities/bytecode. Compares original parsed pass/variant
bindings to its own D3D11 blob entries. This is NOT an authored ShaderLab
replacement, compiled Unity Android import, visual parity or device proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as original
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key

STATUS = "ORIGINAL_HIGH_USE_SHADER48_D3D11_PROGRAM_LINKAGE_SOURCE_ONLY"
MAX_PASSES = 512
MAX_VARIANTS = 16384
EXPECTED_TYPED_SOURCE_TARGETS = 21
EXPECTED_TYPED_SOURCE_SLOTS = 1633
EXPECTED_TOP_USE = 921


def selected_high_use(private_slot_counts: dict, source_report: dict):
    if (type(source_report) is not dict or
        source_report.get("status") != original.STATUS or
        source_report.get("six_original_scenes_sha_verified") is not True or
        source_report.get("counts", {}).get("original_slots_to_verified_Shader48") != EXPECTED_TYPED_SOURCE_SLOTS or
        source_report.get("original_distinct_typed_Shader48_targets") != EXPECTED_TYPED_SOURCE_TARGETS or
        type(private_slot_counts) is not dict):
        raise ValueError("unauthenticated_original_six_scene_Shader_population")
    typed = {key: count for key, count in private_slot_counts.items()
             if key[0] in original.SHADER_OWNERS_SELECTED}
    if (len(typed) != EXPECTED_TYPED_SOURCE_TARGETS or
        sum(typed.values()) != EXPECTED_TYPED_SOURCE_SLOTS or
        max(typed.values()) != EXPECTED_TOP_USE or
        sum(count == EXPECTED_TOP_USE for count in typed.values()) != 1 or
        any(type(count) is not int or count <= 0 for count in typed.values())):
        raise ValueError("original_high_use_shader48_unique_slot_scope_mismatch")
    top = max(typed, key=typed.get)
    if (type(top) is not tuple or len(top) != 2 or
        top[0] not in original.SHADER_OWNERS_SELECTED or
        type(top[1]) is not int or top[1] <= 0):
        raise ValueError("invalid_high_use_original_Shader48_object_identity")
    return top


def summarize(parsed: dict, table: list, *, link=linked_program):
    """Fail-closed stage links; entry contents/hashes never appear in output."""
    if type(parsed) is not dict or type(parsed.get("m_SubShaders")) is not list:
        raise ValueError("missing_original_921_ShaderLab_parsed_structure")
    subshaders = parsed["m_SubShaders"]
    if not subshaders:
        raise ValueError("original_921_Shader_has_no_SubShader")
    if type(table) is not list or not table:
        raise ValueError("empty_original_D3D11_shader_program_table")
    counts = Counter()
    distinct_programs = set()
    pass_types = Counter()
    per_subshader = []
    for sub in subshaders:
        if type(sub) is not dict or type(sub.get("m_Passes")) is not list:
            raise ValueError("invalid_source_SubShader_pass_layout")
        count = len(sub["m_Passes"])
        per_subshader.append(count)
        for p in sub["m_Passes"]:
            counts["original_passes"] += 1
            if counts["original_passes"] > MAX_PASSES or type(p) is not dict or type(p.get("m_Type")) is not int:
                raise ValueError("invalid_or_oversized_original_Shader_pass")
            kind = p["m_Type"]
            if kind < 0 or kind > 32:
                raise ValueError("unsupported_original_pass_type")
            pass_types[kind] += 1
            if kind != 0:
                counts["non_normal_passes_not_stage_linked"] += 1
                continue
            counts["normal_passes"] += 1
            variant_keys = {}
            for field, stage in (("progVertex", 1), ("progFragment", 0)):
                program = p.get(field)
                if type(program) is not dict:
                    raise ValueError("missing_normal_pass_original_stage")
                variants = stage_variants(program)
                counts["all_stage_variant_records"] += len(variants)
                if counts["all_stage_variant_records"] > MAX_VARIANTS:
                    raise ValueError("high_use_Shader_variant_budget_exceeded")
                keys = set()
                for bucket, ordinal, meta in variants:
                    if (type(meta) is not dict or
                        (bucket is not None and (type(bucket) is not int or bucket < 0)) or
                        type(ordinal) is not int or ordinal < 0):
                        raise ValueError("invalid_original_source_stage_variant")
                    code, _private = link(meta, table, stage)
                    if type(code) is not bytes or not code:
                        raise ValueError("missing_genuine_original_D3D11_stage_program")
                    distinct_programs.add(hashlib.sha256(code).digest())
                    counts["vertex_variant_records" if stage == 1 else "fragment_variant_records"] += 1
                    counts["stage_variants_with_keywords"] += bool(meta.get("m_KeywordIndices") or
                        meta.get("m_GlobalKeywordIndices") or meta.get("m_LocalKeywordIndices"))
                    key = variant_key(meta)
                    if key in keys:
                        raise ValueError("duplicated_original_stage_variant_permutation")
                    keys.add(key)
                variant_keys[stage] = keys
            shared = variant_keys[1] & variant_keys[0]
            counts["matched_original_vertex_fragment_permutation_pairs"] += len(shared)
            counts["normal_passes_with_matched_variant_pair"] += bool(shared)
            counts["normal_passes_without_matched_variant_pair"] += not bool(shared)
            counts["unmatched_vertex_permutations"] += len(variant_keys[1] - shared)
            counts["unmatched_fragment_permutations"] += len(variant_keys[0] - shared)
    if not counts["original_passes"]:
        raise ValueError("original_921_Shader_has_no_passes")
    return {
        "schema_version": 1,
        "status": STATUS,
        "original_source_Shader48_SubShader_count": len(subshaders),
        "original_source_Shader48_pass_count": counts["original_passes"],
        "original_source_pass_counts_per_SubShader": per_subshader,
        "original_source_pass_types_aggregate": {str(k):v for k,v in sorted(pass_types.items())},
        "normal_passes": counts["normal_passes"],
        "non_normal_passes_not_stage_linked": counts["non_normal_passes_not_stage_linked"],
        "genuine_D3D11_vertex_stage_variant_records": counts["vertex_variant_records"],
        "genuine_D3D11_fragment_stage_variant_records": counts["fragment_variant_records"],
        "distinct_original_linked_D3D11_programs": len(distinct_programs),
        "matched_vertex_fragment_permutation_pairs": counts["matched_original_vertex_fragment_permutation_pairs"],
        "normal_passes_with_matched_permutation_pair": counts["normal_passes_with_matched_variant_pair"],
        "normal_passes_without_matched_permutation_pair": counts["normal_passes_without_matched_variant_pair"],
        "unmatched_vertex_permutations": counts["unmatched_vertex_permutations"],
        "unmatched_fragment_permutations": counts["unmatched_fragment_permutations"],
        "stage_variants_with_keywords": counts["stage_variants_with_keywords"],
        "full_authored_ShaderLab_program_or_variant_equivalence_proven": False,
        "original_D3D11_bytecode_or_private_ids_published": False,
        "native_Android_Adreno_gpu_execution_verified": False,
        "original_Unity_Assets_changed": False,
    }


def probe(source: Path, manifest: Path):
    private = {}
    source_report = original.load_original(source, manifest, private_slot_counts=private)
    top = selected_high_use(private, source_report)
    owner, original_id = top
    path = source / "Raft_Data" / owner
    if any(p.is_symlink() for p in (path, *path.parents)) or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("original_top_Shader_owner_provenance_mismatch")
    import UnityPy
    file = UnityPy.load(str(path)).file
    objects = [obj for obj in file.objects.values() if obj.path_id == original_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("top_original_Shader48_identity_or_type_drift")
    tree = objects[0].read_typetree()
    tables = []
    for platform, segments in decoded_platforms(tree):
        if platform == 4:  # Unity D3D11 compiled graphics program
            tables.append(records(segments))
    if len(tables) != 1:
        raise ValueError("missing_or_ambiguous_original_D3D11_program_platform")
    result = summarize(tree.get("m_ParsedForm"), tables[0])
    result.update({
        "source_authenticated_original_scene_count": 6,
        "source_authenticated_original_Shader_owner_count": 4,
        "highest_source_Shader_renderer_Material_slot_references": EXPECTED_TOP_USE,
        "selected_source_Shader_class": "Shader48",
        "original_D3D11_program_table_records": len(tables[0]),
        "same_export_ShaderLab_or_full_native_restorer_program_equivalence_proven": False,
    })
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_source_program_feasibility_report")
    try:
        output = probe(args.original, args.manifest)
    except Exception as error:
        output = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "exception_type": type(error).__name__,
            "full_authored_ShaderLab_program_or_variant_equivalence_proven": False,
            "original_D3D11_bytecode_or_private_ids_published": False,
            "native_Android_Adreno_gpu_execution_verified": False,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n", encoding="utf8")
    print("T3_ORIGINAL_921_SHADER_D3D11_FEASIBILITY " + json.dumps(output, sort_keys=True))
    return 0 if output["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
