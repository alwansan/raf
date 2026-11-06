"""Strict source-only authentic GraphicsSettingsBox.Apply IL provenance gate.

Do not infer a UI callback or Android render-resolution selector from direct
compiled IL caller metadata. Original source/IL/method names are never output.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TOP = {
    "schema_version", "original_assembly_sha_verified", "original_assembly_bytes",
    "compiled_original_il_not_decompiled_source", "original_graphics_settings_type_unique",
    "output_method_names_tokens_private", "evidence",
    "selection_to_runtime_callback_proven", "persisted_android_render_scale_proven",
    "device_tested",
}
EVIDENCE_NUMERIC = {
    "original_class_methods_with_body", "apply_method_definitions",
    "apply_method_direct_screen_set_resolution_sites",
    "apply_method_direct_scalable_resize_buffers_sites",
    "internal_apply_call_sites", "distinct_internal_apply_callers",
    "external_apply_call_sites", "distinct_external_apply_callers",
    "external_apply_callers_in_settings_class",
    "original_option_population_sites", "original_option_population_methods",
}
EVIDENCE_FALSE = {
    "serialized_unity_ui_event_binding_proven", "custom_settings_persistence_proven",
    "android_render_scale_selector_proven", "original_game_modified", "phone_tested",
}
PROFILE_NUMERIC = {
    "apply_call_sites", "parameters", "direct_dropdown_api_calls",
    "direct_dropdown_field_references", "direct_screen_resolution_list_reads",
    "direct_screen_current_resolution_reads", "direct_playerprefs_reads",
    "direct_playerprefs_writes", "direct_custom_settings_type_references",
    "direct_same_type_calls",
}
PROFILE_BOOL = {
    "has_int_parameter", "has_bool_parameter", "is_known_unity_lifecycle",
    "contains_option_population", "contains_same_type_delegate_site",
}


def _unique(pairs):
    row = {}
    for key, value in pairs:
        if key in row:
            raise ValueError("Duplicate JSON field")
        row[key] = value
    return row


def verify(value):
    if type(value) is not dict or set(value) != TOP:
        raise ValueError("Unexpected original report fields")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    if type(value["original_assembly_bytes"]) is not int or value["original_assembly_bytes"] != 3211776:
        raise ValueError("Original bytes mismatch")
    for key in ("original_assembly_sha_verified",
                "compiled_original_il_not_decompiled_source",
                "original_graphics_settings_type_unique",
                "output_method_names_tokens_private"):
        if value[key] is not True:
            raise ValueError("Missing original provenance")
    for key in ("selection_to_runtime_callback_proven",
                "persisted_android_render_scale_proven", "device_tested"):
        if value[key] is not False:
            raise ValueError("Unverified runtime proof claimed")
    ev = value["evidence"]
    if type(ev) is not dict or set(ev) != EVIDENCE_NUMERIC | EVIDENCE_FALSE | {"internal_caller_profiles"}:
        raise ValueError("Unexpected evidence or private identifiers")
    if any(ev[k] is not False for k in EVIDENCE_FALSE):
        raise ValueError("Unproven event or Android behavior")
    if any(type(ev[k]) is not int or ev[k] < 0 or ev[k] > 100000 for k in EVIDENCE_NUMERIC):
        raise ValueError("Invalid IL count")
    expected = {
        "original_class_methods_with_body": 42,
        "apply_method_definitions": 1,
        "apply_method_direct_screen_set_resolution_sites": 1,
        "apply_method_direct_scalable_resize_buffers_sites": 0,
        "internal_apply_call_sites": 3,
        "original_option_population_sites": 1,
        "original_option_population_methods": 1,
    }
    for key, count in expected.items():
        if ev[key] != count:
            raise ValueError("Original pinned IL site count changed: " + key)
    profiles = ev["internal_caller_profiles"]
    if (type(profiles) is not list or not 1 <= len(profiles) <= 3
            or ev["distinct_internal_apply_callers"] != len(profiles)):
        raise ValueError("Incomplete caller inventory")
    if (ev["distinct_external_apply_callers"] > ev["external_apply_call_sites"]
            or ev["external_apply_callers_in_settings_class"] > ev["external_apply_call_sites"]):
        raise ValueError("External calling-site count contradictory")
    if not all(type(x) is dict and set(x) == PROFILE_NUMERIC | PROFILE_BOOL for x in profiles):
        raise ValueError("Unexpected method metadata or private identifier")
    for row in profiles:
        if any(type(row[k]) is not int or row[k] < 0 or row[k] > 5000 for k in PROFILE_NUMERIC):
            raise ValueError("Invalid caller method count")
        if any(type(row[k]) is not bool for k in PROFILE_BOOL):
            raise ValueError("Invalid CIL method attribute")
        if row["apply_call_sites"] < 1:
            raise ValueError("Noncalling method in caller inventory")
        if row["has_int_parameter"] and row["parameters"] < 1:
            raise ValueError("Impossible Int32 parameter")
        if row["has_bool_parameter"] and row["parameters"] < 1:
            raise ValueError("Impossible Boolean parameter")
    if sum(p["apply_call_sites"] for p in profiles) != 3:
        raise ValueError("Original caller sites lost")
    if (sum(bool(p["contains_option_population"]) for p in profiles)
            > ev["original_option_population_methods"]):
        raise ValueError("Original option owner duplication")
    return {
        "verified_original_three_apply_calls": True,
        "distinct_caller_methods": ev["distinct_internal_apply_callers"],
        "external_direct_apply_sites": ev["external_apply_call_sites"],
        "caller_methods_with_int_parameter": sum(p["has_int_parameter"] for p in profiles),
        "caller_methods_in_known_unity_lifecycle": sum(p["is_known_unity_lifecycle"] for p in profiles),
        "callers_with_original_option_population": sum(p["contains_option_population"] for p in profiles),
        "caller_playerprefs_write_sites": sum(p["direct_playerprefs_writes"] for p in profiles),
        "selection_to_runtime_callback_proven": False,
        "persisted_android_render_scale_proven": False,
        "device_tested": False,
    }


def load(path: Path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 16384:
        raise ValueError("Missing or unsafe source-only report")
    return verify(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print("T5_APPLY_CALLER_IL_GATE " + json.dumps(load(args.report), sort_keys=True))


if __name__ == "__main__":
    main()
