"""No original game data: adversarial T4 derived RGD initialization CIL proof."""
import unittest
from scripts.t4_validate_original_rgd_init_context import validate


def good():
    return {
        "schema": 1,
        "scope": "PINNED_ORIGINAL_READONLY_IL_CLASSIFICATION",
        "original_assembly_sha_verified": True,
        "original_world_and_user_save_rgd_edges_verified": True,
        "world_producer_declaring_scope": "OTHER_ORIGINAL_CLASS",
        "world_producer_argument_count_category": "ZERO",
        "world_producer_invocation_kind": "STATIC_CALL",
        "world_producer_compiled_method_body_found": True,
        "world_factory_return_metadata": {
            "factory_lexical_return_sites": 2,
            "factory_return_preceded_by_null_literal": 0,
            "factory_return_preceded_by_derived_local": 1,
            "factory_return_preceded_by_derived_field": 0,
            "factory_return_preceded_by_derived_call": 0,
            "factory_return_preceded_by_derived_constructor": 0,
            "factory_return_preceded_by_other_or_unknown": 1,
            "factory_derived_rgd_local_slot_count": 1,
            "factory_direct_derived_rgd_constructor_sites": 1,
            "factory_direct_derived_rgd_returning_call_sites": 0,
            "factory_conditional_branch_sites": 2,
            "factory_throw_or_rethrow_sites": 0,
            "factory_null_literal_load_sites": 0,
            "factory_all_return_paths_proven": False,
            "factory_return_local_lexical_store_sites": 2,
            "factory_return_local_store_null_literal": 0,
            "factory_return_local_store_derived_constructor": 1,
            "factory_return_local_store_derived_call": 0,
            "factory_return_local_store_derived_local": 0,
            "factory_return_local_store_derived_field": 0,
            "factory_return_local_store_other_or_unknown": 1,
            "factory_return_local_nearest_lexical_store_source": "OTHER_OR_UNKNOWN",
            "factory_return_local_store_path_reachability_proven": False,
        },
        "field_write_breakdown": {
            "user_original_direct_write_sites": 3,
            "user_field_writes_in_instance_constructor": 1,
            "user_field_writes_in_static_constructor": 0,
            "user_field_writes_in_saveworld": 0,
            "user_field_writes_in_saveuser": 0,
            "user_field_writes_in_other_saveandload_methods": 2,
            "user_field_writes_in_other_original_types": 0,
            "user_field_write_immediate_null_literals": 1,
            "user_field_write_immediate_derived_typed_values": 1,
            "user_field_write_immediate_unknown_or_other": 1,
        },
        "direct_game_save_invoked": False,
        "actual_world_data_initialized": False,
        "original_rgd_file_read_or_written": False,
        "android_unity_il2cpp_device_executed": False,
        "derived_rgd_object_identity_or_control_flow_proven": False,
        "private_game_code_or_data_published": False,
    }


class TestOriginalRgdInitContext(unittest.TestCase):
    def test_source_real_return_local_stores_remain_lexical(self):
        result = validate(good())
        f = result["source_authentic_world_factory_return_site_categories"]
        self.assertEqual(f["factory_return_local_lexical_store_sites"], 2)
        self.assertFalse(result["factory_control_flow_paths_or_runtime_values_proven"])
        self.assertFalse(result["same_world_saved_or_reopened_proven"])

    def test_no_local_store_is_allowed_but_not_proof_of_initializer(self):
        x = good(); f = x["world_factory_return_metadata"]
        f["factory_return_local_lexical_store_sites"] = 0
        f["factory_return_local_store_derived_constructor"] = 0
        f["factory_return_local_store_other_or_unknown"] = 0
        f["factory_return_local_nearest_lexical_store_source"] = "NO_STORES"
        self.assertFalse(validate(x)["derived_RGD_runtime_value_initialized_proven"])

    def test_missing_return_local_source_field_rejected(self):
        x = good(); del x["world_factory_return_metadata"]["factory_return_local_store_derived_call"]
        with self.assertRaises(ValueError): validate(x)

    def test_private_source_name_cannot_escape(self):
        x = good(); x["world_factory_return_metadata"]["private_factory_local_name"] = "WorldSave"
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_count_must_not_be_boolean(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_lexical_store_sites"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_count_cannot_be_negative(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_lexical_store_sites"] = -1
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_count_cannot_exceed_bound(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_lexical_store_sites"] = 10001
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_count_sum_must_match(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_store_other_or_unknown"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_nearest_class_is_bounded(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_nearest_lexical_store_source"] = "PlayerWorld.PersonPrivate"
        with self.assertRaises(ValueError): validate(x)

    def test_return_store_nearest_requires_matching_site(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_nearest_lexical_store_source"] = "NULL_LITERAL"
        with self.assertRaises(ValueError): validate(x)

    def test_nonzero_stores_cannot_claim_no_stores(self):
        x = good(); x["world_factory_return_metadata"]["factory_return_local_nearest_lexical_store_source"] = "NO_STORES"
        with self.assertRaises(ValueError): validate(x)

    def test_zero_stores_cannot_claim_other_nearest(self):
        x = good(); f=x["world_factory_return_metadata"]
        f["factory_return_local_lexical_store_sites"] = 0
        f["factory_return_local_store_derived_constructor"] = 0
        f["factory_return_local_store_other_or_unknown"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_direct_constructor_missing_must_reject_claimed_predecessor(self):
        x=good(); x["world_factory_return_metadata"]["factory_direct_derived_rgd_constructor_sites"]=0
        with self.assertRaises(ValueError): validate(x)

    def test_direct_typed_call_store_is_structural_not_real_save(self):
        x=good(); f=x["world_factory_return_metadata"]
        f["factory_return_local_store_derived_constructor"]=0
        f["factory_return_local_store_derived_call"]=1
        f["factory_direct_derived_rgd_returning_call_sites"]=1
        f["factory_return_local_nearest_lexical_store_source"]="DERIVED_CALL"
        report=validate(x)
        self.assertFalse(report["derived_RGD_runtime_value_initialized_proven"])
        self.assertFalse(report["Android_Unity_IL2CPP_phone_executed"])

    def test_direct_null_store_no_null_runtime_claim(self):
        x=good(); f=x["world_factory_return_metadata"]
        f["factory_return_local_store_derived_constructor"]=0
        f["factory_return_local_store_null_literal"]=1
        f["factory_return_local_nearest_lexical_store_source"]="NULL_LITERAL"
        report=validate(x)
        self.assertFalse(report["factory_control_flow_paths_or_runtime_values_proven"])

    def test_return_local_path_reachability_claim_rejected(self):
        x=good(); x["world_factory_return_metadata"]["factory_return_local_store_path_reachability_proven"]=True
        with self.assertRaises(ValueError): validate(x)

    def test_return_source_bool_not_allowed(self):
        x=good(); x["world_factory_return_metadata"]["factory_return_local_store_null_literal"]=False
        with self.assertRaises(ValueError): validate(x)

    def test_factory_original_return_partition_still_not_runtime_proof(self):
        out = validate(good())
        f = out["source_authentic_world_factory_return_site_categories"]
        self.assertEqual(f["factory_lexical_return_sites"], 2)
        self.assertFalse(out["factory_control_flow_paths_or_runtime_values_proven"])
        self.assertFalse(out["same_world_saved_or_reopened_proven"])

    def test_original_factory_direct_constructor_not_executed_proof(self):
        out = validate(good())
        f = out["source_authentic_world_factory_return_site_categories"]
        self.assertEqual(f["factory_direct_derived_rgd_constructor_sites"], 1)
        self.assertFalse(out["derived_RGD_runtime_value_initialized_proven"])

    def test_factory_no_returns_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_lexical_return_sites"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_factory_unaccounted_return_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_return_preceded_by_other_or_unknown"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_factory_oversubscribed_returns_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_return_preceded_by_derived_field"] = 2
        with self.assertRaises(ValueError): validate(x)

    def test_factory_bool_return_count_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_lexical_return_sites"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_factory_negative_return_count_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_conditional_branch_sites"] = -1
        with self.assertRaises(ValueError): validate(x)

    def test_factory_unbounded_return_count_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_conditional_branch_sites"] = 10001
        with self.assertRaises(ValueError): validate(x)

    def test_factory_missing_field_rejected(self):
        x = good()
        del x["world_factory_return_metadata"]["factory_null_literal_load_sites"]
        with self.assertRaises(ValueError): validate(x)

    def test_factory_private_member_name_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["private_method_name"] = "OriginalFactory"
        with self.assertRaises(ValueError): validate(x)

    def test_factory_branch_path_proof_rejected(self):
        x = good()
        x["world_factory_return_metadata"]["factory_all_return_paths_proven"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_factory_null_return_needs_null_literal(self):
        x = good()
        x["world_factory_return_metadata"]["factory_return_preceded_by_null_literal"] = 1
        x["world_factory_return_metadata"]["factory_return_preceded_by_other_or_unknown"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_factory_constructor_return_needs_constructor(self):
        x = good()
        x["world_factory_return_metadata"]["factory_return_preceded_by_derived_constructor"] = 1
        x["world_factory_return_metadata"]["factory_return_preceded_by_other_or_unknown"] = 0
        x["world_factory_return_metadata"]["factory_direct_derived_rgd_constructor_sites"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_factory_call_return_needs_call_site(self):
        x = good()
        x["world_factory_return_metadata"]["factory_return_preceded_by_derived_call"] = 1
        x["world_factory_return_metadata"]["factory_return_preceded_by_other_or_unknown"] = 0
        with self.assertRaises(ValueError): validate(x)

    def test_missing_original_factory_body_rejected(self):
        x = good()
        x["world_producer_compiled_method_body_found"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_missing_factory_metadata_rejected(self):
        x = good()
        del x["world_factory_return_metadata"]
        with self.assertRaises(ValueError): validate(x)

    def test_original_factory_metadata_string_rejected(self):
        x = good()
        x["world_factory_return_metadata"] = "private original bytes"
        with self.assertRaises(ValueError): validate(x)

    def test_multiple_lexical_return_sites_can_include_null_but_not_executed(self):
        x = good()
        f = x["world_factory_return_metadata"]
        f["factory_return_preceded_by_null_literal"] = 1
        f["factory_return_preceded_by_other_or_unknown"] = 0
        f["factory_null_literal_load_sites"] = 1
        out = validate(x)
        self.assertEqual(
            out["source_authentic_world_factory_return_site_categories"]["factory_return_preceded_by_null_literal"], 1)
        self.assertFalse(out["factory_control_flow_paths_or_runtime_values_proven"])

    def test_valid_context_remains_source_only(self):
        out = validate(good())
        self.assertEqual(out["world_producer_owner_scope"], "OTHER_ORIGINAL_CLASS")
        self.assertFalse(out["same_world_saved_or_reopened_proven"])
        self.assertFalse(out["derived_RGD_runtime_value_initialized_proven"])
        self.assertFalse(out["Android_Unity_IL2CPP_phone_executed"])

    def test_external_unresolved_scope_cannot_claim_original_factory_return_sites(self):
        # Earlier scope-only reports allowed unresolved producers. This experiment
        # now asserts lexical returns measured from an EXACT original body.
        x = good()
        x["world_producer_declaring_scope"] = "EXTERNAL_OR_UNRESOLVED"
        x["world_producer_compiled_method_body_found"] = False
        with self.assertRaisesRegex(ValueError, "factory_returns_without_exact_original_body"):
            validate(x)

    def test_external_scope_with_body_rejected(self):
        x = good()
        x["world_producer_declaring_scope"] = "EXTERNAL_OR_UNRESOLVED"
        with self.assertRaises(ValueError): validate(x)

    def test_same_class_scope_is_structural(self):
        x = good()
        x["world_producer_declaring_scope"] = "SAVEANDLOAD"
        self.assertFalse(validate(x)["derived_RGD_runtime_value_initialized_proven"])

    def test_one_argument_factory_allowed(self):
        x = good()
        x["world_producer_argument_count_category"] = "ONE"
        self.assertEqual(validate(x)["world_producer_arity"], "ONE")

    def test_multiple_argument_factory_allowed(self):
        x = good()
        x["world_producer_argument_count_category"] = "MULTIPLE"
        self.assertEqual(validate(x)["world_producer_arity"], "MULTIPLE")

    def test_instance_call_allowed(self):
        x = good()
        x["world_producer_invocation_kind"] = "INSTANCE_CALL"
        self.assertEqual(validate(x)["world_producer_invocation"], "INSTANCE_CALL")

    def test_no_private_method_name_allowed(self):
        x = good()
        x["world_producer_declaring_scope"] = "WorldManager.GeneratePrivateUserData"
        with self.assertRaises(ValueError): validate(x)

    def test_type_names_dont_leak(self):
        x = good()
        x["unknown_owner_type_name"] = "Private.WorldName"
        with self.assertRaises(ValueError): validate(x)

    def test_original_source_sha_is_mandatory(self):
        x = good()
        x["original_assembly_sha_verified"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_original_save_edge_is_mandatory(self):
        x = good()
        x["original_world_and_user_save_rgd_edges_verified"] = False
        with self.assertRaises(ValueError): validate(x)

    def test_source_kind_mandatory(self):
        x = good()
        x["scope"] = "SYNTHETIC_ORIGINAL"
        with self.assertRaises(ValueError): validate(x)

    def test_schema_must_be_number(self):
        x = good()
        x["schema"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_missing_user_writer_breakdown_rejected(self):
        x = good()
        del x["field_write_breakdown"]
        with self.assertRaises(ValueError): validate(x)

    def test_missing_source_bucket_rejected(self):
        x = good()
        del x["field_write_breakdown"]["user_field_write_immediate_unknown_or_other"]
        with self.assertRaises(ValueError): validate(x)

    def test_writer_sum_mismatch_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_field_writes_in_other_saveandload_methods"] = 1
        with self.assertRaises(ValueError): validate(x)

    def test_value_sum_mismatch_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_field_write_immediate_null_literals"] = 2
        with self.assertRaises(ValueError): validate(x)

    def test_writer_not_five_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_original_direct_write_sites"] = 2
        with self.assertRaises(ValueError): validate(x)

    def test_bool_site_counts_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_field_writes_in_saveworld"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_negative_counts_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_field_writes_in_saveworld"] = -1
        with self.assertRaises(ValueError): validate(x)

    def test_zero_initialized_not_proven_even_with_call_return(self):
        x = good()
        x["field_write_breakdown"]["user_field_write_immediate_derived_typed_values"] = 2
        x["field_write_breakdown"]["user_field_write_immediate_null_literals"] = 0
        self.assertFalse(validate(x)["derived_RGD_runtime_value_initialized_proven"])

    def test_fake_save_invoked_rejected(self):
        x = good()
        x["direct_game_save_invoked"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_world_initialized_rejected(self):
        x = good()
        x["actual_world_data_initialized"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_original_rgd_written_rejected(self):
        x = good()
        x["original_rgd_file_read_or_written"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_android_phone_rejected(self):
        x = good()
        x["android_unity_il2cpp_device_executed"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_control_flow_proven_rejected(self):
        x = good()
        x["derived_rgd_object_identity_or_control_flow_proven"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_fake_original_source_published_rejected(self):
        x = good()
        x["private_game_code_or_data_published"] = True
        with self.assertRaises(ValueError): validate(x)

    def test_bare_string_is_invalid(self):
        with self.assertRaises(ValueError): validate("null")

    def test_writer_not_dictionary(self):
        x = good()
        x["field_write_breakdown"] = []
        with self.assertRaises(ValueError): validate(x)

    def test_unknown_arity_private_method_rejected(self):
        x = good()
        x["world_producer_argument_count_category"] = "PrivateType"
        with self.assertRaises(ValueError): validate(x)

    def test_null_literal_site_is_not_runtime_null(self):
        x = good()
        x["field_write_breakdown"]["user_field_write_immediate_null_literals"] = 3
        x["field_write_breakdown"]["user_field_write_immediate_derived_typed_values"] = 0
        x["field_write_breakdown"]["user_field_write_immediate_unknown_or_other"] = 0
        self.assertFalse(validate(x)["derived_RGD_runtime_value_initialized_proven"])

    def test_invalid_original_writer_shape_rejected(self):
        x = good()
        x["field_write_breakdown"]["user_field_writes_in_saveworld"] = "0"
        with self.assertRaises(ValueError): validate(x)


if __name__ == "__main__":
    unittest.main()
