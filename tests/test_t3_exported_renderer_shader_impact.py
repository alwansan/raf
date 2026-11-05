"""T3 isolated aggregate-only Renderer→Material→Shader join regression controls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_audit_exported_material_programs as t3
from scripts import t3_exported_renderer_shader_impact as impact

D = "1" * 32
N = "2" * 32
E = "3" * 32
M1 = "a" * 32
M2 = "b" * 32
M3 = "c" * 32
M4 = "d" * 32
SCENE = "e" * 32
UNKNOWN = "f" * 32
BUILTIN = "0000000000000000f000000000000000"
PROGRAM = 'Shader "Synthetic" { SubShader { Pass { CGPROGRAM\nfloat4 frag():SV_Target{return 1;}\nENDCG } } }'


class RendererShaderImpact(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.project = Path(t.name)
        self.assets = self.project / "Assets"
        self.assets.mkdir()
        self.shader("dummy", D, True)
        self.shader("non", N, False)
        self.shader("dummy2", E, True)
        self.material("m1", M1, D)
        self.material("m2", M2, D)
        self.material("m3", M3, E)
        self.material("m4", M4, N)
        self.scene([
            [(2100000, M1, 2), (2100000, M2, 2),
             (2100000, M4, 2), (0, "0"*32, 0), (42, BUILTIN, 0),
             (2100000, UNKNOWN, 2)],
            [(2100000, M3, 2), (2100000, M1, 2)],
        ])

    def file(self, name, text, guid):
        path = self.assets / name
        path.write_text(text, encoding="utf-8")
        (self.assets / (name + ".meta")).write_text(
            "fileFormatVersion: 2\nguid: " + guid + "\n", encoding="utf8")
        return path

    def shader(self, name, guid, dummy):
        self.file(name + ".shader",
                  ("//DummyShaderTextExporter\n" if dummy else "") + PROGRAM,
                  guid)

    def material(self, name, guid, shader_guid):
        return self.file(name + ".mat",
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
            "--- !u!21 &2100000\nMaterial:\n"
            "  m_Name: PrivateSyntheticOriginal\n"
            "  m_Shader: {fileID: 4800000, guid: " + shader_guid + ", type: 3}\n",
            guid)

    def scene(self, renderer_rows):
        raw = "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
        for index, slots in enumerate(renderer_rows, 1):
            raw += "--- !u!23 &" + str(index) + "\nMeshRenderer:\n  m_Materials:\n"
            if not slots:
                raw = raw[:-len("  m_Materials:\n")] + "  m_Materials: []\n"
                continue
            for fid, guid, pointer_type in slots:
                raw += "  - {fileID: %s, guid: %s, type: %s}\n" % (fid, guid, pointer_type)
        return self.file("PrivateName.unity", raw, SCENE)

    def test_real_serialized_material_slot_join_is_not_material_doc_count(self):
        r = impact.audit(self.project, t3.audit(self.project))
        c = r["counts"]
        self.assertEqual(r["status"], impact.RESULT_STATUS)
        self.assertEqual(r["source_material_documents"], 4)
        self.assertEqual(r["source_material_documents_with_dummy_shader"], 3)
        self.assertEqual(c["renderer_objects"], 2)
        self.assertEqual(c["renderer_material_slots"], 8)
        self.assertEqual(c["renderer_slots_resolved_material"], 5)
        self.assertEqual(c["renderer_slots_dummy_shader"], 4)
        self.assertEqual(c["renderer_slots_non_dummy_shader"], 1)
        self.assertEqual(c["renderer_objects_with_at_least_one_dummy_shader_slot"], 2)
        self.assertEqual(c["renderer_slots_null_material"], 1)
        self.assertEqual(c["renderer_slots_builtin_material_unverified"], 1)
        self.assertEqual(c["renderer_slots_unresolved_material"], 1)
        self.assertEqual(r["distinct_renderer_referenced_dummy_shader_targets"], 2)
        self.assertEqual(r["renderer_slot_dummy_target_frequency_bands"],
                         {"1": 1, "2_to_4": 1, "5_to_16": 0, "17_plus": 0})
        self.assertFalse(r["full_native_unity_import_or_android_pixels_verified"])

    def test_no_private_guid_path_name_or_object_id_in_aggregate(self):
        serial = json.dumps(impact.audit(self.project))
        for secret in (D, N, E, M1, M2, M3, M4, SCENE, UNKNOWN,
                       "PrivateName.unity", "PrivateSyntheticOriginal",
                       str(self.project)):
            self.assertNotIn(secret, serial)

    def test_same_export_material_quality_must_match(self):
        previous = t3.audit(self.project)
        previous["counts"]["material_docs_using_dummy_Shader"] += 1
        with self.assertRaisesRegex(ValueError, "same_export"):
            impact.audit(self.project, previous)
        with self.assertRaisesRegex(ValueError, "same_export"):
            impact.audit(self.project, {"status": "WRONG"})

    def test_unresolved_renderer_reference_is_not_assumed_restored(self):
        r = impact.audit(self.project)
        self.assertEqual(r["counts"]["renderer_slots_unresolved_material"], 1)
        self.assertEqual(r["counts"]["renderer_slots_dummy_shader"], 4)

    def test_shader_type_pointer_invalid_is_bounded_unknown(self):
        self.scene([[(2100000, M1, 9)]])
        r = impact.audit(self.project)
        self.assertEqual(r["counts"]["renderer_slots_unsupported_pointer_type"], 1)
        self.assertEqual(r["counts"]["renderer_slots_dummy_shader"], 0)

    def test_malformed_material_shader_field_rejected(self):
        path = self.assets / "m1.mat"
        path.write_text(path.read_text().replace("m_Shader: ", "notShader: "))
        with self.assertRaises(ValueError):
            impact.audit(self.project)

    def test_duplicate_exported_yaml_meta_rejected(self):
        (self.assets / "m4.mat.meta").write_text(
            (self.assets / "m1.mat.meta").read_text())
        with self.assertRaisesRegex(ValueError, "duplicate_exported_YAML_meta_guid"):
            impact.audit(self.project)

    def test_duplicate_renderer_anchor_rejected(self):
        path = self.assets / "PrivateName.unity"
        raw = path.read_text()
        raw = raw.replace("--- !u!23 &2", "--- !u!23 &1")
        path.write_text(raw)
        with self.assertRaisesRegex(ValueError, "duplicate_or_null_yaml_anchor"):
            impact.audit(self.project)

    def test_symlink_and_report_inside_export_rejected(self):
        (self.assets / "redirect.mat").symlink_to(self.assets / "m1.mat")
        with self.assertRaises(ValueError):
            impact.audit(self.project)
        # Destination validation remains independent of bad source.
        with self.assertRaisesRegex(ValueError, "unsafe_aggregate_report_destination"):
            impact.main(["--project", str(self.project),
                         "--out", str(self.project / "inside.json")])

    def test_no_renderers_stays_inconclusive(self):
        (self.assets / "PrivateName.unity").unlink()
        (self.assets / "PrivateName.unity.meta").unlink()
        with self.assertRaisesRegex(ValueError, "no_exported_Renderer"):
            impact.audit(self.project)


if __name__ == "__main__":
    unittest.main()
