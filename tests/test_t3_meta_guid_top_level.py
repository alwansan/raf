"""Synthetic-only regression for Unity .meta top-level identity indexing."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_unity_guid_link_audit.py"
spec = importlib.util.spec_from_file_location("t3_unity_guid_link_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

GOOD = "a" * 32
BAD = "b" * 32

class MetaGuidIdentityTest(unittest.TestCase):
    def test_nested_and_commented_guid_cannot_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test.mat.meta").write_text(
                "# guid: " + BAD + "\n" +
                "fileFormatVersion: 2\n" +
                "guid: " + GOOD.upper() + "\n" +
                "nested:\n  guid: " + BAD + "\n", encoding="utf-8")
            (root / "scene.unity").write_text(
                "m_Material: {fileID: 2100000, guid: " + GOOD + ", type: 2}\n" +
                "m_Other: {fileID: 2100000, guid: " + BAD + ", type: 2}\n", encoding="utf-8")
            result = audit.inspect(root)
            self.assertEqual(result["meta_files_indexed"], 1)
            self.assertEqual(result["reference_counts"]["resolved_in_supplied_tree"], 1)
            self.assertEqual(result["reference_counts"]["unresolved_in_supplied_tree"], 1)

    def test_only_nested_guid_does_not_create_meta_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.mat.meta").write_text("nested:\n  guid: " + BAD + "\n", encoding="utf-8")
            (root / "scene.unity").write_text(
                "m_Material: {fileID: 2100000, guid: " + BAD + ", type: 2}\n", encoding="utf-8")
            result = audit.inspect(root)
            self.assertEqual(result["meta_files_indexed"], 0)
            self.assertEqual(result["reference_counts"]["unresolved_in_supplied_tree"], 1)

if __name__ == "__main__":
    unittest.main()
