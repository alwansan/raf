"""B31: original graphics cache reuse is strict and does not mutate unverified payloads."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.hydrate_render_payloads import (
    missing_payloads,
    reuse_verified_staged_sources,
)


class B31OriginalGraphicsReuse(unittest.TestCase):
    NAME = "Raft/Raft_Data/sharedassets7.assets"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / "cache" / "Raft_Data"
        self.cache.mkdir(parents=True)
        self.work = self.root / "working"
        self.target = self.work / self.NAME
        self.target.parent.mkdir(parents=True)
        self.source = self.cache / "sharedassets7.assets"
        self.data = b"original-shader-owner-7" * 5
        self.digest = hashlib.sha256(self.data).hexdigest()
        self.row = (self.NAME, self.digest, len(self.data))
        self.pointer = (
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{self.digest}\nsize {len(self.data)}\n"
        ).encode("ascii")
        self.target.write_bytes(self.pointer)

    def test_exact_original_fingerprint_replaces_pointer(self):
        self.source.write_bytes(self.data)
        self.assertEqual(
            reuse_verified_staged_sources([self.row], self.cache, self.work),
            (1, len(self.data)),
        )
        self.assertEqual(self.target.read_bytes(), self.data)
        with patch.dict(os.environ, {}, clear=False):
            old = Path.cwd()
            try:
                os.chdir(self.work)
                self.assertEqual(missing_payloads([self.row]), [])
            finally:
                os.chdir(old)

    def test_missing_cache_root_keeps_pointer_for_lfs(self):
        self.assertEqual(
            reuse_verified_staged_sources([self.row], self.root / "missing", self.work),
            (0, 0),
        )
        self.assertEqual(self.target.read_bytes(), self.pointer)

    def test_absent_original_in_existing_cache_keeps_pointer_for_lfs(self):
        self.assertEqual(
            reuse_verified_staged_sources([self.row], self.cache, self.work),
            (0, 0),
        )
        self.assertEqual(self.target.read_bytes(), self.pointer)

    def test_invalid_source_hash_is_not_published(self):
        self.source.write_bytes(b"x" * len(self.data))
        with self.assertRaisesRegex(ValueError, "SHA verification"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(self.target.read_bytes(), self.pointer)
        self.assertEqual(list(self.target.parent.glob(".verified-zip2-graphics-*")), [])

    def test_invalid_source_size_is_not_published(self):
        self.source.write_bytes(self.data + b"x")
        with self.assertRaisesRegex(ValueError, "length"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(self.target.read_bytes(), self.pointer)

    def test_wrong_destination_lfs_pointer_is_rejected(self):
        self.source.write_bytes(self.data)
        self.target.write_bytes(self.pointer.replace(b"oid sha256:", b"oid sha256:0"))
        with self.assertRaises(ValueError):
            reuse_verified_staged_sources([self.row], self.cache, self.work)

    def test_unrelated_destination_bytes_are_not_overwritten(self):
        self.source.write_bytes(self.data)
        self.target.write_bytes(b"unrelated changes")
        with self.assertRaises(ValueError):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(self.target.read_bytes(), b"unrelated changes")

    def test_source_symlink_is_rejected(self):
        external = self.root / "external.bin"
        external.write_bytes(self.data)
        self.source.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "redirect"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(self.target.read_bytes(), self.pointer)

    def test_source_parent_symlink_is_rejected(self):
        real = self.root / "actual-source"
        real.mkdir()
        (real / "sharedassets7.assets").write_bytes(self.data)
        self.cache.rmdir()
        self.cache.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "redirect"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(self.target.read_bytes(), self.pointer)

    def test_destination_symlink_is_rejected(self):
        self.source.write_bytes(self.data)
        external = self.root / "elsewhere"
        external.write_bytes(self.pointer)
        self.target.unlink()
        self.target.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "redirect"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(external.read_bytes(), self.pointer)

    def test_target_hardlink_is_rejected(self):
        self.source.write_bytes(self.data)
        external = self.root / "linked-pointer"
        os.link(self.target, external)
        with self.assertRaisesRegex(ValueError, "hardlinked"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)
        self.assertEqual(external.read_bytes(), self.pointer)

    def test_source_hardlink_is_rejected(self):
        external = self.root / "linked-cache"
        external.write_bytes(self.data)
        os.link(external, self.source)
        with self.assertRaisesRegex(ValueError, "hardlinked"):
            reuse_verified_staged_sources([self.row], self.cache, self.work)

    def test_arbitrary_source_path_is_rejected(self):
        self.source.write_bytes(self.data)
        with self.assertRaisesRegex(ValueError, "allowlist"):
            reuse_verified_staged_sources(
                [("../unsafe", self.digest, len(self.data))], self.cache, self.work
            )


if __name__ == "__main__":
    unittest.main()
