"""Regression tests for conservative T4 aggregate gap classifier."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t4_capture_gap_classifier.py"
spec = importlib.util.spec_from_file_location("t4_capture_gap_classifier", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GapClassifierTests(unittest.TestCase):
    def test_missing_baseline_is_unknown_even_with_callback_growth(self):
        report = {"first_callback_counters": {"left": 1},
                  "monotonic_callback_increases": {"left": 3}}
        self.assertEqual(module.classify(report)["per_counter"]["left"]["state"],
                         "insufficient_paired_baseline")

    def test_callback_only_growth_is_diagnostic_not_proof(self):
        report = {"first_callback_counters": {"left": 0},
                  "first_reader_counters": {"left": 0},
                  "monotonic_callback_increases": {"left": 2}}
        result = module.classify(report)
        self.assertEqual(result["per_counter"]["left"]["state"],
                         "callback_growth_without_reader_growth")
        self.assertFalse(result["gameplay_success_proven"])

    def test_both_growth_still_not_gameplay_proof(self):
        report = {"first_callback_counters": {"scroll": 1},
                  "first_reader_counters": {"scroll": 1},
                  "monotonic_callback_increases": {"scroll": 2},
                  "monotonic_reader_increases": {"scroll": 2}}
        self.assertEqual(module.classify(report)["per_counter"]["scroll"]["state"],
                         "both_grew_no_causal_proof")

    def test_zero_growth_is_not_misclassified_as_dropped(self):
        report = {"first_callback_counters": {"middle": 0},
                  "first_reader_counters": {"middle": 0}}
        self.assertEqual(module.classify(report)["per_counter"]["middle"]["state"],
                         "no_new_growth_observed")


if __name__ == "__main__":
    unittest.main()
