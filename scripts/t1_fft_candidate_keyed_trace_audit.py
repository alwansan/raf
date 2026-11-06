"""Validate a private HLSL-roundtrip invocation-keyed FFT GPU trace.

No raw coordinates, invocation IDs, value bits, trace bytes, binary digest or
shader source may leave the private runner. This is candidate-only evidence:
it does NOT compare original SPIR-V against translated HLSL or Unity runtime.
"""
import argparse
import json
from pathlib import Path

from scripts.t1_fft_trace_compare import INVOCATION_SIZE, decode_invocations


def analyze(data):
    sites = decode_invocations(data)
    counts = [len(site) for site in sites]
    if any(n <= 0 for n in counts):
        raise ValueError("Empty candidate trace site")
    return {
        "status": "candidate_only_invocation_keyed_trace",
        "source_stage": "original_derived_hlsl_roundtrip",
        "trace_layout": "5u32_dispatch_identity_3i32_coords_4u32_values",
        "records_by_site": counts,
        "unique_invocation_keys_verified": True,
        "original_spirv_keyed_capture_present": False,
        "independent_pair_comparison_performed": False,
        "vulkan_vs_unity_numeric_parity_proven": False,
        "android_water_proven": False,
    }


def read_and_analyze(path):
    with Path(path).open("rb") as stream:
        buffer = stream.read(INVOCATION_SIZE + 1)
    if len(buffer) != INVOCATION_SIZE:
        raise ValueError("Invalid candidate capture bytes")
    return analyze(buffer)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_candidate_trace", type=Path)
    args = parser.parse_args()
    try:
        report = read_and_analyze(args.private_candidate_trace)
    except (OSError, ValueError):
        parser.exit(2, "Invalid private invocation-keyed candidate trace\n")
    print("RAFT_T1_HLSL_KEYED_CANDIDATE_TRACE " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
