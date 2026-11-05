"""Validate safe public conclusions from one genuine original shipped RGD deserialize.

This does not allow a .NET8 seed decode to be advertised as a Raft world save,
SaveAndLoad.Load<T> execution, native Android file read or IL2CPP acceptance.
"""
import argparse
import json
from pathlib import Path

FIELDS = {
    "schema_version", "source", "original_dll_sha_verified",
    "original_seed_sha_verified", "managed_reference_siblings",
    "original_CLR_assembly_loaded", "formatter_runtime",
    "actual_formatter_deserialize_attempted",
    "actual_formatter_deserialize_object_created",
    "deserialized_root_defined_in_original_dll",
    "bounded_runtime_category", "original_SaveAndLoad_LoadT_invoked",
    "user_generated_game_world_loaded", "real_game_rgd_write_or_roundtrip",
    "android_unity_il2cpp_or_phone_executed",
    "original_data_or_private_type_names_published",
}
ERRORS = {
    "NONE", "DESERIALIZED_NULL", "SERIALIZATION_OR_ORIGINAL_SCHEMA",
    "MANAGED_DEPENDENCY_MISSING", "MANAGED_DEPENDENCY_LOAD_FAILURE",
    "ORIGINAL_TYPE_LOAD_FAILURE", "ORIGINAL_METHOD_BINDING_UNAVAILABLE",
    "RUNTIME_PLATFORM_UNSUPPORTED", "RUNTIME_API_UNSUPPORTED",
    "ACCESS_DENIED", "RUNTIME_FILE_IO", "RESOURCE_LIMIT",
    "OTHER_ISOLATED_RUNTIME_ERROR",
}


def validate(report):
    if not isinstance(report, dict) or set(report) != FIELDS:
        raise ValueError("unknown_report_fields")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("report_schema_version")
    if report["source"] != "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED":
        raise ValueError("unverified_source")
    for key in ("original_dll_sha_verified", "original_seed_sha_verified",
                "original_CLR_assembly_loaded",
                "actual_formatter_deserialize_attempted"):
        if report[key] is not True:
            raise ValueError("original_input_or_execution_missing")
    if type(report["managed_reference_siblings"]) is not int or report["managed_reference_siblings"] != 151:
        raise ValueError("incomplete_managed_siblings")
    if report["formatter_runtime"] != "DOTNET8_BINARYFORMATTER":
        raise ValueError("unrecognized_formatter_runtime")
    for key in ("original_SaveAndLoad_LoadT_invoked",
                "user_generated_game_world_loaded",
                "real_game_rgd_write_or_roundtrip",
                "android_unity_il2cpp_or_phone_executed",
                "original_data_or_private_type_names_published"):
        if report[key] is not False:
            raise ValueError("false_game_or_native_success")
    success = report["actual_formatter_deserialize_object_created"]
    from_game = report["deserialized_root_defined_in_original_dll"]
    category = report["bounded_runtime_category"]
    if type(success) is not bool or type(from_game) is not bool:
        raise ValueError("untyped_formatter_result")
    if type(category) is not str or category not in ERRORS:
        raise ValueError("unknown_runtime_category")
    if (success and category != "NONE") or (not success and category == "NONE"):
        raise ValueError("contradictory_formatter_outcome")
    if from_game and not success:
        raise ValueError("uncreated_object_has_original_type")
    return {
        "status": "AUTHENTIC_ORIGINAL_SEED_CLR_DESERIALIZE_MEASURED",
        "original_rgd_seed_deserialized": success,
        "actual_original_type_instantiated": from_game,
        "runtime_category": category,
        "real_save_load_on_android_proven": False,
        "original_SaveAndLoad_LoadT_executed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    opts = parser.parse_args(argv)
    path = opts.report
    try:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("symlink")
        if not path.is_file() or path.stat().st_size > 12000 or path.stat().st_nlink != 1:
            raise ValueError("unsafe_report")
        report = json.loads(path.read_text(encoding="utf8"),
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        summary = validate(report)
    except (OSError, ValueError, TypeError, UnicodeError):
        print("T4_ORIGINAL_RGD_VALIDATION status=FAIL_CLOSED raw_original_data_logged=false")
        return 2
    print("T4_ORIGINAL_RGD_VALIDATION " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
