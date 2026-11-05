"""T4 LOCAL-005: strict source-free verifier for SHA-authentic original RGD pre-call metadata.

A structural predecessor is not an executed producer or proof of the value
actually forwarded at runtime. Never print raw original types, IL or paths.
"""
import argparse
import json
from pathlib import Path

PREFIXES = ("FIELD", "FIELD_ADDRESS", "CONSTRUCTOR", "CAST", "BOX",
            "CALL_RETURN", "LOCAL")
RELATIONS = ("EXACT_RGD", "DERIVED_RGD", "OTHER_OR_UNRESOLVED")
SINGLE = {
    "NULL_LITERAL", "DUP_PREVIOUS_STACK", "BRANCH_PREVIOUS_STACK",
    "ARGUMENT_PUSH", "ARRAY_REF_LOAD", "STRING_LITERAL",
    "OTHER_PRECALL", "UNKNOWN_PRECALL",
}
CLASSES = SINGLE | {f"{prefix}_{rel}" for prefix in PREFIXES
                    for rel in RELATIONS}
FIELDS = {
    "schema_version", "source_kind", "original_assembly_sha_verified",
    "original_private_RGD_class_verified",
    "saveworld_exact_original_private_save_edge",
    "saveuser_exact_original_private_save_edge",
    "world_precall_type_class", "user_precall_type_class",
    "original_save_executed", "original_RGD_created_or_read",
    "original_game_source_or_payload_published",
    "Android_Unity_IL2CPP_or_device_executed",
    "dynamic_argument_identity_proven",
}
REQUIRED = (
    "original_assembly_sha_verified", "original_private_RGD_class_verified",
    "saveworld_exact_original_private_save_edge",
    "saveuser_exact_original_private_save_edge",
)
FORBIDDEN = (
    "original_save_executed", "original_RGD_created_or_read",
    "original_game_source_or_payload_published",
    "Android_Unity_IL2CPP_or_device_executed",
    "dynamic_argument_identity_proven",
)


def validate(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError("unrecognized_original_pre_call_contract")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("bad_schema")
    if data["source_kind"] != "PINNED_ORIGINAL_READONLY_IL":
        raise ValueError("source_not_exact_original")
    if any(data[key] is not True for key in REQUIRED):
        raise ValueError("unauthenticated_original_compiled_edge")
    if any(data[key] is not False for key in FORBIDDEN):
        raise ValueError("fabricated_runtime_or_device_proof")
    for key in ("world_precall_type_class", "user_precall_type_class"):
        if type(data[key]) is not str or data[key] not in CLASSES:
            raise ValueError("unrecognized_or_private_original_il_detail")
    return {
        "status": "PINNED_ORIGINAL_RGD_PRECALL_CLASSIFICATION_ONLY",
        "original_assembly_sha_verified": True,
        "world_precall_class": data["world_precall_type_class"],
        "user_precall_class": data["user_precall_type_class"],
        "exact_original_RGD_save_edges_present": True,
        "argument_value_origin_proven": False,
        "gameplay_save_rgd_written_or_reopened": False,
        "unity_android_il2cpp_or_phone_executed": False,
        "original_game_source_or_payload_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        p = args.report
        if any(a.is_symlink() for a in (p, *p.parents)):
            raise ValueError("symlinked_report")
        if not p.is_file() or p.stat().st_size > 12000 or p.stat().st_nlink != 1:
            raise ValueError("unsafe_report")
        raw = json.loads(p.read_text(encoding="utf-8"),
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        result = validate(raw)
    except (ValueError, OSError, UnicodeError, TypeError):
        print("T4_RGD_PRECALL_VERIFICATION status=FAIL_CLOSED original_details_logged=false")
        return 2
    print("T4_RGD_PRECALL_VERIFICATION " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
