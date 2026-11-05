import struct
import unittest
from scripts.t1_fft_first_divergence import compare_passes

def pixel(*values):
    return struct.pack("<4f", *values)

class FirstDivergenceTests(unittest.TestCase):
    def test_first_mismatch_after_matching_pass(self):
        a = pixel(1, 2, 3, 4)
        b = pixel(1, 2, 9, 4)
        result = compare_passes([("input", a, a), ("pass0", a, b), ("pass1", b, b)])
        self.assertEqual(result["first_divergence"], {"index": 1, "pass": "pass0"})
        self.assertEqual(result["passes"][1]["mismatch_by_channel"], [0, 0, 1, 0])
    def test_all_equal(self):
        a = pixel(1, 2, 3, 4)
        self.assertTrue(compare_passes([("p", a, a)])["all_match"])
    def test_nonfinite_is_failure(self):
        a = pixel(1, 2, 3, 4)
        b = pixel(float("nan"), 2, 3, 4)
        self.assertEqual(compare_passes([("p", a, b)])["passes"][0]["nonfinite_by_channel"][0], 1)
    def test_empty_and_duplicate_rejected(self):
        a = pixel(1, 2, 3, 4)
        with self.assertRaises(ValueError):
            compare_passes([])
        with self.assertRaises(ValueError):
            compare_passes([("p", a, a), ("p", a, a)])
        with self.assertRaises(ValueError):
            compare_passes([("p", b"", b"")])
    def test_invalid_tolerance_rejected(self):
        a = pixel(1, 2, 3, 4)
        with self.assertRaises(ValueError):
            compare_passes([("p", a, a)], atol=float("nan"))
if __name__ == "__main__":
    unittest.main()
