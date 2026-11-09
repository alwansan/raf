"""Synthetic-only test of T3 34-slot smoke Shader48→one export instance.

No Raft original assets, shader source names or real IDs in this test.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_smoke34_sameexport_shaderlab as m
from scripts.probe_a13_exported_material_shader_guids import BUILTIN

SRC = ("resources.assets", 777)
GUID = "a" * 32
INSTANCE = "e" * 32
PROGRAM = '''Shader "Synthetic/Smoke" {
SubShader {
 Pass {
  ColorMask RGB
  Blend SrcAlpha OneMinusSrcAlpha, SrcAlpha OneMinusSrcAlpha
  ZWrite Off
  Cull Off
  CGPROGRAM
  float4 v() : SV_Target { return 0; }
  ENDCG
 }
}
}'''


def traces(guid=GUID, kind=3):
    w = {"schema_version": 1, "export_instance": INSTANCE, "objects": [
        {"class_id": 48,
         "source": {"owner": "Raft_Data/" + SRC[0], "path_id": SRC[1]},
         "export": {"file_id": 4800000, "guid": guid, "type": kind}},
        {"class_id": 21,
         "source": {"owner": "Raft_Data/" + SRC[0], "path_id": 778},
         "export": {"file_id": 2100000, "guid": "c" * 32, "type": 2}},
    ]}
    b = {"schema_version": 1, "export_instance": INSTANCE, "objects": [
        {"class_id": 28,
         "source": {"owner": "Raft_Data/" + SRC[0], "path_id": 779},
         "export": {"file_id": 2800000, "guid": "d" * 32, "type": 2}},
    ]}
    return w, b


def write_assets(path, code, guid=GUID):
    path.mkdir(parents=True, exist_ok=True)
    (path / "synthetic.shader.meta").write_text(
        "fileFormatVersion: 2\nguid: " + guid + "\n", encoding="utf-8")
    (path / "synthetic.shader").write_text(code, encoding="utf-8")


class SameExportSourceOnly(unittest.TestCase):
    def test_true_exact_guid_programmed_pass_is_only_structure(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(assets, PROGRAM)
            result = m.compare_same_export(SRC, *traces(), assets)
            self.assertEqual(result["status"], m.STATUS)
            self.assertEqual(result["selected_shaderlab_pass_count"], 1)
            self.assertEqual(result["selected_shaderlab_complete_program_pass_count"], 1)
            self.assertTrue(result["lexical_shaderlab_colormask_RGB_seen"])
            self.assertFalse(result["lexical_colormask_active_pass_or_runtime_proven"])
            self.assertEqual(result["export_shader_status"],
                             "PROGRAMMED_STRUCTURAL_PASS_NOT_AUTHENTICITY")
            self.assertFalse(result["android_game_device_smoke_pixels_verified"])
            public = json.dumps(result, sort_keys=True)
            for private in (GUID, INSTANCE, "resources.assets", "synthetic.shader",
                            "Synthetic/Smoke", "777", "4800000"):
                self.assertNotIn(private, public)

    def test_dummy_marker_overrides_superficially_valid_program(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(
                assets, "//DummyShaderTextExporter\n" + PROGRAM)
            result = m.compare_same_export(SRC, *traces(), assets)
            self.assertEqual(result["export_shader_status"],
                             "ACTUAL_DUMMY_SHADER_TEXT_EXPORTER")
            self.assertTrue(result["selected_shaderlab_dummy_exporter_marker"])
            self.assertFalse(result["exported_active_pass_equivalence_proven"])

    def test_no_subprogram_fails_as_source_quality(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(assets,
                '// No subprograms found\nShader "Synthetic" { SubShader {Pass{}} }')
            result = m.compare_same_export(SRC, *traces(), assets)
            self.assertEqual(result["export_shader_status"],
                             "NO_PROGRAM_SUBPROGRAMS_EXPORTED")

    def test_meta_and_text_missing_never_assumed_success(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d)
            result = m.compare_same_export(SRC, *traces(), assets)
            self.assertEqual(result["export_shader_status"],
                             "CUSTOM_SHADER_META_MISSING")
            (assets / "synthetic.shader.meta").write_text(
                "guid: " + GUID + "\n", encoding="utf-8")
            result = m.compare_same_export(SRC, *traces(), assets)
            self.assertEqual(result["export_shader_status"],
                             "CUSTOM_SHADER_TEXT_MISSING")

    def test_duplicate_guid_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(assets, PROGRAM)
            sub = assets / "copy"; sub.mkdir()
            (sub / "other.shader.meta").write_text(
                "guid: " + GUID + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                m.compare_same_export(SRC, *traces(), assets)

    def test_cross_instance_and_missing_48_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(assets, PROGRAM)
            w, b = traces(); b["export_instance"] = "f" * 32
            with self.assertRaisesRegex(ValueError, "Different exporter instances"):
                m.compare_same_export(SRC, w, b, assets)
            w, b = traces()
            w["objects"] = [x for x in w["objects"] if x["class_id"] != 48]
            with self.assertRaisesRegex(ValueError, "missing_or_duplicate"):
                m.compare_same_export(SRC, w, b, assets)

    def test_nonselected_fire34_trace_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            assets = Path(d); write_assets(assets, PROGRAM)
            w, b = traces()
            w["objects"][0]["source"]["path_id"] = 999
            with self.assertRaises(ValueError):
                m.compare_same_export(SRC, w, b, assets)

    def test_builtin_no_custom_shader_claim(self):
        with tempfile.TemporaryDirectory() as d:
            builtin = next(iter(sorted(BUILTIN - {"0" * 32})))
            result = m.compare_same_export(
                SRC, *traces(guid=builtin, kind=0), Path(d))
            self.assertEqual(result["export_shader_status"],
                             "UNITY_BUILTIN_REFERENCE_NO_CUSTOM_SHADERLAB")
            self.assertFalse(result["actual_exported_custom_shader"])

    def test_lexical_mask_from_comment_does_not_claim_RGB(self):
        d = m.lexical_colormask_scope(
            '// ColorMask RGB\nShader "Synthetic" { SubShader {Pass { ColorMask RGBA\n }}}')
        self.assertFalse(d["lexical_shaderlab_colormask_RGB_seen"])
        self.assertTrue(d["lexical_shaderlab_colormask_RGBA_seen"])

    def test_lexical_only_even_valid_RGB_with_fake_string(self):
        d = m.lexical_colormask_scope(
            'Shader "ColorMask RGB" { SubShader { Pass { ColorMask RGB\n }} }')
        self.assertTrue(d["lexical_shaderlab_colormask_RGB_seen"])
        self.assertFalse(d["lexical_colormask_active_pass_or_runtime_proven"])


if __name__ == "__main__":
    unittest.main()
