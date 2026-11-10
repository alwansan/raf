"""GFX071 SPIR-V source-authenticated CB index producer opcode count-only tests."""
import unittest
from gfxlab.tools.multi_shader_spv_index_root_taxonomy071 import shifted_source_spv_dynamic_UBO_reads
from gfxlab.tests.test_multi_shader_spv_shifted_cb_index070 import spv,AUTH

def analyze(lines):
    return shifted_source_spv_dynamic_UBO_reads(spv(lines),AUTH)

class TestGFX071AuthenticSPVIndexRootTaxonomy(unittest.TestCase):
    def test_direct_shift_op_is_reported_but_never_original_DXBC_equivalence(self):
        d=analyze(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %10 %2 %7",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_load_index_direct_def_opcode_OpShiftLeftLogical"],1)
        self.assertEqual(d["SPV_dynamic_vec_load_index_after_bounded_unary_wrappers_OpShiftLeftLogical"],1)
        self.assertFalse(d["producer_opcode_histogram_is_source_DXBC_operand_mapping"])

    def test_root_opload_and_its_pointer_opcode_are_distinct_count_fields(self):
        d=analyze(["%20 = OpAccessChain %ptr %10 %2 %6",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_load_index_direct_def_opcode_OpLoad"],1)
        self.assertEqual(d["SPV_index_value_OpLoad_pointer_def_opcode_OpVariable"],1)
        self.assertFalse(d["index_OpLoad_pointer_origin_is_OpStore_value_proven"])

    def test_arithmetic_wrapper_root_not_equated_to_ishl_original(self):
        d=analyze(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%9 = OpIAdd %1 %7 %4",
                   "%20 = OpAccessChain %ptr %10 %2 %9",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_load_index_direct_def_opcode_OpIAdd"],1)
        self.assertEqual(d["SPV_dynamic_vec_load_index_after_bounded_unary_wrappers_OpIAdd"],1)
        self.assertFalse(d["SPV_dynamic_shift_ancestor_means_same_original_DXBC_ISHL"])

    def test_unary_copy_chain_is_syntax_only(self):
        d=analyze(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%9 = OpCopyObject %1 %7",
                   "%20 = OpAccessChain %ptr %10 %2 %9",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_load_index_direct_def_opcode_OpCopyObject"],1)
        self.assertEqual(d["SPV_dynamic_vec_load_index_after_bounded_unary_wrappers_OpShiftLeftLogical"],1)

    def test_no_real_OpLoad_makes_no_index_histogram(self):
        d=analyze(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %10 %2 %7"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)
        self.assertEqual(sum(v for k,v in d.items() if k.startswith("SPV_dynamic_vec_load_index_direct_def_opcode_")),0)

    def test_unverified_root_not_recorded(self):
        d=analyze(["%7 = OpShiftLeftLogical %1 %6 %3",
                   "%20 = OpAccessChain %ptr %999 %2 %7",
                   "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_authenticated_dynamic_vec_OpLoad_occurrences"],0)

if __name__=="__main__":unittest.main()
