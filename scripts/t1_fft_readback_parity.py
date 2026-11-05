"""Compare private RGBA32F readbacks from original-DXBC Vulkan and Unity.

The two input blobs for each backend must contain the exact uploaded bytes.
Readbacks must be tightly packed little-endian RGBA, in the same row order.
This compares two captures; it does not authenticate their producers.
"""
import argparse
import json
import math
from pathlib import Path
import struct

PIXEL = struct.Struct("<4f")
SENTINEL = (8192.0,) * 4


def read_image(path: Path, size: int) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(size + 1)
    if len(data) != size:
        raise ValueError("Unexpected image byte length")
    return data


def compare_pass(reference: bytes, candidate: bytes) -> dict:
    if len(reference) != len(candidate) or not reference or len(reference) % PIXEL.size:
        raise ValueError("Invalid paired RGBA32F images")
    compared = missing = invalid = outside = 0
    for expected, actual in zip(PIXEL.iter_unpack(reference), PIXEL.iter_unpack(candidate)):
        if not all(map(math.isfinite, expected + actual)):
            invalid += 1
            continue
        written_expected = expected != SENTINEL
        written_actual = actual != SENTINEL
        if written_expected != written_actual:
            missing += 1
        elif written_expected:
            compared += 1
            if not all(math.isclose(x, y, rel_tol=1e-5, abs_tol=1e-4)
                       for x, y in zip(expected, actual)):
                outside += 1
    return {
        "compared_written_pixels": compared,
        "write_coverage_mismatch_pixels": missing,
        "nonfinite_pixels": invalid,
        "outside_tolerance_pixels": outside,
        "match": compared > 0 and missing == invalid == outside == 0,
    }


def compare_captures(reference: Path, candidate: Path, width: int, height: int) -> dict:
    if not (1 <= width <= 2048 and 1 <= height <= 2048):
        raise ValueError("Invalid capture extent")
    size = width * height * PIXEL.size
    for name in ("source", "butterfly"):
        expected = read_image(reference / (name + ".rgba32f"), size)
        actual = read_image(candidate / (name + ".rgba32f"), size)
        if expected != actual or any(not all(map(math.isfinite, pixel))
                                     for pixel in PIXEL.iter_unpack(expected)):
            raise ValueError("Captures do not share finite, byte-identical inputs")
    passes = [
        compare_pass(read_image(reference / name, size), read_image(candidate / name, size))
        for name in ("pass0.rgba32f", "pass1.rgba32f")
    ]
    return {"input_bytes_match": True, "passes": passes,
            "both_passes_match": all(result["match"] for result in passes)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    args = parser.parse_args()
    try:
        result = compare_captures(args.reference, args.candidate, args.width, args.height)
    except (OSError, ValueError):
        parser.exit(2, "Invalid private capture pair\n")
    print(json.dumps(result))
    return 0 if result["both_passes_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
