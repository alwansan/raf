#!/usr/bin/env python3
"""Regression: private FFT comparator must reject oversized aggregate manifests."""
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "t1_fft_first_divergence.py"

class CaptureBudgetTests(unittest.TestCase):
    def run_manifest(self, entries, root):
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps(entries), encoding="utf-8")
        return subprocess.run([sys.executable, "-m", "scripts.t1_fft_first_divergence", str(manifest)],
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
            (root / "reference.bin").write_bytes(bytes(16))
            (root / "observed.bin").write_bytes(bytes(16))
            result = self.run_manifest([{"name": "fft", "reference": "reference.bin",
                                         "observed": "observed.bin"}], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["all_match"])

    def test_later_oversize_is_rejected_before_any_capture_read(self):
        # A late pass must not cause the first pass to be loaded into RAM.
        from scripts import t1_fft_first_divergence as comparator
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "small.bin").write_bytes(bytes(16))
            with (root / "big.bin").open("wb") as f:
                f.truncate(64 * 1024 * 1024)
            entries = [{"name": "early", "reference": "small.bin", "observed": "small.bin"},
                       {"name": "late", "reference": "big.bin", "observed": "big.bin"}]
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            with patch.object(sys, "argv", ["comparator", str(manifest)]), \
                 patch.object(comparator, "read_private_capture") as read:
                with self.assertRaises(SystemExit) as error:
                    comparator.main()
                self.assertEqual(error.exception.code, 2)
                read.assert_not_called()

    def test_reject_actual_nul_during_manifest_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "small.bin").write_bytes(bytes(16))
            result = self.run_manifest([{"name": "fft",
                                         "reference": "small.bin\\x00".replace("\\x00", "\x00"),
                                         "observed": "small.bin"}], root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Invalid private FFT", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_reject_parent_traversal_before_capture_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = self.run_manifest([{"name": "fft", "reference": "../outside.bin",
                                         "observed": "missing.bin"}], root)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_reject_symlinked_capture(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "original.bin").write_bytes(bytes(16))
            (root / "alias.bin").symlink_to(root / "original.bin")
            result = self.run_manifest([{"name": "fft", "reference": "alias.bin",
                                         "observed": "original.bin"}], root)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_accept_nested_regular_capture(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "nested").mkdir()
            (root / "nested" / "reference.bin").write_bytes(bytes(16))
            (root / "nested" / "observed.bin").write_bytes(bytes(16))
            result = self.run_manifest([{"name": "fft",
                                         "reference": "nested/reference.bin",
                                         "observed": "nested/observed.bin"}], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["all_match"])

if __name__ == "__main__":
    unittest.main()
