#!/usr/bin/env python3
"""Offline regression for T1 sanitized cross-session comparator."""
import unittest
from t1_compare_kernel6_sessions import compare

def sample(name, sha, line):
    return {"session_id": name, "source_sha256": sha * 64,
            "original_kernel_identity_proven": False, "sample_errors_only": True,
            "counts": {"kernel6_lines": 3, "kernel6_error_lines": 1,
                       "water_pass_lines": 5, "findkernel_lines": 2, "dispatch_lines": 1},
            "events": [{"line": line, "before": [], "after": []}], "sampled_hits": 1}

class CrossSessionTest(unittest.TestCase):
    def test_distinct_scans_and_delta(self):
        a, b = sample("220911-559", "a", 14), sample("230108-327", "b", 19)
        b["counts"]["water_pass_lines"] = 7
        result = compare(a, b)
        self.assertEqual(result["count_deltas_second_minus_first"]["water_pass_lines"], 2)
        self.assertEqual(result["first_error_order"], "not_comparable_across_logs")
        self.assertEqual(result["kernel_identity"], "unproven")

    def test_reject_same_hash(self):
        with self.assertRaises(ValueError):
            compare(sample("a", "a", 1), sample("b", "a", 2))

    def test_reject_same_session(self):
        with self.assertRaises(ValueError):
            compare(sample("a", "a", 1), sample("a", "b", 2))

    def test_reject_non_error_sampling(self):
        a = sample("a", "a", 1)
        a["sample_errors_only"] = False
        with self.assertRaises(ValueError):
            compare(a, sample("b", "b", 2))

    def test_reject_invalid_order(self):
        a = sample("a", "a", 2)
        a["events"].append({"line": 1, "before": [], "after": []})
        a["sampled_hits"] = 2
        with self.assertRaises(ValueError):
            compare(a, sample("b", "b", 3))

if __name__ == "__main__":
    unittest.main()
