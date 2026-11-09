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
    if not isinstance(captured, dict) or "captured" not in captured.get("routes", []):
        raise ValueError("on phase must contain captured route")
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
