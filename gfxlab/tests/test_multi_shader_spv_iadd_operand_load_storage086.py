"""GFX086 source-free controls for OpIAdd's actual two OpLoad read-time paths."""
import unittest
from gfxlab.tools.multi_shader_spv_iadd_operand_load_storage086 import (
    authenticated_spv_CB_index_imul_iadd_input_load_storage086
)
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

def counts(lines,auth=AUTH):
    return authenticated_spv_CB_index_imul_iadd_input_load_storage086(dis(lines),auth)

def case(pre,lhs="%90",rhs="%91"):
    return counts([*pre,
      f"%80 = OpIAdd %1 {lhs} {rhs}",
      "%81 = OpBitcast %1 %80",
      "%71 = OpInBoundsAccessChain %ptr %5 %3",
      "%72 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %71 %81",
      "%66 = OpLoad %1 %72",
      "%70 = OpConstant %1 3",
      "%40 = OpIMul %1 %66 %70",
      "%41 = OpBitcast %1 %40",
      "%7 = OpInBoundsAccessChain %ptr %5 %3",
      "%8 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %7 %41",*idxread("%8")
    ])

class TestGFX086ActualTwoIntegerAddInputLoads(unittest.TestCase):
    def test_lhs_prior_store_rhs_different_literal_no_prior(self):
        d=case([
            "%120 = OpInBoundsAccessChain %ptr %5 %3",
            "%121 = OpInBoundsAccessChain %ptr %5 %4",
            "OpStore %120 %4",
            "%90 = OpLoad %1 %120",
            "%91 = OpLoad %1 %121"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_pointer_storage_Function_literal_address"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_rhs_pointer_storage_Function_literal_address"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_same_block_store_syntax"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_rhs_prior_store_at_read_no_prior_matching_store_observed"],1)
        self.assertFalse(d["SPV_OpIAdd_input_prior_Store_class_proves_effective_memory_value"])

    def test_both_inputs_source_load_from_input_storage_without_local_writer(self):
        d=case([
            "%11 = OpVariable %ptr Input",
            "%12 = OpVariable %ptr Input",
            "%90 = OpLoad %1 %11",
            "%91 = OpLoad %1 %12"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_pointer_storage_storage_Input"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_rhs_pointer_storage_storage_Input"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_untrusted_path"],1)

    def test_volatile_lhs_load_is_untrusted_without_false_sameblock(self):
        d=case([
            "%120 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %120 %4",
            "%90 = OpLoad %1 %120 Volatile",
            "%91 = OpLoad %1 %5"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_pointer_storage_untrusted_or_malformed"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_untrusted_or_malformed"],1)

    def test_phi_lhs_not_fake_opload_proof(self):
        d=case([
            "%90 = OpPhi %1 %3 %A %4 %B",
            "%91 = OpLoad %1 %5"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_pointer_storage_not_OpLoad"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_not_OpLoad"],1)
        self.assertFalse(d["SPV_OpIAdd_input_memory_pointer_proves_original_DXBC_temp_mapping"])

    def test_earlier_store_of_later_source_does_not_retroactively_rewrite_snapshot(self):
        d=case([
            "%120 = OpInBoundsAccessChain %ptr %5 %3",
            "%90 = OpLoad %1 %120",
            "OpStore %120 %4",
            "%121 = OpInBoundsAccessChain %ptr %5 %4",
            "%91 = OpLoad %1 %121"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_no_prior_matching_store_observed"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_rhs_prior_store_at_read_no_prior_matching_store_observed"],1)

    def test_distinct_function_root_not_matched(self):
        d=case([
            "%15 = OpVariable %ptr Function",
            "%120 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %120 %4",
            "%121 = OpInBoundsAccessChain %ptr %15 %3",
            "%90 = OpLoad %1 %121",
            "%91 = OpLoad %1 %15"
        ])
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_lhs_prior_store_at_read_no_prior_matching_store_observed"],1)
        self.assertEqual(d["SPV_iadd_operand_actual_OpLoad_rhs_pointer_storage_Function_literal_address"],1)

    def test_gates_always_false_even_for_sameblock_writer_candidates(self):
        d=case([
            "%120 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %120 %4",
            "%90 = OpLoad %1 %120",
            "%91 = OpLoad %1 %120"
        ])
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])
        self.assertFalse(d["SPV_OpIAdd_input_prior_Store_class_proves_effective_memory_value"])
if __name__=="__main__":
    unittest.main()
