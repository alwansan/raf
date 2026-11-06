"""Original FFT butterfly Y integer-inequality typed branch successor audit.

All results are bounded structural possibilities, not evaluated GPU branches.
Do not publish original IDs, literal operands, game binaries, or sample pixels.
"""
import argparse
from collections import deque
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import image_role, read_module, value_shape
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_spirv_lane_alias_effect import load_physical_lane, local_vector_shape
from scripts.t1_fft_site1_y_branch_paths import writer_event

MAX_BRANCHES = 24
MAX_STATES = 20000
TYPE_KINDS = {"sint32", "uint32", "float32"}
SAFE_PRODUCERS = {
    "OpConstant", "OpSpecConstant", "OpLoad", "OpBitcast",
    "OpCopyObject", "OpCompositeExtract", "OpIAdd", "OpISub",
    "OpIMul", "OpSDiv", "OpUDiv", "OpSMod", "OpShiftRightLogical",
    "OpShiftRightArithmetic", "OpShiftLeftLogical", "OpBitwiseAnd",
    "OpBitwiseOr", "OpBitwiseXor", "OpSelect", "OpPhi",
    "OpSConvert", "OpUConvert", "OpFunctionCall",
}


def operand_info(value, values, types):
    kind, width = value_shape(value, values, types)
    op = values.get(value, ("", None, []))[0]
    return {
        "kind": kind if kind in TYPE_KINDS and width == 1 else
                kind + "_vector" if kind in TYPE_KINDS and 2 <= width <= 4
                else "unresolved",
        "producer": op if op in SAFE_PRODUCERS else "other_opcode",
    }


def suffix_from_branch(fun, start, load_block, load_idx, base, lane,
                       shape, values, types):
    blocks, edges = fun["blocks"], fun["edges"]
    if start not in blocks:
        raise ValueError("SPIR-V branch successor missing")
    entry = (start, 0, "prior_writer", False)
    visited = {entry}
    queue = deque([entry])
    endings = set()
    while queue:
        if len(visited) > MAX_STATES:
            raise ValueError("Original branch suffix state bound exceeded")
        block, idx, last, escaped = queue.popleft()
        if block == load_block and idx == load_idx:
            endings.add((last, escaped))
            continue
        ins = blocks[block]
        if idx >= len(ins):
            raise ValueError("Invalid SPIR-V branch terminator")
        op, _, args = ins[idx]
        effect = writer_event(op, args, base, lane, shape, values, types)
        if effect == "pointer_escape":
            escaped = True
        elif effect is not None:
            last = effect
        if op in ("OpBranch", "OpBranchConditional", "OpSwitch"):
            next_steps = [(to, 0) for to in edges[block]]
        elif op in ("OpReturn", "OpReturnValue", "OpKill",
                    "OpUnreachable", "OpTerminateInvocation"):
            next_steps = []
        else:
            next_steps = [(block, idx + 1)]
        for to, loc in next_steps:
            key = (to, loc, last, escaped)
            if key not in visited:
                visited.add(key)
                queue.append(key)
    return {
        "read_can_be_reached": bool(endings),
        "possible_last_writes_since_branch":
            sorted({kind for kind, _ in endings}),
        "escaped_pointer_possible": any(e for _, e in endings),
    }


def analyze(text, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    funs = parse_functions(text)
    if len(fetches) > 16:
        raise ValueError("Unexpected private fetch count")
    roles = [image_role(img, values, decorations) for img, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Original source descriptor layout mismatch")
    if len(fetches) < 2:
        raise ValueError("Missing butterfly fetch")
    load, lane, status = load_physical_lane(fetches[1][1], 1, values, types)
    if load is None:
        return {"status": status, "dynamic_truth_proven": False}
    base = values[load][2][0]
    shape = local_vector_shape(base, values, types)
    if shape is None:
        return {"status": "unsupported_vector", "dynamic_truth_proven": False}
    owners = [(fun, block, idx) for fun in funs
              for block, seq in fun["blocks"].items()
              for idx, (_, rid, _) in enumerate(seq) if rid == load]
    if len(owners) != 1:
        raise ValueError("Ambiguous Function local load")
    fun, read_block, read_idx = owners[0]
    terminators = {
        "OpBranch", "OpBranchConditional", "OpSwitch", "OpReturn",
        "OpReturnValue", "OpKill", "OpUnreachable", "OpTerminateInvocation",
    }
    for instructions in fun["blocks"].values():
        if any(op in terminators for op, _, _ in instructions[:-1]):
            raise ValueError("SPIR-V terminator is not final in its block")
        if instructions[-1][0] not in terminators:
            raise ValueError("Missing SPIR-V block terminator")
    reachable = {fun["entry"]}
    pending = [fun["entry"]]
    while pending:
        for successor in fun["edges"][pending.pop()]:
            if successor not in reachable:
                reachable.add(successor)
                pending.append(successor)

    branches = []
    for block, instructions in fun["blocks"].items():
        if block not in reachable:
            continue
        for op, _, args in instructions:
            if op != "OpBranchConditional":
                continue
            if len(args) < 3:
                raise ValueError("Malformed original conditional")
            compare, _, operands = values.get(args[0], ("", None, []))
            if compare != "OpINotEqual":
                continue
            if len(operands) != 2:
                raise ValueError("Original OpINotEqual operands malformed")
            if len(branches) >= MAX_BRANCHES:
                raise ValueError("Original inequality branch bound exceeded")
            true_side = suffix_from_branch(fun, args[1], read_block, read_idx,
                                           base, lane, shape, values, types)
            false_side = suffix_from_branch(fun, args[2], read_block, read_idx,
                                            base, lane, shape, values, types)
            t, f = true_side["read_can_be_reached"], false_side["read_can_be_reached"]
            if not t and not f:
                continue
            gate = ("both_successors_may_reach_read" if t and f else
                    "only_true_successor_may_reach_read" if t else
                    "only_false_successor_may_reach_read")
            branches.append({
                "predicate": "OpINotEqual",
                "inputs": [operand_info(x, values, types) for x in operands],
                "read_gate": gate,
                "true_successor": true_side,
                "false_successor": false_side,
                "suffix_last_writer_sets_differ":
                    (true_side["possible_last_writes_since_branch"] !=
                     false_side["possible_last_writes_since_branch"]) if t and f else None,
                "branch_truth_proven": False,
            })
    return {
        "status": "bounded_original_inequality_sources",
        "site": 1, "role": "butterfly", "coordinate": "y",
        "physical_lane_outside_xy": lane >= 2,
        "inequality_branches_relevant_to_read": len(branches),
        "anonymous_branches": branches,
        "original_ids_and_literal_values_exported": False,
        "dynamic_truth_proven": False,
        "numeric_parity_proven": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private SPIR-V object outside bounded size")
        d = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                           capture_output=True, text=True, timeout=20, check=True)
        report = analyze(d.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private FFT inequality analysis failed\n")
    print("RAFT_T1_FFT_Y_INEQUAL_OPERANDS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
