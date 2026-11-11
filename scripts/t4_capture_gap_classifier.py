#!/usr/bin/env python3
"""Conservative per-counter comparison of one T4 mouse capture summary.

Never treat telemetry correlation as proof of gameplay or event delivery.
"""
import argparse
import json
import math
from pathlib import Path

KEYS = ("left", "right", "middle", "scroll")


def _valid_growth(value):
    # bool is an int in Python, but never a legitimate counter sample.
    return type(value) is int and value >= 0


def classify(summary):
    callbacks = summary.get("monotonic_callback_increases", {})
    readers = summary.get("monotonic_reader_increases", {})
    cb_first = summary.get("first_callback_counters", {})
    rd_first = summary.get("first_reader_counters", {})
    result = {}
    if not all(isinstance(section, dict) for section in (callbacks, readers, cb_first, rd_first)):
        return {
            "per_counter": {key: {"callback_growth": None, "reader_growth": None,
                                  "state": "invalid_counter_evidence"} for key in KEYS},
            "gameplay_success_proven": False,
            "note": "Malformed telemetry section; no per-button conclusion is possible.",
        }
    for key in KEYS:
        cb = callbacks.get(key)
        rd = readers.get(key)
        if (not _valid_growth(cb) and key in callbacks or not _valid_growth(rd) and key in readers
                or (key in cb_first and not _valid_growth(cb_first[key]))
                or (key in rd_first and not _valid_growth(rd_first[key]))):
            state = "invalid_counter_evidence"
        elif key not in cb_first or key not in rd_first or key not in callbacks or key not in readers:
            state = "insufficient_paired_baseline"
        elif cb > 0 and rd == 0:
            state = "callback_growth_without_reader_growth"
        elif cb == 0 and rd > 0:
            state = "reader_growth_without_callback_growth"
        elif cb > 0 and rd > 0:
            state = "both_grew_no_causal_proof"
        else:
            state = "no_new_growth_observed"
        result[key] = {"callback_growth": cb, "reader_growth": rd, "state": state}
    return {
        "per_counter": result,
        "gameplay_success_proven": False,
        "note": "Counters are aggregates, not paired events. Baselines, resets, logging thresholds, process identity and build identity must be checked independently. No growth is not evidence of missing hardware events.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path, help="JSON output of t4_capture_reader_summary.py")
    args = parser.parse_args()
    print(json.dumps(classify(json.loads(args.summary.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
