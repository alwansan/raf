"""Synthetic GFX060 original Shader48 fifth batch privacy, bounds and disjoint selection guards."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_batch060 import select_pass_scoped_joint_classes as select

def source_rows(n=22):
    return [{"subshader":0 if i<4 else 1,"pass":i if i<4 else i-4,
             "pairs":[("V%d_%d"%(i,j),"F%d_%d"%(i,j)) for j in range(n)]}
             for i in range(7)]

def synthetic_source(name,kind):
    return {"decl":(name+"-decl",),"sampling":(name+"-sampling",),"unresolved":0}

def identity(items):
    return {(r["subshader"],r["pass"],v,f) for r,v,f in items}

class TestGFX060FifthBatch(unittest.TestCase):
    def test_five_independent_slices_do_not_repeat_prior_class_representatives(self):
        checks=[select(source_rows(),synthetic_source,start=k) for k in (0,24,48,72,96)]
        sets=[identity(a[0]) for a in checks]
        self.assertEqual([len(s) for s in sets],[24,24,24,24,24])
        self.assertEqual(len(set.union(*sets)),120)
        for i in range(5):
            for j in range(i+1,5):
                self.assertFalse(sets[i]&sets[j])
        result=checks[-1][1]
        self.assertEqual(result["batch_start_index"],96)
        self.assertEqual(result["batch_end_index_exclusive"],120)
        self.assertEqual(result["previous_96_source_class_proof_run"],42863853554)
        self.assertTrue(result["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertFalse(result["private_declaration_samples_keywords_or_variant_IDs_exported"])
        self.assertFalse(result["untested_classes_CPU_SPIRV_parity_confirmed"])

    def test_start95_is_not_a_valid_previous96_prefix(self):
        bad=select(source_rows(),synthetic_source,start=95,budget=3)[1]
        good=select(source_rows(),synthetic_source,start=96,budget=3)[1]
        self.assertFalse(bad["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertIsNone(bad["previous_96_source_class_proof_run"])
        self.assertTrue(good["batch_selection_disjoint_from_previous_proven_prefix"])

    def test_reconstruction_is_deterministic_and_safe_report_anonymized(self):
        a=select(source_rows(),synthetic_source,start=96)
        b=select(source_rows(),synthetic_source,start=96)
        self.assertEqual(a,b)
        self.assertEqual(a[1]["original_exact_pairs_scanned"],154)
        self.assertEqual(a[1]["pass_scoped_joint_declaration_and_sample_use_classes"],154)
        self.assertEqual(a[1]["joint_classes_untranslated_in_first_batch"],34)
        self.assertNotIn("V0_0",str(a[1])+str(a[2]))

    def test_bounded_tail_is_selected_without_wrap(self):
        chosen,state,_=select(source_rows(),synthetic_source,start=144)
        self.assertEqual(len(chosen),10)
        self.assertEqual(state["batch_end_index_exclusive"],154)
        self.assertEqual(state["joint_classes_untranslated_in_first_batch"],0)
        self.assertTrue(state["batch_selection_disjoint_from_previous_proven_prefix"])

    def test_invalid_budget_offset_or_signature_rejected(self):
        for n in (-1,True,1.5):
            with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
                select(source_rows(),synthetic_source,start=n)
        for n in (154,155,1000):
            with self.assertRaisesRegex(ValueError,"BATCH_START_OUT_OF_RANGE"):
                select(source_rows(),synthetic_source,start=n)
        with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
            select(source_rows(),synthetic_source,budget=25)
        with self.assertRaisesRegex(ValueError,"PASS_PAIR_ROWS"):
            select(source_rows(0),synthetic_source)
        with self.assertRaisesRegex(ValueError,"PRIVATE_SOURCE_INSPECTOR_SHAPE"):
            select(source_rows(1),
                lambda m,s:{"decl":(),"sampling":(),"unresolved":True})

if __name__=="__main__":unittest.main()
