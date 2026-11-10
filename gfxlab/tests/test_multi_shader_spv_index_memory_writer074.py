"""GFX074 source-free negative controls for bounded SPV local store provenance."""
import unittest
from gfxlab.tools.multi_shader_spv_index_memory_writer074 import spv_index_local_store_candidates

AUTH={"%10":(2,0,16,8)}
def module(body):
    return ("\n".join([
        "%1 = OpTypeInt 32 0",
        "%2 = OpConstant %1 0",
        "%3 = OpConstant %1 1",
        "%4 = OpConstant %1 2",
        "%5 = OpVariable %ptr Function",
        "%10 = OpVariable %UBO Uniform",
        "%50 = OpFunction %void None %ft",
        "%51 = OpLabel",
        *body,
        "OpReturn",
        "OpFunctionEnd",
    ])+"\n").encode()
def read(index="%9"):
    return [f"%20 = OpAccessChain %ptr %10 %2 {index}",
            "%30 = OpLoad %vec4 %20"]
def idx_load():
    return ["%6 = OpLoad %1 %5","%9 = OpBitcast %1 %6"]
def probe(lines,auth=AUTH):
    return spv_index_local_store_candidates(module(lines),auth)

class TestGFX074SPVIndexLocalProvenance(unittest.TestCase):
    def test_same_block_store_shift_local_only(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4",
                 "OpStore %5 %7",*idx_load(),*read()])
        self.assertEqual(d["SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences"],1)
        self.assertEqual(d["SPV_same_block_local_store_with_shift_SSA_ancestor_candidates"],1)
        self.assertFalse(d["SPV_local_store_shift_proves_original_DXBC_ISHL_correspondence"])
        self.assertFalse(d["original_DXBC_temp_to_SPV_index_loaded_value_equivalence_proven"])

    def test_same_block_nonshift_value_still_not_proven(self):
        d=probe(["OpStore %5 %3",*idx_load(),*read()])
        self.assertEqual(d["SPV_same_block_local_store_without_proven_shift_candidates"],1)

    def test_no_same_block_store_is_unknown_not_missing_source_writer(self):
        d=probe([*idx_load(),*read()])
        self.assertEqual(d["SPV_index_memory_no_preceding_same_block_store"],1)

    def test_cross_block_store_does_not_prove_dominance(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4","OpStore %5 %7",
                 "OpBranch %52","%52 = OpLabel",*idx_load(),*read()])
        self.assertEqual(d["SPV_index_memory_no_preceding_same_block_store"],1)

    def test_function_call_clears_writer_cache(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4","OpStore %5 %7",
                 "%40 = OpFunctionCall %void %other",*idx_load(),*read()])
        self.assertEqual(d["SPV_index_memory_no_preceding_same_block_store"],1)

    def test_unknown_store_alias_barrier(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4","OpStore %5 %7",
                 "OpStore %unknown %3",*idx_load(),*read()])
        self.assertEqual(d["SPV_index_memory_no_preceding_same_block_store"],1)
        self.assertEqual(d["SPV_untrusted_store_pointer_or_memory_operands_barriers"],1)

    def test_add_with_literal_preserves_actual_index_value_load(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4","OpStore %5 %7",
                 *idx_load(),"%12 = OpIAdd %1 %9 %4",*read("%12")])
        self.assertEqual(d["SPV_same_block_local_store_with_shift_SSA_ancestor_candidates"],1)

    def test_untrusted_select_index_never_claims_writer(self):
        d=probe(["%7 = OpShiftLeftLogical %1 %3 %4","OpStore %5 %7",
                 *idx_load(),"%12 = OpSelect %1 %cond %9 %3",*read("%12")])
        self.assertEqual(d["SPV_index_root_unclassified"],1)
        self.assertEqual(d.get("SPV_same_block_local_store_with_shift_SSA_ancestor_candidates",0),0)

    def test_unused_chain_is_not_real_gpu_load(self):
        d=probe([*idx_load(),"%20 = OpAccessChain %ptr %10 %2 %9"])
        self.assertEqual(d.get("SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences",0),0)

    def test_wrong_root_never_authenticated(self):
        d=probe([*idx_load(),"%20 = OpAccessChain %ptr %11 %2 %9",
                 "%30 = OpLoad %vec4 %20"])
        self.assertEqual(d.get("SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences",0),0)

    def test_duplicate_ubo_loads_are_counted_individually(self):
        d=probe(["OpStore %5 %3",*idx_load(),*read(),
                 "%31 = OpLoad %vec4 %20"])
        self.assertEqual(d["SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences"],2)
        self.assertEqual(d["SPV_same_block_local_store_without_proven_shift_candidates"],2)

    def test_volatile_index_load_not_promoted(self):
        d=probe(["OpStore %5 %3","%6 = OpLoad %1 %5 Volatile",
                 "%9 = OpBitcast %1 %6",*read()])
        self.assertEqual(d["SPV_index_memory_pointer_alias_or_volatile_unknown"],1)

    def test_bad_ubo_layout_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_ORIGINAL_CB_LAYOUT"):
            probe([*idx_load(),*read()],{"%10":(2,4,16,8)})

    def test_duplicate_spv_result_fails(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_RESULT"):
            probe(["%6 = OpLoad %1 %5","%6 = OpLoad %1 %5",*read("%6")])

    def test_no_false_shader_restoration(self):
        d=probe([*idx_load(),*read()])
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])
        self.assertFalse(d["GFX054_original_Material_property_to_CB_member_bridge_proven"])

if __name__=="__main__":unittest.main()
