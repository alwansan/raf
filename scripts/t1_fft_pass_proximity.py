#!/usr/bin/env python3
"""Summarize sanitized same-log FFT kernel-6/pass proximity; never infer causality."""
import argparse
import json
from collections import Counter
from pathlib import Path

ALLOWED = {"spectrum", "foam", "foam_global", "subsurface_blur", "utility_noise"}

def summarize(scan):
    if not isinstance(scan, dict):
        raise ValueError("scan must be object")
    if scan.get("sample_errors_only") is not True or scan.get("original_kernel_identity_proven") is not False:
        raise ValueError("requires unproven-identity --errors-only scan")
    session_id = scan.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip() or len(session_id) > 160:
        raise ValueError("invalid session_id")
    source_sha256 = scan.get("source_sha256")
    if (not isinstance(source_sha256, str) or len(source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in source_sha256)):
        raise ValueError("invalid source_sha256 (expected lowercase hex digest)")
    events = scan.get("events")
    if not isinstance(events, list):
        raise ValueError("missing events")
    # A sampled log line represents one error; duplicates inflate pass association counts.
    seen_error_lines = set()
    histogram = Counter()
    matched = 0
    ambiguous = 0
    ambiguous_bins = Counter()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("event must be object")
        for key in ("pass_tokens", "before", "after"):
            if not isinstance(event.get(key, []), list):
                raise ValueError("invalid event collection: " + key)
        center = event.get("line")
        if type(center) is not int or center < 1:
            raise ValueError("invalid error line")
        if center in seen_error_lines:
            raise ValueError("duplicate sampled error line")
        seen_error_lines.add(center)
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
            distance = min(candidate[0] for candidate in candidates)
            nearest = {(name, direction) for d, name, direction in candidates if d == distance}
            # Equal-distance distinct passes or directions cannot be assigned arbitrarily.
            if len(nearest) != 1:
                ambiguous += 1
                ambiguous_bins[(distance, tuple(sorted(nearest)))] += 1
            else:
                name, direction = next(iter(nearest))
                histogram[(name, direction, distance)] += 1
                matched += 1
    return {
        "session_id": scan["session_id"],
        "source_sha256": scan["source_sha256"],
        "sampled_errors": len(events),
        "errors_with_nearby_pass_marker": matched,
        "ambiguous_nearest_pass_errors": ambiguous,
        "unmatched_sampled_errors": len(events) - matched - ambiguous,
        "ambiguous_nearest_bins": [
            {"line_distance": distance, "candidates": [
                {"pass": name, "direction": direction} for name, direction in candidates
            ], "count": count}
            for (distance, candidates), count in sorted(ambiguous_bins.items())
        ],
        "nearest_pass_bins": [
            {"pass": name, "direction": direction, "line_distance": distance, "count": count}
            for (name, direction, distance), count in sorted(histogram.items())
        ],
        "kernel_identity": "unproven",
        "causality": "not_established",
        "limits": "Only bounded sampled errors; equal-distance ties are ambiguous, not arbitrarily assigned. Marker proximity is not a program binding or GPU/FFT proof."
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sanitized_scan", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.sanitized_scan.read_text(encoding="utf-8"))), indent=2))

if __name__ == "__main__":
    main()
