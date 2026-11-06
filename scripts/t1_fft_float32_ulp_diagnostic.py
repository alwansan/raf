#!/usr/bin/env python3
"""Optional binary32 ULP context for the first differing paired FFT coordinate."""
import argparse
import json
import math
import struct
from scripts.t1_fft_coordinate_probe_compare import read_samples, first_difference

def ulp32_gap(a, b):
    """Return ULP separation for finite binary32 values, or None if out of range."""
    if a == b:
        return 0
    try:
        words = [struct.unpack(">I", struct.pack(">f", value))[0] for value in (a, b)]
    except (OverflowError, struct.error):
        return None
    if any((word & 0x7f800000) == 0x7f800000 for word in words):
        return None
    def ordered(word):
        return (~word & 0xffffffff) if word & 0x80000000 else (word | 0x80000000)
    return abs(ordered(words[0]) - ordered(words[1]))

def diagnose(vulkan, unity):
    result = first_difference(vulkan, unity)
    if result["status"] != "different":
        return result
    key = tuple(result[field] for field in ("pass", "x", "y", "channel"))
    return dict(result, float32_ulp_gap=ulp32_gap(vulkan[key], unity[key]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("vulkan")
    parser.add_argument("unity")
    args = parser.parse_args()
    print(json.dumps(diagnose(read_samples(args.vulkan), read_samples(args.unity)), sort_keys=True))

if __name__ == "__main__":
    main()
