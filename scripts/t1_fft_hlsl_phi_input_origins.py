"""Bounded SHA-pinned FFT translated-HLSL butterfly X Phi input census.

Run only on private compiled SPIR-V from the exact-source isolated workflow.
Reports incoming value opcode/type and CFG predecessor families, NEVER SSA IDs,
literal shader values, source bytes, original pixel results or actual branch truth.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import (
    image_role, read_module, value_shape,
)
from scripts.t1_fft_spirv_read_provenance import lane_input
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_site1_x_writer_lineage import trace_component, safe_op

MAX_STEPS = 12
MAX_PHI_INPUTS = 12
MAX_FETCHES = 16
CONTINUE = {
    "OpBitcast", "OpCopyObject", "OpCompositeConstruct",
    "OpCompositeExtract", "OpCompositeInsert", "OpVectorShuffle",
}
PREDICATE_OPS = {
    "OpINotEqual", "OpIEqual", "OpSLessThan", "OpULessThan",
    "OpSGreaterThan", "OpUGreaterThan", "OpLogicalNot",
    "OpLogicalAnd", "OpLogicalOr", "OpFOrdLessThan",
    "OpFOrdGreaterThan", "OpConstantTrue", "OpConstantFalse",
    "OpLoad", "OpSelect", "OpPhi",
}


def _find_phi_on_x_lane(root, values, types):
    value, lane = root, 0
    seen = set()
    for _ in range(MAX_STEPS):
        if (value, lane) in seen:
            return None, None, "cycle"
        seen.add((value, lane))
        kind, width = value_shape(value, values, types)
        if width < 1 or lane < 0 or lane >= width:
            return None, None, "invalid_lane"
        op, _, args = values.get(value, ("", None, []))
        if op == "OpPhi":
            return value, lane, "phi"
        if op not in CONTINUE:
            return None, None, "other_boundary"
        prev = lane_input(op, args, lane, width, values, types)
        if prev is None:
            return None, None, "unknown_component_selection"
        value, lane = prev
    return None, None, "depth_limit"


def _pred_descriptor(fun, pred, phi_block, values):
    seq = fun["blocks"].get(pred)
    if not seq or phi_block not in fun["edges"].get(pred, ()):
        raise ValueError("Phi predecessor is not a CFG incoming block")
    op, _, args = seq[-1]
    if op == "OpBranch" and len(args) >= 1:
        if args[0] != phi_block:
            raise ValueError("Invalid predecessor branch edge")
        return {"terminator": "OpBranch", "edge": "unconditional",
                "predicate_opcode": "none"}
    if op == "OpBranchConditional" and len(args) >= 3:
        which = ("both" if args[1] == phi_block and args[2] == phi_block
                 else "true" if args[1] == phi_block
                 else "false" if args[2] == phi_block else "none")
        if which == "none":
            raise ValueError("Invalid conditional predecessor edge")
        cond_op = values.get(args[0], ("", None, []))[0]
        return {"terminator": "OpBranchConditional", "edge": which,
                "predicate_opcode": (cond_op if cond_op in PREDICATE_OPS
                                     else "other_predicate")}
    if op == "OpSwitch":
        return {"terminator": "OpSwitch", "edge": "case_or_default",
                "predicate_opcode": "integer_switch"}
    raise ValueError("Unsupported original Phi predecessor terminator")


def analyze(text, *, original_source_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > MAX_FETCHES or len(fetches) < 2:
        raise ValueError("Unexpected original FFT fetch count")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if original_source_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected FFT descriptor source identity")
    result, lane, status = _find_phi_on_x_lane(fetches[1][1], values, types)
    if status != "phi":
        return {"status": status, "site": 1, "coordinate": "x",
                "private_values_exported": False,
                "runtime_branch_truth_proven": False}
    kind, width = value_shape(result, values, types)
    if width != 1 or lane != 0 or kind not in ("float32", "sint32", "uint32"):
        raise ValueError("Unexpected scalar Phi lane type")
    op, _, operands = values[result]
    if op != "OpPhi" or len(operands) < 4 or len(operands) % 2:
        raise ValueError("Malformed Phi incoming value/predecessor list")
    if len(operands) // 2 > MAX_PHI_INPUTS:
        raise ValueError("Phi incoming path bound exceeded")
    owners = [(fun, block) for fun in functions
              for block, instructions in fun["blocks"].items()
              if any(rid == result for _, rid, _ in instructions)]
    if len(owners) != 1:
        raise ValueError("Unresolvable translated Phi Function owner")
    fun, phi_block = owners[0]
    incoming = []
    for source_value, pred in zip(operands[::2], operands[1::2]):
        value_kind, value_width = value_shape(source_value, values, types)
        if (value_kind, value_width) != (kind, width):
            raise ValueError("Incoming Phi value type does not match destination")
        predecessor = _pred_descriptor(fun, pred, phi_block, values)
        upstream = trace_component(source_value, lane, values, types)
        # trace_component emits only restricted op names, type families and
        # symbolic stop causes. No coordinates or original shader ids.
        immediate = values.get(source_value, ("", None, []))[0]
        incoming.append({
            "value_type": value_kind + "_scalar",
            "immediate_producer_opcode": safe_op(immediate),
            "predecessor": predecessor,
            "bounded_component_chain": upstream,
        })
    return {
        "status": "source_safe_phi_incoming_census",
        "site": 1, "role": "butterfly", "coordinate": "x",
        "phi_result_kind": kind + "_scalar",
        "incoming_count": len(incoming),
        "incoming_sources": incoming,
        "private_values_exported": False,
        "runtime_branch_truth_proven": False,
        "original_integer_bitcarrier_parity_proven": False,
        "unity_Adreno_water_proven": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private translated FFT shader size out of bounds")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                             capture_output=True, text=True, check=True, timeout=20)
        report = analyze(dis.stdout, original_source_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private translated FFT Phi input analysis failed\n")
    print("RAFT_T1_FFT_HLSL_BUTTERFLY_X_PHI_INPUTS " +
          json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
