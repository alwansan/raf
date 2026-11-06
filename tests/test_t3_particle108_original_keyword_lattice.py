"""Source-free strict SHA-original Shader48 keyword permutation lattice tests."""
import json
import unittest

from scripts import t3_particle108_original_keyword_lattice as k


def meta(keys=(), global_keys=(), local_keys=(),tier=0):
    return {"m_ShaderHardwareTier":tier,
            "m_KeywordIndices":list(keys),
            "m_GlobalKeywordIndices":list(global_keys),
            "m_LocalKeywordIndices":list(local_keys)}


def program(rows,player=False):
    return {"m_SubPrograms":[] if player else rows,
            "m_PlayerSubPrograms":[rows] if player else []}


def pass_record(rows,fragments=None,player=False):
    return {"m_Type":0,
            "progVertex":program(rows,player),
            "progFragment":program(list(reversed(rows)) if fragments is None else fragments,player)}


class OriginalKeywordLatticeTests(unittest.TestCase):
    def test_two_independent_source_index_toggles(self):
        p=pass_record([meta(),meta([1]),meta([2]),meta([1,2])])
        r=k.classify(p)
        self.assertTrue(r["source_original_exact_independent_two_toggle_index_lattice"])
        self.assertTrue(r["source_original_VSFS_serialized_variant_keys_exact"])
        self.assertEqual(r["source_original_distinct_bucket_tier_groups"],1)
        self.assertEqual(r["source_original_keyword_variable_index_dimension_count"],2)
        self.assertFalse(r["all_four_variants_selectable_in_one_Unity_ShaderLab_proven"])

    def test_shared_fixed_keywords_not_mistaken_as_toggles(self):
        p=pass_record([meta([99]),meta([99,1]),meta([99,2]),meta([99,1,2])])
        r=k.classify(p)
        self.assertTrue(r["source_original_exact_independent_two_toggle_index_lattice"])
        self.assertEqual(r["source_original_keyword_baseline_intersection_count"],1)

    def test_global_local_index_namespaces_distinct_even_same_numeric_index(self):
        p=pass_record([meta(),meta(global_keys=[4]),meta(local_keys=[4]),
                       meta(global_keys=[4],local_keys=[4])])
        self.assertTrue(k.classify(p)["source_original_exact_independent_two_toggle_index_lattice"])

    def test_four_unrelated_singletons_not_two_toggles(self):
        p=pass_record([meta([1]),meta([2]),meta([3]),meta([4])])
        r=k.classify(p)
        self.assertFalse(r["source_original_exact_independent_two_toggle_index_lattice"])
        self.assertEqual(r["source_original_keyword_variable_index_dimension_count"],4)

    def test_cross_tier_four_variants_no_keyword_only_routing_claim(self):
        rows=[meta([],tier=0),meta([1],tier=0),meta([2],tier=1),meta([1,2],tier=1)]
        r=k.classify(pass_record(rows))
        self.assertEqual(r["source_original_distinct_bucket_tier_groups"],2)
        self.assertFalse(r["source_original_exact_independent_two_toggle_index_lattice"])

    def test_stage_permutation_mismatch_refused_not_counted(self):
        with self.assertRaisesRegex(ValueError,"mismatch"):
            k.classify(pass_record([meta(),meta([1]),meta([2]),meta([1,2])],
                    [meta(),meta([1]),meta([2]),meta([9])]))

    def test_duplicate_variant_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            k.classify(pass_record([meta(),meta([1]),meta([1]),meta([1,2])]))

    def test_wrong_or_missing_stage_fail_closed(self):
        p=pass_record([meta(),meta([1]),meta([2]),meta([1,2])])
        del p["progFragment"]
        with self.assertRaises(ValueError):
            k.classify(p)

    def test_invalid_bool_or_negative_index_refused(self):
        for bad in (True,-1,1.5,"7",65536):
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"indices"):
                p=pass_record([meta(),meta([1]),meta([2]),meta([1,2])])
                p["progVertex"]["m_SubPrograms"][0]["m_KeywordIndices"]=[bad]
                k.classify(p)

    def test_duplicate_index_in_one_program_refused(self):
        p=pass_record([meta(),meta([1]),meta([2]),meta([1,2])])
        p["progVertex"]["m_SubPrograms"][1]["m_KeywordIndices"]=[1,1]
        with self.assertRaisesRegex(ValueError,"indices"):k.classify(p)

    def test_wrong_player_or_hardware_stage_bucket_refused(self):
        v=[meta(),meta([1]),meta([2]),meta([1,2])]
        p=pass_record(v)
        p["progFragment"]=program(v,player=True)
        with self.assertRaisesRegex(ValueError,"mismatch"):k.classify(p)

    def test_player_bucket_synthetically_preserved(self):
        v=[meta(),meta([1]),meta([2]),meta([1,2])]
        r=k.classify(pass_record(v,player=True))
        self.assertTrue(r["source_original_exact_independent_two_toggle_index_lattice"])

    def test_missing_or_boolean_tier_rejected(self):
        p=pass_record([meta(),meta([1]),meta([2]),meta([1,2])])
        p["progVertex"]["m_SubPrograms"][0]["m_ShaderHardwareTier"]=True
        with self.assertRaisesRegex(ValueError,"tier"):k.classify(p)

    def test_aggregate_report_does_not_leak_source_keyword_literals(self):
        p=pass_record([meta([417]),meta([417,422]),meta([417,428]),meta([417,422,428])])
        report=k.classify(p)
        out=json.dumps(report)
        for forbidden in ("417","422","428","Shader48_original_secret","private-original-index-417"):
            self.assertNotIn(forbidden,out)
        self.assertFalse(report["source_keyword_names_indices_bytes_guids_or_paths_published"])


if __name__=="__main__":
    unittest.main()
