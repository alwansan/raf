"""GFX-MULTI-050 synthetic original-free DXBC CB DCL vs reflected UBO byte size."""
import unittest
from gfxlab.tools.multi_shader_original_cb_spv_blocksize import cb_size_evidence, numeric_cb_coordinate_candidate

class TestOriginalCBByteSizeComparison(unittest.TestCase):
    def test_exact_real_block_size_equality_does_not_prove_member_offsets(self):
        d=cb_size_evidence({0:16,3:4},[
            {"name":"cb0_16","set":0,"binding":11,"block_size":256},
            {"name":"cb3_4","set":2,"binding":19,"block_size":64}])
        self.assertTrue(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])
        self.assertEqual(d["source_dcl_vec4_times_16_equals_translated_spirv_block_size"],2)
        self.assertFalse(d["equal_byte_size_proves_member_layout_or_Material_property_semantics"])
        self.assertFalse(d["original_b_register_indices_or_CB_byte_sizes_exported"])

    def test_size_mismatch_must_fail_closed(self):
        d=cb_size_evidence({0:16},[{"name":"cb0_16","binding":4,"block_size":240}])
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])
        self.assertEqual(d["source_dcl_vec4_times_16_differs_from_translated_spirv_block_size"],1)

    def test_generated_suffix_wrong_even_when_block_size_is_equal(self):
        d=cb_size_evidence({1:16},[{"name":"cb1_24","binding":4,"block_size":256}])
        self.assertEqual(d["generated_name_vector_count_mismatch"],1)
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])

    def test_unknown_ubo_name_never_inferred_from_numeric_descriptor(self):
        d=cb_size_evidence({3:4},[{"name":"OtherCB","binding":3,"block_size":64}])
        self.assertEqual(d["source_cb_registers_missing_from_translation"],1)
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])

    def test_missing_explicit_size_is_unknown_not_true(self):
        d=cb_size_evidence({0:1},[{"name":"cb0_1","binding":4}])
        self.assertEqual(d["ubo_reflections_missing_block_size"],1)
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])

    def test_duplicate_source_or_descriptor_identity_rejected(self):
        d=cb_size_evidence({0:1,1:1},[
            {"name":"cb0_1","binding":4,"block_size":16},
            {"name":"cb1_1","binding":4,"block_size":16}])
        self.assertEqual(d["invalid_or_duplicate_reflected_cb_binding"],1)
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])

    def test_zero_cb_stage_has_no_positive_claim(self):
        d=cb_size_evidence({},[])
        self.assertFalse(d["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])
        self.assertEqual(d["source_original_dxbc_constant_buffer_declarations"],0)

    def test_unbounded_or_corrupt_input_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"DCL_CB_VECTORS_INVALID"):
            cb_size_evidence({0:0},[])
        with self.assertRaisesRegex(ValueError,"DCL_CB_VECTORS_INVALID"):
            cb_size_evidence({True:1},[])
        with self.assertRaisesRegex(ValueError,"WRONG_INPUT"):
            cb_size_evidence([],[])
        with self.assertRaisesRegex(ValueError,"ROW_NOT_OBJECT"):
            cb_size_evidence({1:1},[None])

    def test_numeric_same_slot_candidate_is_not_semantic_CB_proof(self):
        d=numeric_cb_coordinate_candidate({0:4,3:16},[
            {"name":"OpaqueUno","set":0,"binding":0,"block_size":64},
            {"name":"OpaqueDos","set":0,"binding":3,"block_size":256}])
        self.assertTrue(d["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])
        self.assertEqual(d["numeric_b_binding_candidate_same_byte_sizes"],2)
        self.assertFalse(d["numeric_descriptor_equality_proves_original_CB_identity"])
        self.assertFalse(d["numeric_descriptor_equality_proves_original_CB_member_offsets"])
        self.assertFalse(d["private_register_numbers_or_UBO_sizes_exported"])

    def test_numeric_wrong_set_or_size_never_claimed(self):
        a=numeric_cb_coordinate_candidate({0:4},[{"set":1,"binding":0,"block_size":64}])
        self.assertEqual(a["nonzero_descriptor_set_excluded_from_numeric_identity_candidate"],1)
        self.assertFalse(a["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])
        b=numeric_cb_coordinate_candidate({0:4},[{"set":0,"binding":0,"block_size":48}])
        self.assertEqual(b["numeric_b_binding_candidate_different_byte_sizes"],1)
        self.assertFalse(b["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])

    def test_numeric_duplicate_and_missing_size_rejected(self):
        a=numeric_cb_coordinate_candidate({0:4},[{"binding":0,"block_size":64},
            {"binding":0,"block_size":64}])
        self.assertEqual(a["duplicate_or_invalid_reflected_descriptor_coordinate"],1)
        self.assertFalse(a["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])
        b=numeric_cb_coordinate_candidate({0:4},[{"binding":0}])
        self.assertEqual(b["numeric_b_binding_candidate_missing_block_size"],1)
        self.assertFalse(b["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])

if __name__=="__main__":unittest.main()
