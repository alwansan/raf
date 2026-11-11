#!/usr/bin/env python3
"""Summarize aggregate Android pointer-capture and Unity legacy reader markers.

Does not infer gameplay success from telemetry. Use one build/process log only.
"""
import argparse
import json
import re
from pathlib import Path

CALLBACK = "physical_mouse_captured_action_callbacks"
READER = "physical_mouse_legacy_reader_evidence"
NUM = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]*)=(\d+)(?=;|\s|$)")


def summarize(lines):
    counts = {CALLBACK: 0, READER: 0}
    last = {CALLBACK: {}, READER: {}}
    for line in lines:
        for marker in counts:
            if marker not in line:
                continue
            counts[marker] += 1
            tail = line.split(marker, 1)[1]
            # Reports may contain cumulative counters; do not add snapshots.
            last[marker] = {k: int(v) for k, v in NUM.findall(tail)}
    if not counts[CALLBACK]:
        verdict = "no_callback_marker_observed"
    elif not counts[READER]:
        verdict = "callbacks_observed_readers_not_observed"
    else:
        verdict = "both_markers_observed_no_gameplay_proof"
    return {
        "callback_reports": counts[CALLBACK],
        "reader_reports": counts[READER],
        "last_callback_counters": last[CALLBACK],
        "last_reader_counters": last[READER],
        "diagnostic_state": verdict,
        "gameplay_success_proven": False,
        "note": "Missing markers may reflect logging thresholds, absent instrumentation, or different app sessions. Compare only the same build/process.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    with args.log.open(encoding="utf-8", errors="replace") as handle:
        print(json.dumps(summarize(handle), indent=2))


if __name__ == "__main__":
    main()
