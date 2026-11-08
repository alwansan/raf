#!/usr/bin/env python3
"""Regression for bounded, single-descriptor FFT trace manifest loading."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t1_fft_trace_consistency import MAX_MANIFEST, read_trace_manifest


class TraceManifestDescriptorTests(unittest.TestCase):
    def test_regular_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "trace.json"
            p.write_text("[]", encoding="utf-8")
            self.assertEqual(read_trace_manifest(p), [])

    def test_symlink_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "trace.json"
            target = Path(root) / "target.json"
            target.write_text("[]", encoding="utf-8")
            p.symlink_to(target)
            with self.assertRaises((OSError, ValueError)):
                read_trace_manifest(p)

    def test_oversize_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "trace.json"
            p.write_bytes(b" " * (MAX_MANIFEST + 1))
            with self.assertRaises(ValueError):
                read_trace_manifest(p)

    def test_duplicate_keys_still_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "trace.json"
            p.write_text('[{"session":"one","session":"two"}]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                read_trace_manifest(p)

    def test_invalid_utf8_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "trace.json"
            p.write_bytes(bytes([255]))
            with self.assertRaises(UnicodeError):
                read_trace_manifest(p)


if __name__ == "__main__":
    unittest.main()
