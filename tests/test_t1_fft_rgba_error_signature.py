import struct
import unittest
from t1_fft_rgba_error_signature import signature

def pixel(*values):
    return struct.pack("<4f", *values)

class SignatureTests(unittest.TestCase):
    def test_exact(self):
        data = pixel(1, 2, 3, 4)
        result = signature(data, data)
        self.assertTrue(result["all_within_tolerance"])
        self.assertEqual(result["channels"][0]["max_ulp"], 0)

    def test_channel_and_sign(self):
        result = signature(pixel(1, 2, 3, 4), pixel(2, 1, 3, 4), atol=0, rtol=0)
        self.assertEqual([x["mismatched"] for x in result["channels"]], [1, 1, 0, 0])
        self.assertEqual(result["channels"][0]["signed_positive"], 1)
        self.assertEqual(result["channels"][1]["signed_negative"], 1)

    def test_nonfinite(self):
        self.assertEqual(signature(pixel(float("nan"), 0, 0, 0), pixel(1, 0, 0, 0))["channels"][0]["nonfinite"], 1)

    def test_reject_partial(self):
        with self.assertRaises(ValueError):
            signature(b"\\0" * 15, b"\\0" * 15)

    def test_negative_zero(self):
        result = signature(pixel(-0.0, 0, 0, 0), pixel(0, 0, 0, 0))
        self.assertTrue(result["all_within_tolerance"])
        self.assertEqual(result["channels"][0]["max_ulp"], 1)

if __name__ == "__main__":
    unittest.main()
