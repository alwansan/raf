#!/usr/bin/env python3
"""Regression for repeated error-line samples in sanitized FFT scans."""
import unittest
from t1_fft_pass_proximity import summarize

BASE = {
    "sample_errors_only": True,
    "original_kernel_identity_proven": False,
    "session_id": "device-42058825739-sample",
    "source_sha256": "a" * 64,
}

class SampleLineIdentityTests(unittest.TestCase):
    def test_distinct_lines_are_counted(self):
        scan = dict(BASE, events=[
            {"line": 12, "pass_tokens": ["spectrum"]},
            {"line": 19, "pass_tokens": ["foam"]},
        ])
        self.assertEqual(summarize(scan)["sampled_errors"], 2)

    def test_duplicate_line_rejected_even_with_different_markers(self):
        scan = dict(BASE, events=[
            {"line": 12, "pass_tokens": ["spectrum"]},
            {"line": 12, "pass_tokens": ["foam"]},
        ])
        with self.assertRaisesRegex(ValueError, "duplicate sampled error line"):
            summarize(scan)

    def test_nonadjacent_duplicate_rejected(self):
        scan = dict(BASE, events=[
            {"line": 12, "pass_tokens": []},
            {"line": 15, "pass_tokens": []},
            {"line": 12, "pass_tokens": []},
        ])
        with self.assertRaisesRegex(ValueError, "duplicate sampled error line"):
            summarize(scan)

if __name__ == "__main__":
    unittest.main()
