"""GFX073 synthetic-only private source-b/offset vs SPV OpLoad multiset controls."""
import unittest
from gfxlab.tools.multi_shader_original_cb_index_b_offset073 import (
    original_source_private_b_relative_offset_multiset,
    translated_spv_private_authenticated_b_relative_offset_multiset,
    compare_private_b_and_relative_literal_multisets,
)
from gfxlab.tests.test_multi_shader_original_cb_temp_writer068 import (
    temp,cb_relative,moving
)
from gfxlab.tests.test_multi_shader_original_dynamic_cb_taxonomy import shdr
from gfxlab.tests.test_multi_shader_spv_shifted_cb_index070 import spv

def original(ops):
    return original_source_private_b_relative_offset_multiset(shdr(ops),{2:8})

def translated(lines,b=2):
    return translated_spv_private_authenticated_b_relative_offset_multiset(spv(lines),{"%10":(b,0,16,8)})

def spv_direct_load():
    return ["%7 = OpBitcast %1 %6",
            "%20 = OpAccessChain %ptr %10 %2 %7",
            "%30 = OpLoad %vec4 %20"]

def spv_plus_load(shift_const="%4"):
    return ["%7 = OpBitcast %1 %6",
            f"%9 = OpIAdd %1 %7 {shift_const}",
            "%20 = OpAccessChain %ptr %10 %2 %9",
            "%30 = OpLoad %vec4 %20"]

def cb_direct(b=2,reg=5):
    return [(8<<12)|(2<<20)|2|(2<<25),b]+temp(reg,0)

class TestGFX073OriginalShaderSourceBOffsetPrivateMultiset(unittest.TestCase):
    def test_direct_original_source_b_matches_real_spv_UBO_root(self):
        src,sc=original([moving(temp(0,0,True),cb_direct())])
        sp,counts=translated(spv_direct_load())
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertEqual((sc["source_relative_CB_index_keys_classified"],counts[
            "SPV_dynamic_UBO_index_b_and_offset_keys_classified"]),(1,1))
        self.assertTrue(d["private_stage_b_offset_shape_multiset_equal"])
        self.assertFalse(d["original_temp_component_to_translated_SPV_index_value_proven"])
        self.assertFalse(d["original_source_CB_relative_operand_to_SPV_instruction_bijection_proven"])

    def test_immediate_source_positive_offset_matches_SPV_literal_iadd(self):
        src,_=original([moving(temp(0,0,True),cb_relative(5,0,base=3,b=2))])
        sp,_=translated(spv_plus_load())
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertEqual(d["private_source_b_offset_shape_multiset_occurrences_matched"],1)
        self.assertTrue(d["private_stage_b_offset_shape_multiset_equal"])

    def test_wrong_original_CB_b_identity_never_matched(self):
        src,_=original([moving(temp(0,0,True),cb_relative(5,0,base=3,b=2))])
        sp,_=translated(spv_plus_load(),b=3)
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertEqual(d["private_source_b_offset_shape_multiset_occurrences_matched"],0)
        self.assertEqual(d["private_source_b_offset_shape_occurrences_missing_in_SPV"],1)
        self.assertEqual(d["private_translated_SPV_b_offset_shape_occurrences_without_source"],1)

    def test_different_literal_offset_fails_even_if_same_stage_shape_counts(self):
        src,_=original([moving(temp(0,0,True),cb_relative(5,0,base=3,b=2))])
        sp,_=translated(spv_plus_load("%3")) # %3 is source-free synthetic literal 2
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertFalse(d["private_stage_b_offset_shape_multiset_equal"])
        self.assertEqual(d["private_source_b_offset_shape_occurrences_missing_in_SPV"],1)

    def test_duplicate_operand_uses_are_multiset_not_set(self):
        src,_=original([moving(temp(0,0,True),cb_direct()),moving(temp(1,0,True),cb_direct())])
        lines=["%7 = OpBitcast %1 %6","%20 = OpAccessChain %ptr %10 %2 %7",
               "%30 = OpLoad %vec4 %20","%31 = OpLoad %vec4 %20"]
        sp,_=translated(lines)
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertEqual(d["private_source_b_offset_shape_multiset_occurrences_matched"],2)
        self.assertTrue(d["private_stage_b_offset_shape_multiset_equal"])

    def test_unloaded_SpV_access_chain_not_claimed_as_real_CB_read(self):
        src,_=original([moving(temp(0,0,True),cb_direct())])
        sp,_=translated(["%7 = OpBitcast %1 %6",
                         "%20 = OpAccessChain %ptr %10 %2 %7"])
        d=compare_private_b_and_relative_literal_multisets(src,sp)
        self.assertEqual(d["private_source_b_offset_shape_occurrences_missing_in_SPV"],1)

    def test_untrusted_spv_select_index_not_mapped_to_original(self):
        src,_=original([moving(temp(0,0,True),cb_direct())])
        sp,c=translated(["%7 = OpBitcast %1 %6",
                         "%9 = OpSelect %1 %cond %7 %6",
                         "%20 = OpAccessChain %ptr %10 %2 %9",
                         "%30 = OpLoad %vec4 %20"])
        self.assertEqual(c["SPV_dynamic_UBO_index_shape_unclassified"],1)
        self.assertFalse(compare_private_b_and_relative_literal_multisets(src,sp)[
            "private_stage_b_offset_shape_multiset_equal"])

    def test_original_undeclared_CB_b_fails_source_parse(self):
        with self.assertRaisesRegex(ValueError,"CB_B_NOT_AUTHENTIC"):
            original([moving(temp(0,0,True),cb_direct(b=4))])

    def test_malformed_SPV_source_CB_authentication_fails(self):
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_B"):
            translated_spv_private_authenticated_b_relative_offset_multiset(
                spv(spv_direct_load()),{"%10":(2,4,16,8)})

if __name__=="__main__":unittest.main()
