#!/usr/bin/env python3
"""Summarize sanitized same-log FFT kernel-6/pass proximity; never infer causality."""
import argparse
import json
from collections import Counter
from pathlib import Path

ALLOWED = {"spectrum", "foam", "foam_global", "subsurface_blur", "utility_noise"}

def summarize(scan):
    if scan.get("sample_errors_only") is not True or scan.get("original_kernel_identity_proven") is not False:
        raise ValueError("requires unproven-identity --errors-only scan")
    if not isinstance(scan, dict):
        raise ValueError("scan must be object")
    events = scan.get("events")
    if not isinstance(events, list):
        raise ValueError("missing events")
    histogram = Counter()
    matched = 0
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("event must be object")
        for key in ("pass_tokens", "before", "after"):
            if not isinstance(event.get(key, []), list):
                raise ValueError("invalid event collection: " + key)
        center = event.get("line")
        if type(center) is not int or center < 1:
            raise ValueError("invalid error line")
        candidates = []
        for token in event.get("pass_tokens", []):
            if not isinstance(token, str):
                raise ValueError("pass token must be string")
            normalized = token.lower().replace(" ", "_")
            if normalized not in ALLOWED:
                raise ValueError("unknown pass token")
            candidates.append((0, normalized, "same_line"))
        for side in ("before", "after"):
            for row in event.get(side, []):
                if not isinstance(row, dict) or not isinstance(row.get("markers", []), list):
                    raise ValueError("invalid context row")
                line = row.get("line")
                if type(line) is not int or line < 1 or (side == "before" and line >= center) or (side == "after" and line <= center):
                    raise ValueError("invalid context position")
                for marker in row.get("markers", []):
                    if not isinstance(marker, str):
                        raise ValueError("marker must be string")
                    if marker.startswith("pass:"):
                        name = marker[5:]
                        if name not in ALLOWED:
                            raise ValueError("unknown pass marker")
                        candidates.append((abs(line - center), name, side))
        if candidates:
            # Deterministic nearest marker, tie broken by pass and direction.
            distance, name, direction = min(candidates)
            histogram[(name, direction, distance)] += 1
            matched += 1
    return {
        "session_id": scan["session_id"],
        "source_sha256": scan["source_sha256"],
        "sampled_errors": len(events),
        "errors_with_nearby_pass_marker": matched,
        "unmatched_sampled_errors": len(events) - matched,
        "nearest_pass_bins": [
            {"pass": name, "direction": direction, "line_distance": distance, "count": count}
            for (name, direction, distance), count in sorted(histogram.items())
        ],
        "kernel_identity": "unproven",
        "causality": "not_established",
        "limits": "Only bounded sampled errors; marker proximity is not a program binding or GPU/FFT proof."
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sanitized_scan", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.sanitized_scan.read_text(encoding="utf-8"))), indent=2))

if __name__ == "__main__":
    main()
