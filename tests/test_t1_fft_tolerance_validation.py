"""Regression: FFT numeric comparator must fail closed for invalid API tolerances."""
import math
import struct
import unittest

from scripts.t1_fft_rgba_error_signature import signature


def pixel(value):
    return struct.pack("<4f", value, 0.0, 0.0, 1.0)


class T1ToleranceValidation(unittest.TestCase):
    def test_rejects_nonfinite_and_negative_tolerances(self):
        for field in ("atol", "rtol"):
            for bad in (float("nan"), float("inf"), -float("inf"), -1.0):
                with self.subTest(field=field, value=repr(bad)):
                    kwargs = {field: bad}
                    with self.assertRaises(ValueError):
                        signature(pixel(0.0), pixel(1.0), **kwargs)

    def test_zero_tolerance_detects_finite_difference(self):
        report = signature(pixel(0.0), pixel(1.0), atol=0.0, rtol=0.0)
        self.assertFalse(report["all_within_tolerance"])
        self.assertEqual(report["channels"][0]["mismatched"], 1)

    def test_valid_positive_tolerance_can_accept_difference(self):
        report = signature(pixel(0.0), pixel(1.0), atol=1.0, rtol=0.0)
        self.assertTrue(report["all_within_tolerance"])


if __name__ == "__main__":
    unittest.main()
