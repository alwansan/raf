"""Pure synthetic GFX056 original-class-selection negative controls."""
import unittest
from gfxlab.tools.multi_shader_pass_joint_class_selection import select_pass_scoped_joint_classes

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

class TestGFX056SourceFree(unittest.TestCase):
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
if __name__=="__main__":unittest.main()
