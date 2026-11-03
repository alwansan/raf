"""ZIP2 reconstructor synthetic correctness and fail-closed negative tests."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.a12r_zip2_shader_owners import restore


class Zip2RestorerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Raft" / "Raft_Data"
        self.root.mkdir(parents=True)
        self.out = Path(self.temp.name) / "output"
        self.original = b"test-real-bytes" * 3
        self.expected = {"fake.assets": (len(self.original), hashlib.sha256(self.original).hexdigest())}
        self.parts = self.root / "fake.assets"
        self.parts.mkdir()
        (self.parts / "part-00000").write_bytes(self.original[:9])
        (self.parts / "part-00001").write_bytes(self.original[9:])

    def test_restores_exact_bytes_without_lfs(self):
        result = restore(self.root, self.out, self.expected)
        self.assertEqual((self.out / "fake.assets").read_bytes(), self.original)
        self.assertTrue(result["sha256_verified"])
        self.assertFalse(result["lfs_network_downloaded"])

    def test_missing_part_fails(self):
        (self.parts / "part-00001").rename(self.parts / "part-00003")
        with self.assertRaisesRegex(ValueError, "sequence"):
            restore(self.root, self.out, self.expected)

    def test_bad_sha_removes_partial(self):
        (self.parts / "part-00001").write_bytes(b"not-the-same")
        with self.assertRaises(ValueError):
            restore(self.root, self.out, self.expected)
        self.assertFalse((self.out / "fake.assets").exists())

    def test_bad_part_name_fails(self):
        (self.parts / "part-fake").write_bytes(b"x")
        with self.assertRaises(ValueError):
            restore(self.root, self.out, self.expected)

    def test_symlink_part_fails(self):
        (self.parts / "part-00001").unlink()
        (self.parts / "part-00001").symlink_to(self.parts / "part-00000")
        with self.assertRaises(ValueError):
            restore(self.root, self.out, self.expected)

    def test_existing_output_cannot_be_overwritten(self):
        self.out.mkdir()
        (self.out / "fake.assets").write_bytes(b"other")
        with self.assertRaises(ValueError):
            restore(self.root, self.out, self.expected)
        self.assertEqual((self.out / "fake.assets").read_bytes(), b"other")

    def test_plain_original_file_supported(self):
        for part in self.parts.iterdir():
            part.unlink()
        self.parts.rmdir()
        (self.root / "fake.assets").write_bytes(self.original)
        self.assertEqual(restore(self.root, self.out, self.expected)["restored_owners"], 1)

    def test_never_stage_inside_zip2(self):
        with self.assertRaises(ValueError):
            restore(self.root, self.root / "inside", self.expected)


if __name__ == "__main__":
    unittest.main()
