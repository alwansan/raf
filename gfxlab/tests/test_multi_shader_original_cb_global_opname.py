"""GFX052 synthetic original-source-free UBO global label tests."""
import unittest
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence

class TestGFX052Synthetic(unittest.TestCase):
    def test_real_uniform_global_label_binds_source_slot_and_bytes(self):
        text=b"""
OpName %99 "cb3_4"
OpName %10 "cb3_4"
OpDecorate %10 Binding 3
OpDecorate %10 DescriptorSet 0
%99 = OpTypeStruct %v
%10 = OpVariable %123 Uniform
"""
        c=global_cb_evidence(text,{3:4},[{"binding":3,"block_size":64,"name":"OtherType"}])
        self.assertEqual(c["opname_labels_on_non_Uniform_global_ids_ignored"],1)
        self.assertEqual(c["actual_global_name_source_b_binding_and_block_bytes_match"],1)
        self.assertTrue(c["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"])
        self.assertFalse(c["original_Material_property_or_member_byte_layout_verified"])

    def test_type_label_not_inferred_as_resource_symbol(self):
        d=b'OpName %99 "cb3_4"\nOpDecorate %10 Binding 3\n%10 = OpVariable %123 Uniform\n'
        c=global_cb_evidence(d,{3:4},[{"binding":3,"block_size":64}])
        self.assertEqual(c["actual_reflected_ubo_globals_missing_opname"],1)
        self.assertFalse(c["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"])

    def test_unrecognized_global_name_does_not_assume_numeric_binding(self):
        d=b'OpName %10 "BlockType"\nOpDecorate %10 Binding 3\n%10 = OpVariable %123 Uniform\n'
        c=global_cb_evidence(d,{3:4},[{"binding":3,"block_size":64}])
        self.assertEqual(c["actual_reflected_ubo_globals_unrecognized_CB_register_grammar"],1)
        self.assertEqual(c["actual_global_name_source_b_binding_and_block_bytes_match"],0)

    def test_wrong_source_name_and_byte_size_fail(self):
        d=b'OpName %10 "cb4_4"\nOpDecorate %10 Binding 3\n%10 = OpVariable %123 Uniform\n'
        c=global_cb_evidence(d,{3:4},[{"binding":3,"block_size":64}])
        self.assertEqual(c["global_cb_grammar_names_outside_original_b_set"],1)
        x=d.replace(b"cb4_4",b"cb3_4")
        y=global_cb_evidence(x,{3:4},[{"binding":3,"block_size":48}])
        self.assertEqual(y["actual_global_name_source_b_binding_block_bytes_mismatch"],1)

    def test_duplicate_actual_global_name_fails_closed(self):
        d=b"""
OpName %10 "cb3_4"
OpName %11 "cb3_4"
OpDecorate %10 Binding 3
OpDecorate %11 Binding 4
%10 = OpVariable %123 Uniform
%11 = OpVariable %123 Uniform
"""
        c=global_cb_evidence(d,{3:4,4:4},[{"binding":3,"block_size":64},{"binding":4,"block_size":64}])
        self.assertEqual(c["real_ubo_global_name_duplicates"],1)
        self.assertFalse(c["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"])

    def test_missing_binding_and_duplicate_decorations_reject(self):
        with self.assertRaisesRegex(ValueError,"MISSING_BINDING"):
            global_cb_evidence(b"%10 = OpVariable %123 Uniform\n",{3:4},[])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_DECORATION"):
            global_cb_evidence(b"OpDecorate %10 Binding 3\nOpDecorate %10 Binding 4\n%10 = OpVariable %123 Uniform\n",{3:4},[])
if __name__=="__main__":unittest.main()
