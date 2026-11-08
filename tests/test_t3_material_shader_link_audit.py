import tempfile
import unittest
from pathlib import Path
from scripts.t3_material_shader_link_audit import audit

class MaterialShaderAuditTests(unittest.TestCase):
    def test_resolved_unresolved_builtin_null_and_unparsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = "a" * 32
            absent = "b" * 32
            (root / "Known.shader").write_text('Shader "Test/Known" {}\n')
            (root / "Known.shader.meta").write_text("fileFormatVersion: 2\nguid: " + good + "\n")
            for name, fid, guid in [
                ("known", 4800000, good),
                ("absent", 4800000, absent),
                ("builtin", 4800000, "0" * 32),
                ("null", 0, "0" * 32),
            ]:
                (root / (name + ".mat")).write_text(
                    "%YAML 1.1\nMaterial:\n  m_Shader: {fileID: %d, guid: %s, type: 3}\n" % (fid, guid))
            (root / "invalid.mat").write_text("Material:\n  m_Shader: malformed\n")
            result = audit(root)
            self.assertEqual(result["material_seen"], 5)
            self.assertEqual(result["shader_guid_resolved_in_scan"], 1)
            self.assertEqual(result["shader_guid_unresolved_in_scan"], 1)
            self.assertEqual(result["shader_pointer_builtin_or_null"], 1)
            self.assertEqual(result["shader_pointer_null"], 1)
            self.assertEqual(result["material_shader_pointer_unparsed"], 1)
            self.assertEqual(result["shader_meta_seen"], 1)
            self.assertNotIn(good, str(result))
            self.assertNotIn(absent, str(result))

    def test_dangling_shader_meta_is_not_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            guid = "c" * 32
            (root / "Orphan.shader.meta").write_text("fileFormatVersion: 2\nguid: " + guid + "\n")
            (root / "orphan.mat").write_text(
                "Material:\n  m_Shader: {fileID: 4800000, guid: %s, type: 3}\n" % guid)
            result = audit(root)
            self.assertEqual(result["shader_meta_without_source"], 1)
            self.assertEqual(result["shader_guid_unresolved_in_scan"], 1)
            self.assertEqual(result["shader_guid_resolved_in_scan"], 0)

    def test_duplicate_shader_guid_is_ambiguous_not_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            guid = "d" * 32
            for name in ("One", "Two"):
                (root / (name + ".shader")).write_text('Shader "Test/' + name + '" {}\n')
                (root / (name + ".shader.meta")).write_text("guid: " + guid + "\n")
            (root / "duplicate.mat").write_text(
                "Material:\n  m_Shader: {fileID: 4800000, guid: %s, type: 3}\n" % guid)
            result = audit(root)
            self.assertEqual(result["shader_guid_ambiguous_in_scan"], 1)
            self.assertEqual(result["shader_guid_resolved_in_scan"], 0)
            self.assertEqual(result["shader_guid_unresolved_in_scan"], 0)
            self.assertEqual(result["duplicate_shader_guid_entries"], 1)
            self.assertNotIn(guid, str(result))

    def test_nonexistent_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                audit(Path(tmp) / "missing")

if __name__ == "__main__":
    unittest.main()
