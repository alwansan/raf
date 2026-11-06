"""Source-authentic Foam CB0 compiled SPIR-V load-index diagnostics.

Fail closed for unknown pointer operations. A compiled OpLoad path is NOT a
runtime-executed access, a complete dataflow proof, or Unity upload evidence.
Source names, absolute IDs, shader bytes, exact indices and capacities stay private.
"""
import argparse
import json
from pathlib import Path
import struct
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_candidate_embedded_validation import (
    _invoke, extract_embedded_programs, LIMIT_BYTES
)
from scripts.t2_foam_embedded_stage_io import reflect_stage
from scripts.t2_foam_private_cb0_member_shape import _ubo_map, _member_geometry
from scripts.t2_foam_private_descriptor_set_remap import (
    scan_binary_decorations, reflected_ids
)
from scripts.t2_foam_original_pair_compile import MAX_SPV

OP_TYPE_INT = 21
OP_CONSTANT = 43
OP_CONSTANT_NULL = 46
OP_ACCESS_CHAIN = 65
OP_IN_BOUNDS_ACCESS_CHAIN = 66
OP_PTR_ACCESS_CHAIN = 67
OP_IN_BOUNDS_PTR_ACCESS_CHAIN = 70
OP_LOAD = 61
OP_COPY_OBJECT = 83
OP_PHI = 245
OP_SELECT = 169
OP_FUNCTION_CALL = 57
OP_COPY_MEMORY = 63
OP_COPY_MEMORY_SIZED = 64
MAX_COMPILED_LOAD_PATHS = 4096
MAX_INSTRUCTIONS = 200000


def private_shared_ubo(vertex, fragment):
    """Authenticate one same-coordinate UBO with a one-dimensional array member."""
    vs, fs = _ubo_map(vertex, "vert"), _ubo_map(fragment, "frag")
    shared = set(vs) & set(fs)
    if len(shared) != 1:
        raise ValueError("ambiguous_private_shared_ubo")
    coord = next(iter(shared))
    vm, fm = _member_geometry(vertex, vs[coord]), _member_geometry(fragment, fs[coord])
    if len(vm) != 1 or len(fm) != 1 or set(vm) != set(fm):
        raise ValueError("private_array_member_identity_unproved")
    v, f = vm[next(iter(vm))], fm[next(iter(fm))]
    if (v[0] != f[0] or v[2:] != f[2:]
            or len(v[1]) != 1 or len(f[1]) != 1
            or v[1] == f[1]):
        raise ValueError("private_array_shape_hypothesis_not_observed")
    return coord, v[1][0], f[1][0]


def _instructions(blob):
    words, bindings, sets, _ = scan_binary_decorations(blob)
    bound = words[3]
    result = []
    pos = 5
    while pos < len(words):
        header = words[pos]
        count, op = header >> 16, header & 0xffff
        if count < 1 or pos + count > len(words):
            raise ValueError("invalid_private_spirv_instruction")
        result.append((op, words[pos+1:pos+count]))
        if len(result) > MAX_INSTRUCTIONS:
            raise ValueError("unbounded_private_spirv_instruction_count")
        pos += count
    if pos != len(words):
        raise ValueError("private_spirv_instruction_alignment_invalid")
    return result, bound, bindings, sets


def compiled_cb0_load_paths(blob, reflection, coordinate, own_length, other_length):
    """Count observed SPIR-V OpLoad indexing, never assert all possible reads.

    Root ID joins reflection through exact binary OpDecorate set+binding, not
    symbol names or declaration order. Only direct AccessChain/CopyObject
    pointer provenance is tracked; unsupported pointer flows block proof.
    """
    if (type(own_length) is not int or type(other_length) is not int
            or not 1 <= own_length <= 65536 or not 1 <= other_length <= 65536
            or not isinstance(coordinate, tuple) or len(coordinate) != 2):
        raise ValueError("invalid_private_CB0_array_capacity")
    instructions, bound, bindings, sets = _instructions(blob)
    mode = reflection["entryPoints"][0]["mode"]
    joined = reflected_ids(reflection, bindings, sets, mode=mode)
    roots = [ident for ident, coord in joined.items() if coord == coordinate]
    if len(roots) != 1:
        raise ValueError("CB0_reflected_binary_id_not_unique")
    root = roots[0]
    int_types, constants = {}, {}
    aliases = {root: ()}
    static_loads = dynamic_loads = whole_loads = 0
    outside_own = outside_other = 0
    unresolved_paths = 0
    static_in_common = 0

    for op, args in instructions:
        if op == OP_TYPE_INT:
            if len(args) != 3 or not 0 < args[0] < bound:
                raise ValueError("malformed_private_index_integer_type")
            int_types[args[0]] = (args[1], args[2])
        elif op in (OP_CONSTANT, OP_CONSTANT_NULL):
            if len(args) < 2 or not 0 < args[1] < bound:
                raise ValueError("malformed_private_constant_index")
            typ = int_types.get(args[0])
            if typ == (32, 0) or typ == (32, 1):
                if op == OP_CONSTANT and len(args) == 3:
                    value = args[2]
                elif op == OP_CONSTANT_NULL and len(args) == 2:
                    value = 0
                else:
                    value = None
                if value is not None and typ[1] == 1 and value >= 2**31:
                    value = None
                if value is not None:
                    constants[args[1]] = value
        elif op in (OP_ACCESS_CHAIN, OP_IN_BOUNDS_ACCESS_CHAIN):
            if len(args) < 4 or not 0 < args[1] < bound:
                raise ValueError("malformed_private_access_chain")
            base = args[2]
            if base in aliases:
                if args[1] in aliases:
                    raise ValueError("duplicate_private_pointer_id")
                aliases[args[1]] = (None if aliases[base] is None
                                    else aliases[base] + tuple(args[3:]))
        elif op in (OP_PTR_ACCESS_CHAIN, OP_IN_BOUNDS_PTR_ACCESS_CHAIN):
            if len(args) < 4:
                raise ValueError("malformed_private_ptr_access_chain")
            if args[2] in aliases:
                unresolved_paths += 1
                aliases[args[1]] = None
        elif op == OP_COPY_OBJECT:
            if len(args) != 3:
                raise ValueError("malformed_private_pointer_copy")
            if args[2] in aliases:
                aliases[args[1]] = aliases[args[2]]
        elif op == OP_PHI:
            if len(args) < 4 or len(args[2:]) % 2:
                raise ValueError("malformed_private_pointer_phi")
            if any(i in aliases for i in args[2::2]):
                unresolved_paths += 1
                aliases[args[1]] = None
        elif op == OP_SELECT:
            if len(args) != 5:
                raise ValueError("malformed_private_pointer_select")
            if args[3] in aliases or args[4] in aliases:
                unresolved_paths += 1
                aliases[args[1]] = None
        elif op == OP_FUNCTION_CALL:
            if len(args) < 3:
                raise ValueError("malformed_private_function_call")
            if any(a in aliases for a in args[3:]):
                unresolved_paths += 1
        elif op in (OP_COPY_MEMORY, OP_COPY_MEMORY_SIZED):
            if len(args) < 2:
                raise ValueError("malformed_private_memory_copy")
            if args[0] in aliases or args[1] in aliases:
                unresolved_paths += 1
        elif op == OP_LOAD:
            if len(args) < 3:
                raise ValueError("malformed_private_load")
            pointer = args[2]
            if pointer not in aliases:
                continue
            path = aliases[pointer]
            if path is None or len(path) < 2 or constants.get(path[0]) != 0:
                unresolved_paths += 1
                if path is not None and len(path) == 1:
                    whole_loads += 1
                continue
            idx = constants.get(path[1])
            if idx is None:
                dynamic_loads += 1
            else:
                static_loads += 1
                outside_own += idx >= own_length
                outside_other += idx >= other_length
                static_in_common += idx < min(own_length, other_length)
            if (static_loads + dynamic_loads + unresolved_paths
                    > MAX_COMPILED_LOAD_PATHS):
                raise ValueError("unbounded_private_cb0_load_path_count")
    return {
        "observed_static_index_load_count": static_loads,
        "observed_dynamic_or_unknown_index_load_count": dynamic_loads,
        "observed_unresolved_pointer_or_whole_load_count": unresolved_paths,
        "observed_whole_array_load_count": whole_loads,
        "static_index_exceeds_own_reflected_array_count": outside_own,
        "static_index_exceeds_other_stage_array_count": outside_other,
        "static_index_in_common_reflected_prefix_count": static_in_common,
        "observed_load_index_paths_not_runtime_access_proof": True,
        "no_trace_means_no_reads_proven": False,
    }


def inspect_candidate(candidate, scratch, *, invoke=_invoke, reflect=reflect_stage):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or not 0 < candidate.stat().st_size <= LIMIT_BYTES
            or not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("unsafe_private_candidate_or_scratch")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    if len(bodies) != 2:
        raise ValueError("private_two_pass_candidate_missing")
    output = []
    with tempfile.TemporaryDirectory(prefix="t2-original-cb0-index-", dir=scratch) as tmp:
        tmp = Path(tmp)
        for pi, body in enumerate(bodies):
            hlsl = tmp / ("p%d-private.hlsl" % pi)
            hlsl.write_text(body, encoding="utf-8")
            refs, binaries = {}, {}
            for mode, macro in (("vert", "VERTEX"), ("frag", "FRAGMENT")):
                spv = tmp / ("p%d-%s.spv" % (pi, mode))
                if not invoke(["glslangValidator", "-V", "-D",
                               "-DSHADER_STAGE_" + macro + "=1",
                               "-S", mode, "-e", "main",
                               "-o", str(spv), str(hlsl)]):
                    raise ValueError("private_original_compile_failed")
                if (not spv.is_file() or not _physical(spv)
                        or not 20 <= spv.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1", str(spv)])):
                    raise ValueError("private_original_validation_failed")
                refs[mode], binaries[mode] = reflect(spv), spv.read_bytes()
            coord, vl, fl = private_shared_ubo(refs["vert"], refs["frag"])
            vs = compiled_cb0_load_paths(binaries["vert"], refs["vert"], coord, vl, fl)
            fs = compiled_cb0_load_paths(binaries["frag"], refs["frag"], coord, fl, vl)
            output.append({
                "pass_index": pi,
                "relative_array_capacity": ("vertex_larger" if vl > fl else "fragment_larger"),
                "same_member_start_type_and_stride": True,
                "vertex_compiled_loads": vs,
                "fragment_compiled_loads": fs,
            })
    return {
        "status": "authentic_two_pass_CB0_compiled_load_paths_observed",
        "original_pass_count": 2,
        "original_compiled_stage_count": 4,
        "per_pass_relative_loads": output,
        "active_runtime_branch_reachability_verified": False,
        "Unity_original_CB0_upload_verified": False,
        "Android_Adreno_water_verified": False,
        "private_names_indices_and_spirv_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("candidate", "scratch", "out"):
        p.add_argument("--"+key, required=True, type=Path)
    a = p.parse_args()
    out = a.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out) or out.exists()
                or out.is_relative_to(a.candidate.absolute())
                or not out.is_relative_to(a.scratch.absolute())):
            raise ValueError("unsafe_private_report_path")
        data = inspect_candidate(a.candidate, a.scratch)
        rc = 0
    except BaseException:
        data = {
            "status": "blocked_private_CB0_index_analysis",
            "active_runtime_branch_reachability_verified": False,
            "Unity_original_CB0_upload_verified": False,
            "Android_Adreno_water_verified": False,
            "private_names_indices_and_spirv_published": False,
        }
        rc = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(data, sort_keys=True)+"\n", encoding="utf-8")
    print("T2_CB0_COMPILED_LOAD_SAFE " + json.dumps(data, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
