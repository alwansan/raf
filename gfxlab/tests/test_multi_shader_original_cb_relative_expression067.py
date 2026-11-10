"""Synthetic-only fail-closed GFX067 DXBC nested relative CB grammar tests."""
import unittest,struct
from gfxlab.tools.multi_shader_original_cb_relative_expression067 import (
    signed32,signed64,decode_original_operand_tree,
    source_relative_CB_index_AST_census,
    source_to_spv_relative_expression_acceptance
)
from gfxlab.tests.test_multi_shader_original_dynamic_cb_taxonomy import arg,mov,shdr

def census(ops,cb=None):
    return source_relative_CB_index_AST_census(shdr(ops),{2:8} if cb is None else cb)

class TestGFX067RelativeOriginalCBNestedAST(unittest.TestCase):
    def test_all_three_relative_vec4_index_encodings_are_preserved(self):
        c=census([mov(arg(8,(2,0),(0,2))),mov(arg(8,(2,3),(0,3))),
                  mov(arg(8,(2,0),(0,4)))])
        self.assertEqual(c["relative_original_CB_vec4_operand_occurrences"],3)
        self.assertEqual(c["relative_representation_2"],1)
        self.assertEqual(c["relative_representation_3"],1)
        self.assertEqual(c["relative_representation_4"],1)
        self.assertEqual(c["relative_base_positive"],1)
        self.assertEqual(c["relative_base_zero"],2)
        self.assertEqual(c["relative_nested_temporary"],3)

    def test_signed_relative_base_is_not_silently_treated_unsigned(self):
        self.assertEqual(signed32(0xffffffff),-1)
        self.assertEqual(signed64(0xffffffff,0xffffffff),-1)
        self.assertEqual(signed32(3),3)
        c=census([mov(arg(8,(2,0xfffffffd),(0,3)))])
        self.assertEqual(c["relative_base_negative"],1)

    def test_two_relative_uses_same_private_expression_not_one_occurrence(self):
        op=mov(arg(8,(2,1),(0,3)))
        c=census([op,op])
        self.assertEqual(c["relative_original_CB_vec4_operand_occurrences"],2)
        self.assertEqual(c["relative_private_distinct_expression_keys_within_this_stage"],1)

    def test_static_extended_is_not_relative(self):
        c=census([mov(arg(8,(2,5),(0,0),mod=True)),
                  mov(arg(8,(2,2),(0,0)))])
        self.assertEqual(c.get("relative_original_CB_vec4_operand_occurrences",0),0)
        self.assertEqual(c["static_CB_operand_occurrences"],2)
        self.assertEqual(c["covered_CB_operand_occurrences"],2)

    def test_dynamic_CB_register_not_reclassified_as_relative_vec_index(self):
        c=census([mov(arg(8,(2,2),(2,0)))])
        self.assertEqual(c["dynamic_original_b_register_index_unresolved"],1)
        self.assertEqual(c.get("relative_original_CB_vec4_operand_occurrences",0),0)

    def test_invalid_or_undeclared_CB_register_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"REGISTER_NOT_DECLARED"):
            census([mov(arg(8,(3,1),(0,2)))])
        with self.assertRaisesRegex(ValueError,"OUTSIDE_ORIGINAL_CB"):
            census([mov(arg(8,(2,8),(0,0)))])

    def test_truncated_or_overlong_DXBC_rejected(self):
        data=shdr([mov(arg(8,(2,4),(0,3)))])
        with self.assertRaises(ValueError):
            source_relative_CB_index_AST_census(data[:-4],{2:8})
        values=list(struct.unpack("<%dI"%(len(data)//4),data))
        values[2]=(127<<24)|54
        with self.assertRaisesRegex(ValueError,"BOUNDS"):
            source_relative_CB_index_AST_census(struct.pack("<%dI"%len(values),*values),{2:8})

    def test_original_operand_nested_decoder_requires_complete_relative(self):
        words=arg(8,(2,5),(0,3))
        node,pos=decode_original_operand_tree(words,0,len(words))
        self.assertEqual(pos,len(words))
        self.assertEqual(node["type"],8)
        self.assertEqual(node["indices"][1][0],"relative")
        self.assertEqual(node["indices"][1][2],5)
        self.assertEqual(node["indices"][1][3]["type"],0)
        with self.assertRaisesRegex(ValueError,"RELATIVE_OPERAND_TREE_BOUNDS|TRUNCATED|BOUNDS"):
            decode_original_operand_tree(words[:-1],0,len(words)-1)

    def test_original_nested_relative_ast_does_not_claim_translation(self):
        denied=source_to_spv_relative_expression_acceptance(
            {"relative_offset":2},{"SPV_numerically_equal_offset":2})
        self.assertEqual(denied["verdict"],"BLOCKED_NO_INDEPENDENT_DXBC_TO_SPV_SSA_ROOT")
        self.assertFalse(denied["per_source_operand_expression_parity_proven"])
        self.assertFalse(denied["source_relative_index_runtime_bounds_proven"])
        with self.assertRaisesRegex(ValueError,"NO_AUTHENTICATED_SSA_IDENTITY"):
            source_to_spv_relative_expression_acceptance({}, {}, {"fake_origin_match":True})

    def test_other_opcode_family_does_not_count_as_zero_cb_proof(self):
        c=census([[(2<<24)|210,0]])
        self.assertEqual(c["outside_nine_supported_arithmetic_opcodes"],1)
        self.assertEqual(c.get("covered_CB_operand_occurrences",0),0)

if __name__=="__main__":unittest.main()
