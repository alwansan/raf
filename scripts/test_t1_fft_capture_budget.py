#!/usr/bin/env python3
"""Regression: private FFT comparator must reject oversized aggregate manifests."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "t1_fft_first_divergence.py"

class CaptureBudgetTests(unittest.TestCase):
    def run_manifest(self, entries, root):
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps(entries), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(manifest)],
                              capture_output=True, text=True, timeout=15)

    def test_reject_too_many_passes_before_file_reads(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            entries = [{"name": str(i), "reference": "absent", "observed": "absent"} for i in range(33)]
            result = self.run_manifest(entries, root)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_reject_aggregate_budget_before_capture_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Sparse file: no large payload allocated or read.
            with (root / "big.bin").open("wb") as f:
                f.truncate(64 * 1024 * 1024)
            entries = [{"name": str(i), "reference": "big.bin", "observed": "big.bin"} for i in range(2)]
            result = self.run_manifest(entries, root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Invalid private FFT", result.stderr)

    def test_single_small_matching_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "small.bin").write_bytes(bytes(16))
            result = self.run_manifest([{"name": "fft", "reference": "small.bin",
                                         "observed": "small.bin"}], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["all_match"])

if __name__ == "__main__":
    unittest.main()
