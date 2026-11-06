import unittest
from scripts.t1_fft_carrier_report_shape import parse_report


def report(values=None):
    values = [0] * 10 if values is None else values
    return ("\n".join(map(str, values)) + "\n").encode("ascii")


class CarrierReportShapeTests(unittest.TestCase):
    def test_valid_zero(self):
        self.assertTrue(parse_report(report())["positive_controls_pass"])

    def test_noncontrol_difference_is_visible(self):
        v = [0] * 10
        v[1] = 63
        parsed = parse_report(report(v))
        self.assertEqual(parsed["noncontrol_mismatch_categories"], 1)
        self.assertFalse(parsed["gpu_execution_verified"])

    def test_positive_control_fails(self):
        v = [0] * 10
        v[3] = 1
        self.assertFalse(parse_report(report(v))["positive_controls_pass"])

    def test_bad_inputs(self):
        for bad in [b"", b"0\n" * 9, b"0\n" * 11, b"0\r\n" * 10,
                    b"00\n" * 10, b"-1\n" * 10, b"65\n" * 10,
                    b"0\n" * 9 + b"1", b"0\n" * 9 + b"1.0\n",
                    b"0\n" * 9 + b"\xff\n", b"0" * 513]:
            with self.subTest(bad=bad[:25]):
                with self.assertRaises(ValueError):
                    parse_report(bad)


if __name__ == "__main__":
    unittest.main()
