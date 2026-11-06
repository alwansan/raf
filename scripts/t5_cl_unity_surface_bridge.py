#!/usr/bin/env python3
"""Join source-pinned Unity performance intervals to contemporaneous stale SF windows.

Read-only bounded analysis. Unity Update FPS is NOT a guarantee that frames
were presented; stale SurfaceFlinger is NOT proof the game froze.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import statistics
from scripts.t5_cl_fps_cohort_gate import load_samples as load_sf

MAX_BYTES = 2_000_000
MAX_LINES = 3000
MAX_GAP_MS = 15_000
KEY = re.compile(r"^[a-zA-Z][a-zA-Z_0-9]*$")


def millis(value):
    if type(value) is not str or not value.endswith("Z"):
        raise ValueError("Missing timezone-aware UTC sample date")
    try:
        dt = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("Malformed UTC sample date") from exc
    return int(dt.timestamp() * 1000)


def _numeric(x):
    return type(x) in (int, float) and math.isfinite(x)


def detail_fields(text):
    if type(text) is not str or not 0 < len(text) <= 10_000:
        raise ValueError("Malformed bounded Unity performance detail")
    fields = {}
    for segment in text.split("; "):
        if "=" not in segment:
            raise ValueError("Unexpected Unity performance field")
        k, v = segment.split("=", 1)
        if not KEY.fullmatch(k) or k in fields:
            raise ValueError("Duplicate or invalid Unity performance key")
        fields[k] = v
    return fields


def scene_window_provenance(fields, scene):
    """Don't convert older unlabeled intervals into confirmed same-scene frames."""
    names = ("frame_window_start_scene", "frame_window_end_scene",
             "frame_window_active_scene_changes", "frame_window_content_scene_events",
             "frame_window_active_scene_stable", "frame_window_content_stable")
    present = [name in fields for name in names]
    if not any(present):
        return "legacy_unlabeled"
    if not all(present):
        raise ValueError("Partial mixed-scene telemetry provenance")
    try:
        active_changes = int(fields[names[2]])
        content_events = int(fields[names[3]])
    except ValueError as exc:
        raise ValueError("Invalid scene transition counter") from exc
    if active_changes < 0 or content_events < 0:
        raise ValueError("Negative scene transition counter")
    if fields[names[4]] not in ("True", "False") or fields[names[5]] not in ("True", "False"):
        raise ValueError("Invalid mixed-scene telemetry boolean")
    start, end = fields[names[0]], fields[names[1]]
    if not start or len(start) > 80 or not end or len(end) > 80 or end != scene:
        raise ValueError("Invalid start/end scene identity")
    expected_active = active_changes == 0 and start == end
    expected_content = expected_active and content_events == 0
    if (fields[names[4]] != str(expected_active)
            or fields[names[5]] != str(expected_content)):
        raise ValueError("Contradictory scene provenance flags")
    return "tagged_stable_content" if expected_content else "tagged_mixed_loading"


def load_unity(path):
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Missing, linked or oversized Unity diagnostic JSONL")
    parsed = []
    prior_seq, prior_ts = 0, 0
    with path.open(encoding="utf-8") as stream:
        for row_text in stream:
            if len(parsed) >= MAX_LINES or not row_text.strip():
                raise ValueError("Invalid Unity JSONL row count or blank")
            row = json.loads(row_text)
            if type(row) is not dict or type(row.get("session")) is not str:
                raise ValueError("Malformed Unity JSONL structure")
            seq = row.get("sequence")
            ts = millis(row.get("utc"))
            if type(seq) is not int or seq <= prior_seq or ts < prior_ts:
                raise ValueError("Non-monotone Unity log record")
            prior_seq, prior_ts = seq, ts
            if row.get("area") == "performance" and row.get("operation") == "sample":
                fields = detail_fields(row.get("detail"))
                try:
                    frames = int(fields["interval_frames"])
                    samples = int(fields["frame_samples"])
                    overflow = int(fields["frame_sample_overflow"])
                    width = int(fields["width"])
                    height = int(fields["height"])
                    fps = float(fields["fps"])
                    p95 = float(fields["frame_p95_ms"])
                    scene = fields["scene"]
                    orientation = fields["orientation"]
                except (ValueError, TypeError, KeyError) as exc:
                    raise ValueError("Incomplete or invalid Unity interval fields") from exc
                if not all(_numeric(z) for z in (fps, p95)):
                    raise ValueError("Nonfinite Unity frame metric")
                if not scene or len(scene) > 80 or any(x in scene for x in "/\\:"):
                    raise ValueError("Unsafe/unknown scene label")
                provenance = scene_window_provenance(fields, scene)
                parsed.append({"at_ms": ts, "scene": scene, "frames": frames,
                               "samples": samples, "overflow": overflow,
                               "fps": fps, "p95_ms": p95, "width": width,
                               "height": height, "orientation": orientation,
                               "scene_window_provenance": provenance})
    if not parsed:
        raise ValueError("No game-side Unity performance intervals")
    return parsed


def valid_unity(p):
    return (p["frames"] >= 30 and p["frames"] == p["samples"]
            and p["overflow"] == 0 and 0 < p["fps"] <= 1000
            and 0 < p["p95_ms"] < 120_000
            and p["width"] > 0 and p["height"] > 0
            and p["orientation"] == "Landscape")


def stale_windows(sf_rows):
    # Split runs when a nonstale sample intervenes or the logger has a gap.
    windows = []
    current = []
    prev_time = None
    for r in sf_rows:
        ts = r["timestamp_unix_ms"]
        stale = r.get("frame_telemetry_stale") is True and r.get("state") == "game_running"
        if not stale or (prev_time is not None and ts - prev_time > MAX_GAP_MS):
            if current:
                windows.append((current[0], current[-1], len(current)))
            current = []
        if stale:
            current.append(ts)
        prev_time = ts
    if current:
        windows.append((current[0], current[-1], len(current)))
    return windows


def _stats(rows):
    fps = sorted(r["fps"] for r in rows)
    interval_p95 = sorted(r["p95_ms"] for r in rows)
    if not fps:
        return {"intervals": 0, "median_fps": None, "median_of_interval_frame_p95_ms": None}
    return {
        "intervals": len(fps),
        "median_fps": round(statistics.median(fps), 2),
        # Median of 5-second-window p95 figures != combined per-frame p95.
        "median_of_interval_frame_p95_ms": round(statistics.median(interval_p95), 2),
        "fps_range": [round(fps[0], 2), round(fps[-1], 2)],
    }


def analyze(unity, sf, session):
    windows = stale_windows(sf)
    qualified = [x for x in unity if valid_unity(x)]
    overlap = [x for x in qualified if any(a <= x["at_ms"] <= b for a, b, _ in windows)]
    scenes = {}
    for r in overlap:
        scenes.setdefault(r["scene"], []).append(r)
    scene_evidence = {
        key: sum(x["scene_window_provenance"] == key for x in qualified)
        for key in ("legacy_unlabeled", "tagged_stable_content", "tagged_mixed_loading")
    }
    return {
        "session": session,
        "unity_qualified_scene_window_provenance": scene_evidence,
        "tagged_stable_scene_does_not_prove_same_world_or_camera": True,
        "sf_total_samples": len(sf),
        "sf_stale_sample_count": sum(x.get("frame_telemetry_stale") is True for x in sf),
        "sf_stale_windows": len(windows),
        "unity_total_performance_intervals": len(unity),
        "unity_qualified_intervals": len(qualified),
        "qualified_unity_intervals_during_sf_stale": len(overlap),
        "unity_during_sf_stale_by_scene": {k: _stats(v) for k, v in sorted(scenes.items())},
        "unity_whole_session_by_scene": {
            k: _stats([v for v in qualified if v["scene"] == k])
            for k in sorted({v["scene"] for v in qualified})
        },
        "unity_frame_source": "Time.unscaledDeltaTime / Unity capture window, not screen-present proof",
        "sf_frame_source": "SurfaceFlinger --latency, external presentation estimate",
        "unity_logged_frames_do_not_prove_presented_frames": True,
        "sf_stale_does_not_prove_game_freeze": True,
        "gameplay_scene_and_binary_equivalence_unproven": True,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--unity-a", type=Path, required=True)
    p.add_argument("--sf-a", type=Path, required=True)
    p.add_argument("--unity-b", type=Path, required=True)
    p.add_argument("--sf-b", type=Path, required=True)
    args = p.parse_args()
    first = analyze(load_unity(args.unity_a), load_sf(args.sf_a), "220911-559")
    second = analyze(load_unity(args.unity_b), load_sf(args.sf_b), "230108-327")
    print("T5_CL_UNITY_SURFACE_BRIDGE " + json.dumps(
        {"first": first, "second": second, "cross_session_gameplay_fps_gain_proven": False},
        sort_keys=True))


if __name__ == "__main__":
    main()
