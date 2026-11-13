"""GT source-free negative controls for the owner-device graphics log gate."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.gt_device_graphics_acceptance import analyze, main, PACKAGE


def fixture(passes=0, kernel=0, cursor=0, guid=0, sink=0):
    errors = {
        "ultimate_water_invalid_pass": {"count": passes},
        "water_fft_invalid_compute_kernel": {"count": kernel},
        "unity_cursor_rgba32_required": {"count": cursor},
        "obb_guid_load_failed": {"count": guid},
        "unity_missing_mono_script": {"count": 0},
    }
    return {
        "schema": 1, "target_package": PACKAGE,
        "raw_log_policy": "preserve all segments; never delete",
        "final_error_category_breakdown": errors,
        "final_shader_pass_errors_total": passes,
        "final_compute_kernel_errors_total": kernel,
        "final_game_log_lines": passes + kernel + cursor + guid,
        "final_remote_sink_failed_batches": sink,
        "performance_statistics": {
            "total_samples": 10, "metrics": {
                "presented_fps_estimate": {"readable_samples": 3}}},
        "final_render_failure_breakdown": {
            "ultimate_water_invalid_pass_by_material": {
                "spectrum": passes, "foam_global": 0,
                "subsurface_blur": 0, "utility_noise": 0,
                "other_ultimate_water": 0},
            "invalid_kernel_index_root_lines": {
                "index_6": kernel, "other_index": 0}}
    }


class GraphicsLogGateTests(unittest.TestCase):
    def test_known_error_free_only_narrow_pass(self):
        r = analyze(fixture())
        self.assertTrue(r["strict_known_log_gate_passed"])
        self.assertEqual(r["status"], "KNOWN_DEVICE_LOG_GATE_PASSED_ONLY")
        self.assertFalse(r["all_pixels_correct_verified"])
        self.assertFalse(r["original_shader_sampler_or_material_parity_verified"])

    def test_owner_observed_water_error_family_rejected(self):
        d = fixture(passes=42229, kernel=7263, cursor=4668, guid=2)
        d["final_render_failure_breakdown"]["ultimate_water_invalid_pass_by_material"].update(
            spectrum=19191, foam_global=23038)
        r = analyze(d)
        self.assertFalse(r["strict_known_log_gate_passed"])
        self.assertEqual(r["observed_critical_error_count"], 49494)
        self.assertEqual(r["water_invalid_pass_by_family"]["foam_global"], 23038)
        self.assertEqual(r["compute_invalid_kernel_index"]["six"], 7263)

    def test_missing_known_error_category_is_not_a_false_green(self):
        # The collector writes explicit zeroes for all known buckets.
        for category in ("ultimate_water_invalid_pass",
                         "water_fft_invalid_compute_kernel",
                         "obb_guid_load_failed",
                         "unity_cursor_rgba32_required",
                         "unity_missing_mono_script"):
            d = fixture()
            del d["final_error_category_breakdown"][category]
            with self.subTest(category=category), self.assertRaisesRegex(
                ValueError, "missing_required_error_category"):
                analyze(d)

    def test_cursor_warning_not_original_water_program_failure(self):
        r = analyze(fixture(cursor=4668))
        self.assertTrue(r["strict_known_log_gate_passed"])
        self.assertEqual(r["observed_warning_count"], 4668)

    def test_exit_info_scoped_real_collector_counters(self):
        d = fixture(passes=5, kernel=7, sink=0)
        d["stop_time_android_process_exit_info"] = {
            k: d.pop(k) for k in (
                "final_shader_pass_errors_total",
                "final_compute_kernel_errors_total",
                "final_remote_sink_failed_batches")}
        self.assertEqual(
            analyze(d)["observed_critical_error_count"], 12)
        # Duplicate inconsistent values are not silently reconciled.
        d["final_shader_pass_errors_total"] = 6
        with self.assertRaisesRegex(ValueError, "conflicting_device_final_counter"):
            analyze(d)

    def test_new_owner_20261112_night_water_session_rejected(self):
        # Source-count only fixture: CL@a320d5e, session 20261112-235351-196.
        d = fixture(passes=36828, kernel=6106, cursor=2844, guid=2)
        d["final_render_failure_breakdown"][
            "ultimate_water_invalid_pass_by_material"].update(
                spectrum=15054, foam_global=21774)
        d.update(writer_received_batches=3390, writer_written_batches=3390,
                 writer_failed_batches=0, writer_pending_bytes_at_stop=0)
        r = analyze(d)
        self.assertEqual(r["status"], "KNOWN_DEVICE_LOG_GATE_REJECTED")
        self.assertEqual(r["observed_critical_error_count"], 42936)
        self.assertEqual(r["water_invalid_pass_by_family"]["foam_global"], 21774)
        self.assertEqual(r["compute_invalid_kernel_index"]["six"], 6106)
        self.assertTrue(r["collector_writer_accounting_verified"])
        self.assertEqual(r["collector_writer_failed_batches"], 0)
        self.assertFalse(r["strict_known_log_gate_passed"])
        self.assertFalse(r["all_pixels_correct_verified"])

    def test_modern_writer_accounting_cannot_false_green(self):
        clean = fixture()
        clean.update(writer_received_batches=30, writer_written_batches=30,
                     writer_failed_batches=0, writer_pending_bytes_at_stop=0)
        self.assertTrue(analyze(clean)["strict_known_log_gate_passed"])
        missing = copy.deepcopy(clean)
        del missing["writer_failed_batches"]
        with self.assertRaisesRegex(ValueError, "partial_collector_writer_accounting"):
            analyze(missing)
        unaccounted = copy.deepcopy(clean)
        unaccounted["writer_written_batches"] = 29
        with self.assertRaisesRegex(ValueError, "unaccounted_collector_writer_batches"):
            analyze(unaccounted)
        impossible = copy.deepcopy(clean)
        impossible["writer_written_batches"] = 31
        with self.assertRaisesRegex(ValueError, "impossible_collector_writer_batch_totals"):
            analyze(impossible)
        pending = copy.deepcopy(clean)
        pending["writer_pending_bytes_at_stop"] = 42
        self.assertFalse(analyze(pending)["strict_known_log_gate_passed"])
        failed = copy.deepcopy(clean)
        failed["writer_written_batches"] = 29
        failed["writer_failed_batches"] = 1
        failed["final_remote_sink_failed_batches"] = 1
        self.assertFalse(analyze(failed)["strict_known_log_gate_passed"])
        mismatch = copy.deepcopy(failed)
        mismatch["final_remote_sink_failed_batches"] = 0
        with self.assertRaisesRegex(ValueError, "collector_writer_sink_failure_count_mismatch"):
            analyze(mismatch)

    def test_silent_batch_loss_rejects_acceptance(self):
        self.assertFalse(analyze(fixture(sink=1))["strict_known_log_gate_passed"])

    def test_missing_or_inconsistent_pass_totals_rejected(self):
        d = fixture(passes=4)
        d["final_shader_pass_errors_total"] = 5
        with self.assertRaisesRegex(ValueError, "shader_pass_category_total_mismatch"):
            analyze(d)
        d = fixture(passes=4)
        d["final_render_failure_breakdown"][
            "ultimate_water_invalid_pass_by_material"]["spectrum"] = 3
        with self.assertRaisesRegex(ValueError, "water_material_sum_mismatch"):
            analyze(d)

    def test_invalid_schema_and_type_rejected(self):
        for mutation in (
            {"target_package": "untrusted.package"},
            {"schema": 2},
            {"final_shader_pass_errors_total": True},
            {"final_compute_kernel_errors_total": -1},
            {"raw_log_policy": "unknown"},
        ):
            d = fixture()
            d.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                analyze(d)

    def test_truncated_or_incorrect_kernel_breakdown_rejected(self):
        d = fixture(kernel=5)
        d["final_render_failure_breakdown"]["invalid_kernel_index_root_lines"]["index_6"] = 4
        with self.assertRaisesRegex(ValueError, "kernel_index_sum_mismatch"):
            analyze(d)

    def test_owner_summary_not_modified(self):
        d = fixture(passes=1)
        old = copy.deepcopy(d)
        analyze(d)
        self.assertEqual(d, old)


if __name__ == "__main__":
    unittest.main()
