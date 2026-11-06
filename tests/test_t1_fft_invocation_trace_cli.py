"""Invocation trace CLI regression tests, independent of Vulkan/Unity availability."""
import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.t1_fft_invocation_trace_cli import main
from scripts.t1_fft_trace_compare import INVOCATION_RECORD, INVOCATION_SIZE, RECORD, SIZE


def capture(rows):
    return (struct.pack("<I", len(rows)) +
            b"".join(INVOCATION_RECORD.pack(*row) for row in rows)).ljust(INVOCATION_SIZE, b"\0")


ROWS = [(site, 3, 0, 0, 0, 1, 2, 0, 10, 0, 0, 0) for site in range(3)]


class InvocationCliTests(unittest.TestCase):
    def run_pair(self, left, right):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.bin", Path(tmp) / "b.bin"
            a.write_bytes(left)
            b.write_bytes(right)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = main([str(a), str(b)])
            return status, out.getvalue(), err.getvalue()

    def test_identical_reordered_capture_passes(self):
        status, output, _ = self.run_pair(capture(ROWS), capture(ROWS[::-1]))
        self.assertEqual(status, 0)
        self.assertIn('"match": true', output)

    def test_coordinate_drift_fails_even_with_identical_value(self):
        drift = [(*ROWS[0][:5], 9, *ROWS[0][6:]), *ROWS[1:]]
        status, output, _ = self.run_pair(capture(ROWS), capture(drift))
        self.assertEqual(status, 1)
        self.assertIn('"coordinate_mismatches": 1', output)

    def test_duplicate_invocation_fails_closed(self):
        status, output, error = self.run_pair(capture(ROWS), capture(ROWS + ROWS[:1]))
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("invalid_capture", error)

    def test_truncated_or_oversized_capture_fails_closed(self):
        for bad in (capture(ROWS)[:-1], capture(ROWS) + b"x"):
            status, output, _ = self.run_pair(capture(ROWS), bad)
            self.assertEqual(status, 2)
            self.assertEqual(output, "")

    def test_legacy_trace_layout_is_rejected(self):
        legacy = (struct.pack("<I", 3) +
                  b"".join(RECORD.pack(site, 1, 2, 0, 10, 0, 0, 0)
                           for site in range(3))).ljust(SIZE, b"\0")
        status, _, _ = self.run_pair(capture(ROWS), legacy)
        self.assertEqual(status, 2)


if __name__ == "__main__":
    unittest.main()
