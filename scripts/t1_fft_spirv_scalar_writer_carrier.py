"""Classify typed producer kinds of per-lane original FFT Function-local writers.

This is a bounded static may-reach analysis. OpBitcast preserves bits but does
not by itself prove that an original integer coordinate is numerically correct.
No SPIR-V IDs, constant values, raw shaders or pixels are emitted.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import image_role, read_module, value_shape
from scripts.t1_fft_spirv_reaching_stores import MAX_BLOCKS, aliases, parse_functions
from scripts.t1_fft_spirv_lane_alias_effect import (
    load_physical_lane, local_vector_shape, pointer_effect,
)

UNINIT = -1
UNKNOWN = -2
MAX_VALUE_DEPTH = 10
MAX_WRITERS = 4096


def scalar_carrier(value, values, types):
    """A named type category, never a value's literal bits or its SSA identity."""
    seen = set()
    for _ in range(MAX_VALUE_DEPTH):
        if value in seen:
            return "unresolved_cycle"
        seen.add(value)
        op, dest, args = values.get(value, ("unresolved", None, []))
        kind, width = value_shape(value, values, types)
        if width != 1:
            return "unresolved_non_scalar"
        if op == "OpCopyObject" and len(args) == 1:
            if value_shape(args[0], values, types) != (kind, width):
                return "unresolved_copy_type"
            value = args[0]
            continue
        if op == "OpConstant" and len(args) == 1:
            return kind + "_constant"
        if op == "OpBitcast" and len(args) == 1:
            src_kind, src_width = value_shape(args[0], values, types)
            if src_width != 1:
                return "unresolved_bitcast_shape"
            if kind == "float32" and src_kind in ("sint32", "uint32"):
                return src_kind + "_bits_to_float32"
            if kind in ("sint32", "uint32") and src_kind == "float32":
                return "float32_bits_to_" + kind
            return "other_bitcast"
        if op in ("OpConvertSToF", "OpConvertUToF") and len(args) == 1:
            src_kind, src_width = value_shape(args[0], values, types)
            if kind == "float32" and src_width == 1:
                return "numeric_" + src_kind + "_to_float32"
            return "unresolved_numeric_conversion"
        if op == "OpLoad":
            return kind + "_load"
        if op.startswith("Op") and op[2:].isalnum():
            return kind + "_other_opcode"
        return "unresolved_opcode"
    return "unresolved_depth"


def may_reaching_writers(fun, load_id, physical_lane, base, shape, values, types):
    blocks, edges = fun["blocks"], fun["edges"]
    load_positions = [(block, idx) for block, instructions in blocks.items()
                      for idx, (_, result, _) in enumerate(instructions)
                      if result == load_id]
    if len(load_positions) != 1:
        raise ValueError("Unresolved private load ownership")
    load_block, load_at = load_positions[0]

    candidates = {}
    for block, instructions in blocks.items():
        for idx, (op, _, args) in enumerate(instructions):
            if op != "OpStore" or len(args) < 2:
                continue
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect in ("whole", "same_lane"):
                if len(candidates) >= MAX_WRITERS:
                    raise ValueError("Too many bounded original writer candidates")
                candidates[(block, idx)] = (len(candidates), effect, args[1])

    def next_state(state, op, args, location):
        if op == "OpStore" and len(args) >= 2:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect in ("whole", "same_lane"):
                return {candidates[location][0]} | ({UNKNOWN} if UNKNOWN in state else set())
            if effect == "unknown" or args[1] == base or aliases(args[1], base, values):
                return state | {UNKNOWN}
        elif op in ("OpCopyMemory", "OpCopyMemorySized") and args:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect in ("whole", "same_lane", "unknown"):
                return state | {UNKNOWN}
        elif op == "OpFunctionCall" and any(aliases(x, base, values) for x in args[1:]):
            return state | {UNKNOWN}
        elif op.startswith("OpAtomic") and args:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect not in ("other_lane", "unrelated"):
                return state | {UNKNOWN}
        return state

    incoming = {block: None for block in blocks}
    incoming[fun["entry"]] = {UNINIT}
    for _ in range(MAX_BLOCKS * 2):
        changed = False
        for block, instructions in blocks.items():
            if incoming[block] is None:
                continue
            state = set(incoming[block])
            for idx, (op, _, args) in enumerate(instructions):
                state = next_state(state, op, args, (block, idx))
            for successor in edges[block]:
                old = incoming[successor]
                new = state if old is None else old | state
                if old is None or old != new:
                    incoming[successor] = set(new)
                    changed = True
        if not changed:
            break
    else:
        raise ValueError("Private FFT writer dataflow budget exceeded")

    if incoming[load_block] is None:
        return {"status": "unreachable", "numeric_origin_proven": False}
    result_set = set(incoming[load_block])
    for idx, (op, _, args) in enumerate(blocks[load_block][:load_at]):
        result_set = next_state(result_set, op, args, (load_block, idx))
    typed_component, whole_count = Counter(), 0
    for _, (ordinal, effect, value) in candidates.items():
        if ordinal in result_set:
            if effect == "same_lane":
                typed_component[scalar_carrier(value, values, types)] += 1
            else:
                whole_count += 1
    return {"status": "typed_may_reach",
            "component_producer_categories": dict(sorted(typed_component.items())),
            "whole_vector_writer_candidates": whole_count,
            "may_reach_writer_count": whole_count + sum(typed_component.values()),
            "unknown_writer_possible": UNKNOWN in result_set,
            "uninitialized_path_possible": UNINIT in result_set,
            "numeric_origin_proven": False}


def analyze(text, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > 16:
        raise ValueError("Unexpected private fetch count")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected original shader descriptor identity")
    sites = []
    for site, ((_, coord), role) in enumerate(zip(fetches, roles)):
        lanes = {}
        for axis, lane in (("x", 0), ("y", 1)):
            load, physical_lane, status = load_physical_lane(coord, lane, values, types)
            if load is None:
                lanes[axis] = {"status": status, "numeric_origin_proven": False}
                continue
            pointer = values[load][2][0]
            shape = local_vector_shape(pointer, values, types)
            if shape is None:
                lanes[axis] = {"status": "unsupported_local_vector", "numeric_origin_proven": False}
                continue
            owners = [f for f in functions if any(result == load
                for ins in f["blocks"].values() for _, result, _ in ins)]
            if len(owners) != 1:
                raise ValueError("Ambiguous function owner of private FFT read")
            item = may_reaching_writers(owners[0], load, physical_lane,
                                        pointer, shape, values, types)
            item["physical_load_lane"] = (
                "x" if physical_lane == 0 else "y" if physical_lane == 1 else "other")
            lanes[axis] = item
        sites.append({"site": site, "role": role, "lanes": lanes})
    return {"scope": "private_original_scalar_bit_carrier_candidates",
            "private_ids_and_literals_exported": False,
            "original_integer_coordinate_semantics_proven": False,
            "sites": sites}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private input size outside bound")
        d = subprocess.run(["spirv-dis", "--raw-id", str(args.module)], check=True,
                           capture_output=True, text=True, timeout=20)
        report = analyze(d.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private original FFT scalar carrier audit failed\n")
    print("RAFT_T1_FFT_SCALAR_WRITER_CARRIERS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
