"""Bounded component-aware may-reach audit for original FFT slot0 SPIR-V.

A constant OpAccessChain index only disambiguates a physical vector element
when the base is an exact Function pointer to that vector, the result points
to its scalar, and the SSA load lane can be traced without guessing.
May-reach is NOT a complete memory/alias proof or a numerical shader fix.
Public output excludes SSA IDs, constant values, original code and pixels.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import (
    image_role, lane_predecessor, read_module, value_shape,
)
from scripts.t1_fft_spirv_reaching_stores import (
    MAX_BLOCKS, aliases, parse_functions,
)

UNKNOWN_WRITE = -2
ESCAPED_POINTER = -3
UNINITIALIZED = -1
MAX_DEPTH = 12
MAX_INSTRUCTIONS = 60000

ACCESS = {"OpAccessChain", "OpInBoundsAccessChain"}
UNSUPPORTED_ACCESS = {"OpPtrAccessChain", "OpInBoundsPtrAccessChain"}


def load_physical_lane(root, axis, values, types):
    """Walk vector constructs/shuffles to the physical component of a load."""
    visited = set()
    value, lane = root, axis
    for _ in range(MAX_DEPTH + 1):
        if (value, lane) in visited:
            return None, None, "cycle"
        visited.add((value, lane))
        kind, width = value_shape(value, values, types)
        if kind == "unresolved" or lane < 0 or lane >= width:
            return None, None, "unresolved_lane"
        op, _, args = values.get(value, ("", None, []))
        if op == "OpLoad" and len(args) >= 1:
            return value, lane, "load"
        if op in ("OpConstant", "OpConstantComposite", "OpConstantNull"):
            return None, None, "constant"
        if op == "OpUndef":
            return None, None, "undefined"
        next_lane = lane_predecessor(op, args, lane, width, values, types)
        if next_lane is None:
            return None, None, "unresolved_lane"
        value, lane = next_lane
    return None, None, "depth_limit"


def local_vector_shape(pointer, values, types):
    var_op, ptr_type, var_args = values.get(pointer, ("", None, []))
    typ_op, typ_args = types.get(ptr_type, ("", []))
    if (var_op != "OpVariable" or not var_args or var_args[0] != "Function"
            or typ_op != "OpTypePointer" or len(typ_args) != 2
            or typ_args[0] != "Function"):
        return None
    vec_op, vec_args = types.get(typ_args[1], ("", []))
    if vec_op != "OpTypeVector" or len(vec_args) != 2:
        return None
    try:
        width = int(vec_args[1])
    except ValueError:
        return None
    scalar_op, scalar_args = types.get(vec_args[0], ("", []))
    if not 2 <= width <= 4 or (scalar_op, scalar_args) not in (
            ("OpTypeFloat", ["32"]), ("OpTypeInt", ["32", "0"]),
            ("OpTypeInt", ["32", "1"])):
        return None
    return {"width": width, "pointer_type": ptr_type,
            "scalar_type": vec_args[0], "element_type": typ_args[1]}


def index_value(value, values, types):
    op, type_id, args = values.get(value, ("", None, []))
    if op != "OpConstant" or len(args) != 1:
        return None
    ty_op, ty_args = types.get(type_id, ("", []))
    if ty_op != "OpTypeInt" or ty_args not in (["32", "0"], ["32", "1"]):
        return None
    try:
        return int(args[0], 0)
    except ValueError:
        return None


def pointer_effect(candidate, base, target_lane, shape, values, types):
    """Target lane may be affected: whole / same_lane / other_lane / unknown."""
    seen = set()
    current = candidate
    for _ in range(64):
        if current == base:
            return "whole"
        if current in seen:
            return "unknown"
        seen.add(current)
        op, result_type, args = values.get(current, ("", None, []))
        if op == "OpCopyObject" and len(args) == 1:
            if result_type != values.get(args[0], ("", None, []))[1]:
                return "unknown"
            current = args[0]
            continue
        if op in ACCESS and args and aliases(args[0], base, values):
            # Prove a single step directly from the Function vector base.
            source = args[0]
            for _ in range(64):
                if source == base:
                    break
                source_op, source_ty, source_args = values.get(source, ("", None, []))
                if (source_op != "OpCopyObject" or len(source_args) != 1
                        or source_ty != values.get(source_args[0], ("", None, []))[1]):
                    return "unknown"
                source = source_args[0]
            if source != base or len(args) != 2:
                return "unknown"
            ptr_op, ptr_args = types.get(result_type, ("", []))
            if (ptr_op != "OpTypePointer" or ptr_args !=
                    ["Function", shape["scalar_type"]]):
                return "unknown"
            lane = index_value(args[1], values, types)
            if lane is None or not 0 <= lane < shape["width"]:
                return "unknown"
            return "same_lane" if lane == target_lane else "other_lane"
        if op in UNSUPPORTED_ACCESS or aliases(current, base, values):
            return "unknown"
        return "unrelated"
    return "unknown"


def analyze_load(load_id, physical_lane, funcs, values, types):
    op, _, args = values.get(load_id, ("", None, []))
    if op != "OpLoad" or not args:
        return {"status": "unresolved_load", "numerical_origin_proven": False}
    base = args[0]
    shape = local_vector_shape(base, values, types)
    if shape is None or physical_lane >= shape["width"]:
        return {"status": "unsupported_local_type", "numerical_origin_proven": False}

    owners = [(f, b, idx) for f in funcs for b, instructions in f["blocks"].items()
              for idx, (_, result, _) in enumerate(instructions)
              if result == load_id]
    if len(owners) != 1:
        return {"status": "ambiguous_load_owner", "numerical_origin_proven": False}
    fun, load_block, load_at = owners[0]
    blocks, edges = fun["blocks"], fun["edges"]
    static = Counter()
    writers = {}
    for block, instr in blocks.items():
        for offset, (code, _, operands) in enumerate(instr):
            if code != "OpStore" or len(operands) < 2:
                continue
            effect = pointer_effect(operands[0], base, physical_lane, shape, values, types)
            static[effect] += 1
            if effect in ("whole", "same_lane"):
                writers[(block, offset)] = (len(writers), effect, operands[1])
    if len(writers) > MAX_INSTRUCTIONS:
        raise ValueError("Excessive private writer count")

    def transfer(state, op, operands, location):
        if op == "OpStore" and len(operands) >= 2:
            destination, source = operands[:2]
            effect = pointer_effect(destination, base, physical_lane, shape, values, types)
            if effect in ("whole", "same_lane"):
                # Preserve pointer-escape/unknown-write uncertainty conservatively.
                hazards = {x for x in state if x in (UNKNOWN_WRITE, ESCAPED_POINTER)}
                return {writers[location][0]} | hazards
            if effect == "unknown":
                return state | {UNKNOWN_WRITE}
            if source == base or aliases(source, base, values):
                return state | {ESCAPED_POINTER}
        if op in ("OpCopyMemory", "OpCopyMemorySized") and operands:
            effect = pointer_effect(operands[0], base, physical_lane, shape, values, types)
            if effect != "unrelated" and effect != "other_lane":
                return state | {UNKNOWN_WRITE}
        if op == "OpFunctionCall" and any(aliases(x, base, values) for x in operands[1:]):
            return state | {UNKNOWN_WRITE}
        if op.startswith("OpAtomic") and operands:
            effect = pointer_effect(operands[0], base, physical_lane, shape, values, types)
            if effect not in ("unrelated", "other_lane"):
                return state | {UNKNOWN_WRITE}
        return state

    incoming = {label: None for label in blocks}
    incoming[fun["entry"]] = {UNINITIALIZED}
    for _ in range(MAX_BLOCKS * 2):
        modified = False
        for block, instructions in blocks.items():
            if incoming[block] is None:
                continue
            state = set(incoming[block])
            for offset, (opcode, _, operands) in enumerate(instructions):
                state = transfer(state, opcode, operands, (block, offset))
            for next_block in edges[block]:
                old = incoming[next_block]
                new = state if old is None else old | state
                if old is None or new != old:
                    incoming[next_block] = set(new)
                    modified = True
        if not modified:
            break
    else:
        raise ValueError("Private component dataflow did not converge")
    if incoming[load_block] is None:
        return {"status": "unreachable", "numerical_origin_proven": False}
    state = set(incoming[load_block])
    for offset, (opcode, _, operands) in enumerate(blocks[load_block][:load_at]):
        state = transfer(state, opcode, operands, (load_block, offset))

    categories = Counter()
    opcodes = Counter()
    for block, offset in writers:
        ordinal, effect, value = writers[(block, offset)]
        if ordinal in state:
            categories[effect] += 1
            producer = values.get(value, ("unresolved", None, []))[0]
            opcodes[producer if producer.startswith("Op") and producer[2:].isalnum()
                    else "unresolved"] += 1
    return {
        "status": "component_aware_may_reach",
        "static_whole_writers": static["whole"],
        "static_same_lane_writers": static["same_lane"],
        "static_other_lane_writers": static["other_lane"],
        "static_unknown_alias_writers": static["unknown"],
        "reachable_writer_count": sum(categories.values()),
        "reachable_writer_forms": dict(sorted(categories.items())),
        "reachable_value_opcodes": dict(sorted(opcodes.items())),
        "uninitialized_possible": UNINITIALIZED in state,
        "unknown_write_possible": UNKNOWN_WRITE in state,
        "pointer_escape_possible": ESCAPED_POINTER in state,
        "full_value_proven": False,
        "numerical_origin_proven": False,
    }


def analyze(disassembly, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(disassembly)
    functions = parse_functions(disassembly)
    if len(fetches) > 16:
        raise ValueError("Unexpected private fetch count")
    roles = [image_role(root, values, decorations) for root, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected original source FFT fetch roles")
    sites = []
    for site, ((_, coord), role) in enumerate(zip(fetches, roles)):
        lanes = {}
        for axis, number in (("x", 0), ("y", 1)):
            load, lane, boundary = load_physical_lane(coord, number, values, types)
            lanes[axis] = analyze_load(load, lane, functions, values, types) if load else {
                "status": boundary, "numerical_origin_proven": False}
            if load is not None:
                lanes[axis]["physical_load_lane"] = "x" if lane == 0 else (
                    "y" if lane == 1 else "other")
        sites.append({"site": site, "role": role, "lanes": lanes})
    return {"scope": "static_function_vector_component_may_reach",
            "no_private_identifiers_exported": True,
            "original_integer_origin_proven": False, "sites": sites}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private source SPIR-V size out of bound")
        d = subprocess.run(["spirv-dis", "--raw-id", str(args.module)], timeout=20,
                           check=True, capture_output=True, text=True)
        result = analyze(d.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private FFT component-alias audit failed\n")
    print("RAFT_T1_FFT_VECTOR_LANE_EFFECT " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
