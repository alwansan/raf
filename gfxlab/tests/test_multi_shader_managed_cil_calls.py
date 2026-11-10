"""GFX-MULTI-044 original-free test of CIL property string + API call co-presence.

No private MethodDef names, property strings or original .NET bytes committed.
"""
import unittest
from gfxlab.tools.multi_shader_managed_cil_calls import (
    classify_method_events,CALL_WINDOW,
)
PROP={"_SyntheticTex","_SyntheticColor","_SyntheticOther"}
TEXTURES={"_SyntheticTex"}
BOUND={"_SyntheticTex"}


class TestOriginalManagedCILCalls(unittest.TestCase):
    def test_same_method_and_forward_window_is_only_weak_candidate(self):
        events=[(0,"property","_SyntheticTex"),(5,"api","Material")]
        a=classify_method_events(events,PROP,TEXTURES,BOUND)
        self.assertTrue(a["method_has_both_literal_and_API_call"])
        self.assertEqual(a["property_ldstr_with_later_API_call_in_12_instructions"],1)
        self.assertEqual(a["distinct_exact_bound_texenv_strings_in_method"],1)
        self.assertFalse(a.get("original_material_to_GPU_register_mapping_verified",False))

    def test_backward_call_not_a_forward_argument_candidate(self):
        a=classify_method_events([
            (0,"api","Shader"),(3,"property","_SyntheticTex")
        ],PROP,TEXTURES,BOUND)
        self.assertTrue(a["method_has_both_literal_and_API_call"])
        self.assertEqual(a["property_ldstr_with_later_API_call_in_12_instructions"],0)

    def test_unrelated_method_and_late_call_not_proof_of_dataflow(self):
        a=classify_method_events([
            (0,"property","_SyntheticTex"),
            (50,"api","MaterialPropertyBlock")
        ],PROP,TEXTURES,BOUND)
        self.assertEqual(a["property_ldstr_with_later_API_call_in_12_instructions"],0)
        self.assertFalse(a.get("co_presence_proves_argument_dataflow",False))

    def test_exact_only_ignore_any_other_literals(self):
        a=classify_method_events([(0,"property","_SyntheticTexture"),
                (2,"property","_SyntheticColor"),(3,"api","Material")],
                PROP,TEXTURES,BOUND)
        self.assertEqual(a["property_ldstr_instruction_count"],1)
        self.assertEqual(a["distinct_exact_texture_property_strings_in_method"],0)
        self.assertEqual(a["private_literal_names_with_nearby_API_call"],{"_SyntheticColor"})

    def test_no_events_and_fail_closed_invalid_indices(self):
        self.assertIsNone(classify_method_events([],PROP,TEXTURES,BOUND))
        with self.assertRaisesRegex(ValueError,"ORDER_INVALID"):
            classify_method_events([(5,"property","_SyntheticTex"),(4,"api","Material")],
                PROP,TEXTURES,BOUND)
        with self.assertRaisesRegex(ValueError,"KIND_INVALID"):
            classify_method_events([(1,"something","secret")],PROP,TEXTURES,BOUND)

    def test_bounded_window_exact_threshold(self):
        self.assertEqual(CALL_WINDOW,12)
        a=classify_method_events([
            (2,"property","_SyntheticTex"),(2+CALL_WINDOW,"api","Material")
        ],PROP,TEXTURES,BOUND)
        self.assertEqual(a["property_ldstr_with_later_API_call_in_12_instructions"],1)
        a=classify_method_events([
            (2,"property","_SyntheticTex"),(3+CALL_WINDOW,"api","Material")
        ],PROP,TEXTURES,BOUND)
        self.assertEqual(a["property_ldstr_with_later_API_call_in_12_instructions"],0)
