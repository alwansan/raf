"""Synthetic original-IL proof-contract fixtures; no proprietary game source."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.t5_validate_resolution_apply_callers import (
    EVIDENCE_FALSE, PROFILE_NUMERIC, PROFILE_BOOL, load, verify,
)


def sample():
    def caller(**kw):
        row = {k: 0 for k in PROFILE_NUMERIC}
        row.update({k: False for k in PROFILE_BOOL})
        row.update(apply_call_sites=1)
        row.update(kw)
        return row

    return {
        "schema_version": 1,
        "original_assembly_sha_verified": True,
        "original_assembly_bytes": 3211776,
        "compiled_original_il_not_decompiled_source": True,
        "original_graphics_settings_type_unique": True,
        "output_method_names_tokens_private": True,
        "evidence": {
            "original_class_methods_with_body": 42,
            "apply_method_definitions": 1,
            "apply_method_direct_screen_set_resolution_sites": 1,
            "apply_method_direct_scalable_resize_buffers_sites": 0,
            "internal_apply_call_sites": 3,
            "distinct_internal_apply_callers": 3,
            "external_apply_call_sites": 0,
            "distinct_external_apply_callers": 0,
            "external_apply_callers_in_settings_class": 0,
            "original_option_population_sites": 1,
            "original_option_population_methods": 1,
            "internal_caller_profiles": [
                caller(parameters=1, has_int_parameter=True),
                caller(is_known_unity_lifecycle=True, contains_option_population=True),
                caller(direct_screen_current_resolution_reads=1),
            ],
            **{k: False for k in EVIDENCE_FALSE},
        },
        "selection_to_runtime_callback_proven": False,
        "persisted_android_render_scale_proven": False,
        "device_tested": False,
    }


class OriginalApplyCallerGateTests(unittest.TestCase):
    def test_valid_three_distinct_callers_are_source_not_android_proof(self):
        result = verify(sample())
        self.assertTrue(result["verified_original_three_apply_calls"])
        self.assertEqual(result["distinct_caller_methods"], 3)
        self.assertFalse(result["selection_to_runtime_callback_proven"])
        self.assertFalse(result["persisted_android_render_scale_proven"])

    def test_three_sites_in_one_method_distinct_from_three_method_claim(self):
        data = sample()
        data["evidence"]["internal_caller_profiles"] = [
            {**data["evidence"]["internal_caller_profiles"][0], "apply_call_sites": 3}]
        data["evidence"]["distinct_internal_apply_callers"] = 1
        self.assertEqual(verify(data)["distinct_caller_methods"], 1)
        self.assertFalse(verify(data)["selection_to_runtime_callback_proven"])

    def test_bad_source_and_method_sites_fail_closed(self):
        for key, val in [
            ("original_class_methods_with_body", 41),
            ("internal_apply_call_sites", 2),
            ("apply_method_direct_screen_set_resolution_sites", 0),
            ("apply_method_definitions", 2),
            ("original_option_population_sites", 0),
            ("apply_method_direct_scalable_resize_buffers_sites", 1),
        ]:
            with self.subTest(key=key):
                data = sample()
                data["evidence"][key] = val
                with self.assertRaises(ValueError):
                    verify(data)

    def test_missing_caller_or_site_cannot_be_silent(self):
        data = sample()
        data["evidence"]["internal_caller_profiles"].pop()
        with self.assertRaises(ValueError):
            verify(data)
        data = sample()
        data["evidence"]["internal_caller_profiles"][0]["apply_call_sites"] = 0
        with self.assertRaises(ValueError):
            verify(data)
        data = sample()
        data["evidence"]["internal_caller_profiles"][0]["apply_call_sites"] = 2
        with self.assertRaises(ValueError):
            verify(data)

    def test_external_call_site_metadata_is_bounded_but_not_proof(self):
        data = sample()
        data["evidence"].update(external_apply_call_sites=3,
                                distinct_external_apply_callers=2,
                                external_apply_callers_in_settings_class=1)
        self.assertEqual(verify(data)["external_direct_apply_sites"], 3)
        self.assertFalse(verify(data)["persisted_android_render_scale_proven"])
        data["evidence"]["distinct_external_apply_callers"] = 4
        with self.assertRaises(ValueError):
            verify(data)

    def test_false_runtime_and_persistence_claims_refused(self):
        for key in ("selection_to_runtime_callback_proven",
                    "persisted_android_render_scale_proven", "device_tested"):
            data = sample()
            data[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)
        for key in EVIDENCE_FALSE:
            data = sample()
            data["evidence"][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)

    def test_method_signature_type_and_subset_guards(self):
        for key, value in [
            ("apply_call_sites", True), ("parameters", -1),
            ("has_int_parameter", 1), ("is_known_unity_lifecycle", "yes"),
        ]:
            data = sample()
            data["evidence"]["internal_caller_profiles"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)
        data = sample()
        data["evidence"]["internal_caller_profiles"][0]["parameters"] = 0
        with self.assertRaises(ValueError):
            verify(data)
        data = sample()
        data["evidence"]["internal_caller_profiles"][0]["private_method_name"] = "not-allowed"
        with self.assertRaises(ValueError):
            verify(data)

    def test_more_than_original_option_owners_rejected(self):
        data = sample()
        data["evidence"]["internal_caller_profiles"][0]["contains_option_population"] = True
        with self.assertRaises(ValueError):
            verify(data)

    def test_json_duplicate_and_symlink_size_limits(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "safe.json"
            p.write_text(json.dumps(sample()), encoding="utf-8")
            self.assertEqual(load(p)["distinct_caller_methods"], 3)
            p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text("x" * 16385, encoding="utf-8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text(json.dumps(sample()), encoding="utf-8")
            link = Path(d) / "link.json"
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                load(link)

    def test_source_provenance_cannot_be_boolean_or_missing(self):
        for key, bad in [
            ("original_assembly_sha_verified", 1),
            ("original_assembly_bytes", True),
            ("original_assembly_bytes", 3211775),
            ("output_method_names_tokens_private", False),
            ("compiled_original_il_not_decompiled_source", False),
        ]:
            data = sample()
            data[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(data)


if __name__ == "__main__":
    unittest.main()
