"""Original SHA-authenticated single 6-Material / 1-Pass Shader48 topology.

The two VS-FS keyword routes and three unique DXBC stages were obtained from
the actual original post14 216-Dummy census. No GUID is inferred from a name.
"""
import unittest
from scripts.gt_translate_next_remaining_6_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_6_material_name,
    validate_authentic_source_ranges,
)


class SixMaterialAuthenticOriginalShader48(unittest.TestCase):
    def test_unique_original_sha_digest_and_source_owner_required(self):
        original={("resources.assets",101):"a"*64,
                  ("level0",202):"b"*64,
                  ("level3",303):"c"*64}
        census={"a"*64:6,"b"*64:5,"c"*64:205}
        self.assertEqual(sum(census.values()),216)
        self.assertEqual(
            select_exact_6_material_name(original,census),
            [("resources.assets",101)],
        )
        self.assertEqual(EXPECTED_TOPOLOGY,(1,2,0,3))
        self.assertIn("REMAINING_6_MATERIAL",STATUS)

    def test_ambiguous_original_six_material_source_fails_closed(self):
        original={("resources.assets",101):"a"*64,("level0",202):"b"*64}
        for census in ({"a"*64:5,"b"*64:5},
                       {"a"*64:6,"b"*64:6}):
            with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
                select_exact_6_material_name(original,census)
        original[("other",303)]="a"*64
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_6_material_name(original,{"a"*64:6,"b"*64:5})
        with self.assertRaisesRegex(ValueError,"malformed_original"):
            select_exact_6_material_name(original,{"a"*63:6,"b"*64:5})

    def test_original_range_properties_must_not_inherit_another_shader(self):
        parsed={"m_PropInfo":{"m_Props":[{
            "m_Type":3,"m_DefValue[0]":2.5,
            "m_DefValue[1]":0.0,"m_DefValue[2]":1.0,
            "m_DefValue[3]":0.0
        }]}}
        counts=validate_authentic_source_ranges(parsed)
        self.assertEqual(counts["source_original_ShaderLab_Range_property_count"],1)
        self.assertEqual(counts["source_original_Range_default_outside_lower_upper_count"],1)
        parsed["m_PropInfo"]["m_Props"][0]["m_DefValue[3]"]=1.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic"):
            validate_authentic_source_ranges(parsed)


if __name__=="__main__":
    unittest.main()
