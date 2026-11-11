#!/usr/bin/env python3
"""End-to-end sanitized FFT log pipeline contract; synthetic data only."""
import json
import tempfile
import unittest
from pathlib import Path

from t1_kernel6_log_context import scan
from t1_compare_kernel6_sessions import compare


class Kernel6PipelineEndToEnd(unittest.TestCase):
    def test_independent_logs_and_privacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "220911.log"
            second = Path(tmp) / "230108.log"
            secret = "PRIVATE_SYNTHETIC_PAYLOAD_DO_NOT_EXPORT"
            first.write_text(
                "FindKernel " + secret + "\n"
                + "ordinary filler\n" * 9
                + "ultimate_water_invalid_pass Spectrum\n"
                + "invalid kernel index (6) " + secret + "\n"
                + "Dispatch\n"
                + "kernel 16 invalid\n"
                + "kernel index 6.1 invalid\n",
                encoding="utf-8",
            )
            second.write_text(
                "FindKernel\n"
                + "invalid kernel #6 " + secret + "\n"
                + "ultimate_water_invalid_pass Foam\n"
                + "invalid kernel 6 " + secret + "\n"
                + "Dispatch\n",
                encoding="utf-8",
            )
            a = scan(first, "220911-559", before=2, after=2,
                     max_hits=10, errors_only=True)
            b = scan(second, "230108-327", before=2, after=2,
                     max_hits=10, errors_only=True)
            self.assertEqual(a["counts"]["kernel6_error_lines"], 1)
            self.assertEqual(b["counts"]["kernel6_error_lines"], 2)
            self.assertEqual(a["counts"]["water_pass_lines"], 1)
            self.assertEqual(b["counts"]["water_pass_lines"], 1)
            self.assertEqual(a["sampled_hits"], 1)
            self.assertEqual(b["sampled_hits"], 2)
            self.assertEqual(a["events"][0]["before"], [])
            self.assertEqual(a["events"][0]["after"][0]["markers"], ["Dispatch"])
            result = compare(a, b)
            self.assertEqual(result["count_deltas_second_minus_first"]["kernel6_error_lines"], 1)
            self.assertEqual(result["kernel_identity"], "unproven")
            self.assertEqual(result["causality"], "not_established")
            self.assertEqual(result["first_error_order"], "not_comparable_across_logs")
            self.assertNotEqual(result["inputs"][0]["source_sha256"],
                                result["inputs"][1]["source_sha256"])
            self.assertNotIn(secret, json.dumps({"scans": [a, b], "comparison": result}))

    def test_identical_bytes_rejected_despite_different_session_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "same.log"
            path.write_text("invalid kernel #6\n", encoding="utf-8")
            a = scan(path, "first", errors_only=True)
            b = scan(path, "second", errors_only=True)
            with self.assertRaisesRegex(ValueError, "identical log bytes"):
                compare(a, b)


if __name__ == "__main__":
    unittest.main()
