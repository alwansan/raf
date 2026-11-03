"""Synthetic ZIP2 chunks only; never load or print original Raft source data."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from scripts.stage_zip2_fft_owner import (
    ORIGINAL, PART_BYTES, SHA256, SIZE, stage,
)


class Zip2OriginalFftOwnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="a1-zip2-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.root = base / "zip2"
        self.parts = self.root / "Raft" / "Raft_Data" / "sharedassets0.assets"
        self.parts.mkdir(parents=True)
        self.dest = base / "staged" / "Raft_Data" / "sharedassets0.assets"
        self.payload = b"ABCDWXYZ1"
        self.sha = hashlib.sha256(self.payload).hexdigest()
        self.parts.joinpath("README.txt").write_text("synthetic")
        self._parts()

    def _parts(self):
        for p in self.parts.glob("part-*"):
            p.unlink()
        for i in range(3):
            self.parts.joinpath("part-%05d" % i).write_bytes(
                self.payload[i * 4:(i + 1) * 4])

    def _manifest(self, *, sha=None, size=None, kind="split", duplicate=False):
        one = "\t".join((
            kind, str(len(self.payload) if size is None else size),
            self.sha if sha is None else sha, "660", ORIGINAL))
        content = "kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n" + one + "\n"
        if duplicate:
            content += one + "\n"
        self.root.joinpath("RAFT_FILE_MANIFEST.tsv").write_text(content)

    def _stage(self, **opts):
        return stage(self.root, self.dest, expected_bytes=len(self.payload),
                     expected_sha256=self.sha, max_part_bytes=4, **opts)

    def test_three_parts_restore_only_pinned_original_with_hash(self):
        self._manifest()
        result = self._stage()
        self.assertEqual(self.dest.read_bytes(), self.payload)
        self.assertEqual(result["verified_sha256"], self.sha)
        self.assertEqual(result["source_parts"], 3)
        self.assertFalse(result["android_or_unity_executed"])
        self.assertEqual(self.parts.joinpath("part-00000").read_bytes(), b"ABCD")

    def test_existing_original_file_never_overwritten(self):
        self._manifest()
        self.dest.parent.mkdir(parents=True)
        self.dest.write_bytes(b"existing")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            self._stage()
        self.assertEqual(self.dest.read_bytes(), b"existing")

    def test_missing_or_extra_chunk_fails_closed(self):
        self._manifest()
        self.parts.joinpath("part-00001").unlink()
        with self.assertRaisesRegex(ValueError, "Missing, extra"):
            self._stage()
        self.assertFalse(self.dest.exists())
        self._parts()
        self.parts.joinpath("part-00003").write_bytes(b"X")
        with self.assertRaisesRegex(ValueError, "Missing, extra"):
            self._stage()

    def test_swapped_chunks_are_not_accepted_as_same_file(self):
        self._manifest()
        a = self.parts.joinpath("part-00000")
        b = self.parts.joinpath("part-00001")
        pa, pb = a.read_bytes(), b.read_bytes()
        a.write_bytes(pb)
        b.write_bytes(pa)
        with self.assertRaisesRegex(ValueError, "pinned size/SHA256"):
            self._stage()
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.dest.parent.glob(".zip2-fft-*")), [])

    def test_tampered_bytes_with_unchanged_size_fail(self):
        self._manifest()
        self.parts.joinpath("part-00002").write_bytes(b"9")
        with self.assertRaisesRegex(ValueError, "pinned size/SHA256"):
            self._stage()
        self.assertFalse(self.dest.exists())

    def test_manifest_wrong_digest_size_or_duplicates_rejected(self):
        for fields in ({"sha": "0"*64}, {"size": 10}, {"kind": "plain"},
                       {"duplicate": True}):
            with self.subTest(fields=fields):
                self._manifest(**fields)
                with self.assertRaisesRegex(ValueError, "manifest"):
                    self._stage()

    def test_disallow_symlink_source_chunk_and_output_parent(self):
        self._manifest()
        original = self.parts / "part-00001"
        original.unlink()
        original.symlink_to(self.parts / "part-00000")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self._stage()
        original.unlink()
        self._parts()
        other = Path(self.temporary.name) / "outside"
        other.mkdir()
        self.dest.parent.parent.mkdir(parents=True, exist_ok=True)
        self.dest.parent.symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self._stage()

    def test_no_private_readme_or_additional_paths_as_chunks(self):
        self._manifest()
        self.parts.joinpath("part-00002-copy").write_bytes(b"1")
        with self.assertRaisesRegex(ValueError, "Unexpected ZIP2 chunk"):
            self._stage()

    def test_manifest_missing_and_wrong_schema_rejected(self):
        with self.assertRaisesRegex(ValueError, "checkout"):
            self._stage()
        self.root.joinpath("RAFT_FILE_MANIFEST.tsv").write_text("wrong\tcolumns\n")
        with self.assertRaisesRegex(ValueError, "schema"):
            self._stage()

    def test_original_pin_constants_are_independent_of_manifest(self):
        self.assertEqual(SIZE, 115978112)
        self.assertEqual(SHA256, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3")
        self.assertEqual(PART_BYTES, 47185920)


if __name__ == "__main__":
    unittest.main()
