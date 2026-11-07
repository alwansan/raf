#!/usr/bin/env python3
"""Compare sanitized FFT traces; structural and provenance mismatches fail closed."""
import argparse
import json
import math
from pathlib import Path

FIELDS = ("source_sha", "fixture_sha256", "input_sha256", "kernel", "dispatch", "pass", "invocation", "read_site", "coordinate", "value")
PROVENANCE = ("fixture_sha256", "input_sha256", "kernel", "dispatch")

def _parse(line, path, number):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError(f"{path}:{number}: duplicate JSON field {key}")
            out[key] = value
        return out
    obj = json.loads(line, object_pairs_hook=pairs)
    if not isinstance(obj, dict) or any(k not in obj for k in FIELDS):
        raise ValueError(f"{path}:{number}: incomplete record")
    for field in ("source_sha", "fixture_sha256", "input_sha256", "kernel"):
        if not isinstance(obj[field], str) or not obj[field]:
            raise ValueError(f"{path}:{number}: invalid {field}")
    for field in ("pass", "invocation", "read_site"):
        if type(obj[field]) is not int or obj[field] < 0:
            raise ValueError(f"{path}:{number}: invalid {field}")
    for field, length in (("dispatch", 3), ("coordinate", None)):
        values = obj[field]
        if not isinstance(values, list) or (len(values) != length if length else len(values) not in (2, 3)):
            raise ValueError(f"{path}:{number}: invalid {field}")
        if any(type(v) is not int or (field == "dispatch" and v <= 0) for v in values):
            raise ValueError(f"{path}:{number}: invalid {field}")
    values = obj["value"]
    if not isinstance(values, list) or not values or any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError(f"{path}:{number}: invalid value")
    return obj

def load(path):
    rows = {}
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = _parse(line, path, number)
        key = (obj["pass"], obj["invocation"], obj["read_site"])
        if key in rows:
            raise ValueError(f"{path}:{number}: repeated trace key {key}")
        rows[key] = obj
    if not rows:
        raise ValueError(f"{path}: empty trace")
    return rows

def compare(left, right, atol=0.0):
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    a, b = load(left), load(right)
    if set(a) != set(b):
        return {"status": "unpaired", "left_only": len(a.keys()-b.keys()), "right_only": len(b.keys()-a.keys())}
    # Validate the complete paired dataset before reporting any numeric/coordinate
    # divergence: an early mismatch must never hide a later provenance conflict.
    for key in sorted(a):
        x, y = a[key], b[key]
        for field in PROVENANCE:
            if x[field] != y[field]:
                return {"status": "provenance_mismatch", "key": key, "field": field}
    for key in sorted(a):
        x, y = a[key], b[key]
        if x["coordinate"] != y["coordinate"]:
            return {"status": "coordinate_mismatch", "key": key, "left": x["coordinate"], "right": y["coordinate"]}
        if len(x["value"]) != len(y["value"]) or any(abs(i-j) > atol for i,j in zip(x["value"], y["value"])):
            return {"status": "numeric_mismatch", "key": key, "left": x["value"], "right": y["value"]}
    return {"status": "matched", "count": len(a)}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("vulkan"); p.add_argument("unity")
    p.add_argument("--atol", type=float, default=0.0)
    args = p.parse_args()
    try:
        result = compare(args.vulkan, args.unity, args.atol)
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "matched" else 1)
