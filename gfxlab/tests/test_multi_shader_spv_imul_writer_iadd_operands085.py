"""GFX085 source-free controls for original SPV OpIAdd input operand origins."""
import unittest
from gfxlab.tools.multi_shader_spv_imul_writer_iadd_operands085 import (
    authenticated_spv_CB_index_imul_input_writer_iadd_operands085
)
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

def counts(body,auth=AUTH):
    return authenticated_spv_CB_index_imul_input_writer_iadd_operands085(dis(body),auth)

def sample(iadd_line,pre=(),writer_before=True):
    src=[*pre,iadd_line,"%81 = OpBitcast %1 %80",
         "%71 = OpInBoundsAccessChain %ptr %5 %3",
         "%72 = OpInBoundsAccessChain %ptr %5 %3"]
    if writer_before:src.append("OpStore %71 %81")
    src.append("%66 = OpLoad %1 %72")
    if not writer_before:src.append("OpStore %71 %81")
    return counts([*src,
      "%70 = OpConstant %1 3",
      "%40 = OpIMul %1 %66 %70",
      "%41 = OpBitcast %1 %40",
      "%7 = OpInBoundsAccessChain %ptr %5 %3",
      "%8 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %7 %41",*idxread("%8")])

class TestGFX085IntegerAddOperandProvenance(unittest.TestCase):
    def test_left_dynamic_load_right_literal_nonzero(self):
        d=sample("%80 = OpIAdd %1 %90 %4",
                 ["%90 = OpLoad %1 %5"])
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_constant_nonzero_dynamic"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_source_OpLoad"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_constant"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_type_verified_32bit_scalar_integer_opcode"],1)
        self.assertFalse(d["SPV_OpIAdd_operand_shape_proves_numeric_input_parity"])

    def test_literal_zero_left_dynamic_bitcast_to_load_right(self):
        d=sample("%80 = OpIAdd %1 %2 %91",
                 ["%90 = OpLoad %1 %5","%91 = OpBitcast %1 %90"])
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_constant_zero_dynamic"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_constant"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_source_OpLoad"],1)

    def test_two_dynamic_inputs_remain_unproven(self):
        d=sample("%80 = OpIAdd %1 %90 %91",
                 ["%90 = OpLoad %1 %5",
                  "%91 = OpSelect %1 %cond %3 %4"])
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_dynamic_dynamic"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_source_OpSelect"],1)
        self.assertFalse(d["SPV_OpIAdd_operand_SSA_proves_original_DXBC_component_mapping"])

    def test_both_constant_operands_are_not_variable_proof(self):
        d=sample("%80 = OpIAdd %1 %2 %4")
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_constant_nonzero_constant_zero"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_constant"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_constant"],1)

    def test_wrong_iadd_type_not_upgraded_to_32bit_scalar(self):
        d=sample("%80 = OpIAdd %otherType %90 %4",
                 ["%90 = OpLoad %1 %5"])
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_not_verified_32bit_OpIAdd"],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_type_unverified"],1)

    def test_unknown_operand_has_anonymous_unknown_source(self):
        d=sample("%80 = OpIAdd %1 %unknown %4")
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_dynamic_constant_nonzero".replace("dynamic_constant_nonzero","constant_nonzero_dynamic")],1)
        self.assertEqual(d["SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_source_missing_or_other"],1)

    def test_future_writer_not_used_for_previous_input_load(self):
        d=sample("%80 = OpIAdd %1 %90 %4",
                 ["%90 = OpLoad %1 %5"],writer_before=False)
        self.assertEqual(d.get("SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_constant_nonzero_dynamic",0),0)
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_no_prior_matching_store_observed"],1)

    def test_original_shaders_never_promoted_from_shape(self):
        d=sample("%80 = OpIAdd %1 %90 %4",["%90 = OpLoad %1 %5"])
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])
        self.assertFalse(d["SPV_OpIAdd_operand_SSA_proves_original_DXBC_component_mapping"])

if __name__=="__main__":
    unittest.main()
