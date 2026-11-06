"""Bounded, privacy-safe nested Phi provenance for FFT butterfly1 coordinate X.

This diagnostic parses a private SHA-pinned, original-derived HLSL SPIR-V in the
isolated runner. It explores Phi input CFG edges and one selected vector lane.
All returned source names are fixed opcode/type categories: no private IDs,
literal indexes, shader constants, original bytes or invocation pixels.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import image_role, read_module, value_shape
from scripts.t1_fft_spirv_read_provenance import lane_input
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_hlsl_phi_input_origins import (
    _find_phi_on_x_lane, _pred_descriptor,
)
from scripts.t1_fft_site1_x_writer_lineage import safe_op, trace_component

MAX_DEPTH = 24
MAX_EXPANSIONS = 256
MAX_INCOMING = 12
MAX_PHI_NODES = 24
MAX_FETCHES = 16
CONTINUE = {
    "OpCompositeConstruct", "OpCompositeExtract", "OpCompositeInsert",
    "OpVectorShuffle", "OpCopyObject", "OpBitcast",
}
KINDS = {"float32", "sint32", "uint32"}


def _component_name(lane):
    return "x" if lane == 0 else "y" if lane == 1 else "other"


def _type(value, values, types):
    kind, width = value_shape(value, values, types)
    if kind not in KINDS or width not in (1, 2, 3, 4):
        raise ValueError("Unsupported selected component numeric type")
    return kind, width


def analyze(text, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    funs = parse_functions(text)
    if len(fetches) < 2 or len(fetches) > MAX_FETCHES:
        raise ValueError("Unexpected FFT private fetch census")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Original-derived HLSL FFT role identity mismatch")
    root, lane, status = _find_phi_on_x_lane(fetches[1][1], values, types)
    if status != "phi":
        return {"status": status, "private_values_exported": False,
                "selected_runtime_predecessor_proven": False}
    owner_by_result = {}
    for fun in funs:
        for block, instructions in fun["blocks"].items():
            for op, rid, _ in instructions:
                if op == "OpPhi" and rid is not None:
                    if rid in owner_by_result:
                        raise ValueError("Phi has multiple CFG definitions")
                    owner_by_result[rid] = (fun, block)

    budget = {"states": 0, "phis": 0, "cycles": 0}
    def visit(value, index, path, depth):
        budget["states"] += 1
        if depth > MAX_DEPTH or budget["states"] > MAX_EXPANSIONS:
            return {"status": "bounded_unknown", "reason": "depth_or_state_limit"}
        kind, width = _type(value, values, types)
        if not 0 <= index < width:
            return {"status": "bounded_unknown", "reason": "invalid_selected_lane"}
        op, _, args = values.get(value, ("unknown", None, []))
        if op == "OpPhi":
            if (value, index) in path:
                budget["cycles"] += 1
                return {"status": "loop_carried_or_cyclic_phi", "type": kind,
                        "selected_component": _component_name(index)}
            budget["phis"] += 1
            if budget["phis"] > MAX_PHI_NODES:
                return {"status": "bounded_unknown", "reason": "phi_budget"}
            if len(args) < 4 or len(args) % 2 != 0 or len(args)//2 > MAX_INCOMING:
                raise ValueError("Malformed or excessive Phi predecessor pairs")
            owner = owner_by_result.get(value)
            if owner is None:
                raise ValueError("Phi CFG owner not found")
            fun, phi_block = owner
            incoming = []
            for operand, predecessor in zip(args[::2], args[1::2]):
                if _type(operand, values, types) != (kind, width):
                    raise ValueError("Phi incoming vector shape mismatch")
                pred = _pred_descriptor(fun, predecessor, phi_block, values)
                incoming.append({
                    "predecessor": pred,
                    "source": visit(operand, index, path | {(value, index)}, depth+1)
                })
            return {"status": "phi_merge",
                    "value_kind": kind + ("_scalar" if width == 1 else "_vector"),
                    "selected_component": _component_name(index),
                    "incoming_count": len(incoming),
                    "incoming": incoming}
        if op in CONTINUE:
            nxt = lane_input(op, args, index, width, values, types)
            if nxt is None:
                return {"status": "bounded_unknown", "reason": "unsupported_component_selector",
                        "opcode": safe_op(op)}
            result = visit(nxt[0], nxt[1], path, depth+1)
            # Do not disclose constant indexes, Phi result IDs or bit values.
            return {"status": "component_routing", "opcode": safe_op(op),
                    "source": result}
        # Any arithmetic/unknown/memory/constant boundary remains an explicit
        # unproven source category; reuse the established privacy-safe leaf.
        terminal = trace_component(value, index, values, types)
        return {"status": "typed_boundary", "immediate_opcode": safe_op(op),
                "detail": terminal}

    kind, width = _type(root, values, types)
    result = visit(root, lane, frozenset(), 0)
    return {
        "status": "bounded_nested_phi_component_provenance",
        "site": 1, "coordinate": "x", "role": "butterfly",
        "top_phi_kind": kind + ("_scalar" if width == 1 else "_vector"),
        "top_selected_component": _component_name(lane),
        "phi_expansions": budget["phis"], "cycle_boundaries": budget["cycles"],
        "chain": result, "private_values_exported": False,
        "selected_runtime_predecessor_proven": False,
        "actual_original_vs_unity_numeric_parity_proven": False,
        "adreno_water_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024*1024:
            raise ValueError("Private FFT translated module size out of bound")
        d = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                           capture_output=True, text=True, check=True, timeout=20)
        result = analyze(d.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        # Never dump raw error strings or original shader data.
        parser.exit(2, "Private FFT nested Phi classification failed\n")
    print("RAFT_T1_FFT_HLSL_NESTED_PHI_X " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
