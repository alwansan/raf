"""No-original-file negative controls for private original Save outcome."""
import copy
import unittest
from scripts.t4_verify_original_rgd_save_roundtrip import validate

def genuine():
    return {
        "schema_version":1, "source":"IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED",
        "original_dll_sha_verified":True, "original_seed_sha_verified":True,
        "managed_reference_siblings":151, "original_CLR_assembly_loaded":True,
        "formatter_runtime":"DOTNET8_BINARYFORMATTER",
        "actual_formatter_deserialize_attempted":True,
        "actual_formatter_deserialize_object_created":True,
        "deserialized_root_defined_in_original_dll":True,
        "bounded_runtime_category":"NONE",
        "original_SaveAndLoad_LoadT_invoked":True,
        "user_generated_game_world_loaded":False,
        "real_game_rgd_write_or_roundtrip":False,
        "android_unity_il2cpp_or_phone_executed":False,
        "original_data_or_private_type_names_published":False,
        "original_LoadT_method_signature_verified":True,
        "original_LoadT_returned_matching_seed_type":True,
        "original_LoadT_result_category":"NONE",
        "original_private_Save_IL_guard_passed":True,
        "original_private_Save_safe_calls":5,
        "original_private_Save_invoked":True,
        "original_private_Save_output_created":True,
        "original_private_Save_output_nonzero":True,
        "original_private_Save_generated_LoadT_matching_root":True,
        "original_private_Save_isolated_temp_removed":True,
        "original_private_Save_result_category":"NONE"
    }

class OriginalSaveContract(unittest.TestCase):
    def test_complete_authentic_seed_only(self):
        p=validate(genuine())
        self.assertTrue(p["generated_original_seed_LoadT_same_type"])
        self.assertFalse(p["user_world_save_or_relaunch_proven"])
        self.assertFalse(p["Android_Unity_IL2CPP_device_executed"])

    def test_guard_refusal_is_a_measured_negative_not_success(self):
        p=genuine()
        for k in ("original_private_Save_IL_guard_passed","original_private_Save_invoked",
                  "original_private_Save_output_created","original_private_Save_output_nonzero",
                  "original_private_Save_generated_LoadT_matching_root",
                  "original_private_Save_isolated_temp_removed"):
            p[k]=False
        p["original_private_Save_result_category"]="ORIGINAL_PRIVATE_SAVE_METHOD_IL_NOT_AUTHENTICATED"
        q=validate(p)
        self.assertFalse(q["original_private_Save_invoked"])

    def test_invocation_without_guard_refused(self):
        p=genuine()
        p["original_private_Save_IL_guard_passed"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_nonzero_without_file_refused(self):
        p=genuine()
        p["original_private_Save_output_created"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_loader_success_without_nonzero_save_refused(self):
        p=genuine()
        p["original_private_Save_output_nonzero"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_premature_category_none_refused(self):
        p=genuine()
        p["original_private_Save_generated_LoadT_matching_root"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_failed_cleanup_cannot_be_full_success(self):
        p=genuine()
        p["original_private_Save_isolated_temp_removed"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_fake_user_world_success_refused(self):
        p=genuine()
        p["user_generated_game_world_loaded"]=True
        with self.assertRaises(ValueError):
            validate(p)

    def test_fake_android_success_refused(self):
        p=genuine()
        p["android_unity_il2cpp_or_phone_executed"]=True
        with self.assertRaises(ValueError):
            validate(p)

    def test_wrong_original_sha_refused(self):
        p=genuine()
        p["original_seed_sha_verified"]=False
        with self.assertRaises(ValueError):
            validate(p)

    def test_original_reference_count_false_bool_refused(self):
        p=genuine()
        p["managed_reference_siblings"]=True
        with self.assertRaises(ValueError):
            validate(p)

    def test_private_extra_data_rejected(self):
        p=genuine()
        p["original_game_object"]="private"
        with self.assertRaises(ValueError):
            validate(p)

    def test_unknown_error_category_refused(self):
        p=genuine()
        p["original_private_Save_result_category"]="System.Exception.private_stack"
        with self.assertRaises(ValueError):
            validate(p)

    def test_contradictory_success_status_refused(self):
        p=genuine()
        p["original_private_Save_result_category"]="OTHER_ISOLATED_RUNTIME_ERROR"
        with self.assertRaises(ValueError):
            validate(p)

if __name__ == "__main__":
    unittest.main()
