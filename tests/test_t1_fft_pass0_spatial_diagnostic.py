import unittest

from scripts.t1_fft_pass0_spatial_diagnostic import PIXEL, SENTINEL, analyze


def image(*values):
    return b"".join(PIXEL.pack(*(SENTINEL if v is None else (v, v + 1, v + 2, v + 3)))
                    for v in values)


class SpatialDiagnosticTests(unittest.TestCase):
    def test_sparse_row_flip(self):
        expected = image(1, 2, None, None, None, None)
        candidate = image(None, None, None, 1, 2, None)
        report = analyze(expected, candidate, 3, 2)
        self.assertTrue(report["flip_y"]["full_match"])
        self.assertEqual(report["identity"]["coverage_mismatches"], 4)

    def test_horizontal_reversal_with_identical_coverage(self):
        report = analyze(image(1, 2, 3), image(3, 2, 1), 3, 1)
        self.assertEqual(report["identity"]["coverage_mismatches"], 0)
        self.assertEqual(report["identity"]["numeric_mismatches"], 2)
        self.assertTrue(report["flip_x"]["full_match"])

    def test_shift_cannot_hide_extra_edge_write(self):
        report = analyze(image(1, None, None), image(7, 1, None), 3, 1)
        shift = report["shift_x_minus_one"]
        self.assertEqual(shift["jointly_written"], 1)
        self.assertEqual(shift["coverage_mismatches"], 1)
        self.assertFalse(shift["full_match"])

    def test_rejects_empty_bad_shape_and_nonfinite(self):
        with self.assertRaises(ValueError):
            analyze(image(None), image(None), 1, 1)
        with self.assertRaises(ValueError):
            analyze(image(1), image(1), 2, 1)
        result = analyze(image(1), image(float("inf")), 1, 1)["identity"]
        self.assertEqual(result["nonfinite_pixels"], 1)
        self.assertFalse(result["full_match"])
