"""Guard exact two 23-material source names and immutable 4-pass 33-pair selection."""
import unittest
from scripts.gt_translate_next_remaining_23_shader48 import (
    STATUS, EXPECTED_TOPOLOGY, select_exact_23_material_name,
)


class Next23OriginalShaderSelectionTests(unittest.TestCase):
    def test_two_unique_original_23_material_names(self):
        original={
            ("resources.assets",10):"a"*64,
            ("sharedassets0.assets",20):"b"*64,
            ("level0",30):"c"*64,
        }
        material_count={"a"*64:23,"b"*64:23,"c"*64:200}
        targets=select_exact_23_material_name(original,material_count)
        self.assertEqual(set(targets),{("resources.assets",10),("sharedassets0.assets",20)})
        self.assertEqual(EXPECTED_TOPOLOGY,(4,33,8,58))
        self.assertIn("23_MATERIAL",STATUS)

    def test_reject_missing_or_name_collisions_without_private_guesses(self):
        original={("resources.assets",10):"a"*64,("level0",20):"a"*64,
                  ("sharedassets0.assets",30):"b"*64}
        with self.assertRaisesRegex(ValueError,"not_one_authentic"):
            select_exact_23_material_name(original,{"a"*64:23,"b"*64:23})
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            select_exact_23_material_name(original,{"a"*64:23,"b"*64:18})


if __name__=="__main__":
    unittest.main()
