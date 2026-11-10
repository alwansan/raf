"""GFX077 source-free negative controls: actual CB OpLoad index POINTER origins."""
import unittest
from gfxlab.tools.multi_shader_spv_index_local_store_value077 import authenticated_spv_CB_index_local_store_value_producers

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
    return authenticated_spv_CB_index_local_store_value_producers(dis(ops),auth)

class TestGFX077OriginalIndexPointerOrigins(unittest.TestCase):
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

class TestGFX077NormalizedLiteralFunctionAddressPath(unittest.TestCase):
    def test_equivalent_literal_path_different_pointer_ids_sameblock_candidate(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"],1)
        self.assertEqual(d.get("SPV_same_block_prior_OpStore_exact_pointer_ID_candidates",0),0)
        self.assertFalse(d["SPV_equivalent_Function_literal_address_paths_prove_runtime_dataflow"])

    def test_different_literal_index_rejected_even_when_same_function_root(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %4",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_no_prior_matching_path_store"],1)

    def test_store_before_branch_only_crossblock_syntactic_evidence(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4", "OpBranch %52",
                  "%52 = OpLabel",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  *idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"],1)
        self.assertFalse(d["SPV_equivalent_address_path_store_proves_CFG_dominance"])

    def test_function_call_invalidates_previous_write_candidate(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4",
                  "%99 = OpFunctionCall %void %func",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  *idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_no_prior_matching_path_store"],1)

    def test_unknown_pointer_store_barrier_invalidates(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4","OpStore %unknown %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  *idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_no_prior_matching_path_store"],1)

    def test_opcopyobject_other_pointer_id_same_function_literal_path(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpCopyObject %ptr %7",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"],1)
        self.assertFalse(d["SPV_equivalent_address_path_proves_DXBC_temp_to_SPV_SSA_mapping"])

    def test_dynamic_function_path_not_promoted(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %6",
                  "OpStore %7 %4",*idxread("%7")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_unresolved"],1)
        self.assertEqual(d.get("SPV_index_normalized_Function_literal_path_same_block_path_store_candidate",0),0)

    def test_second_function_root_not_same_address_path(self):
        d=counts(["%15 = OpVariable %ptr Function",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %15 %3",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_no_prior_matching_path_store"],1)

    def test_no_unproven_shader_claims(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4",*idxread("%7")])
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])
        self.assertFalse(d["SPV_equivalent_address_path_proves_DXBC_temp_to_SPV_SSA_mapping"])


class TestGFX077BoundedSameBlockSPVStoreValueSyntax(unittest.TestCase):
    def test_original_sameblock_address_candidate_direct_shift_Store_value(self):
        c=counts(["%40 = OpShiftLeftLogical %1 %3 %4",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %40",*idxread("%8")])
        self.assertEqual(c["SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpShiftLeftLogical"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_direct_shift"],1)
        self.assertFalse(c["SPV_Store_value_SSA_shift_ancestry_proves_original_DXBC_ISHL"])

    def test_shift_ancestor_through_iadd_is_not_mislabelled_direct(self):
        c=counts(["%40 = OpShiftLeftLogical %1 %3 %4",
                  "%41 = OpIAdd %1 %40 %3",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %41",*idxread("%8")])
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpIAdd"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_via_shift"],1)

    def test_constant_stored_value_has_no_shift(self):
        c=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %4",*idxread("%8")])
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpConstant"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_no_shift"],1)

    def test_memory_loaded_Store_value_is_unknown_not_negated(self):
        c=counts(["%40 = OpLoad %1 %5",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %40",*idxread("%8")])
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpLoad"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_unknown"],1)

    def test_control_select_Store_value_has_unknown_shift_ancestry(self):
        c=counts(["%40 = OpSelect %1 %condition %3 %4",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %40",*idxread("%8")])
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpSelect"],1)
        self.assertEqual(c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_unknown"],1)

    def test_previous_block_Store_is_not_a_sameblock_value_origin(self):
        c=counts(["%40 = OpShiftLeftLogical %1 %3 %4",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %40", "OpBranch %52",
                  "%52 = OpLabel",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",*idxread("%8")])
        self.assertEqual(c["SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"],1)
        self.assertEqual(c.get("SPV_sameblock_equivalent_path_Store_value_immediate_producer_OpShiftLeftLogical",0),0)
        self.assertFalse(c["SPV_local_store_value_producer_proves_actual_runtime_index_value"])

    def test_unknown_alias_barrier_blocks_Store_value_claim(self):
        c=counts(["%40 = OpShiftLeftLogical %1 %3 %4",
                  "%7 = OpInBoundsAccessChain %ptr %5 %3",
                  "OpStore %7 %40","OpStore %unknown %3",
                  "%8 = OpInBoundsAccessChain %ptr %5 %3",*idxread("%8")])
        self.assertEqual(c.get("SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_direct_shift",0),0)
        self.assertEqual(c["SPV_index_normalized_Function_literal_path_no_prior_matching_path_store"],1)

if __name__=="__main__":
    unittest.main()
