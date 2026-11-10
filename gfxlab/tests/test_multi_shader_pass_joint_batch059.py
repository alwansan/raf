"""GFX059 synthetic privacy, stable source order and four disjoint batch guards."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_batch059 import select_pass_scoped_joint_classes as select

def rows(n=18):
    return [{"subshader":0 if i<4 else 1,"pass":i if i<4 else i-4,
      "pairs":[("V%d_%d"%(i,j),"F%d_%d"%(i,j)) for j in range(n)]} for i in range(7)]
def source(m,k):
    return {"decl":(m+"decl",),"sampling":(m+"sample",),"unresolved":0}
def keys(rows):
    return {(p["subshader"],p["pass"],v,f) for p,v,f in rows}

class GFX059BatchTests(unittest.TestCase):
    def test_four_bounded_batch_sets_nonoverlapping(self):
        data=[select(rows(),source,start=k) for k in (0,24,48,72)]
        seq=[keys(a) for a,_,_ in data]
        self.assertEqual([len(x) for x in seq],[24]*4)
        self.assertEqual(len(seq[0]|seq[1]|seq[2]|seq[3]),96)
        for i in range(4):
            for j in range(i+1,4):
                self.assertFalse(seq[i]&seq[j])
        self.assertEqual(data[3][1]["batch_start_index"],72)
        self.assertEqual(data[3][1]["batch_end_index_exclusive"],96)
        self.assertEqual(data[3][1]["previous_72_source_class_proof_run"],42861618032)
        self.assertTrue(data[3][1]["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertFalse(data[3][1]["private_declaration_samples_keywords_or_variant_IDs_exported"])

    def test_source_71_is_not_proven_prefix_72(self):
        a=select(rows(),source,start=71,budget=5)[1]
        b=select(rows(),source,start=72,budget=5)[1]
        self.assertFalse(a["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertIsNone(a["previous_72_source_class_proof_run"])
        self.assertTrue(b["batch_selection_disjoint_from_previous_proven_prefix"])

    def test_stable_reselection_census_and_no_identifiers_in_safe_counts(self):
        x=select(rows(),source,start=72)
        y=select(rows(),source,start=72)
        self.assertEqual(x,y)
        self.assertEqual(x[1]["original_exact_pairs_scanned"],126)
        self.assertEqual(x[1]["pass_scoped_joint_declaration_and_sample_use_classes"],126)
        self.assertEqual(x[1]["joint_classes_untranslated_in_first_batch"],30)
        self.assertNotIn("V0_0",str(x[1])+str(x[2]))
        self.assertFalse(x[1]["untested_classes_CPU_SPIRV_parity_confirmed"])

    def test_partial_tail_and_bounds_fail_closed(self):
        a,s,_=select(rows(),source,start=120)
        self.assertEqual(len(a),6)
        self.assertEqual(s["batch_end_index_exclusive"],126)
        for n in (126,127):
            with self.assertRaisesRegex(ValueError,"BATCH_START_OUT_OF_RANGE"):
                select(rows(),source,start=n)
        for n in (-1,True,1.5):
            with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
                select(rows(),source,start=n)
        with self.assertRaisesRegex(ValueError,"PASS_PAIR_ROWS"):
            select(rows(0),source)
        with self.assertRaisesRegex(ValueError,"PRIVATE_SOURCE_INSPECTOR_SHAPE"):
            select(rows(1),lambda m,k:{"decl":(),"sampling":(),"unresolved":True})
if __name__=="__main__":unittest.main()
