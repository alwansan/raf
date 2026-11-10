"""GFX080 source-free negative controls for anonymous SPV unknown-terminal
and strict CFG block dominance, never effective Store->Load memory SSA."""
import unittest
from gfxlab.tools.multi_shader_spv_integer_terminal_shapes080 import authenticated_spv_CB_index_unknown_integer_opcode_shapes080
from gfxlab.tools.multi_shader_spv_cfg_dominance078 import StrictSpvBlockCfg
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

def counts(ops, auth=AUTH):
    return authenticated_spv_CB_index_unknown_integer_opcode_shapes080(dis(ops),auth)

class TestGFX080StrictCfg(unittest.TestCase):
    def test_direct_branch_block_dominance_only(self):
        rec=[
          ("%50","OpFunction",["%void","None","%fn"]),
          ("%51","OpLabel",[]),
          (None,"OpBranch",["%52"]),
          ("%52","OpLabel",[]),
          (None,"OpReturn",[]),
          (None,"OpFunctionEnd",[])]
        g=StrictSpvBlockCfg(rec)
        self.assertEqual(g.classify("%51","%52"),"dominates")
        self.assertEqual(g.classify("%52","%51"),"not_dominates")
        self.assertEqual(g.classify("%52","%52"),"same_block")

    def test_diamond_does_not_promote_one_arm_to_dominator(self):
        rec=[
          ("%50","OpFunction",[]),("%51","OpLabel",[]),
          (None,"OpBranchConditional",["%cond","%52","%53"]),
          ("%52","OpLabel",[]),(None,"OpBranch",["%54"]),
          ("%53","OpLabel",[]),(None,"OpBranch",["%54"]),
          ("%54","OpLabel",[]),(None,"OpReturn",[]),
          (None,"OpFunctionEnd",[])]
        g=StrictSpvBlockCfg(rec)
        self.assertEqual(g.classify("%52","%54"),"not_dominates")
        self.assertEqual(g.classify("%51","%54"),"dominates")

    def test_missing_target_is_unknown_fail_closed(self):
        rec=[("%50","OpFunction",[]),("%51","OpLabel",[]),
             (None,"OpBranch",["%missing"]),
             ("%52","OpLabel",[]),(None,"OpReturn",[]),
             (None,"OpFunctionEnd",[])]
        self.assertEqual(StrictSpvBlockCfg(rec).classify("%51","%52"),"unknown")

    def test_malformed_block_without_terminator_is_unknown(self):
        rec=[("%50","OpFunction",[]),("%51","OpLabel",[]),
             ("%52","OpLabel",[]),(None,"OpReturn",[]),
             (None,"OpFunctionEnd",[])]
        self.assertEqual(StrictSpvBlockCfg(rec).classify("%51","%52"),"unknown")

    def test_invalid_cross_function_branch_not_accepted(self):
        rec=[("%50","OpFunction",[]),("%51","OpLabel",[]),
             (None,"OpBranch",["%61"]),(None,"OpFunctionEnd",[]),
             ("%60","OpFunction",[]),("%61","OpLabel",[]),
             (None,"OpReturn",[]),(None,"OpFunctionEnd",[])]
        self.assertEqual(StrictSpvBlockCfg(rec).classify("%51","%61"),"unknown")

    def test_switch_branch_and_loop_cfg(self):
        rec=[("%50","OpFunction",[]),("%51","OpLabel",[]),
             (None,"OpBranch",["%52"]),
             ("%52","OpLabel",[]),
             (None,"OpSwitch",["%selector","%54","0","%53"]),
             ("%53","OpLabel",[]),(None,"OpBranch",["%52"]),
             ("%54","OpLabel",[]),(None,"OpReturn",[]),
             (None,"OpFunctionEnd",[])]
        self.assertEqual(StrictSpvBlockCfg(rec).classify("%52","%54"),"dominates")

class TestGFX080AuthenticatedCBIndexStoreUnknowns(unittest.TestCase):
    @staticmethod
    def crossblock():
        return ["%7 = OpInBoundsAccessChain %ptr %5 %3",
                "OpStore %7 %4","OpBranch %52",
                "%52 = OpLabel",
                "%8 = OpInBoundsAccessChain %ptr %5 %3",*idxread("%8")]

    def test_crossblock_direct_edge_dominates_but_not_memory(self):
        d=counts(self.crossblock())
        self.assertEqual(d["SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"],1)
        self.assertEqual(d["SPV_prior_path_store_CFG_block_relation_dominates"],1)
        self.assertFalse(d["SPV_CFG_block_dominance_proves_Store_memory_value_reaching_Load"])

    def test_diamond_writer_arm_does_not_dominate_join(self):
        d=counts(["OpBranchConditional %condition %52 %53",
            "%52 = OpLabel",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %4","OpBranch %54",
            "%53 = OpLabel","OpBranch %54",
            "%54 = OpLabel",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",*idxread("%8")])
        self.assertEqual(d["SPV_prior_path_store_CFG_block_relation_not_dominates"],1)

    def test_crossblock_invalid_unknown_target_no_cfg_proof(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %4","OpBranch %unused",
            "%52 = OpLabel",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",*idxread("%8")])
        self.assertEqual(d["SPV_prior_path_store_CFG_block_relation_unknown"],1)

    def test_unknown_value_terminal_load_but_no_absence_of_shift(self):
        d=counts(["%40 = OpLoad %1 %5",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%8")])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_OpLoad"],1)
        self.assertFalse(d["SPV_unknown_Store_value_terminal_proves_absent_shift"])

    def test_unknown_value_terminal_select_and_phi_negative(self):
        d=counts(["%40 = OpSelect %1 %cond %3 %4",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%7")])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_OpSelect"],1)

    def test_unknown_value_terminal_composite_extract(self):
        d=counts(["%40 = OpCompositeExtract %1 %other 0",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%7")])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_OpCompositeExtract"],1)

    def test_sameblock_shift_candidate_not_misclassified_unknown(self):
        d=counts(["%40 = OpShiftLeftLogical %1 %3 %4",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%7")])
        self.assertEqual(d["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_via_shift"],1)
        self.assertEqual(sum(v for k,v in d.items() if k.startswith(
            "SPV_sameblock_store_unknown_ancestry_terminal_")),0)

    def test_source_and_gpu_claims_remain_false(self):
        d=counts(self.crossblock())
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])
        self.assertFalse(d["SPV_equivalent_address_path_proves_DXBC_temp_to_SPV_SSA_mapping"])
        self.assertFalse(d["SPV_CFG_block_dominance_proves_Store_memory_value_reaching_Load"])

class TestGFX080PublicOpcodeFamilyClassification(unittest.TestCase):
    def _store_value(self,expression):
        return counts([*expression,
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            *idxread("%8")])

    def test_float_math_terminal_family(self):
        d=self._store_value(["%40 = OpFMul %1 %other %3"])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_float_math"],1)

    def test_integer_math_terminal_family(self):
        d=self._store_value(["%40 = OpIMul %1 %other %3"])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_integer_math"],1)

    def test_convert_unsigned_terminal_family(self):
        d=self._store_value(["%40 = OpConvertFToU %1 %other"])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_conversion"],1)

    def test_logical_bitwise_nontransparent_terminal_family(self):
        d=self._store_value(["%40 = OpBitFieldUExtract %1 %other %3 %4"])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_integer_bitwise"],1)

    def test_vendor_or_unlisted_opcode_must_not_export_private_value(self):
        d=self._store_value(["%40 = OpPrivateUnknownVendorThing %1 %other"])
        self.assertEqual(d["SPV_sameblock_store_unknown_ancestry_terminal_other_public_opcode"],1)
        self.assertFalse(d["SPV_unknown_opcode_family_is_shader_semantic_proof"])

    def test_preserve_47_crossblock_block_dominance_not_memory(self):
        d=counts(["%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %4","OpBranch %52",
            "%52 = OpLabel",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            *idxread("%8")])
        self.assertEqual(d["SPV_prior_path_store_CFG_block_relation_dominates"],1)
        self.assertFalse(d["SPV_CFG_block_dominance_proves_Store_memory_value_reaching_Load"])

class TestGFX080IntegerOperand32BitShape(unittest.TestCase):
    def read_with_value(self,defs,value_expr):
        return counts([*defs,
            value_expr,
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            *idxread("%8")])

    def test_imul_one_literal_pow2_with_actual_dynamic_operand(self):
        c=self.read_with_value(["%66 = OpLoad %1 %5"],
           "%40 = OpIMul %1 %66 %4")
        self.assertEqual(c["SPV_unknown_integer_terminal_public_core_opcode_OpIMul"],1)
        self.assertEqual(c["SPV_unknown_integer_terminal_OpIMul_literal_shape_one_unsigned_power_of_two_literal"],1)
        self.assertFalse(c["SPV_OpIMul_literal_power_two_proves_original_DXBC_ISHL"])

    def test_imul_nonpower_and_zero_literals(self):
        a=self.read_with_value(["%66 = OpLoad %1 %5",
           "%70 = OpConstant %1 3"],"%40 = OpIMul %1 %66 %70")
        self.assertEqual(a["SPV_unknown_integer_terminal_OpIMul_literal_shape_nonpower_of_two_literal"],1)
        b=self.read_with_value(["%66 = OpLoad %1 %5"],"%40 = OpIMul %1 %66 %2")
        self.assertEqual(b["SPV_unknown_integer_terminal_OpIMul_literal_shape_literal_zero"],1)

    def test_imul_both_literal_not_fake_variable_shift(self):
        c=self.read_with_value([],"%40 = OpIMul %1 %3 %4")
        self.assertEqual(c["SPV_unknown_integer_terminal_OpIMul_literal_shape_both_constant_operands"],1)

    def test_imul_no_literal_or_untrusted_operand_unknown(self):
        a=self.read_with_value(["%66 = OpLoad %1 %5",
           "%60 = OpLoad %1 %5"],"%40 = OpIMul %1 %66 %60")
        self.assertEqual(a["SPV_unknown_integer_terminal_OpIMul_literal_shape_no_proven_literal"],1)
        b=self.read_with_value([],"%40 = OpIMul %1 %unknown %4")
        self.assertEqual(b["SPV_unknown_integer_terminal_OpIMul_literal_shape_other_operand_type_or_origin_unproven"],1)

    def test_imul_wrong_32bit_type_not_promoted(self):
        c=self.read_with_value(["%66 = OpLoad %1 %5"],
           "%40 = OpIMul %unknownType %6 %4")
        self.assertEqual(c["SPV_unknown_integer_terminal_OpIMul_literal_shape_unverified_integer_width_or_arity"],1)

    def test_imul_signed_highbit_literal_classified_u32_without_sign_claim(self):
        c=self.read_with_value(["%66 = OpLoad %1 %5",
             "%70 = OpConstant %1 -2147483648"],
             "%40 = OpIMul %1 %66 %70")
        self.assertEqual(c["SPV_unknown_integer_terminal_OpIMul_literal_shape_one_unsigned_power_of_two_literal"],1)
        self.assertFalse(c["SPV_OpIMul_literal_power_two_proves_memory_Store_to_Load_value"])

    def test_integer_iadd_kept_separate_not_imul_literal(self):
        c=self.read_with_value(["%66 = OpLoad %1 %5"],
             "%40 = OpIAdd %1 %66 %4")
        # GFX077 bounded SSA walk already knows IAdd, but root has an
        # untrusted memory-loaded operand so the ancestry is UNKNOWN.
        self.assertEqual(c["SPV_sameblock_store_unknown_ancestry_terminal_OpIAdd"],1)
        self.assertEqual(c.get("SPV_unknown_integer_terminal_public_core_opcode_OpIAdd",0),0)
        self.assertEqual(c.get("SPV_unknown_integer_terminal_OpIMul_literal_shape_not_imul",0),0)

if __name__=="__main__":
    unittest.main()
