"""T2: private source-authentic Foam SPIR-V DescriptorSet-only remap proof.

This experiment operates only on temporary compiled SPIR-V. It does not
modify proprietary source, code instructions, Binding decorations, variable
IDs, ShaderLab, Unity runtime, Material calls, .meta/GUID or Android APK.
No original symbols, private descriptor coordinates, bytecode or pixels logged.
"""
import argparse
import json
from pathlib import Path
import struct
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_candidate_embedded_validation import (
    extract_embedded_programs, _invoke, LIMIT_BYTES
)
from scripts.t2_foam_embedded_descriptor_layout import (
    CATEGORIES, reflected_descriptor_map, compare_cross_stage_descriptors
)
from scripts.t2_foam_embedded_stage_io import reflect_stage
from scripts.t2_foam_original_pair_compile import MAX_SPV

SPIRV_MAGIC = 0x07230203
OP_DECORATE = 71
DECOR_BINDING = 33
DECOR_DESCRIPTOR_SET = 34
MAX_SPIRV_WORDS = MAX_SPV // 4


def scan_binary_decorations(blob):
    """Parse exact SPIR-V word boundaries, fail closed for binding decorations."""
    if (not isinstance(blob, bytes) or not 20 <= len(blob) <= MAX_SPV
            or len(blob) % 4):
        raise ValueError("unbounded_or_misaligned_private_SPIRV")
    words = list(struct.unpack("<%dI" % (len(blob)//4), blob))
    if (words[0] != SPIRV_MAGIC or not 0 < words[3] < MAX_SPIRV_WORDS
            or words[4] != 0 or not 0x00010000 <= words[1] <= 0x00010600):
        raise ValueError("private_SPIRV_header_invalid")
    bindings = {}
    sets = {}
    set_sites = {}
    i = 5
    while i < len(words):
        opcode = words[i] & 0xFFFF
        n = words[i] >> 16
        if not n or i+n > len(words):
            raise ValueError("malformed_private_SPIRV_opcode_boundaries")
        if opcode == OP_DECORATE and n >= 3 and words[i+2] in (
                DECOR_BINDING, DECOR_DESCRIPTOR_SET):
            if n != 4 or not 0 < words[i+1] < words[3]:
                raise ValueError("malformed_private_descriptor_decoration")
            target, mode, value = words[i+1], words[i+2], words[i+3]
            if value > 65535:
                raise ValueError("unbounded_SPIRV_decorated_register")
            if mode == DECOR_BINDING:
                if target in bindings:
                    raise ValueError("duplicated_SPIRV_Binding_decoration")
                bindings[target] = value
            else:
                if target in sets:
                    raise ValueError("duplicated_SPIRV_DescriptorSet_decoration")
                sets[target] = value
                set_sites[target] = i+3
        i += n
    if i != len(words) or set(bindings) != set(sets):
        raise ValueError("incomplete_descriptor_decoration_pair")
    return words, bindings, sets, set_sites


def reflected_ids(reflection, *, mode):
    """Verify stage identity and no ambiguity between reflection and SPIR-V."""
    private = reflected_descriptor_map(reflection, mode=mode)
    ids = {}
    for category in CATEGORIES:
        for descriptor in reflection.get(category, []):
            target = descriptor.get("id")
            if (type(target) is not int or target <= 0
                    or target in ids):
                raise ValueError("no_unique_reflected_SPIRV_descriptor_id")
            ids[target] = (descriptor["set"], descriptor["binding"])
    if len(ids) != len(private):
        raise ValueError("reflected_SPIRV_descriptor_cardinality_mismatch")
    if set(ids.values()) != set(private):
        raise ValueError("SPIRV_resource_id_register_map_invalid")
    return ids


def relocate_fragment_sets(blob, reflection, new_set):
    """Modify only the DescriptorSet OpDecorate literal of each fragment ID.

    All original opcode words, resource variable/Binding IDs, and source code
    are bitwise identical. Original source registers are never inferred by
    alphabetical name or reordered B20 stage packet entry.
    """
    if type(new_set) is not int or not 1 <= new_set <= 15:
        raise ValueError("invalid_unique_stage_descriptor_set")
    ids = reflected_ids(reflection, mode="frag")
    words, bindings, sets, positions = scan_binary_decorations(blob)
    if set(ids) != set(bindings):
        raise ValueError("private_binary_descriptor_reflection_id_drift")
    if not ids:
        raise ValueError("original_Foam_fragment_descriptor_set_missing")
    if any(sets[i] != ids[i][0] or bindings[i] != ids[i][1]
           for i in ids):
        raise ValueError("private_OpDecorate_does_not_match_reflection")
    if any(sets[i] != 0 for i in ids):
        raise ValueError("source_fragment_descriptor_set_not_single_zero")
    if len(set(ids.values())) != len(ids):
        raise ValueError("ambiguous_reflected_binding_alias")
    modified = words[:]
    changed = []
    for identifier in ids:
        site = positions[identifier]
        if modified[site] == new_set:
            raise ValueError("already_moved_original_fragment_descriptor")
        modified[site] = new_set
        changed.append(site)
    if len(changed) != len(ids) or any(
            words[i] != modified[i] for i in range(len(words)) if i not in changed):
        raise ValueError("private_SPIRV_non_Decorate_words_changed")
    patched = struct.pack("<%dI" % len(modified), *modified)
    if patched == blob or len(patched) != len(blob):
        raise ValueError("source_program_not_modified_only_as_expected")
    _, before_bindings, before_sets, _ = scan_binary_decorations(blob)
    _, after_bindings, after_sets, _ = scan_binary_decorations(patched)
    if (before_bindings != after_bindings
            or set(after_sets) != set(before_sets)
            or any(after_sets[i] != new_set for i in before_sets)):
        raise ValueError("original_SPIRV_register_or_instruction_drift")
    return patched, {
        "descriptor_set_decorations_only_changed": True,
        "original_Binding_and_non_descriptor_words_unchanged": True,
        "fragment_descriptor_count_relocated": len(ids),
    }


def compare_before_after_reflection(before, after, target_set):
    """Confirm private descriptor identity and typed class were not changed."""
    original = reflected_descriptor_map(before, mode="frag")
    revised = reflected_descriptor_map(after, mode="frag")
    if (not original or any(s != 0 for s, _ in original)
            or target_set not in {s for s, _ in revised}
            or len(original) != len(revised)):
        raise ValueError("SPIRV_reflection_after_relocation_incomplete")
    for (_, binding), signature in original.items():
        if revised.get((target_set, binding)) != signature:
            raise ValueError("source_stage_resource_class_or_binding_drift")
    if set(s for s, _ in revised) != {target_set}:
        raise ValueError("post_relocation_extra_set_or_missing_binding")
    old_ids = reflected_ids(before, mode="frag")
    new_ids = reflected_ids(after, mode="frag")
    if (set(old_ids) != set(new_ids)
            or any(new_ids[i] != (target_set, old_ids[i][1]) for i in old_ids)):
        raise ValueError("post_relocation_original_resource_id_drift")
    return True


def source_preserving_stage_set(vertex):
    """Select a fresh fragment-only set, never guessing current shader usage."""
    used = {key[0] for key in reflected_descriptor_map(vertex, mode="vert")}
    for target in range(1, 16):
        if target not in used:
            return target
    raise ValueError("no_unused_private_fragment_descriptor_set")


def test_original_candidate(candidate, scratch, *, invoke=_invoke,
                            reflect=reflect_stage):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or not 0 < candidate.stat().st_size <= LIMIT_BYTES
            or not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("private_original_candidate_or_scratch_invalid")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    summary = []
    with tempfile.TemporaryDirectory(prefix="t2-foam-private-set-remap-", dir=scratch) as temp:
        temp = Path(temp)
        for pass_id, body in enumerate(bodies):
            hlsl = temp / ("pass%d-actual-embedded.hlsl" % pass_id)
            hlsl.write_text(body, encoding="utf-8")
            modules, reports = {}, {}
            for stage_id, macro, kind in ((1, "VERTEX", "vert"),
                                          (0, "FRAGMENT", "frag")):
                raw = temp / ("pass%d-stage%d-original.spv" % (pass_id, stage_id))
                cmd = ["glslangValidator", "-V", "-D",
                       "-DSHADER_STAGE_" + macro + "=1",
                       "-S", kind, "-e", "main",
                       "-o", str(raw), str(hlsl)]
                if not invoke(cmd):
                    return {"status": "blocked_original_pass_compilation",
                            "failed_pass": pass_id, "failed_stage": stage_id,
                            "private_source_published": False}
                if (not raw.is_file() or not _physical(raw)
                        or not 20 <= raw.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(raw)])):
                    return {"status": "blocked_original_pass_spirv_val",
                            "failed_pass": pass_id, "failed_stage": stage_id,
                            "private_source_published": False}
                modules[stage_id], reports[stage_id] = raw, reflect(raw)
            pre = compare_cross_stage_descriptors(reports[1], reports[0])
            if not pre["shared_descriptor_class_conflict_count"]:
                raise ValueError("original_stage_descriptor_conflict_pin_missing")
            new_set = source_preserving_stage_set(reports[1])
            old_binary = modules[0].read_bytes()
            patched_binary, guard = relocate_fragment_sets(
                old_binary, reports[0], new_set)
            patched = temp / ("pass%d-stage0-remapped-private.spv" % pass_id)
            patched.write_bytes(patched_binary)
            if (not _physical(patched) or not invoke(
                    ["spirv-val", "--target-env", "vulkan1.1", str(patched)])):
                return {"status": "blocked_private_relocated_spirv_val",
                        "failed_pass": pass_id, "private_source_published": False}
            after = reflect(patched)
            if not compare_before_after_reflection(reports[0], after, new_set):
                raise ValueError("reflection_mismatch_after_descriptor_relocation")
            post = compare_cross_stage_descriptors(reports[1], after)
            if (post["shared_numeric_set_binding_count"] != 0
                    or post["shared_descriptor_class_conflict_count"] != 0
                    or not post["same_type_pipeline_descriptor_set_layout_possible"]):
                raise ValueError("remapped_shader_still_has_cross_stage_collision")
            summary.append({
                "original_cross_stage_descriptor_class_conflicts":
                    pre["shared_descriptor_class_conflict_count"],
                "original_shared_UBO_extent_differences":
                    pre["shared_CB_buffer_extent_difference_count"],
                "fragment_descriptors_relocated":
                    guard["fragment_descriptor_count_relocated"],
                "post_relocation_descriptor_class_conflicts":
                    post["shared_descriptor_class_conflict_count"],
                "post_relocation_shared_bindings":
                    post["shared_numeric_set_binding_count"],
                "SPIRV_non_descriptor_words_and_original_Binding_unchanged":
                    guard["original_Binding_and_non_descriptor_words_unchanged"],
            })
    return {
        "status": "source_original_foam_private_decorations_only_remap_valid",
        "source_original_passes": 2,
        "original_compiled_and_validated_stage_variants": 4,
        "privately_relocated_fragment_variants_validated": len(summary),
        "original_compiled_descriptor_type_conflicts": sum(
            r["original_cross_stage_descriptor_class_conflicts"] for r in summary),
        "private_descriptor_type_conflicts_after_relocation": sum(
            r["post_relocation_descriptor_class_conflicts"] for r in summary),
        "total_fragment_descriptor_decorations_relocated": sum(
            r["fragment_descriptors_relocated"] for r in summary),
        "all_original_non_descriptor_SPIRV_words_unchanged": all(
            r["SPIRV_non_descriptor_words_and_original_Binding_unchanged"]
            for r in summary),
        "per_pass_aggregate_only": summary,
        "real_Unity_ShaderLab_import_or_descriptor_upload_verified": False,
        "original_CB0_and_material_texture_sampler_delivery_verified": False,
        "original_Adreno_water_pixels_verified": False,
        "private_binary_or_original_shader_source_published": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = a.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out)
                or out.exists() or out.is_relative_to(a.candidate.absolute())):
            raise ValueError("unsafe_numeric_output")
        result = test_original_candidate(a.candidate, a.scratch)
        code = 0 if result["status"] == (
            "source_original_foam_private_decorations_only_remap_valid") else 2
    except BaseException as exc:
        result = {"status": "blocked_private_fragment_descriptor_set_relocation",
                  "failure_type": type(exc).__name__,
                  "private_binary_or_original_shader_source_published": False}
        code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(result, sort_keys=True)+"\n", encoding="utf-8")
    print("T2_FOAM_DESCRIPTOR_REMAP_SAFE "+json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
