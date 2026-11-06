"""Source-free LogRaft frame presentation freshness/error-phase controls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t5_cl_fps_cohort_gate import (
    PACKAGE, analyze, compare, load_samples, MIN_PHASE_SAMPLES,
)


def row(sample, *, fps=24.0, error=1, stale=False, running=True):
    return {
        "schema": 1, "source": "lograf_shell",
        "package": PACKAGE,
        "sample": sample, "timestamp_unix_ms": 1700000000000 + 3200*sample,
        "state": "game_running" if running else "game_not_running",
        "pid": 123 if running else None,
        "pid_probe_status": "main_pid_verified",
        "fps_quality": "surface_presentation_estimate",
        "fps_tracking_status": "valid_surface_presentation_estimate",
        "fps_valid_sample_count": sample,
        "frame_telemetry_stale": stale,
        "presented_fps_estimate": fps,
        "presented_frame_window_count": 50,
        "last_present_progress_age_ms": 0,
        "shader_pass_errors_total": error,
        "invalid_compute_kernel_total": 0,
        "render_error_roots_per_second": 0.0,
        "render_error_flood_warning": error > 0,
    }


class CohortTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.file = Path(temp.name) / "samples.jsonl"

    def save(self, rows):
        self.file.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf8")
        return load_samples(self.file)

    def test_fresh_fps_after_first_render_error(self):
        samples = [row(1, fps=120.0, error=0),
                   row(2, fps=120.5, error=0),
                   row(3, fps=22.0, error=3),
                   row(4, fps=18.0, error=8)]
        report = analyze(self.save(samples), "fixture")
        self.assertEqual(report["first_observed_render_failure_sample"], 3)
        self.assertEqual(report["fresh_fps_before_first_render_error"]["samples"], 2)
        self.assertEqual(report["fresh_fps_during_or_after_render_error"]["samples"], 2)
        self.assertEqual(report["fresh_fps_during_or_after_render_error"]["fps_median"], 20)

    def test_second_session_high_startup_fps_does_not_establish_gameplay_gain(self):
        first = analyze([row(i, fps=21, error=i) for i in range(1, 18)], "first")
        second = analyze([row(1, fps=120.77, error=0), row(2, fps=120.78, error=0)]
                         + [row(i, fps=None, error=100, stale=True) for i in range(3, 21)], "second")
        self.assertEqual(second["fresh_fps_during_or_after_render_error"], None)
        self.assertEqual(second["stale_presentation_samples"], 18)
        self.assertEqual(compare(first, second)["assessment"],
                         "NOT_COMPARABLE_inadequate_fresh_post_render_error_samples")

    def test_even_two_large_post_error_cohorts_not_same_scene(self):
        first = analyze([row(i, fps=18, error=i) for i in range(1, MIN_PHASE_SAMPLES+1)], "one")
        second = analyze([row(i, fps=35, error=i) for i in range(1, MIN_PHASE_SAMPLES+1)], "two")
        self.assertIn("missing_same_scene_settings", compare(first, second)["assessment"])

    def test_stale_nonnull_fps_is_excluded(self):
        a = row(1, fps=120, stale=True)
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_fps_120_without_progress_is_excluded(self):
        a = row(1, fps=120)
        a["last_present_progress_age_ms"] = 9999
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_unverified_pid_fps_excluded(self):
        a = row(1)
        a["pid_probe_status"] = "pid_tracking_lost_unverified"
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_wrong_surface_status_excluded(self):
        a = row(1)
        a["fps_tracking_status"] = "insufficient_presentation_samples"
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_background_fps_excluded(self):
        self.assertIsNone(analyze([row(1, running=False)], "test")["fresh_surface_fps_all"])

    def test_fps_valid_window_required(self):
        a = row(1)
        a["presented_frame_window_count"] = 0
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_nan_fps_excluded(self):
        a = row(1, fps=float("nan"))
        self.assertIsNone(analyze([a], "test")["fresh_surface_fps_all"])

    def test_mismatched_file_package_refused(self):
        a = row(1)
        a["package"] = "com.elsewhere.app"
        with self.assertRaisesRegex(ValueError, "source or package"):
            self.save([a])

    def test_duplicate_sample_refused(self):
        a = row(1)
        with self.assertRaisesRegex(ValueError, "ordering"):
            self.save([a, a])

    def test_out_of_order_timestamp_refused(self):
        a, b = row(1), row(2)
        b["timestamp_unix_ms"] = a["timestamp_unix_ms"] - 1
        with self.assertRaisesRegex(ValueError, "ordering"):
            self.save([a, b])

    def test_corrupt_schema_refused(self):
        a = row(1)
        a["source"] = "unknown"
        with self.assertRaisesRegex(ValueError, "schema"):
            self.save([a])

    def test_blank_row_refused(self):
        self.file.write_text(json.dumps(row(1)) + "\n\n", encoding="utf8")
        with self.assertRaisesRegex(ValueError, "Blank"):
            load_samples(self.file)

    def test_symlink_refused(self):
        real = self.file.parent / "real.jsonl"
        real.write_text(json.dumps(row(1))+"\n", encoding="utf8")
        try:
            self.file.symlink_to(real)
        except (NotImplementedError, OSError):
            self.skipTest("symlinks not available")
        with self.assertRaisesRegex(ValueError, "symlinked"):
            load_samples(self.file)

    def test_cumulative_compute_only_still_defines_error_onset(self):
        a, b = row(1, error=0), row(2, error=0)
        b["invalid_compute_kernel_total"] = 7
        result = analyze([a,b], "test")
        self.assertEqual(result["first_observed_render_failure_sample"], 2)
        self.assertEqual(result["fresh_fps_during_or_after_render_error"]["samples"], 1)

    def test_valid_presentation_does_not_equal_unity_fps(self):
        x = analyze([row(1)], "test")
        self.assertIn("not Unity", x["fps_method"])
        self.assertIn("system-wide", x["gpu_busy_attribution"])
        self.assertTrue(x["missing_presentation_does_not_prove_freeze"])


if __name__ == "__main__":
    unittest.main()
