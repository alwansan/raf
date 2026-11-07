#!/usr/bin/env python3
"""Regression: first FFT mismatch must be chosen by trace key, not mismatch kind."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("t1_fft_trace_first_divergence_7c3a.py")
spec = importlib.util.spec_from_file_location("t1_fft_first_divergence", MODULE)
fft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fft)

def row(invocation, coordinate, value):
    return dict(source_sha="vulkan-program", fixture_sha256="fixture",
                input_sha256="input", kernel="FFT", dispatch=[1, 1, 1],
                **{"pass": 0}, invocation=invocation, read_site=0,
                coordinate=coordinate, value=value)

class FirstMismatchOrder(unittest.TestCase):
    def test_numeric_before_later_coordinate(self):
        a = [row(0, [0, 0], [1.0]), row(1, [1, 0], [2.0])]
        b = [row(0, [0, 0], [1.5]), row(1, [9, 0], [2.0])]
        self.assert_pair(a, b, "numeric_mismatch", [0, 0, 0])

    def test_coordinate_before_later_numeric(self):
        a = [row(0, [0, 0], [1.0]), row(1, [1, 0], [2.0])]
        b = [row(0, [9, 0], [1.0]), row(1, [1, 0], [2.5])]
        self.assert_pair(a, b, "coordinate_mismatch", [0, 0, 0])

    def assert_pair(self, a, b, expected, key):
        for x in b:
            x["source_sha"] = "unity-program"
        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / "vulkan.jsonl", Path(directory) / "unity.jsonl"
            left.write_text("".join(json.dumps(x) + "\n" for x in a), encoding="utf-8")
            right.write_text("".join(json.dumps(x) + "\n" for x in b), encoding="utf-8")
            result = fft.compare(left, right)
        self.assertEqual(result["status"], expected)
        self.assertEqual(list(result["key"]), key)

if __name__ == "__main__":
    unittest.main()
