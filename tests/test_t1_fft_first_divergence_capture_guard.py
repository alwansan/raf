"""Source-free regression tests for private FFT capture path/size safety."""
import tempfile
import unittest
from pathlib import Path

from scripts.t1_fft_first_divergence import MAX_CAPTURE_BYTES, read_private_capture


class PrivateCaptureGuardTests(unittest.TestCase):
    def test_regular_capture_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / "sample.bin").write_bytes(bytes(16))
            self.assertEqual(read_private_capture(root, "sample.bin"), bytes(16))

    def test_parent_traversal_and_absolute_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            for value in ("../outside.bin", str(root / "file.bin"), ""):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    read_private_capture(root, value)

    def test_symlink_file_and_directory_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / "actual.bin").write_bytes(bytes(16))
            (root / "alias.bin").symlink_to(root / "actual.bin")
            (root / "nested").mkdir()
            (root / "nested" / "actual.bin").write_bytes(bytes(16))
            (root / "aliasdir").symlink_to(root / "nested", target_is_directory=True)
            for value in ("alias.bin", "aliasdir/actual.bin"):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    read_private_capture(root, value)

    def test_empty_partial_and_oversized_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            p = root / "sample.bin"
            for payload in (b"", bytes(15)):
                p.write_bytes(payload)
                with self.assertRaises(ValueError):
                    read_private_capture(root, p.name)
            with p.open("wb") as stream:
                stream.truncate(MAX_CAPTURE_BYTES + 16)
            with self.assertRaises(ValueError):
                read_private_capture(root, p.name)


if __name__ == "__main__":
    unittest.main()
