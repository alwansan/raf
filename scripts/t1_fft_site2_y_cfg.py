"""Original FFT slot0 butterfly fetch #2 Y: bounded CFG possible-last-writer audit.

Reports only fixed, source-safe opcode/role labels; does NOT evaluate actual
branch truth, shader numeric equivalence, Unity authored kernel identity,
GPU pixels or Android water.
"""
import argparse
import json
from pathlib import Path
import subprocess
from scripts.t1_fft_local_store_writers import image_role, read_module
from scripts.t1_fft_spirv_lane_alias_effect import load_physical_lane, local_vector_shape
from scripts.t1_fft_spirv_read_provenance import coordinate_lane
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_site1_y_branch_paths import path_witness

ROLES = ("source", "butterfly", "butterfly")
SITE = 2

def analyze(text, *, require_original=True):
    types, values, dec, _, fetches = read_module(text)
    if len(fetches) != 3:
        raise ValueError("Expected exactly three original FFT fetches")
    roles = tuple(image_role(im, values, dec) for im, _ in fetches)
    if require_original and roles != ROLES:
        raise ValueError("Original FFT descriptor identity changed")
    coord = fetches[SITE][1]
    lane = coordinate_lane(coord, 1, values, types, 12)
    load, physical, boundary = load_physical_lane(coord, 1, values, types)
    result = {
        "status": "bounded_original_fft_third_butterfly_y",
        "site": SITE, "role": roles[SITE], "coordinate_axis": "y",
        "value_origin_boundary": boundary,
        "coordinate_lane_structure": lane,
        "original_private_ids_exported": False,
        "original_authored_unity_kernel_mapping_proven": False,
        "actual_invocation_branch_truth_proven": False,
        "integer_numeric_semantics_proven": False,
        "unity_vulkan_numeric_parity_proven": False,
        "android_water_proven": False,
    }
    if load is None:
        return {**result, "last_writer_evidence_available": False,
                "physical_lane_outside_xy": None, "full_execution_path_proven": False}
    ptr = values[load][2][0]
    shape = local_vector_shape(ptr, values, types)
    if shape is None or physical is None or not 0 <= physical < shape["width"]:
        return {**result, "value_origin_boundary": "unsupported_local_vector",
                "last_writer_evidence_available": False,
                "physical_lane_outside_xy": None, "full_execution_path_proven": False}
    funcs = parse_functions(text)
    owners = [f for f in funcs if any(
        rid == load for seq in f["blocks"].values() for _, rid, _ in seq)]
    if len(owners) != 1:
        raise ValueError("Third fetch load has no unique owning CFG")
    may = path_witness(owners[0], load, physical, ptr, shape, values, types)
    return {**result, "physical_lane_outside_xy": physical >= 2,
            "last_writer_evidence_available": may.get("status") == "bounded_cfg_may_path_witnesses",
            **may}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        src = args.module
        if src.is_symlink() or not src.is_file() or not 20 <= src.stat().st_size <= 1024 * 1024:
            raise ValueError("Private SPIR-V source outside safe bounds")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(src)],
                             capture_output=True, text=True, timeout=20, check=True)
        result = analyze(dis.stdout)
    except (OSError, ValueError, TypeError, KeyError, IndexError, subprocess.SubprocessError):
        parser.exit(2, "RAFT_T1_SITE2Y_CFG original_input_unverified=true\n")
    print("RAFT_T1_SITE2Y_CFG " + json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
