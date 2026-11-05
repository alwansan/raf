#!/usr/bin/env python3
"""Source-free aggregate RGBA32F comparison; private pixel bytes never printed."""
import argparse
import json
import math
import struct
from pathlib import Path

def ordered_bits(bits):
    return (~bits & 0xffffffff) if bits & 0x80000000 else (bits | 0x80000000)

def signature(expected, observed, *, atol=1e-5, rtol=1e-4):
    if len(expected) != len(observed) or len(expected) % 16:
        raise ValueError("RGBA32F inputs must have equal whole-pixel byte lengths")
    channels = [dict(compared=0, mismatched=0, nonfinite=0, signed_positive=0,
                     signed_negative=0, max_ulp=0, max_absolute_error=0.0) for _ in range(4)]
    for offset in range(0, len(expected), 4):
        c = channels[(offset // 4) % 4]
        ab, bb = struct.unpack_from("<I", expected, offset)[0], struct.unpack_from("<I", observed, offset)[0]
        a, b = struct.unpack("<f", struct.pack("<I", ab))[0], struct.unpack("<f", struct.pack("<I", bb))[0]
        c["compared"] += 1
        if not (math.isfinite(a) and math.isfinite(b)):
            c["nonfinite"] += 1
            c["mismatched"] += 1
            continue
        error = abs(a - b)
        c["max_absolute_error"] = max(c["max_absolute_error"], error)
        c["max_ulp"] = max(c["max_ulp"], abs(ordered_bits(ab) - ordered_bits(bb)))
        if error > atol + rtol * abs(a):
            c["mismatched"] += 1
            c["signed_positive" if b > a else "signed_negative"] += 1
    return {"pixels": len(expected) // 16, "channels": channels,
            "all_within_tolerance": all(c["mismatched"] == 0 for c in channels)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected", type=Path, required=True)
    p.add_argument("--observed", type=Path, required=True)
    p.add_argument("--atol", type=float, default=1e-5)
    p.add_argument("--rtol", type=float, default=1e-4)
    a = p.parse_args()
    if not all(math.isfinite(x) and x >= 0 for x in (a.atol, a.rtol)):
        p.error("tolerances must be nonnegative and finite")
    print(json.dumps(signature(a.expected.read_bytes(), a.observed.read_bytes(),
                               atol=a.atol, rtol=a.rtol), sort_keys=True))

if __name__ == "__main__":
    main()
