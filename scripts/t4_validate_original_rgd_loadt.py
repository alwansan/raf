"""Verify actual ORIGINAL SaveAndLoad.Load<T> result on one pinned shipped RGD seed.

A seed deserialized by original CLR code does not prove a user-saved world or
Android native/Unity process restart. No private original CLR type is exported.
"""
import argparse
import json
from pathlib import Path

from scripts.t4_validate_original_rgd_runtime_load import ERRORS, FIELDS

LOADT_FIELDS = FIELDS | {
    "original_LoadT_method_signature_verified",
    "original_LoadT_returned_matching_seed_type",
    "original_LoadT_result_category",
}
LOADT_CATEGORIES = ERRORS | {
    "RETURNED_DEFAULT_OR_NONMATCHING_TYPE",
    "ORIGINAL_METHOD_BINDING_UNAVAILABLE",
    "ORIGINAL_ROOT_TYPE_UNAVAILABLE",
}


def validate(report):
    if not isinstance(report, dict) or set(report) != LOADT_FIELDS:
        raise ValueError("unrecognized_original_LoadT_report")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1 or (
            report["source"] != "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED"):
        raise ValueError("unverified_original_RGD_source")
    for key in ("original_dll_sha_verified", "original_seed_sha_verified",
                "original_CLR_assembly_loaded",
                "actual_formatter_deserialize_attempted",
                "actual_formatter_deserialize_object_created",
                "deserialized_root_defined_in_original_dll",
                "original_LoadT_method_signature_verified",
                "original_SaveAndLoad_LoadT_invoked"):
        if report[key] is not True:
            raise ValueError("missing_authentic_original_loader_execution")
    if type(report["managed_reference_siblings"]) is not int or (
            report["managed_reference_siblings"] != 151):
        raise ValueError("missing_authentic_reference_context")
    if report["formatter_runtime"] != "DOTNET8_BINARYFORMATTER" or (
            report["bounded_runtime_category"] != "NONE"):
        raise ValueError("direct_original_RGD_seed_failed_before_loader")
    for key in ("user_generated_game_world_loaded", "real_game_rgd_write_or_roundtrip",
                "android_unity_il2cpp_or_phone_executed",
                "original_data_or_private_type_names_published"):
        if report[key] is not False:
            raise ValueError("fabricated_android_or_gameplay_evidence")
    result = report["original_LoadT_returned_matching_seed_type"]
    category = report["original_LoadT_result_category"]
    if type(result) is not bool or type(category) is not str or (
            category not in LOADT_CATEGORIES):
        raise ValueError("invalid_original_loader_result")
    if (result and category != "NONE") or (not result and category == "NONE"):
        raise ValueError("contradictory_original_loader_result")
    return {
        "status": "ACTUAL_ORIGINAL_LOADT_SHIPPED_RGD_MEASURED",
        "original_SaveAndLoad_LoadT_invoked": True,
        "actual_original_RGD_root_returned": result,
        "bounded_original_loader_category": category,
        "game_world_playability_proven": False,
        "android_process_relaunch_or_RGD_roundtrip_proven": False,
        "original_private_data_published": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, required=True)
    opts = p.parse_args(argv)
    path = opts.report
    try:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("linked_report")
        if not path.is_file() or path.stat().st_size > 12000 or path.stat().st_nlink != 1:
            raise ValueError("unsafe_report")
        report = json.loads(path.read_text(encoding="utf8"),
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        summary = validate(report)
    except (OSError, ValueError, TypeError, UnicodeError):
        print("T4_ORIGINAL_LOADT_VALIDATION status=FAIL_CLOSED private_data_logged=false")
        return 2
    print("T4_ORIGINAL_LOADT_VALIDATION " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
