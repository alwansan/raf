import tempfile
import unittest
from pathlib import Path
from scripts.t3_material_texture_binding_audit import audit, reference

A = "a" * 32
B = "b" * 32
C = "c" * 32

class TextureBindingTests(unittest.TestCase):
    def test_reference(self):
        self.assertEqual(reference("fileID: 0"), ("null", None))
        self.assertEqual(reference("fileID: 2800000, guid: " + A + ", type: 3"), ("external", A))
        self.assertEqual(reference("fileID: 2800000"), ("builtin_or_local", None))
        self.assertEqual(reference("guid: invalid, fileID: 2800000"), ("malformed", None))

    def test_consecutive_slots_missing_texture_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.mat").write_text(
                "Material:\n  m_SavedProperties:\n    m_TexEnvs:\n"
                "    - _Missing:\n        m_Scale: {x: 1, y: 1}\n"
                "    - _Null:\n        m_Texture: {fileID: 0}\n"
                "    - _LastMissing:\n        m_Offset: {x: 0, y: 0}\n"
                "    m_Floats:\n"
            )
            counts = audit(root)["counts"]
            self.assertEqual(counts["texenv_slots_seen"], 3)
            self.assertEqual(counts["texenv_slots_without_texture_line"], 2)
            self.assertEqual(counts["texture_null"], 1)

    def test_asset_meta_is_ambiguous_not_proven_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "opaque.asset").write_text("not a proven Texture2D")
            (root / "opaque.asset.meta").write_text("guid: " + A + "\n")
            (root / "sample.mat").write_text(
                "Material:\n  m_SavedProperties:\n    m_TexEnvs:\n"
                "    - _MainTex:\n        m_Texture: {fileID: 2800000, guid: " + A + ", type: 3}\n"
                "    m_Floats:\n"
            )
            counts = audit(root)["counts"]
            self.assertEqual(counts["texture_guid_ambiguous_asset_meta"], 1)
            self.assertEqual(counts.get("texture_guid_unique_texture_meta", 0), 0)

    def test_scoped_slots_and_owner_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "image.png").write_bytes(b"x")
            (root / "image.png.meta").write_text("guid: " + A + "\n")
            (root / "other.shader").write_text("Shader \"X\" {}")
            (root / "other.shader.meta").write_text("guid: " + B + "\n")
            (root / "sample.mat").write_text(
                "Material:\n  m_SavedProperties:\n    m_TexEnvs:\n"
                "    - _MainTex:\n        m_Texture: {fileID: 2800000, guid: " + A + ", type: 3}\n"
                "    - _BumpMap:\n        m_Texture: {fileID: 2800000, guid: " + B + ", type: 3}\n"
                "    - _Mask:\n        m_Texture: {fileID: 2800000, guid: " + C + ", type: 3}\n"
                "    - _Null:\n        m_Texture: {fileID: 0}\n"
                "    m_Floats:\n      - first: _Value\n        second: 1\n"
                "    m_Texture: {fileID: 2800000, guid: " + C + ", type: 3}\n"
            )
            counts = audit(root)["counts"]
            self.assertEqual(counts["texenv_slots_seen"], 4)
            self.assertEqual(counts["texture_guid_unique_texture_meta"], 1)
            self.assertEqual(counts["texture_guid_points_to_nontexture_meta"], 1)
            self.assertEqual(counts["texture_guid_absent_from_supplied_tree"], 1)
            self.assertEqual(counts["texture_null"], 1)

if __name__ == "__main__":
    unittest.main()
