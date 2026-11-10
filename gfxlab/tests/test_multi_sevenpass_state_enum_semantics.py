import unittest
from gfxlab.tools.multi_sevenpass_state_enum_semantics import (
 classify_state_value,classify_bool,classify_material_keyword_field,
 CULL,ZTEST,SWITCH)
class TestSourceStateEnumCategories(unittest.TestCase):
 def test_official_cull_and_compare_values(self):
    self.assertEqual(classify_state_value({"val":2.0,"name":""},CULL),"back")
    self.assertEqual(classify_state_value({"val":1.0,"name":""},CULL),"front")
    self.assertEqual(classify_state_value({"val":4.0,"name":""},ZTEST),"less_equal")
    self.assertEqual(classify_state_value({"val":8.0,"name":""},ZTEST),"always")
 def test_named_override_never_claims_numeric_value(self):
    self.assertEqual(classify_state_value({"val":2,"name":"private"},CULL),"named_dynamic_override")
 def test_non_numeric_nonfinite_and_unmapped_enum(self):
    self.assertEqual(classify_state_value(None,CULL),"missing_or_null")
    self.assertEqual(classify_state_value(float("nan"),SWITCH),"non_numeric_or_nonfinite")
    self.assertEqual(classify_state_value(0.25,SWITCH),"non_integral_value")
    self.assertEqual(classify_state_value(25,CULL),"out_of_enum_range")
 def test_material_keywords_absent_vs_empty(self):
    self.assertEqual(classify_material_keyword_field({},"m_ValidKeywords"),"field_absent")
    self.assertEqual(classify_material_keyword_field({"m_ValidKeywords":[]},"m_ValidKeywords"),"empty")
    self.assertEqual(classify_material_keyword_field({"m_ValidKeywords":[4]},"m_ValidKeywords"),"nonempty")
 def test_bool_only_known_forms(self):
    self.assertEqual(classify_bool(True),"true")
    self.assertEqual(classify_bool(0),"false")
    self.assertEqual(classify_bool("1"),"unknown_boolean_shape")
