import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("probe", Path(__file__).resolve().parents[1] / "scripts" / "t5_lograft_presented_fps.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

class TestLogRaft(unittest.TestCase):
    def test_missing_and_invalid_not_counted(self):
        out = probe.summarize([{}, {"presented_fps_estimate": 0}, {"presented_fps_estimate": 20}, {"presented_fps_estimate": 30}], expected_session="a")
        self.assertEqual((out["valid_estimates"], out["median_presented_fps_estimate"]), (2, 25))
        self.assertIsNone(out["gpu_frame_ms"])
    def test_never_infer_from_refresh(self):
        self.assertEqual(probe.summarize([{"refresh_hz": 120, "fps": 120}], expected_session="a")["valid_estimates"], 0)
    def test_reject_session_mismatch(self):
        with self.assertRaises(ValueError):
            probe.summarize([{"session_id": "b", "presented_fps_estimate": 20}], expected_session="a")
    def test_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"
            p.write_text('{"presented_fps_estimate":20,"presented_fps_estimate":30}\n')
            with self.assertRaises(ValueError):
                list(probe.load(p))
    def test_original_lograft_quality_gate(self):
        original = {"source": "lograf_shell", "presented_fps_estimate": 33.56,
                    "fps_quality": "surface_presentation_estimate",
                    "fps_tracking_status": "valid_surface_presentation_estimate",
                    "main_process_pid_verified": True,
                    "frame_telemetry_stale": False,
                    "fps_surface": "SurfaceView[com.alwansan.raft.androidtest]"}
        good = probe.summarize([original], expected_session="a")
        self.assertEqual(good["valid_estimates"], 1)
        for changes in ({"fps_quality": "unavailable"},
                        {"fps_tracking_status": "pid_tracking_unverified"},
                        {"main_process_pid_verified": False},
                        {"frame_telemetry_stale": True},
                        {"fps_surface": None},
                        {"fps_surface": " "}):
            with self.subTest(changes=changes):
                bad = probe.summarize([{**original, **changes}], expected_session="a")
                self.assertEqual(bad["valid_estimates"], 0)
                self.assertEqual(bad["rejected"]["unverified_surface_estimate"], 1)

    def test_lograft_requires_quality_fields_not_just_numeric_fps(self):
        row = {"source": "lograf_shell", "presented_fps_estimate": 30}
        self.assertEqual(probe.summarize([row], expected_session="a")["valid_estimates"], 0)
        self.assertEqual(probe.summarize([{"presented_fps_estimate": 30}], expected_session="a")["valid_estimates"], 1)

    def test_empty_samples_not_fabricated(self):
        out = probe.summarize([{}], expected_session="a")
        self.assertIsNone(out["median_presented_fps_estimate"])
        self.assertIsNone(out["p95_presented_fps_estimate"])

if __name__ == "__main__":
    unittest.main()
