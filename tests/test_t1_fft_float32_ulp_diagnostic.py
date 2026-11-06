import unittest
from scripts.t1_fft_float32_ulp_diagnostic import ulp32_gap, diagnose

class Float32UlpDiagnosticTests(unittest.TestCase):
    def test_one_ulp_positive(self):
        self.assertEqual(ulp32_gap(1.0, 1.0 + 2**-23), 1)
    def test_one_ulp_negative(self):
        self.assertEqual(ulp32_gap(-1.0, -1.0 - 2**-23), 1)
    def test_signed_zero(self):
        self.assertEqual(ulp32_gap(0.0, -0.0), 0)
    def test_out_of_float32_range(self):
        self.assertIsNone(ulp32_gap(1e300, 1.0))
    def test_diagnostic_first_coordinate_only(self):
        key = (0, 2, 3, "r")
        result = diagnose({key: 1.0}, {key: 1.0 + 2**-23})
        self.assertEqual(result["status"], "different")
        self.assertEqual(result["float32_ulp_gap"], 1)
    def test_missing_has_no_ulp(self):
        result = diagnose({}, {(0, 0, 0, "r"): 1.0})
        self.assertEqual(result["status"], "missing")
        self.assertNotIn("float32_ulp_gap", result)

if __name__ == "__main__":
    unittest.main()
