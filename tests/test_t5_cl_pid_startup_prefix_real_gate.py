"""Source-only CL prefix-vs-restart guard. Synthetic records, no original PIDs."""
import unittest
from scripts.t5_cl_pid_epoch_audit import audit
from scripts.t5_cl_fps_cohort_gate import analyze


def row(i, state="game_running"):
    running = state == "game_running"
    return {
        "sample": i, "timestamp_unix_ms": 1700000000000 + i*3000,
        "state": state, "pid": 42 if running else None,
        "pid_probe_status": "main_pid_verified" if running else "unknown",
        "fps_quality": "surface_presentation_estimate",
        "fps_tracking_status": "valid_surface_presentation_estimate",
        "frame_telemetry_stale": False, "fps_valid_sample_count": i,
        "presented_frame_window_count": 10, "last_present_progress_age_ms": 100,
        "presented_fps_estimate": 23.0,
    }


class RealCLStartupBoundaryTests(unittest.TestCase):
    def test_original_one_and_six_unknown_leading_samples(self):
        for n in (1, 6):
            with self.subTest(leading_unknown=n):
                rows = [row(i, "game_process_state_unknown") for i in range(1, n+1)]
                rows += [row(n+1), row(n+2)]
                state = audit(rows)
                self.assertEqual(state["process_epoch_count"], 1)
                self.assertTrue(state["safe_to_aggregate_entire_session"])
                cohort = analyze(rows, "synthetic")
                self.assertEqual(cohort["process_epoch_count"], 1)
                self.assertEqual(cohort["fresh_surface_fps_all"]["samples"], 2)

    def test_actual_stop_and_reused_pid_always_splits(self):
        rows = [row(1), row(2, "game_not_running"), row(3)]
        state = audit(rows)
        self.assertEqual(state["process_epoch_count"], 3)
        self.assertFalse(state["safe_to_aggregate_entire_session"])
        self.assertIsNone(analyze(rows, "synthetic")["fresh_surface_fps_all"])

    def test_unknown_prefix_then_real_stop_remains_unsafe(self):
        rows = [row(1, "game_process_state_unknown"), row(2),
                row(3, "game_not_running"), row(4)]
        state = audit(rows)
        self.assertEqual(state["process_epoch_count"], 3)
        self.assertFalse(state["safe_to_aggregate_entire_session"])

    def test_unknown_running_pid_breaks_verified_cohort(self):
        rows = [row(1), row(2), row(3)]
        rows[1].update({"pid": None, "pid_probe_status": "pid_tracking_lost_unverified"})
        self.assertEqual(audit(rows)["process_epoch_count"], 3)
        self.assertFalse(audit(rows)["safe_to_aggregate_entire_session"])

    def test_unknown_state_after_verified_pid_is_not_startup_prefix(self):
        # The startup exception is valid only BEFORE the first verified PID.
        # Unknown process state after verification may hide a stop/restart,
        # even if Android later reuses the same numeric PID.
        rows = [row(1), row(2, "game_process_state_unknown"), row(3)]
        state = audit(rows)
        self.assertEqual(state["process_epoch_count"], 3)
        self.assertFalse(state["safe_to_aggregate_entire_session"])
        self.assertIsNone(analyze(rows, "synthetic")["fresh_surface_fps_all"])

    def test_never_verified_process_is_not_eligible(self):
        state = audit([row(1, "game_process_state_unknown")])
        self.assertFalse(state["safe_to_aggregate_entire_session"])


if __name__ == "__main__":
    unittest.main()
