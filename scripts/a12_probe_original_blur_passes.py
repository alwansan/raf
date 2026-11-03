"""A12 SHA-pinned original Subsurface Blur pass/stage recovery feasibility.

Original Shader name is an exact publicly known gate target. Actual original
source/bytecode, other private names, GUIDs and per-object identifiers stay
inside the disposable CI runner; only counts and SHA commitments are emitted.
This does not install or synthesize any shader.
"""
import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path

from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key

TARGET = "UltimateWater/Utilities/Blur (Subsurface Scattering)"
MIN_PASSES = 2
MAX_PASSES = 128
MAX_VARIANTS_PER_STAGE = 96
MAX_TOTAL_VARIANTS = 2048


def inspect_shader(parsed, entries):
    """Fail closed on unknown original graphics linkage, but do not invent passes."""
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Subsurface Blur identity mismatch")
    subshaders = parsed.get("m_SubShaders")
    if not isinstance(subshaders, list) or not subshaders:
        raise ValueError("Missing original subshader graph")
    counts = Counter()
    programs = set()
    variant_pairs = 0
    per_subshader = []
    for subshader in subshaders:
        passes = subshader.get("m_Passes") if isinstance(subshader, dict) else None
        if not isinstance(passes, list):
            raise ValueError("Invalid original pass layout")
        per_subshader.append(len(passes))
        for shader_pass in passes:
            counts["original_passes"] += 1
            if counts["original_passes"] > MAX_PASSES:
                raise ValueError("Original water pass count exceeds budget")
            if not isinstance(shader_pass, dict) or type(shader_pass.get("m_Type")) is not int:
                raise ValueError("Invalid original pass type")
            counts["pass_type_" + str(shader_pass["m_Type"])] += 1
            mapping = {}
            for field, stage in (("progVertex", 1), ("progFragment", 0)):
                program = shader_pass.get(field)
                if not isinstance(program, dict):
                    raise ValueError("Missing original pass stage program")
                variants = stage_variants(program)
                counts["stage_" + str(stage) + "_variants"] += len(variants)
                if len(variants) > MAX_VARIANTS_PER_STAGE or counts["stage_0_variants"] + counts["stage_1_variants"] > MAX_TOTAL_VARIANTS:
                    raise ValueError("Original shader variant budget exceeded")
                mapping[stage] = set()
                for bucket, vi, metadata in variants:
                    code, source_ref = linked_program(metadata, entries, stage)
                    programs.add(hashlib.sha256(code).hexdigest())
                    mapping[stage].add((bucket, variant_key(metadata)))
                    counts["linked_stage_programs"] += 1
                    if metadata.get("m_KeywordIndices"):
                        counts["stages_with_keyword_permutations"] += 1
                    # Guard the independent parameter-block indexing, which the
                    # prior Depth Copy wrapper required for correct binding.
                    if bucket is not None:
                        parameter_indices = program.get("m_ParameterBlobIndices")
                        players = program.get("m_PlayerSubPrograms")
                        if (not isinstance(parameter_indices, list) or not isinstance(players, list)
                            or len(parameter_indices) != len(players)
                            or bucket >= len(parameter_indices)
                            or len(parameter_indices[bucket]) != len(players[bucket])):
                            counts["parameter_index_layout_unresolved"] += 1
                        else:
                            param_index = parameter_indices[bucket][vi]
                            if type(param_index) is not int or not 0 <= param_index < len(entries):
                                counts["parameter_index_layout_unresolved"] += 1
            variant_pairs += len(mapping[0] & mapping[1])
            counts["paired_passes"] += bool(mapping[0] & mapping[1])
            counts["unpaired_passes"] += not bool(mapping[0] & mapping[1])
            counts["single_variant_paired_passes"] += (
                len(mapping[0]) == 1 and len(mapping[1]) == 1 and bool(mapping[0] & mapping[1])
            )
    if counts["original_passes"] == 0:
        raise ValueError("Original Subsurface Blur pass graph is empty")
    return {
        "original_subshader_count": len(subshaders),
        "original_pass_count": counts["original_passes"],
        "pass_counts_per_subshader": per_subshader,
        "original_minimum_logged_passes_met": counts["original_passes"] >= MIN_PASSES,
        "linked_stage_programs": counts["linked_stage_programs"],
        "distinct_stage_programs": len(programs),
        "vertex_variants": counts["stage_1_variants"],
        "fragment_variants": counts["stage_0_variants"],
        "paired_original_passes": counts["paired_passes"],
        "unpaired_original_passes": counts["unpaired_passes"],
        "exact_permutation_stage_pairs": variant_pairs,
        "single_variant_paired_passes": counts["single_variant_paired_passes"],
        "stages_with_keyword_permutations": counts["stages_with_keyword_permutations"],
        "parameter_index_layout_unresolved": counts["parameter_index_layout_unresolved"],
        "non_normal_passes": counts["original_passes"] - counts["pass_type_0"],
        "shaderlab_wrapper_constructed": False,
        "original_shader_meta_or_guid_changed": False,
        "shaderlab_installed": False,
        "unity_or_gpu_or_android_executed": False,
        "original_material_binding_verified": False,
        "water_or_fft_build_ready": False,
    }


def original_shader(root):
    """Select one genuine original object from only the verified W1 owners."""
    verify_sources(root, expected=OWNERS)
    import UnityPy
    matches = []
    for owner in sorted(OWNERS):
        env = UnityPy.load(str(root / owner))
        for obj in env.file.objects.values():
            if obj.type.name != "Shader":
                continue
            tree = obj.read_typetree()
            parsed = tree.get("m_ParsedForm")
            if isinstance(parsed, dict) and parsed.get("m_Name") == TARGET:
                matches.append((owner, obj, tree))
        if not matches:
            del env
            gc.collect()
    if len(matches) != 1:
        raise ValueError("Original Subsurface Blur target missing or ambiguous in two SHA-pinned resource owners")
    owner, obj, tree = matches[0]
    return owner, hashlib.sha256(obj.get_raw_data()).hexdigest(), tree


def probe(root, out):
    owner, object_sha, tree = original_shader(root)
    tables = [(platform, records(segments)) for platform, segments in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError("Original water Blur D3D11 table missing or ambiguous")
    parsed = tree["m_ParsedForm"]
    result = inspect_shader(parsed, tables[0][1])
    result.update({
        "authenticated_original_owner_count": len(OWNERS),
        "authenticated_input_size_bytes": 227511628,
        "original_object_sha256": object_sha,
        "parsed_form_sha256": hashlib.sha256(json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest(),
        "genuine_original_object_selected": True,
        "full_140_shader_asset_ripper_export_mapped": False,
        "original_source_kept_private": True,
        "shader_program_source_published": False,
        "numeric_render_equivalence": False,
    })
    public = json.dumps(result, sort_keys=True)
    out.write_text(public + "\n", encoding="utf-8")
    print("RAFT_A12_WATER_BLUR_PASS_GRAPH " + public)
    if not result["original_minimum_logged_passes_met"]:
        raise ValueError("Original Blur logged pass minimum not met; do not fabricate passes")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    probe(a.source, a.out)
