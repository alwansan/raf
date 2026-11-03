"""A10 synthetic-only SHA-identity regression cases; no original game source or Unity."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.adapt_android_offline_startup import fingerprint
from scripts.verify_android_offline_candidate import select_original_source


class OriginalSourceSelectionTests(unittest.TestCase):
    def test_sdk_homonym_does_not_obscure_game_source(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = "class SaveAndLoad { void Save() {} }\n"
            game = root / "ILSpy" / "SaveAndLoad.cs"
            sdk = root / "Vendor" / "SaveAndLoad.cs"
            game.parent.mkdir()
            sdk.parent.mkdir()
            game.write_text(code)
            sdk.write_text("class SaveAndLoad { void Sdk() {} }")
            self.assertEqual(select_original_source(root, "SaveAndLoad", fingerprint(code)), (game, code))
            self.assertIn("Sdk", sdk.read_text())

    def test_unpinned_candidate_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SaveAndLoad.cs"
            path.write_text("unrelated source")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(Path(tmp), "SaveAndLoad", fingerprint("genuine"))
            self.assertEqual(path.read_text(), "unrelated source")

    def test_two_matching_sources_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("A", "B"):
                path = root / directory / "SaveAndLoad.cs"
                path.parent.mkdir()
                path.write_text("same original")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(root, "SaveAndLoad", fingerprint("same original"))

    def test_symlinked_source_is_not_followed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "external.cs"
            target.write_text("genuine")
            link = root / "SaveAndLoad.cs"
            try:
                link.symlink_to(target)
            except (NotImplementedError, OSError):
                self.skipTest("File symlink unavailable")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(root, "SaveAndLoad", fingerprint("genuine"))
            self.assertEqual(target.read_text(), "genuine")

    def test_bom_crlf_normalization_does_not_write_source(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SaveAndLoad.cs"
            raw = b"\xef\xbb\xbfclass SaveAndLoad {\r\n}\r\n"
            path.write_bytes(raw)
            normalized = "class SaveAndLoad {\n}\n"
            self.assertEqual(select_original_source(Path(tmp), "SaveAndLoad", fingerprint(normalized)), (path, normalized))
            self.assertEqual(path.read_bytes(), raw)

    def test_undecodable_sdk_homonym_ignored(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.joinpath("Game").mkdir()
            root.joinpath("SDK").mkdir()
            original = root / "Game" / "SaveAndLoad.cs"
            sdk = root / "SDK" / "SaveAndLoad.cs"
            original.write_text("genuine")
            sdk.write_bytes(b"\xff\x80")
            self.assertEqual(select_original_source(root, "SaveAndLoad", fingerprint("genuine")), (original, "genuine"))
            self.assertEqual(sdk.read_bytes(), b"\xff\x80")


if __name__ == "__main__":
    unittest.main()
