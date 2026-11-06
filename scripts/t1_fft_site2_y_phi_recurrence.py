"""Bounded, source-safe selected-component SSA recurrence for FFT Site2/Y Phi.

CFG backedge != selected-lane data dependence. Unknown memory/unsupported
operators != proven independence. Never emit original private SSA IDs, literals,
shader code or GPU pixels; only fixed categories and structural booleans.
"""
import argparse
import json
from pathlib import Path
import subprocess
from scripts.t1_fft_local_store_writers import read_module, image_role, value_shape
from scripts.t1_fft_spirv_read_provenance import lane_input
from scripts.t1_fft_site2_y_phi_inputs import analyze as checked_phi, top_phi
from scripts.t1_fft_hlsl_phi_input_origins import _pred_descriptor
from scripts.t1_fft_spirv_reaching_stores import parse_functions

TRANSPARENT = {"OpBitcast", "OpCopyObject", "OpCompositeConstruct",
               "OpCompositeExtract", "OpCompositeInsert", "OpVectorShuffle"}
BINARY = {"OpIAdd", "OpISub", "OpIMul", "OpFAdd", "OpFSub", "OpFMul",
          "OpBitwiseAnd", "OpBitwiseOr", "OpBitwiseXor", "OpShiftLeftLogical",
          "OpShiftRightLogical", "OpShiftRightArithmetic", "OpUDiv", "OpSDiv"}
UNARY = {"OpSConvert", "OpUConvert", "OpConvertFToS",
         "OpConvertFToU", "OpConvertSToF", "OpConvertUToF", "OpFNegate"}
CONSTANTS = {"OpConstant", "OpConstantNull", "OpConstantComposite",
             "OpConstantTrue", "OpConstantFalse", "OpSpecConstant"}
MAX_DEPTH, MAX_STATES = 32, 512


def dependency(root, target_lane, candidate, lane, values, types, owners):
    budget = [0]
    uncertainty = set()

    def step(value, axis, path, depth):
        budget[0] += 1
        if budget[0] > MAX_STATES or depth > MAX_DEPTH:
            uncertainty.add("budget")
            return (False, False, True)
        kind, width = value_shape(value, values, types)
        if kind not in ("float32", "sint32", "uint32") or not 0 <= axis < width:
            uncertainty.add("shape")
            return (False, False, True)
        if value == root:
            return (axis == target_lane, axis != target_lane, False)
        if (value, axis) in path:
            uncertainty.add("other_cycle")
            return (False, False, True)
        op, _, args = values.get(value, ("", None, []))
        if op in CONSTANTS:
            return (False, False, False)
        if op in TRANSPARENT:
            prev = lane_input(op, args, axis, width, values, types)
            if prev is None:
                uncertainty.add("routing")
                return (False, False, True)
            children = [prev]
        elif op in BINARY:
            if len(args) != 2 or any(value_shape(v, values, types) != (kind, width) for v in args):
                uncertainty.add("arithmetic_shape")
                return (False, False, True)
            children = [(v, axis) for v in args]
        elif op in UNARY:
            if len(args) != 1 or value_shape(args[0], values, types)[1] != width:
                uncertainty.add("conversion_shape")
                return (False, False, True)
            children = [(args[0], axis)]
        elif op == "OpSelect":
            if len(args) != 3 or any(value_shape(v, values, types) != (kind, width) for v in args[1:]):
                uncertainty.add("select_shape")
                return (False, False, True)
            children = [(v, axis) for v in args[1:]]
        elif op == "OpPhi":
            owner = owners.get(value)
            if owner is None or not 4 <= len(args) <= 24 or len(args) % 2:
                uncertainty.add("nested_phi")
                return (False, False, True)
            fun, block = owner
            children = []
            for item, pred in zip(args[::2], args[1::2]):
                if value_shape(item, values, types) != (kind, width):
                    uncertainty.add("nested_phi_shape")
                    return (False, False, True)
                _pred_descriptor(fun, pred, block, values)
                children.append((item, axis))
        else:
            uncertainty.add("load" if op == "OpLoad" else "unknown_opcode")
            return (False, False, True)
        results = [step(v, l, path | {(value, axis)}, depth + 1) for v, l in children]
        return tuple(any(result[i] for result in results) for i in range(3))

    same, cross, unknown = step(candidate, lane, frozenset(), 0)
    return {
        "same_selected_phi_component_data_edge_possible": same,
        "different_phi_component_data_edge_possible": cross,
        "unknown_dataflow_possible": unknown,
        "recurrence_class": ("selected_component_cycle" if same else
                             "unresolved" if unknown else
                             "cross_component_only" if cross else
                             "no_direct_selected_component_cycle_in_supported_SSA"),
        "states_visited": budget[0],
        "uncertainty_categories": sorted(uncertainty),
        "runtime_predecessor_or_numeric_causality_proven": False,
    }


def analyze(disassembly, *, require_original=True):
    checked = checked_phi(disassembly, require_original=require_original)
    if checked.get("status") != "verified_translated_site2_y_phi_incoming_cfg":
        raise ValueError("Third butterfly Y Phi predecessor checks unavailable")
    types, values, decorations, _, fetches = read_module(disassembly)
    if len(fetches) != 3 or (require_original and [
            image_role(image, values, decorations) for image, _ in fetches
            ] != ["source", "butterfly", "butterfly"]):
        raise ValueError("Unrecognized original FFT resource role order")
    root, lane, status = top_phi(fetches[2][1], values, types)
    if status != "phi" or root is None:
        raise ValueError("Third read Phi not found")
    op, _, args = values[root]
    if op != "OpPhi" or len(args)//2 != checked["incoming_count"]:
        raise ValueError("Top Phi changed during analysis")
    owners = {}
    for fun in parse_functions(disassembly):
        for block, instructions in fun["blocks"].items():
            for opcode, result, _ in instructions:
                if opcode == "OpPhi" and result is not None:
                    if result in owners:
                        raise ValueError("Duplicate Phi result")
                    owners[result] = (fun, block)
    if root not in owners:
        raise ValueError("Phi has no unambiguous CFG owner")
    rows = []
    for i, (value, pred) in enumerate(zip(args[::2], args[1::2])):
        _pred_descriptor(owners[root][0], pred, owners[root][1], values)
        row = dependency(root, lane, value, lane, values, types, owners)
        row["predecessor_on_structural_backedge"] = checked["incoming"][i][
            "predecessor_in_structural_cfg_cycle"]
        rows.append(row)
    return {
        "status": "original_derived_third_butterfly_Y_Phi_component_SSA_audit",
        "site": 2, "coordinate": "y", "role": "butterfly",
        "selected_phi_physical_component": checked["selected_phi_lane"],
        "incoming_count": len(rows), "inputs": rows,
        "CFG_backedge_alone_does_not_prove_data_recurrence": True,
        "selected_runtime_branch_proven": False,
        "original_or_unity_numeric_parity_proven": False,
        "android_water_proven": False,
        "private_shader_SSA_constants_or_pixels_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    a = p.parse_args()
    try:
        f = a.module
        if f.is_symlink() or not f.is_file() or not 20 <= f.stat().st_size <= 1024*1024:
            raise ValueError("Private source module unsafe")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(f)],
                             capture_output=True, text=True, check=True, timeout=20)
        report = analyze(dis.stdout)
    except (OSError, ValueError, TypeError, KeyError, IndexError, subprocess.SubprocessError):
        p.exit(2, "RAFT_T1_SITE2Y_PHI_SSA private_source_unverifiable=true\n")
    print("RAFT_T1_SITE2Y_PHI_SSA " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
