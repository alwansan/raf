"""Fail-closed controls for overflowing effective FFT comparison tolerances."""
import struct
import unittest
from scripts.t1_fft_rgba_error_signature import signature


def pixel(x):
    return struct.pack("<4f", x, 0.0, 0.0, 1.0)


class T1ToleranceOverflow(unittest.TestCase):
    def test_finite_tolerance_product_overflow_cannot_certify_parity(self):
        same = pixel(3.4e38)
        report = signature(same, same, atol=0.0, rtol=1e308)
        self.assertFalse(report["all_within_tolerance"])
        self.assertEqual(report["channels"][0]["uninformative_tolerance"], 1)
        self.assertEqual(report["channels"][0]["mismatched"], 1)

    def test_ordinary_relative_tolerance_remains_valid(self):
        same = pixel(3.4e38)
        report = signature(same, same, atol=0.0, rtol=1e-4)
        self.assertTrue(report["all_within_tolerance"])
        self.assertEqual(report["channels"][0]["uninformative_tolerance"], 0)

    def test_overflow_guard_is_per_component(self):
        report = signature(pixel(3.4e38), pixel(-3.4e38), atol=0.0, rtol=1e308)
        self.assertEqual([c["uninformative_tolerance"] for c in report["channels"]], [1, 0, 0, 0])
        self.assertFalse(report["all_within_tolerance"])


if __name__ == "__main__":
    unittest.main()
