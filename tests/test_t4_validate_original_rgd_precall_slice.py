"""No-original-data adversarial tests for original SaveWorld RGD precursor report."""
import unittest
from scripts.t4_validate_original_rgd_precall_slice import validate


def good():
    return {
        "schema_version": 1,
        "source_kind": "PINNED_ORIGINAL_READONLY_IL",
        "original_assembly_sha_verified": True,
        "original_private_RGD_class_verified": True,
        "saveworld_exact_original_private_save_edge": True,
        "saveuser_exact_original_private_save_edge": True,
        "world_precall_type_class": "CONSTRUCTOR_DERIVED_RGD",
        "user_precall_type_class": "FIELD_EXACT_RGD",
        "world_local_lexical_store_site_count": 1,
        "world_nearest_lexical_store_precall_class": "CONSTRUCTOR_DERIVED_RGD",
        "user_field_declaring_scope": "OTHER_ORIGINAL_CLASS",
        "user_field_direct_store_site_count": 3,
        "lexical_local_store_reached_save_at_runtime": False,
        "user_field_initialized_at_runtime": False,
        "original_save_executed": False,
        "original_RGD_created_or_read": False,
        "original_game_source_or_payload_published": False,
        "Android_Unity_IL2CPP_or_device_executed": False,
        "dynamic_argument_identity_proven": False,
    }


class VerifyOriginalRgdPrecallSlice(unittest.TestCase):
    def test_adversarial_positive_cannot_claim_world_save(self):
        report = validate(good())
        self.assertEqual(report["world_precall_class"], "CONSTRUCTOR_DERIVED_RGD")
        self.assertFalse(report["argument_value_origin_proven"])
        self.assertFalse(report["unity_android_il2cpp_or_phone_executed"])

    def test_unknown_is_valid_and_not_claim(self):
        r=good()
        r["world_precall_type_class"]="UNKNOWN_PRECALL"
        o=validate(r)
        self.assertEqual(o["world_precall_class"], "UNKNOWN_PRECALL")
        self.assertFalse(o["gameplay_save_rgd_written_or_reopened"])

    def test_null_literal_does_not_prove_actual_null_was_saved(self):
        r=good()
        r["world_precall_type_class"]="NULL_LITERAL"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_factory_return_is_structural_not_execution(self):
        r=good()
        r["user_precall_type_class"]="CALL_RETURN_EXACT_RGD"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_exact_field_is_structural_not_execution(self):
        r=good()
        r["user_precall_type_class"]="FIELD_EXACT_RGD"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_derived_local_is_structural_not_execution(self):
        r=good()
        r["user_precall_type_class"]="LOCAL_DERIVED_RGD"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_branch_is_unknown_stack_identity(self):
        r=good()
        r["user_precall_type_class"]="BRANCH_PREVIOUS_STACK"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_duped_stack_is_unknown_identity(self):
        r=good()
        r["user_precall_type_class"]="DUP_PREVIOUS_STACK"
        self.assertFalse(validate(r)["argument_value_origin_proven"])

    def test_lexical_constructor_is_not_executed_path(self):
        result=validate(good())
        self.assertEqual(result["world_nearest_store_source_class"], "CONSTRUCTOR_DERIVED_RGD")
        self.assertFalse(result["original_local_store_reached_save_at_runtime"])

    def test_no_stores_can_remain_unknown(self):
        r=good();r["world_local_lexical_store_site_count"]=0
        r["world_nearest_lexical_store_precall_class"]="NO_LEXICAL_STORE"
        result=validate(r)
        self.assertEqual(result["world_local_lexical_store_sites"], 0)
        self.assertFalse(result["argument_value_origin_proven"])

    def test_local_store_count_cannot_be_boolean(self):
        r=good();r["world_local_lexical_store_site_count"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_store_count_cannot_be_negative(self):
        r=good();r["world_local_lexical_store_site_count"]=-1
        with self.assertRaises(ValueError):validate(r)

    def test_store_count_cannot_be_huge(self):
        r=good();r["world_local_lexical_store_site_count"]=10001
        with self.assertRaises(ValueError):validate(r)

    def test_false_store_source_without_store_rejected(self):
        r=good();r["world_local_lexical_store_site_count"]=0
        with self.assertRaises(ValueError):validate(r)

    def test_fake_store_without_source_rejected(self):
        r=good();r["world_nearest_lexical_store_precall_class"]="NO_LEXICAL_STORE"
        with self.assertRaises(ValueError):validate(r)

    def test_unknown_local_source_kind_rejected(self):
        r=good();r["world_nearest_lexical_store_precall_class"]="FIELD_PrivateInfo"
        with self.assertRaises(ValueError):validate(r)

    def test_no_field_load_cannot_claim_write_sites(self):
        r=good();r["user_field_declaring_scope"]="NOT_A_FIELD_LOAD"
        with self.assertRaises(ValueError):validate(r)

    def test_unresolved_field_declaration_without_stores_is_uncertain(self):
        r=good();r["user_field_declaring_scope"]="DECLARER_UNRESOLVED"
        r["user_field_direct_store_site_count"]=0
        self.assertFalse(validate(r)["original_user_field_initialized_at_runtime"])

    def test_external_field_source_name_rejected(self):
        r=good();r["user_field_declaring_scope"]="Game.PlayerRgd.private"
        with self.assertRaises(ValueError):validate(r)

    def test_field_write_count_not_boolean(self):
        r=good();r["user_field_direct_store_site_count"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_fake_user_initialization_rejected(self):
        r=good();r["user_field_initialized_at_runtime"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_fake_lexical_path_execution_rejected(self):
        r=good();r["lexical_local_store_reached_save_at_runtime"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_bool_as_schema_rejected(self):
        r=good()
        r["schema_version"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_missing_SHA_rejected(self):
        r=good()
        r["original_assembly_sha_verified"]=False
        with self.assertRaises(ValueError):validate(r)

    def test_fake_SaveWorld_edge_rejected(self):
        r=good()
        r["saveworld_exact_original_private_save_edge"]=False
        with self.assertRaises(ValueError):validate(r)

    def test_fake_SaveUser_edge_rejected(self):
        r=good()
        r["saveuser_exact_original_private_save_edge"]=False
        with self.assertRaises(ValueError):validate(r)

    def test_original_save_claim_rejected(self):
        r=good()
        r["original_save_executed"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_game_file_read_claim_rejected(self):
        r=good()
        r["original_RGD_created_or_read"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_phone_claim_rejected(self):
        r=good()
        r["Android_Unity_IL2CPP_or_device_executed"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_dynamic_identity_claim_rejected(self):
        r=good()
        r["dynamic_argument_identity_proven"]=True
        with self.assertRaises(ValueError):validate(r)

    def test_raw_member_name_rejected(self):
        r=good()
        r["world_precall_type_class"]="FIELD_GameManager.worldSaveData"
        with self.assertRaises(ValueError):validate(r)

    def test_private_clr_type_rejected(self):
        r=good()
        r["user_precall_type_class"]="CALL_RETURN_CustomSaveType"
        with self.assertRaises(ValueError):validate(r)

    def test_unknown_key_rejected(self):
        r=good()
        r["original_private_data"]="secret"
        with self.assertRaises(ValueError):validate(r)

    def test_unverified_scope_rejected(self):
        r=good()
        r["source_kind"]="SYNTHETIC_GAME_SOURCE"
        with self.assertRaises(ValueError):validate(r)

    def test_malformed_report_rejected(self):
        with self.assertRaises(ValueError):validate([good()])

    def test_unrelated_type_relation_valid_no_identity(self):
        r=good()
        r["world_precall_type_class"]="FIELD_OTHER_OR_UNRESOLVED"
        self.assertFalse(validate(r)["argument_value_origin_proven"])


if __name__ == "__main__":
    unittest.main()
