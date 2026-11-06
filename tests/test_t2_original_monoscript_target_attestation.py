"""Source-free adverse controls for pinned original typed-target attestation."""
import json
import unittest

from scripts.t2_original_monoscript_target_attestation import (
    EXPECTED_COUNTS, EXPECTED_FLAGS, EXPECTED_STATUS, EXPECTED_KEYS,
    parse_safe_json, validate_safe_report,
)


def valid():
    return {"status": EXPECTED_STATUS, **EXPECTED_COUNTS, **EXPECTED_FLAGS}


class PositiveAttestationTests(unittest.TestCase):
    def test_pinned_full_positive_coverage_is_accepted(self):
        self.assertEqual(validate_safe_report(valid()), 55328)
        self.assertEqual(set(valid()), EXPECTED_KEYS)

    def test_pinned_safe_json_roundtrip(self):
        self.assertEqual(validate_safe_report(parse_safe_json(json.dumps(valid()))), 55328)

    def test_zero_typed_is_not_green_even_if_partition_self_consistent(self):
        r = valid()
        r["original_opaque_m_Script_rows_typed_target_checked"] = 0
        r["script_refs_to_SHA_original_typed_MonoScript_objects"] = 0
        r["source_target_rows_budget_skipped"] = 55328
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_partial_coverage_is_not_green(self):
        r = valid()
        r["original_opaque_m_Script_rows_typed_target_checked"] = 55000
        r["script_refs_to_SHA_original_typed_MonoScript_objects"] = 55000
        r["source_target_rows_budget_skipped"] = 328
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_non_typed_object_is_not_green(self):
        r = valid()
        r["script_refs_to_SHA_original_typed_MonoScript_objects"] = 55327
        r["script_refs_to_SHA_original_absent_or_other_type_PathIDs"] = 1
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_source_provenance_false_rejected(self):
        r = valid()
        r["original_zip2_SHA_authenticated"] = False
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_ambiguous_manifest_match_rejected(self):
        r = valid()
        r["original_ambiguous_manifest_candidate_ref_rows"] = 1
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_absent_manifest_match_rejected(self):
        r = valid()
        r["original_missing_manifest_candidate_ref_rows"] = 1
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_no_staged_provider_rejected(self):
        r = valid()
        r["original_typed_target_files_SHA_staged"] = 0
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_original_provider_bytes_drift_rejected(self):
        r = valid()
        r["original_typed_target_bytes_SHA_staged"] = 758413
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_distinct_MonoScript_targets_drift_rejected(self):
        r = valid()
        r["sum_per_original_provider_distinct_typed_MonoScript_targets"] = 0
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_boolean_cannot_pretend_to_be_integer(self):
        r = valid()
        r["source_target_rows_budget_skipped"] = False
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_float_cannot_pretend_to_be_integer(self):
        r = valid()
        r["original_typed_target_files_SHA_staged"] = 1.0
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_false_device_and_guid_claims_rejected(self):
        for key in ("Android_water_pixels_verified",
                    "source_external_basename_proves_Unity_GUID",
                    "original_Foam_Runtime_Shader_binding_verified"):
            r = valid()
            r[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_safe_report(r)

    def test_missing_or_private_extra_field_rejected(self):
        r = valid()
        del r["source_external_path_variants"]
        with self.assertRaises(ValueError):
            validate_safe_report(r)
        r = valid()
        r["original_script_class_name"] = "private"
        with self.assertRaises(ValueError):
            validate_safe_report(r)

    def test_json_duplicate_field_rejected_before_validation(self):
        with self.assertRaises(ValueError):
            parse_safe_json('{"status":"a","status":"b"}')

    def test_json_too_large_rejected(self):
        with self.assertRaises(ValueError):
            parse_safe_json("x" * 17000)

    def test_status_is_source_original_not_runtime(self):
        r = valid()
        r["status"] = "Android_water_success"
        with self.assertRaises(ValueError):
            validate_safe_report(r)


if __name__ == "__main__":
    unittest.main()
