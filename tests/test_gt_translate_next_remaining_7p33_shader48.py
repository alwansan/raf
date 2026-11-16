"""SOURCE SHA/owner identity guard for two distinct 7-Material original Shader48."""
import unittest
from scripts.gt_translate_next_remaining_7p33_shader48 import (
    STATUS,EXPECTED_TOPOLOGY,select_exact_7p33_material_name,
    validate_authentic_source_ranges,
)


class TwoSevenMaterialOriginalShaderSafety(unittest.TestCase):
    def test_two_source_owners_have_distinct_name_digests(self):
        src={("resources.assets",101):"a"*64,
             ("level0",202):"b"*64,("level3",303):"c"*64}
        q={"a"*64:7,"b"*64:7,"c"*64:202}
        self.assertEqual(sum(q.values()),216)
        self.assertEqual(select_exact_7p33_material_name(src,q),
                         [("resources.assets",101),("level0",202)])
        self.assertEqual(EXPECTED_TOPOLOGY,(4,33,8,58))
        self.assertIn("7P33_MATERIAL",STATUS)

    def test_missing_and_colliding_digest_cannot_select_wrong_source_owner(self):
        src={("resources.assets",1):"a"*64,("level0",2):"b"*64}
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_7p33_material_name(src,{"a"*64:7,"b"*64:8})
        src[("level1",3)]="c"*64
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_7p33_material_name(src,{"a"*64:7,"b"*64:7,"c"*64:7})
        src[("level2",4)]="a"*64
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_7p33_material_name(src,{"a"*64:7,"b"*64:7})

    def test_original_numeric_Range_contract_fail_closed(self):
        parsed={"m_PropInfo":{"m_Props":[{
            "m_Type":3,"m_DefValue[0]":2.5,
            "m_DefValue[1]":0.0,"m_DefValue[2]":1.0,
            "m_DefValue[3]":0.0
        }]}}
        r=validate_authentic_source_ranges(parsed)
        self.assertEqual(r["source_original_ShaderLab_Range_property_count"],1)
        self.assertEqual(r["source_original_Range_default_outside_lower_upper_count"],1)
        parsed["m_PropInfo"]["m_Props"][0]["m_DefValue[3]"]=1.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic"):
            validate_authentic_source_ranges(parsed)


if __name__=="__main__":
    unittest.main()
