"""Pure synthetic GFX057 original-class-selection negative controls."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_batch057 import select_pass_scoped_joint_classes

def passes(first):
    x=[]
    for k in range(7):
        x.append({"subshader":0 if k<4 else 1,"pass":k if k<4 else k-4,
                  "pairs":[("A"+str(k),"B"+str(k))]})
    x[0]["pairs"]=first
    return x

def inspector(meta,stage):
    cases={
      "A0":(("d0",),("s0",)),"B0":(("d1",),("s1",)),
      "Ax":(("d0",),("sx",)),"Bx":(("d1",),("s1",)),
      "Ay":(("dy",),("s0",)),"By":(("d1",),("s1",)),
    }
    d,s=cases.get(meta,((meta+"d",),(meta+"s",)))
    return {"decl":d,"sampling":s,"unresolved":0}

class TestGFX057SourceFree(unittest.TestCase):
    def test_independent_decl_and_sampling_classes(self):
        x=passes([("A0","B0"),("Ax","Bx"),("Ay","By"),("A0","B0")])
        chosen,stats,per=select_pass_scoped_joint_classes(x,inspector)
        self.assertEqual(stats["original_exact_pairs_scanned"],10)
        self.assertEqual(stats["pass_scoped_declaration_classes"],8)
        self.assertEqual(stats["pass_scoped_joint_declaration_and_sample_use_classes"],9)
        self.assertEqual(per[0]["declaration_classes"],2)
        self.assertEqual(per[0]["sampling_signature_classes"],2)
        self.assertEqual(per[0]["joint_declaration_sampling_classes"],3)
        self.assertEqual(len(chosen),9)
        self.assertFalse(stats["untested_classes_CPU_SPIRV_parity_confirmed"])
    def test_balanced_round_robin_seven_passes(self):
        x=passes([("A0","B0"),("Ax","Bx"),("Ay","By")])
        _,s,rows=select_pass_scoped_joint_classes(x,inspector,budget=7)
        self.assertEqual(s["first_CPU_batch_representative_pairs"],7)
        self.assertEqual([row["first_CPU_batch_representative_pairs"] for row in rows],[1]*7)
        self.assertEqual(s["joint_classes_untranslated_in_first_batch"],2)
    def test_repeated_variant_not_new_joint_class(self):
        x=passes([("A0","B0"),("A0","B0")])
        _,s,_=select_pass_scoped_joint_classes(x,inspector)
        self.assertEqual(s["pass_scoped_joint_declaration_and_sample_use_classes"],7)
    def test_no_raw_source_meta_in_aggregate(self):
        _,stats,rows=select_pass_scoped_joint_classes(passes([("A0","B0")]),inspector)
        self.assertNotIn("A0",str(stats)+str(rows))
        self.assertNotIn("B0",str(stats)+str(rows))
        self.assertFalse(stats["private_declaration_samples_keywords_or_variant_IDs_exported"])
    def test_zero_budget_and_no_pass_pairs_rejected(self):
        with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
            select_pass_scoped_joint_classes(passes([("A0","B0")]),inspector,0)
        with self.assertRaisesRegex(ValueError,"PAIR_ROWS"):
            select_pass_scoped_joint_classes(passes([]),inspector)
    def test_invalid_private_inspector_rejected(self):
        with self.assertRaisesRegex(ValueError,"INSPECTOR_SHAPE"):
            select_pass_scoped_joint_classes(passes([("A0","B0")]),
                 lambda a,b:{"decl":None,"sampling":(),"unresolved":0})

class TestGFX057BatchSlicing(unittest.TestCase):
    @staticmethod
    def generated_source_free_classes():
        rows=[]
        for k in range(7):
            rows.append({"subshader":0 if k<4 else 1,
                         "pass":k if k<4 else k-4,
                         "pairs":[("V"+str(k)+"_"+str(i),"F"+str(k)+"_"+str(i))
                                  for i in range(10)]})
        return rows

    def test_exact_nonoverlap_across_three_bounded_batches(self):
        rows=self.generated_source_free_classes()
        one,a,_=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=0)
        two,b,_=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=24)
        last,c,_=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=48)
        identity=lambda seq:{(x[0]["subshader"],x[0]["pass"],x[1],x[2]) for x in seq}
        self.assertEqual([len(one),len(two),len(last)],[24,24,22])
        self.assertFalse(identity(one)&identity(two))
        self.assertFalse(identity(two)&identity(last))
        self.assertFalse(identity(one)&identity(last))
        self.assertEqual(len(identity(one)|identity(two)|identity(last)),70)
        self.assertEqual(b["batch_start_index"],24)
        self.assertEqual(b["batch_end_index_exclusive"],48)
        self.assertEqual(b["joint_classes_untranslated_in_first_batch"],22)
        self.assertTrue(b["batch_selection_disjoint_from_previous_proven_prefix"])
        self.assertEqual(b["previous_first24_source_class_proof_run"],42857815446)
        self.assertEqual([x["batch_start_index"] for x in (a,b,c)],[0,24,48])

    def test_order_is_stable_when_restarted_with_same_source(self):
        rows=self.generated_source_free_classes()
        a,s,_=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=24)
        b,t,_=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=24)
        self.assertEqual(a,b)
        self.assertEqual(s,t)
        self.assertNotIn("V0_0",str(s))
        self.assertNotIn("F0_0",str(s))

    def test_invalid_or_exhausted_offset_never_wraps_to_first_batch(self):
        rows=self.generated_source_free_classes()
        for start in (-1, True, 1.5):
            with self.assertRaisesRegex(ValueError,"PASS_OR_BUDGET"):
                select_pass_scoped_joint_classes(rows,inspector,budget=24,start=start)
        for start in (70,71,1000):
            with self.assertRaisesRegex(ValueError,"BATCH_START_OUT_OF_RANGE"):
                select_pass_scoped_joint_classes(rows,inspector,budget=24,start=start)

    def test_second_batch_is_not_accidentally_first_batch(self):
        rows=self.generated_source_free_classes()
        a,_,pa=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=0)
        b,stats,pb=select_pass_scoped_joint_classes(rows,inspector,budget=24,start=24)
        self.assertNotEqual([(x[1],x[2]) for x in a],[(x[1],x[2]) for x in b])
        self.assertEqual(sum(r["first_CPU_batch_representative_pairs"] for r in pb),24)
        self.assertEqual(stats["original_exact_pairs_scanned"],70)
        self.assertFalse(stats["untested_classes_CPU_SPIRV_parity_confirmed"])

if __name__=="__main__":unittest.main()
