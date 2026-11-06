"""Synthetic fail-closed controls for actual original owner-world CLR Save/Load.

No private RGD is used in these tests. Values are report-only booleans.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from scripts.t4_validate_owner_world_roundtrip import (
    validate, read_private_report,
    FIELDS,
)

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "android-port/Experiments/T4/OwnerWorldRgdRoundtrip/Program.cs"
SHA7 = [
    "458e0c2bb46f26084cbb2aacaa33913c8ac52daa",
    "8564720a2f72a47091d30c9eae05ebd527be50ac",
    "7e8be5203dd47ea6469e43abacb901b4089bb246",
    "f30fc3f416899cca5b2fb955e437fc716bfcafff",
    "65280828d55f133854fc4c16474c4e3f0bfeac30",
    "a091dd94d84047e68eb8d9715987948b57178aa6",
    "7fad8e552e737cc73985a6906c7ce753d45a41a5",
]


def success():
    return {
        "schema_version": 1,
        "source": "IMMUTABLE_SHA_VERIFIED_OWNER5NOV_WORLD_RGD",
        "original_dll_sha_verified": True,
        "owner_world_git_blob_verified": True,
        "managed_reference_siblings": 151,
        "original_CLR_assembly_loaded": True,
        "formatter_runtime": "DOTNET8_BINARYFORMATTER",
        "actual_formatter_deserialize_attempted": True,
        "actual_formatter_deserialize_object_created": True,
        "deserialized_root_defined_in_original_dll": True,
        "bounded_runtime_category": "NONE",
        "original_SaveAndLoad_LoadT_invoked": True,
        "user_generated_game_world_loaded": False,
        "real_game_rgd_write_or_roundtrip": False,
        "android_unity_il2cpp_or_phone_executed": False,
        "original_data_or_private_type_names_published": False,
        "original_LoadT_method_signature_verified": True,
        "original_LoadT_returned_matching_seed_type": True,
        "original_LoadT_result_category": "NONE",
        "original_private_Save_IL_guard_passed": True,
        "original_private_Save_safe_calls": 5,
        "original_private_Save_audit_category": "NONE",
        "original_private_Save_invoked": True,
        "original_private_Save_output_created": True,
        "original_private_Save_output_nonzero": True,
        "original_private_Save_generated_LoadT_matching_root": True,
        "original_private_Save_isolated_temp_removed": True,
        "original_private_Save_result_category": "NONE",
        "original_isolated_owner_world_roundtrip_verified": True,
        "android_saved_world_or_player_progress_verified": False,
    }


class OriginalOwnerRoundtripContract(unittest.TestCase):
    def test_complete_private_CLR_only_never_phone(self):
        v = validate(success())
        self.assertTrue(v["original_generated_LoadT_matching"])
        self.assertFalse(v["native_android_verified"])
        self.assertFalse(v["phone_world_save_reopen_verified"])

    def test_real_seven_exact_git_hashes_compiled_into_probe(self):
        source = ORIGINAL.read_text()
        for sha in SHA7:
            self.assertIn(sha, source)
        self.assertEqual(len(set(SHA7)), 7)
        self.assertIn("new Dictionary<long, string[]>", source)
        self.assertIn("[319239] = new[]", source)
        self.assertIn("IncrementalHash.CreateHash(HashAlgorithmName.SHA1)", source)
        self.assertIn('GetBytes("blob " + info.Length +', source)
        self.assertIn("OriginalDllSha", source)

    def test_guard_refusal_accepted_only_as_refusal(self):
        p = success()
        for key in (
            "original_private_Save_IL_guard_passed", "original_private_Save_invoked",
            "original_private_Save_output_created", "original_private_Save_output_nonzero",
            "original_private_Save_generated_LoadT_matching_root",
            "original_private_Save_isolated_temp_removed",
            "original_isolated_owner_world_roundtrip_verified",
        ):
            p[key] = False
        p["original_private_Save_audit_category"] = (
            "OWNER_WORLD_ROOT_NOT_ASSIGNABLE_TO_ORIGINAL_RGD_SAVE_ARGUMENT")
        p["original_private_Save_result_category"] = (
            "OWNER_WORLD_ROOT_NOT_ASSIGNABLE_TO_ORIGINAL_RGD_SAVE_ARGUMENT")
        q = validate(p)
        self.assertFalse(q["original_private_Save_invoked"])

    def test_wrong_owner_provenance_rejected(self):
        p = success()
        p["source"] = "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED"
        with self.assertRaises(ValueError):
            validate(p)

    def test_missing_exact_field_refused(self):
        p = success()
        del p["original_private_Save_IL_guard_passed"]
        with self.assertRaises(ValueError):
            validate(p)

    def test_extra_private_class_or_path_field_rejected(self):
        p = success()
        p["original_user_path"] = "never publish private path"
        with self.assertRaises(ValueError):
            validate(p)

    def test_missing_hash_verification_rejected(self):
        p = success()
        p["owner_world_git_blob_verified"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_wrong_original_managed_context_rejected(self):
        p = success()
        p["managed_reference_siblings"] = True
        with self.assertRaises(ValueError):
            validate(p)

    def test_false_original_typed_load_rejected(self):
        p = success()
        p["original_LoadT_returned_matching_seed_type"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_android_device_claim_rejected(self):
        p = success()
        p["android_unity_il2cpp_or_phone_executed"] = True
        with self.assertRaises(ValueError):
            validate(p)

    def test_user_progress_claim_rejected(self):
        p = success()
        p["android_saved_world_or_player_progress_verified"] = True
        with self.assertRaises(ValueError):
            validate(p)

    def test_real_game_world_claim_rejected(self):
        p = success()
        p["real_game_rgd_write_or_roundtrip"] = True
        with self.assertRaises(ValueError):
            validate(p)

    def test_unaudited_save_invoke_rejected(self):
        p = success()
        p["original_private_Save_IL_guard_passed"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_nonzero_output_without_created_rejected(self):
        p = success()
        p["original_private_Save_output_created"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_original_load_return_requires_nonzero_save(self):
        p = success()
        p["original_private_Save_output_nonzero"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_generated_load_and_roundtrip_flag_must_match(self):
        p = success()
        p["original_isolated_owner_world_roundtrip_verified"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_missing_cleanup_never_full_success(self):
        p = success()
        p["original_private_Save_isolated_temp_removed"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_none_category_requires_real_guarded_success(self):
        p = success()
        p["original_private_Save_generated_LoadT_matching_root"] = False
        p["original_isolated_owner_world_roundtrip_verified"] = False
        with self.assertRaises(ValueError):
            validate(p)

    def test_guarded_success_must_report_none(self):
        p = success()
        p["original_private_Save_result_category"] = "RUNTIME_FILE_IO"
        with self.assertRaises(ValueError):
            validate(p)

    def test_private_exception_category_rejected(self):
        p = success()
        p["original_private_Save_result_category"] = "System.PrivateException"
        with self.assertRaises(ValueError):
            validate(p)

    def test_unexpected_il_category_rejected(self):
        p = success()
        p["original_private_Save_audit_category"] = "Method::Field.WithName"
        with self.assertRaises(ValueError):
            validate(p)

    def test_il_uses_exact_type_identity_and_bounded_allowlist(self):
        source = ORIGINAL.read_text()
        self.assertIn("originalArg.IsAssignableFrom(originalRootType)", source)
        self.assertIn("originalArg.Assembly == originalRootType.Assembly", source)
        self.assertIn('sourceArg.Name != "RGD"', source)
        self.assertIn("method[0].GetParameters()[1].ParameterType.IsAssignableFrom(", source)
        self.assertNotIn("m.Parameters[1].ParameterType.Name == originalRootType.Name", source)
        self.assertNotIn("ParameterType != originalRootType", source)
        self.assertIn("AuditOriginalPrivateSave(", source)
        self.assertIn("ORIGINAL_SAVE_FIELD_OR_INDIRECT_ACCESS", source)
        self.assertIn("UNKNOWN_ORIGINAL_SAVE_SUCCESS_CALLEE", source)
        self.assertIn("RuntimeHelpers.GetUninitializedObject", source)
        self.assertIn("new object?[] { savedPath, seedRootObject }", source)
        self.assertIn("Directory.Delete(workDirectory, recursive: true)", source)
        self.assertIn("OriginalFile(assemblyPath, OriginalDllSize, OriginalDllSha)", source)
        self.assertIn("AuthenticOwnerWorldFile(seedPath)", source)
        self.assertNotIn("OriginalSeedSha", source)
        self.assertNotIn("original_seed_sha_verified", source)

    def test_report_reader_rejects_hardlinked_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "result.json"
            b = root / "link.json"
            a.write_text("{}", encoding="utf-8")
            import os
            os.link(a, b)
            with self.assertRaises(ValueError):
                read_private_report(a)

    def test_report_reader_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "result.json"
            a.write_text("{}", encoding="utf-8")
            alias = root / "alias.json"
            alias.symlink_to(a)
            with self.assertRaises(ValueError):
                read_private_report(alias)


if __name__ == "__main__":
    unittest.main()
