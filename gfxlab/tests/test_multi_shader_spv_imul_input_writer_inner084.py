"""GFX084: only public opcode taxonomies for private prior-Store OpBitcast SSA."""
import json
import unittest
from gfxlab.tools.multi_shader_spv_imul_input_writer_inner084 import (
    authenticated_spv_CB_index_imul_input_writer_underlying084
)
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis, idxread, AUTH

def counts(lines,auth=AUTH):
    return authenticated_spv_CB_index_imul_input_writer_underlying084(dis(lines),auth)

def case(inner, extras=(), before=True):
    # Distinct result IDs from the shared fixture %6/%9/%20/%30.
    prefix=[
      *extras,
      inner,
      "%81 = OpBitcast %1 %80",
      "%71 = OpInBoundsAccessChain %ptr %5 %3",
      "%72 = OpInBoundsAccessChain %ptr %5 %3",
      "%66 = OpLoad %1 %72",
    ]
    if before:
        prefix.insert(prefix.index("%66 = OpLoad %1 %72"),"OpStore %71 %81")
    else:
        prefix.append("OpStore %71 %81")
    return counts([*prefix,
      "%70 = OpConstant %1 3",
      "%40 = OpIMul %1 %66 %70",
      "%41 = OpBitcast %1 %40",
      "%7 = OpInBoundsAccessChain %ptr %5 %3",
      "%8 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %7 %41",*idxread("%8")])

class TestGFX084StoredValueInnerSPVOpcode(unittest.TestCase):
    def test_composite_extract_single_literal_from_vector_load(self):
        c=case("%80 = OpCompositeExtract %1 %90 0",
               extras=["%90 = OpLoad %vec4 %5"])
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpCompositeExtract"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_one_literal_component"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_source_class_composite_source_OpLoad"],1)
        self.assertFalse(c["SPV_Bitcast_inner_opcode_proves_original_DXBC_temp_component"])

    def test_multiple_literal_composite_indices(self):
        c=case("%80 = OpCompositeExtract %1 %90 0 2",
               extras=["%90 = OpCompositeConstruct %struct %3 %4"])
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_multiple_literal_components"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_source_class_composite_source_OpCompositeConstruct"],1)

    def test_nonliteral_component_index_rejected_as_unverified(self):
        c=case("%80 = OpCompositeExtract %1 %90 %dynamic",
               extras=["%90 = OpLoad %vec4 %5"])
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_nonliteral_or_malformed_component"],1)

    def test_underlying_integer_add_does_not_imply_shift_or_source_temp(self):
        c=case("%80 = OpIAdd %1 %90 %3",
               extras=["%90 = OpLoad %1 %5"])
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_integer_arithmetic"],1)
        self.assertFalse(c["SPV_OpIMul_input_prior_writer_value_SSA_proves_original_DXBC_ISHL"])

    def test_inner_memory_load_function_path_no_value_proof(self):
        c=case("%80 = OpLoad %1 %5")
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpLoad"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_Function_literal_pointer"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_source_class_memory_reaching_value_unproven"],1)

    def test_control_merge_is_not_expression_equivalence(self):
        c=case("%80 = OpSelect %1 %condition %3 %4")
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpSelect"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_control_or_call_merge"],1)

    def test_unknown_custom_opcode_is_generic_and_never_leaked(self):
        c=case("%80 = OpVeryPrivateShaderName %1 %3")
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_missing_or_other"],1)
        text=json.dumps(c)
        self.assertNotIn("VeryPrivateShaderName",text)
        self.assertNotIn("%80",text)
        self.assertFalse(c["originalShaderRestored"])
        self.assertFalse(c["phase_closed"])

    def test_only_future_store_is_never_preexisting_input_writer(self):
        c=case("%80 = OpCompositeExtract %1 %90 0",
               extras=["%90 = OpLoad %vec4 %5"],before=False)
        self.assertEqual(c.get("SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpCompositeExtract",0),0)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_no_prior_matching_store_observed"],1)

    def test_bitcast_wrappers_are_bounded(self):
        c=case("%80 = OpBitcast %1 %91",
               extras=["%91 = OpCompositeExtract %1 %90 0",
                       "%90 = OpLoad %vec4 %5"])
        self.assertEqual(c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpCompositeExtract"],1)
        self.assertFalse(c["SPV_CompositeExtract_source_SSA_proves_actual_pixel_parity"])

if __name__=="__main__":
    unittest.main()
