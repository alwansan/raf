"""Compare two observed original-Vulkan versus Unity-OpenGLCore FFT job logs.

Source-only post-run classifier. CI markers and their run identities are
UNSIGNED; this does not attest the GPU compiled binary, the original author's
runtime kernel mapping, or any Android water pixel. Never print raw logs,
shader code, private SHA values, shader identifiers or invocation coordinates.
"""
import argparse
import json
from pathlib import Path
import re

MAX_LOG_BYTES = 8 * 1024 * 1024
MAX_LINE_CHARS = 16384
RECORDS = (64, 256, 64)
TOTAL_TEXELS = 32768
SAFE_MARKERS = (
    "RAFT_T1_REPLAY_LAST_ENTERED_STAGE",
    "RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN",
    "RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER",
    "RAFT_T1_INPUT_IDENTITY",
    "RAFT_T1_UNITY_TRACE_OUTPUT_PARITY",
)
VARIANT = "RAFT_T1_SLOT0_VARIANT"
TIMESTAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z ")


def _dupe_pairs(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError("Duplicate safe diagnostic field")
        obj[k] = v
    return obj


def _count(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Unsafe private diagnostic count")
    return value


def _true(obj, name):
    if obj.get(name) is not True:
        raise ValueError("Private original/Unity producer evidence missing")


def _false(obj, name):
    if obj.get(name) is not False:
        raise ValueError("Private producer incorrectly asserts device/runtime proof")


def _read_events(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Private CI log must be a regular non-symlink file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_LOG_BYTES + 1)
    if not 0 < len(raw) <= MAX_LOG_BYTES:
        raise ValueError("Private job log exceeds size bound")
    events = {}
    for line in raw.decode("utf-8").splitlines():
        if len(line) > MAX_LINE_CHARS:
            raise ValueError("Private log line overlong")
        m = TIMESTAMP.match(line)
        if not m:
            continue
        msg = line[m.end():]
        marker, sep, payload = msg.partition(" ")
        if not sep or marker not in (*SAFE_MARKERS, VARIANT):
            continue
        if marker in events:
            raise ValueError("Duplicate private GPU marker")
        if marker in (VARIANT, "RAFT_T1_REPLAY_LAST_ENTERED_STAGE"):
            events[marker] = payload
            continue
        if not 0 < len(payload) <= MAX_LINE_CHARS:
            raise ValueError("Private GPU JSON marker too large")
        obj = json.loads(
            payload, object_pairs_hook=_dupe_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
        )
        if type(obj) is not dict:
            raise ValueError("Private marker JSON must be object")
        events[marker] = obj
    if any(k not in events for k in SAFE_MARKERS):
        raise ValueError("One or more actual private GPU producer markers missing")
    return events


def _profile(path, *, variant):
    events = _read_events(path)
    if events["RAFT_T1_REPLAY_LAST_ENTERED_STAGE"] != "stage=complete":
        raise ValueError("Unity NUnit did not reach complete stage")
    if variant is None:
        if VARIANT in events:
            raise ValueError("Baseline was modified")
    elif events.get(VARIANT) != "mode=" + variant + " untouched_vulkan_reference=true":
        raise ValueError("Incorrect FFT counterfactual mode")

    paired = events["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"]
    if paired.get("status") != "private_actual_original_spirv_vs_unity_declared_keyed_input_join":
        raise ValueError("Private direct-original source gate missing")
    for name in (
        "actual_direct_original_spirv_trace_source_declared_by_private_producer",
        "actual_gpu_copy_input_report_required",
        "actual_physical_input_pairs_sha_bound_to_original_private_sidecar",
    ):
        _true(paired, name)
    for name in (
        "android_adreno_water_proven",
        "original_runtime_findkernel_mapping_proven",
        "unity_gpu_shader_compiled_binary_attested_independently",
    ):
        _false(paired, name)
    if paired.get("original_and_unity_keyed_trace_site_coverage") != list(RECORDS):
        raise ValueError("Original and Unity keyed sites incomplete")

    producer = events["RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER"]
    if producer.get("status") != "private_original_derived_unity_fft_producer_stage_and_candidate_hashes_checked":
        raise ValueError("Unity candidate SHA gate missing")
    for name in (
        "private_unity_producer_complete_stage_file_verified",
        "private_unity_trace_shader_and_output_physically_sha_bound",
        "reported_unity_copyinput_identity_required",
    ):
        _true(producer, name)
    for name in (
        "unity_compiler_shader_binary_independently_attested",
        "unity_nunit_stage_file_is_signed_attestation",
        "original_authored_runtime_findkernel_proven",
        "android_adreno_water_proven",
    ):
        _false(producer, name)
    if type(producer.get("original_derived_candidate_slots_physically_sha_bound")) is not int or producer["original_derived_candidate_slots_physically_sha_bound"] != 2:
        raise ValueError("Private translated candidate SHA provenance missing")

    identity = events["RAFT_T1_INPUT_IDENTITY"]
    if identity.get("unity_backend") != "OpenGLCore" or identity.get("texels_per_input") != TOTAL_TEXELS:
        raise ValueError("Different Unity backend or source fixture")
    for name in ("source_mismatches", "butterfly_mismatches"):
        if type(identity.get(name)) is not int or identity[name] != 0:
            raise ValueError("Actual Unity GPU CopyInput image mismatch")

    output = events["RAFT_T1_UNITY_TRACE_OUTPUT_PARITY"]
    if output.get("match") is not True or type(output.get("compared_written_pixels")) is not int or output["compared_written_pixels"] != 64:
        raise ValueError("Unity instrumented output not invariant")
    for name in ("write_coverage_mismatch_pixels", "nonfinite_pixels", "outside_tolerance_pixels"):
        if type(output.get(name)) is not int or output[name] != 0:
            raise ValueError("Unity instrumented shader introduced output drift")

    sites = paired.get("diagnostics")
    if type(sites) is not list or len(sites) != 3:
        raise ValueError("Three real keyed read sites missing")
    mismatch, zeros_x, zeros_y = [], [], []
    for i, (site, expected) in enumerate(zip(sites, RECORDS)):
        if type(site) is not dict or type(site.get("site")) is not int or site["site"] != i:
            raise ValueError("FFT site identity or ordering changed")
        _count(site.get("paired_invocations"), expected, expected)
        for name in ("reference_only_invocations", "unity_only_invocations"):
            _count(site.get(name), 0, 0)
        changed = _count(site.get("coordinate_mismatching_invocations"), 0, expected)
        _count(site.get("value_comparison_skipped_after_coordinate_drift"), changed, changed)
        zero, other = (site.get("coordinate_zero_collapse_by_axis"),
                       site.get("other_coordinate_drift_by_axis"))
        if (type(zero) is not dict or type(other) is not dict or
                set(zero) != {"x", "y", "mip"} or set(other) != {"x", "y", "mip"}):
            raise ValueError("Unknown original/Unity coordinate axes")
        for axis in ("x", "y", "mip"):
            if _count(zero[axis], 0, changed) + _count(other[axis], 0, changed) > changed:
                raise ValueError("Impossible per-axis coordinate profile")
        # Every mismatched coordinate must differ on at least one axis.
        # Axes may overlap per invocation, so only reject insufficient coverage.
        axis_coverage_upper_bound = sum(zero[axis] + other[axis] for axis in ("x", "y", "mip"))
        if axis_coverage_upper_bound < changed:
            raise ValueError("FFT coordinate drift lacks axis coverage")
        mismatch.append(changed)
        zeros_x.append(zero["x"])
        zeros_y.append(zero["y"])
    return {"coordinate_mismatch_by_site": mismatch,
            "zero_collapse_x_by_site": zeros_x,
            "zero_collapse_y_by_site": zeros_y}


def compare(baseline_log, variant_log):
    baseline, variant = Path(baseline_log), Path(variant_log)
    if baseline.samefile(variant):
        raise ValueError("Baseline and integer-source job logs alias")
    a = _profile(baseline, variant=None)
    b = _profile(variant, variant="integer_source")
    first, second = a["coordinate_mismatch_by_site"], b["coordinate_mismatch_by_site"]
    return {
        "status": "private_original_vulkan_vs_unity_real_gpu_keyed_integer_source_delta",
        "baseline_coordinate_mismatch_by_site": first,
        "variant_coordinate_mismatch_by_site": second,
        "site_coordinate_mismatch_delta_variant_minus_baseline": [v - u for u, v in zip(first, second)],
        "site0_source_integer_variant_reduces_coordinate_drift": second[0] < first[0],
        "all_three_sites_coordinate_parity_observed": second == [0, 0, 0],
        "variant_not_worse_on_any_site": all(v <= u for u, v in zip(first, second)),
        "all_real_gpu_markers_and_input_identity_aggregates_present": True,
        "source_bytes_or_compiler_binary_independently_authenticated_here": False,
        "runtime_findkernel_and_android_adreno_water_proven": False,
        "raw_shader_log_source_pixels_ids_and_private_hashes_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-job-log", required=True, type=Path)
    p.add_argument("--integer-job-log", required=True, type=Path)
    args = p.parse_args()
    try:
        report = compare(args.baseline_job_log, args.integer_job_log)
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_REAL_GPU_INTEGER_DELTA incomplete_or_untrusted_aggregate_evidence=true\n")
    print("RAFT_T1_REAL_GPU_INTEGER_DELTA " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
