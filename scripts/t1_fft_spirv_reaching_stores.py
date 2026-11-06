"""Bounded CFG-sensitive direct-store candidates for private original FFT SPIR-V.

This analysis follows SSA Function-local coordinate loads only. It computes
may-reach sets across branches/loops; a unique writer does NOT prove original
integer semantics, pointer alias safety, or Android FFT parity. Public output
contains aggregate operation names/counts, never SSA IDs or shader literals.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import (
    MAX_DEPTH, image_role, lane_predecessor, read_module, value_shape,
)

MAX_BLOCKS = 512
MAX_OPERATIONS = 60000
MAX_STORES = 64
UNKNOWN = -2
UNINITIALIZED = -1
TERMINATORS = {"OpBranch", "OpBranchConditional", "OpSwitch", "OpReturn",
               "OpReturnValue", "OpKill", "OpUnreachable", "OpTerminateInvocation"}
EXIT_OPS = {"OpReturn", "OpReturnValue", "OpKill", "OpUnreachable", "OpTerminateInvocation"}
POINTER_ALIAS_OPS = {"OpCopyObject", "OpAccessChain", "OpInBoundsAccessChain",
                     "OpPtrAccessChain", "OpInBoundsPtrAccessChain", "OpPhi", "OpSelect"}


def parse_functions(text):
    functions, current, active = [], None, None
    seen_labels = set()
    op_count = 0
    for raw in text.splitlines():
        tok = raw.split(";", 1)[0].split()
        if not tok:
            continue
        is_assignment = len(tok) >= 3 and tok[1] == "="
        op = tok[2] if is_assignment else tok[0]
        result = tok[0] if is_assignment else None
        args = tok[3:] if is_assignment else tok[1:]
        if op == "OpFunction":
            if current is not None:
                raise ValueError("Nested SPIR-V function")
            current = {"blocks": {}, "entry": None}
            functions.append(current)
            active = None
        elif op == "OpFunctionEnd":
            if current is None or not current["blocks"]:
                raise ValueError("Invalid SPIR-V function end")
            current, active = None, None
        elif current is not None and op == "OpLabel":
            if not result or result in seen_labels or len(current["blocks"]) >= MAX_BLOCKS:
                raise ValueError("Duplicate or excessive block label")
            seen_labels.add(result)
            current["blocks"][result] = []
            if current["entry"] is None:
                current["entry"] = result
            active = result
        elif current is not None and active is not None:
            op_count += 1
            if op_count > MAX_OPERATIONS:
                raise ValueError("Excessive private SPIR-V function operations")
            current["blocks"][active].append((op, result, args))
    if current is not None:
        raise ValueError("Unterminated SPIR-V function")
    for fun in functions:
        blocks = fun["blocks"]
        for instructions in blocks.values():
            if not instructions or instructions[-1][0] not in TERMINATORS:
                raise ValueError("Invalid SPIR-V basic-block terminator")
        edges = {}
        for label, instructions in blocks.items():
            op, _, args = instructions[-1]
            if op == "OpBranch" and len(args) == 1:
                succ = args
            elif op == "OpBranchConditional" and len(args) >= 3:
                succ = args[1:3]
            elif op == "OpSwitch" and len(args) >= 2 and len(args[2:]) % 2 == 0:
                succ = [args[1], *args[3::2]]
            elif op in EXIT_OPS:
                succ = []
            else:
                raise ValueError("Unsupported SPIR-V branch terminator")
            if any(target not in blocks for target in succ):
                raise ValueError("Branch references missing basic block")
            edges[label] = succ
        fun["edges"] = edges
    return functions


def load_leaf(root, lane, values, types):
    value = root
    seen = set()
    for _ in range(MAX_DEPTH + 1):
        if value in seen:
            return None, "cycle"
        seen.add(value)
        _, width = value_shape(value, values, types)
        if not 0 <= lane < width:
            return None, "unresolved"
        op, _, args = values.get(value, ("unresolved", None, []))
        if op == "OpLoad" and args:
            return value, "load"
        if op in ("OpConstant", "OpConstantComposite", "OpConstantNull"):
            return None, "constant"
        if op == "OpUndef":
            return None, "undefined"
        predecessor = lane_predecessor(op, args, lane, width, values, types)
        if predecessor is None:
            return None, "unresolved"
        value, lane = predecessor
    return None, "depth_limit"


def aliases(pointer, target, values):
    """Conservative transitive SSA pointer alias observation, bounded."""
    if pointer == target:
        return True
    pending, seen = [pointer], set()
    while pending:
        item = pending.pop()
        if item in seen:
            continue
        seen.add(item)
        if len(seen) > 256:
            raise ValueError("Pointer alias slice beyond bound")
        op, _, args = values.get(item, ("", None, []))
        if op not in POINTER_ALIAS_OPS:
            continue
        if op == "OpPhi":
            deps = args[::2]
        elif op == "OpSelect":
            deps = args[1:3]
        else:
            deps = args[:1]
        for dep in deps:
            if dep == target:
                return True
            pending.append(dep)
    return False


def store_transfer(op, args, state, pointer, values, ordinal_by_instruction,
                   location):
    if op == "OpStore" and len(args) >= 2:
        if args[0] == pointer:
            return {ordinal_by_instruction[location]}
        if aliases(args[0], pointer, values) or aliases(args[1], pointer, values):
            return set(state) | {UNKNOWN}
    elif op in ("OpCopyMemory", "OpCopyMemorySized") and len(args) >= 2:
        if aliases(args[0], pointer, values) or aliases(args[1], pointer, values):
            return set(state) | {UNKNOWN}
    elif op == "OpFunctionCall" and any(aliases(v, pointer, values) for v in args[1:]):
        return set(state) | {UNKNOWN}
    elif op.startswith("OpAtomic") and any(aliases(v, pointer, values) for v in args[:1]):
        return set(state) | {UNKNOWN}
    return state


def summarize_writer(value, values, types):
    op, _, _ = values.get(value, ("unresolved", None, []))
    if not op.startswith("Op") or not op[2:].isalnum():
        op = "unresolved"
    return op, value_shape(value, values, types)[0]


def analyze_load(load_id, functions, values, types):
    op, _, args = values.get(load_id, ("", None, []))
    if op != "OpLoad" or not args:
        return {"status": "unresolved_load"}
    pointer = args[0]
    var_op, ptr_type, var_args = values.get(pointer, ("", None, []))
    # No claims for alias pointers, non-Function storage or missing declarations.
    storage = types.get(ptr_type, ("", []))
    if (var_op != "OpVariable" or storage[0] != "OpTypePointer"
            or not storage[1] or storage[1][0] != "Function"
            or not var_args or var_args[0] != "Function"):
        return {"status": "nonlocal_or_indirect_load"}
    for fun in functions:
        blocks, edges = fun["blocks"], fun["edges"]
        load_positions = [(label, i) for label, ops in blocks.items()
                          for i, (_, result, _) in enumerate(ops) if result == load_id]
        if not load_positions:
            continue
        if len(load_positions) != 1:
            raise ValueError("Duplicate load result position")
        label, offset = load_positions[0]
        direct_stores = [(b, i, ins[2][1]) for b, instructions in blocks.items()
                         for i, ins in enumerate(instructions)
                         if ins[0] == "OpStore" and len(ins[2]) >= 2 and ins[2][0] == pointer]
        if len(direct_stores) > MAX_STORES:
            raise ValueError("Excessive direct candidate stores")
        by_location = {(b, i): k for k, (b, i, _) in enumerate(direct_stores)}
        input_sets = {b: None for b in blocks}
        input_sets[fun["entry"]] = {UNINITIALIZED}
        converged = False
        for _ in range(MAX_BLOCKS * 2):
            modified = False
            for block, instructions in blocks.items():
                if input_sets[block] is None:
                    continue
                state = set(input_sets[block])
                for i, (opcode, _, operands) in enumerate(instructions):
                    state = store_transfer(opcode, operands, state, pointer, values,
                                           by_location, (block, i))
                for successor in edges[block]:
                    prior = input_sets[successor]
                    merged = state if prior is None else prior | state
                    if prior is None or merged != prior:
                        input_sets[successor] = set(merged)
                        modified = True
            if not modified:
                converged = True
                break
        if not converged:
            raise ValueError("Reaching-store analysis did not converge")
        input_state = input_sets[label]
        if input_state is None:
            return {"status": "unreachable_load",
                    "static_direct_store_candidates": len(direct_stores)}
        state = set(input_state)
        for i, (opcode, _, operands) in enumerate(blocks[label][:offset]):
            state = store_transfer(opcode, operands, state, pointer, values,
                                   by_location, (label, i))
        ids = sorted(index for index in state if index >= 0)
        opcode_counts, kind_counts = Counter(), Counter()
        for index in ids:
            opcode, kind = summarize_writer(direct_stores[index][2], values, types)
            opcode_counts[opcode] += 1
            kind_counts[kind] += 1
        return {
            "status": "function_load_reaching_candidates",
            "static_direct_store_candidates": len(direct_stores),
            "reachable_direct_store_candidates": len(ids),
            "writer_opcodes": dict(sorted(opcode_counts.items())),
            "writer_numeric_kinds": dict(sorted(kind_counts.items())),
            "uninitialized_path_possible": UNINITIALIZED in state,
            "unknown_alias_or_side_effect_path": UNKNOWN in state,
            "unique_direct_store_if_no_unmodeled_aliases": (
                len(ids) == 1 and UNINITIALIZED not in state and UNKNOWN not in state),
            "integer_coordinate_origin_proven": False,
        }
    return {"status": "load_not_in_function"}


def analyze(text, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > 16:
        raise ValueError("Unexpected fetch-site count")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected original FFT fetch-site layout")
    sites = []
    for index, ((_, coordinate), role) in enumerate(zip(fetches, roles)):
        _, width = value_shape(coordinate, values, types)
        if width < 2:
            raise ValueError("Fetch coordinate has no XY lanes")
        lanes = {}
        for number, axis in enumerate(("x", "y")):
            load, boundary = load_leaf(coordinate, number, values, types)
            lanes[axis] = analyze_load(load, functions, values, types) if load else {
                "status": boundary, "integer_coordinate_origin_proven": False}
        sites.append({"site": index, "role": role, "lanes": lanes})
    return {"ssa_ids_exported": False, "original_integer_origin_proven": False,
            "scope": "static_may_reach_function_local_stores", "sites": sites}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("SPIR-V file outside bounded size")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                             check=True, capture_output=True, text=True, timeout=20)
        report = analyze(dis.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private original FFT CFG reaching-store audit failed\n")
    print("RAFT_T1_FFT_CFG_REACHING_STORES " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
