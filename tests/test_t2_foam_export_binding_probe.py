"""Synthetic-only test suite for T2 read-only Foam exported GUID and Material PPtr proof.

Never embeds original game source/assets/metadata, private shader symbols, or
material identifiers besides public Foam ShaderLab identity and fake GUIDs.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.b24_original_foam_stage_translation import TARGET
from scripts.t2_foam_export_binding_probe import inspect_export

A = "a" * 32
B = "b" * 32
ORIGINAL_PASS = (
    'Shader "' + TARGET + '" { SubShader { '
    'Pass { HLSLPROGRAM\nfloat4 main():SV_Target{return 1;}\nENDHLSL } } }\n'
)
TWO_PASS = ORIGINAL_PASS.replace(
    "ENDHLSL } } }", "ENDHLSL } Pass { HLSLPROGRAM\nfloat4 main():SV_Target{return 1;}\nENDHLSL } } }"
)
MATERIAL = (
    "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n"
    "  m_Name: SyntheticFixture\n  m_Shader: {fileID: 4800000, guid: " + A + ", type: 3}\n"
)


def fixture(base: str):
    project = Path(base) / "Unity"
    assets = project / "Assets"
    shaders = assets / "Shaders"
    shaders.mkdir(parents=True)
    shader = shaders / "SyntheticFoam.shader"
    shader.write_text(ORIGINAL_PASS, encoding="utf-8")
    meta = Path(str(shader) + ".meta")
    meta.write_text("fileFormatVersion: 2\nguid: " + A + "\n")
    material = assets / "Material.mat"
    material.write_text(MATERIAL, encoding="utf-8")
    return project, shader, meta, material


class FoamExportBindingProbeTests(unittest.TestCase):
    def test_single_exported_Foam_and_exact_synthetic_material(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            r = inspect_export(project)
            self.assertEqual(r["status"], "EXPORTED_FOAM_GUID_MATERIAL_STRUCTURAL_PROBE_ONLY")
            self.assertEqual(r["exact_Foam_exported_ShaderLab_targets"], 1)
            self.assertEqual(r["foam_exported_subshader_pass_counts"], [1])
            self.assertEqual(r["material_documents"], 1)
            self.assertEqual(r["material_docs_referencing_exported_Foam_guid"], 1)
            self.assertFalse(r["exported_Foam_meta_guid_original_Unity_PPtr_proven"])
            self.assertFalse(r["Foam_Material_links_at_runtime_verified"])
            self.assertFalse(r["android_Foam_pixels_verified"])
            self.assertFalse(r["modified_exported_Assets"])
            self.assertNotIn(A, str(r))
            self.assertNotIn(str(shader), str(r))

    def test_post_source_candidate_two_pass_keeps_material_identity(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            before = inspect_export(project)
            guid_bytes = meta.read_bytes()
            material_bytes = material.read_bytes()
            shader.write_text(TWO_PASS, encoding="utf-8")
            after = inspect_export(project)
            self.assertEqual(after["foam_exported_subshader_pass_counts"], [2])
            self.assertEqual(after["material_docs_referencing_exported_Foam_guid"],
                             before["material_docs_referencing_exported_Foam_guid"])
            self.assertEqual(before["material_documents"], after["material_documents"])
            self.assertEqual(meta.read_bytes(), guid_bytes)
            self.assertEqual(material.read_bytes(), material_bytes)
            self.assertFalse(after["unity_shader_import_compile_verified"])

    def test_zero_serialized_Material_refs_is_not_false_unbound_claim(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.unlink()
            r = inspect_export(project)
            self.assertEqual(r["material_documents"], 0)
            self.assertEqual(r["material_docs_referencing_exported_Foam_guid"], 0)
            self.assertFalse(r["Foam_Material_links_at_runtime_verified"])

    def test_wrong_guid_material_is_not_a_Foam_link(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.write_text(MATERIAL.replace(A, B), encoding="utf-8")
            r = inspect_export(project)
            self.assertEqual(r["material_documents"], 1)
            self.assertEqual(r["material_docs_other_nonnull_Shader"], 1)
            self.assertEqual(r["material_docs_referencing_exported_Foam_guid"], 0)

    def test_material_pointer_wrong_fileID_fails(self):
        for file_id in ("0", "4800001", "-1"):
            with tempfile.TemporaryDirectory() as d:
                project, shader, meta, material = fixture(d)
                material.write_text(MATERIAL.replace("fileID: 4800000",
                                                  "fileID: " + file_id), encoding="utf-8")
                with self.subTest(file_id=file_id), self.assertRaises(ValueError):
                    inspect_export(project)

    def test_material_pointer_wrong_type_fails(self):
        for typ in ("0", "1", "2"):
            with tempfile.TemporaryDirectory() as d:
                project, shader, meta, material = fixture(d)
                material.write_text(MATERIAL.replace("type: 3", "type: " + typ), encoding="utf-8")
                with self.subTest(typ=typ), self.assertRaises(ValueError):
                    inspect_export(project)

    def test_duplicate_Material_mShader_fields_refused(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.write_text(MATERIAL + "  m_Shader: {fileID: 4800000, guid: " + A + ", type: 3}\n")
            with self.assertRaises(ValueError):
                inspect_export(project)

    def test_fake_text_link_outside_Material_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.unlink()
            fake = project / "Assets" / "Fake.prefab"
            fake.write_text("%YAML 1.1\n--- !u!1 &1\nGameObject:\n"
                            "  m_Shader: {fileID: 4800000, guid: " + A + ", type: 3}\n")
            self.assertEqual(inspect_export(project)["material_docs_referencing_exported_Foam_guid"], 0)

    def test_nonYaml_material_file_refused_not_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.write_text("A fake non-YAML material with a string GUID")
            with self.assertRaises(ValueError):
                inspect_export(project)

    def test_duplicate_Foam_ShaderLab_identity_refused(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            second = shader.parent / "OtherFoam.shader"
            second.write_text(ORIGINAL_PASS)
            Path(str(second) + ".meta").write_text("guid: " + B + "\n")
            with self.assertRaises(ValueError):
                inspect_export(project)

    def test_missing_Foam_ShaderLab_identity_refused(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            shader.write_text('Shader "Synthetic/Other" { SubShader {} }')
            with self.assertRaises(ValueError):
                inspect_export(project)

    def test_duplicate_meta_guid_in_unrelated_asset_refused(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            unrelated = project / "Assets" / "Scene.prefab.meta"
            unrelated.write_text("fileFormatVersion: 2\nguid: " + A + "\n")
            with self.assertRaises(ValueError):
                inspect_export(project)

    def test_missing_or_ambiguous_Foam_meta_refused(self):
        for mode in ("missing", "duplicate_guid_lines", "bad_guid", "zero_guid"):
            with tempfile.TemporaryDirectory() as d:
                project, shader, meta, material = fixture(d)
                if mode == "missing":
                    meta.unlink()
                elif mode == "duplicate_guid_lines":
                    meta.write_text("guid: " + A + "\nguid: " + B + "\n")
                elif mode == "bad_guid":
                    meta.write_text("guid: not-a-guid\n")
                else:
                    meta.write_text("guid: " + "0" * 32 + "\n")
                with self.subTest(mode=mode), self.assertRaises(ValueError):
                    inspect_export(project)

    def test_symlinked_yaml_or_meta_and_assets_rejected(self):
        for mode in ("mat", "meta", "assets"):
            with tempfile.TemporaryDirectory() as d:
                project, shader, meta, material = fixture(d)
                if mode == "assets":
                    source = project / "Assets"
                    outside = Path(d) / "outside_assets"
                    source.rename(outside)
                    source.symlink_to(outside, target_is_directory=True)
                else:
                    file = {"mat": material, "meta": meta}[mode]
                    other = Path(d) / ("outside_" + mode)
                    other.write_bytes(file.read_bytes())
                    file.unlink()
                    file.symlink_to(other)
                with self.subTest(mode=mode), self.assertRaises(ValueError):
                    inspect_export(project)

    def test_material_and_other_doc_mixed(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            material.write_text(MATERIAL + "\n--- !u!1 &10\nGameObject:\n  m_Shader: {fileID: 4800000, guid: " + A + ", type: 3}\n")
            r = inspect_export(project)
            self.assertEqual(r["material_documents"], 1)
            self.assertEqual(r["material_docs_referencing_exported_Foam_guid"], 1)

    def test_unbalanced_ShaderLab_is_invalid_even_with_correct_Guid(self):
        with tempfile.TemporaryDirectory() as d:
            project, shader, meta, material = fixture(d)
            shader.write_text(ORIGINAL_PASS[:-3], encoding="utf-8")
            with self.assertRaises(ValueError):
                inspect_export(project)


if __name__ == "__main__":
    unittest.main()
