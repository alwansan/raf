"""Strict, privacy-safe verifier for exact CL@520c owner-world original CLR Save→Load.

Only seven immutable Git-blob-authenticated world RGD samples are accepted by
the private .NET probe. This verifier prints no original types, paths or bytes.
No successful CLR Save/Load proves Unity/IL2CPP or same-world phone relaunch.
"""
import argparse
import json
from pathlib import Path

FIELDS = frozenset({
    "schema_version", "source", "original_dll_sha_verified",
    "owner_world_git_blob_verified", "managed_reference_siblings",
    "original_CLR_assembly_loaded", "formatter_runtime",
    "actual_formatter_deserialize_attempted",
    "actual_formatter_deserialize_object_created",
    "deserialized_root_defined_in_original_dll", "bounded_runtime_category",
    "original_SaveAndLoad_LoadT_invoked", "user_generated_game_world_loaded",
    "real_game_rgd_write_or_roundtrip", "android_unity_il2cpp_or_phone_executed",
    "original_data_or_private_type_names_published",
    "original_LoadT_method_signature_verified",
    "original_LoadT_returned_matching_seed_type", "original_LoadT_result_category",
    "original_private_Save_IL_guard_passed", "original_private_Save_safe_calls",
    "original_private_Save_audit_category", "original_private_Save_invoked",
    "original_private_Save_output_created", "original_private_Save_output_nonzero",
    "original_private_Save_generated_LoadT_matching_root",
    "original_private_Save_fresh_CLR_child_attempted",
    "original_private_Save_fresh_CLR_child_LoadT_matching_root",
    "original_private_Save_private_wire_compared",
    "original_private_Save_private_wire_identical",
    "original_private_Save_isolated_temp_removed",
    "original_private_Save_result_category",
    "original_isolated_owner_world_roundtrip_verified",
    "android_saved_world_or_player_progress_verified",
})
CATEGORIES = frozenset({
    "NONE", "ORIGINAL_ROOT_TYPE_UNAVAILABLE", "NOT_AUDITED",
    "NO_EXACT_PRIVATE_SAVE_SIGNATURE",
    "ORIGINAL_SAVE_CLASS_IDENTITY_MISSING",
    "ORIGINAL_SAVE_PRIVATE_SIGNATURE_SHAPE_MISSING",
    "OWNER_WORLD_ROOT_NOT_ASSIGNABLE_TO_ORIGINAL_RGD_SAVE_ARGUMENT",
    "ORIGINAL_SAVE_ARGUMENT_DIFFERS_FROM_OWNER_WORLD_ROOT",
    "UNEXPECTED_ORIGINAL_SAVE_IL_COMPLEXITY",
    "UNEXPECTED_ORIGINAL_SAVE_EXCEPTION_REGION",
    "ORIGINAL_SAVE_FIELD_OR_INDIRECT_ACCESS",
    "UNKNOWN_ORIGINAL_SAVE_CALL_OPERAND",
    "UNKNOWN_ORIGINAL_SAVE_CATCH_CALLEE",
    "UNKNOWN_ORIGINAL_SAVE_SUCCESS_CALLEE",
    "ORIGINAL_SAVE_EXPECTED_CREATE_OR_SERIALIZE_MISSING",
    "ORIGINAL_SAVE_REFLECTION_SIGNATURE_MISMATCH",
    "GENUINE_SAVE_OR_LOAD_ROUNDTRIP_UNVERIFIED",
    "SERIALIZATION_OR_ORIGINAL_SCHEMA",
    "MANAGED_DEPENDENCY_MISSING",
    "MANAGED_DEPENDENCY_LOAD_FAILURE",
    "ORIGINAL_TYPE_LOAD_FAILURE",
    "ORIGINAL_METHOD_BINDING_UNAVAILABLE",
    "RUNTIME_PLATFORM_UNSUPPORTED",
    "RUNTIME_API_UNSUPPORTED",
    "ACCESS_DENIED",
    "RUNTIME_FILE_IO",
    "RESOURCE_LIMIT",
    "OTHER_ISOLATED_RUNTIME_ERROR",
})
SAFE_BOOL_TRUE = (
    "original_dll_sha_verified", "owner_world_git_blob_verified",
    "original_CLR_assembly_loaded", "actual_formatter_deserialize_attempted",
    "actual_formatter_deserialize_object_created",
    "deserialized_root_defined_in_original_dll",
    "original_SaveAndLoad_LoadT_invoked",
    "original_LoadT_method_signature_verified",
    "original_LoadT_returned_matching_seed_type",
)
SAFE_BOOL_FALSE = (
    "user_generated_game_world_loaded", "real_game_rgd_write_or_roundtrip",
    "android_unity_il2cpp_or_phone_executed",
    "original_data_or_private_type_names_published",
    "android_saved_world_or_player_progress_verified",
)
SAVE_BOOLEANS = (
    "original_private_Save_IL_guard_passed", "original_private_Save_invoked",
    "original_private_Save_output_created", "original_private_Save_output_nonzero",
    "original_private_Save_generated_LoadT_matching_root",
    "original_private_Save_fresh_CLR_child_attempted",
    "original_private_Save_fresh_CLR_child_LoadT_matching_root",
    "original_private_Save_private_wire_compared",
    "original_private_Save_private_wire_identical",
    "original_private_Save_isolated_temp_removed",
    "original_isolated_owner_world_roundtrip_verified",
)


def validate(document: dict) -> dict:
    if type(document) is not dict or set(document) != FIELDS:
        raise ValueError("unexpected_original_owner_report_fields")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("invalid_report_version")
    if document["source"] != "IMMUTABLE_SHA_VERIFIED_OWNER5NOV_WORLD_RGD":
        raise ValueError("wrong_owner_source")
    if (type(document["managed_reference_siblings"]) is not int or
            document["managed_reference_siblings"] != 151):
        raise ValueError("wrong_original_companions")
    if (document["formatter_runtime"] != "DOTNET8_BINARYFORMATTER" or
            document["bounded_runtime_category"] != "NONE" or
            document["original_LoadT_result_category"] != "NONE"):
        raise ValueError("real_original_world_load_failed")
    for key in SAFE_BOOL_TRUE:
        if document[key] is not True:
            raise ValueError("missing_authenticated_original_load")
    for key in SAFE_BOOL_FALSE:
        if document[key] is not False:
            raise ValueError("false_android_or_world_proof")
    if any(type(document[key]) is not bool for key in SAVE_BOOLEANS):
        raise ValueError("invalid_save_boolean")
    calls = document["original_private_Save_safe_calls"]
    if type(calls) is not int or not 0 <= calls <= 100:
        raise ValueError("invalid_original_audit_bounds")
    audit = document["original_private_Save_audit_category"]
    category = document["original_private_Save_result_category"]
    if type(audit) is not str or audit not in CATEGORIES:
        raise ValueError("unsafe_original_il_category")
    if type(category) is not str or category not in CATEGORIES:
        raise ValueError("unsafe_save_result_category")
    guard = document["original_private_Save_IL_guard_passed"]
    invoked = document["original_private_Save_invoked"]
    created = document["original_private_Save_output_created"]
    nonzero = document["original_private_Save_output_nonzero"]
    matched = document["original_private_Save_generated_LoadT_matching_root"]
    wire_compared = document["original_private_Save_private_wire_compared"]
    wire_identical = document["original_private_Save_private_wire_identical"]
    cleaned = document["original_private_Save_isolated_temp_removed"]
    isolated = document["original_isolated_owner_world_roundtrip_verified"]
    fresh_attempted = document["original_private_Save_fresh_CLR_child_attempted"]
    fresh_loaded = document["original_private_Save_fresh_CLR_child_LoadT_matching_root"]
    if (guard and audit != "NONE") or (not guard and audit == "NONE"):
        raise ValueError("audit_guard_inconsistent")
    if (invoked and not guard or created and not guard or
            nonzero and not created or matched and not nonzero or
            isolated != matched):
        raise ValueError("impossible_original_save_event")
    if not guard and any((invoked, created, nonzero, matched, cleaned, isolated,
                          wire_compared, wire_identical)):
        raise ValueError("original_method_invoked_without_preflight")
    if (wire_compared and not nonzero or wire_identical and not wire_compared or
            matched and not wire_compared):
        raise ValueError("impossible_original_wire_comparison")
    if (fresh_loaded and not fresh_attempted or fresh_attempted and not all(
            (guard, invoked, created, nonzero, matched, wire_identical))):
        raise ValueError("impossible_fresh_clr_child_evidence")
    if category == "NONE" and not all((guard, invoked, created, nonzero, matched, cleaned)):
        raise ValueError("fabricated_complete_roundtrip")
    if all((guard, invoked, created, nonzero, matched, cleaned)) and category != "NONE":
        raise ValueError("contradictory_success")
    if matched and not cleaned:
        raise ValueError("original_temp_data_not_cleaned")
    return {
        "original_Save_IL_guard_passed": guard,
        "original_private_Save_invoked": invoked,
        "original_temp_file_nonzero": nonzero,
        "original_generated_LoadT_matching": matched,
        "original_wire_compared": wire_compared,
        "original_wire_identical": wire_identical,
        "original_fresh_CLR_child_executed": fresh_attempted,
        "original_fresh_CLR_generated_LoadT_matching": fresh_loaded,
        "original_temporary_files_removed": cleaned,
        "Save_audit_category": audit,
        "Save_result_category": category,
        "native_android_verified": False,
        "phone_world_save_reopen_verified": False,
        "raw_game_data_published": False,
    }


def read_private_report(path: Path) -> dict:
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("private_report_symlink")
    if (not path.is_file() or path.stat().st_size > 12000 or
            path.stat().st_nlink != 1):
        raise ValueError("untrusted_private_report")
    doc = json.loads(path.read_text(encoding="utf-8"),
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    return validate(doc)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = read_private_report(args.report)
    except (ValueError, OSError, TypeError, UnicodeError):
        print("T4_OWNER_RGD_GUARDED_SAVE status=INVALID_REPORT " +
              "private_data_published=false")
        return 2
    print("T4_OWNER_RGD_GUARDED_SAVE " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
