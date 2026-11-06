import json
import tempfile
import unittest
from pathlib import Path
from scripts.t1_fft_coordinate_probe_compare import read_samples, first_difference, MAX_CAPTURE_BYTES, MAX_SAMPLES

class CoordinateProbeTests(unittest.TestCase):
    def test_first_pass(self):
        a = {(2, 0, 0, "r"): 1., (0, 0, 0, "r"): 2.}
        b = {(2, 0, 0, "r"): 4., (0, 0, 0, "r"): 3.}
        self.assertEqual(first_difference(a, b)["pass"], 0)
    def test_both_empty_captures_do_not_match(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            first_difference({}, {})

    def test_missing_not_numeric(self):
        self.assertEqual(first_difference({}, {(0, 0, 0, "r"): 1.})["status"], "missing")
    def test_tolerance(self):
        self.assertEqual(first_difference({(0, 0, 0, "r"): 1.}, {(0, 0, 0, "r"): 1.0000001})["status"], "match")
    def test_duplicate_sample(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"data.json"
            row = {"pass": 0, "x": 0, "y": 0, "channel": "r", "value": 1}
            path.write_text(json.dumps({"samples": [row, row]}))
            with self.assertRaisesRegex(ValueError, "duplicate sample"):
                read_samples(path)
    def test_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"data.json"
            path.write_text('{"samples":[{"pass":0,"x":0,"y":0,"channel":"r","value":NaN}]}')
            with self.assertRaises(ValueError):
                read_samples(path)
    def test_duplicate_json_field(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"data.json"
            path.write_text('{"samples":[],"samples":[]}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                read_samples(path)
    def test_integer_float_overflow_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"overflow.json"
            path.write_text(json.dumps({"samples": [{"pass": 0, "x": 0, "y": 0, "channel": "r", "value": 10 ** 400}]}))
            with self.assertRaisesRegex(ValueError, "invalid value"):
                read_samples(path)
    def test_capture_byte_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"huge.json"
            path.write_bytes(b" " * (MAX_CAPTURE_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "size limit"):
                read_samples(path)
    def test_capture_sample_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"many.json"
            row = {"pass": 0, "x": 0, "y": 0, "channel": "r", "value": 1}
            path.write_text(json.dumps({"samples": [row] * (MAX_SAMPLES + 1)}))
            with self.assertRaisesRegex(ValueError, "sample limit"):
                read_samples(path)
    def test_capture_limit_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"boundary.json"
            path.write_text(json.dumps({"samples": [{"pass": 0, "x": 0, "y": 0, "channel": "r", "value": 1}]}))
            self.assertEqual(len(read_samples(path)), 1)
if __name__ == "__main__":
    unittest.main()
