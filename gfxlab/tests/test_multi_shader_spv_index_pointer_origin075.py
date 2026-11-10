"""GFX075 source-free negative controls: actual CB OpLoad index POINTER origins."""
import unittest
from gfxlab.tools.multi_shader_spv_index_pointer_origin075 import authenticated_spv_CB_index_pointer_origins

AUTH={"%10":(2,0,16,8)}
def dis(body):
    return ("\n".join([
        "%1 = OpTypeInt 32 0",
        "%2 = OpConstant %1 0",
        "%3 = OpConstant %1 1",
        "%4 = OpConstant %1 2",
        "%10 = OpVariable %UBO Uniform",
        "%50 = OpFunction %void None %ft",
        "%51 = OpLabel",
        "%5 = OpVariable %ptr Function",
        *body,
        "OpReturn",
        "OpFunctionEnd",
    ])+"\n").encode("utf8")
def idxread(pointer="%5",tail=""):
    return [f"%6 = OpLoad %1 {pointer}{tail}", "%9 = OpBitcast %1 %6",
            "%20 = OpAccessChain %ptr %10 %2 %9", "%30 = OpLoad %vec4 %20"]
def counts(ops,auth=AUTH):
    return authenticated_spv_CB_index_pointer_origins(dis(ops),auth)

class TestGFX075OriginalIndexPointerOrigins(unittest.TestCase):
    def test_direct_function_pointer_store_is_only_syntactic_candidate(self):
        c=counts(["OpStore %5 %3",*idxread()])
        self.assertEqual(c["SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"],1)
        self.assertEqual(c["SPV_index_pointer_direct_definition_OpVariable"],1)
        self.assertEqual(c["SPV_index_pointer_root_storage_Function"],1)
        self.assertEqual(c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"],1)
        self.assertFalse(c["SPV_exact_pointer_ID_prior_Store_means_aliased_memory_value_proven"])
        self.assertFalse(c["SPV_pointer_origin_shape_proves_original_DXBC_temp_provenance"])

    def test_function_local_accesschain_exact_ssa_pointer_candidate(self):
        c=counts(["%7 = OpAccessChain %ptr %5 %3",
                  "OpStore %7 %4",*idxread("%7")])
        self.assertEqual(c["SPV_index_pointer_direct_definition_OpAccessChain"],1)
        self.assertEqual(c["SPV_index_pointer_root_storage_Function"],1)
        self.assertEqual(c["SPV_index_pointer_root_index_shape_literal"],1)
        self.assertEqual(c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"],1)

    def test_different_accesschain_ssa_pointer_not_exact_even_same_source_root(self):
        c=counts(["%7 = OpAccessChain %ptr %5 %3",
                  "%8 = OpAccessChain %ptr %5 %3",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(c.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)
        self.assertEqual(c["SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"],1)

    def test_copy_object_carries_function_storage_without_exposing_id(self):
        c=counts(["%7 = OpCopyObject %ptr %5",
                  "OpStore %7 %4",*idxread("%7")])
        self.assertEqual(c["SPV_index_pointer_direct_definition_OpCopyObject"],1)
        self.assertEqual(c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"],1)

    def test_branch_to_new_block_clears_same_block_store(self):
        c=counts(["OpStore %5 %4", "OpBranch %52",
                  "%52 = OpLabel",*idxread()])
        self.assertEqual(c.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)
        self.assertEqual(c["SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"],1)

    def test_function_call_memory_barrier_clears_store(self):
        c=counts(["OpStore %5 %4","%7 = OpFunctionCall %void %other",
                  *idxread()])
        self.assertEqual(c.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)

    def test_volatile_index_load_and_store_fail_closed(self):
        l=counts(["OpStore %5 %4",*idxread(tail=" Volatile")])
        self.assertEqual(l.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)
        s=counts(["OpStore %5 %4 Volatile",*idxread()])
        self.assertEqual(s.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)

    def test_dynamic_index_in_function_accesschain_is_not_trusted_literal(self):
        c=counts(["%7 = OpAccessChain %ptr %5 %6",
                  "OpStore %7 %4",*idxread("%7")])
        self.assertEqual(c["SPV_index_pointer_root_index_shape_dynamic"],1)
        self.assertEqual(c.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)

    def test_no_store_is_not_proof_original_source_lacks_writer(self):
        c=counts([*idxread()])
        self.assertEqual(c["SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"],1)
        self.assertFalse(c["originalShaderRestored"])

    def test_wrong_CBUbo_root_does_not_count_index_read(self):
        c=counts(["%6 = OpLoad %1 %5","%9 = OpBitcast %1 %6",
                  "%20 = OpAccessChain %ptr %11 %2 %9",
                  "%30 = OpLoad %vec4 %20"])
        self.assertEqual(c.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0),0)

    def test_iadd_literal_is_separately_accepted_with_actual_root_load(self):
        c=counts(["OpStore %5 %4",
                  "%6 = OpLoad %1 %5","%9 = OpBitcast %1 %6",
                  "%12 = OpIAdd %1 %9 %3",
                  "%20 = OpAccessChain %ptr %10 %2 %12",
                  "%30 = OpLoad %vec4 %20"])
        self.assertEqual(c["SPV_index_OpLoad_pointer_root_classified"],1)

    def test_duplicate_cb_loads_counted_as_occurrences(self):
        c=counts(["OpStore %5 %4",*idxread(),"%31 = OpLoad %vec4 %20"])
        self.assertEqual(c["SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"],2)
        self.assertEqual(c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"],2)

    def test_wrong_cb_authentication_must_fail(self):
        with self.assertRaisesRegex(ValueError,"INVALID_AUTHENTICATED"):
            counts([*idxread()],{"%10":(2,0,4,8)})

    def test_duplicate_ssa_def_must_fail(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SSA"):
            counts(["%6 = OpLoad %1 %5","%6 = OpLoad %1 %5",
                    "%9 = OpBitcast %1 %6",
                    "%20 = OpAccessChain %ptr %10 %2 %9","%30 = OpLoad %vec4 %20"])

    def test_unknown_pointer_origin_must_not_be_promoted(self):
        c=counts(["%7 = OpPhi %ptr %5 %A %5 %B",
                  "OpStore %7 %3",*idxread("%7")])
        self.assertEqual(c["SPV_index_pointer_root_storage_unresolved"],1)
        self.assertEqual(c.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)

    def test_source_device_gates_never_promoted_by_pointer_count(self):
        c=counts(["OpStore %5 %3",*idxread()])
        self.assertFalse(c["originalShaderRestored"])
        self.assertFalse(c["phase_closed"])
        self.assertFalse(c["original_Shader48_Material_CB_register_byte_semantics_proven"])
if __name__=="__main__":
    unittest.main()
