"""Fail-closed source-only contract for a bounded original managed display IL report.

No decompiled source, private method/field identities, original assets or IL are emitted.
A structural callsite count does not prove callback dataflow or a working Android
render-resolution selector.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TOP = {
    "schema_version", "original_assembly_sha_verified", "original_assembly_bytes",
    "original_classes_unique", "settings", "dynamic", "compiled_il_inspected",
    "option_to_callback_dataflow_proven", "persisted_android_render_scale_proven",
    "equal_axis_render_scale_proven", "phone_tested", "original_game_modified",
}
COUNTS = {
    "method_bodies", "call_sites", "screen_set_resolution",
    "screen_resolutions_read", "screen_current_resolution_read",
    "screen_dimensions_read", "event_add_listener", "option_population",
    "playerprefs_reads", "playerprefs_writes", "local_apply_resolution_calls",
    "dynamic_resolution_references", "scalable_resize_buffers",
    "same_type_delegate_targets",
}


def _unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Duplicate report field")
        result[key] = value
    return result


def verify(data):
    if type(data) is not dict or set(data) != TOP:
        raise ValueError("Unexpected report shape")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Schema mismatch")
    if type(data["original_assembly_bytes"]) is not int or data["original_assembly_bytes"] != 3211776:
        raise ValueError("Original size mismatch")
    for key in ("original_assembly_sha_verified", "original_classes_unique", "compiled_il_inspected"):
        if data[key] is not True:
            raise ValueError("Missing original byte/IL evidence")
    for key in ("option_to_callback_dataflow_proven", "persisted_android_render_scale_proven",
                "equal_axis_render_scale_proven", "phone_tested", "original_game_modified"):
        if data[key] is not False:
            raise ValueError("Unproved Android/Settings success claimed")
    for key in ("settings", "dynamic"):
        counters = data[key]
        if type(counters) is not dict or set(counters) != COUNTS:
            raise ValueError("Incomplete counter schema")
        if any(type(x) is not int or x < 0 or x > 100000 for x in counters.values()):
            raise ValueError("Invalid counter value")
        if counters["method_bodies"] < 1 or counters["call_sites"] < 1:
            raise ValueError("No executable original IL")
        if counters["call_sites"] < counters["screen_set_resolution"]:
            raise ValueError("Impossible callsite counts")
    # Confirm existing original compiled Screen and DynamicResolution API
    # boundaries; do not infer Settings callback or persisted render scale.
    if data["settings"]["screen_set_resolution"] != 1:
        raise ValueError("Known original Settings resolution mutation not present")
    if data["dynamic"]["scalable_resize_buffers"] != 2:
        raise ValueError("Known original DynamicResolution resize sites not present")
    return {
        "original_compiled_display_calls_source_verified": True,
        "settings_set_resolution_sites": 1,
        "dynamic_resize_buffer_sites": 2,
        "option_to_callback_dataflow_proven": False,
        "persisted_android_render_scale_proven": False,
        "game_device_tested": False,
    }


def load(path: Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8192:
        raise ValueError("Missing, linked or oversized report")
    text = path.read_text(encoding="utf-8")
    return verify(json.loads(text, object_pairs_hook=_unique))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print("T5_RESOLUTION_ORIGINAL_IL_GATE " +
          json.dumps(load(args.report), sort_keys=True))


if __name__ == "__main__":
    main()
