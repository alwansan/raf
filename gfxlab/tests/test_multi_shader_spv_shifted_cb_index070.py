"""GFX070 SPIR-V only synthetic dynamic UBO shift-index ancestry negative controls."""
import unittest
from gfxlab.tools.multi_shader_spv_shifted_cb_index070 import shifted_source_spv_dynamic_UBO_reads

AUTH={"%10":(2,0,16,8)}

def spv(lines):
    return ("\n".join([
        "%1 = OpTypeInt 32 0",
        "%2 = OpConstant %1 0",
        "%3 = OpConstant %1 2",
        "%4 = OpConstant %1 3",
        "%10 = OpVariable %UBO Uniform",
        "%8 = OpVariable %ptr Function",
        "%6 = OpLoad %1 %8",
        *lines,
    ])+"\n").encode("utf8")

def inspect(lines,auth=AUTH):
    return shifted_source_spv_dynamic_UBO_reads(spv(lines),auth)

class TestGFX070AuthenticatedSPVIndexShiftAncestors(unittest.TestCase):
    def test_direct_shift_used_by_real_loaded_authenticated_CBUbo(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %10 %2 %7",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_direct_shift"],1)
        self.assertFalse(d["SPV_dynamic_shift_ancestor_means_same_original_DXBC_ISHL"])
        self.assertFalse(d["original_source_temp_to_SPV_SSA_global_mapping_proven"])

    def test_add_with_shift_ancestor_is_not_mislabelled_direct(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%9 = OpIAdd %1 %7 %4",
                   "%20 = OpAccessChain %ptr %10 %2 %9",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_via_shift_ancestor"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_direct_shift"],0)

    def test_no_load_does_not_count_as_observed_read(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %10 %2 %7"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)
        self.assertEqual(d["SPV_dynamic_vec_pointers_without_OpLoad"],1)

    def test_index_is_runtime_load_but_no_shift_evidence(self):
        d=inspect(["%20 = OpAccessChain %ptr %10 %2 %6",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_unproven_expression"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_direct_shift"],0)

    def test_wrong_unverified_root_not_counted(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %11 %2 %7",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)

    def test_wrong_structure_member_and_out_of_bounds_component_rejected(self):
        wrong=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                       "%20 = OpAccessChain %ptr %10 %3 %7",
                       "%30 = OpLoad %vec4 %20"])
        self.assertEqual(wrong["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)
        self.assertEqual(wrong["SPV_invalid_struct_member_or_index_path"],1)
        component=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                           "%21 = OpConstant %1 5",
                           "%20 = OpAccessChain %ptr %10 %2 %7 %21",
                           "%30 = OpLoad %scalar %20"])
        self.assertEqual(component["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)
        self.assertEqual(component["SPV_invalid_struct_member_or_index_path"],1)

    def test_phi_select_index_is_not_trusted_shift_ancestry(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%9 = OpSelect %1 %condition %7 %6",
                   "%20 = OpAccessChain %ptr %10 %2 %9",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_unproven_expression"],1)

    def test_split_array_pointer_and_copy_object_propagate_root_and_index(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%13 = OpAccessChain %arrayptr %10 %2",
                   "%20 = OpAccessChain %ptr %13 %7",
                   "%21 = OpCopyObject %ptr %20",
                   "%30 = OpLoad %vec4 %21"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_direct_shift"],1)

    def test_duplicate_spv_result_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                     "%7 = OpIAdd %1 %6 %3"])

    def test_authenticated_ubo_malformed_layout_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_AUTHENTICATED"):
            inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                     "%20 = OpAccessChain %ptr %10 %2 %7"],{"%10":(2,0,12,8)})

    def test_unknown_phi_pointer_alias_cannot_be_claimed(self):
        d=inspect(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %10 %2 %7",
                   "%21 = OpPhi %ptr %20 %bb1 %20 %bb2",
                   "%30 = OpLoad %vec4 %21"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)
        self.assertEqual(d["SPV_unproven_phi_or_select_pointer_alias"],1)

    def test_unary_and_binary_non_shift_index_is_not_claimed(self):
        d=inspect(["%7 = OpIAdd %1 %3 %4",
                   "%20 = OpAccessChain %ptr %10 %2 %7",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_with_no_proven_shift"],1)
        self.assertEqual(d["SPV_dynamic_vec_OpLoad_index_direct_shift"],0)

if __name__=="__main__":
    unittest.main()
