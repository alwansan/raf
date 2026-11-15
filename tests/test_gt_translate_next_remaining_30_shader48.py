"""Select exactly one original Shader48 by authenticated 30-Material source digest."""
import unittest
from scripts.gt_translate_next_remaining_30_shader48 import (
    select_exact_30_material_name, EXPECTED_TOPOLOGY,
)


class OriginalThirtyMaterialShaderTests(unittest.TestCase):
    def test_anonymous_source_guid_selection_requires_one_matched_Shader48(self):
        source={
            ("resources.assets", 100):"a"*64,
            ("sharedassets0.assets", 200):"b"*64,
            ("level0", 30):"c"*64,
        }
        materials={"a"*64:30,"b"*64:48,"c"*64:255}
        self.assertEqual(select_exact_30_material_name(source,materials),
                         ("resources.assets",100))
        self.assertEqual(EXPECTED_TOPOLOGY,(4,31,8,55))

    def test_duplicate_original_names_and_multiple_thirty_material_names_rejected(self):
        original={("resources.assets",1):"a"*64,
                  ("sharedassets0.assets",2):"a"*64}
        materials={"a"*64:30}
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_30_material_name(original,materials)
        original={("resources.assets",1):"a"*64}
        materials={"a"*64:30,"b"*64:30}
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_30_material_name(original,materials)


if __name__=="__main__":
    unittest.main()
