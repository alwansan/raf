"""GFX-MULTI-049 purely synthetic 58-profile source selector guards."""
import unittest
from gfxlab.tools.multi_shader_representative_spirv_profiles import (
    select_private_sample_profiles, safe_failure_code
)

def stage(name, pairs):
    return {"name":name,"synthetic_pairs":pairs}

def make_seven(records):
    return [{"subshader":0 if i<4 else 1, "pass":i if i<4 else i-4,
             "pairs": x} for i,x in enumerate(records)]

def fake_inspector(meta,kind):
    return {"pairs":meta["synthetic_pairs"]}

class TestRepresentativeProfileSelection(unittest.TestCase):
    def test_globally_unique_signature_across_all_passes(self):
        a=(stage("V0",[]), stage("F0",[(2,3)]))
        b=(stage("V1",[]), stage("F1",[(2,3)]))
        c=(stage("V2",[]), stage("F2",[(2,3),(2,3)]))
        # Source-only synthetic fixtures with 524 pairs, zero private source.
        passes=make_seven([[a]*70,[b]*100,[c]*100,[a]*80,[c]*60,[b]*60,[a]*54])
        self.assertEqual(sum(len(p["pairs"]) for p in passes),524)
        selections,by_pass,checked,unique=select_private_sample_profiles(passes,fake_inspector)
        self.assertEqual(checked,524)
        self.assertEqual(unique,2)
        self.assertEqual(len(selections),2)
        self.assertEqual(sum(x["new_global_sampling_profile_representatives_selected"] for x in by_pass),2)
        self.assertEqual(by_pass[0]["new_global_sampling_profile_representatives_selected"],1)
        self.assertEqual(by_pass[2]["new_global_sampling_profile_representatives_selected"],1)

    def test_order_is_private_but_multiset_class_must_preserve_multiplicity(self):
        a=(stage("V",[]),stage("F",[(1,2),(1,2),(3,4)]))
        b=(stage("V",[]),stage("F",[(3,4),(1,2),(1,2)]))
        c=(stage("V",[]),stage("F",[(1,2),(3,4)]))
        passes=make_seven([[a,b,c]+[a]*77,[a]*80,[b]*70,[c]*74,[a]*80,[b]*80,[c]*60])
        self.assertEqual(sum(len(p["pairs"]) for p in passes),524)
        chosen,_,_,classes=select_private_sample_profiles(passes,fake_inspector)
        self.assertEqual(classes,2)
        self.assertEqual(len(chosen),2)

    def test_wrong_source_total_fails_closed(self):
        p=make_seven([[("v","f")]]*7)
        def inspector(v,k):return {"pairs":[]}
        with self.assertRaisesRegex(ValueError,"524_PAIR_COUNT_DRIFT"):
            select_private_sample_profiles(p,inspector)

    def test_bounded_signature_classes_not_silently_truncated(self):
        perpass=[[] for _ in range(7)]
        for n in range(524):
            perpass[n%7].append((stage("v",[]),stage("f",[(n,0)])))
        passes=make_seven(perpass)
        with self.assertRaisesRegex(ValueError,"PROFILE_LIMIT_EXCEEDED"):
            select_private_sample_profiles(passes,fake_inspector,limit=10)

    def test_malformed_source_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_PASS_INPUT"):
            select_private_sample_profiles([],fake_inspector)
        p=make_seven([[None]]*7)
        with self.assertRaisesRegex(ValueError,"INVALID_EXACT_PAIR"):
            select_private_sample_profiles(p,fake_inspector)

    def test_selection_contains_private_metadata_not_exported_in_public_counts(self):
        a=(stage("v",[]),stage("f",[(3,4)]))
        p=make_seven([[a]*80,[a]*156,[a]*32,[a]*80,[a]*40,[a]*120,[a]*16])
        selected,summary,n,k=select_private_sample_profiles(p,fake_inspector)
        self.assertEqual((n,k),(524,1))
        self.assertEqual(len(selected),1)
        self.assertEqual(summary[0]["exact_source_variant_pairs_examined"],80)
        self.assertNotIn("synthetic_pairs",str(summary))
        self.assertNotIn("F",str(summary))

    def test_safe_failure_category_exact_allowlist_only(self):
        self.assertEqual(safe_failure_code(ValueError("GFX046_INCOMPLETE_AUTHENTIC_REGISTER_COVERAGE")),
                         "GFX046_INCOMPLETE_AUTHENTIC_REGISTER_COVERAGE")
        self.assertEqual(safe_failure_code(ValueError("GFX046_SOME_PRIVATE_NAME")), "UNCLASSIFIED_FAIL_CLOSED")
        self.assertEqual(safe_failure_code(ValueError("GFX046_REFLECTION_SYMBOL_OUTSIDE_SOURCE t6")), "UNCLASSIFIED_FAIL_CLOSED")
        self.assertEqual(safe_failure_code(KeyError("GFX046_REFLECTION_SYMBOL_OUTSIDE_SOURCE")), "UNCLASSIFIED_FAIL_CLOSED")

if __name__=="__main__":unittest.main()
