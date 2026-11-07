#!/usr/bin/env python3
"""Fail-closed Unity internal interval cohort analyzer; never pooled frame quantiles."""
import argparse
import json
import math
import statistics
from pathlib import Path

MAX_BYTES = 2_000_000
MAX_ROWS = 3000

def parse_detail(value):
    if not isinstance(value, str):
        raise ValueError("Missing performance detail")
    out = {}
    for item in value.split(";"):
        if not item.strip():
            continue
        if "=" not in item:
            raise ValueError("Malformed detail field")
        key, val = item.strip().split("=", 1)
        key = key.strip()
        if not key or key in out:
            raise ValueError("Duplicate or empty detail key")
        out[key] = val.strip()
    return out

def numeric(data, key, *, integer=False, positive=True):
    value = data.get(key)
    try:
        n = int(value) if integer else float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Missing/invalid " + key)
    if not math.isfinite(n) or (positive and n <= 0):
        raise ValueError("Nonpositive/nonfinite " + key)
    if integer and str(n) != str(value):
        raise ValueError("Noncanonical integer " + key)
    return n

def analyze_rows(rows, minimum_frames=30):
    if type(minimum_frames) is not int or minimum_frames < 1:
        raise ValueError("Invalid startup threshold")
    cohorts = {}
    last_key = None
    epoch = 0
    count = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid JSONL object")
        if row.get("area") != "performance" or row.get("operation") != "sample":
            continue
        count += 1
        if count > MAX_ROWS:
            raise ValueError("Too many performance samples")
        data = parse_detail(row.get("detail"))
        scene = data.get("scene")
        if not scene or len(scene) > 128:
            raise ValueError("Missing/invalid scene")
        refresh = numeric(data, "refresh_hz")
        frames = numeric(data, "frame_samples", integer=True)
        fps = numeric(data, "fps")
        p50 = numeric(data, "frame_p50_ms")
        p95 = numeric(data, "frame_p95_ms")
        width = numeric(data, "width", integer=True)
        height = numeric(data, "height", integer=True)
        if not (1 <= refresh <= 360 and fps <= 1000 and p50 <= p95 <= 60000):
            raise ValueError("Implausible frame statistics")
        key = (scene, refresh, width, height)
        if key != last_key:
            epoch += 1
            last_key = key
        bucket = cohorts.setdefault(epoch, {"scene": scene, "refresh_hz": refresh,
                                            "width": width, "height": height,
                                            "total_intervals": 0, "startup_excluded": 0,
                                            "_fps": [], "_p95": []})
        bucket["total_intervals"] += 1
        if frames < minimum_frames:
            bucket["startup_excluded"] += 1
        else:
            bucket["_fps"].append(fps)
            bucket["_p95"].append(p95)
    result = []
    for n, bucket in cohorts.items():
        fps, p95 = bucket.pop("_fps"), bucket.pop("_p95")
        bucket["epoch"] = n
        bucket["qualified_intervals"] = len(fps)
        bucket["median_interval_fps"] = round(statistics.median(fps), 3) if fps else None
        bucket["median_of_interval_p95_ms_not_pooled_frames"] = round(statistics.median(p95), 3) if p95 else None
        result.append(bucket)
    return {"performance_intervals": count, "epochs": result,
            "cross_epoch_aggregation": "prohibited",
            "frame_p95_semantics": "median of interval p95 values, not pooled per-frame p95",
            "gpu_time_inferred": False}

def unique_json_object(pairs):
    """Reject ambiguous duplicate JSONL object keys at any nesting level."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSONL key: " + key)
        result[key] = value
    return result

def load(path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Unsafe or oversized JSONL")
    with path.open(encoding="utf-8") as f:
        rows = []
        for line in f:
            if not line.strip():
                raise ValueError("Blank JSONL row")
            rows.append(json.loads(line, object_pairs_hook=unique_json_object))
            if len(rows) > MAX_ROWS:
                raise ValueError("Too many JSONL rows")
    return rows

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze_rows(load(args.jsonl)), ensure_ascii=False, sort_keys=True))
