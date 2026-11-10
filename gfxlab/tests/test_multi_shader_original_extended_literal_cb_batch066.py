"""GFX066 safe remaining-133 batch negative controls: no original Raft shader bytes."""
import unittest
from gfxlab.tools.multi_shader_original_extended_literal_cb_loads import (
    source_extended_literal_CB_ranges, compare_private_source_extended_ranges_to_SPV
)
from gfxlab.tests.test_multi_shader_original_extended_literal_cb_loads import arg, mov, dxbc

class TestGFX066ExtendedSourceRangeBatch(unittest.TestCase):
    def test_matched_source_range_only_proves_structural_read_presence(self):
        d=compare_private_source_extended_ranges_to_SPV({2:{3,4}},{2:{3,4,6}})
        self.assertEqual(d["extended_literal_source_distinct_CB_vec4_ranges"],2)
        self.assertEqual(d["extended_literal_source_distinct_ranges_with_SPV_OpLoad"],2)
        self.assertEqual(d["extended_literal_source_distinct_ranges_without_SPV_OpLoad"],0)
        self.assertFalse(d["extended_literal_range_presence_proves_per_source_operand_read_equivalence"])
        self.assertFalse(d["extended_literal_range_presence_proves_source_modifier_value_semantics"])
    def test_missing_original_vec4_read_is_not_promoted_to_success(self):
        d=compare_private_source_extended_ranges_to_SPV({2:{3,4}},{2:{3}})
        self.assertEqual(d["extended_literal_source_distinct_ranges_without_SPV_OpLoad"],1)
    def test_other_b_register_is_not_the_same_source_CB(self):
        d=compare_private_source_extended_ranges_to_SPV({2:{4}},{3:{4}})
        self.assertEqual(d["extended_literal_source_distinct_ranges_without_SPV_OpLoad"],1)
    def test_duplicate_original_operand_occurrences_are_not_distinct_ranges(self):
        ranges,c=source_extended_literal_CB_ranges(dxbc([
            mov(arg(8,(2,4),(0,0),(1,))),mov(arg(8,(2,4),(0,0),(1,)))
        ]),{2:8})
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],2)
        self.assertEqual(c["original_extended_literal_CB_distinct_b_vec4_ranges"],1)
        self.assertEqual(ranges,{2:{4}})
    def test_dynamic_index_not_claimed_by_fixed_literal_range(self):
        ranges,c=source_extended_literal_CB_ranges(dxbc([
            mov(arg(8,(2,4),(0,3),(1,)))
        ]),{2:8})
        self.assertEqual(c["original_CB_true_dynamic_index_operand_occurrences"],1)
        self.assertEqual(ranges,{2:set()})
    def test_wrong_extended_token_type_is_rejected(self):
        with self.assertRaises(ValueError):
            source_extended_literal_CB_ranges(dxbc([
                mov(arg(8,(2,4),(0,0),(5,)))
            ]),{2:8})

if __name__=="__main__":
    unittest.main()
