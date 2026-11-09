#!/usr/bin/env python3
"""Fail-closed triage of T4 Android mouse JSONL analyzer output.

This is an evidence *triage*, not a Unity/game acceptance test.  The analyzer
reports callbacks only; no possible output of this tool can be DEVICE_PASS.
"""
import argparse
import json
from pathlib import Path

BUTTONS = ("left", "right", "middle")

def triage(report):
    if not isinstance(report, dict):
        raise ValueError("report must be an object")
    phases = report.get("phases")
    if not isinstance(phases, dict):
        raise ValueError("missing phases")
    captured = phases.get("on")
    if captured is None:
        return {"status": "NEEDS_CAPTURED_CALLBACKS", "android": {}, "unity": "UNVERIFIED",
                "device_pass": False}
    if not isinstance(captured, dict):
        raise ValueError("on phase must be an object")
    routes = captured.get("routes")
    if not isinstance(routes, list) or not all(isinstance(route, str) for route in routes) or "captured" not in routes:
        raise ValueError("on phase must contain captured route")
    for field in ("button_presses_observed", "button_releases_observed"):
        values = captured.get(field, [])
        if not isinstance(values, list) or not all(isinstance(v, str) and v in BUTTONS for v in values):
            raise ValueError(f"{field} must be a list of known mouse buttons")
    for field in ("vertical_scroll_events", "horizontal_scroll_events"):
        count = captured.get(field, 0)
        if type(count) is not int or count < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    presses = set(captured.get("button_presses_observed", []))
    releases = set(captured.get("button_releases_observed", []))
    result = {button: ("CALLBACK_PAIR_ONLY" if button in presses and button in releases
                       else "NEEDS_CAPTURED_PRESS_RELEASE") for button in BUTTONS}
    result["vertical_scroll"] = ("CALLBACK_ONLY" if captured.get("vertical_scroll_events", 0) > 0
                                  else "NEEDS_CAPTURED_SCROLL")
    result["horizontal_scroll"] = ("CALLBACK_ONLY" if captured.get("horizontal_scroll_events", 0) > 0
                                    else "NEEDS_CAPTURED_SCROLL")
    return {"status": "ANDROID_ONLY_UNITY_UNVERIFIED", "android": result,
            "unity": "UNVERIFIED", "device_pass": False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("analyzer_json", type=Path)
    args = p.parse_args()
    report = json.loads(args.analyzer_json.read_text(encoding="utf-8"))
    print(json.dumps(triage(report), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
