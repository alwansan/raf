"""T4 original SHA-pinned shipped RGD Save->Load experiment outcome verifier.

Never publish original CLR type/member names, original seed bytes, path, logs or
exception details. A fully successful CLR seed roundtrip is not a game save.
"""
import argparse
import json
from pathlib import Path

from scripts.t4_validate_original_rgd_loadt import LOADT_FIELDS

ADDITIONAL = {
    "original_private_Save_IL_guard_passed",
    "original_private_Save_safe_calls",
    "original_private_Save_invoked",
    "original_private_Save_output_created",
    "original_private_Save_output_nonzero",
    "original_private_Save_generated_LoadT_matching_root",
    "original_private_Save_isolated_temp_removed",
    "original_private_Save_result_category",
}
CATEGORIES = {
    "NONE", "ORIGINAL_ROOT_TYPE_UNAVAILABLE",
    "ORIGINAL_PRIVATE_SAVE_METHOD_IL_NOT_AUTHENTICATED",
    "ORIGINAL_SAVE_REFLECTION_SIGNATURE_MISMATCH",
    "GENUINE_SAVE_OR_LOAD_ROUNDTRIP_UNVERIFIED",
    "SERIALIZATION_OR_ORIGINAL_SCHEMA", "MANAGED_DEPENDENCY_MISSING",
    "MANAGED_DEPENDENCY_LOAD_FAILURE", "ORIGINAL_TYPE_LOAD_FAILURE",
    "ORIGINAL_METHOD_BINDING_UNAVAILABLE", "RUNTIME_PLATFORM_UNSUPPORTED",
    "RUNTIME_API_UNSUPPORTED", "ACCESS_DENIED", "RUNTIME_FILE_IO",
    "RESOURCE_LIMIT", "OTHER_ISOLATED_RUNTIME_ERROR",
}

def validate(doc):
    if not isinstance(doc, dict) or set(doc) != LOADT_FIELDS | ADDITIONAL:
        raise ValueError("unrecognized_original_save_report")
    if doc["schema_version"] != 1 or doc["source"] != "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED":
        raise ValueError("unverified_original_provenance")
    for k in ("original_dll_sha_verified", "original_seed_sha_verified",
              "original_CLR_assembly_loaded",
              "actual_formatter_deserialize_attempted",
              "actual_formatter_deserialize_object_created",
              "deserialized_root_defined_in_original_dll",
              "original_SaveAndLoad_LoadT_invoked",
              "original_LoadT_method_signature_verified",
              "original_LoadT_returned_matching_seed_type"):
        if doc[k] is not True:
            raise ValueError("missing_original_type_or_loader")
    if type(doc["managed_reference_siblings"]) is not int or doc["managed_reference_siblings"] != 151:
        raise ValueError("missing_original_managed_context")
    if doc["formatter_runtime"] != "DOTNET8_BINARYFORMATTER" or doc["bounded_runtime_category"] != "NONE" or doc["original_LoadT_result_category"] != "NONE":
        raise ValueError("original_seed_load_failed")
    for k in ("user_generated_game_world_loaded", "real_game_rgd_write_or_roundtrip",
              "android_unity_il2cpp_or_phone_executed",
              "original_data_or_private_type_names_published"):
        if doc[k] is not False:
            raise ValueError("fabricated_actual_world_or_phone")
    bools = ("original_private_Save_IL_guard_passed",
             "original_private_Save_invoked", "original_private_Save_output_created",
             "original_private_Save_output_nonzero",
             "original_private_Save_generated_LoadT_matching_root",
             "original_private_Save_isolated_temp_removed")
    if any(type(doc[k]) is not bool for k in bools):
        raise ValueError("invalid_original_save_boolean")
    calls = doc["original_private_Save_safe_calls"]
    if type(calls) is not int or not 0 <= calls <= 100:
        raise ValueError("invalid_original_save_guard_count")
    category = doc["original_private_Save_result_category"]
    if type(category) is not str or category not in CATEGORIES:
        raise ValueError("invalid_original_save_outcome_category")
    guard = doc["original_private_Save_IL_guard_passed"]
    invoked = doc["original_private_Save_invoked"]
    created = doc["original_private_Save_output_created"]
    nonzero = doc["original_private_Save_output_nonzero"]
    loaded = doc["original_private_Save_generated_LoadT_matching_root"]
    cleaned = doc["original_private_Save_isolated_temp_removed"]
    if invoked and not guard or nonzero and not created or loaded and not nonzero:
        raise ValueError("contradictory_guarded_serialization")
    if not guard and any((invoked, created, nonzero, loaded)):
        raise ValueError("unaudited_original_save_executed")
    if category == "NONE" and not all((guard, invoked, created, nonzero, loaded, cleaned)):
        raise ValueError("falsely_complete_original_save")
    if all((guard, invoked, created, nonzero, loaded, cleaned)) and category != "NONE":
        raise ValueError("contradictory_success_category")
    return {
        "status": "EXACT_ORIGINAL_RGD_SEED_PRIVATE_SAVE_PATH_MEASURED",
        "original_private_Save_IL_guard_passed": guard,
        "original_private_Save_invoked": invoked,
        "original_private_Save_output_nonzero": nonzero,
        "generated_original_seed_LoadT_same_type": loaded,
        "temp_cleanup_proven": cleaned,
        "bounded_result_category": category,
        "user_world_save_or_relaunch_proven": False,
        "Android_Unity_IL2CPP_device_executed": False,
        "private_data_published": False,
    }

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, required=True)
    opts = p.parse_args(argv)
    try:
        path = opts.report
        if any(x.is_symlink() for x in (path, *path.parents)):
            raise ValueError("report_symlink")
        if not path.is_file() or path.stat().st_size > 12000 or path.stat().st_nlink != 1:
            raise ValueError("untrusted_original_report")
        report = json.loads(path.read_text(encoding="utf8"),
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        result = validate(report)
    except (OSError, ValueError, UnicodeError, TypeError):
        print("T4_ORIGINAL_RGD_SAVE_ROUNDTRIP status=UNTRUSTED_RESULT raw_game_data_published=false")
        return 2
    print("T4_ORIGINAL_RGD_SAVE_ROUNDTRIP " + json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
