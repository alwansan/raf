"""Source-free safety tests for one genuine post14 17-material original Shader48."""
import unittest

from scripts.gt_translate_next_remaining_17_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_17_material_name,
    validate_authentic_source_ranges,
)


class Next17OriginalShaderSourceSelectionTests(unittest.TestCase):
    def test_only_one_original_17_material_source_unique_and_expected_topology(self):
        source={
            ("resources.assets",10):"a"*64,
            ("sharedassets0.assets",20):"b"*64,
            ("level0",30):"c"*64,
        }
        usage={"a"*64:17,"b"*64:23,"c"*64:176}
        self.assertEqual(sum(usage.values()),216)
        selected=select_exact_17_material_name(source,usage)
        self.assertEqual(selected,[("resources.assets",10)])
        self.assertEqual(EXPECTED_TOPOLOGY,(3,23,8,43))
        self.assertIn("17_MATERIAL",STATUS)

    def test_range_shape_is_sha_source_driven_not_next23_fixed_3_count(self):
        p={"m_PropInfo":{"m_Props":[
            {"m_Type":3,
             "m_DefValue[0]":2.0,
             "m_DefValue[1]":0.0,
             "m_DefValue[2]":1.0,
             "m_DefValue[3]":0.0},
            {"m_Type":3,
             "m_DefValue[0]":0.5,
             "m_DefValue[1]":0.0,
             "m_DefValue[2]":1.0,
             "m_DefValue[3]":0.0},
        ]}}
        result=validate_authentic_source_ranges(p)
        self.assertEqual(result["source_original_ShaderLab_Range_property_count"],2)
        self.assertEqual(result["source_original_Range_default_outside_lower_upper_count"],1)
        p["m_PropInfo"]["m_Props"][1]["m_DefValue[1]"]=2.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic_next17"):
            validate_authentic_source_ranges(p)
        p["m_PropInfo"]["m_Props"][1]["m_DefValue[1]"]=0.0
        p["m_PropInfo"]["m_Props"][0]["m_DefValue[3]"]=1.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic_next17"):
            validate_authentic_source_ranges(p)

    def test_missing_duplicate_material_names_and_colliding_source_owner_rejected(self):
        sources={("resources.assets",10):"a"*64,("level0",20):"a"*64,
                 ("sharedassets0.assets",30):"b"*64}
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_17_material_name(sources,{"a"*64:17,"b"*64:23})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_17_material_name(sources,{"a"*64:17,"b"*64:17})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_17_material_name(sources,{"a"*64:23,"b"*64:17})


if __name__=="__main__":
    unittest.main()
