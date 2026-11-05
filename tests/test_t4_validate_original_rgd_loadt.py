"""Fail-closed controls for actual original game generic Load<T>, not world ready."""
import tempfile
import unittest
from pathlib import Path
from scripts.t4_validate_original_rgd_loadt import validate, main


def result(loaded=True, category="NONE"):
    return {
        "schema_version": 1,
        "source": "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED",
        "original_dll_sha_verified": True,
        "original_seed_sha_verified": True,
        "managed_reference_siblings": 151,
        "original_CLR_assembly_loaded": True,
        "formatter_runtime": "DOTNET8_BINARYFORMATTER",
        "actual_formatter_deserialize_attempted": True,
        "actual_formatter_deserialize_object_created": True,
        "deserialized_root_defined_in_original_dll": True,
        "bounded_runtime_category": "NONE",
        "original_SaveAndLoad_LoadT_invoked": True,
        "original_LoadT_method_signature_verified": True,
        "original_LoadT_returned_matching_seed_type": loaded,
        "original_LoadT_result_category": category,
        "user_generated_game_world_loaded": False,
        "real_game_rgd_write_or_roundtrip": False,
        "android_unity_il2cpp_or_phone_executed": False,
        "original_data_or_private_type_names_published": False,
    }


class OriginalLoadTSafeControls(unittest.TestCase):
    def test_true_original_loadt_returned_genuine_root_not_world(self):
        x = validate(result())
        self.assertTrue(x["actual_original_RGD_root_returned"])
        self.assertFalse(x["game_world_playability_proven"])

    def test_original_loader_returns_default_is_a_valid_measured_failure(self):
        x = validate(result(False, "RETURNED_DEFAULT_OR_NONMATCHING_TYPE"))
        self.assertFalse(x["actual_original_RGD_root_returned"])

    def test_real_original_loader_can_throw_bound_category(self):
        x = validate(result(False, "ORIGINAL_TYPE_LOAD_FAILURE"))
        self.assertEqual(x["bounded_original_loader_category"], "ORIGINAL_TYPE_LOAD_FAILURE")

    def test_loader_must_be_actually_invoked(self):
        r = result(); r["original_SaveAndLoad_LoadT_invoked"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_compiled_signature_must_match(self):
        r = result(); r["original_LoadT_method_signature_verified"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_genuine_seed_must_be_authenticated(self):
        r = result(); r["original_seed_sha_verified"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_original_dll_must_be_authenticated(self):
        r = result(); r["original_dll_sha_verified"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_direct_original_binaryformatter_must_run(self):
        r = result(); r["actual_formatter_deserialize_object_created"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_root_original_assembly_must_match(self):
        r = result(); r["deserialized_root_defined_in_original_dll"] = False
        with self.assertRaises(ValueError): validate(r)

    def test_no_android_world_claim(self):
        r = result(); r["android_unity_il2cpp_or_phone_executed"] = True
        with self.assertRaises(ValueError): validate(r)

    def test_no_relaunch_claim(self):
        r = result(); r["real_game_rgd_write_or_roundtrip"] = True
        with self.assertRaises(ValueError): validate(r)

    def test_no_user_game_world_claim(self):
        r = result(); r["user_generated_game_world_loaded"] = True
        with self.assertRaises(ValueError): validate(r)

    def test_no_original_private_types_published(self):
        r = result(); r["private_rgd_type"] = "private"
        with self.assertRaises(ValueError): validate(r)

    def test_no_claim_without_positive_category(self):
        with self.assertRaises(ValueError): validate(result(True, "SERIALIZATION_OR_ORIGINAL_SCHEMA"))

    def test_no_claim_success_on_failure(self):
        with self.assertRaises(ValueError): validate(result(False, "NONE"))

    def test_no_private_error_messages(self):
        r = result(False, "private exception detail")
        with self.assertRaises(ValueError): validate(r)

    def test_unverified_sibling_assemblies_rejected(self):
        r = result(); r["managed_reference_siblings"] = 150
        with self.assertRaises(ValueError): validate(r)

    def test_unknown_file_refused(self):
        with tempfile.TemporaryDirectory() as base:
            self.assertEqual(main(["--report", str(Path(base)/"missing")]), 2)


if __name__ == "__main__":
    unittest.main()
