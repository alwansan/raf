#!/usr/bin/env python3
"""Source-free RGBA32F channel diagnostic; never emits raw pixels."""
import argparse
import itertools
import json
import math
import struct
from pathlib import Path

PIXEL = struct.Struct("<4f")
CHANNELS = "RGBA"

def read_pixels(path):
    data = Path(path).read_bytes()
    if len(data) % PIXEL.size:
        raise ValueError("RGBA32F payload must be a multiple of 16 bytes")
    return list(PIXEL.iter_unpack(data))

def analyze(reference, candidate, atol=1e-5, rtol=1e-5):
    if len(reference) != len(candidate):
        raise ValueError("pixel counts differ")
    if not reference:
        raise ValueError("empty image")
    if atol < 0 or rtol < 0 or not math.isfinite(atol + rtol):
        raise ValueError("tolerances must be finite and nonnegative")
    matrix = []
    for i in range(4):
        row = []
        for j in range(4):
            comparable = mismatch = nonfinite = 0
            max_error = 0.0
            sum_error = 0.0
            for ref, got in zip(reference, candidate):
                a, b = ref[i], got[j]
                if not math.isfinite(a) or not math.isfinite(b):
                    nonfinite += 1
                    continue
                comparable += 1
                delta = abs(a - b)
                max_error = max(max_error, delta)
                sum_error += delta
                if delta > atol + rtol * abs(a):
                    mismatch += 1
            row.append({"comparable": comparable, "mismatch": mismatch,
                        "nonfinite": nonfinite, "max_abs": max_error,
                        "mean_abs": sum_error / comparable if comparable else None})
        matrix.append(row)
    permutations = []
    for perm in itertools.permutations(range(4)):
        mismatches = sum(matrix[i][perm[i]]["mismatch"] for i in range(4))
        nonfinite = sum(matrix[i][perm[i]]["nonfinite"] for i in range(4))
        permutations.append((nonfinite, mismatches, perm))
    permutations.sort()
    best = permutations[0]
    identity = tuple(range(4))
    return {"pixels": len(reference), "identity": [matrix[i][i] for i in range(4)],
            "best_channel_permutation": "".join(CHANNELS[i] for i in best[2]),
            "best_mismatch_count": best[1], "best_nonfinite_count": best[0],
            "identity_mismatch_count": sum(matrix[i][i]["mismatch"] for i in range(4)),
            "permutation_improves": best[2] != identity and
                (best[0], best[1]) < (sum(matrix[i][i]["nonfinite"] for i in range(4)),
                                        sum(matrix[i][i]["mismatch"] for i in range(4)))}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference")
    parser.add_argument("candidate")
    parser.add_argument("--atol", type=float, default=1e-5)
    parser.add_argument("--rtol", type=float, default=1e-5)
    args = parser.parse_args()
    print(json.dumps(analyze(read_pixels(args.reference), read_pixels(args.candidate),
                             args.atol, args.rtol), sort_keys=True))

if __name__ == "__main__":
    main()
