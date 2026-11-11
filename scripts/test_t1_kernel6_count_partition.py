#!/usr/bin/env python3
"""Regression: sanitized scanner mention partitions must be internally consistent."""
import unittest
from t1_compare_kernel6_sessions import validate

class Kernel6PartitionContract(unittest.TestCase):
    def summary(self, mentions, errors, nonerrors):
        return {
            "session_id": "synthetic", "source_sha256": "a" * 64,
            "original_kernel_identity_proven": False, "sample_errors_only": True,
            "counts": {"kernel6_lines": mentions, "kernel6_error_lines": errors,
                       "kernel6_nonerror_mentions": nonerrors, "water_pass_lines": 0,
                       "findkernel_lines": 0, "dispatch_lines": 0},
            "events": [], "sampled_hits": 0,
        }

    def test_partition_valid(self):
        self.assertEqual(validate(self.summary(3, 0, 3))["counts"]["kernel6_lines"], 3)

    def test_partition_underreported(self):
        with self.assertRaisesRegex(ValueError, "partition"):
            validate(self.summary(3, 1, 1))

    def test_partition_overreported(self):
        with self.assertRaisesRegex(ValueError, "partition"):
            validate(self.summary(3, 2, 2))

    def test_partition_bool_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid counts"):
            validate(self.summary(3, 1, True))

if __name__ == "__main__":
    unittest.main()
