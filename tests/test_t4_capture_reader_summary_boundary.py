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

    def test_partial_reports_preserve_previous_cumulative_fields(self):
        result = module.summarize([
            "physical_mouse_captured_action_callbacks left=7; right=2; middle=1",
            "physical_mouse_captured_action_callbacks scroll=3",
            "physical_mouse_captured_action_callbacks left=8",
        ])
        self.assertEqual(result["last_callback_counters"],
                         {"left": 8, "right": 2, "middle": 1, "scroll": 3})
        self.assertEqual(result["max_callback_counters"],
                         {"left": 8, "right": 2, "middle": 1, "scroll": 3})
        self.assertEqual(result["callback_counter_decreases"], 0)
        self.assertFalse(result["gameplay_success_proven"])

    def test_first_observation_is_not_mistaken_for_new_action(self):
        result = module.summarize([
            "physical_mouse_captured_action_callbacks left=4; right=2",
            "physical_mouse_legacy_reader_evidence left=10; right=5",
            "physical_mouse_captured_action_callbacks left=5; right=2",
            "physical_mouse_legacy_reader_evidence left=10; right=6",
        ])
        self.assertEqual(result["first_callback_counters"], {"left": 4, "right": 2})
        self.assertEqual(result["first_reader_counters"], {"left": 10, "right": 5})
        self.assertEqual(result["monotonic_callback_increases"], {"left": 1})
        self.assertEqual(result["monotonic_reader_increases"], {"right": 1})
        self.assertFalse(result["gameplay_success_proven"])

    def test_reset_drop_not_counted_as_increase(self):
        result = module.summarize([
            "physical_mouse_legacy_reader_evidence left=9",
            "physical_mouse_legacy_reader_evidence left=2",
            "physical_mouse_legacy_reader_evidence left=4",
        ])
        self.assertEqual(result["monotonic_reader_increases"], {"left": 2})
        self.assertEqual(result["reader_counter_decreases"], 1)
        self.assertFalse(result["gameplay_success_proven"])

    def test_missing_reader_marker_is_not_success(self):
        result = module.summarize(["physical_mouse_captured_action_callbacks left=1"])
        self.assertEqual(result["diagnostic_state"], "callbacks_observed_readers_not_observed")
        self.assertFalse(result["gameplay_success_proven"])


if __name__ == "__main__":
    unittest.main()
