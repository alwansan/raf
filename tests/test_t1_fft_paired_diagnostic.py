import unittest

from scripts.t1_fft_paired_diagnostic import diagnose
from scripts.t1_fft_readback_parity import PIXEL, SENTINEL


class PairedDiagnosticTests(unittest.TestCase):
    def test_swap_on_written_pixels_only(self):
        empty = PIXEL.pack(*SENTINEL)
        result = diagnose(PIXEL.pack(1, 2, 3, 4) + empty,
                          PIXEL.pack(2, 1, 3, 4) + empty, 2, 1)
        self.assertEqual(result["channel"]["jointly_written"], 1)
        self.assertTrue(result["channel"]["full_match"])
        self.assertTrue(result["channel"]["permutation_improves"])

    def test_coverage_mismatch_prevents_channel_match(self):
        value = PIXEL.pack(1, 2, 3, 4)
        result = diagnose(value + PIXEL.pack(*SENTINEL), value + value, 2, 1)
        self.assertFalse(result["channel"]["full_match"])

    def test_spatial_can_match_without_joint_coordinates(self):
        value, empty = PIXEL.pack(1, 2, 3, 4), PIXEL.pack(*SENTINEL)
        result = diagnose(value + empty, empty + value, 2, 1)
        self.assertIsNone(result["channel"])
        self.assertTrue(result["spatial"]["flip_x"]["full_match"])
