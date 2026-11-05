"""T4 LOCAL-005: reject fabricated original CIL SaveWorld/RGD provenance claims.

Reports counts/booleans only. An original CIL constructor and Save call
do not establish that the very same instance flowed into Save at runtime.
"""
import argparse
import json
from pathlib import Path

FIELDS = {
    "schema_version", "scope", "original_managed_dll_size_sha_verified",
    "original_saveandload_owner_unique", "original_saveworld_unique",
    "original_saveuser_unique", "original_private_save_rgd_signature_unique",
    "world_direct_calls_to_exact_save_rgd", "world_other_calls_named_save",
    "user_direct_calls_to_exact_save_rgd", "user_other_calls_named_save",
    "world_direct_rgd_constructor_calls", "user_direct_rgd_constructor_calls",
    "world_rgd_typed_locals", "user_rgd_typed_locals",
    "world_rgd_field_stores",
    "world_pre_call_rgd_source_clue", "user_pre_call_rgd_source_clue",
    "direct_constructor_is_dynamically_proven_save_argument",
    "original_save_method_invoked", "game_world_rgd_written_or_loaded",
    "source_or_rgd_payload_published", "android_unity_il2cpp_or_phone_executed",
}
PROVENANCE = (
    "original_managed_dll_size_sha_verified",
    "original_saveandload_owner_unique",
    "original_saveworld_unique",
    "original_saveuser_unique",
    "original_private_save_rgd_signature_unique",
)
NEGATIVE = (
    "direct_constructor_is_dynamically_proven_save_argument",
    "original_save_method_invoked",
    "game_world_rgd_written_or_loaded",
    "source_or_rgd_payload_published",
    "android_unity_il2cpp_or_phone_executed",
)
PRODUCER_CLUES = {
    "RGD_TYPED_INSTANCE_FIELD_LOAD", "RGD_TYPED_STATIC_FIELD_LOAD",
    "RGD_TYPED_CALL_RETURN", "RGD_TYPED_LOCAL_LOAD",
    "DIRECT_RGD_CONSTRUCTION", "UNKNOWN_PRECALL_SOURCE",
}

COUNTS = (
    "world_direct_calls_to_exact_save_rgd",
    "world_other_calls_named_save", "user_direct_calls_to_exact_save_rgd",
    "user_other_calls_named_save",
    "world_direct_rgd_constructor_calls", "user_direct_rgd_constructor_calls",
    "world_rgd_typed_locals", "user_rgd_typed_locals",
    "world_rgd_field_stores",
)


def validate(report):
    if not isinstance(report, dict) or set(report) != FIELDS:
        raise ValueError("unknown_original_il_contract")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("unrecognized_schema")
    if report["scope"] != "EXACT_ORIGINAL_COMPILED_IL_READ_ONLY":
        raise ValueError("missing_exact_original_provenance")
    if any(report[k] is not True for k in PROVENANCE):
        raise ValueError("unverified_compiled_original_methods")
    if any(report[k] is not False for k in NEGATIVE):
        raise ValueError("fabricated_dynamic_or_device_result")
    for key in COUNTS:
        x = report[key]
        if type(x) is not int or x < 0 or x > 100:
            raise ValueError("invalid_original_il_count")
    for label in ("world_pre_call_rgd_source_clue", "user_pre_call_rgd_source_clue"):
        if type(report[label]) is not str or report[label] not in PRODUCER_CLUES:
            raise ValueError("unrecognized_original_pre_call_argument_source")
    if report["world_direct_calls_to_exact_save_rgd"] != 1:
        raise ValueError("original_world_persistence_edge_unresolved")
    if report["world_other_calls_named_save"] != 0:
        raise ValueError("ambiguous_original_world_persistence_edge")
    return {
        "status": "EXACT_ORIGINAL_SAVEWORLD_RGD_IL_EDGE_MEASURED",
        "original_source_bytes_verified": True,
        "world_direct_save_rgd_call_count": 1,
        "world_direct_rgd_constructor_call_count":
            report["world_direct_rgd_constructor_calls"],
        "world_rgd_typed_local_count": report["world_rgd_typed_locals"],
        "world_rgd_field_store_count": report["world_rgd_field_stores"],
        "world_pre_call_rgd_source_clue": report["world_pre_call_rgd_source_clue"],
        "user_pre_call_rgd_source_clue": report["user_pre_call_rgd_source_clue"],
        "world_argument_construction_clue": (
            "DIRECT_RGD_CTOR_IN_SAVEWORLD"
            if report["world_direct_rgd_constructor_calls"] > 0
            else "NO_DIRECT_RGD_CTOR_IN_SAVEWORLD"
        ),
        "save_user_same_rgd_target_call_count":
            report["user_direct_calls_to_exact_save_rgd"],
        "save_user_other_save_call_count":
            report["user_other_calls_named_save"],
        "actual_argument_instance_identity_proven": False,
        "actual_save_invoked": False,
        "game_world_rgd_written_or_reloaded": False,
        "android_device_tested": False,
        "original_game_data_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        p = args.report
        if any(x.is_symlink() for x in (p, *p.parents)):
            raise ValueError("symlinked_report")
        if not p.is_file() or p.stat().st_size > 12000 or p.stat().st_nlink != 1:
            raise ValueError("unsafe_report")
        doc = json.loads(p.read_text(encoding="utf-8"),
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        result = validate(doc)
    except (ValueError, OSError, TypeError, UnicodeError):
        print("T4_ORIGINAL_RGD_PRODUCER_VALIDATION status=FAIL_CLOSED " +
              "original_il_or_game_data_logged=false")
        return 2
    print("T4_ORIGINAL_RGD_PRODUCER_VALIDATION " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
