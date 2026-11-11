"""T3 duplicate GUID ambiguity regression: synthetic fixtures only."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t3_unity_guid_link_audit import inspect


class DuplicateGuidAmbiguityTests(unittest.TestCase):
    def test_duplicate_owner_is_ambiguous_not_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            duplicate = "a" * 32
            unique = "b" * 32
            missing = "c" * 32
            for name in ("first.shader.meta", "second.shader.meta"):
                (root / name).write_text("fileFormatVersion: 2\nguid: " + duplicate + "\n", encoding="utf-8")
            (root / "unique.shader.meta").write_text("guid: " + unique + "\n", encoding="utf-8")
            (root / "effect.mat").write_text(
                "m_Shader: {fileID: 4800000, guid: " + duplicate + ", type: 3}\n"
                "m_Texture: {guid: " + unique + ", fileID: 2800000, type: 3}\n"
                "m_Unknown: {fileID: 2800000, guid: " + missing + ", type: 3}\n"
                "m_Null: {fileID: 0, guid: " + "0" * 32 + ", type: 0}\n",
                encoding="utf-8",
            )
            report = inspect(root)
            counts = report["reference_counts"]
            self.assertEqual(report["duplicate_guid_groups"], 1)
            self.assertEqual(report["ambiguous_duplicate_guid_references"], 1)
            self.assertEqual(counts["ambiguous_duplicate_guid_in_supplied_tree"], 1)
            self.assertEqual(counts["resolved_in_supplied_tree"], 1)
            self.assertEqual(counts["unresolved_in_supplied_tree"], 1)
            self.assertEqual(counts["builtin_or_null"], 1)
            self.assertNotIn(duplicate, str(report))

    def test_duplicate_without_reference_is_not_ambiguous_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("one.mat.meta", "two.mat.meta"):
                (root / name).write_text("guid: " + "d" * 32 + "\n", encoding="utf-8")
            report = inspect(root)
            self.assertEqual(report["duplicate_guid_groups"], 1)
            self.assertEqual(report["ambiguous_duplicate_guid_references"], 0)


if __name__ == "__main__":
    unittest.main()
