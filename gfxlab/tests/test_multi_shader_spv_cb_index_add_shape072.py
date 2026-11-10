"""GFX072 synthetic source vs translated SPV index shape comparison is COUNT ONLY."""
import unittest
from gfxlab.tools.multi_shader_spv_cb_index_add_shape072 import (
    shifted_source_spv_dynamic_UBO_reads,
    compare_private_stage_relative_source_to_spv_index_shapes,
)
from gfxlab.tests.test_multi_shader_spv_shifted_cb_index070 import spv,AUTH

def parse(lines):
    return shifted_source_spv_dynamic_UBO_reads(spv(lines),AUTH)

class TestGFX072CBIndexOffsetShape(unittest.TestCase):
    def test_immediate_plus_relative_spv_index_add_literal_bitcast_load(self):
        d=parse(["%7 = OpBitcast %1 %6",
                 "%9 = OpIAdd %1 %7 %4",
                 "%20 = OpAccessChain %ptr %10 %2 %9",
                 "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_dynamic_vec_load_index_direct_def_opcode_OpIAdd"],1)
        self.assertEqual(d["SPV_index_IAdd_exactly_one_literal_i32_operand"],1)
        self.assertEqual(d["SPV_index_IAdd_literal_is_positive"],1)
        self.assertEqual(d["SPV_index_IAdd_literal_plus_Bitcast_of_OpLoad"],1)
        cmp=compare_private_stage_relative_source_to_spv_index_shapes(0,1,d)
        self.assertTrue(cmp["per_stage_source_vs_SPV_direct_and_add_count_equal"])
        self.assertFalse(cmp["source_to_SPV_per_instruction_correspondence_proven"])

    def test_direct_relative_bitcast_opload_in_translated_spv(self):
        d=parse(["%7 = OpBitcast %1 %6",
                 "%20 = OpAccessChain %ptr %10 %2 %7",
                 "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_index_direct_Bitcast_of_OpLoad"],1)
        self.assertTrue(compare_private_stage_relative_source_to_spv_index_shapes(1,0,d)[
            "per_stage_source_vs_SPV_direct_and_add_count_equal"])

    def test_wrong_per_stage_count_never_claims_match(self):
        d=parse(["%7 = OpBitcast %1 %6",
                 "%20 = OpAccessChain %ptr %10 %2 %7",
                 "%30 = OpLoad %vec4 %20"])
        self.assertFalse(compare_private_stage_relative_source_to_spv_index_shapes(0,1,d)[
            "per_stage_source_vs_SPV_direct_and_add_count_equal"])

    def test_add_without_immediate_does_not_claim_literal_plus_load(self):
        d=parse(["%7 = OpBitcast %1 %6",
                 "%9 = OpIAdd %1 %7 %6",
                 "%20 = OpAccessChain %ptr %10 %2 %9",
                 "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_index_IAdd_not_one_literal_operand"],1)
        self.assertEqual(d.get("SPV_index_IAdd_literal_plus_Bitcast_of_OpLoad",0),0)

    def test_offset_literal_without_bitcast_of_load_is_not_accepted_as_proof(self):
        d=parse(["%9 = OpIAdd %1 %6 %4",
                 "%20 = OpAccessChain %ptr %10 %2 %9",
                 "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_index_IAdd_exactly_one_literal_i32_operand"],1)
        self.assertEqual(d.get("SPV_index_IAdd_literal_plus_Bitcast_of_OpLoad",0),0)

    def test_wrong_shape_count_input_rejects_negative_bool_or_inconsistent_spv(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_STAGE_COUNT"):
            compare_private_stage_relative_source_to_spv_index_shapes(-1,0,{})
        with self.assertRaisesRegex(ValueError,"SOURCE_STAGE_COUNT"):
            compare_private_stage_relative_source_to_spv_index_shapes(True,0,{})
        with self.assertRaisesRegex(ValueError,"ROOT_COUNT_INCONSISTENT"):
            compare_private_stage_relative_source_to_spv_index_shapes(0,0,{
                "SPV_authenticated_dynamic_vec_OpLoad_occurrences":0,
                "SPV_dynamic_vec_load_index_direct_def_opcode_OpBitcast":1,
            })
if __name__=="__main__":
    unittest.main()
