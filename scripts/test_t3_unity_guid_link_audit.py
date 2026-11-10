import tempfile
import unittest
from pathlib import Path
from t3_unity_guid_link_audit import inspect

class GuidAuditTests(unittest.TestCase):
    def test_known_external_and_null(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a = "a" * 32
            b = "b" * 32
            (root / "shader.shader.meta").write_text("fileFormatVersion: 2\\nguid: " + a + "\\n")
            (root / "sample.mat").write_text(
                "m_Shader: {fileID: 4800000, guid: " + a + ", type: 3}\\n"
                "m_Texture: {fileID: 2800000, guid: " + b + ", type: 3}\\n"
                "m_Builtin: {fileID: 0, guid: " + "0"*32 + ", type: 0}\\n"
            )
            result = inspect(root)
            self.assertEqual(result["reference_counts"]["resolved_in_supplied_tree"], 1)
            self.assertEqual(result["reference_counts"]["unresolved_in_supplied_tree"], 1)
            self.assertEqual(result["reference_counts"]["builtin_or_null"], 1)
            self.assertEqual(result["status"], "STATIC_PARTIAL_TREE_ONLY")

    def test_guid_before_fileid_and_no_cross_block_pairing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a = "a" * 32
            b = "b" * 32
            (root / "shader.shader.meta").write_text("guid: " + a + "\\n")
            (root / "sample.mat").write_text(
                "m_Shader: {guid: " + a + ", type: 3, fileID: 4800000}\\n"
                "m_Texture: {guid: " + b + ", fileID: 2800000, type: 3}\\n"
                "m_OnlyGuid: {guid: " + b + "}\\n"
                "m_OnlyFileID: {fileID: 2800000}\\n"
            )
            counts = inspect(root)["reference_counts"]
            self.assertEqual(counts["resolved_in_supplied_tree"], 1)
            self.assertEqual(counts["unresolved_in_supplied_tree"], 1)

    def test_duplicate_meta_guid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("a.meta", "b.meta"):
                (root / name).write_text("guid: " + "f"*32 + "\\n")
            self.assertEqual(inspect(root)["duplicate_guid_groups"], 1)

if __name__ == "__main__":
    unittest.main()
