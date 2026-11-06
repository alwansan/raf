"""T5 process-epoch isolation regression tests."""
import unittest
from scripts.t5_cl_pid_epoch_audit import audit, split_verified_pid_epochs


def sample(n, pid=42, status="main_pid_verified"):
    return {"sample": n, "state": "game_running", "pid": pid,
            "pid_probe_status": status, "fps_quality": "surface_presentation_estimate",
            "fps_tracking_status": "valid_surface_presentation_estimate",
            "frame_telemetry_stale": False, "fps_valid_sample_count": n,
            "presented_frame_window_count": 10,
            "last_present_progress_age_ms": 100,
            "presented_fps_estimate": 22.0}


class EpochTests(unittest.TestCase):
    def test_same_pid_stays_one_epoch(self):
        result = audit([sample(1), sample(2)])
        self.assertEqual(result["process_epoch_count"], 1)
        self.assertTrue(result["safe_to_aggregate_entire_session"])

    def test_restart_cannot_mix_fps(self):
        result = audit([sample(1), sample(2), sample(3, 99)])
        self.assertEqual(result["process_epoch_count"], 2)
        self.assertFalse(result["safe_to_aggregate_entire_session"])
        self.assertEqual([x["fresh_presentation_samples"] for x in result["epochs"]], [2, 1])
        self.assertNotIn("42", str(result))
        self.assertNotIn("99", str(result))

    def test_unknown_pid_breaks_cohort(self):
        result = audit([sample(1), sample(2, None, "pid_tracking_lost_unverified"),
                        sample(3)])
        self.assertEqual(result["process_epoch_count"], 3)
        self.assertFalse(result["safe_to_aggregate_entire_session"])

    def test_stop_restart_same_numeric_pid_is_not_one_lifetime(self):
        stopped = {"state": "game_not_running", "pid": None,
                   "pid_probe_status": "game_not_running"}
        result = audit([sample(1), stopped, sample(2)])
        self.assertEqual(result["process_epoch_count"], 3)
        self.assertFalse(result["safe_to_aggregate_entire_session"])
        self.assertEqual([e["fresh_presentation_samples"] for e in result["epochs"]], [1, 0, 1])

    def test_stop_restart_different_pid_is_not_merged(self):
        stopped = {"state": "game_not_running", "pid": None}
        result = audit([sample(1), stopped, sample(2, 99)])
        self.assertEqual(result["process_epoch_count"], 3)
        self.assertFalse(result["safe_to_aggregate_entire_session"])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            split_verified_pid_epochs([])


if __name__ == "__main__":
    unittest.main()
