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

# Never expose arbitrary exception text from source parsers/compiler. Only our
# exact static classifications may appear in the public-safe status report.
SAFE_FAILURE_CODES = frozenset((
    "unbounded_or_misaligned_private_SPIRV",
    "private_SPIRV_header_invalid",
    "malformed_private_SPIRV_opcode_boundaries",
    "malformed_private_descriptor_decoration",
    "unbounded_SPIRV_decorated_register",
    "duplicated_SPIRV_Binding_decoration",
    "duplicated_SPIRV_DescriptorSet_decoration",
    "incomplete_descriptor_decoration_pair",
    "no_unique_reflected_SPIRV_descriptor_id",
    "reflected_SPIRV_descriptor_cardinality_mismatch",
    "SPIRV_resource_id_register_map_invalid",
    "ambiguous_SPIRV_decorated_descriptor_coordinates",
    "SPIRV_numeric_reflection_decoration_mismatch",
    "optional_resource_id_conflicts_with_decorations",
    "invalid_unique_stage_descriptor_set",
    "private_binary_descriptor_reflection_id_drift",
    "original_Foam_fragment_descriptor_set_missing",
    "private_OpDecorate_does_not_match_reflection",
    "source_fragment_descriptor_set_not_single_zero",
    "ambiguous_reflected_binding_alias",
    "already_moved_original_fragment_descriptor",
    "private_SPIRV_non_Decorate_words_changed",
    "source_program_not_modified_only_as_expected",
    "original_SPIRV_register_or_instruction_drift",
    "SPIRV_reflection_after_relocation_incomplete",
    "source_stage_resource_class_or_binding_drift",
    "post_relocation_extra_set_or_missing_binding",
    "post_relocation_original_resource_id_drift",
    "no_unused_private_fragment_descriptor_set",
    "original_stage_descriptor_conflict_pin_missing",
    "remapped_shader_still_has_cross_stage_collision",
    "reflection_mismatch_after_descriptor_relocation",
    "private_original_candidate_or_scratch_invalid",
    "unsafe_numeric_output",
    "no_conflicting_original_resource_type",
    "selective_target_descriptor_set_not_free",
    "selective_spirv_reflection_conflict_join_invalid",
    "selective_spirv_other_words_changed",
    "selective_original_resource_ids_or_bindings_changed",
    "selective_reflection_descriptor_count_changed",
    "selective_reflection_signature_or_CB0_changed",
    "selective_reflection_resource_id_changed",
    "selective_spirv_val_failed",
    "selective_unmodified_CB0_interface_not_retained",
))


def safe_failure_code(exc):
    message = str(exc)
    if isinstance(exc, ValueError) and message in SAFE_FAILURE_CODES:
        return message
    return "unclassified_private_error"


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


def reflected_ids(reflection, bindings, sets, *, mode):
    """Authenticate SPIR-V variable IDs by unique numeric decorations.

    Reflection's id field is optional. A one-to-one numeric set/binding map
    with the SPIR-V OpDecorate variables is sufficient; supplied IDs must
    match, but neither symbol names nor declaration order are authoritative.
    """
    private = reflected_descriptor_map(reflection, mode=mode)
    if set(bindings) != set(sets):
        raise ValueError("incomplete_descriptor_decoration_pair")
    by_coord = {}
    for identifier in bindings:
        coord = (sets[identifier], bindings[identifier])
        if coord in by_coord:
            raise ValueError("ambiguous_SPIRV_decorated_descriptor_coordinates")
        by_coord[coord] = identifier
    if len(by_coord) != len(private) or set(by_coord) != set(private):
        raise ValueError("SPIRV_numeric_reflection_decoration_mismatch")
    for category in CATEGORIES:
        for descriptor in reflection.get(category, []):
            identity = descriptor.get("id")
            if identity is not None:
                coord = (descriptor["set"], descriptor["binding"])
                if type(identity) is not int or identity != by_coord[coord]:
                    raise ValueError("optional_resource_id_conflicts_with_decorations")
    return {identifier: coord for coord, identifier in by_coord.items()}

def relocate_fragment_sets(blob, reflection, new_set):
    """Modify only the DescriptorSet OpDecorate literal of each fragment ID.

    All original opcode words, resource variable/Binding IDs, and source code
    are bitwise identical. Original source registers are never inferred by
    alphabetical name or reordered B20 stage packet entry.
    """
    if type(new_set) is not int or not 1 <= new_set <= 15:
        raise ValueError("invalid_unique_stage_descriptor_set")
    words, bindings, sets, positions = scan_binary_decorations(blob)
    ids = reflected_ids(reflection, bindings, sets, mode="frag")
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
    # Reflection IDs may be absent; instruction-word identity already
    # guarantees binary variable IDs never changed. Validate optional IDs.
    for category in CATEGORIES:
        old_ids = {r["binding"]: r.get("id") for r in before.get(category, [])}
        new_ids = {r["binding"]: r.get("id") for r in after.get(category, [])}
        if old_ids != new_ids:
            raise ValueError("post_relocation_original_resource_id_drift")
    return True


def source_preserving_stage_set(vertex):
    """Select a fresh fragment-only set, never guessing current shader usage."""
    used = {key[0] for key in reflected_descriptor_map(vertex, mode="vert")}
    for target in range(1, 16):
        if target not in used:
            return target
    raise ValueError("no_unused_private_fragment_descriptor_set")


def relocate_conflicting_only(blob, vertex, fragment, target_set):
    """Move only type/array-conflicting Fragment descriptors; retain shared CB0."""
    vs=reflected_descriptor_map(vertex,mode="vert")
    fs=reflected_descriptor_map(fragment,mode="frag")
    conflict={coord for coord in set(vs)&set(fs) if vs[coord][:2]!=fs[coord][:2]}
    if not conflict:
        raise ValueError("no_conflicting_original_resource_type")
    occupied={coord[0] for coord in vs}|{coord[0] for coord in fs}
    if type(target_set) is not int or target_set not in range(1,16) or target_set in occupied:
        raise ValueError("selective_target_descriptor_set_not_free")
    words, bindings, sets, sites=scan_binary_decorations(blob)
    id_to_coord=reflected_ids(fragment,bindings,sets,mode="frag")
    moved={ident for ident,coord in id_to_coord.items() if coord in conflict}
    if len(moved)!=len(conflict):
        raise ValueError("selective_spirv_reflection_conflict_join_invalid")
    revised=words[:]
    for ident in moved:
        revised[sites[ident]]=target_set
    diff={i for i,(a,b) in enumerate(zip(words,revised)) if a!=b}
    if diff!={sites[i] for i in moved} or len(diff)!=len(conflict):
        raise ValueError("selective_spirv_other_words_changed")
    output=struct.pack("<%dI"%len(revised),*revised)
    _,check_bindings,check_sets,_=scan_binary_decorations(output)
    if check_bindings!=bindings or any(
        check_sets[i]!=(target_set if i in moved else sets[i]) for i in bindings
    ):
        raise ValueError("selective_original_resource_ids_or_bindings_changed")
    return output,conflict


def verify_selective_reflection(before, after, conflicts, target_set):
    original=reflected_descriptor_map(before,mode="frag")
    revised=reflected_descriptor_map(after,mode="frag")
    if len(original)!=len(revised):
        raise ValueError("selective_reflection_descriptor_count_changed")
    expected={(target_set,k[1]) if k in conflicts else k:v for k,v in original.items()}
    if revised!=expected or len(expected)!=len(original):
        raise ValueError("selective_reflection_signature_or_CB0_changed")
    # Reflection's optional ID is verified where reported. Actual SPIR-V ID
    # identity is guaranteed by exact non-DescriptorSet word equality.
    for category in CATEGORIES:
        old_rows=before.get(category,[])
        new_rows=after.get(category,[])
        if (len(old_rows)!=len(new_rows) or
            {x["binding"]:x.get("id") for x in old_rows}!=
            {x["binding"]:x.get("id") for x in new_rows}):
            raise ValueError("selective_reflection_resource_id_changed")
    return True


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
            # Second, more conservative experiment: move only the colliding
            # fragment resources, leaving the original same-class CB0 shared
            # coordinate untouched. This does not prove CB0 upload semantics.
            old_vs=reflected_descriptor_map(reports[1],mode="vert")
            old_fs=reflected_descriptor_map(reports[0],mode="frag")
            occupied={x[0] for x in old_vs}|{x[0] for x in old_fs}
            selective_set=next((i for i in range(1,16) if i not in occupied),None)
            if selective_set is None:
                raise ValueError("selective_target_descriptor_set_not_free")
            minimal,conflicts=relocate_conflicting_only(
                old_binary,reports[1],reports[0],selective_set)
            only_patch=temp/("pass%d-stage0-conflict-only.spv"%pass_id)
            only_patch.write_bytes(minimal)
            if not _physical(only_patch) or not invoke(
                ["spirv-val","--target-env","vulkan1.1",str(only_patch)]
            ):
                raise ValueError("selective_spirv_val_failed")
            only_report=reflect(only_patch)
            verify_selective_reflection(reports[0],only_report,conflicts,selective_set)
            only_post=compare_cross_stage_descriptors(reports[1],only_report)
            if (only_post["shared_descriptor_class_conflict_count"]!=0 or
                only_post["shared_descriptor_array_shape_mismatch_count"]!=0 or
                only_post["shared_same_descriptor_type_count"]!=
                   pre["shared_same_descriptor_type_count"] or
                only_post["shared_numeric_set_binding_count"]!=
                   pre["shared_same_descriptor_type_count"] or
                only_post["shared_CB_buffer_extent_difference_count"]!=
                   pre["shared_CB_buffer_extent_difference_count"]):
                raise ValueError("selective_unmodified_CB0_interface_not_retained")
            summary.append({
                "original_conflicting_only_descriptors_relocated":len(conflicts),
                "selective_post_class_conflicts":
                    only_post["shared_descriptor_class_conflict_count"],
                "selective_shared_same_type_CB_links_retained":
                    only_post["shared_same_descriptor_type_count"],
                "selective_CB_extent_differences_still_unresolved":
                    only_post["shared_CB_buffer_extent_difference_count"],
                "selective_original_other_SPIRV_words_unchanged":True,
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
        "selective_fragment_conflicting_descriptors_only_relocated":sum(
            r["original_conflicting_only_descriptors_relocated"] for r in summary),
        "selective_remaining_resource_type_conflicts":sum(
            r["selective_post_class_conflicts"] for r in summary),
        "selective_original_same_type_CB_links_retained":sum(
            r["selective_shared_same_type_CB_links_retained"] for r in summary),
        "selective_CB_extent_differences_still_unresolved":sum(
            r["selective_CB_extent_differences_still_unresolved"] for r in summary),
        "selective_private_relocated_fragment_variants_validated":len(summary),
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
                  "safe_failure_code": safe_failure_code(exc),
                  "private_binary_or_original_shader_source_published": False}
        code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(result, sort_keys=True)+"\n", encoding="utf-8")
    print("T2_FOAM_DESCRIPTOR_REMAP_SAFE "+json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
