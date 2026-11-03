"""Synthetic-only source signature and serializable field negative-controls."""
import tempfile
from pathlib import Path
import unittest

from scripts.probe_a2_scaler_raw_shapes import managed_fields, managed_sha, MANAGED_UI_GIT_BLOB


class A2ScalerSchemaTests(unittest.TestCase):
    def test_distinguishes_unverified_serialized_order(self):
        source = """public class CanvasScaler {
          private ScaleMode m_UiScaleMode;
          private float m_ScaleFactor = 1f;
          private Vector2 m_ReferenceResolution = new Vector2(800, 600);
          private ScreenMatchMode m_ScreenMatchMode;
          private float m_MatchWidthOrHeight;
          public bool unrelated;
        }"""
        out = managed_fields(source)
        self.assertEqual(out["field_count"], 5)
        self.assertTrue(out["field_types_match_expected"])
        self.assertFalse(out["source_order_is_verified_serialization_order"])
        self.assertFalse(out["serialized_base_header_length_verified"])
        self.assertNotIn("800", str(out))

    def test_fields_in_comment_or_string_are_not_counted(self):
        source = """class CanvasScaler {
            // private float m_MatchWidthOrHeight;
            string comment = "private ScreenMatchMode m_ScreenMatchMode;";
            private Vector2 m_ReferenceResolution;
        }"""
        out = managed_fields(source)
        self.assertEqual(out["fields_matched"], ["m_ReferenceResolution"])

    def test_wrong_field_type_is_not_accepted_as_metadata_verified(self):
        out = managed_fields("class CanvasScaler { private string m_ScreenMatchMode; }")
        self.assertFalse(out["field_types_match_expected"])
        self.assertEqual(out["field_count"], 1)

    def test_duplicate_source_declaration_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            managed_fields("""class CanvasScaler {
              private float m_ScaleFactor;
              private float m_ScaleFactor;
            }""")

    def test_original_ui_binary_sha_rejects_tampering_and_symlinks(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            f = root / "UnityEngine.UI.dll"
            f.write_bytes(b"synthetic bytes only" * 1000)
            with self.assertRaisesRegex(ValueError, "drift"):
                managed_sha(f)
            f.unlink()
            f.symlink_to("/etc/passwd")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                managed_sha(f)
            self.assertEqual(len(MANAGED_UI_GIT_BLOB), 40)

    def test_suspicious_class_text_length_rejected(self):
        with self.assertRaisesRegex(ValueError, "size"):
            managed_fields("x" * 400001)



    def test_extra_preset_flag_is_not_automatically_verified_layout(self):
        source = """class CanvasScaler {
            [SerializeField]
            private bool m_PresetInfoIsWorld;
            private float m_PrevScaleFactor;
            private float m_ScaleFactor;
        }"""
        out = managed_fields(source)
        self.assertEqual(out["additional_instance_m_field_declarations"], 2)
        self.assertTrue(out["extra_preset_info_is_world_bool_declared"])
        self.assertTrue(out["extra_preset_info_is_world_has_serializefield_near"])
        self.assertFalse(out["extra_preset_info_is_world_is_last"])
        self.assertEqual(out["other_extra_serializefield_markers"], 0)
        self.assertFalse(out["original_unity_ui_serialized_typetree_verified"])



    def test_preset_bool_source_last_and_other_undeclared_serializations_rejected(self):
        result = managed_fields("""class CanvasScaler {
          [SerializeField] private ScaleMode m_UiScaleMode;
          [SerializeField] private float m_MatchWidthOrHeight;
          [SerializeField] private bool m_PresetInfoIsWorld;
          private float m_PrevScaleFactor;
        }""")
        self.assertTrue(result["extra_preset_info_is_world_is_last"])
        self.assertEqual(result["other_extra_serializefield_markers"], 0)


if __name__ == "__main__":
    unittest.main()
