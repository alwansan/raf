"""Source-private FFT butterfly1 X reaching-writer vector component lineage.

Bounded, source-authenticated static CFG/SSA audit. Never prints original
SPIR-V identifiers, shader literals, private code, or pixel values.
A component's producer chain is NOT original/Unity numeric parity proof.
"""
import argparse
from collections import Counter, deque
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import (
    image_role, lane_predecessor, read_module, value_shape,
)
from scripts.t1_fft_spirv_reaching_stores import aliases, parse_functions
from scripts.t1_fft_spirv_lane_alias_effect import (
    load_physical_lane, local_vector_shape, pointer_effect,
)

MAX_STATES = 30000
MAX_TRACE_DEPTH = 18
MAX_WRITERS = 256
MAX_FETCHES = 16

TRANSPARENT = {
    "OpVectorShuffle", "OpCompositeConstruct", "OpCompositeExtract",
    "OpCompositeInsert", "OpCopyObject", "OpBitcast",
}
LEAF_OPS = {
    "OpConstant": "constant_boundary",
    "OpConstantComposite": "constant_boundary",
    "OpConstantNull": "constant_boundary",
    "OpSpecConstant": "specialization_constant_boundary",
    "OpUndef": "undefined_boundary",
    "OpLoad": "memory_load_boundary",
    "OpImageFetch": "texture_fetch_boundary",
    "OpImageSampleImplicitLod": "texture_sample_boundary",
    "OpImageSampleExplicitLod": "texture_sample_boundary",
    "OpFunctionParameter": "parameter_boundary",
    "OpPhi": "conditional_phi_boundary",
    "OpSelect": "conditional_select_boundary",
}
ARITHMETIC = {
    "OpFAdd", "OpFSub", "OpFMul", "OpFDiv", "OpFNegate", "OpIAdd",
    "OpISub", "OpIMul", "OpShiftLeftLogical", "OpShiftRightArithmetic",
    "OpShiftRightLogical", "OpBitwiseAnd", "OpBitwiseOr",
    "OpBitwiseXor", "OpConvertSToF", "OpConvertUToF", "OpConvertFToS",
    "OpConvertFToU", "OpSConvert", "OpUConvert",
}


def kind_label(value, values, types):
    kind, width = value_shape(value, values, types)
    if kind not in ("float32", "sint32", "uint32") or not 1 <= width <= 4:
        return "unresolved"
    return kind + ("_scalar" if width == 1 else "_vector")


def safe_op(op):
    if op in TRANSPARENT or op in LEAF_OPS or op in ARITHMETIC:
        return op
    return "other_opcode"


def load_pointer_storage(pointer, values, types):
    op, ty, operands = values.get(pointer, ("", None, []))
    if op == "OpVariable" and operands:
        storage = operands[0]
    elif op == "OpAccessChain" and operands:
        # One-level derivation has unknown subscript identity; retain only
        # the pointer storage class, not its index or offset.
        op, ty, operands = values.get(operands[0], ("", None, []))
        storage = operands[0] if op == "OpVariable" and operands else None
    else:
        storage = None
    return storage if storage in (
        "Function", "Private", "Input", "Output", "Uniform",
        "UniformConstant", "Workgroup", "StorageBuffer", "PushConstant"
    ) else "unknown"


def trace_component(value, lane, values, types):
    visited = set()
    steps = []
    casts = []
    selected_inputs = []
    for _ in range(MAX_TRACE_DEPTH):
        if (value, lane) in visited:
            return {"status": "cycle", "ssa_ops": steps, "cast_kinds": casts,
                    "shuffle_inputs": selected_inputs}
        visited.add((value, lane))
        kind, width = value_shape(value, values, types)
        if not 0 <= lane < width:
            return {"status": "type_or_lane_unresolved", "ssa_ops": steps,
                    "cast_kinds": casts, "shuffle_inputs": selected_inputs}
        op, _, args = values.get(value, ("", None, []))
        steps.append(safe_op(op))
        if op == "OpBitcast" and len(args) == 1:
            source_kind, source_width = value_shape(args[0], values, types)
            if source_width == width and source_kind in ("float32", "sint32", "uint32"):
                casts.append(source_kind + "_bits_to_" + kind)
            else:
                casts.append("unresolved_bitcast")
        if op == "OpVectorShuffle" and len(args) >= 3:
            predecessor = lane_predecessor(op, args, lane, width, values, types)
            if predecessor is not None:
                # Classify input index without exporting private component numbers.
                first_width = value_shape(args[0], values, types)[1]
                try:
                    index = int(args[2 + lane])
                except (IndexError, ValueError):
                    index = -1
                selected_inputs.append("first" if 0 <= index < first_width else "second")
        if op == "OpLoad":
            return {"status": LEAF_OPS[op],
                    "leaf_storage_class": load_pointer_storage(args[0], values, types)
                        if args else "unknown",
                    "leaf_numeric_kind": kind_label(value, values, types),
                    "ssa_ops": steps, "cast_kinds": casts,
                    "shuffle_inputs": selected_inputs}
        if op in LEAF_OPS:
            return {"status": LEAF_OPS[op],
                    "leaf_numeric_kind": kind_label(value, values, types),
                    "ssa_ops": steps, "cast_kinds": casts,
                    "shuffle_inputs": selected_inputs}
        if op in ARITHMETIC:
            return {"status": "arithmetic_boundary",
                    "arithmetic_opcode": op,
                    "leaf_numeric_kind": kind_label(value, values, types),
                    "ssa_ops": steps, "cast_kinds": casts,
                    "shuffle_inputs": selected_inputs}
        if op not in TRANSPARENT:
            return {"status": "unsupported_opcode",
                    "ssa_ops": steps, "cast_kinds": casts,
                    "shuffle_inputs": selected_inputs}
        previous = lane_predecessor(op, args, lane, width, values, types)
        if previous is None:
            return {"status": "unknown_component_selection", "ssa_ops": steps,
                    "cast_kinds": casts, "shuffle_inputs": selected_inputs}
        value, lane = previous
    return {"status": "depth_limit", "ssa_ops": steps,
            "cast_kinds": casts, "shuffle_inputs": selected_inputs}


def last_writer_candidates(fun, read_id, base, physical_lane, shape, values, types):
    locations = [(block, index) for block, ins in fun["blocks"].items()
                 for index, (_, rid, _) in enumerate(ins) if rid == read_id]
    if len(locations) != 1:
        raise ValueError("Ambiguous original FFT load position")
    target_block, target_index = locations[0]
    writers = {}
    for block, seq in fun["blocks"].items():
        if not seq or seq[-1][0] not in (
            "OpBranch", "OpBranchConditional", "OpSwitch", "OpReturn",
            "OpReturnValue", "OpKill", "OpUnreachable", "OpTerminateInvocation"
        ):
            raise ValueError("Malformed SPIR-V basic block")
        for index, (op, _, args) in enumerate(seq):
            if index < len(seq) - 1 and op in (
                "OpBranch", "OpBranchConditional", "OpSwitch", "OpReturn",
                "OpReturnValue", "OpKill", "OpUnreachable", "OpTerminateInvocation"
            ):
                raise ValueError("Nonfinal SPIR-V terminator")
            if op == "OpStore" and len(args) >= 2 and pointer_effect(
                args[0], base, physical_lane, shape, values, types
            ) in ("whole", "same_lane"):
                if len(writers) >= MAX_WRITERS:
                    raise ValueError("Source writer bound exceeded")
                writers[(block, index)] = (len(writers), args[1],
                                           pointer_effect(args[0], base, physical_lane, shape, values, types))
    # Bounded path-state enumeration propagates last exact instruction; unlike
    # merged static store counts, downstream overwritten writers are excluded.
    initial = (fun["entry"], 0, -1, False, False)
    queue = deque([initial])
    seen = {initial}
    at_read = set()
    while queue:
        if len(seen) > MAX_STATES:
            raise ValueError("Source branch path state bound exceeded")
        block, index, last, unknown_write, pointer_escape = queue.popleft()
        if (block, index) == (target_block, target_index):
            at_read.add((last, unknown_write, pointer_escape))
            continue
        seq = fun["blocks"][block]
        if index >= len(seq):
            raise ValueError("Missing instruction terminator")
        op, _, args = seq[index]
        if op == "OpStore" and len(args) >= 2:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect in ("whole", "same_lane"):
                last = writers[(block, index)][0]
            elif effect == "unknown":
                unknown_write = True
            if args[1] == base or aliases(args[1], base, values):
                pointer_escape = True
        elif op in ("OpCopyMemory", "OpCopyMemorySized") and args:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect not in ("other_lane", "unrelated"):
                unknown_write = True
        elif op == "OpFunctionCall" and any(
            aliases(x, base, values) for x in args[1:]
        ):
            unknown_write = True
        elif op.startswith("OpAtomic") and args:
            effect = pointer_effect(args[0], base, physical_lane, shape, values, types)
            if effect not in ("other_lane", "unrelated"):
                unknown_write = True
        if op in ("OpBranch", "OpBranchConditional", "OpSwitch"):
            next_positions = [(to, 0) for to in fun["edges"][block]]
        elif op in ("OpReturn", "OpReturnValue", "OpKill",
                    "OpUnreachable", "OpTerminateInvocation"):
            next_positions = []
        else:
            next_positions = [(block, index + 1)]
        for to, loc in next_positions:
            state = (to, loc, last, unknown_write, pointer_escape)
            if state not in seen:
                seen.add(state)
                queue.append(state)
    if not at_read:
        return {"status": "unreachable_load", "complete_proof": False}
    indices = {last for last, _, _ in at_read if last >= 0}
    summaries = []
    for index, value, form in writers.values():
        if index not in indices:
            continue
        entry = trace_component(value, physical_lane if form == "whole" else 0,
                                values, types)
        entry["write_form"] = form
        entry["immediate_store_value_opcode"] = safe_op(
            values.get(value, ("", None, []))[0])
        summaries.append(entry)
    return {
        "status": "bounded_last_write_component_lineage",
        "static_affecting_store_count": len(writers),
        "reachable_last_writer_count": len(indices),
        "possible_last_writer_component_sources": summaries,
        "possible_uninitialized_path": any(x[0] < 0 for x in at_read),
        "possible_unknown_alias_write": any(x[1] for x in at_read),
        "possible_pointer_escape": any(x[2] for x in at_read),
        "complete_proof": False,
        "numeric_parity_proven": False,
    }


def analyze(text, *, original_layout=False):
    types, values, decor, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > MAX_FETCHES:
        raise ValueError("Unexpected private FFT fetch count")
    roles = [image_role(image, values, decor) for image, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Original FFT descriptor order mismatch")
    if len(fetches) < 2:
        raise ValueError("Original first butterfly missing")
    load, physical_lane, boundary = load_physical_lane(fetches[1][1], 0, values, types)
    if load is None:
        return {"status": boundary, "original_numeric_semantics_proven": False}
    base = values[load][2][0]
    shape = local_vector_shape(base, values, types)
    if shape is None or physical_lane >= shape["width"]:
        return {"status": "unsupported_vector_pointer",
                "original_numeric_semantics_proven": False}
    owners = [f for f in functions if any(
        rid == load for ops in f["blocks"].values() for _, rid, _ in ops)]
    if len(owners) != 1:
        raise ValueError("Original load Function ambiguity")
    result = last_writer_candidates(
        owners[0], load, base, physical_lane, shape, values, types)
    return {
        "site": 1, "role": "butterfly", "coordinate": "x",
        "physical_source_lane": "x" if physical_lane == 0 else
            "y" if physical_lane == 1 else "other",
        "original_ids_and_constants_exported": False,
        "original_numeric_semantics_proven": False,
        **result,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("SPIR-V private source size out of bound")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                             capture_output=True, text=True, timeout=20, check=True)
        print("RAFT_T1_FFT_BUTTERFLY_X_WRITER_LINEAGE " +
              json.dumps(analyze(dis.stdout, original_layout=True), sort_keys=True))
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private butterfly X producer lineage failed\n")


if __name__ == "__main__":
    main()
