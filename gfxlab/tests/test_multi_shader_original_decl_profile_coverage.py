"""GFX-MULTI-055 original-free synthetic b/t/s/CB profile-coverage tests."""
import unittest
from gfxlab.tools.multi_shader_original_decl_profile_coverage import (
  canonical_private_declaration_profile, safe_one_pass_profile_summary)

def profile(b,bs,t,s):
    return canonical_private_declaration_profile(
        {"constant_buffer":set(b),"resource":set(t),"sampler":set(s)},dict(bs))

class TestOriginalProfileCoverage(unittest.TestCase):
    def test_same_b_ts_layout_class_for_independent_stage_shapes(self):
        a=profile([0],[(0,4)],[0,2],[0])
        b=profile([0],[(0,4)],[0,2],[0])
        summary=safe_one_pass_profile_summary([(a,b),(a,b),(a,b)])
        self.assertEqual(summary["private_joint_VS_FS_declaration_profile_classes"],1)
        self.assertEqual(summary["pairs_outside_first_structural_profile"],0)
        self.assertEqual(summary["vertex_CB_slot_and_vec4_length_profile_classes"],1)
        self.assertFalse(summary["same_profile_implies_same_shader_instructions_or_pixel_output"])

    def test_change_in_cb_size_is_distinct_even_same_slots(self):
        a=profile([1],[(1,4)],[0],[0])
        b=profile([1],[(1,8)],[0],[0])
        summary=safe_one_pass_profile_summary([(a,a),(a,b),(a,a)])
        self.assertEqual(summary["private_joint_VS_FS_declaration_profile_classes"],2)
        self.assertEqual(summary["pairs_outside_first_structural_profile"],1)
        self.assertEqual(summary["fragment_pairs_outside_first_CB_size_register_profile"],1)
        self.assertEqual(summary["fragment_CB_slot_and_vec4_length_profile_classes"],2)

    def test_texture_slot_identity_shift_not_hidden_by_same_count(self):
        a=profile([0],[(0,4)],[0],[0])
        b=profile([0],[(0,4)],[9],[0])
        s=safe_one_pass_profile_summary([(a,a),(b,a)])
        self.assertEqual(s["vertex_texture_resource_registers_identity_profile_classes"],2)
        self.assertEqual(s["vertex_texture_resource_registers_count_histogram"],{"1":2})
        self.assertEqual(s["vertex_pairs_outside_first_texture_resource_registers_identity"],1)
        self.assertEqual(s["vertex_pairs_outside_first_CB_size_register_profile"],0)

    def test_cb_same_size_new_register_is_distinct(self):
        a=profile([2],[(2,8)],[0],[0])
        b=profile([3],[(3,8)],[0],[0])
        s=safe_one_pass_profile_summary([(a,a),(b,a)])
        self.assertEqual(s["vertex_CB_slot_and_vec4_length_profile_classes"],2)

    def test_zero_source_cb_only_count_not_fake_cb_bytes(self):
        a=profile([],[],[],[])
        s=safe_one_pass_profile_summary([(a,a)])
        self.assertEqual(s["vertex_zero_original_CB_declaration_pair_references"],1)
        self.assertEqual(s["vertex_constant_buffer_registers_count_histogram"],{"0":1})
        self.assertFalse(s["private_CB_register_values_or_sizes_in_report"])

    def test_input_slot_and_size_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"DECLARATION_SET_MISMATCH"):
            canonical_private_declaration_profile({"constant_buffer":{0},"resource":set(),"sampler":set()}, {})
        with self.assertRaisesRegex(ValueError,"CB_SIZE_INVALID"):
            profile([0],[(0,0)],[],[])

    def test_type_and_bounds_rejected(self):
        with self.assertRaisesRegex(ValueError,"REGISTER_INVALID"):
            profile([True],[(True,4)],[],[])
        with self.assertRaisesRegex(ValueError,"PASS_EXACT_PAIRS_INVALID"):
            safe_one_pass_profile_summary([])
        with self.assertRaisesRegex(ValueError,"PAIR_STAGE_PROFILE_INVALID"):
            safe_one_pass_profile_summary([("bad",)])
        with self.assertRaisesRegex(ValueError,"SLOT_FAMILIES_INVALID"):
            canonical_private_declaration_profile({"resource":set()},{})

    def test_first_pair_missing_second_class_counted(self):
        a=profile([0],[(0,4)],[0],[0])
        b=profile([0],[(0,4)],[0,1],[0,1])
        s=safe_one_pass_profile_summary([(a,a),(b,b),(a,a),(b,a)])
        self.assertEqual(s["private_joint_VS_FS_declaration_profile_classes"],3)
        self.assertEqual(s["pairs_same_full_structural_profile_as_first_pair"],2)
        self.assertEqual(s["pairs_outside_first_structural_profile"],2)
        self.assertFalse(s["same_profile_implies_same_shader_instructions_or_pixel_output"])
if __name__=="__main__":unittest.main()
