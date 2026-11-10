"""Source-free regression fixtures for T3's read-only Unity GUID link audit."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_unity_guid_link_audit.py"
spec = importlib.util.spec_from_file_location("t3_guid_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

A = "a" * 32
B = "b" * 32
C = "c" * 32
ZERO = "0" * 32


class GuidAuditContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8")

    def test_resolved_unresolved_builtin_and_order(self):
        self.put("Assets/known.mat.meta", "fileFormatVersion: 2\nguid: " + A + "\n")
        self.put("Assets/scene.unity", "\n".join([
            "m_Material: {fileID: 2100000, guid: " + A + ", type: 2}",
            "m_Shader: {guid: " + B + ", fileID: 4800000, type: 3}",
            "m_Null: {fileID: 0, guid: " + ZERO + ", type: 0}",
            "m_Broken: {fileID: 2100000, guid: " + C + ", type: 2}",
        ]))
        result = audit.inspect(self.root)
        self.assertEqual(result["status"], "STATIC_PARTIAL_TREE_ONLY")
        self.assertEqual(result["meta_files_indexed"], 1)
        self.assertEqual(result["yaml_files_scanned"], 1)
        self.assertEqual(result["reference_counts"], {
            "builtin_or_null": 1,
            "resolved_in_supplied_tree": 1,
            "unresolved_in_supplied_tree": 2,
        })

    def test_duplicate_meta_guid_is_reported(self):
        self.put("Assets/one.mat.meta", "guid: " + A + "\n")
        self.put("Assets/two.mat.meta", "guid: " + A + "\n")
        result = audit.inspect(self.root)
        self.assertEqual(result["duplicate_guid_groups"], 1)
        self.assertEqual(result["meta_files_indexed"], 2)

    def test_no_cross_reference_field_stitching(self):
        self.put("Assets/a.prefab", "x: {fileID: 2100000}\ny: {guid: " + B + ", type: 2}\n")
        self.assertEqual(audit.inspect(self.root)["reference_counts"], {})

    def test_unresolved_references_are_grouped_by_source_extension(self):
        self.put("Assets/smoke.mat", "m_Shader: {fileID: 4800000, guid: " + B + ", type: 3}\n")
        self.put("Assets/raft.prefab", "m_Material: {guid: " + C + ", fileID: 2100000, type: 2}\n")
        self.put("Assets/scene.unity", "m_Material: {fileID: 2100000, guid: " + B + ", type: 2}\n")
        result = audit.inspect(self.root)
        self.assertEqual(result["reference_counts"]["unresolved_in_supplied_tree"], 3)
        self.assertEqual(result["unresolved_by_source_extension"], {
            ".mat": 1, ".prefab": 1, ".unity": 1,
        })

    def test_non_yaml_and_oversized_skipped(self):
        self.put("Assets/notes.txt", "{fileID: 1, guid: " + B + "}")
        self.put("Assets/small.mat", "{fileID: 1, guid: " + B + "}")
        self.assertEqual(audit.inspect(self.root)["yaml_files_scanned"], 1)


if __name__ == "__main__":
    unittest.main()
