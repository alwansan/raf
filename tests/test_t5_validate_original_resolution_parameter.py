"""Synthetic category/identity checks; no original game method/type strings."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.t5_validate_original_resolution_parameter import (
    CATEGORIES, R_NUMERIC, R_BOOL, load, verify,
)


def fixture():
    row = {k: 0 for k in R_NUMERIC}
    row.update({k: False for k in R_BOOL})
    row.update(
        original_settings_method_bodies=42, apply_definitions=1,
        apply_direct_call_sites=3, distinct_apply_caller_methods=3,
        zero_parameter_caller_count=2, one_parameter_caller_count=1,
        one_parameter_public_type_category="unity_screen_resolution",
        one_parameter_caller_direct_dropdown_api_calls=8,
        one_parameter_caller_dropdown_field_reference_sites=8,
        one_parameter_caller_returns_void=True,
    )
    return {
        "schema_version": 1, "original_assembly_sha256_verified": True,
        "original_assembly_bytes": 3211776, "compiled_original_il": True,
        "original_method_and_type_identifiers_private": True, "report": row,
        "serialized_unity_event_callback_proven": False,
        "persisted_android_render_resolution_proven": False,
        "original_game_modified": False, "android_device_tested": False,
    }


class T5OriginalResolutionParameterTests(unittest.TestCase):
    def test_category_is_not_event_or_persistence_proof(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                x = fixture()
                x["report"]["one_parameter_public_type_category"] = category
                result = verify(x)
                self.assertEqual(result["one_parameter_caller_type_category"], category)
                self.assertFalse(result["runtime_dropdown_callback_proven"])
                self.assertFalse(result["persisted_android_render_resolution_proven"])

    def test_exact_source_counts_required(self):
        for key, value in (
            ("original_settings_method_bodies", 41),
            ("apply_definitions", 2),
            ("apply_direct_call_sites", 2),
            ("distinct_apply_caller_methods", 2),
            ("zero_parameter_caller_count", 1),
            ("one_parameter_caller_count", 2),
            ("one_parameter_caller_direct_dropdown_api_calls", 7),
            ("one_parameter_caller_dropdown_field_reference_sites", 9),
        ):
            x = fixture()
            x["report"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(x)

    def test_metadata_true_claims_refused(self):
        for key in ("serialized_unity_event_callback_proven",
                    "persisted_android_render_resolution_proven",
                    "original_game_modified", "android_device_tested"):
            x = fixture()
            x[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(x)
        for key in ("unity_serialized_onvaluechanged_binding_proven",
                    "persistent_android_render_scale_binding_proven",
                    "android_device_tested"):
            x = fixture()
            x["report"][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(x)

    def test_unapproved_identifier_or_private_type_rejected(self):
        x = fixture()
        x["report"]["one_parameter_public_type_category"] = "Game.GraphicsSettingsBox.PrivateType"
        with self.assertRaises(ValueError):
            verify(x)
        x = fixture()
        x["report"]["original_method_token"] = 123456
        with self.assertRaises(ValueError):
            verify(x)

    def test_not_leaking_fake_bool_or_missing_source_provenance(self):
        for key, val in (
            ("original_assembly_sha256_verified", 1),
            ("original_assembly_bytes", True),
            ("original_assembly_bytes", 3211775),
            ("compiled_original_il", False),
            ("original_method_and_type_identifiers_private", False),
        ):
            x = fixture()
            x[key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(x)

    def test_mutually_exclusive_method_flags(self):
        x = fixture()
        x["report"]["one_parameter_caller_is_public"] = True
        x["report"]["one_parameter_caller_is_private"] = True
        with self.assertRaises(ValueError):
            verify(x)

    def test_value_get_set_refresh_event_subset(self):
        x = fixture()
        x["report"]["one_parameter_caller_direct_dropdown_value_get_sites"] = 5
        x["report"]["one_parameter_caller_direct_dropdown_value_set_sites"] = 4
        with self.assertRaises(ValueError):
            verify(x)
        x = fixture()
        x["report"]["one_parameter_caller_direct_dropdown_onvaluechanged_get_sites"] = 1
        with self.assertRaises(ValueError):
            verify(x)
        x = fixture()
        x["report"]["one_parameter_caller_direct_addlistener_sites"] = 1
        with self.assertRaises(ValueError):
            verify(x)

    def test_bad_numeric_types_and_boolean_flags(self):
        for key, val in (
            ("one_parameter_caller_direct_dropdown_value_get_sites", True),
            ("class_direct_addlistener_sites", -1),
            ("one_parameter_caller_direct_dropdown_value_set_sites", 100001),
            ("one_parameter_caller_is_static", "no"),
        ):
            x = fixture()
            x["report"][key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(x)

    def test_duplicate_json_and_symlink_and_oversized(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "report.json"
            p.write_text(json.dumps(fixture()), encoding="utf8")
            self.assertEqual(load(p)["one_parameter_caller_type_category"],
                             "unity_screen_resolution")
            p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text("x" * 16385, encoding="utf8")
            with self.assertRaises(ValueError):
                load(p)
            p.write_text(json.dumps(fixture()), encoding="utf8")
            link = Path(tmp) / "alias.json"
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                load(link)


if __name__ == "__main__":
    unittest.main()
