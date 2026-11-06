"""Synthetic negative controls for exact seven owner-world RGD source intake."""
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.t4_stage_owner5nov_world_rgds import (
    EXPECTED, git_blob_sha1, stage_verified_worlds, verify_worlds,
)

ROOT = Path(__file__).resolve().parents[1]
CLR = (ROOT / "android-port/Experiments/T4/ClWorldRgdRuntime/Program.cs").read_text()


def fixture(root, items=(b"abc", b"xyz")):
    path = root / "checkout" / "User" / "World" / "worldA"
    path.mkdir(parents=True)
    expected = {}
    for number, value in enumerate(items, start=1):
        (path / ("file" + str(number) + ".rgd")).write_bytes(value)
        expected[git_blob_sha1(value)] = len(value)
    return root / "checkout", expected, path


class OwnerWorldAuthenticity(unittest.TestCase):
    def test_immutable_seven_distinct_real_objects_and_duplicate_sizes(self):
        self.assertEqual(len(EXPECTED), 7)
        self.assertEqual(sum(1 for value in EXPECTED.values() if value == 319239), 2)
        self.assertEqual(min(EXPECTED.values()), 309519)
        self.assertEqual(max(EXPECTED.values()), 331887)
        self.assertEqual(len(set(EXPECTED)), 7)
        self.assertTrue(all(len(item) == 40 for item in EXPECTED))

    def test_actual_original_loader_authenticates_all_ten_pinned_blobs(self):
        for sha in EXPECTED:
            self.assertIn(sha, CLR)
        # The earlier 4 Nov three saved-world inputs still require their SHA.
        for sha in ("8d250dec17e0ff5688fb760948ced35db7808580",
                    "64f5cbfb35ab12a986d007cfbbb89d298ca5b46f",
                    "65b5b93d98c3e17c679e74d1568ef99ff52e1145"):
            self.assertIn(sha, CLR)
        self.assertIn("new Dictionary<long, string[]>", CLR)
        self.assertIn("expected.Contains(", CLR)

    def test_equal_length_distinct_blobs_are_both_staged_by_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, _ = fixture(root)
            out = root / "private"
            self.assertEqual(stage_verified_worlds(checkout, out, allowlist=allowed), 2)
            result = sorted(out.glob("*.rgd"))
            self.assertEqual([p.name for p in result], ["owner01.rgd", "owner02.rgd"])
            self.assertEqual({git_blob_sha1(p.read_bytes()) for p in result}, set(allowed))
            self.assertTrue(all(p.parent == out for p in result))

    def test_modified_same_size_blob_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, folder = fixture(root)
            (folder / "file2.rgd").write_bytes(b"xy0")
            out = root / "stage"
            with self.assertRaisesRegex(ValueError, "SHA_SIZE"):
                stage_verified_worlds(checkout, out, allowlist=allowed)
            self.assertFalse(out.exists())

    def test_missing_blob_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, folder = fixture(root)
            (folder / "file2.rgd").unlink()
            with self.assertRaisesRegex(ValueError, "COUNT"):
                verify_worlds(checkout, allowlist=allowed)

    def test_unlisted_duplicate_same_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, folder = fixture(root)
            (folder / "file2.rgd").write_bytes(b"abc")
            with self.assertRaisesRegex(ValueError, "SHA_SIZE"):
                verify_worlds(checkout, allowlist=allowed)

    def test_symlinked_file_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, folder = fixture(root)
            (folder / "file2.rgd").unlink()
            (folder / "file2.rgd").symlink_to(folder / "file1.rgd")
            with self.assertRaisesRegex(ValueError, "LINK"):
                verify_worlds(checkout, allowlist=allowed)

    def test_symlinked_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, _ = fixture(root)
            symlink = root / "linked"
            symlink.symlink_to(checkout, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "ROOT_INVALID"):
                verify_worlds(symlink, allowlist=allowed)

    def test_world_collection_must_be_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, _ = fixture(root)
            (checkout / "User2" / "World").mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "SINGLE_WORLD"):
                verify_worlds(checkout, allowlist=allowed)

    def test_output_file_collision_and_source_alias_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, _ = fixture(root)
            dest = root / "dest"
            dest.mkdir()
            (dest / "existing.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "OUTPUT_MUST_BE_EMPTY"):
                stage_verified_worlds(checkout, dest, allowlist=allowed)
            self.assertEqual((dest / "existing.txt").read_text(), "preserve")
            with self.assertRaisesRegex(ValueError, "OUTPUT_MUST_BE_OUTSIDE_SOURCE"):
                stage_verified_worlds(checkout, checkout / "stage", allowlist=allowed)

    def test_player_side_rgds_not_misidentified_as_worlds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, _ = fixture(root)
            player = checkout / "User" / "Player"
            player.mkdir()
            (player / "nonworld.rgd").write_bytes(b"do not touch")
            self.assertEqual(set(verify_worlds(checkout, allowlist=allowed)), set(allowed))

    def test_unrecognized_extra_world_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout, allowed, folder = fixture(root)
            (folder / "third.rgd").write_bytes(b"another")
            with self.assertRaisesRegex(ValueError, "COUNT"):
                verify_worlds(checkout, allowlist=allowed)


if __name__ == "__main__":
    unittest.main()
