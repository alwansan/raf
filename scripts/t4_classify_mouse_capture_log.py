#!/usr/bin/env python3
"""Conservative read-only analysis of Android physical mouse event sequences."""
import argparse
import json

EVENTS = ("physical_mouse_lock_intent", "physical_mouse_capture_requested",
          "physical_mouse_relative", "physical_mouse_capture_released",
          "physical_mouse_capture_release_outcome")


def classify(lines):
    hits = {event: [] for event in EVENTS}
    for number, line in enumerate(lines, 1):
        for event in EVENTS:
            if event in line:
                hits[event].append((number, line.strip()[:500]))
    locks = [n for n, s in hits[EVENTS[0]] if "authored_lock" in s]
    escapes = [n for n, s in hits[EVENTS[0]] if "escape_release" in s]
    requests = [n for n, _ in hits[EVENTS[1]]]
    relative = [n for n, _ in hits[EVENTS[2]]]
    releases = [n for n, _ in hits[EVENTS[3]]]
    findings = []
    for index, escape in enumerate(escapes):
        end = escapes[index + 1] if index + 1 < len(escapes) else float("inf")
        subsequent_locks = [n for n in locks if escape < n < end]
        if not subsequent_locks:
            state = "NO_REARM_OBSERVED"
        else:
            lock = subsequent_locks[0]
            subsequent_requests = [n for n in requests if lock < n < end]
            if not subsequent_requests:
                state = "LOCK_WITHOUT_REQUEST_OBSERVED"
            else:
                request = subsequent_requests[0]
                first_release = next((n for n in releases if request < n < end), end)
                if any(request < n < first_release for n in relative):
                    state = "RELATIVE_AFTER_REARM_OBSERVED"
                elif first_release < end:
                    state = "RELEASED_BEFORE_RELATIVE_OBSERVED"
                else:
                    state = "REQUEST_WITHOUT_RELATIVE_OBSERVED"
        findings.append({"escape_line": escape, "classification": state})
    if not escapes:
        findings.append({"classification": "NO_ESCAPE_SEQUENCE_OBSERVED"})
    return {"counts": {event: len(items) for event, items in hits.items()},
            "findings": findings, "device_success_proven": False,
            "caveat": "Partial logs and lack of physical mouse activity can mimic missing events. Confirm actual gameplay/menu transition on device."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", help="UTF-8 log file; never modified")
    args = parser.parse_args()
    with open(args.log, encoding="utf-8", errors="replace") as source:
        print(json.dumps(classify(source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
