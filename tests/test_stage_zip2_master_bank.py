"""A9: real reassembler behavior with independent synthetic tiny Git fixtures.

Never includes or downloads original game files. Production pins are verified
separately by the isolated real-ZIP2 GitHub Actions job.
"""
import hashlib
import subprocess
import tempfile
from pathlib import Path
import unittest

from scripts.stage_zip2_master_bank import stage


class ZIP2MasterBankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "zip2"
        self.repo.mkdir()
        self._git("init", "-q")
        self.part_dir = self.repo / "Raft/Raft_Data/StreamingAssets/MasterBank.bank"
        self.part_dir.mkdir(parents=True)
        self.parts = [b"abcdefgh", b"12345678", b"end"]
        for i, chunk in enumerate(self.parts):
            (self.part_dir / f"part-{i:05d}").write_bytes(chunk)
        (self.part_dir / "README.txt").write_text("test fixture, not game data")
        self.data = b"".join(self.parts)
        self.bytes = len(self.data)
        self.sha256 = hashlib.sha256(self.data).hexdigest()
        self.manifest = self.repo / "RAFT_FILE_MANIFEST.tsv"
        self.manifest.write_text(
            "kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
            f"split\t{self.bytes}\t{self.sha256}\t660\t"
            "Raft_Data/StreamingAssets/MasterBank.bank\n", encoding="utf-8")
        self._commit()
        self.pinned_commit = self._git("rev-parse", "HEAD")
        self.pinned_manifest = self._git("hash-object", "--", "RAFT_FILE_MANIFEST.tsv")
        self.target = self.root / "verified" / "MasterBank.bank"

    def _git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], text=True
        ).strip()

    def _commit(self):
        self._git("add", ".")
        self._git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                  "commit", "-qm", "synthetic source")

    def _stage(self):
        return stage(
            self.repo, self.target, expected_commit=self.pinned_commit,
            expected_manifest_blob=self.pinned_manifest,
            expected_bytes=self.bytes, expected_sha256=self.sha256,
            part_bytes=8,
        )

    def _no_partial(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.rglob(".zip2-masterbank-*.partial")), [])

    def test_restores_byte_identical_and_declines_second_publish(self):
        result = self._stage()
        self.assertEqual(self.target.read_bytes(), self.data)
        self.assertEqual(result["chunks"], 3)
        self.assertEqual(result["original_bytes"], self.bytes)
        with self.assertRaisesRegex(ValueError, "already published"):
            self._stage()
        self.assertEqual(self.target.read_bytes(), self.data)

    def test_corrupted_chunk_same_length_is_not_published(self):
        (self.part_dir / "part-00001").write_bytes(b"87654321")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self._stage()
        self._no_partial()

    def test_missing_part_fails_closed(self):
        (self.part_dir / "part-00001").unlink()
        with self.assertRaisesRegex(ValueError, "missing/extra"):
            self._stage()
        self._no_partial()

    def test_added_unexpected_chunk_fails_closed(self):
        (self.part_dir / "part-00003").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "missing/extra"):
            self._stage()
        self._no_partial()

    def test_wrong_chunk_length_fails_closed(self):
        (self.part_dir / "part-00002").write_bytes(b"shorter")
        with self.assertRaisesRegex(ValueError, "part length"):
            self._stage()
        self._no_partial()

    def test_swapped_chunks_preserve_sizes_but_fail_hash(self):
        first, second = self.part_dir / "part-00000", self.part_dir / "part-00001"
        first.write_bytes(self.parts[1])
        second.write_bytes(self.parts[0])
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self._stage()
        self._no_partial()

    def test_manifest_changed_without_commit_fails(self):
        self.manifest.write_text(self.manifest.read_text() + "#changed\n")
        with self.assertRaisesRegex(ValueError, "manifest blob identity"):
            self._stage()
        self._no_partial()

    def test_manifest_and_commit_changed_together_fails_on_pinned_commit(self):
        self.manifest.write_text(self.manifest.read_text().replace("split\t", "plain\t"))
        self._commit()
        with self.assertRaisesRegex(ValueError, "source commit identity"):
            self._stage()
        self._no_partial()

    def test_symlinked_part_rejected(self):
        external = self.root / "other"
        external.write_bytes(self.parts[0])
        part = self.part_dir / "part-00000"
        part.unlink()
        part.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "linked"):
            self._stage()
        self._no_partial()
        self.assertEqual(external.read_bytes(), self.parts[0])

    def test_symlinked_source_ancestor_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        linked_root = self.root / "linked"
        linked_root.symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            stage(linked_root, self.target, expected_commit=self.pinned_commit,
                  expected_manifest_blob=self.pinned_manifest,
                  expected_bytes=self.bytes, expected_sha256=self.sha256,
                  part_bytes=8)
        self._no_partial()

    def test_existing_destination_never_overwritten(self):
        self.target.parent.mkdir()
        self.target.write_bytes(b"not the game bank")
        with self.assertRaisesRegex(ValueError, "already published"):
            self._stage()
        self.assertEqual(self.target.read_bytes(), b"not the game bank")
        self.assertEqual(list(self.root.rglob(".zip2-masterbank-*.partial")), [])

    def test_output_parent_link_cannot_redirect(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.target.parent.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "unsafe|Unsafe"):
            self._stage()
        self.assertFalse((elsewhere / "MasterBank.bank").exists())


if __name__ == "__main__":
    unittest.main()
