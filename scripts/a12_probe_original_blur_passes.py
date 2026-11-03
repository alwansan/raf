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
from scripts.probe_w2_fullgame_texture_colors import verify_and_hash
from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key

TARGET = "UltimateWater/Utilities/Blur (Subsurface Scattering)"
MIN_PASSES = 2
MAX_PASSES = 128
MAX_VARIANTS_PER_STAGE = 96
MAX_TOTAL_VARIANTS = 2048

# Full-game W3 original inventory (blob ebe5247d...) records 165 actual
# Shader objects across exactly these 14 source owners. Every owner is checked
# against its original SHA/size AND committed Git identity before any reads.
# This is not a claim that every original AssetRipper export can be re-generated.
SHADER_OWNERS = {
    "globalgamemanagers.assets": (758412, "b549af329d48244d80f28cb3cce6cd0b17769176081c249dc4646e1d62c58e28"),
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
    "sharedassets1.assets": (34888388, "c6bdf49f7d38ab060872fcb298770bc7113959f85ea2fd1a42dc663323d7660a"),
    "sharedassets24.assets": (7987136, "a28921562b0d64a0c5aeddfabd7a50c2695d9e9422725c19df9c786f8fdd6bdc"),
    "sharedassets25.assets": (17611892, "b29ec028607fe74f9b0ac6fe55d0e565e26b29ac520bd80732c5a3bc851f7f67"),
    "sharedassets29.assets": (9198256, "1d1e3e9047e5d67df2dade7f85e32ff2873f1d07dc75611ade3e7d4be2bd8e8e"),
    "sharedassets30.assets": (19568972, "0cacdad92d1f1c94e9b8f4c971619851908a0305a0d32f66e6d67b8068320b26"),
    "sharedassets34.assets": (13612772, "c422af7ca6e4153ef9abe8e6522123ee089b82b90d85b29223db011987dcdb9e"),
    "sharedassets35.assets": (26845236, "6e52bc4588605289c00b95dd3d4b2ad15a427c40c7f857ea52fb36a5d73a00e5"),
    "sharedassets36.assets": (110149324, "b32fcd9d327c8926b2309ffc1b5645a0c23d64ed95be37ed94e96f34736530c8"),
    "sharedassets6.assets": (6607272, "0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632"),
    "sharedassets8.assets": (9257796, "55477662f824670d0e38e8b9811e55850c7d25bb4e6aff837d08d933aa3e1823"),
    "sharedassets9.assets": (4442272, "a7ce9c85095d19712100c61329f198a54ff0c8a077426c2acc4f2b96af13c54c"),
}
ORIGINAL_SHADER_OBJECTS = 165


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


def original_shader(root, repo):
    """Exact-name target across 14 SHA-pinned original Shader-bearing owners.

    W3 separately verified that the other 68 serialized owners have zero
    Shader objects. The 14-owner subset is checked again independently here.
    No original identities or owner path IDs enter the published report.
    """
    if len(SHADER_OWNERS) != 14 or sum(v[0] for v in SHADER_OWNERS.values()) != 488439356:
        raise ValueError("Original shader owner manifest changed")
    verify_sources(root, expected=OWNERS)
    for owner, (expected_size, expected_sha) in SHADER_OWNERS.items():
        path = root / owner
        if path.is_symlink() or not path.is_file() or path.stat().st_size != expected_size:
            raise ValueError("Original Shader-bearing owner missing or changed")
        verified = verify_and_hash(path, repo, "Raft/Raft_Data/" + owner)
        if verified["sha256"] != expected_sha:
            raise ValueError("Original shader owner SHA mismatch")
    import UnityPy
    matches = []
    original_count = 0
    for owner in sorted(SHADER_OWNERS):
        env = UnityPy.load(str(root / owner))
        for obj in env.file.objects.values():
            if obj.type.name != "Shader":
                continue
            original_count += 1
            tree = obj.read_typetree()
            parsed = tree.get("m_ParsedForm")
            if isinstance(parsed, dict) and parsed.get("m_Name") == TARGET:
                matches.append((owner, hashlib.sha256(obj.get_raw_data()).hexdigest(), tree))
        del env
        gc.collect()
    if original_count != ORIGINAL_SHADER_OBJECTS:
        raise ValueError("Complete Shader-bearing original source inventory drift")
    if len(matches) != 1:
        raise ValueError("Original Subsurface Blur target missing or ambiguous in 14 SHA-pinned source owners")
    return matches[0]



def probe(root, out, repo):
    owner, object_sha, tree = original_shader(root, repo)
    tables = [(platform, records(segments)) for platform, segments in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError("Original water Blur D3D11 table missing or ambiguous")
    parsed = tree["m_ParsedForm"]
    result = inspect_shader(parsed, tables[0][1])
    result.update({
        "authenticated_shader_bearing_owner_count": len(SHADER_OWNERS),
        "authenticated_input_size_bytes": 488439356,
        "all_original_shader_objects_count": ORIGINAL_SHADER_OBJECTS,
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
    p.add_argument("--repo", type=Path, required=True)
    a = p.parse_args()
    probe(a.source, a.out, a.repo)
