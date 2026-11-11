"""GT ZIP2-only original resource staging regression tests; no network or LFS."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
from unittest import mock
import unittest

from scripts.gt_zip2_payloads import (
    SourceFailure, manifest, source_parts, stage
)


def git(root: Path, *args: str):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def setup_fixture(root, rows):
    root.mkdir()
    git(root, "init", "-q")
    text = "kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
    for rel, (kind, data) in rows.items():
        text += f"{kind}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\t660\t{rel}\n"
        p = root / "Raft" / rel
        if kind == "plain":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        elif kind == "split":
            p.mkdir(parents=True, exist_ok=True)
            # Individual part sizes are simulated by patching PART_SIZE to 3.
            for i, start in enumerate(range(0, len(data), 3)):
                (p / f"part-{i:05d}").write_bytes(data[start:start+3])
            (p / "README.txt").write_text("fixture\n")
    (root / "RAFT_FILE_MANIFEST.tsv").write_text(text)
    git(root, "add", ".")
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=Test",
        "-c", "user.email=test@example.test", "commit", "-q", "-m", "fixture"
    ], check=True)
    return git(root, "rev-parse", "HEAD"), git(
        root, "hash-object", str(root / "RAFT_FILE_MANIFEST.tsv"))


class ZIP2OnlyTests(unittest.TestCase):
    def test_plain_and_split_originals_verified_and_cached(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            rows = {"Raft_Data/level0.resS": ("plain", b"hello"),
                    "Raft_Data/sharedassets29.assets.resS": ("split", b"abcdefgh")}
            sha, manifest_sha = setup_fixture(root, rows)
            with mock.patch("scripts.gt_zip2_payloads.PART_SIZE", 3):
                r = stage(root, base / "output", list(rows),
                          expected_commit=sha, expected_blob=manifest_sha)
                self.assertEqual(r["files_selected"], 2)
                self.assertEqual(r["newly_staged"], 2)
                self.assertFalse(r["git_lfs_used"])
                self.assertEqual(
                    (base / "output/Raft/Raft_Data/sharedassets29.assets.resS").read_bytes(),
                    rows["Raft_Data/sharedassets29.assets.resS"][1])
                again = stage(root, base / "output", list(rows),
                              expected_commit=sha, expected_blob=manifest_sha)
            self.assertEqual(again["newly_staged"], 0)
            self.assertEqual(again["previously_verified_cache"], 2)

    def test_wrong_checkout_commit_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            sha, blob = setup_fixture(root, {"Raft_Data/level0": ("plain", b"scene")})
            with self.assertRaisesRegex(SourceFailure, "pinned_commit"):
                stage(root, base / "out", ["Raft_Data/level0"],
                      expected_commit="0"*40, expected_blob=blob)

    def test_corrupt_split_does_not_publish_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            name = "Raft_Data/sharedassets29.assets.resS"
            sha, blob = setup_fixture(root, {name: ("split", b"abcdefg")})
            part = root / "Raft" / name / "part-00001"
            part.write_bytes(b"Zef")
            with mock.patch("scripts.gt_zip2_payloads.PART_SIZE", 3):
                with self.assertRaisesRegex(SourceFailure, "sha256_mismatch"):
                    stage(root, base / "out", [name],
                          expected_commit=sha, expected_blob=blob)
            self.assertFalse((base / "out/Raft" / name).exists())

    def test_missing_parts_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            name = "Raft_Data/resources.assets.resS"
            sha, blob = setup_fixture(root, {name: ("split", b"abcdef")})
            (root / "Raft" / name / "part-00001").unlink()
            with mock.patch("scripts.gt_zip2_payloads.PART_SIZE", 3):
                with self.assertRaisesRegex(SourceFailure, "split_parts_missing"):
                    stage(root, base / "out", [name],
                          expected_commit=sha, expected_blob=blob)

    def test_dangerous_paths_rejected_even_if_present_in_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            sha, blob = setup_fixture(root, {"Raft_Data/level0": ("plain", b"abc")})
            original = root / "RAFT_FILE_MANIFEST.tsv"
            original.write_text(original.read_text() +
                "plain\t3\t" + hashlib.sha256(b"abc").hexdigest() +
                "\t660\tRaft_Data/../outside\n")
            new_blob = git(root, "hash-object", str(original))
            with self.assertRaisesRegex(SourceFailure, "invalid_or_duplicated_zip2_path"):
                manifest(root, expected_commit=sha, expected_blob=new_blob)

    def test_symlink_input_and_bad_cache_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            name = "Raft_Data/level0.resS"
            sha, blob = setup_fixture(root, {name: ("plain", b"genuine")})
            original = root / "Raft" / name
            original.unlink()
            original.symlink_to(base / "outside")
            with self.assertRaisesRegex(SourceFailure, "symlinked"):
                stage(root, base / "out", [name],
                      expected_commit=sha, expected_blob=blob)
            original.unlink()
            original.write_bytes(b"genuine")
            cached = base / "out/Raft" / name
            cached.parent.mkdir(parents=True)
            cached.write_bytes(b"forged!")
            with self.assertRaisesRegex(SourceFailure, "cached_payload_not_original"):
                stage(root, base / "out", [name],
                      expected_commit=sha, expected_blob=blob)

    def test_budget_limit_blocks_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "src"
            name = "Raft_Data/level0.resS"
            sha, blob = setup_fixture(root, {name: ("plain", b"hello")})
            with self.assertRaisesRegex(SourceFailure, "acquisition_exceeds_budget"):
                stage(root, base / "out", [name], byte_budget=4,
                      expected_commit=sha, expected_blob=blob)
            self.assertFalse((base / "out").exists())


if __name__ == "__main__":
    unittest.main()
