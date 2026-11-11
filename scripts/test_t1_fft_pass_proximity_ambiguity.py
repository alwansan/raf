#!/usr/bin/env python3
"""Regression: nearest water-pass evidence must not be fabricated on ties."""
import unittest
from t1_fft_pass_proximity import summarize

def scan(events):
    return {
        "session_id": "device-42058825739-synthetic",
        "source_sha256": "a" * 64,
        "sample_errors_only": True,
        "original_kernel_identity_proven": False,
        "events": events,
    }

class TestNearestPassAmbiguity(unittest.TestCase):
    def test_distinct_passes_same_line(self):
        result = summarize(scan([{"line": 10, "pass_tokens": ["foam", "spectrum"]}]))
        self.assertEqual(result["errors_with_nearby_pass_marker"], 0)
        self.assertEqual(result["ambiguous_nearest_pass_errors"], 1)
        self.assertEqual(result["unmatched_sampled_errors"], 0)
        self.assertEqual({c["pass"] for c in result["ambiguous_nearest_bins"][0]["candidates"]}, {"foam", "spectrum"})

    def test_same_pass_duplicate_is_unique(self):
        result = summarize(scan([{"line": 10, "pass_tokens": ["foam", "foam"]}]))
        self.assertEqual(result["errors_with_nearby_pass_marker"], 1)
        self.assertEqual(result["ambiguous_nearest_pass_errors"], 0)

    def test_equal_distance_before_after_is_ambiguous(self):
        result = summarize(scan([{"line": 10,
            "before": [{"line": 9, "markers": ["pass:foam"]}],
            "after": [{"line": 11, "markers": ["pass:foam"]}]}]))
        self.assertEqual(result["ambiguous_nearest_pass_errors"], 1)

    def test_nearer_marker_wins(self):
        result = summarize(scan([{"line": 10,
            "before": [{"line": 9, "markers": ["pass:foam"]}],
            "after": [{"line": 13, "markers": ["pass:spectrum"]}]}]))
        self.assertEqual(result["errors_with_nearby_pass_marker"], 1)
        self.assertEqual(result["nearest_pass_bins"][0]["pass"], "foam")

    def test_no_marker_is_unmatched(self):
        result = summarize(scan([{"line": 10}]))
        self.assertEqual(result["unmatched_sampled_errors"], 1)
        self.assertEqual(result["ambiguous_nearest_pass_errors"], 0)

if __name__ == "__main__":
    unittest.main()
