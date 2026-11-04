"""B31: external Texture2D streams must not pass a linked-provider coverage gate."""
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from scripts.audit_texture_stream_coverage import (
    _regular_unlinked_provider,
    audit,
    extent,
)


class B31TextureStreamProvenance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Raft_Data"
        self.root.mkdir()
        self.source = self.root / "sharedassets0.assets.resS"
        self.source.write_bytes(b"16 verified test bytes" * 2)

    def test_regular_bytes_cover_valid_extent(self):
        self.assertIsNone(_regular_unlinked_provider(self.source))
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "covered")
        self.assertEqual(extent(self.root, self.source.name, 0, 999), "truncated_provider")

    def test_archive_slashes_only_select_same_root_basename(self):
        path = "archive:/CAB-123/sharedassets0.assets.resS"
        self.assertEqual(extent(self.root, path, 1, 5), "covered")

    def test_linked_stream_outside_source_is_never_covered(self):
        outside = Path(self.temp.name) / "external-original"
        outside.write_bytes(self.source.read_bytes())
        self.source.unlink()
        self.source.symlink_to(outside)
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "unsafe_provider")
        self.assertEqual(outside.read_bytes(), b"16 verified test bytes" * 2)

    def test_dangling_stream_symlink_is_not_missing_provider(self):
        self.source.unlink()
        self.source.symlink_to(self.root / "missing")
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "unsafe_provider")

    def test_hardlink_stream_is_not_original_coverage(self):
        outside = Path(self.temp.name) / "same-inode"
        os.link(self.source, outside)
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "unsafe_provider")

    def test_root_directory_symlink_is_rejected(self):
        mirror = Path(self.temp.name) / "linked-root"
        mirror.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(extent(mirror, self.source.name, 0, 16), "unsafe_provider")

    def test_missing_provider_remains_a_distinct_error(self):
        self.source.unlink()
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "missing_provider")

    def test_lfs_pointer_remains_uncovered(self):
        self.source.write_bytes(
            b"version https://git-lfs.github.com/spec/v1\n"
            + b"oid sha256:" + b"a" * 64 + b"\nsize 4096\n"
        )
        self.assertEqual(extent(self.root, self.source.name, 0, 16), "lfs_pointer")

    def test_negative_empty_extent_must_not_bypass_validation(self):
        self.assertEqual(extent(self.root, "", -1, 0), "invalid_extent")
        self.assertEqual(extent(self.root, "", 0, 0), "inline_or_empty")
        self.assertEqual(extent(self.root, self.source.name, 0, 0), "inline_or_empty")

    def test_linked_serialized_owner_rejected_before_unity_load(self):
        other = Path(self.temp.name) / "original-serialized-owner"
        other.write_bytes(b"not real Unity serialized data")
        owner = self.root / "sharedassets1.assets"
        owner.symlink_to(other)
        unity = types.SimpleNamespace(load=lambda path: self.fail("Unity load followed a link"))
        with patch.dict(sys.modules, {"UnityPy": unity}):
            with self.assertRaisesRegex(ValueError, "Unsafe or missing"):
                audit(self.root)

    def test_hardlinked_serialized_owner_rejected_before_unity_load(self):
        other = Path(self.temp.name) / "original-serialized-owner"
        other.write_bytes(b"not real Unity serialized data")
        os.link(other, self.root / "sharedassets2.assets")
        unity = types.SimpleNamespace(load=lambda path: self.fail("Unity load followed a hardlink"))
        with patch.dict(sys.modules, {"UnityPy": unity}):
            with self.assertRaisesRegex(ValueError, "Unsafe or missing"):
                audit(self.root)


if __name__ == "__main__":
    unittest.main()
