#!/usr/bin/env python3
"""Compare two sanitized T1 kernel6 scans; never infer kernel identity or causality."""
import argparse
import json
import re
from pathlib import Path

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SESSION = re.compile(r"[A-Za-z0-9_.-]{1,100}\Z")
REQUIRED = ("kernel6_lines", "kernel6_error_lines", "water_pass_lines", "findkernel_lines", "dispatch_lines")

def validate(obj):
    if not isinstance(obj, dict) or not SESSION.fullmatch(str(obj.get("session_id", ""))):
        raise ValueError("missing/invalid session_id")
    if not HEX64.fullmatch(str(obj.get("source_sha256", ""))):
        raise ValueError("missing/invalid log SHA256")
    if obj.get("original_kernel_identity_proven") is not False:
        raise ValueError("original kernel identity must remain unproven")
    if obj.get("sample_errors_only") is not True:
        raise ValueError("input must use --errors-only")
    counts = obj.get("counts")
    if not isinstance(counts, dict) or any(type(counts.get(k)) is not int or counts[k] < 0 for k in REQUIRED):
        raise ValueError("invalid counts")
    if counts["kernel6_error_lines"] > counts["kernel6_lines"]:
        raise ValueError("error count exceeds mentions")
    events = obj.get("events")
    if not isinstance(events, list) or len(events) > 1000:
        raise ValueError("invalid events")
    lines = []
    for e in events:
        if not isinstance(e, dict) or type(e.get("line")) is not int or e["line"] < 1:
            raise ValueError("invalid event line")
        if not isinstance(e.get("before"), list) or not isinstance(e.get("after"), list):
            raise ValueError("invalid marker context")
        lines.append(e["line"])
    if lines != sorted(set(lines)) or type(obj.get("sampled_hits")) is not int or obj["sampled_hits"] != len(events):
        raise ValueError("unordered/duplicate samples")
    if len(events) > counts["kernel6_error_lines"]:
        raise ValueError("sampled errors exceed total error count")
    return {"session_id": obj["session_id"], "source_sha256": obj["source_sha256"],
            "counts": {k: counts[k] for k in REQUIRED},
            "first_sampled_error_line": lines[0] if lines else None,
            "sampled_error_lines": lines}

def compare(a, b):
    left, right = validate(a), validate(b)
    if left["session_id"] == right["session_id"]:
        raise ValueError("two distinct sessions required")
    if left["source_sha256"] == right["source_sha256"]:
        raise ValueError("identical log bytes: not independent sessions")
    return {"inputs": [left, right],
            "count_deltas_second_minus_first": {k: right["counts"][k] - left["counts"][k] for k in REQUIRED},
            "first_error_order": "not_comparable_across_logs",
            "kernel_identity": "unproven",
            "causality": "not_established",
            "limits": "Sampled line positions are local to each log; no timestamp, pass mapping, GUID, numeric FFT equivalence or GPU proof."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("first", type=Path)
    p.add_argument("second", type=Path)
    args = p.parse_args()
    print(json.dumps(compare(json.loads(args.first.read_text()), json.loads(args.second.read_text())), indent=2))

if __name__ == "__main__":
    main()
