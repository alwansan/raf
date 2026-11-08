"""Regression: detect same-size FFT trace mutation while reading one descriptor."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.t1_fft_trace_consistency import read_trace_manifest


class TraceMutationTests(unittest.TestCase):
    def test_unchanged_manifest_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.json"
            path.write_text(json.dumps([{"session": "a"}]), encoding="utf-8")
            self.assertEqual(read_trace_manifest(path), [{"session": "a"}])

    def test_same_size_metadata_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.json"
            path.write_bytes(b"[]")
            original_fstat = os.fstat
            calls = 0

            def changed_fstat(fd):
                nonlocal calls
                calls += 1
                original = original_fstat(fd)
                if calls == 1:
                    return original
                return SimpleNamespace(st_size=original.st_size,
                                       st_mtime_ns=original.st_mtime_ns + 1,
                                       st_ctime_ns=original.st_ctime_ns,
                                       st_mode=original.st_mode)

            with patch("scripts.t1_fft_trace_consistency.os.fstat", side_effect=changed_fstat):
                with self.assertRaisesRegex(ValueError, "changed"):
                    read_trace_manifest(path)
            self.assertEqual(calls, 2)

    def test_same_size_ctime_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.json"
            path.write_bytes(b"[]")
            original_fstat = os.fstat
            calls = 0

            def changed_fstat(fd):
                nonlocal calls
                calls += 1
                original = original_fstat(fd)
                if calls == 1:
                    return original
                return SimpleNamespace(st_size=original.st_size,
                                       st_mtime_ns=original.st_mtime_ns,
                                       st_ctime_ns=original.st_ctime_ns + 1,
                                       st_mode=original.st_mode)

            with patch("scripts.t1_fft_trace_consistency.os.fstat", side_effect=changed_fstat):
                with self.assertRaisesRegex(ValueError, "changed"):
                    read_trace_manifest(path)
            self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
