"""A13 synthetic exported Unity Material->Shader GUID regression tests; no game data."""
from pathlib import Path
import tempfile
import unittest

from scripts.probe_a13_exported_material_shader_guids import GuardError, audit, main

G = "a" * 32
B = "b" * 32
BUILTIN = "0000000000000000f000000000000000"


class MaterialShaderGuidTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.assets = self.root / "Assets"
        self.assets.mkdir()
        self.shader("main", G)
        self.material("one", G)

    def shader(self, name, guid):
        (self.assets / (name + ".shader")).write_text('Shader "Synthetic" {}\n')
        (self.assets / (name + ".shader.meta")).write_text("fileFormatVersion: 2\nguid: " + guid + "\n")

    def material(self, name, guid, fid=4800000, kind=3):
        (self.assets / (name + ".mat")).write_text(
            "--- !u!21 &2100000\nMaterial:\n  m_Name: Synthetic\n  m_Shader: {fileID: "
            + str(fid) + ", guid: " + guid + ", type: " + str(kind) + "}\n")

    def test_local_export_link_and_scope_limits(self):
        r = audit(self.root)
        self.assertEqual(r["material_objects"], 1)
        self.assertEqual(r["resolved_shader_guids"], 1)
        self.assertFalse(r["original_export_provenance_verified"])
        self.assertFalse(r["original_material_link_equivalence_verified"])
        self.assertFalse(r["ready_for_build"])

    def test_multiple_materials_one_shader(self):
        self.material("two", G)
        r = audit(self.root, expected_materials=2)
        self.assertEqual(r["resolved_shader_guids"], 2)
        self.assertEqual(r["distinct_target_shader_guids"], 1)

    def test_builtin_transport_not_resolved_to_custom(self):
        self.material("two", BUILTIN, fid=46, kind=0)
        r = audit(self.root, expected_materials=2)
        self.assertEqual(r["builtin_transport_unresolved"], 1)
        self.assertEqual(r["resolved_shader_guids"], 1)

    def test_missing_shader_guid_rejected(self):
        self.material("one", B)
        with self.assertRaisesRegex(GuardError, "missing_or_wrong_type"):
            audit(self.root)

    def test_guid_of_non_shader_meta_rejected(self):
        (self.assets / "notshader.asset.meta").write_text("guid: " + B + "\n")
        self.material("one", B)
        with self.assertRaisesRegex(GuardError, "missing_or_wrong_type"):
            audit(self.root)

    def test_duplicate_guids_rejected(self):
        (self.assets / "other.asset.meta").write_text("guid: " + G + "\n")
        with self.assertRaisesRegex(GuardError, "duplicate"):
            audit(self.root)

    def test_orphan_shader_meta_rejected(self):
        (self.assets / "main.shader").unlink()
        with self.assertRaisesRegex(GuardError, "orphan"):
            audit(self.root)

    def test_missing_shader_meta_rejected(self):
        (self.assets / "main.shader.meta").unlink()
        with self.assertRaisesRegex(GuardError, "missing_shader_meta"):
            audit(self.root)

    def test_null_and_negative_fileids_rejected(self):
        for fid in (0, -1):
            with self.subTest(fid=fid):
                self.material("one", G, fid=fid)
                with self.assertRaisesRegex(GuardError, "null_or_negative"):
                    audit(self.root)

    def test_wrong_type_for_custom_and_builtin_rejected(self):
        self.material("one", G, kind=0)
        with self.assertRaisesRegex(GuardError, "invalid_custom"):
            audit(self.root)
        self.material("one", BUILTIN, kind=3)
        with self.assertRaisesRegex(GuardError, "invalid_builtin"):
            audit(self.root)

    def test_missing_multiple_and_malformed_m_shader_rejected(self):
        p = self.assets / "one.mat"
        original = p.read_text()
        for bad in (
            original.replace("m_Shader:", "notShader:"),
            original + "  m_Shader: {fileID: 4, guid: " + G + ", type: 3}\n",
            original.replace(G, "invalid"),
            original.replace(", type: 3", ", type: 3, type: 3"),
        ):
            with self.subTest(bad=bad[:45]):
                p.write_text(bad)
                with self.assertRaises(GuardError):
                    audit(self.root)
        p.write_text(original)

    def test_symlinked_asset_rejected(self):
        (self.assets / "redirect.shader").symlink_to(self.assets / "main.shader")
        with self.assertRaisesRegex(GuardError, "symlinked"):
            audit(self.root)

    def test_no_material_rejected(self):
        (self.assets / "one.mat").unlink()
        with self.assertRaisesRegex(GuardError, "no_exported_materials"):
            audit(self.root)

    def test_expected_material_count_not_assumed(self):
        with self.assertRaisesRegex(GuardError, "expected_material_count_mismatch"):
            audit(self.root, expected_materials=1556)

    def test_cli_fails_closed(self):
        self.material("one", B)
        self.assertEqual(main(["--project", str(self.root)]), 2)


if __name__ == "__main__":
    unittest.main()
