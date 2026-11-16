"""Fail-closed original ZIP2 SHA Shader48 10-material *two* candidate topology selector."""
import unittest
from scripts.gt_translate_next_remaining_10p31_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_10p31_material_name,
    validate_authentic_source_ranges,
)

class TwoTenMaterialAuthenticSourceTopologyTests(unittest.TestCase):
    def test_two_source_candidates_are_not_the_same_Shader_GUID(self):
        src={("resources.assets",10):"a"*64,("level0",20):"b"*64,
             ("level1",30):"c"*64}
        usage={"a"*64:10, "b"*64:10, "c"*64:196}
        self.assertEqual(sum(usage.values()),216)
        self.assertEqual(select_exact_10p31_material_name(src,usage),
                         [("resources.assets",10),("level0",20)])
        self.assertEqual(EXPECTED_TOPOLOGY,(4,31,8,55))
        self.assertIn("10P31_MATERIAL", STATUS)

    def test_missing_or_ambiguous_source_name_digest_fails_closed(self):
        src={("resources.assets",1):"a"*64,("level0",2):"b"*64,
             ("level1",3):"c"*64}
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_10p31_material_name(src,{"a"*64:10,"b"*64:11})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_10p31_material_name(src,{"a"*64:10,"b"*64:10,"c"*64:10})
        src[("other",4)]="a"*64
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_10p31_material_name(src,{"a"*64:10,"b"*64:10})

    def test_post20_single_remaining_name_requires_explicit_source_scope(self):
        source={("original",11):"a"*64,("original",22):"b"*64}
        post20={"a"*64:10,"b"*64:112}
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_10p31_material_name(source,post20)
        self.assertEqual(
            select_exact_10p31_material_name(
                source,post20,expected_name_count=1),
            [("original",11)])
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_10p31_material_name(
                source,{"a"*64:10,"b"*64:10},expected_name_count=1)
        with self.assertRaisesRegex(ValueError,"invalid_original_10p31_expected"):
            select_exact_10p31_material_name(
                source,post20,expected_name_count=3)

    def test_source_range_contract_must_preserve_original_count(self):
        source={"m_PropInfo":{"m_Props":[
            {"m_Type":3, "m_DefValue[0]":2.5,"m_DefValue[1]":0.0,
             "m_DefValue[2]":1.0,"m_DefValue[3]":0.0}]}}
        q=validate_authentic_source_ranges(source)
        self.assertEqual(q["source_original_ShaderLab_Range_property_count"],1)
        self.assertEqual(q["source_original_Range_default_outside_lower_upper_count"],1)
        source["m_PropInfo"]["m_Props"][0]["m_DefValue[3]"]=1.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic"):
            validate_authentic_source_ranges(source)

if __name__=="__main__":
    unittest.main()
