#!/usr/bin/env python3
"""Synthetic, no game data."""
import unittest
from t1_fft_pass_proximity import summarize

def sample(events):
    return {"session_id": "synthetic", "source_sha256": "a"*64,
            "sample_errors_only": True, "original_kernel_identity_proven": False,
            "events": events}

class TestPassProximity(unittest.TestCase):
    def test_same_line_precedes_nearby(self):
        result = summarize(sample([{"line": 20, "pass_tokens": ["Spectrum"],
            "before": [{"line": 19, "markers": ["pass:foam"]}], "after": []}]))
        self.assertEqual(result["nearest_pass_bins"][0]["direction"], "same_line")
        self.assertEqual(result["nearest_pass_bins"][0]["pass"], "spectrum")
        self.assertEqual(result["causality"], "not_established")

    def test_distance_and_unmatched(self):
        result = summarize(sample([
            {"line": 10, "pass_tokens": [], "before": [{"line": 6, "markers": ["pass:foam"]}],
             "after": [{"line": 11, "markers": ["pass:spectrum"]}]},
            {"line": 30, "pass_tokens": [], "before": [], "after": []}]))
        self.assertEqual(result["nearest_pass_bins"][0]["line_distance"], 1)
        self.assertEqual(result["nearest_pass_bins"][0]["direction"], "after")
        self.assertEqual(result["unmatched_sampled_errors"], 1)

    def test_invalid_context_direction(self):
        with self.assertRaises(ValueError):
            summarize(sample([{"line": 5, "pass_tokens": [], "before":
                [{"line": 6, "markers": ["pass:foam"]}], "after": []}]))

    def test_unknown_marker_rejected(self):
        with self.assertRaises(ValueError):
            summarize(sample([{"line": 5, "pass_tokens": [], "before":
                [{"line": 4, "markers": ["pass:secret"]}], "after": []}]))

    def test_reject_non_error_sampling(self):
        with self.assertRaises(ValueError):
            summarize({"sample_errors_only": False, "original_kernel_identity_proven": False, "events": []})

if __name__ == "__main__":
    unittest.main()
