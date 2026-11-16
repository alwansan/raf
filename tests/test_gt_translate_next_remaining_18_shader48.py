"""Source-free safety tests for one genuine post14 18-material original Shader48."""
import unittest

from scripts.gt_translate_next_remaining_18_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_18_material_name,
)


class Next18OriginalShaderSourceSelectionTests(unittest.TestCase):
    def test_only_one_original_18_material_source_unique_and_expected_topology(self):
        source={
            ("resources.assets",10):"a"*64,
            ("sharedassets0.assets",20):"b"*64,
            ("level0",30):"c"*64,
        }
        usage={"a"*64:18,"b"*64:23,"c"*64:175}
        self.assertEqual(sum(usage.values()),216)
        selected=select_exact_18_material_name(source,usage)
        self.assertEqual(selected,[("resources.assets",10)])
        self.assertEqual(EXPECTED_TOPOLOGY,(4,33,8,58))
        self.assertIn("18_MATERIAL",STATUS)

    def test_missing_duplicate_material_names_and_colliding_source_owner_rejected(self):
        sources={("resources.assets",10):"a"*64,("level0",20):"a"*64,
                 ("sharedassets0.assets",30):"b"*64}
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_18_material_name(sources,{"a"*64:18,"b"*64:23})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_18_material_name(sources,{"a"*64:18,"b"*64:18})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_18_material_name(sources,{"a"*64:23,"b"*64:17})


if __name__=="__main__":
    unittest.main()
