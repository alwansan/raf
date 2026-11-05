"""Fail-closed FFT RGBA32F evidence controls; no game assets required."""
import struct
import unittest

from scripts.t1_fft_rgba_error_signature import signature
from scripts.t1_fft_first_divergence import compare_passes


class EmptyCaptureGuardTests(unittest.TestCase):
    def test_empty_both_inputs_are_not_parity(self):
        with self.assertRaisesRegex(ValueError, "at least one pixel"):
            signature(b"", b"")

    def test_empty_against_valid_capture_is_rejected(self):
        pixel = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
        with self.assertRaises(ValueError):
            signature(b"", pixel)

    def test_one_identical_pixel_still_matches(self):
        pixel = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
        report = signature(pixel, pixel)
        self.assertEqual(report["pixels"], 1)
        self.assertTrue(report["all_within_tolerance"])

    def test_one_different_pixel_is_not_parity(self):
        a = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
        b = struct.pack("<4f", 9.0, 2.0, 3.0, 4.0)
        self.assertFalse(signature(a, b)["all_within_tolerance"])

    def test_first_divergence_rejects_empty_capture(self):
        with self.assertRaisesRegex(ValueError, "empty capture"):
            compare_passes([("pass0", b"", b"")])


if __name__ == "__main__":
    unittest.main()
