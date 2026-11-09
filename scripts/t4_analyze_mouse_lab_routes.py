#!/usr/bin/env python3
"""Classify T4 mini-lab mouse callback coverage without claiming Unity/device success."""
import argparse
import json
import math
import re
from collections import defaultdict

ROUTES = ("activity_touch", "activity_generic", "view_touch", "view_generic", "captured")
BUTTONS = {"left": 1, "right": 2, "middle": 4}
PATTERN = re.compile(r"([A-Za-z]+)=([^ ]+)")
# Android InputDevice: SOURCE_MOUSE=0x2002, SOURCE_MOUSE_RELATIVE=0x20004.
# Class bits must match too; touchscreen SOURCE_TOUCHSCREEN=0x1002 is not a mouse.
MOUSE_SOURCES = (0x2002, 0x20004)

def physical_mouse_source(value):
    if value is None:
        return False
    source = int(value, 0)
    if source < 0:
        return False
    return any(source & mask == mask for mask in MOUSE_SOURCES)

def nonzero_scroll(value):
    number = float(value)
    return math.isfinite(number) and number != 0


def analyze(lines):
    phase = "unknown"
    groups = defaultdict(lambda: {"routes": set(), "actions": set(), "buttons": set(),
                                  "wheel_v": 0, "wheel_h": 0, "samples": 0,
                                  "button_presses": set(), "button_releases": set()})
    rejected = 0
    capture_route_conflicts = 0
    for line in lines:
        try:
            obj = json.loads(line)
            kind = obj.get("event")
            detail = obj.get("detail", "")
            if not isinstance(detail, str):
                raise ValueError("detail must be string")
            if kind == "capture_request":
                if detail in ("ON", "OFF"):
                    phase = detail.lower()
                continue
            if kind != "input":
                continue
            fields = dict(PATTERN.findall(detail))
            route = fields.get("route")
            if route not in ROUTES or not physical_mouse_source(fields.get("source")):
                rejected += 1
                continue
            captured = fields.get("captured")
            # A capture request is not proof that Android granted capture.
            # Never label callbacks without an explicit captured=true as captured.
            key = "on" if captured == "true" else "off" if captured == "false" else "unknown"
            if (captured == "true" and route != "captured") or (captured == "false" and route == "captured"):
                # Contradictory route/flag pairs cannot establish either captured or uncaptured delivery.
                capture_route_conflicts += 1
                rejected += 1
                continue
            group = groups[key]
            group["samples"] += 1
            group["routes"].add(route)
            action = fields.get("action", "")
            group["actions"].add(action)
            state = int(fields.get("buttonState", "0"), 0)
            action_button = int(fields.get("actionButton", "0"), 0)
            if state < 0 or action_button < 0:
                rejected += 1
                group["samples"] -= 1
                group["routes"].discard(route) if group["samples"] == 0 else None
                continue
            for name, bit in BUTTONS.items():
                if (state | action_button) & bit:
                    group["buttons"].add(name)
                if action in ("ACTION_DOWN", "ACTION_BUTTON_PRESS") and action_button & bit:
                    group["button_presses"].add(name)
                if action in ("ACTION_UP", "ACTION_BUTTON_RELEASE") and action_button & bit:
                    group["button_releases"].add(name)
            if action == "ACTION_SCROLL" and nonzero_scroll(fields.get("vscroll", "0")):
                group["wheel_v"] += 1
            if action == "ACTION_SCROLL" and nonzero_scroll(fields.get("hscroll", "0")):
                group["wheel_h"] += 1
        except (ValueError, TypeError, json.JSONDecodeError):
            rejected += 1
    result = {}
    for phase, group in sorted(groups.items()):
        result[phase] = {
            "samples": group["samples"], "routes": sorted(group["routes"]),
            "actions": sorted(group["actions"]), "buttons_observed": sorted(group["buttons"]),
            "button_presses_observed": sorted(group["button_presses"]),
            "button_releases_observed": sorted(group["button_releases"]),
            "vertical_scroll_events": group["wheel_v"],
            "horizontal_scroll_events": group["wheel_h"],
            "missing_button_evidence": sorted(set(BUTTONS) - group["buttons"]),
        }
    return {"phases": result, "rejected_records": rejected,
            "capture_route_conflicts": capture_route_conflicts,
            "device_success_proven": False,
            "note": "Capture request ON alone does not establish captured=true; contradictory capture flags and routes are rejected; missing capture flag stays unknown. Only source-identified physical mouse callbacks count; rejected includes nonmouse/unknown-source events. Missing button evidence is not proof of failure unless actions were attempted; callbacks do not prove Unity Mouse0/1/2."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", help="Exported T4 mini-lab JSONL")
    args = p.parse_args()
    with open(args.jsonl, encoding="utf-8") as f:
        print(json.dumps(analyze(f), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
