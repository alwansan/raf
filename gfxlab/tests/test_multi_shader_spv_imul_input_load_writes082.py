"""GFX082 source-free negative controls for anonymous SPV unknown-terminal
and strict CFG block dominance, never effective Store->Load memory SSA."""
import unittest
from gfxlab.tools.multi_shader_spv_imul_input_load_writes082 import authenticated_spv_CB_index_imul_input_load_writes082
from gfxlab.tools.multi_shader_spv_cfg_dominance078 import StrictSpvBlockCfg
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

def counts(ops, auth=AUTH):
    return authenticated_spv_CB_index_imul_input_load_writes082(dis(ops),auth)

class TestGFX082StrictCfg(unittest.TestCase):
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

class TestGFX082AuthenticatedCBIndexStoreUnknowns(unittest.TestCase):
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

class TestGFX082PublicOpcodeFamilyClassification(unittest.TestCase):
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

class TestGFX082IntegerOperand32BitShape(unittest.TestCase):
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


class TestGFX082NonpowerIMulDynamicInputSSA(unittest.TestCase):
    def scan(self,input_lines,mul_operand="%66",op="OpLoad"):
        return counts([
            *input_lines,
            "%70 = OpConstant %1 3",
            f"%40 = OpIMul %1 {mul_operand} %70",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%8")
        ])

    def test_source_input_direct_function_load(self):
        c=self.scan(["%66 = OpLoad %1 %5"])
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_immediate_OpLoad"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_memory_origin_Function_literal_path"],1)
        self.assertFalse(c["SPV_OpIMul_input_OpLoad_proves_reaching_memory_Store"])
        self.assertFalse(c["SPV_OpIMul_input_SSA_syntax_proves_original_DXBC_source_temp"])

    def test_input_bitcast_load_under_bounded_chain(self):
        c=self.scan(["%65 = OpLoad %1 %5",
                     "%66 = OpBitcast %1 %65"])
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_immediate_OpBitcast"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_memory_origin_Function_literal_path"],1)

    def test_input_select_or_phi_not_confused_with_memory_value(self):
        a=self.scan(["%66 = OpSelect %1 %cond %3 %4"])
        self.assertEqual(a["SPV_nonpower_OpIMul_dynamic_input_terminal_OpSelect"],1)
        self.assertEqual(a["SPV_nonpower_OpIMul_dynamic_input_memory_origin_nonmemory_terminal"],1)
        b=self.scan(["%66 = OpPhi %1 %3 %labelA %4 %labelB"])
        self.assertEqual(b["SPV_nonpower_OpIMul_dynamic_input_terminal_OpPhi"],1)
        self.assertFalse(b["SPV_OpIMul_input_SSA_syntax_proves_original_DXBC_source_temp"])

    def test_untrusted_volatile_memory_load(self):
        c=self.scan(["%66 = OpLoad %1 %5 Volatile"])
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_memory_origin_untrusted_memory_operands"],1)

    def test_function_dynamic_index_address_fails_closed(self):
        c=self.scan(["%65 = OpLoad %1 %5",
                     "%72 = OpInBoundsAccessChain %ptr %5 %65",
                     "%66 = OpLoad %1 %72"])
        self.assertTrue(c["SPV_nonpower_OpIMul_dynamic_input_memory_origin_Function_dynamic_or_unresolved_path"]==1)

    def test_unrecognized_operand_result_is_anonymous_other(self):
        c=self.scan(["%66 = OpMysteryPrivateOpcode %1 %3"])
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_immediate_other"],1)
        self.assertEqual(c["SPV_nonpower_OpIMul_dynamic_input_terminal_other"],1)
        self.assertFalse(c["originalShaderRestored"])

    def test_imul_power_of_two_not_enter_nonpower_cohort(self):
        c=counts([
            "%66 = OpLoad %1 %5",
            "%40 = OpIMul %1 %66 %4",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%7")
        ])
        self.assertEqual(sum(v for k,v in c.items() if k.startswith(
            "SPV_nonpower_OpIMul_dynamic_input_")),0)
        self.assertEqual(c["SPV_unknown_integer_terminal_OpIMul_literal_shape_one_unsigned_power_of_two_literal"],1)

class TestGFX082ActualIMulInputLoadReadTimeStore(unittest.TestCase):
    def make(self,pre):
        return counts([*pre,
            "%70 = OpConstant %1 3",
            "%40 = OpIMul %1 %66 %70",
            "%41 = OpBitcast %1 %40",
            "%7 = OpInBoundsAccessChain %ptr %5 %3",
            "%8 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %7 %41",*idxread("%8")])

    def test_same_block_equivalent_path_store_before_input_load(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %71 %4",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_same_block_store_syntax"],1)
        self.assertFalse(d["SPV_OpIMul_input_prior_Store_syntax_proves_memory_reaching_value"])

    def test_later_store_cannot_be_readtime_writer(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72",
            "OpStore %71 %4"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_no_prior_matching_store_observed"],1)

    def test_other_literal_path_is_not_same_address(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %4",
            "OpStore %71 %4",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_no_prior_matching_store_observed"],1)

    def test_direct_branch_dominates_block_but_not_memory_value(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %71 %4","OpBranch %52",
            "%52 = OpLabel",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_prior_store_CFG_dominates"],1)
        self.assertFalse(d["SPV_OpIMul_input_writer_CFG_block_dominance_proves_alias_freedom"])

    def test_cfg_diamond_writer_arm_not_dominating_join(self):
        d=self.make([
            "OpBranchConditional %cond %52 %53",
            "%52 = OpLabel",
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %71 %4","OpBranch %54",
            "%53 = OpLabel","OpBranch %54",
            "%54 = OpLabel",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_prior_store_CFG_not_dominates"],1)

    def test_unknown_pointer_store_invalidates_before_input_load(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %71 %4","OpStore %unknown %4",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_no_prior_matching_store_observed"],1)

    def test_volatile_input_load_is_untrusted(self):
        d=self.make([
            "%71 = OpInBoundsAccessChain %ptr %5 %3",
            "OpStore %71 %4",
            "%72 = OpInBoundsAccessChain %ptr %5 %3",
            "%66 = OpLoad %1 %72 Volatile"
        ])
        self.assertEqual(d["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_unresolved_read_snapshot"],1)
        self.assertFalse(d["originalShaderRestored"])

if __name__=="__main__":
    unittest.main()
