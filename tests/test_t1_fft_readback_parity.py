import math
from pathlib import Path
import tempfile
import unittest

from scripts.t1_fft_readback_parity import PIXEL, SENTINEL, compare_captures, compare_pass


class ReadbackParityTest(unittest.TestCase):
    def test_tolerance_and_untouched_pixel(self):
        untouched = PIXEL.pack(*SENTINEL)
        expected = PIXEL.pack(1, 2, 3, 4) + untouched
        actual = PIXEL.pack(1.00001, 2, 3, 4) + untouched
        self.assertTrue(compare_pass(expected, actual)["match"])
        self.assertFalse(compare_pass(untouched, untouched)["match"])

    def test_coverage_nonfinite_and_channel_error(self):
        pixel = PIXEL.pack(1, 2, 3, 4)
        for actual, field in (
            (PIXEL.pack(*SENTINEL), "write_coverage_mismatch_pixels"),
            (PIXEL.pack(1, 2, math.nan, 4), "nonfinite_pixels"),
            (PIXEL.pack(1, 2, 3, 5), "outside_tolerance_pixels"),
        ):
            with self.subTest(field=field):
                result = compare_pass(pixel, actual)
                self.assertFalse(result["match"])
                self.assertEqual(result[field], 1)

    def test_capture_requires_same_input_and_both_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            reference = Path(temp) / "reference"
            candidate = Path(temp) / "candidate"
            for directory in (reference, candidate):
                directory.mkdir()
                for name in ("source", "butterfly", "pass0", "pass1"):
                    (directory / (name + ".rgba32f")).write_bytes(PIXEL.pack(1, 2, 3, 4))
            self.assertTrue(compare_captures(reference, candidate, 1, 1)["both_passes_match"])
            (candidate / "pass0.rgba32f").write_bytes(PIXEL.pack(2, 2, 3, 4))
            self.assertFalse(compare_captures(reference, candidate, 1, 1)["both_passes_match"])
            (candidate / "butterfly.rgba32f").write_bytes(PIXEL.pack(2, 2, 3, 4))
            with self.assertRaises(ValueError):
                compare_captures(reference, candidate, 1, 1)
            (candidate / "butterfly.rgba32f").write_bytes(b"short")
            with self.assertRaises(ValueError):
                compare_captures(reference, candidate, 1, 1)
