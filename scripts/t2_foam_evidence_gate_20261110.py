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


def _unique_object_pairs(pairs):
    """Reject duplicate keys at every depth before constructing a dict."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError("duplicate JSON key")
        result[key] = value
    return result


def _reject_nonfinite(_value):
    """Python json.loads otherwise accepts NaN and Infinity extensions."""
    raise EvidenceError("non-finite JSON number")


def parse_aggregate_json(raw):
    """Strict JSON parsing before the existing allowlist-based sanitizer."""
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise EvidenceError("invalid aggregate JSON size or type")
    try:
        parsed = json.loads(raw.decode("utf-8"),
                            object_pairs_hook=_unique_object_pairs,
                            parse_constant=_reject_nonfinite)
    except UnicodeDecodeError as exc:
        raise EvidenceError("invalid aggregate JSON encoding") from exc
    except ValueError as exc:
        # Python 3.11+ rejects enormous integer literals before sanitization.
        # Do not leak interpreter-dependent parse errors to callers.
        raise EvidenceError("invalid aggregate JSON value") from exc
    return sanitize(parsed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="local aggregate JSON file, never raw game log")
    args = parser.parse_args()
    try:
        with open(args.input, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise EvidenceError("aggregate report exceeds size limit")
        result = parse_aggregate_json(raw)
    except (OSError, UnicodeError, json.JSONDecodeError, EvidenceError) as exc:
        print("REJECTED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
