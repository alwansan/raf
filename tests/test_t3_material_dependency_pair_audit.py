"""Source-free controls for T3 material shader/texture pair comparison."""
import tempfile
import unittest
from pathlib import Path
from scripts import t3_material_dependency_pair_audit as audit

A = "a" * 32
B = "b" * 32
S = "c" * 32


def material(first=A, second=B):
    return (f"""%YAML 1.1
Material:
  m_Shader: {{fileID: 4800000, guid: {S}, type: 3}}
  m_SavedProperties:
    m_TexEnvs:
    - _MainTex:
        m_Texture: {{fileID: 2800000, guid: {first}, type: 3}}
        m_Scale: {{x: 1, y: 1}}
    - _BumpMap:
        m_Texture: {{fileID: 2800000, guid: {second}, type: 3}}
        m_Scale: {{x: 1, y: 1}}
    m_Floats:
    - _Glossiness: 0.5
""")


class MaterialPairSlotTests(unittest.TestCase):
    def test_swapped_slots_are_detected_despite_same_guid_multiset(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original"
            exported = Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            (original / "test.mat").write_text(material(), encoding="utf-8")
            (exported / "test.mat").write_text(material(B, A), encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["paired_materials"], 1)
            self.assertEqual(result["counts"]["changed_texture_reference_materials"], 1)
            self.assertNotIn("test.mat", str(result))
            self.assertNotIn(A, str(result))

    def test_same_guid_different_fileid_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            original, exported = Path(temp) / "original", Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            source = material()
            (original / "test.mat").write_text(source, encoding="utf-8")
            (exported / "test.mat").write_text(
                source.replace("fileID: 2800000, guid: " + A,
                               "fileID: 2800001, guid: " + A),
                encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["changed_texture_reference_materials"], 1)
            self.assertNotIn(A, str(result))

    def test_same_pointer_reordered_fields_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            original, exported = Path(temp) / "original", Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            source = material()
            (original / "test.mat").write_text(source, encoding="utf-8")
            (exported / "test.mat").write_text(
                source.replace("fileID: 2800000, guid: " + A + ", type: 3",
                               "type: 3, guid: " + A + ", fileID: 2800000"),
                encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["unchanged_reference_materials"], 1)

    def test_shader_mapping_reordered_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            original, exported = Path(temp) / "original", Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            source = material()
            (original / "test.mat").write_text(source, encoding="utf-8")
            (exported / "test.mat").write_text(
                source.replace("fileID: 4800000, guid: " + S + ", type: 3",
                               "type: 3, guid: " + S + ", fileID: 4800000"),
                encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["unchanged_reference_materials"], 1)
            self.assertEqual(result["counts"].get("changed_shader_reference_materials", 0), 0)

    def test_shader_fileid_change_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            original, exported = Path(temp) / "original", Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            source = material()
            (original / "test.mat").write_text(source, encoding="utf-8")
            (exported / "test.mat").write_text(
                source.replace("fileID: 4800000, guid: " + S,
                               "fileID: 4800001, guid: " + S),
                encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["changed_shader_reference_materials"], 1)

    def test_same_slots_and_shader_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original"
            exported = Path(temp) / "exported"
            original.mkdir()
            exported.mkdir()
            for root in (original, exported):
                (root / "test.mat").write_text(material(), encoding="utf-8")
            result = audit.compare(original, exported)
            self.assertEqual(result["counts"]["unchanged_reference_materials"], 1)
            self.assertEqual(result["counts"].get("changed_texture_reference_materials", 0), 0)


if __name__ == "__main__":
    unittest.main()
