"""T4 LOCAL-005: source-free, privacy-preserving original derived-RGD initializer context.

Only bounded metadata categories from exact original SHA. Never accept a claim
about runtime branch execution, real RGD contents, device, or player/world state.
"""
import argparse
import json
from pathlib import Path

SCOPE = {"SAVEANDLOAD", "OTHER_ORIGINAL_CLASS", "EXTERNAL_OR_UNRESOLVED"}
ARITY = {"ZERO", "ONE", "MULTIPLE"}
KIND = {"INSTANCE_CALL", "STATIC_CALL"}
FACTORY_RETURN_LOCAL_FIELDS = (
    "factory_return_local_lexical_store_sites",
    "factory_return_local_store_null_literal",
    "factory_return_local_store_derived_constructor",
    "factory_return_local_store_derived_call",
    "factory_return_local_store_derived_local",
    "factory_return_local_store_derived_field",
    "factory_return_local_store_other_or_unknown",
    "factory_return_local_nearest_lexical_store_source",
    "factory_return_local_store_path_reachability_proven",
)
FACTORY_RETURN_LOCAL_PARTITION = (
    "factory_return_local_store_null_literal",
    "factory_return_local_store_derived_constructor",
    "factory_return_local_store_derived_call",
    "factory_return_local_store_derived_local",
    "factory_return_local_store_derived_field",
    "factory_return_local_store_other_or_unknown",
)
FACTORY_STORE_CATEGORIES = {
    "NULL_LITERAL", "DERIVED_CONSTRUCTOR", "DERIVED_CALL",
    "DERIVED_LOCAL", "DERIVED_FIELD", "OTHER_OR_UNKNOWN", "NO_STORES",
}

FACTORY_FIELDS = (
    "factory_lexical_return_sites",
    "factory_return_preceded_by_null_literal",
    "factory_return_preceded_by_derived_local",
    "factory_return_preceded_by_derived_field",
    "factory_return_preceded_by_derived_call",
    "factory_return_preceded_by_derived_constructor",
    "factory_return_preceded_by_other_or_unknown",
    "factory_derived_rgd_local_slot_count",
    "factory_direct_derived_rgd_constructor_sites",
    "factory_direct_derived_rgd_returning_call_sites",
    "factory_conditional_branch_sites",
    "factory_throw_or_rethrow_sites",
    "factory_null_literal_load_sites",
    "factory_all_return_paths_proven",
    *FACTORY_RETURN_LOCAL_FIELDS,
)
FACTORY_RETURN_PARTITION = (
    "factory_return_preceded_by_null_literal",
    "factory_return_preceded_by_derived_local",
    "factory_return_preceded_by_derived_field",
    "factory_return_preceded_by_derived_call",
    "factory_return_preceded_by_derived_constructor",
    "factory_return_preceded_by_other_or_unknown",
)

WRITE_KEYS = (
    "user_original_direct_write_sites",
    "user_field_writes_in_instance_constructor",
    "user_field_writes_in_static_constructor",
    "user_field_writes_in_saveworld",
    "user_field_writes_in_saveuser",
    "user_field_writes_in_other_saveandload_methods",
    "user_field_writes_in_other_original_types",
    "user_field_write_immediate_null_literals",
    "user_field_write_immediate_derived_typed_values",
    "user_field_write_immediate_unknown_or_other",
)
MUST_TRUE = (
    "original_assembly_sha_verified",
    "original_world_and_user_save_rgd_edges_verified",
)
MUST_FALSE = (
    "direct_game_save_invoked",
    "actual_world_data_initialized",
    "original_rgd_file_read_or_written",
    "android_unity_il2cpp_device_executed",
    "derived_rgd_object_identity_or_control_flow_proven",
    "private_game_code_or_data_published",
)
TOP = {
    "schema", "scope",
    "original_assembly_sha_verified",
    "original_world_and_user_save_rgd_edges_verified",
    "world_producer_declaring_scope",
    "world_producer_argument_count_category",
    "world_producer_invocation_kind",
    "world_producer_compiled_method_body_found",
    "field_write_breakdown", "world_factory_return_metadata", *MUST_FALSE
}


def validate(result):
    if not isinstance(result, dict) or set(result) != TOP:
        raise ValueError("unknown_original_RGD_context_report")
    if type(result["schema"]) is not int or result["schema"] != 1:
        raise ValueError("wrong_report_version")
    if result["scope"] != "PINNED_ORIGINAL_READONLY_IL_CLASSIFICATION":
        raise ValueError("unknown_original_source_scope")
    if any(result[key] is not True for key in MUST_TRUE):
        raise ValueError("original_source_or_edge_unverified")
    if any(result[key] is not False for key in MUST_FALSE):
        raise ValueError("fabricated_runtime_or_device_acceptance")
    if type(result["world_producer_compiled_method_body_found"]) is not bool:
        raise ValueError("invalid_method_body_evidence")
    if result["world_producer_declaring_scope"] not in SCOPE:
        raise ValueError("unknown_producer_scope")
    if result["world_producer_argument_count_category"] not in ARITY:
        raise ValueError("unknown_producer_arity")
    if result["world_producer_invocation_kind"] not in KIND:
        raise ValueError("unknown_producer_invocation")
    if (result["world_producer_declaring_scope"] == "EXTERNAL_OR_UNRESOLVED"
            and result["world_producer_compiled_method_body_found"]):
        raise ValueError("external_method_cannot_claim_pinned_original_body")
    factory = result["world_factory_return_metadata"]
    if not isinstance(factory, dict) or set(factory) != set(FACTORY_FIELDS):
        raise ValueError("unknown_original_factory_return_contract")
    for key in FACTORY_FIELDS:
        if key in ("factory_all_return_paths_proven",
                   "factory_return_local_store_path_reachability_proven"):
            if factory[key] is not False:
                raise ValueError("fabricated_control_flow_path_proof")
            continue
        if key == "factory_return_local_nearest_lexical_store_source":
            if type(factory[key]) is not str or factory[key] not in FACTORY_STORE_CATEGORIES:
                raise ValueError("invalid_original_return_local_source_class")
            continue
        if type(factory[key]) is not int or not 0 <= factory[key] <= 10000:
            raise ValueError("invalid_original_factory_site_count")
    returns = factory["factory_lexical_return_sites"]
    if returns == 0 or sum(factory[k] for k in FACTORY_RETURN_PARTITION) != returns:
        raise ValueError("unaccounted_original_factory_lexical_return")
    if result["world_producer_compiled_method_body_found"] is not True:
        raise ValueError("factory_returns_without_exact_original_body")
    if (factory["factory_return_preceded_by_null_literal"] >
            factory["factory_null_literal_load_sites"]):
        raise ValueError("null_return_without_literal_site")
    if (factory["factory_return_preceded_by_derived_constructor"] >
            factory["factory_direct_derived_rgd_constructor_sites"]):
        raise ValueError("constructor_return_without_constructor")
    if (factory["factory_return_preceded_by_derived_call"] >
            factory["factory_direct_derived_rgd_returning_call_sites"]):
        raise ValueError("call_return_without_call_site")
    store_sites = factory["factory_return_local_lexical_store_sites"]
    if sum(factory[k] for k in FACTORY_RETURN_LOCAL_PARTITION) != store_sites:
        raise ValueError("original_return_local_unaccounted_stores")
    if store_sites == 0 and factory["factory_return_local_nearest_lexical_store_source"] != "NO_STORES":
        raise ValueError("fabricated_nearest_store_without_writes")
    if store_sites > 0 and factory["factory_return_local_nearest_lexical_store_source"] == "NO_STORES":
        raise ValueError("missing_nearest_store_with_writes")
    if store_sites == 0 and any(factory[k] for k in FACTORY_RETURN_LOCAL_PARTITION):
        raise ValueError("missing_original_local_store_site")
    nearest_to_key = {
        "NULL_LITERAL": "factory_return_local_store_null_literal",
        "DERIVED_CONSTRUCTOR": "factory_return_local_store_derived_constructor",
        "DERIVED_CALL": "factory_return_local_store_derived_call",
        "DERIVED_LOCAL": "factory_return_local_store_derived_local",
        "DERIVED_FIELD": "factory_return_local_store_derived_field",
        "OTHER_OR_UNKNOWN": "factory_return_local_store_other_or_unknown",
    }
    nearest = factory["factory_return_local_nearest_lexical_store_source"]
    if nearest in nearest_to_key and factory[nearest_to_key[nearest]] < 1:
        raise ValueError("nearest_source_without_matching_store_site")
    if (factory["factory_return_local_store_derived_constructor"] >
            factory["factory_direct_derived_rgd_constructor_sites"] or
            factory["factory_return_local_store_derived_call"] >
            factory["factory_direct_derived_rgd_returning_call_sites"]):
        raise ValueError("typed_immediate_producer_without_original_site")
    b = result["field_write_breakdown"]
    if not isinstance(b, dict) or set(b) != set(WRITE_KEYS):
        raise ValueError("unrecognized_field_writer_contract")
    for key in WRITE_KEYS:
        if type(b[key]) is not int or b[key] < 0 or b[key] > 3:
            raise ValueError("invalid_original_field_site_count")
    if b["user_original_direct_write_sites"] != 3:
        raise ValueError("original_saveuser_field_site_contract_drift")
    method_sum = sum(b[k] for k in (
        "user_field_writes_in_instance_constructor",
        "user_field_writes_in_static_constructor",
        "user_field_writes_in_saveworld",
        "user_field_writes_in_saveuser",
        "user_field_writes_in_other_saveandload_methods",
        "user_field_writes_in_other_original_types",
    ))
    source_sum = sum(b[k] for k in (
        "user_field_write_immediate_null_literals",
        "user_field_write_immediate_derived_typed_values",
        "user_field_write_immediate_unknown_or_other",
    ))
    if method_sum != 3 or source_sum != 3:
        raise ValueError("incomplete_or_conflicting_original_writer_site_partition")

    return {
        "status": "ORIGINAL_DERIVED_RGD_PRODUCER_CONTEXT_MEASURED_ONLY",
        "original_managed_assembly_sha_verified": True,
        "world_producer_owner_scope": result["world_producer_declaring_scope"],
        "world_producer_arity": result["world_producer_argument_count_category"],
        "world_producer_invocation": result["world_producer_invocation_kind"],
        "world_producer_original_method_body_exists":
            result["world_producer_compiled_method_body_found"],
        "source_authentic_world_factory_return_site_categories": {
            key: factory[key] for key in FACTORY_FIELDS
            if key not in ("factory_all_return_paths_proven",
                           "factory_return_local_store_path_reachability_proven")
        },
        "factory_control_flow_paths_or_runtime_values_proven": False,
        "saveuser_direct_writer_method_categories": {
            key: b[key] for key in (
                "user_field_writes_in_instance_constructor",
                "user_field_writes_in_static_constructor",
                "user_field_writes_in_saveworld",
                "user_field_writes_in_saveuser",
                "user_field_writes_in_other_saveandload_methods",
                "user_field_writes_in_other_original_types",
            )
        },
        "saveuser_lexical_writer_value_categories": {
            key: b[key] for key in (
                "user_field_write_immediate_null_literals",
                "user_field_write_immediate_derived_typed_values",
                "user_field_write_immediate_unknown_or_other",
            )
        },
        "same_world_saved_or_reopened_proven": False,
        "derived_RGD_runtime_value_initialized_proven": False,
        "Android_Unity_IL2CPP_phone_executed": False,
        "original_game_payload_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        p = args.report
        if any(a.is_symlink() for a in (p, *p.parents)):
            raise ValueError("linked_report")
        if (not p.is_file() or p.stat().st_size > 12000 or
                p.stat().st_nlink != 1):
            raise ValueError("unsafe_private_report")
        result = validate(json.loads(
            p.read_text(encoding="utf-8"),
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()),
        ))
    except (ValueError, OSError, TypeError, UnicodeError):
        print("T4_ORIGINAL_RGD_CONTEXT_VERIFICATION status=FAIL_CLOSED "
              "private_game_data_logged=false")
        return 2
    print("T4_ORIGINAL_RGD_CONTEXT_VERIFICATION " + json.dumps(
        result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
