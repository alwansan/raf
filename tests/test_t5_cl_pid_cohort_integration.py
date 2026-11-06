"""T5: prevent mixed Raft process lifetime FPS aggregation in the existing CL CLI."""
import unittest

from scripts.t5_cl_fps_cohort_gate import analyze, compare
from scripts.t5_cl_pid_epoch_audit import audit
from scripts.t5_cl_fps_cohort_gate import PACKAGE


def row(sample, *, fps=24.0, error=1, running=True):
    """Public synthetic only; never inject actual owner PID or timestamps."""
    return {
        "schema": 1, "source": "lograf_shell", "package": PACKAGE,
        "sample": sample, "timestamp_unix_ms": 1700000000000 + 3200 * sample,
        "state": "game_running" if running else "game_not_running",
        "pid": 123 if running else None,
        "pid_probe_status": "main_pid_verified",
        "fps_quality": "surface_presentation_estimate",
        "fps_tracking_status": "valid_surface_presentation_estimate",
        "fps_valid_sample_count": sample,
        "frame_telemetry_stale": False,
        "presented_fps_estimate": fps,
        "presented_frame_window_count": 50,
        "last_present_progress_age_ms": 0,
        "shader_pass_errors_total": error,
        "invalid_compute_kernel_total": 0,
        "render_error_roots_per_second": 0.0,
        "render_error_flood_warning": error > 0,
    }



class ProcessEpochCohortIntegration(unittest.TestCase):
    def test_single_verified_pid_preserves_historical_fresh_samples(self):
        rows = [row(1, fps=25.0, error=0), row(2, fps=20.0, error=8)]
        report = analyze(rows, "single")
        self.assertEqual(report["process_epoch_count"], 1)
        self.assertTrue(report["safe_to_aggregate_entire_session"])
        self.assertEqual(report["fps_rows_withheld_unverified_process_epoch"], 0)
        self.assertEqual(report["fresh_surface_fps_all"]["samples"], 2)
        self.assertEqual(report["fresh_surface_fps_all"]["fps_median"], 22.5)

    def test_verified_restart_forbids_cross_pid_fps_median(self):
        original = [row(1, fps=120.0), row(2, fps=10.0), row(3, fps=80.0)]
        original[2]["pid"] = 456
        report = analyze(original, "restarted")
        self.assertEqual(report["process_epoch_count"], 2)
        self.assertFalse(report["safe_to_aggregate_entire_session"])
        self.assertIsNone(report["fresh_surface_fps_all"])
        self.assertIsNone(report["fresh_fps_during_or_after_render_error"])
        self.assertEqual(report["fps_rows_withheld_unverified_process_epoch"], 3)
        self.assertNotIn("123", str(report))
        self.assertNotIn("456", str(report))

    def test_unverified_running_gap_forbids_stale_pid_reuse(self):
        rows = [row(1, fps=20), row(2, fps=20), row(3, fps=20)]
        rows[1]["pid_probe_status"] = "pid_tracking_lost_unverified"
        rows[1]["pid"] = None
        report = analyze(rows, "gap")
        self.assertEqual(report["process_epoch_count"], 3)
        self.assertFalse(report["safe_to_aggregate_entire_session"])
        self.assertEqual(report["fps_rows_withheld_unverified_process_epoch"], 2)
        self.assertIsNone(report["fresh_surface_fps_all"])

    def test_only_non_running_rows_does_not_claim_verified_process(self):
        stopped = row(1, running=False)
        report = analyze([stopped], "stopped")
        self.assertEqual(report["process_epoch_count"], 1)
        self.assertFalse(report["safe_to_aggregate_entire_session"])
        self.assertIsNone(report["fresh_surface_fps_all"])

    def test_audit_and_original_fps_report_have_same_epoch_verdict(self):
        for data in ([row(1), row(2)],
                     [row(1), dict(row(2), pid=777)],
                     [dict(row(1), pid_probe_status="pid_tracking_lost_unverified")]):
            with self.subTest(rows=len(data)):
                source = audit(data)
                report = analyze(data, "audit")
                self.assertEqual(
                    report["safe_to_aggregate_entire_session"],
                    source["safe_to_aggregate_entire_session"])
                self.assertEqual(report["process_epoch_count"], source["process_epoch_count"])

    def test_cross_session_comparison_rejects_mixed_pid_before_medians(self):
        a = [row(i, fps=20.0) for i in range(1, 14)]
        b = [row(i, fps=35.0) for i in range(1, 14)]
        b[-1]["pid"] = 789
        one, two = analyze(a, "one"), analyze(b, "two")
        verdict = compare(one, two)
        self.assertEqual(verdict["assessment"],
                         "NOT_COMPARABLE_unverified_or_mixed_process_epoch")
        self.assertEqual(verdict["post_error_fresh_sample_counts"], [13, 0])
        self.assertTrue(verdict["no_aggregate_cross_session_fps"])

    def test_stale_unverified_running_does_not_masquerade_as_valid_aggregate(self):
        data = [row(i, fps=30.0) for i in range(1, 14)]
        data[5]["pid_probe_status"] = "not_queried"
        data[5]["frame_telemetry_stale"] = True
        report = analyze(data, "unverified")
        self.assertFalse(report["safe_to_aggregate_entire_session"])
        self.assertIsNone(report["fresh_surface_fps_all"])
        self.assertEqual(report["fps_rows_withheld_unverified_process_epoch"], 12)


if __name__ == "__main__":
    unittest.main()
