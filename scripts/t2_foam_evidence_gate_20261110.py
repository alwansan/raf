#!/usr/bin/env python3
"""Fail-closed sanitizer for public T2 water/foam evidence summaries.

Input is a JSON object with aggregate counters only. Never pass raw logs,
shader source, decompiled names, asset paths, or texture payloads.
"""
import argparse
import json
import sys

MAX_BYTES = 65536
COUNTERS = ("water_pass_errors", "fft_kernel_errors", "cursor_warnings", "obb_guid_warnings")
ALLOWED = frozenset(("schema", "run_id", "session_label", "source_commit", "counts", "status"))
STATUSES = frozenset(("OBSERVED", "NOT_OBSERVED", "UNKNOWN"))


class EvidenceError(ValueError):
    pass


def sanitize(payload):
    if type(payload) is not dict or set(payload) != ALLOWED:
        raise EvidenceError("unexpected or missing top-level fields")
    if payload["schema"] != "t2-water-aggregate-v1":
        raise EvidenceError("unsupported schema")
    run = payload["run_id"]
    if type(run) is not int or not (1 <= run <= 999999999999):
        raise EvidenceError("invalid run ID")
    label = payload["session_label"]
    if type(label) is not str or not (1 <= len(label) <= 40):
        raise EvidenceError("invalid session label")
    if not all(c.isascii() and (c.isalnum() or c in "_-") for c in label):
        raise EvidenceError("unsafe session label")
    sha = payload["source_commit"]
    if type(sha) is not str or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise EvidenceError("invalid commit SHA")
    if type(payload["status"]) is not str or payload["status"] not in STATUSES:
        raise EvidenceError("invalid status")
    counts = payload["counts"]
    if type(counts) is not dict or set(counts) != set(COUNTERS):
        raise EvidenceError("unexpected or missing counters")
    for key in COUNTERS:
        value = counts[key]
        if value is not None and (type(value) is not int or not (0 <= value <= 1000000000)):
            raise EvidenceError("invalid aggregate count")
    return {
        "schema": "t2-water-aggregate-v1",
        "run_id": run,
        "session_label": label,
        "source_commit": sha,
        "status": payload["status"],
        "counts": {key: counts[key] for key in COUNTERS},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="local aggregate JSON file, never raw game log")
    args = parser.parse_args()
    try:
        with open(args.input, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise EvidenceError("aggregate report exceeds size limit")
        payload = json.loads(raw.decode("utf-8"))
        result = sanitize(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, EvidenceError) as exc:
        print("REJECTED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
