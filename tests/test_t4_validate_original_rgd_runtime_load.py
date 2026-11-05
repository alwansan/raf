"""Adversarial tests: actual original Data.rgd CLR probe must not fake phone proof."""
import tempfile
import unittest
from pathlib import Path
from scripts.t4_validate_original_rgd_runtime_load import validate, main


def report(success=False, category="SERIALIZATION_OR_ORIGINAL_SCHEMA", native_root=False):
    return {
        "schema_version": 1,
        "source": "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED",
        "original_dll_sha_verified": True,
        "original_seed_sha_verified": True,
        "managed_reference_siblings": 151,
        "original_CLR_assembly_loaded": True,
        "formatter_runtime": "DOTNET8_BINARYFORMATTER",
        "actual_formatter_deserialize_attempted": True,
        "actual_formatter_deserialize_object_created": success,
        "deserialized_root_defined_in_original_dll": native_root,
        "bounded_runtime_category": category,
        "original_SaveAndLoad_LoadT_invoked": False,
        "user_generated_game_world_loaded": False,
        "real_game_rgd_write_or_roundtrip": False,
        "android_unity_il2cpp_or_phone_executed": False,
        "original_data_or_private_type_names_published": False,
    }


class AuthenticRgdRuntimeSchemaTests(unittest.TestCase):
    def test_genuine_seed_deserialize_failure_is_valid_bounded_result(self):
        result = validate(report())
        self.assertEqual(result["runtime_category"], "SERIALIZATION_OR_ORIGINAL_SCHEMA")
        self.assertFalse(result["real_save_load_on_android_proven"])

    def test_genuine_seed_deserialize_success_is_not_game_success(self):
        result = validate(report(True, "NONE", True))
        self.assertTrue(result["original_rgd_seed_deserialized"])
        self.assertFalse(result["original_SaveAndLoad_LoadT_executed"])

    def test_runtime_may_create_object_from_other_assembly(self):
        result = validate(report(True, "NONE", False))
        self.assertFalse(result["actual_original_type_instantiated"])

    def test_original_seed_authentication_is_required(self):
        x = report(); x["original_seed_sha_verified"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_original_dll_authentication_is_required(self):
        x = report(); x["original_dll_sha_verified"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_real_deserializer_execution_required(self):
        x = report(); x["actual_formatter_deserialize_attempted"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_unrecognized_original_companion_count(self):
        x = report(); x["managed_reference_siblings"] = 150
        with self.assertRaises(ValueError): validate(x)

    def test_no_runtime_api_substitution(self):
        x = report(); x["formatter_runtime"] = "SAFE_RECORDS_ONLY"
        with self.assertRaises(ValueError): validate(x)

    def test_reject_false_world_load_success(self):
        x = report(); x["user_generated_game_world_loaded"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_reject_false_original_load_method(self):
        x = report(); x["original_SaveAndLoad_LoadT_invoked"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_reject_native_android_claim(self):
        x = report(); x["android_unity_il2cpp_or_phone_executed"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_reject_private_data_field(self):
        x = report(); x["decoded_root_name"] = "private-data"
        with self.assertRaises(ValueError): validate(x)

    def test_reject_exceptions_not_on_public_allowlist(self):
        x = report(); x["bounded_runtime_category"] = "PRIVATE_EXCEPTION_TEXT"
        with self.assertRaises(ValueError): validate(x)

    def test_reject_success_with_failure_category(self):
        x = report(True, "SERIALIZATION_OR_ORIGINAL_SCHEMA")
        with self.assertRaises(ValueError): validate(x)

    def test_reject_failure_without_category(self):
        with self.assertRaises(ValueError): validate(report(False, "NONE"))

    def test_reject_nonboolean_result(self):
        x = report(); x["actual_formatter_deserialize_object_created"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_reject_original_type_claim_without_object(self):
        with self.assertRaises(ValueError): validate(report(False, "OTHER_ISOLATED_RUNTIME_ERROR", True))

    def test_missing_report_file_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(main(["--report", str(Path(root) / "absent.json")]), 2)


if __name__ == "__main__":
    unittest.main()
