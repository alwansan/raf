"""Strict source-only proof gate for authenticated original Settings delegate IL.

This verifies recorded structural evidence, not callback registration, persistence,
Android render-scale UI, or game/device readiness. Do not accept private tokens.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

KEYS = {
    "schema_version", "original_assembly_sha_verified", "original_assembly_bytes",
    "original_compiled_il", "unique_original_graphics_settings_type",
    "graph_method_limit", "evidence",
    "no_original_methods_tokens_il_or_sources_emitted",
    "event_registration_and_callback_dataflow_proven",
    "android_render_scale_persistence_proven", "actual_android_device_tested",
}
COUNTERS = {
    "compiled_methods", "delegate_instruction_sites",
    "resolved_delegate_sites", "unresolved_delegate_sites",
    "unique_delegate_target_methods", "delegate_targets_with_int_parameter",
    "option_population_call_sites", "methods_populating_options",
    "option_methods_with_delegate_sites", "option_methods_direct_apply_calls",
    "option_methods_reach_apply", "option_methods_reach_screen_setresolution",
    "delegate_targets_direct_apply_calls", "delegate_targets_reach_apply",
    "delegate_targets_direct_screen_setresolution",
    "delegate_targets_reach_screen_setresolution",
    "delegate_targets_direct_playerprefs_write",
    "internal_direct_call_edges", "unresolved_internal_call_sites",
}
DISCLAIMERS = {
    "runtime_dropdown_callback_binding_proven",
    "original_custom_persistence_proven",
    "android_render_scale_binding_proven",
}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def verify(data):
    if type(data) is not dict or set(data) != KEYS:
        raise ValueError("Unexpected report fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Incorrect schema version")
    if type(data["original_assembly_bytes"]) is not int or data["original_assembly_bytes"] != 3211776:
        raise ValueError("Unexpected original binary size")
    if type(data["graph_method_limit"]) is not int or data["graph_method_limit"] != 256:
        raise ValueError("Unbounded graph scope")
    for key in ("original_assembly_sha_verified", "original_compiled_il",
                "unique_original_graphics_settings_type",
                "no_original_methods_tokens_il_or_sources_emitted"):
        if data[key] is not True:
            raise ValueError("Missing original-source provenance")
    for key in ("event_registration_and_callback_dataflow_proven",
                "android_render_scale_persistence_proven", "actual_android_device_tested"):
        if data[key] is not False:
            raise ValueError("Unverified runtime/Android success claimed")

    ev = data["evidence"]
    if type(ev) is not dict or set(ev) != COUNTERS | DISCLAIMERS:
        raise ValueError("Unexpected delegate evidence schema")
    for key in DISCLAIMERS:
        if ev[key] is not False:
            raise ValueError("Source graph cannot prove runtime/UI/persistence")
    if any(type(ev[k]) is not int or ev[k] < 0 or ev[k] > 100000 for k in COUNTERS):
        raise ValueError("Invalid or fabricated numeric evidence")
    if not 1 <= ev["compiled_methods"] <= 256:
        raise ValueError("Invalid compiled original method bound")
    # Unique methods and distinct option-populating methods are both subsets
    # of the compiled graph. A report with more methods than the graph itself
    # cannot be treated as authenticated original topology.
    if (ev["unique_delegate_target_methods"] > ev["compiled_methods"] or
            ev["methods_populating_options"] > ev["compiled_methods"]):
        raise ValueError("Method population exceeds compiled original graph")
    if (ev["delegate_instruction_sites"] != 2 or
        ev["resolved_delegate_sites"] != 2 or
        ev["unresolved_delegate_sites"] != 0 or
        not 1 <= ev["unique_delegate_target_methods"] <= 2):
        raise ValueError("Original delegate target cannot be authenticated")
    # A per-method subset cannot exceed its parent population. These bounds
    # prevent self-contradictory source reports from passing the provenance gate.
    if ev["option_methods_with_delegate_sites"] > ev["delegate_instruction_sites"]:
        raise ValueError("More option delegate methods than original delegate sites")
    if ev["delegate_targets_with_int_parameter"] > ev["resolved_delegate_sites"]:
        raise ValueError("More typed targets than resolved delegate sites")
    if ev["option_methods_direct_apply_calls"] > ev["option_methods_reach_apply"]:
        raise ValueError("Direct option apply call lacks reachability")
    if ev["delegate_targets_direct_playerprefs_write"] > ev["unique_delegate_target_methods"]:
        raise ValueError("PlayerPrefs targets exceed original target methods")
    if ev["unresolved_internal_call_sites"] != 0:
        raise ValueError("Incomplete same-type compiled call graph")
    if not 1 <= ev["methods_populating_options"] <= ev["option_population_call_sites"]:
        raise ValueError("Missing original option population")
    unique = ev["unique_delegate_target_methods"]
    for key in ("delegate_targets_with_int_parameter", "delegate_targets_direct_apply_calls",
                "delegate_targets_reach_apply",
                "delegate_targets_direct_screen_setresolution",
                "delegate_targets_reach_screen_setresolution",
                "delegate_targets_direct_playerprefs_write"):
        if ev[key] > unique:
            raise ValueError("Delegate target exceeds unique source methods")
    for key in ("option_methods_with_delegate_sites", "option_methods_direct_apply_calls",
                "option_methods_reach_apply", "option_methods_reach_screen_setresolution"):
        if ev[key] > ev["methods_populating_options"]:
            raise ValueError("Option method subset impossible")
    if (ev["delegate_targets_direct_apply_calls"] >
        ev["delegate_targets_reach_apply"] or
        ev["delegate_targets_direct_screen_setresolution"] >
        ev["delegate_targets_reach_screen_setresolution"] or
        ev["option_methods_direct_apply_calls"] > ev["option_methods_reach_apply"]):
        raise ValueError("Reachability contradicts direct call")
    # Calls to the same-type Apply method must appear among internal direct
    # call edges. Reachability alone cannot manufacture an absent direct edge.
    if ev["internal_direct_call_edges"] < max(
        ev["delegate_targets_direct_apply_calls"],
        ev["option_methods_direct_apply_calls"],
    ):
        raise ValueError("Direct Apply calls exceed internal call edges")
    return {
        "original_compiled_delegate_sites_authenticated": 2,
        "unique_targets": unique,
        "option_population_methods": ev["methods_populating_options"],
        "delegate_targets_reach_legacy_setresolution": ev["delegate_targets_reach_screen_setresolution"],
        "delegate_targets_reach_apply_method": ev["delegate_targets_reach_apply"],
        "option_population_methods_contain_delegate_site": ev["option_methods_with_delegate_sites"],
        "option_population_methods_reach_setresolution": ev["option_methods_reach_screen_setresolution"],
        "runtime_ui_callback_dataflow_verified": False,
        "persistent_android_render_scale_verified": False,
        "device_tested": False,
    }


def load(path: Path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 16384:
        raise ValueError("Missing, linked or oversized IL report")
    return verify(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    print("T5_ORIGINAL_DELEGATE_IL_GATE " + json.dumps(load(args.report), sort_keys=True))


if __name__ == "__main__":
    main()
