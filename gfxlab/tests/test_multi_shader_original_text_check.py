import unittest
from gfxlab.tools.multi_shader_original_text_check import (
    safe_embedded_script_evidence,bound_material_property_check)

class TestOriginalShaderEmbeddedTextEvidence(unittest.TestCase):
    def test_missing_script_false_and_no_mapping_claim(self):
        s=safe_embedded_script_evidence(None)
        self.assertFalse(s["original_embedded_script_field_present"])
        self.assertFalse(s["original_material_name_to_DX11_register_authoritatively_verified"])
    def test_text_source_marker_is_not_registration_parity_proof(self):
        s=safe_embedded_script_evidence("Shader X HLSLPROGRAM Texture2D x : register(t5);")
        self.assertTrue(s["hlsl_or_cg_program_markers_found"])
        self.assertTrue(s["register_syntax_marker_found"])
        self.assertFalse(s["original_material_name_to_DX11_register_authoritatively_verified"])
    def test_original_bound_name_intersection(self):
        s=bound_material_property_check({"_MainTex","_BumpMap"},
            [{"_MainTex","_BumpMap","Extra"}],[{"_MainTex","_BumpMap"}])
        self.assertEqual(s["stored_texenv_slots"],3)
        self.assertEqual(s["bound_texenv_names_declared_in_shader"],2)
        self.assertEqual(s["bound_texenv_slots"],2)
    def test_not_bound_subset_rejects(self):
        with self.assertRaises(ValueError):
            bound_material_property_check({"A"},[{"A"}],[{"Missing"}])
