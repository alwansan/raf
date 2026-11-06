"""Bounded source-private top OpPhi incoming evidence for FFT slot0 site2 Y.

Input is HLSL50→glslang SPIR-V assembled privately from authenticated original
DXBC. CFG edges validate predecessor shape, not runtime branch satisfiability.
Never export original identifiers, shader literals, raw HLSL, or GPU pixels.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import read_module, image_role, value_shape
from scripts.t1_fft_spirv_read_provenance import lane_input
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_hlsl_phi_input_origins import _pred_descriptor
from scripts.t1_fft_hlsl_nested_phi_lineage import _cfg_can_reach
from scripts.t1_fft_site1_x_writer_lineage import safe_op, trace_component

MOVES = {
    "OpBitcast", "OpCopyObject", "OpVectorShuffle",
    "OpCompositeConstruct", "OpCompositeExtract", "OpCompositeInsert",
}
ROLES = ["source", "butterfly", "butterfly"]
MAX_STEPS = 16
MAX_INCOMING = 12

def top_phi(root, values, types):
    current, lane = root, 1
    seen = set()
    for _ in range(MAX_STEPS):
        if (current, lane) in seen:
            return None, None, "cycle"
        seen.add((current, lane))
        kind, width = value_shape(current, values, types)
        if kind not in ("float32", "sint32", "uint32") or not 0 <= lane < width:
            return None, None, "unsupported_type_or_lane"
        op, _, operands = values.get(current, ("", None, []))
        if op == "OpPhi":
            return current, lane, "phi"
        if op not in MOVES:
            return None, None, "non_phi_boundary"
        previous = lane_input(op, operands, lane, width, values, types)
        if previous is None:
            return None, None, "unresolved_component_routing"
        current, lane = previous
    return None, None, "depth_limit"

def analyze(disassembly, *, require_original=True):
    types, values, decorations, _, fetches = read_module(disassembly)
    if len(fetches) != 3 or (
            require_original and [image_role(i, values, decorations)
                                  for i, _ in fetches] != ROLES):
        raise ValueError("Translated FFT original descriptor role/source identity mismatch")
    root, lane, boundary = top_phi(fetches[2][1], values, types)
    if boundary != "phi":
        return {
            "status": "translated_site2_y_no_verifiable_phi",
            "source_boundary": boundary, "site": 2, "axis": "y",
            "private_identifiers_exported": False,
            "actual_branch_or_numeric_parity_proven": False,
        }
    kind, width = value_shape(root, values, types)
    if kind != "float32" or not 0 <= lane < width or width not in (1, 2, 3, 4):
        raise ValueError("Unexpected translated Y Phi type")
    op, _, args = values[root]
    if op != "OpPhi" or len(args) < 4 or len(args) % 2 or len(args)//2 > MAX_INCOMING:
        raise ValueError("Malformed or unbounded translated Phi")
    funs = parse_functions(disassembly)
    owners = [(fun, block) for fun in funs for block, seq in fun["blocks"].items()
              if any(rid == root and opcode == "OpPhi" for opcode, rid, _ in seq)]
    if len(owners) != 1:
        raise ValueError("No unique original-derived Phi owner CFG")
    fun, phi_block = owners[0]
    seen_preds = set()
    incoming = []
    for value, predecessor in zip(args[::2], args[1::2]):
        if predecessor in seen_preds:
            raise ValueError("Repeated Phi incoming predecessor")
        seen_preds.add(predecessor)
        if value_shape(value, values, types) != (kind, width):
            raise ValueError("Phi input numeric vector/scalar type mismatch")
        cfg = _pred_descriptor(fun, predecessor, phi_block, values)
        writer = values.get(value, ("", None, []))[0]
        incoming.append({
            "predecessor": cfg,
            "predecessor_in_structural_cfg_cycle":
                _cfg_can_reach(fun, phi_block, predecessor),
            "immediate_value_opcode": safe_op(writer),
            "typed_input_component": trace_component(value, lane, values, types),
        })
    return {
        "status": "verified_translated_site2_y_phi_incoming_cfg",
        "site": 2, "role": "butterfly", "axis": "y",
        "phi_value_kind": kind + ("_scalar" if width == 1 else "_vector"),
        "selected_phi_lane": "x" if lane == 0 else "y" if lane == 1 else "other",
        "incoming_count": len(incoming),
        "incoming": incoming,
        "private_identifiers_exported": False,
        "actual_branch_truth_proven": False,
        "original_to_translated_numeric_parity_proven": False,
        "unity_gpu_compiler_executed": False,
        "android_water_proven": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        path = args.module
        if path.is_symlink() or not path.is_file() or not 20 <= path.stat().st_size <= 1024*1024:
            raise ValueError("Private SPIR-V input invalid")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(path)],
                             check=True, capture_output=True, text=True, timeout=20)
        result = analyze(dis.stdout)
    except (OSError, ValueError, TypeError, KeyError, IndexError,
            subprocess.SubprocessError):
        p.exit(2, "RAFT_T1_SITE2Y_PHI_INPUTS private_cfg_unverifiable=true\n")
    print("RAFT_T1_SITE2Y_PHI_INPUTS " + json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
