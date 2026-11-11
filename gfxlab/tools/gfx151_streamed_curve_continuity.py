"""Inspect source-derived curve junctions before reconstructing continuous clips."""
import argparse
import json
import math
from pathlib import Path

LIMIT = 1e-5


def summarize(inputs):
    reports = []
    for index, clip in enumerate(inputs["clips"]):
        start, stop = clip["start"], clip["stop"]
        if not math.isfinite(start) or not math.isfinite(stop) or stop <= start:
            raise ValueError("Invalid source clip interval")
        deltas = []
        for curve in clip["curves"]:
            keys = curve["keys"]
            for left, right in zip(keys, keys[1:]):
                width = right["time"] - left["time"]
                if not math.isfinite(width) or width <= 0:
                    raise ValueError("Unordered source curve keys")
                if not start <= right["time"] <= stop:
                    continue
                a, b, c, d = left["coeff"]
                delta = abs(((a * width + b) * width + c) * width + d - right["coeff"][3])
                if not math.isfinite(delta):
                    raise ValueError("Nonfinite source curve endpoint")
                deltas.append(delta)
        reports.append({"clip_index": index, "streamed_curve_count": len(clip["curves"]),
                        "checked_junctions": len(deltas), "above_tolerance": sum(d > LIMIT for d in deltas),
                        "max_absolute_junction_error": max(deltas, default=0)})
    return {"experiment": "GFX151", "junction_tolerance": LIMIT, "clips": reports,
            "continuous_unity_playback_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("clips", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.clips.read_text())), indent=2))
