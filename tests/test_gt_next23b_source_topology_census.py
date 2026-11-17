"""Source-free protections for distinct remaining 23-material group identity."""
import unittest

from scripts.gt_next23b_source_topology_census import (
    STATUS,select_remaining_23_source_owners,
)


def post23_quality():
    weights=[23,6,*([5]*3),*([4]*3),*([3]*6),*([2]*3),*([1]*18)]
    assert sum(weights)==98 and len(weights)==35
    return {
        "status":"NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY",
        "counts":{
            "material_documents":1536,
            "material_docs_using_local_custom_Shader":786,
            "material_docs_using_non_dummy_Shader":688,
            "material_docs_using_dummy_Shader":98,
            "distinct_dummy_Shader_targets_referenced":37,
        },
        "dummy_shader_material_counts_by_name_digest":{
            f"{idx:064x}":weight for idx,weight in enumerate(weights)
        },
    }


class SourceOriginalNext23B(unittest.TestCase):
    def test_unique_remaining_23_digest_and_explicit_multiple_owner_candidates(self):
        q=post23_quality()
        digest=next(k for k,v in
                    q["dummy_shader_material_counts_by_name_digest"].items()
                    if v==23)
        owners={
            ("source_owner_A",12):digest,
            ("source_owner_B",34):digest,
            ("other_owner",99):f"{1:064x}",
        }
        matches=select_remaining_23_source_owners(owners,q)
        self.assertEqual(len(matches),2)
        self.assertEqual(set(matches),{
            ("source_owner_A",12),("source_owner_B",34)})
        with self.assertRaisesRegex(
                ValueError, "source_23_material_original_Shader48_owner_absent"):
            select_remaining_23_source_owners({},q)

    def test_no_source_selection_from_prior_or_forged_material_report(self):
        q=post23_quality()
        q["counts"]["material_docs_using_dummy_Shader"]=105
        with self.assertRaisesRegex(ValueError,"untrusted_original_post23"):
            select_remaining_23_source_owners({},q)

    def test_target_weight_profile_not_a_shader_guid_or_source_name(self):
        self.assertIn("TOPOLOGY", STATUS)
        self.assertNotIn("GUID_INSTALLED", STATUS)
        self.assertEqual(
            sum(post23_quality()[
                "dummy_shader_material_counts_by_name_digest"].values()),98)


if __name__=="__main__":
    unittest.main()
