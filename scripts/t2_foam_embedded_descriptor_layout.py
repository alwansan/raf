"""T2 original Foam PRIVATE cross-stage Vulkan descriptor-set layout diagnosis.

Reads the actual four SPIR-V stage variants recompiled from the final private
two-pass ShaderLab. Classifies (set,binding) collisions across VS and PS.
Never prints/copies source shader, private descriptor keys, variable names,
original source parameters or SPIR-V. This is NOT Unity runtime binding proof.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_candidate_embedded_validation import (
    extract_embedded_programs, _invoke, LIMIT_BYTES
)
from scripts.t2_foam_embedded_stage_io import reflect_stage
from scripts.t2_foam_original_pair_compile import MAX_SPV

# SPIRV-Cross --reflect descriptor categories. Each is one Vulkan descriptor
# type; different categories must not share a binding in a single pipeline
# descriptor-set layout.
CATEGORIES = {
    "ubos": "uniform_buffer",
    "ssbos": "storage_buffer",
    "separate_images": "sampled_image",
    "separate_samplers": "sampler",
    "sampled_images": "combined_image_sampler",
    "textures": "combined_image_sampler",
    "images": "storage_image",
    "storage_images": "storage_image",
    "subpass_inputs": "input_attachment",
    "acceleration_structures": "acceleration_structure",
}
UNSUPPORTED = ("atomic_counters", "plain_uniforms", "uniforms", "push_constants")
MAX_ROWS = 64
MAX_SET = 31
MAX_BINDING = 1023


def _array_signature(row):
    dims = row.get("array", [])
    if (not isinstance(dims, list) or len(dims) > 3
            or any(type(x) is not int or not 1 <= x <= 65536 for x in dims)):
        raise ValueError("ambiguous_original_descriptor_array")
    return tuple(dims)


def reflected_descriptor_map(reflection, *, mode):
    """Private numeric set/binding->(descriptor class, array, UBO byte size)."""
    if not isinstance(reflection, dict) or mode not in ("vert", "frag"):
        raise ValueError("malformed_descriptor_reflection")
    entry = reflection.get("entryPoints")
    if (not isinstance(entry, list) or len(entry) != 1
            or not isinstance(entry[0], dict) or entry[0].get("mode") != mode):
        raise ValueError("original_compiled_stage_entry_unrecognized")
    for key in UNSUPPORTED:
        if reflection.get(key):
            raise ValueError("unsupported_original_descriptor_category")
    result = {}
    seen_ids = set()
    total = 0
    for key, klass in CATEGORIES.items():
        rows = reflection.get(key, [])
        if not isinstance(rows, list) or len(rows) > MAX_ROWS:
            raise ValueError("unbounded_compiled_descriptor_category")
        total += len(rows)
        if total > MAX_ROWS:
            raise ValueError("unbounded_compiled_stage_descriptor_count")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("malformed_compiled_descriptor")
            set_id, binding = row.get("set"), row.get("binding")
            if (type(set_id) is not int or type(binding) is not int
                    or not 0 <= set_id <= MAX_SET or not 0 <= binding <= MAX_BINDING):
                raise ValueError("missing_or_invalid_numeric_descriptor_binding")
            key_pair = (set_id, binding)
            if key_pair in result:
                raise ValueError("conflicting_same_stage_descriptor_binding")
            # An explicit duplicate variable ID is suspicious even when the
            # register binding differs. Never infer aliasing by source names.
            identifier = row.get("id")
            if identifier is not None:
                if type(identifier) is not int or identifier < 1 or identifier in seen_ids:
                    raise ValueError("duplicate_or_invalid_SPIRV_descriptor_id")
                seen_ids.add(identifier)
            dims = _array_signature(row)
            byte_extent = None
            if klass in ("uniform_buffer", "storage_buffer"):
                byte_extent = row.get("block_size")
                if (type(byte_extent) is not int or not 1 <= byte_extent <= 16*1024*1024):
                    raise ValueError("missing_or_invalid_compiled_buffer_extent")
            result[key_pair] = (klass, dims, byte_extent)
    return result


def compare_cross_stage_descriptors(vertex, fragment):
    """Return category-count-only comparisons; no private slot coordinates."""
    vs = reflected_descriptor_map(vertex, mode="vert")
    fs = reflected_descriptor_map(fragment, mode="frag")
    common = set(vs) & set(fs)
    classes = {}
    different_arrays = 0
    different_extents = 0
    exact_shared = 0
    shared_same_descriptor_type = 0
    for key in common:
        vk, va, vz = vs[key]
        fk, fa, fz = fs[key]
        if vk != fk:
            # Only fixed public descriptor class labels, never original names.
            group = "_versus_".join(sorted((vk, fk)))
            classes[group] = classes.get(group, 0) + 1
        else:
            shared_same_descriptor_type += 1
            if va != fa:
                different_arrays += 1
            if vz is not None and fz is not None and vz != fz:
                different_extents += 1
            if va == fa and vz == fz:
                exact_shared += 1
    return {
        "vertex_descriptor_count": len(vs),
        "fragment_descriptor_count": len(fs),
        "shared_numeric_set_binding_count": len(common),
        "shared_same_descriptor_type_count": shared_same_descriptor_type,
        "shared_exact_descriptor_and_buffer_range_count": exact_shared,
        "shared_descriptor_class_conflict_count": sum(classes.values()),
        "conflict_descriptor_class_pairs": dict(sorted(classes.items())),
        "shared_descriptor_array_shape_mismatch_count": different_arrays,
        "shared_CB_buffer_extent_difference_count": different_extents,
        "vertex_exclusive_descriptor_count": len(vs)-len(common),
        "fragment_exclusive_descriptor_count": len(fs)-len(common),
        "same_type_pipeline_descriptor_set_layout_possible":
            sum(classes.values()) == 0 and different_arrays == 0,
    }


def probe(candidate, scratch, *, invoke=_invoke, reflect=reflect_stage):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or not 0 < candidate.stat().st_size <= LIMIT_BYTES
            or not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("private_candidate_or_scratch_unsafe")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    stage_reports = {}
    with tempfile.TemporaryDirectory(prefix="t2-foam-descriptor-layout-", dir=scratch) as temp:
        temp = Path(temp)
        for pass_id, body in enumerate(bodies):
            hlsl = temp / ("private-pass%d.hlsl" % pass_id)
            hlsl.write_text(body, encoding="utf-8")
            for stage_id, macro, kind in ((1, "VERTEX", "vert"), (0, "FRAGMENT", "frag")):
                binary = temp / ("private-pass%d-stage%d.spv" % (pass_id, stage_id))
                cmd = ["glslangValidator", "-V", "-D",
                       "-DSHADER_STAGE_" + macro + "=1", "-S", kind,
                       "-e", "main", "-o", str(binary), str(hlsl)]
                if not invoke(cmd):
                    return {"status": "blocked_real_original_stage_compilation",
                            "failed_pass": pass_id, "failed_stage": stage_id,
                            "private_source_published": False}
                if (not binary.is_file() or not _physical(binary)
                        or not 20 <= binary.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(binary)])):
                    return {"status": "blocked_real_original_spirv_validation",
                            "failed_pass": pass_id, "failed_stage": stage_id,
                            "private_source_published": False}
                stage_reports[(pass_id, stage_id)] = reflect(binary)
        rows = [compare_cross_stage_descriptors(
            stage_reports[(pass_id, 1)], stage_reports[(pass_id, 0)])
            for pass_id in range(2)]
    collisions = sum(r["shared_descriptor_class_conflict_count"] for r in rows)
    shape_mismatch = sum(r["shared_descriptor_array_shape_mismatch_count"] for r in rows)
    compatible = collisions == 0 and shape_mismatch == 0
    return {
        "status": ("original_private_foam_vulkan_stage_descriptor_types_compatible"
                   if compatible else
                   "original_private_foam_vulkan_stage_descriptor_layout_conflict"),
        "authentic_private_ShaderLab_pass_count": 2,
        "embedded_stages_recompiled_and_spirv_val": len(stage_reports),
        "per_pass_descriptor_set_layout": rows,
        "total_descriptor_type_conflicts": collisions,
        "total_descriptor_array_shape_conflicts": shape_mismatch,
        "single_unmodified_descriptor_layout_possible_for_both_passes":
            compatible,
        "original_Unity_shaderlab_import_or_descriptor_remapping_verified": False,
        "original_cb0_material_texture_sampler_upload_verified": False,
        "original_GPU_or_Adreno_frame_verified": False,
        "private_source_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("candidate", "scratch", "out"):
        p.add_argument("--"+name, required=True, type=Path)
    args = p.parse_args()
    out = args.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out)
                or out.exists()
                or out.is_relative_to(args.candidate.absolute())):
            raise ValueError("unsafe_report_destination")
        result = probe(args.candidate, args.scratch)
        # A measured descriptor-class conflict is a valid *negative* result,
        # not the absence of a completed source-original experiment.
        code = 0 if result["status"] in (
            "original_private_foam_vulkan_stage_descriptor_types_compatible",
            "original_private_foam_vulkan_stage_descriptor_layout_conflict",
        ) else 2
    except BaseException as exc:
        result = {
            "status": "blocked_private_descriptor_layout_reflection",
            "failure_type": type(exc).__name__,
            "private_source_published": False,
        }
        code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(result, sort_keys=True)+"\n", encoding="utf-8")
    print("T2_FOAM_CROSS_STAGE_DESCRIPTOR_SAFE "+json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
