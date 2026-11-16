"""Original SHA owner and exact 11-Material Shader48 4-pass/33-route source guard."""
import unittest
from scripts.gt_translate_next_remaining_11_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_11_material_name,
    validate_authentic_source_ranges,
)


class Next11OriginalSourceSafetyTests(unittest.TestCase):
    def test_unique_11_material_name_must_resolve_only_one_original_Shader48(self):
        sources={("resources.assets",1):"a"*64,("level0",2):"b"*64,
                 ("sharedassets0.assets",3):"c"*64}
        weights={"a"*64:11,"b"*64:23,"c"*64:182}
        self.assertEqual(sum(weights.values()),216)
        self.assertEqual(select_exact_11_material_name(sources,weights),
                         [("resources.assets",1)])
        self.assertEqual(EXPECTED_TOPOLOGY,(4,33,8,58))
        self.assertIn("11_MATERIAL",STATUS)

    def test_missing_or_colliding_source_material_names_fail_closed(self):
        src={("resources.assets",1):"a"*64,("level0",2):"a"*64,
             ("sharedassets0.assets",3):"b"*64}
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_11_material_name(src,{"a"*64:11,"b"*64:23})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_11_material_name(src,{"a"*64:11,"b"*64:11})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_11_material_name(src,{"a"*64:23,"b"*64:10})

    def test_source_range_is_not_replaced_with_another_shader_sliders(self):
        source={"m_PropInfo":{"m_Props":[
            {"m_Type":3,"m_DefValue[0]":3.5,"m_DefValue[1]":0.0,
             "m_DefValue[2]":1.0,"m_DefValue[3]":0.0}]}}
        result=validate_authentic_source_ranges(source)
        self.assertEqual(result["source_original_ShaderLab_Range_property_count"],1)
        self.assertEqual(result["source_original_Range_default_outside_lower_upper_count"],1)
        source["m_PropInfo"]["m_Props"][0]["m_DefValue[3]"]=1.0
        with self.assertRaisesRegex(ValueError,"invalid_authentic_next11"):
            validate_authentic_source_ranges(source)


if __name__=="__main__":
    unittest.main()
