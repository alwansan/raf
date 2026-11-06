"""Fail-closed source-only validator for a SHA-pinned original Settings parameter probe.

The category is a narrow original compiled IL type classification, NOT proof
of a Unity UI event callback, saved preference, or Android render-scale option.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TOP = {
    "schema_version", "original_assembly_sha256_verified", "original_assembly_bytes",
    "compiled_original_il", "original_method_and_type_identifiers_private", "report",
    "serialized_unity_event_callback_proven",
    "persisted_android_render_resolution_proven",
    "original_game_modified", "android_device_tested",
}
R_NUMERIC = {
    "original_settings_method_bodies", "apply_definitions", "apply_direct_call_sites",
    "distinct_apply_caller_methods", "zero_parameter_caller_count",
    "one_parameter_caller_count", "one_parameter_caller_direct_dropdown_api_calls",
    "one_parameter_caller_dropdown_field_reference_sites",
    "one_parameter_caller_direct_dropdown_value_get_sites",
    "one_parameter_caller_direct_dropdown_value_set_sites",
    "one_parameter_caller_direct_dropdown_refresh_sites",
    "one_parameter_caller_direct_dropdown_onvaluechanged_get_sites",
    "one_parameter_caller_direct_addlistener_sites",
    "one_parameter_caller_direct_playerprefs_write_sites",
    "one_parameter_caller_direct_screen_setresolution_sites",
    "one_parameter_caller_direct_resizebuffers_sites",
    "class_direct_addlistener_sites",
    "class_direct_dropdown_onvaluechanged_get_sites",
}
R_BOOL = {
    "one_parameter_caller_is_static", "one_parameter_caller_is_public",
    "one_parameter_caller_is_private", "one_parameter_caller_is_virtual",
    "one_parameter_caller_returns_void",
    "unity_serialized_onvaluechanged_binding_proven",
    "persistent_android_render_scale_binding_proven", "android_device_tested",
}
CATEGORIES = {
    "by_reference", "array", "generic_instance", "generic_parameter",
    "system_int32", "system_boolean", "system_string", "system_float",
    "unity_screen_resolution", "unity_ui_dropdown", "tmp_dropdown",
    "unity_ui_other", "unity_engine_other", "system_other",
    "custom_value_type_or_enum", "custom_reference_type",
}


def no_duplicates(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("Duplicate JSON field")
        result[k] = v
    return result


def verify(data):
    if type(data) is not dict or set(data) != TOP:
        raise ValueError("Unexpected report schema")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Schema revision mismatch")
    if type(data["original_assembly_bytes"]) is not int or data["original_assembly_bytes"] != 3211776:
        raise ValueError("Wrong original assembly bytes")
    for field in ("original_assembly_sha256_verified", "compiled_original_il",
                  "original_method_and_type_identifiers_private"):
        if data[field] is not True:
            raise ValueError("Original proof boundary not met")
    for field in ("serialized_unity_event_callback_proven",
                  "persisted_android_render_resolution_proven",
                  "original_game_modified", "android_device_tested"):
        if data[field] is not False:
            raise ValueError("Unsupported runtime or UI proof")
    row = data["report"]
    if type(row) is not dict or set(row) != R_NUMERIC | R_BOOL | {"one_parameter_public_type_category"}:
        raise ValueError("Unexpected or private original method field")
    if any(type(row[k]) is not int or not 0 <= row[k] <= 100000 for k in R_NUMERIC):
        raise ValueError("Invalid numeric IL evidence")
    if any(type(row[k]) is not bool for k in R_BOOL):
        raise ValueError("Invalid boolean IL evidence")
    if type(row["one_parameter_public_type_category"]) is not str or (
        row["one_parameter_public_type_category"] not in CATEGORIES
    ):
        raise ValueError("Unsafe or unknown parameter category")
    for key, expected in {
        "original_settings_method_bodies": 42,
        "apply_definitions": 1,
        "apply_direct_call_sites": 3,
        "distinct_apply_caller_methods": 3,
        "zero_parameter_caller_count": 2,
        "one_parameter_caller_count": 1,
        "one_parameter_caller_direct_dropdown_api_calls": 8,
        "one_parameter_caller_dropdown_field_reference_sites": 8,
    }.items():
        if row[key] != expected:
            raise ValueError("Known original IL evidence drift: " + key)
    if row["one_parameter_caller_is_public"] and row["one_parameter_caller_is_private"]:
        raise ValueError("Impossible original access flags")
    if any(row[k] is True for k in (
        "unity_serialized_onvaluechanged_binding_proven",
        "persistent_android_render_scale_binding_proven", "android_device_tested"
    )):
        raise ValueError("False callback or device proof")
    if sum(row[k] for k in (
        "one_parameter_caller_direct_dropdown_value_get_sites",
        "one_parameter_caller_direct_dropdown_value_set_sites",
        "one_parameter_caller_direct_dropdown_refresh_sites",
        "one_parameter_caller_direct_dropdown_onvaluechanged_get_sites",
    )) > row["one_parameter_caller_direct_dropdown_api_calls"]:
        raise ValueError("Dropdown method subcategories exceed total calls")
    if row["one_parameter_caller_direct_addlistener_sites"] > row["class_direct_addlistener_sites"]:
        raise ValueError("Listener count exceeds class count")
    if (row["one_parameter_caller_direct_dropdown_onvaluechanged_get_sites"] >
        row["class_direct_dropdown_onvaluechanged_get_sites"]):
        raise ValueError("Dropdown event-get count exceeds class count")
    return {
        "source_authenticated": True,
        "original_three_apply_callers_verified": True,
        "one_parameter_caller_type_category": row["one_parameter_public_type_category"],
        "one_parameter_caller_is_public": row["one_parameter_caller_is_public"],
        "one_parameter_caller_is_static": row["one_parameter_caller_is_static"],
        "one_parameter_caller_direct_value_get": row["one_parameter_caller_direct_dropdown_value_get_sites"],
        "one_parameter_caller_direct_value_set": row["one_parameter_caller_direct_dropdown_value_set_sites"],
        "one_parameter_caller_direct_refresh": row["one_parameter_caller_direct_dropdown_refresh_sites"],
        "class_direct_listener_subscriptions": row["class_direct_addlistener_sites"],
        "runtime_dropdown_callback_proven": False,
        "persisted_android_render_resolution_proven": False,
        "device_tested": False,
    }


def load(path: Path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 16384:
        raise ValueError("Unsafe source-only report path or size")
    return verify(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    print("T5_ORIGINAL_RESOLUTION_PARAMETER_GATE " +
          json.dumps(load(args.report), sort_keys=True))


if __name__ == "__main__":
    main()
