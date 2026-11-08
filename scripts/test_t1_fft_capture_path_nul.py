"""Regression for exact NUL validation in private FFT capture paths."""
import tempfile
import unittest
from pathlib import Path

from scripts.t1_fft_first_divergence import read_private_capture


class PrivateCaptureNulPathTests(unittest.TestCase):
    def test_nul_is_rejected_before_path_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "invalid private capture path"):
                read_private_capture(Path(directory), "capture\\x00.rgba32f".replace("\\x00", "\x00"))

    def test_literal_backslash_x00_filename_is_not_nul_on_posix(self):
        # POSIX permits a literal backslash; this is distinct from a NUL byte.
        import os
        if os.name != "posix":
            self.skipTest("POSIX filename semantics required")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            filename = r"capture\x00.rgba32f"
            payload = bytes(16)
            (root / filename).write_bytes(payload)
            self.assertEqual(read_private_capture(root, filename), payload)


if __name__ == "__main__":
    unittest.main()
