import unittest
from gfxlab.tools.multi_shader_state_material_float_link import (
 normalize_private_state_name,compare_named_state)
class TestPrivateRenderStateNameMaterialBridge(unittest.TestCase):
 def test_exact_source_shader_material_slot_matches_without_gpu_claim(self):
    x=compare_named_state("_Cull",{"_Cull"},[{"_Cull":2.0},{"_Cull":1.0}],{0:"Off",1:"Front",2:"Back"})
    self.assertTrue(x["source_property_declaration_present"])
    self.assertEqual(x["material_float_matching_slots"],2)
    self.assertEqual(x["material_float_valid_enum_slots"],2)
    self.assertFalse(x["effective_shader_gpu_state_verified"])
 def test_explicit_bracketed_shaderlab_reference(self):
    k,used=normalize_private_state_name("[_ZWrite]")
    self.assertEqual(k,"_ZWrite");self.assertTrue(used)
 def test_bad_bracket_does_not_guess(self):
    x=compare_named_state("[Non matching]",{"_ZWrite"},[{"_ZWrite":1}],{0:"off",1:"on"})
    self.assertFalse(x["source_property_declaration_present"])
    self.assertEqual(x["material_float_matching_slots"],0)
 def test_wrong_float_enum_keeps_unknown(self):
    x=compare_named_state("_ZTest",{"_ZTest"},[{"_ZTest":99.5}],{0:"disabled",1:"never"})
    self.assertEqual(x["material_float_valid_enum_slots"],0)
    self.assertEqual(x["material_float_unrecognized_value_slots"],1)
 def test_no_matched_property_does_not_claim_runtime(self):
    x=compare_named_state("_C",set(),[{}],{1:"test"})
    self.assertFalse(x["source_property_declaration_present"])
    self.assertEqual(x["material_float_matching_slots"],0)
    self.assertFalse(x["effective_shader_gpu_state_verified"])
