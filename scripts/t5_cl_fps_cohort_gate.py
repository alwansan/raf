#!/usr/bin/env python3
"""Conservative, read-only audit of *fresh* device-frame presentation evidence.

SurfaceFlinger is not Unity FPS. A sample before the first observed shader/FFT
error cannot be used as post-error gameplay performance. "No fresh frames"
never means a frozen game. No individual device/log payload is emitted.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import statistics

PACKAGE = "com.alwansan.raft.androidtest"
MAX_FILE = 2_000_000
MAX_SAMPLES = 2000
MIN_PHASE_SAMPLES = 10


def _is_int(x):
    return type(x) is int and x > 0


def _is_number(x):
    return type(x) in (int, float) and math.isfinite(x)


def _reject_duplicate_json_keys(pairs):
    """Fail closed on ambiguous telemetry fields, including nested JSON objects."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON telemetry key: " + key)
        result[key] = value
    return result


def load_samples(path: Path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_FILE:
        raise ValueError("Missing, symlinked or oversized telemetry file")
    rows = []
    last_sample = 0
    last_time = 0
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                raise ValueError("Blank JSONL row")
            if len(rows) >= MAX_SAMPLES:
                raise ValueError("Too many telemetry rows")
            row = json.loads(line, object_pairs_hook=_reject_duplicate_json_keys)
            if type(row) is not dict or row.get("schema") != 1 or row.get("source") != "lograf_shell" or row.get("package") != PACKAGE:
                raise ValueError("Unexpected telemetry schema, source or package")
            number = row.get("sample")
            timestamp = row.get("timestamp_unix_ms")
            if not _is_int(number) or not _is_int(timestamp) or number <= last_sample or timestamp <= last_time:
                raise ValueError("Telemetry ordering, sample ID or timestamp invalid")
            last_sample, last_time = number, timestamp
            rows.append(row)
    if not rows:
        raise ValueError("Telemetry is empty")
    return rows


def _fresh_fps(row):
    fps = row.get("presented_fps_estimate")
    window = row.get("presented_frame_window_count")
    age = row.get("last_present_progress_age_ms")
    return (row.get("state") == "game_running"
            and row.get("pid_probe_status") == "main_pid_verified"
            and _is_int(row.get("pid"))
            and row.get("fps_quality") == "surface_presentation_estimate"
            and row.get("fps_tracking_status") == "valid_surface_presentation_estimate"
            and row.get("frame_telemetry_stale") is False
            and _is_int(row.get("fps_valid_sample_count"))
            and _is_int(window)
            and _is_number(age) and 0 <= age <= 2000
            and _is_number(fps) and 0 < fps <= 1000)


def _error_observed(row):
    # The first independently sampled shader/kernel failure is a temporal
    # boundary. It does not prove why FPS changes or which scene was active.
    return any(_is_number(row.get(k)) and row[k] > 0 for k in (
        "shader_pass_errors_total", "invalid_compute_kernel_total",
        "render_error_roots_per_second"))


def _digest_values(rows):
    if not rows:
        return None
    vals = [float(x["presented_fps_estimate"]) for x in rows]
    return {"samples": len(vals), "fps_median": round(statistics.median(vals), 3),
            "fps_min": round(min(vals), 3), "fps_max": round(max(vals), 3)}


def analyze(rows, session_label):
    if not isinstance(session_label, str) or not session_label or len(session_label) > 64:
        raise ValueError("Invalid session label")
    # T5 scheduled PID-epoch auditor is the sole process-lifetime source of
    # truth. Import at call-time because that auditor imports the existing
    # _fresh_fps predicate from this module. This protects both direct analyze()
    # consumers and the CLI: no medians may span verified PID changes or
    # unverified running-process intervals.
    from scripts.t5_cl_pid_epoch_audit import audit
    process = audit(rows)
    process_safe = process["safe_to_aggregate_entire_session"]
    onset = next((r for r in rows if _error_observed(r)), None)
    onset_sample = onset["sample"] if onset else None
    onset_time = onset["timestamp_unix_ms"] if onset else None
    # Never take medians of otherwise fresh SurfaceFlinger rows when they may
    # refer to a different Raft process lifetime. Retain counts separately.
    all_fresh = [r for r in rows if _fresh_fps(r)]
    fresh = all_fresh if process_safe else []
    before = [r for r in fresh if onset_time is None or r["timestamp_unix_ms"] < onset_time]
    after = [r for r in fresh if onset_time is not None and r["timestamp_unix_ms"] >= onset_time]
    return {
        "process_epoch_count": process["process_epoch_count"],
        "safe_to_aggregate_entire_session": process_safe,
        "fps_rows_withheld_unverified_process_epoch": 0 if process_safe else len(all_fresh),
        "process_epoch_diagnostic": "verified_one_process" if process_safe else "unsafe_mixed_or_unverified_process_epoch",
        "session": session_label,
        "total_samples": len(rows),
        "game_running_samples": sum(r.get("state") == "game_running" for r in rows),
        "stale_presentation_samples": sum(r.get("frame_telemetry_stale") is True for r in rows),
        "first_observed_render_failure_sample": onset_sample,
        "fresh_surface_fps_all": _digest_values(fresh),
        "fresh_fps_before_first_render_error": _digest_values(before),
        "fresh_fps_during_or_after_render_error": _digest_values(after),
        "render_error_flood_flag_samples": sum(r.get("render_error_flood_warning") is True for r in rows),
        "fps_method": "SurfaceFlinger presented-frame estimate, not Unity Update/GPU FPS",
        "gpu_busy_attribution": "KGSL system-wide utilization; not per-game GPU time",
        "missing_presentation_does_not_prove_freeze": True,
    }


def compare(first, second):
    a = first["fresh_fps_during_or_after_render_error"]
    b = second["fresh_fps_during_or_after_render_error"]
    na = a["samples"] if a else 0
    nb = b["samples"] if b else 0
    if (first.get("safe_to_aggregate_entire_session") is not True
            or second.get("safe_to_aggregate_entire_session") is not True):
        outcome = "NOT_COMPARABLE_unverified_or_mixed_process_epoch"
    elif min(na, nb) < MIN_PHASE_SAMPLES:
        outcome = "NOT_COMPARABLE_inadequate_fresh_post_render_error_samples"
    else:
        outcome = "NOT_COMPARABLE_missing_same_scene_settings_and_binary_identity"
    return {
        "assessment": outcome,
        "minimum_post_error_fps_samples_per_session": MIN_PHASE_SAMPLES,
        "post_error_fresh_sample_counts": [na, nb],
        "no_aggregate_cross_session_fps": True,
        "not_evidence_of_game_freeze_or_thermal_causation": True,
        "next_required_evidence": "same-signed-binary/scene/settings plus valid Unity and SurfaceFlinger frame timing windows",
    }


def main():
    # Keep the original documented "python3 scripts/t5_cl_fps_cohort_gate.py"
    # entry point working, not only "python3 -m scripts.t5_cl_fps_cohort_gate".
    # Its sibling PID-epoch audit imports this module by package name, while
    # direct file execution otherwise only puts the scripts/ directory on
    # sys.path. Use the resolved local repo root, never an untrusted CL path.
    if not __package__:
        import sys
        repo_root = str(Path(__file__).resolve().parents[1])
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-a", required=True, type=Path)
    parser.add_argument("--label-a", default="220911-559")
    parser.add_argument("--session-b", required=True, type=Path)
    parser.add_argument("--label-b", default="230108-327")
    args = parser.parse_args()
    first = analyze(load_samples(args.session_a), args.label_a)
    second = analyze(load_samples(args.session_b), args.label_b)
    print("T5_CL_PRESENTATION_EVIDENCE " + json.dumps(
        {"session_a": first, "session_b": second, "comparison": compare(first, second)},
        sort_keys=True))


if __name__ == "__main__":
    main()
