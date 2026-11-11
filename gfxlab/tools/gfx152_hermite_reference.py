"""Verify the source cubic-to-Hermite conversion at interior times."""
import argparse
import json
import math
from pathlib import Path


def evaluate(coefficients, width, u):
    a, b, c, d = coefficients
    t = width * u
    source = ((a*t+b)*t+c)*t+d
    end = ((a*width+b)*width+c)*width+d
    slope = (3*a*width+2*b)*width+c
    u2, u3 = u*u, u*u*u
    hermite = ((2*u3-3*u2+1)*d + (u3-2*u2+u)*width*c
               + (-2*u3+3*u2)*end + (u3-u2)*width*slope)
    return source, hermite


def audit(inputs):
    results = []
    for index, clip in enumerate(inputs["clips"]):
        samples = 0
        worst = 0.0
        for curve in clip["curves"]:
            keys = curve["keys"]
            for left, right in zip(keys, keys[1:]):
                width = right["time"] - left["time"]
                if not math.isfinite(width) or width <= 0:
                    raise ValueError("Invalid segment duration")
                for u in (0.125, 0.375, 0.625, 0.875):
                    time = left["time"] + width*u
                    if not clip["start"] <= time <= clip["stop"]:
                        continue
                    source, reconstructed = evaluate(left["coeff"], width, u)
                    if not math.isfinite(reconstructed) or not math.isclose(
                            source, reconstructed, abs_tol=1e-9, rel_tol=1e-9):
                        raise ValueError("Hermite reconstruction diverges")
                    worst = max(worst, abs(source-reconstructed))
                    samples += 1
        results.append({"clip_index": index, "interior_scalar_samples": samples,
                        "max_absolute_error": worst})
    if len(results) != 3 or results[0]["interior_scalar_samples"] or any(
            row["interior_scalar_samples"] == 0 for row in results[1:]):
        raise ValueError("Expected one constant and two moving clips")
    return {"experiment": "GFX152", "clips": results, "unity_animator_verified": False,
            "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.inputs.read_text())), indent=2))
