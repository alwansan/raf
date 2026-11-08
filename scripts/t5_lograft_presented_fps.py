#!/usr/bin/env python3
"""Conservative flat JSONL SurfaceFlinger FPS estimates; NOT Unity FPS."""
import argparse
import json
import math
import statistics
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100000

def no_duplicate_keys(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key: " + k)
        d[k] = v
    return d

def summarize(rows, *, expected_session):
    if not isinstance(expected_session, str) or not expected_session.strip():
        raise ValueError("explicit session identity required")
    values, rejected, count = [], {}, 0
    for row in rows:
        count += 1
        if count > MAX_ROWS:
            raise ValueError("too many rows")
        if not isinstance(row, dict):
            raise ValueError("non-object row")
        if "session_id" in row and row["session_id"] != expected_session:
            raise ValueError("session identity conflict")
        # Flat projection contract. Real CL nested records need verified adapter.
        val = row.get("presented_fps_estimate")
        if val is None:
            rejected["missing_estimate"] = rejected.get("missing_estimate", 0) + 1
            continue
        if type(val) not in (int, float) or not math.isfinite(val) or val <= 0 or val > 360:
            rejected["invalid_estimate"] = rejected.get("invalid_estimate", 0) + 1
            continue
        values.append(float(val))
    ordered = sorted(values)
    def percentile(p):
        if not ordered:
            return None
        return round(ordered[max(0, math.ceil(len(ordered) * p) - 1)], 3)
    return {"session_id": expected_session, "rows": count, "valid_estimates": len(values),
            "rejected": rejected,
            "median_presented_fps_estimate": round(statistics.median(values), 3) if values else None,
            "p05_presented_fps_estimate": percentile(.05),
            "p95_presented_fps_estimate": percentile(.95),
            "source": "SurfaceFlinger presented-fps estimate (not Unity FPS)",
            "unity_frame_p95_ms": None, "gpu_frame_ms": None,
            "comparability": "requires same installed APK/OBB, scene, render resolution and refresh settings"}

def load(path):
    if path.is_symlink() or not path.is_file() or not (0 < path.stat().st_size <= MAX_BYTES):
        raise ValueError("unsafe or oversized input")
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                raise ValueError("blank row")
            yield json.loads(line, object_pairs_hook=no_duplicate_keys)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", type=Path)
    p.add_argument("--session-id", required=True)
    a = p.parse_args()
    print(json.dumps(summarize(load(a.jsonl), expected_session=a.session_id), sort_keys=True))
