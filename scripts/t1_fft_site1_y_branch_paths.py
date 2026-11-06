"""Bounded CFG path-witness classes for private original FFT butterfly-1 Y.

This follows potential control-flow paths, NOT satisfiable GPU invocations.
Any predicate families are observed on paths, not proofs they select a writer.
Never export original SPIR-V identifiers, literal values or shader bytecode.
"""
import argparse
from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import image_role, read_module
from scripts.t1_fft_spirv_reaching_stores import aliases, parse_functions
from scripts.t1_fft_spirv_lane_alias_effect import (
    load_physical_lane, local_vector_shape, pointer_effect,
)
from scripts.t1_fft_spirv_scalar_writer_carrier import scalar_carrier

MAX_ABSTRACT_STATES = 35000
MAX_BLOCKS = 512
MAX_FETCHES = 16
MAX_CATEGORIES = 16
ALLOWED_PREDICATES = (
    "OpSLessThan", "OpULessThan", "OpSGreaterThan", "OpUGreaterThan",
    "OpIEqual", "OpINotEqual", "OpFOrdLessThan", "OpFOrdGreaterThan",
    "OpLogicalAnd", "OpLogicalOr", "OpLogicalNot", "OpSelect",
    "OpPhi", "OpLoad", "OpCompositeExtract", "OpConstantTrue",
    "OpConstantFalse", "OpFunctionCall",
)


def safe_category(category):
    if category in ("whole_vector", "uninitialized", "unknown_write", "pointer_escape"):
        return category
    if category in ("sint32_bits_to_float32", "uint32_bits_to_float32",
                    "float32_constant", "float32_load", "numeric_sint32_to_float32",
                    "numeric_uint32_to_float32", "other_bitcast",
                    "unresolved_non_scalar", "unresolved_depth"):
        return category
    return "other_scalar"


def safe_predicate(op):
    return op if op in ALLOWED_PREDICATES else "other_predicate"


def writer_event(op, operands, base, lane, shape, values, types):
    """Return None, or safe writer category; unknown writes fail closed."""
    if op == "OpStore" and len(operands) >= 2:
        dst, src = operands[:2]
        effect = pointer_effect(dst, base, lane, shape, values, types)
        if effect == "whole":
            return "whole_vector"
        if effect == "same_lane":
            return safe_category(scalar_carrier(src, values, types))
        if effect == "unknown":
            return "unknown_write"
        if src == base or aliases(src, base, values):
            return "pointer_escape"
    elif op in ("OpCopyMemory", "OpCopyMemorySized") and operands:
        effect = pointer_effect(operands[0], base, lane, shape, values, types)
        if effect in ("whole", "same_lane", "unknown"):
            return "unknown_write"
    elif op == "OpFunctionCall":
        if any(aliases(v, base, values) for v in operands[1:]):
            return "unknown_write"
    elif op.startswith("OpAtomic") and operands:
        effect = pointer_effect(operands[0], base, lane, shape, values, types)
        if effect not in ("other_lane", "unrelated"):
            return "unknown_write"
    return None


def path_witness(fun, load_id, physical_lane, base, shape, values, types):
    blocks, edges = fun["blocks"], fun["edges"]
    if len(blocks) > MAX_BLOCKS:
        raise ValueError("Private CFG block limit exceeded")
    load_positions = [(b, idx) for b, ins in blocks.items()
                      for idx, (_, rid, _) in enumerate(ins) if rid == load_id]
    if len(load_positions) != 1:
        raise ValueError("Ambiguous private load")
    load_block, load_idx = load_positions[0]
    static = Counter()
    for ins in blocks.values():
        for op, _, args in ins:
            event = writer_event(op, args, base, physical_lane, shape, values, types)
            if event is not None:
                static[event] += 1
    if len(static) > MAX_CATEGORIES:
        raise ValueError("Unexpected typed FFT writer diversity")
    # State: block, offset, last writer, has seen bitcarrier, has seen constant,
    # predicates encountered, has crossed a CFG backward edge, pointer escape.
    order = {b: i for i, b in enumerate(blocks)}
    init = (fun["entry"], 0, "uninitialized", False, False, 0, False, False)
    queue = deque([init])
    seen = {init}
    endings = set()
    while queue:
        if len(seen) > MAX_ABSTRACT_STATES:
            raise ValueError("Private CFG path-state bound exceeded")
        block, offset, last, bit, const, mask, backwards, escaped = queue.popleft()
        if (block, offset) == (load_block, load_idx):
            endings.add((last, bit, const, mask, backwards, escaped))
            continue
        instr = blocks[block]
        if offset >= len(instr):
            raise ValueError("Missing private basic block terminator")
        op, _, args = instr[offset]
        event = writer_event(op, args, base, physical_lane, shape, values, types)
        if event == "pointer_escape":
            escaped = True
        elif event is not None:
            last = event
            bit = bit or event == "sint32_bits_to_float32"
            const = const or event == "float32_constant"
        if op == "OpBranchConditional":
            if len(args) < 3:
                raise ValueError("Incomplete conditional branch")
            producer = values.get(args[0], ("unresolved", None, []))[0]
            tag = safe_predicate(producer)
            bit_index = ALLOWED_PREDICATES.index(tag) if tag in ALLOWED_PREDICATES else len(ALLOWED_PREDICATES)
            mask |= 1 << bit_index
        elif op == "OpSwitch":
            mask |= 1 << (len(ALLOWED_PREDICATES) + 1)
        if op in ("OpBranch", "OpBranchConditional", "OpSwitch"):
            targets = edges[block]
            successors = [(target, 0) for target in targets]
        elif op in ("OpReturn", "OpReturnValue", "OpKill",
                    "OpUnreachable", "OpTerminateInvocation"):
            successors = []
        else:
            successors = [(block, offset + 1)]
        for target, next_offset in successors:
            edge_back = backwards or (
                target != block and order[target] <= order[block])
            key = (target, next_offset, last, bit, const, mask, edge_back, escaped)
            if key not in seen:
                seen.add(key)
                queue.append(key)

    if not endings:
        return {"status": "unreachable_load",
                "full_execution_path_proven": False}
    final = Counter(last for last, *_ in endings)
    pred_by_final = defaultdict(set)
    backwards_by_final = defaultdict(bool)
    for last, seen_bit, seen_const, mask, backwards, escaped in endings:
        for idx, pred in enumerate(ALLOWED_PREDICATES):
            if mask & (1 << idx):
                pred_by_final[last].add(pred)
        if mask & (1 << len(ALLOWED_PREDICATES)):
            pred_by_final[last].add("other_predicate")
        if mask & (1 << (len(ALLOWED_PREDICATES) + 1)):
            pred_by_final[last].add("OpSwitch")
        backwards_by_final[last] |= backwards

    return {
        "status": "bounded_cfg_may_path_witnesses",
        "static_writer_categories": dict(sorted(static.items())),
        "final_writer_categories_possible": sorted(final),
        "abstract_states_at_load": len(endings),
        "may_visit_bitcarrier_and_float_constant_on_same_cfg_path":
            any(bit and const for _, bit, const, _, _, _ in endings),
        "conditional_predicate_producers_seen_on_paths_by_final_writer":
            {k: sorted(v) for k, v in sorted(pred_by_final.items())},
        "backward_cfg_edge_seen_by_final_writer":
            {k: v for k, v in sorted(backwards_by_final.items())},
        "unknown_final_writer_path_possible": "unknown_write" in final,
        "pointer_escape_seen_on_any_cfg_path": any(s[-1] for s in endings),
        "uninitialized_final_path_possible": "uninitialized" in final,
        "full_execution_path_proven": False,
        "original_integer_numeric_semantics_proven": False,
    }


def analyze(text, *, require_original=False):
    types, values, decorations, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > MAX_FETCHES:
        raise ValueError("Unexpected private fetch count")
    roles = [image_role(img, values, decorations) for img, _ in fetches]
    if require_original and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected source FFT descriptor layout")
    if len(fetches) <= 1:
        raise ValueError("No first butterfly fetch site")
    coordinate = fetches[1][1]
    load, physical_lane, boundary = load_physical_lane(coordinate, 1, values, types)
    if load is None:
        return {"status": boundary, "full_execution_path_proven": False}
    ptr = values[load][2][0]
    shape = local_vector_shape(ptr, values, types)
    if shape is None or physical_lane >= shape["width"]:
        return {"status": "unsupported_local_vector", "full_execution_path_proven": False}
    owners = [f for f in functions if any(
        rid == load for ins in f["blocks"].values() for _, rid, _ in ins)]
    if len(owners) != 1:
        raise ValueError("Original read ownership not unique")
    result = path_witness(owners[0], load, physical_lane, ptr, shape, values, types)
    return {
        "site": 1, "role": "butterfly", "coordinate_lane": "y",
        "physical_load_lane_is_outside_xy": physical_lane >= 2,
        "original_private_ids_exported": False,
        "branch_predicates_are_only_cfg_may_path_observations": True,
        **result
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private source SPIR-V exceeds allowed size")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                             text=True, capture_output=True, check=True, timeout=20)
        report = analyze(dis.stdout, require_original=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private FFT branch path analysis failed\n")
    print("RAFT_T1_FFT_BUTTERFLY_Y_GUARD_PATHS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
