"""Synthetic-only GFX062 157-class final tail and source privacy controls."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes as select

def cases():
    return [{"subshader":0 if i<4 else 1,"pass":i if i<4 else i-4,
             "pairs":[("synthetic-v-%d-%d"%(i,j),"synthetic-f-%d-%d"%(i,j))
                      for j in range(23 if i<3 else 22)]}
            for i in range(7)]

def inspect(name,kind):
    return {"decl":(name+"-decl",),"sampling":(name+"-sample",),"unresolved":0}

def private_keyset(rows):
    return {(r["subshader"],r["pass"],v,f) for r,v,f in rows}

class TestGFX062FinalSourceClassTail(unittest.TestCase):
    def test_seven_disjoint_source_batches_cover_exactly_157_final_classes(self):
        slices=[select(cases(),inspect,budget=24,start=i) for i in (0,24,48,72,96,120,144)]
        keys=[private_keyset(r[0]) for r in slices]
        self.assertEqual([len(s) for s in keys],[24,24,24,24,24,24,13])
        self.assertEqual(len(set.union(*keys)),157)
        for i in range(7):
            for j in range(i+1,7):
                self.assertFalse(keys[i]&keys[j])
        safe=slices[-1][1]
        self.assertEqual(safe["batch_start_index"],144)
        self.assertEqual(safe["batch_end_index_exclusive"],157)
        self.assertEqual(safe["first_CPU_batch_budget"],24)
        self.assertEqual(safe["first_CPU_batch_representative_pairs"],13)
        self.assertEqual(safe["joint_classes_untranslated_in_first_batch"],0)
        self.assertEqual(safe["previous_144_source_class_proof_run"],42866819484)
        self.assertTrue(safe["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertFalse(safe["private_declaration_samples_keywords_or_variant_IDs_exported"])
        self.assertFalse(safe["untested_classes_CPU_SPIRV_parity_confirmed"])

    def test_private_class_selection_deterministic(self):
        first=select(cases(),inspect,start=144)
        second=select(cases(),inspect,start=144)
        self.assertEqual(first,second)
        self.assertEqual(first[1]["original_exact_pairs_scanned"],157)
        self.assertEqual(first[1]["pass_scoped_joint_declaration_and_sample_use_classes"],157)
        self.assertNotIn("synthetic-v-0-0",str(first[1])+str(first[2]))

    def test_143_cannot_impersonate_144_previous_prefix_proof(self):
        before=select(cases(),inspect,start=143)[1]
        after=select(cases(),inspect,start=144)[1]
        self.assertFalse(before["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertIsNone(before["previous_144_source_class_proof_run"])
        self.assertTrue(after["batch_selection_disjoint_from_previous_proven_prefix"])

    def test_final_tail_is_bounded_never_restarts_previous_batches(self):
        for start in (155,156):
            pairs,safe,_=select(cases(),inspect,start=start)
            self.assertEqual(len(pairs),157-start)
            self.assertEqual(safe["batch_end_index_exclusive"],157)
        for start in (157,158,500):
            with self.assertRaisesRegex(ValueError,"BATCH_START_OUT_OF_RANGE"):
                select(cases(),inspect,start=start)

    def test_malformed_original_shape_and_budget_fail_closed(self):
        for value in (-1,True,1.5):
            with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
                select(cases(),inspect,start=value)
        with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
            select(cases(),inspect,budget=25)
        with self.assertRaisesRegex(ValueError,"PRIVATE_SOURCE_INSPECTOR_SHAPE"):
            select(cases(),lambda m,k:{"decl":(),"sampling":(),"unresolved":True})
        broken=cases();broken[3]["pairs"]=[]
        with self.assertRaisesRegex(ValueError,"PASS_PAIR_ROWS"):
            select(broken,inspect)
if __name__=="__main__":unittest.main()
