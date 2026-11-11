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
                  "monotonic_callback_increases": {"left": 2},
                  "monotonic_reader_increases": {"left": 0}}
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
                  "first_reader_counters": {"middle": 0},
                  "monotonic_callback_increases": {"middle": 0},
                  "monotonic_reader_increases": {"middle": 0}}
        self.assertEqual(module.classify(report)["per_counter"]["middle"]["state"],
                         "no_new_growth_observed")


    def test_missing_growth_is_unknown_not_measured_zero(self):
        report = {"first_callback_counters": {"left": 0},
                  "first_reader_counters": {"left": 0},
                  "monotonic_callback_increases": {"left": 2}}
        self.assertEqual(module.classify(report)["per_counter"]["left"]["state"],
                         "insufficient_paired_baseline")

    def test_malformed_telemetry_section_rejected_without_crash(self):
        report = {"first_callback_counters": {"left": 0},
                  "first_reader_counters": {"left": 0},
                  "monotonic_callback_increases": None,
                  "monotonic_reader_increases": {"left": 0}}
        self.assertEqual(module.classify(report)["per_counter"]["left"]["state"],
                         "invalid_counter_evidence")

    def test_malformed_root_is_invalid_not_exception(self):
        for root in (None, [], "corrupt", 42):
            with self.subTest(root=root):
                result = module.classify(root)
                self.assertFalse(result["gameplay_success_proven"])
                self.assertEqual(result["per_counter"]["left"]["state"],
                                 "invalid_counter_evidence")

    def test_negative_growth_rejected(self):
        report = {"first_callback_counters": {"left": 0},
                  "first_reader_counters": {"left": 0},
                  "monotonic_callback_increases": {"left": -2}}
        self.assertEqual(module.classify(report)["per_counter"]["left"]["state"],
                         "invalid_counter_evidence")

    def test_boolean_growth_rejected(self):
        report = {"first_callback_counters": {"right": 0},
                  "first_reader_counters": {"right": 0},
                  "monotonic_callback_increases": {"right": True}}
        self.assertEqual(module.classify(report)["per_counter"]["right"]["state"],
                         "invalid_counter_evidence")

    def test_string_growth_rejected_without_type_error(self):
        report = {"first_callback_counters": {"middle": 0},
                  "first_reader_counters": {"middle": 0},
                  "monotonic_reader_increases": {"middle": "3"}}
        self.assertEqual(module.classify(report)["per_counter"]["middle"]["state"],
                         "invalid_counter_evidence")

    def test_invalid_baseline_rejected(self):
        report = {"first_callback_counters": {"scroll": -1},
                  "first_reader_counters": {"scroll": 0},
                  "monotonic_callback_increases": {"scroll": 3}}
        self.assertEqual(module.classify(report)["per_counter"]["scroll"]["state"],
                         "invalid_counter_evidence")

    def test_counter_reset_blocks_false_paired_growth(self):
        report = {"first_callback_counters": {"left": 0},
                  "first_reader_counters": {"left": 0},
                  "monotonic_callback_increases": {"left": 4},
                  "monotonic_reader_increases": {"left": 2},
                  "callback_counter_decreases": 1,
                  "reader_counter_decreases": 0}
        result = module.classify(report)
        self.assertEqual(result["per_counter"]["left"]["state"],
                         "counter_reset_requires_epoch_segmentation")
        self.assertFalse(result["gameplay_success_proven"])

    def test_reader_reset_also_blocks_comparison(self):
        report = {"first_callback_counters": {"scroll": 0},
                  "first_reader_counters": {"scroll": 0},
                  "monotonic_callback_increases": {"scroll": 2},
                  "monotonic_reader_increases": {"scroll": 1},
                  "reader_counter_decreases": 1}
        self.assertEqual(module.classify(report)["per_counter"]["scroll"]["state"],
                         "counter_reset_requires_epoch_segmentation")

    def test_malformed_reset_metadata_rejected(self):
        for bad in (-1, True, "1", None, 1.5):
            with self.subTest(bad=bad):
                result = module.classify({"callback_counter_decreases": bad})
                self.assertEqual(result["per_counter"]["left"]["state"],
                                 "invalid_counter_evidence")


if __name__ == "__main__":
    unittest.main()
