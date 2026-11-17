"""Fail-closed source-free tests for numeric-only post23 original Shader GUID inventory."""
import json
import unittest
from scripts.gt_remaining_original_guid_weights import (
    STATUS,safe_remaining_weights,
)


def fixture():
    names={f"{i:064x}": (33 if i==0 else 30 if i==1 else 1)
           for i in range(37)}
    return {
        "status":"NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY",
        "counts":{
            "material_documents":1536,
            "material_docs_using_local_custom_Shader":786,
            "material_docs_using_non_dummy_Shader":688,
            "material_docs_using_dummy_Shader":98,
            "distinct_dummy_Shader_targets_referenced":37,
        },
        "dummy_shader_material_counts_by_name_digest":names,
    }


class RemainingGuidWeights(unittest.TestCase):
    def test_only_safe_original_weight_histogram_escapes(self):
        original=fixture()
        result=safe_remaining_weights(original)
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(result["custom_dummy_actual"],98)
        self.assertEqual(result["remaining_original_shader_guid_targets_actual"],37)
        self.assertEqual(
            result["original_materials_per_name_digest_weight_histogram"],
            {"33":1,"30":1,"1":35})
        published=json.dumps(result)
        for digest in original["dummy_shader_material_counts_by_name_digest"]:
            self.assertNotIn(digest,published)
        self.assertFalse(result["source_names_guids_and_digest_identifiers_exported"])

    def test_source_name_group_count_is_not_forced_to_equal_shader_guid_count(self):
        report=fixture()
        names=report["dummy_shader_material_counts_by_name_digest"]
        keys=list(names)
        names[keys[1]] += names.pop(keys[2])
        result=safe_remaining_weights(report)
        self.assertEqual(result["remaining_original_shader_guid_targets_actual"],37)
        self.assertEqual(result["remaining_original_shader_name_digest_groups_actual"],36)
        self.assertEqual(result["custom_dummy_actual"],98)
        self.assertNotIn(keys[2],json.dumps(result))

    def test_prior_or_forged_real_material_counts_rejected(self):
        cases=[]
        for key,value in (
            ("material_docs_using_non_dummy_Shader",643),
            ("material_docs_using_dummy_Shader",105),
            ("distinct_dummy_Shader_targets_referenced",38),
        ):
            report=fixture()
            report["counts"][key]=value
            cases.append(report)
        for report in cases:
            with self.subTest(report=report["counts"]):
                with self.assertRaisesRegex(ValueError,"untrusted_original_post23"):
                    safe_remaining_weights(report)

    def test_invalid_or_inconsistent_digest_weights_rejected(self):
        bad=fixture()
        bad["dummy_shader_material_counts_by_name_digest"].pop(f"{0:064x}")
        with self.assertRaises(ValueError):
            safe_remaining_weights(bad)
        bad=fixture()
        bad["dummy_shader_material_counts_by_name_digest"][f"{0:064x}"]=34
        with self.assertRaisesRegex(ValueError,"inconsistent_original_post23"):
            safe_remaining_weights(bad)
        bad=fixture()
        bad["dummy_shader_material_counts_by_name_digest"]["not-hex"]=1
        with self.assertRaises(ValueError):
            safe_remaining_weights(bad)


if __name__=="__main__":
    unittest.main()
