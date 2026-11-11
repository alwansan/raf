"""GFX145 source-free regression: classifying saved source Cull metadata."""
import unittest
from gfxlab.tools.gfx145_original_cull_gate import inspect_cull


class CullSourceGateTests(unittest.TestCase):
    def test_literal_default_back_is_not_runtime_proof(self):
        row=inspect_cull(2,set(),[{}])
        self.assertEqual(row["fallback_cull_enum"],"back")
        self.assertFalse(row["runtime_unity_effective_cull_verified"])
        self.assertFalse(row["named_dynamic_override"])

    def test_literal_default_off_is_supported(self):
        self.assertEqual(inspect_cull(0,set(),[{}])["fallback_cull_enum"],"off")

    def test_named_override_absent_in_materials_stays_unresolved(self):
        row=inspect_cull({"name":"[_CullMode]","val":2},set(),[{},{}])
        self.assertEqual(row["fallback_cull_enum"],"back")
        self.assertTrue(row["named_dynamic_override"])
        self.assertEqual(row["material_slots_with_matching_saved_float"],0)
        self.assertFalse(row["runtime_unity_override_resolution_verified"])
        self.assertTrue(row["name_is_bracketed_ShaderLab_token"])

    def test_named_override_matches_original_material_floats_only(self):
        row=inspect_cull({"name":"[_CullMode]","val":0},
                         {"_CullMode"},[{"_CullMode":("float",(2.,))},
                                       {"_CullMode":("float",(1.,))},
                                       {"notCull":("float",(0.,))}])
        self.assertTrue(row["name_declared_as_ShaderLab_property"])
        self.assertEqual(row["material_slots_with_matching_saved_float"],2)
        self.assertEqual(row["matching_material_cull_enum_categories"],{"back":1,"front":1})
        self.assertEqual(row["fallback_cull_enum"],"off")
        self.assertFalse(row["runtime_unity_effective_cull_verified"])

    def test_unrecognized_override_value_does_not_infer_effective_mode(self):
        row=inspect_cull({"name":"_CullMode","val":2},set(),
                         [{"_CullMode":("float",(99.,))}])
        self.assertEqual(row["material_slots_with_unrecognized_enum"],1)
        self.assertEqual(row["matching_material_cull_enum_categories"],{})
        self.assertFalse(row["runtime_unity_effective_cull_verified"])

    def test_named_color_is_not_mistaken_for_float(self):
        row=inspect_cull({"name":"_CullMode","val":2},set(),
                         [{"_CullMode":("color",(2.,0.,0.,0.))}])
        self.assertEqual(row["material_slots_with_unrecognized_enum"],1)
        self.assertEqual(row["material_slots_with_matching_saved_float"],1)

    def test_bad_source_name_rejected(self):
        with self.assertRaisesRegex(ValueError,"Invalid source Cull"):
            inspect_cull({"name":42,"val":2},set(),[{}])

    def test_bad_source_inventory_rejected(self):
        with self.assertRaisesRegex(ValueError,"Invalid source"):
            inspect_cull(2,set(),[])
        with self.assertRaisesRegex(ValueError,"Invalid source"):
            inspect_cull(2,[],[{}])

    def test_out_of_enum_fallback_never_becomes_back_or_off(self):
        row=inspect_cull({"name":"[_CullMode]","val":88},set(),[{}])
        self.assertEqual(row["fallback_cull_enum"],"out_of_enum_range")
        self.assertFalse(row["runtime_unity_effective_cull_verified"])


if __name__=="__main__":
    unittest.main()
