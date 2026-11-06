"""Compute safe bounds on co-occurring FFT read-coordinate zero collapse.

Inputs are aggregate, unsigned GPU job markers checked by the existing T1
original-Vulkan/Unity profile gate. No shader, pixel, runtime-kernel, binary
signature or Android device proof can be inferred independently here.
"""
import argparse
import json
from pathlib import Path

from scripts.t1_fft_real_gpu_variant_delta_gate import RECORDS, _profile, compare

SITE_COUNT = 3


def bounds(changed, x, y):
    """Fréchet intersection bounds, without assuming axis independence."""
    if (any(type(n) is not int for n in (changed, x, y))
            or not (0 <= x <= changed and 0 <= y <= changed)):
        raise ValueError("Impossible private FFT aggregate")
    low, high = max(0, x + y - changed), min(x, y)
    return {
        "x_y_zero_collapse_overlap_min": low,
        "x_y_zero_collapse_overlap_max": high,
        "x_or_y_zero_collapse_union_min": max(x, y),
        "x_or_y_zero_collapse_union_max": min(changed, x + y),
        "overlap_determined_exactly": low == high,
        "all_coordinate_mismatches_include_y_zero_collapse": changed > 0 and y == changed,
        "all_coordinate_mismatches_include_x_zero_collapse": changed > 0 and x == changed,
    }


def analyze_profiles(baseline, variant):
    """Apply set limits to two already source-gated aggregate profiles."""
    results = []
    for profile in (baseline, variant):
        fields = ("coordinate_mismatch_by_site", "zero_collapse_x_by_site", "zero_collapse_y_by_site")
        if (type(profile) is not dict or any(
            type(profile.get(k)) is not list or len(profile[k]) != SITE_COUNT
            for k in fields
        )):
            raise ValueError("Missing three-site FFT aggregate")
        if any(type(c) is not int or c > maximum
               for c, maximum in zip(profile[fields[0]], RECORDS)):
            raise ValueError("FFT coordinate mismatch exceeds expected site coverage")
        counts = [bounds(c, x, y) for c, x, y
                  in zip(*(profile[k] for k in fields))]
        results.append(counts)
    return {
        "status": "bounded_original_vulkan_unity_coordinate_axis_intersections",
        "baseline_sites": results[0],
        "integer_source_variant_sites": results[1],
        "real_gpu_logs_and_source_authenticated_independently_by_this_gate": False,
        "individual_shader_invocations_recovered": False,
        "site2_integer_carrier_causality_proven": False,
        "full_fft_numeric_parity_or_android_water_proven": False,
    }


def analyze_logs(baseline_log, integer_log):
    # Existing classifier validates marker/provenance shape, 64/256/64 keyed
    # coverage, physical CopyInput and distinct logs before we use axis counts.
    result = compare(baseline_log, integer_log)
    a = _profile(baseline_log, variant=None)
    b = _profile(integer_log, variant="integer_source")
    if (a["coordinate_mismatch_by_site"] != result["baseline_coordinate_mismatch_by_site"]
            or b["coordinate_mismatch_by_site"] != result["variant_coordinate_mismatch_by_site"]):
        raise ValueError("Concurrent edit or mismatched FFT log profile")
    return analyze_profiles(a, b)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-job-log", type=Path, required=True)
    p.add_argument("--integer-job-log", type=Path, required=True)
    args = p.parse_args()
    try:
        result = analyze_logs(args.baseline_job_log, args.integer_job_log)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_FFT_AXIS_OVERLAP incomplete_or_untrusted_aggregate_evidence=true\n")
    print("RAFT_T1_FFT_AXIS_OVERLAP " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
