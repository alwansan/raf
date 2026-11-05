"""T4 original SaveWorld RGD CIL edge validator source-free controls."""
import copy
import unittest
from scripts.t4_validate_original_rgd_producer import validate


def baseline():
    return {
        "schema_version": 1,
        "scope": "EXACT_ORIGINAL_COMPILED_IL_READ_ONLY",
        "original_managed_dll_size_sha_verified": True,
        "original_saveandload_owner_unique": True,
        "original_saveworld_unique": True,
        "original_saveuser_unique": True,
        "original_private_save_rgd_signature_unique": True,
        "world_direct_calls_to_exact_save_rgd": 1,
        "world_other_calls_named_save": 0,
        "user_direct_calls_to_exact_save_rgd": 0,
        "user_other_calls_named_save": 1,
        "world_direct_rgd_constructor_calls": 1,
        "user_direct_rgd_constructor_calls": 0,
        "world_rgd_typed_locals": 1,
        "user_rgd_typed_locals": 0,
        "world_rgd_field_stores": 3,
        "direct_constructor_is_dynamically_proven_save_argument": False,
        "original_save_method_invoked": False,
        "game_world_rgd_written_or_loaded": False,
        "source_or_rgd_payload_published": False,
        "android_unity_il2cpp_or_phone_executed": False,
    }


class TestOriginalSaveWorldProvenance(unittest.TestCase):
    def test_bounded_positive_never_game_success(self):
        x=validate(baseline())
        self.assertEqual(x["world_direct_save_rgd_call_count"], 1)
        self.assertEqual(x["world_argument_construction_clue"], "DIRECT_RGD_CTOR_IN_SAVEWORLD")
        self.assertFalse(x["actual_argument_instance_identity_proven"])
        self.assertFalse(x["actual_save_invoked"])
        self.assertFalse(x["game_world_rgd_written_or_reloaded"])
        self.assertFalse(x["android_device_tested"])

    def test_zero_direct_rgd_constructor_is_ambiguity_not_failure(self):
        x=baseline()
        x["world_direct_rgd_constructor_calls"]=0
        y=validate(x)
        self.assertEqual(y["world_argument_construction_clue"], "NO_DIRECT_RGD_CTOR_IN_SAVEWORLD")
        self.assertFalse(y["actual_argument_instance_identity_proven"])

    def test_duplicate_direct_save_calls_rejected(self):
        x=baseline()
        x["world_direct_calls_to_exact_save_rgd"]=2
        with self.assertRaises(ValueError):validate(x)

    def test_missing_direct_save_call_rejected(self):
        x=baseline()
        x["world_direct_calls_to_exact_save_rgd"]=0
        with self.assertRaises(ValueError):validate(x)

    def test_ambiguous_overloaded_save_call_rejected(self):
        x=baseline()
        x["world_other_calls_named_save"]=1
        with self.assertRaises(ValueError):validate(x)

    def test_unverified_original_sha_rejected(self):
        x=baseline()
        x["original_managed_dll_size_sha_verified"]=False
        with self.assertRaises(ValueError):validate(x)

    def test_unverified_rgd_signature_rejected(self):
        x=baseline()
        x["original_private_save_rgd_signature_unique"]=False
        with self.assertRaises(ValueError):validate(x)

    def test_wrong_original_source_scope_rejected(self):
        x=baseline()
        x["scope"]="SYNTHETIC_SOURCE"
        with self.assertRaises(ValueError):validate(x)

    def test_counter_as_bool_rejected(self):
        x=baseline()
        x["world_direct_rgd_constructor_calls"]=True
        with self.assertRaises(ValueError):validate(x)

    def test_negative_counter_rejected(self):
        x=baseline()
        x["world_rgd_field_stores"]=-1
        with self.assertRaises(ValueError):validate(x)

    def test_fabricated_runtime_instance_identity_rejected(self):
        x=baseline()
        x["direct_constructor_is_dynamically_proven_save_argument"]=True
        with self.assertRaises(ValueError):validate(x)

    def test_fabricated_method_invocation_rejected(self):
        x=baseline()
        x["original_save_method_invoked"]=True
        with self.assertRaises(ValueError):validate(x)

    def test_fabricated_phone_acceptance_rejected(self):
        x=baseline()
        x["android_unity_il2cpp_or_phone_executed"]=True
        with self.assertRaises(ValueError):validate(x)

    def test_fabricated_original_rgd_write_rejected(self):
        x=baseline()
        x["game_world_rgd_written_or_loaded"]=True
        with self.assertRaises(ValueError):validate(x)

    def test_extra_private_field_rejected(self):
        x=baseline()
        x["original_serializer_raw_field"]="test"
        with self.assertRaises(ValueError):validate(x)

    def test_report_without_proprietary_payload(self):
        x=validate(baseline())
        self.assertNotIn("raw", str(x).lower())
        self.assertFalse(x["original_game_data_published"])


if __name__=="__main__":
    unittest.main()
