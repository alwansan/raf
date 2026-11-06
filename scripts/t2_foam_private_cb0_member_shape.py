"""Private Foam VS/FS UBO member-geometry audit for original two-pass candidate.

This is an observational, fail-closed SPIRV-Cross reflection diagnostic.
It does not infer original source member offsets, Unity CB0 writes, or pixels.
Never output private type names, resource keys, descriptor positions or code.
"""
import argparse
import json
from pathlib import Path
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_candidate_embedded_validation import (
    _invoke, extract_embedded_programs, LIMIT_BYTES
)
from scripts.t2_foam_embedded_stage_io import reflect_stage
from scripts.t2_foam_embedded_descriptor_layout import reflected_descriptor_map
from scripts.t2_foam_original_pair_compile import MAX_SPV

MAX_MEMBERS = 64
MAX_TYPES = 2048
MAX_BLOCK = 16 * 1024 * 1024


def _ubo_map(reflection, mode):
    # Validate all reflected descriptor classes, duplicates and coordinates.
    descriptor_map = reflected_descriptor_map(reflection, mode=mode)
    rows = reflection.get("ubos", [])
    if not isinstance(rows, list) or len(rows) > 16:
        raise ValueError("unbounded_private_ubo_rows")
    result = {}
    for row in rows:
        coord = (row.get("set"), row.get("binding"))
        if coord in result or descriptor_map.get(coord, (None,))[0] != "uniform_buffer":
            raise ValueError("ambiguous_private_ubo_coordinate")
        result[coord] = row
    return result


def _member_geometry(reflection, ubo):
    """Return PRIVATE offset-keyed member geometry; omit source names entirely."""
    types = reflection.get("types")
    type_id = ubo.get("type")
    if (not isinstance(types, dict) or not 1 <= len(types) <= MAX_TYPES
            or not isinstance(type_id, str) or not 1 <= len(type_id) <= 100
            or type_id not in types):
        raise ValueError("missing_private_ubo_struct_type")
    definition = types[type_id]
    members = definition.get("members") if isinstance(definition, dict) else None
    if not isinstance(members, list) or not 1 <= len(members) <= MAX_MEMBERS:
        raise ValueError("invalid_private_ubo_member_list")
    block = ubo.get("block_size")
    if type(block) is not int or not 0 < block <= MAX_BLOCK:
        raise ValueError("invalid_private_block_extent")
    result = {}
    for row in members:
        if not isinstance(row, dict):
            raise ValueError("malformed_private_member")
        off, kind = row.get("offset"), row.get("type")
        if (type(off) is not int or not 0 <= off < block
                or not isinstance(kind, str) or not 1 <= len(kind) <= 100):
            raise ValueError("invalid_private_member_offset_type")
        arr = row.get("array", [])
        literal = row.get("array_size_is_literal")
        if (not isinstance(arr, list) or len(arr) > 3
                or any(type(x) is not int or not 1 <= x <= 65536 for x in arr)
                or (literal is not None and
                    (not isinstance(literal, list)
                     or len(literal) != len(arr)
                     or any(x is not True for x in literal)))):
            raise ValueError("unbounded_or_dynamic_private_member_array")
        array_stride = row.get("array_stride")
        matrix_stride = row.get("matrix_stride")
        if any(v is not None and (type(v) is not int or not 1 <= v <= MAX_BLOCK)
               for v in (array_stride, matrix_stride)):
            raise ValueError("invalid_private_member_stride")
        row_major = row.get("row_major", False)
        if type(row_major) is not bool:
            raise ValueError("invalid_private_member_major")
        # Reflected names, type labels, and offsets are private; no serialization.
        if off in result:
            raise ValueError("overlapping_private_member_start")
        result[off] = (kind, tuple(arr), array_stride, matrix_stride, row_major)
    return result


def compare_private_cb0_geometry(vertex, fragment):
    """Source-free testable comparison of same numeric coordinate shared UBOs.

    Equal member strings/offsets are reflected structure evidence only, never
    original HLSL semantic identity, byte-wise upload, or a valid GPU pipeline.
    """
    vs = _ubo_map(vertex, "vert")
    fs = _ubo_map(fragment, "frag")
    common = set(vs) & set(fs)
    if len(common) != 1:
        raise ValueError("unexpected_private_shared_cb0_link_count")
    coord = next(iter(common))
    va = _member_geometry(vertex, vs[coord])
    fa = _member_geometry(fragment, fs[coord])
    shared = set(va) & set(fa)
    same_type = sum(va[offset][0] == fa[offset][0] for offset in shared)
    same_shape = sum(va[offset] == fa[offset] for offset in shared)
    altered_array = sum(
        va[offset][0] == fa[offset][0] and va[offset][1] != fa[offset][1]
        for offset in shared
    )
    altered_stride = sum(
        va[offset][0] == fa[offset][0]
        and (va[offset][2:] != fa[offset][2:])
        for offset in shared
    )
    return {
        "shared_uniform_buffer_coordinate_count": 1,
        "vertex_reflected_member_count": len(va),
        "fragment_reflected_member_count": len(fa),
        "same_offset_member_count": len(shared),
        "same_offset_same_type_token_count": same_type,
        "same_offset_exact_reflected_geometry_count": same_shape,
        "same_offset_array_shape_difference_count": altered_array,
        "same_offset_stride_or_major_difference_count": altered_stride,
        "different_reflected_block_byte_extent": vs[coord]["block_size"] != fs[coord]["block_size"],
        "reflected_member_shape_is_not_Unity_CB0_upload_evidence": True,
    }


def inspect_private_candidate(candidate, scratch, *, invoke=_invoke, reflect=reflect_stage):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or not 0 < candidate.stat().st_size <= LIMIT_BYTES
            or not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("private_candidate_or_scratch_invalid")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    if len(bodies) != 2:
        raise ValueError("private_two_pass_candidate_incomplete")
    result = []
    with tempfile.TemporaryDirectory(prefix="t2-private-cb0-member-shape-", dir=scratch) as tmp:
        work = Path(tmp)
        for pass_idx, body in enumerate(bodies):
            hlsl = work / ("p%d-embedded.hlsl" % pass_idx)
            hlsl.write_text(body, encoding="utf-8")
            stages = {}
            for stage, kind in (("VERTEX", "vert"), ("FRAGMENT", "frag")):
                spv = work / ("p%d-%s.spv" % (pass_idx, kind))
                if not invoke(["glslangValidator", "-V", "-D",
                               "-DSHADER_STAGE_" + stage + "=1",
                               "-S", kind, "-e", "main", "-o", str(spv), str(hlsl)]):
                    raise ValueError("private_original_spv_compile_failed")
                if (not spv.is_file() or not _physical(spv)
                        or not 20 <= spv.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(spv)])):
                    raise ValueError("private_original_spv_validation_failed")
                stages[kind] = reflect(spv)
            counts = compare_private_cb0_geometry(stages["vert"], stages["frag"])
            counts["pass_index"] = pass_idx
            result.append(counts)
    if len(result) != 2:
        raise ValueError("private_original_two_passes_not_checked")
    return {
        "status": "private_two_pass_CB0_member_geometry_observed",
        "compiled_stage_variants": 4,
        "pass_count": 2,
        "per_pass_CB0_member_geometry": result,
        "original_member_semantics_or_CBuffer_upload_verified": False,
        "actual_Unity_2021_or_Adreno_verified": False,
        "private_identifiers_or_spirv_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out) or out.exists()
                or out.is_relative_to(args.candidate.absolute())
                or out.is_relative_to(args.scratch.absolute()) is False):
            raise ValueError("unsafe_private_report_destination")
        data = inspect_private_candidate(args.candidate, args.scratch)
        exit_code = 0
    except BaseException:
        data = {
            "status": "blocked_private_CB0_member_geometry",
            "original_member_semantics_or_CBuffer_upload_verified": False,
            "actual_Unity_2021_or_Adreno_verified": False,
            "private_identifiers_or_spirv_published": False,
        }
        exit_code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_CB0_MEMBER_SHAPE_SAFE " + json.dumps(data, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
