"""A10 LOCAL-005 — synthetic-only original game save source selector tests.

The original .rgd serializer, game C# bytes and .meta/GUIDs are never part
of these fixtures. No Unity or Android execution is asserted.
"""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.adapt_original_save_paths import apply


def make_source(project, folder, content):
    path = project / "Assets" / folder / "SaveAndLoad.cs"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class A10SaveSelectorTests(unittest.TestCase):
    def test_original_game_source_selected_when_sdk_homonym_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            backup = root / "private-backup"
            game = make_source(project, "Scripts/Assembly-CSharp", "synthetic game")
            meta = game.with_suffix(".cs.meta")
            meta.write_bytes(b"synthetic-guid-metadata")
            sdk = make_source(project, "Plugins/Vendor", "synthetic SDK")
            with patch("scripts.adapt_original_save_paths.adapt",
                       side_effect=lambda text: text + "\n// adapted"):
                result = apply(project, backup, write=True)
            self.assertTrue(result["changed"])
            self.assertTrue(result["originalMetaUnchanged"])
            self.assertEqual(game.read_text(), "synthetic game\n// adapted")
            self.assertEqual(sdk.read_text(), "synthetic SDK")
            self.assertEqual(meta.read_bytes(), b"synthetic-guid-metadata")
            self.assertEqual((backup / "SaveAndLoad.cs").read_text(), "synthetic game")
            self.assertEqual((backup / "SaveAndLoad.cs.meta").read_bytes(),
                             b"synthetic-guid-metadata")

    def test_sdk_only_cannot_be_mistaken_for_original_game_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            sdk = make_source(project, "Plugins/Vendor", "synthetic SDK")
            with patch("scripts.adapt_original_save_paths.adapt",
                       side_effect=lambda text: text + "\n// patched"):
                with self.assertRaisesRegex(ValueError,
                                            "Require one original SaveAndLoad source"):
                    apply(project, root / "backup", write=True)
            self.assertEqual(sdk.read_text(), "synthetic SDK")
            self.assertFalse((root / "backup").exists())

    def test_multiple_game_assembly_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            first = make_source(project, "Scripts/Assembly-CSharp", "game one")
            second = make_source(project, "Other/Assembly-CSharp", "game two")
            with self.assertRaisesRegex(ValueError,
                                        "Require one original SaveAndLoad source"):
                apply(project, root / "backup", write=True)
            self.assertEqual(first.read_text(), "game one")
            self.assertEqual(second.read_text(), "game two")
            self.assertFalse((root / "backup").exists())

    def test_preexisting_game_meta_stays_unchanged_in_inspection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            game = make_source(project, "Scripts/Assembly-CSharp", "original bytes")
            meta = game.with_suffix(".cs.meta")
            meta.write_bytes(b"exact-byte-fixture")
            with patch("scripts.adapt_original_save_paths.adapt",
                       side_effect=lambda text: text + "\n// inspected"):
                result = apply(project, root / "backup", write=False)
            self.assertTrue(result["changed"])
            self.assertFalse(result["applied"])
            self.assertEqual(game.read_text(), "original bytes")
            self.assertEqual(meta.read_bytes(), b"exact-byte-fixture")
            self.assertFalse((root / "backup").exists())


if __name__ == "__main__":
    unittest.main()
