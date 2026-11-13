#!/usr/bin/env python3
"""GT: fail-closed, *device-log-only* Raft graphics regression receipt.

Consumes a LogRaft session-summary.json provided by the owner (e.g. CL).
Never reads/transmits raw Unity logs, screenshots, source assets or device IDs.
Zero observed errors proves only this narrow log contract, NOT original shader
equivalence, complete GPU pixels, or absence of unlogged rendering defects.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_BYTES = 512 * 1024
PACKAGE = "com.alwansan.raft.androidtest"
CRITICAL = ("ultimate_water_invalid_pass", "water_fft_invalid_compute_kernel",
            "obb_guid_load_failed")
WARNINGS = ("unity_cursor_rgba32_required", "unity_missing_mono_script")
ALL = CRITICAL + WARNINGS


def _natural(value, label):
    if type(value) is not int or not 0 <= value <= 100_000_000:
        raise ValueError("invalid_" + label)
    return value


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError("missing_or_invalid_" + label)
    return value


def _final_counter(data, name):
    """Device collector stores final counters under exit-info in some versions."""
    exit_info = data.get("stop_time_android_process_exit_info", {})
    if not isinstance(exit_info, dict):
        raise ValueError("invalid_exit_info_receipt")
    outer = data.get(name)
    inner = exit_info.get(name)
    if outer is not None and inner is not None and outer != inner:
        raise ValueError("conflicting_device_final_counter_" + name)
    return _natural(outer if outer is not None else inner, name)


def analyze(data):
    data = _require_mapping(data, "session")
    if data.get("schema") != 1 or data.get("target_package") != PACKAGE:
        raise ValueError("unsupported_device_session_schema_or_package")
    if data.get("raw_log_policy") != "preserve all segments; never delete":
        raise ValueError("raw_log_capture_policy_unproven")
    breakdown = _require_mapping(data.get("final_error_category_breakdown"),
                                 "final_error_categories")
    receipts = {}
    for key in ALL:
        # LogRaft 0.6.89 reports every known category with an explicit
        # zero count. A missing category is unobserved, NOT a clean pass.
        if key not in breakdown:
            raise ValueError("missing_required_error_category_" + key)
        receipts[key] = _natural(
            _require_mapping(breakdown[key], key).get("count"), key)
    total_pass = _final_counter(data, "final_shader_pass_errors_total")
    total_kernel = _final_counter(data, "final_compute_kernel_errors_total")
    if total_pass != receipts["ultimate_water_invalid_pass"]:
        raise ValueError("shader_pass_category_total_mismatch")
    if total_kernel != receipts["water_fft_invalid_compute_kernel"]:
        raise ValueError("compute_kernel_category_total_mismatch")
    if _natural(data.get("final_game_log_lines"), "final_game_log_lines") < (
        total_pass + total_kernel):
        raise ValueError("invalid_log_count_lower_bound")
    lost_local = _final_counter(data, "final_remote_sink_failed_batches")
    stats = _require_mapping(data.get("performance_statistics"), "statistics")
    samples = _natural(stats.get("total_samples"), "sample_count")
    fps = _require_mapping(
        _require_mapping(stats.get("metrics"), "statistics_metrics").get(
            "presented_fps_estimate"), "fps_metric")
    fps_readable = _natural(fps.get("readable_samples"), "fps_samples")
    if fps_readable > samples:
        raise ValueError("fps_samples_exceed_sample_count")
    sources = _require_mapping(
        data.get("final_render_failure_breakdown"), "render_failure_breakdown")
    categories = _require_mapping(
        sources.get("ultimate_water_invalid_pass_by_material"),
        "water_material_categories")
    spectrum = _natural(categories.get("spectrum"), "water_spectrum_count")
    foam = _natural(categories.get("foam_global"), "water_foam_count")
    other = sum(_natural(categories.get(k), k) for k in (
        "subsurface_blur", "utility_noise", "other_ultimate_water"))
    if spectrum + foam + other != total_pass:
        raise ValueError("water_material_sum_mismatch")
    kernel = _require_mapping(sources.get("invalid_kernel_index_root_lines"),
                              "kernel_index_counts")
    k6 = _natural(kernel.get("index_6"), "kernel6_count")
    k_other = _natural(kernel.get("other_index"), "other_kernel_count")
    if k6 + k_other != total_kernel:
        raise ValueError("kernel_index_sum_mismatch")
    # Modern LogRaft records the FIFO writer counts independently of the
    # remote-sink exit totals. Reject a false green if final batches were
    # never committed, even when all known rendering-error buckets are zero.
    writer_fields = ("writer_received_batches", "writer_written_batches",
                     "writer_failed_batches", "writer_pending_bytes_at_stop")
    writer_present = any(key in data for key in writer_fields)
    writer_failed = None
    writer_pending = None
    if writer_present:
        if not all(key in data for key in writer_fields):
            raise ValueError("partial_collector_writer_accounting")
        received = _natural(data["writer_received_batches"], "writer_received_batches")
        written = _natural(data["writer_written_batches"], "writer_written_batches")
        writer_failed = _natural(data["writer_failed_batches"], "writer_failed_batches")
        writer_pending = _natural(data["writer_pending_bytes_at_stop"],
                                  "writer_pending_bytes_at_stop")
        if written + writer_failed > received:
            raise ValueError("impossible_collector_writer_batch_totals")
        if writer_failed != lost_local:
            raise ValueError("collector_writer_sink_failure_count_mismatch")
        if writer_pending == 0 and written + writer_failed != received:
            raise ValueError("unaccounted_collector_writer_batches")
    # Android ActivityManager's matched PID reason is separate from render
    # errors. Expose a specific LOW_MEMORY observation; never infer the
    # originating GPU/asset allocation or the exact killer without evidence.
    exit_info = data.get("stop_time_android_process_exit_info", {})
    if not isinstance(exit_info, dict):
        raise ValueError("invalid_exit_info_receipt")
    matched_exit = exit_info.get("status") == "matched_pid_in_android_exit_history"
    if matched_exit:
        reason_code = _natural(exit_info.get("android_exit_reason_code"),
                               "android_exit_reason_code")
        reason_label = exit_info.get("android_exit_reason_label")
        if not isinstance(reason_label, str) or not 1 <= len(reason_label) <= 64:
            raise ValueError("malformed_android_exit_reason_label")
        low_memory_exit = reason_code == 3 and reason_label == "LOW_MEMORY"
    else:
        low_memory_exit = False
    critical_ok = all(receipts[x] == 0 for x in CRITICAL)
    capture_ok = (lost_local == 0 and
                  (not writer_present or
                   (writer_failed == 0 and writer_pending == 0)))
    # The owner must still check screenshots and an actual device render even
    # if the known log errors disappear from a new session.
    return {
        "schema": 1,
        "status": ("KNOWN_DEVICE_LOG_GATE_PASSED_ONLY" if critical_ok and capture_ok
                   else "KNOWN_DEVICE_LOG_GATE_REJECTED"),
        "observed_critical_error_count": sum(receipts[x] for x in CRITICAL),
        "observed_warning_count": sum(receipts[x] for x in WARNINGS),
        "error_counts": receipts,
        "water_invalid_pass_by_family": {
            "spectrum": spectrum, "foam_global": foam, "other": other},
        "compute_invalid_kernel_index": {"six": k6, "other": k_other},
        "android_matched_low_memory_exit_observed": low_memory_exit,
        "android_process_exit_cause_other_than_reported_reason_proven": False,
        "log_capture_local_batches_failed": lost_local,
        "collector_writer_accounting_verified": writer_present,
        "collector_writer_failed_batches": writer_failed,
        "collector_writer_pending_bytes_at_stop": writer_pending,
        "samples": samples,
        "presented_fps_samples": fps_readable,
        "device_runtime_render_equivalence_verified": False,
        "original_shader_sampler_or_material_parity_verified": False,
        "all_pixels_correct_verified": False,
        "future_new_error_classes_excluded": False,
        "strict_known_log_gate_passed": critical_ok and capture_ok,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-summary", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    source = args.session_summary
    if source.is_symlink() or not source.is_file() or not 0 < source.stat().st_size <= MAX_BYTES:
        raise ValueError("unsafe_or_oversized_owner_session_summary")
    report = analyze(json.loads(source.read_text(encoding="utf-8")))
    if args.out is not None:
        if args.out.is_symlink() or args.out.exists() or args.out.resolve() == source.resolve():
            raise ValueError("unsafe_or_existing_report_destination")
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print("GT_DEVICE_GRAPHICS_LOG_GATE " + json.dumps(report, sort_keys=True))
    if args.strict and not report["strict_known_log_gate_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
