"""Synthetic tests only, not raw DXBC material/shader property content."""
import unittest
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import (
    private_signature,safe_histogram,summarize_pass_variants
)

def fake(pairs,unknown=0):
    return {"pairs":pairs,
       "stat":{"source_sample_or_gather_operations":len(pairs)+unknown,
               "source_distinct_pairs_within_stage":len(set(pairs)),
               "source_original_unresolved_dynamic_t_s":unknown,
               "original_sample_ops":len(pairs)+unknown,
               "original_gather_ops":0}}

class TestGFX048OriginalVariantCensus(unittest.TestCase):
    def test_pair_multiplicity_and_order_canonical(self):
        self.assertEqual(private_signature([(1,2),(3,4),(1,2)]),
                         private_signature([(3,4),(1,2),(1,2)]))
        self.assertNotEqual(private_signature([(1,2),(3,4)]),
                            private_signature([(1,2),(1,2)]))

    def test_counts_do_not_reveal_original_pairs(self):
        one={"vertex":fake([]),"fragment":fake([(2,3),(2,3)])}
        two={"vertex":fake([]),"fragment":fake([(4,1),(4,1)])}
        three={"vertex":fake([]),"fragment":fake([(2,3),(1,3)],1)}
        report=summarize_pass_variants([one,two,three])
        self.assertEqual(report["exact_original_matched_variant_pairs"],3)
        self.assertEqual(report["fragment_private_unique_t_s_pair_multiset_signature_classes"],3)
        self.assertEqual(report["fragment_sample_instruction_count_histogram"],{"2":2,"3":1})
        self.assertEqual(report["fragment_dynamic_unresolved_count_histogram"],{"0":2,"1":1})
        self.assertFalse(report["all_variant_register_values_and_pair_fingerprints_exported"])
        self.assertNotIn("2,3",str(report))
        self.assertFalse(report["all_variant_PC_or_Android_GPU_parity_verified"])

    def test_identical_sample_counts_can_hide_different_register_signatures(self):
        a={"vertex":fake([]),"fragment":fake([(0,1),(0,2)])}
        b={"vertex":fake([]),"fragment":fake([(4,4),(4,5)])}
        s=summarize_pass_variants([a,b])
        self.assertEqual(s["fragment_sample_instruction_count_histogram"],{"2":2})
        self.assertEqual(s["fragment_private_unique_t_s_pair_multiset_signature_classes"],2)

    def test_sample_gather_and_unknown_preserved(self):
        s=summarize_pass_variants([{"vertex":fake([]),"fragment":fake([(2,3)],1)}])
        self.assertEqual(s["fragment_variants_with_unresolved_dynamic_source_indices"],1)

    def test_reject_corrupt_stat(self):
        f=fake([(1,2)])
        f["stat"]["source_sample_or_gather_operations"]=4
        with self.assertRaisesRegex(ValueError,"INCONSISTENT"):
            summarize_pass_variants([{"vertex":fake([]),"fragment":f}])

    def test_bounds_negative_guards(self):
        with self.assertRaisesRegex(ValueError,"BAD_VARIANT_HISTOGRAM"):
            safe_histogram([0]*2001)
        with self.assertRaisesRegex(ValueError,"BAD_VALUE"):
            safe_histogram([True])
        with self.assertRaisesRegex(ValueError,"INVALID"):
            private_signature([(1,-1)])
        with self.assertRaisesRegex(ValueError,"PAIR_ROWS_INVALID"):
            summarize_pass_variants([])
if __name__=="__main__":unittest.main()
