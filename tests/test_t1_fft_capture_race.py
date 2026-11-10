"""Synthetic regression: a capture swapped after stat must never pass the SHA gate."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.t1_fft_capture_integrity_gate import verify_captures


class CaptureRaceTests(unittest.TestCase):
    def test_inode_swap_before_open_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "v.bin").write_bytes(b"V" * 16)
            (root / "u.bin").write_bytes(b"U" * 16)
            (root / "replacement.bin").write_bytes(b"U" * 16)
            manifest = {
                "build_sha": "a" * 40,
                "session_id": "synthetic",
                "passes": [{
                    "name": "first",
                    "vulkan_bytes": 16, "unity_bytes": 16,
                    "vulkan_sha256": hashlib.sha256(b"V" * 16).hexdigest(),
                    "unity_sha256": hashlib.sha256(b"U" * 16).hexdigest(),
                }],
            }
            paths = {"first": {"vulkan": "v.bin", "unity": "u.bin"}}
            real_open = os.open
            swapped = False

            def swap_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if str(path).endswith("u.bin") and not swapped:
                    swapped = True
                    os.replace(root / "replacement.bin", root / "u.bin")
                return real_open(path, flags, *args, **kwargs)

            with patch("scripts.t1_fft_capture_integrity_gate.os.open",
                       side_effect=swap_before_open):
                with self.assertRaisesRegex(ValueError, "changed before read"):
                    verify_captures(manifest, paths, root)
            self.assertTrue(swapped)


if __name__ == "__main__":
    unittest.main()
