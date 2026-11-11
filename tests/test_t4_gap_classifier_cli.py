"""Black-box CLI regressions for T4 physical-mouse evidence classification.

These are source-only tests, not evidence that a physical mouse works in Raft.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t4_capture_gap_classifier.py"


class GapClassifierCliTests(unittest.TestCase):
    def run_summary(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, timeout=15, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(completed.stdout)

    def test_reset_never_reports_paired_growth(self):
        report = {
            "first_callback_counters": {"left": 0},
            "first_reader_counters": {"left": 0},
            "monotonic_callback_increases": {"left": 9},
            "monotonic_reader_increases": {"left": 9},
            "callback_counter_decreases": 1,
        }
        result = self.run_summary(report)
        self.assertEqual(
            result["per_counter"]["left"]["state"],
            "counter_reset_requires_epoch_segmentation",
        )
        self.assertIs(result["gameplay_success_proven"], False)

    def test_malformed_root_is_fail_closed_at_cli_boundary(self):
        for payload in (None, [], "not-a-report"):
            with self.subTest(payload=payload):
                result = self.run_summary(payload)
                self.assertEqual(
                    result["per_counter"]["left"]["state"],
                    "invalid_counter_evidence",
                )
                self.assertIs(result["gameplay_success_proven"], False)

    def test_valid_aggregate_still_never_claims_gameplay(self):
        report = {
            "first_callback_counters": {"scroll": 0},
            "first_reader_counters": {"scroll": 0},
            "monotonic_callback_increases": {"scroll": 2},
            "monotonic_reader_increases": {"scroll": 2},
        }
        result = self.run_summary(report)
        self.assertEqual(
            result["per_counter"]["scroll"]["state"],
            "both_grew_no_causal_proof",
        )
        self.assertIs(result["gameplay_success_proven"], False)


if __name__ == "__main__":
    unittest.main()
