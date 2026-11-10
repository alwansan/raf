#!/usr/bin/env python3
"""Conservative INPUT-005 gate triage of signed Raft Android runtime logs.

This tool never infers device success from source or absent log lines.
It reports the last observed gate and request evidence, not OS acceptance.
"""
import argparse
import json
import re
from pathlib import Path

FIELDS = ("paused", "focused", "authoredLock", "inputSystemPhysicalMouse", "shouldCapture")
MARKER = "physical_mouse_capture_eligibility"
REQUEST = "physical_mouse_capture_requested"
RETRY = "physical_mouse_capture_retry"
RELATIVE = "physical_mouse_relative"
CALLBACK = "physical_mouse_captured_action_callbacks"


def parse_bool(line, field):
    match = re.search(r"(?<![A-Za-z_])" + re.escape(field) + r"=(true|false)\b", line, re.I)
    return None if match is None else match.group(1).lower() == "true"


def diagnose(lines):
    gates = []
    counts = {"requests": 0, "retries": 0, "relative_markers": 0,
              "action_callback_markers": 0}
    epoch_counts = counts.copy()
    for number, line in enumerate(lines, 1):
        if MARKER in line:
            gates.append({"line": number, **{k: parse_bool(line, k) for k in FIELDS}})
            epoch_counts = dict.fromkeys(counts, 0)
        if REQUEST in line:
            counts["requests"] += 1
            epoch_counts["requests"] += 1
        if RETRY in line:
            counts["retries"] += 1
            epoch_counts["retries"] += 1
        if RELATIVE in line:
            counts["relative_markers"] += 1
            epoch_counts["relative_markers"] += 1
        if CALLBACK in line:
            counts["action_callback_markers"] += 1
            epoch_counts["action_callback_markers"] += 1
    if not gates:
        status = "NO_ELIGIBILITY_TELEMETRY"
    else:
        last = gates[-1]
        if any(last[k] is None for k in FIELDS):
            status = "INCOMPLETE_ELIGIBILITY_MARKER"
        elif last["paused"] or not last["focused"]:
            status = "FOCUS_OR_PAUSE_GATE"
        elif not last["authoredLock"]:
            status = "NO_AUTHORED_LOCK"
        elif not last["inputSystemPhysicalMouse"]:
            status = "NO_INPUT_SYSTEM_PHYSICAL_MOUSE"
        elif not last["shouldCapture"]:
            status = "INCONSISTENT_GATE"
        elif not epoch_counts["requests"] and not epoch_counts["retries"]:
            status = "ELIGIBLE_NO_REQUEST_OBSERVED"
        elif not epoch_counts["relative_markers"] and not epoch_counts["action_callback_markers"]:
            status = "REQUEST_NO_CALLBACK_MARKER_OBSERVED"
        else:
            status = "CALLBACK_MARKER_PRESENT_UNVERIFIED_GAMEPLAY"
    return {
        "classification": status,
        "eligibility_transitions": len(gates),
        "last_eligibility": gates[-1] if gates else None,
        "observed_markers": counts,
        "last_gate_epoch_markers": epoch_counts,
        "device_success_proven": False,
        "limitations": ("Last gate epoch starts at the latest eligibility transition, but is not a confirmed capture "
                        "epoch. Truncated logs, absent mouse activity and callback sampling "
                        "can mimic failure. No keyboard, click, wheel or gameplay success inferred.")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="Read-only UTF-8 runtime log")
    args = parser.parse_args()
    with args.log.open(encoding="utf-8", errors="replace") as handle:
        print(json.dumps(diagnose(handle), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
