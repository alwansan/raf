"""Regression tests for aggregate physical mouse capture diagnostics."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t4_capture_reader_summary.py"
spec = importlib.util.spec_from_file_location("t4_capture_reader_summary", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CaptureReaderSummaryBoundaryTests(unittest.TestCase):
    def test_exact_marker_not_substring(self):
        result = module.summarize([
            "physical_mouse_captured_action_callbacks_extra left=99",
            "xphysical_mouse_legacy_reader_evidence left=88",
        ])
        self.assertEqual(result["callback_reports"], 0)
        self.assertEqual(result["reader_reports"], 0)
        self.assertEqual(result["diagnostic_state"], "no_callback_marker_observed")

    def test_cumulative_reset_does_not_erase_peak(self):
        result = module.summarize([
            "physical_mouse_captured_action_callbacks left=8; right=3",
            "physical_mouse_captured_action_callbacks left=2; right=3",
            "physical_mouse_legacy_reader_evidence left=1",
        ])
        self.assertEqual(result["last_callback_counters"]["left"], 2)
        self.assertEqual(result["max_callback_counters"]["left"], 8)
        self.assertEqual(result["callback_counter_decreases"], 1)
        self.assertEqual(result["diagnostic_state"], "both_markers_observed_no_gameplay_proof")
        self.assertFalse(result["gameplay_success_proven"])

    def test_concatenated_markers_keep_counters_separate(self):
        result = module.summarize([
            "physical_mouse_captured_action_callbacks left=4 physical_mouse_legacy_reader_evidence right=6",
        ])
        self.assertEqual(result["last_callback_counters"], {"left": 4})
        self.assertEqual(result["last_reader_counters"], {"right": 6})

    def test_missing_reader_marker_is_not_success(self):
        result = module.summarize(["physical_mouse_captured_action_callbacks left=1"])
        self.assertEqual(result["diagnostic_state"], "callbacks_observed_readers_not_observed")
        self.assertFalse(result["gameplay_success_proven"])


if __name__ == "__main__":
    unittest.main()
