#!/usr/bin/env python3
"""Identify earliest divergent private FFT RGBA32F pass; never print pixel values."""
import argparse
import json
import math
from pathlib import Path
from scripts.t1_fft_rgba_error_signature import signature

def compare_passes(pairs, *, atol=1e-5, rtol=1e-4):
    if not pairs:
        raise ValueError("at least one pass is required")
    if not all(math.isfinite(x) and x >= 0 for x in (atol, rtol)):
        raise ValueError("invalid tolerances")
    seen = set()
    results = []
    first = None
    for index, (name, reference, observed) in enumerate(pairs):
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError("pass names must be nonempty and unique")
        seen.add(name)
        if not reference or not observed:
            raise ValueError("empty capture")
        report = signature(reference, observed, atol=atol, rtol=rtol)
        failed = not report["all_within_tolerance"]
        if failed and first is None:
            first = {"index": index, "pass": name}
        results.append({
            "pass": name, "pixels": report["pixels"],
            "mismatch_by_channel": [c["mismatched"] for c in report["channels"]],
            "nonfinite_by_channel": [c["nonfinite"] for c in report["channels"]],
            "within_tolerance": not failed,
        })
    return {"first_divergence": first, "passes": results, "all_match": first is None}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Private JSON list: [{name,reference,observed}]")
    parser.add_argument("--atol", type=float, default=1e-5)
    parser.add_argument("--rtol", type=float, default=1e-4)
    args = parser.parse_args()
    try:
        entries = json.loads(args.manifest.read_text())
        if not isinstance(entries, list):
            raise ValueError("manifest must be a list")
        pairs = []
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"name", "reference", "observed"}:
                raise ValueError("invalid pass entry")
            pairs.append((entry["name"], Path(entry["reference"]).read_bytes(),
                          Path(entry["observed"]).read_bytes()))
        report = compare_passes(pairs, atol=args.atol, rtol=args.rtol)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, "Invalid private FFT pass manifest or capture: " + type(exc).__name__ + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
