"""GFX061 source-free synthetic original source six-batch no-overlap and privacy guards."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_batch061 import select_pass_scoped_joint_classes as select

def rows(n=22):
    return [{"subshader":0 if i<4 else 1,"pass":i if i<4 else i-4,
             "pairs":[("V%d_%d"%(i,j),"F%d_%d"%(i,j)) for j in range(n)]}
             for i in range(7)]

def inspect(name,kind):
    return {"decl":(name+"-decl",),"sampling":(name+"-sample-use",),"unresolved":0}

def keys(items):
    return {(r["subshader"],r["pass"],v,f) for r,v,f in items}

class TestGFX061SixthBatch(unittest.TestCase):
    def test_six_independent_slices_nonoverlap_and_source_private_counters(self):
        checks=[select(rows(),inspect,start=i) for i in (0,24,48,72,96,120)]
        sets=[keys(c[0]) for c in checks]
        self.assertEqual([len(s) for s in sets],[24]*6)
        self.assertEqual(len(set.union(*sets)),144)
        for i in range(6):
            for j in range(i+1,6):
                self.assertFalse(sets[i]&sets[j])
        result=checks[-1][1]
        self.assertEqual(result["batch_start_index"],120)
        self.assertEqual(result["batch_end_index_exclusive"],144)
        self.assertEqual(result["previous_120_source_class_proof_run"],42865341763)
        self.assertTrue(result["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertFalse(result["private_declaration_samples_keywords_or_variant_IDs_exported"])
        self.assertFalse(result["untested_classes_CPU_SPIRV_parity_confirmed"])

    def test_119_does_not_claim_proven_first120(self):
        before=select(rows(),inspect,start=119,budget=3)[1]
        actual=select(rows(),inspect,start=120,budget=3)[1]
        self.assertFalse(before["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertIsNone(before["previous_120_source_class_proof_run"])
        self.assertTrue(actual["batch_selection_disjoint_from_previous_proven_prefix"])

    def test_deterministic_order_only_aggregate_not_original_identifiers(self):
        a=select(rows(),inspect,start=120)
        b=select(rows(),inspect,start=120)
        self.assertEqual(a,b)
        self.assertEqual(a[1]["original_exact_pairs_scanned"],154)
        self.assertEqual(a[1]["pass_scoped_joint_declaration_and_sample_use_classes"],154)
        self.assertEqual(a[1]["joint_classes_untranslated_in_first_batch"],10)
        self.assertNotIn("V0_0",str(a[1])+str(a[2]))

    def test_tail_selected_without_wrapping_and_bounds_reject(self):
        chosen,state,_=select(rows(),inspect,start=144)
        self.assertEqual(len(chosen),10)
        self.assertEqual(state["batch_end_index_exclusive"],154)
        self.assertEqual(state["joint_classes_untranslated_in_first_batch"],0)
        for n in (154,155,1000):
            with self.assertRaisesRegex(ValueError,"BATCH_START_OUT_OF_RANGE"):
                select(rows(),inspect,start=n)

    def test_corrupt_inspector_or_invalid_budget_fails_closed(self):
        for n in (-1,True,1.5):
            with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
                select(rows(),inspect,start=n)
        with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
            select(rows(),inspect,budget=25)
        with self.assertRaisesRegex(ValueError,"PASS_PAIR_ROWS"):
            select(rows(0),inspect)
        with self.assertRaisesRegex(ValueError,"PRIVATE_SOURCE_INSPECTOR_SHAPE"):
            select(rows(1),lambda m,s:{"decl":(),"sampling":(),"unresolved":True})

if __name__=="__main__":unittest.main()
