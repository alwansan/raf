import unittest
from gfxlab.tools.multi_secondary_color_alias import (
    safe_color_role,vector_shape,alias_group_stats
)

class TestSecondaryColorAlias(unittest.TestCase):
    def test_color_semantics_known_english_unity_names_only(self):
        self.assertEqual(safe_color_role("_Color"),"base_tint_named")
        self.assertEqual(safe_color_role("_EmissionColor"),"emission_named_candidate")
        self.assertEqual(safe_color_role("_NotAnAllowlistedProperty"),"other_original_color_property")
        with self.assertRaises(ValueError):
            safe_color_role(None)

    def test_rgba_black_vs_white_and_alpha(self):
        w=vector_shape({"r":1,"g":1,"b":1,"a":1})
        b=vector_shape({"r":0,"g":0,"b":0,"a":1})
        self.assertTrue(w["rgba_white"])
        self.assertTrue(b["rgb_black"])
        self.assertTrue(b["alpha_one"])
        self.assertFalse(b["rgba_white"])
        self.assertFalse(b["rgb_has_nonzero"])

    def test_nonzero_color_signature(self):
        c=vector_shape({"r":0.2,"g":0.5,"b":0.1,"a":0})
        self.assertTrue(c["rgb_has_nonzero"])
        self.assertTrue(c["alpha_zero"])
        self.assertFalse(c["alpha_one"])

    def test_reject_bad_color(self):
        with self.assertRaises(ValueError):
            vector_shape({"r":0,"g":0,"b":0})
        with self.assertRaises(ValueError):
            vector_shape({"r":float("nan"),"g":0,"b":0,"a":1})

    def test_unique_material_and_repeated_texture_groups(self):
        rows=[
            (("private_owner_a",11),0,"material"),
            (("private_owner_a",11),1,"material"),
            (("private_owner_b",22),1,"material"),
        ]
        result=alias_group_stats(rows)
        self.assertEqual(result["slots"],3)
        self.assertEqual(result["unique_original_objects"],2)
        self.assertEqual(result["aliased_references"],1)
        self.assertEqual(result["alias_group_size_histogram"],{"1":1,"2":1})
        self.assertEqual(result["groups_shared_across_models"],1)

    def test_cross_role_shared_source_count(self):
        rows=[
            (("private",1),0,"basecolor"),
            (("private",1),1,"metallic"),
        ]
        result=alias_group_stats(rows)
        self.assertEqual(result["groups_shared_across_roles"],1)
        self.assertNotIn("private",str(result))

    def test_reject_malformed_alias_rows(self):
        with self.assertRaises(ValueError):
            alias_group_stats([])
        with self.assertRaises(ValueError):
            alias_group_stats([("private",0,"role")])
        with self.assertRaises(ValueError):
            alias_group_stats([(("private",1),True,"role")])
