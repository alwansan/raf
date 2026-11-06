"""Bounded, private-only taxonomy for keyed original FFT vs Unity candidate reads.

Requires the existing SHA256-bound same-input/dispatch paired manifest and
independent fixed-size trace buffers. Candidate Unity role is a DECLARATION,
not proof of Unity compilation, authored runtime kernel mapping or device pixels.
Never print raw coordinates, samples, original binary or private fingerprints.
"""
import argparse
import json
from pathlib import Path

from scripts.t1_fft_invocation_pair_gate import (
    _read_manifest, _read_trace, analyze as verify_pair,
)
from scripts.t1_fft_trace_compare import decode_invocations

SITE_COUNT = 3
AXES = ("x", "y", "mip")


def _subnormal(word: int) -> bool:
    return (word & 0x7f800000) == 0 and (word & 0x007fffff) != 0


def _zero(word: int) -> bool:
    # Ignore sign of zero for the FTZ hypothesis only; preserve bitwise
    # identity checks for all other differences.
    return (word & 0x7fffffff) == 0


def classify(manifest, original, unity) -> dict:
    original, unity = Path(original), Path(unity)
    if original.is_symlink() or unity.is_symlink() or Path(manifest).is_symlink():
        raise ValueError("Private evidence symlink rejected")
    # Reuse exact SHA and coverage, same-origin input & dispatch checks.
    provenance = verify_pair(manifest, original, unity)
    metadata = _read_manifest(manifest)
    if metadata["candidate"]["role"] != "unity_compute_spirv":
        raise ValueError("Unity-stage producer declaration required")
    left, right = [decode_invocations(_read_trace(p)) for p in (original, unity)]
    sites = []
    for i in range(SITE_COUNT):
        a, b = left[i], right[i]
        shared = a.keys() & b.keys()
        counts = {
            "site": i,
            "paired_invocations": len(shared),
            "reference_only_invocations": len(a.keys() - b.keys()),
            "unity_only_invocations": len(b.keys() - a.keys()),
            "coordinate_mismatching_invocations": 0,
            "coordinate_zero_collapse_by_axis": {axis: 0 for axis in AXES},
            "other_coordinate_drift_by_axis": {axis: 0 for axis in AXES},
            "same_coordinate_bitwise_value_mismatches": 0,
            "same_coordinate_subnormal_to_zero_channels": 0,
            "same_coordinate_other_value_mismatch_channels": 0,
            "value_comparison_skipped_after_coordinate_drift": 0,
        }
        for key in shared:
            ca, va = a[key]
            cb, vb = b[key]
            if ca != cb:
                counts["coordinate_mismatching_invocations"] += 1
                counts["value_comparison_skipped_after_coordinate_drift"] += 1
                for axis, before, after in zip(AXES, ca, cb):
                    if before != after:
                        label = ("coordinate_zero_collapse_by_axis" if
                                 before != 0 and after == 0 else
                                 "other_coordinate_drift_by_axis")
                        counts[label][axis] += 1
                continue
            for before, after in zip(va, vb):
                if before == after:
                    continue
                counts["same_coordinate_bitwise_value_mismatches"] += 1
                if _subnormal(before) and _zero(after):
                    counts["same_coordinate_subnormal_to_zero_channels"] += 1
                else:
                    counts["same_coordinate_other_value_mismatch_channels"] += 1
        sites.append(counts)
    return {
        "status": "private_paired_original_vs_claimed_unity_trace_taxonomy",
        "signed_unity_producer_attestation": False,
        "unity_runtime_shader_or_backend_verified_by_this_tool": False,
        "pair_trace_digests_and_same_declared_input_dispatch_verified": True,
        "independent_private_traces_verified": provenance["independent_trace_files_verified"],
        "actual_original_asset_authenticity_verified_by_this_tool": False,
        "synthetic_or_real_gpu_execution_independently_verified": False,
        "diagnostics": sites,
        "float32_FTZ_causality_proven": False,
        "unity_shader_binding_causality_proven": False,
        "android_water_or_pixels_proven": False,
        "private_coordinates_values_hashes_or_shader_code_exported": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--unity", required=True, type=Path)
    args = p.parse_args()
    try:
        report = classify(args.manifest, args.original, args.unity)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_FTZ_TRACE invalid_private_paired_evidence=true\n")
    print("RAFT_T1_FTZ_TRACE " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
