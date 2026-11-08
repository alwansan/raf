"""Regression: bounded FFT trace ingestion must tolerate short regular-file reads."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.t1_fft_trace_consistency import read_trace_manifest


class TraceExactReadTests(unittest.TestCase):
    def test_short_reads_reconstruct_complete_manifest(self):
        payload = json.dumps([{"session": "sample"}]).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_bytes(payload)
            original_read = os.read

            def short_read(fd, size):
                return original_read(fd, min(size, 3))

            with patch("scripts.t1_fft_trace_consistency.os.read", side_effect=short_read):
                self.assertEqual(read_trace_manifest(path), [{"session": "sample"}])

    def test_truncated_after_stat_is_rejected(self):
        payload = b'[{"session":"sample"}]'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_bytes(payload)
            original_read = os.read
            truncated = False

            def truncate_on_first_read(fd, size):
                nonlocal truncated
                if not truncated:
                    truncated = True
                    path.write_bytes(b"[")
                return original_read(fd, size)

            with patch("scripts.t1_fft_trace_consistency.os.read", side_effect=truncate_on_first_read):
                with self.assertRaisesRegex(ValueError, "truncated"):
                    read_trace_manifest(path)

    def test_growth_after_stat_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_bytes(b"[]")
            original_read = os.read
            grown = False

            def grow_on_first_read(fd, size):
                nonlocal grown
                if not grown:
                    grown = True
                    with path.open("ab") as stream:
                        stream.write(b" ")
                return original_read(fd, size)

            with patch("scripts.t1_fft_trace_consistency.os.read", side_effect=grow_on_first_read):
                with self.assertRaisesRegex(ValueError, "changed"):
                    read_trace_manifest(path)


if __name__ == "__main__":
    unittest.main()
