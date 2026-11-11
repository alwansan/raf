#!/usr/bin/env python3
"""Regression: kernel index 6 must not absorb decimal/suffixed indices."""
import unittest
from t1_kernel6_log_context import KERNEL6


class KernelSixLexicalBoundary(unittest.TestCase):
    def test_canonical_forms(self):
        for value in ("kernel 6", "kernel #6", "kernel index (6)",
                      "kernel index:6", "kernel=6", "KERNEL INDEX 6:"):
            with self.subTest(value=value):
                self.assertIsNotNone(KERNEL6.search(value))

    def test_noninteger_or_prefixed_forms(self):
        for value in ("kernel 6.0", "kernel index 6.1", "kernel #6.25",
                      "kernel 60", "kernel 6_extra", "subkernel #6"):
            with self.subTest(value=value):
                self.assertIsNone(KERNEL6.search(value))


if __name__ == "__main__":
    unittest.main()
