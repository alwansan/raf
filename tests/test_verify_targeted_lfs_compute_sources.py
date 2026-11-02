"""Synthetic LFS identity tests: no original game assets."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.verify_targeted_lfs_compute_sources import verify_sources


class TargetedComputeLfsTests(unittest.TestCase):
    def test_exact_pointer_and_payload_identity(self):
        blob = b"independent synthetic compute owner"
        digest = hashlib.sha256(blob).hexdigest()
        expected = {"resources.assets": (len(blob), digest)}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "resources.assets"
            path.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{digest}\nsize {len(blob)}\n")
            report = verify_sources(Path(folder), pointers_only=True, expected=expected)
            self.assertEqual(report["authenticated_owners"], 1)
            self.assertTrue(report["sources"][0]["verified_pointer"])
            with self.assertRaisesRegex(ValueError, "still a pointer"):
                verify_sources(Path(folder), expected=expected)
            path.write_bytes(blob)
            report = verify_sources(Path(folder), expected=expected)
            self.assertTrue(report["sources"][0]["verified_payload"])
            self.assertFalse(report["game_sources_modified"])

    def test_stale_pointer_and_corrupt_payload_rejected(self):
        blob = b"original fake data"
        expected = {"sharedassets0.assets": (len(blob), hashlib.sha256(blob).hexdigest())}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sharedassets0.assets"
            path.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 18\n")
            with self.assertRaisesRegex(ValueError, "identity changed"):
                verify_sources(Path(folder), pointers_only=True, expected=expected)
            path.write_bytes(b"X" + blob[1:])
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                verify_sources(Path(folder), expected=expected)
            path.write_bytes(blob[:-1])
            with self.assertRaisesRegex(ValueError, "size mismatch"):
                verify_sources(Path(folder), expected=expected)

    def test_symlink_and_unsafe_names_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "source").write_bytes(b"a")
            (root / "resources.assets").symlink_to("source")
            expected = {"resources.assets": (1, hashlib.sha256(b"a").hexdigest())}
            with self.assertRaisesRegex(ValueError, "unsafe symlink"):
                verify_sources(root, expected=expected)
            with self.assertRaisesRegex(ValueError, "Unsafe original LFS owner name"):
                verify_sources(root, expected={"../escape.assets": (1, "a" * 64)})


if __name__ == "__main__":
    unittest.main()
