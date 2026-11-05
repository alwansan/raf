"""Bounded output-coordinate hypotheses for private FFT pass-zero captures."""
import argparse
import json
import math
from pathlib import Path

from scripts.t1_fft_readback_parity import PIXEL, SENTINEL, read_image


def analyze(reference, candidate, width, height):
    if not (1 <= width <= 2048 and 1 <= height <= 2048):
        raise ValueError("Invalid fixture extent")
    if len(reference) != width * height * PIXEL.size or len(candidate) != len(reference):
        raise ValueError("Invalid capture byte length")
    expected, actual = (
        {(i % width, i // width): pixel for i, pixel in enumerate(PIXEL.iter_unpack(image))
         if pixel != SENTINEL}
        for image in (reference, candidate)
    )
    if not expected or not actual:
        raise ValueError("Both captures must have observable writes")

    # Map candidate coordinates into reference coordinates. Out-of-bounds
    # writes are counted as extra coverage; they cannot silently disappear.
    transforms = {
        "identity": lambda x, y: (x, y),
        "flip_x": lambda x, y: (width - 1 - x, y),
        "flip_y": lambda x, y: (x, height - 1 - y),
        "flip_xy": lambda x, y: (width - 1 - x, height - 1 - y),
        "shift_x_minus_one": lambda x, y: (x - 1, y),
        "shift_x_plus_one": lambda x, y: (x + 1, y),
        "shift_y_minus_one": lambda x, y: (x, y - 1),
        "shift_y_plus_one": lambda x, y: (x, y + 1),
    }
    # A global image flip can move a sparse footprint entirely. Also test
    # mirrors around the occupied reference bounds without dropping writes.
    xs, ys = zip(*expected)
    x_sum, y_sum = min(xs) + max(xs), min(ys) + max(ys)
    if min(xs) != max(xs) and x_sum != width - 1:
        transforms["footprint_flip_x"] = lambda x, y: (x_sum - x, y)
    if min(ys) != max(ys) and y_sum != height - 1:
        transforms["footprint_flip_y"] = lambda x, y: (x, y_sum - y)

    report = {}
    for name, transform in transforms.items():
        remapped = {transform(*coord): pixel for coord, pixel in actual.items()}
        common = expected.keys() & remapped.keys()
        coverage = len(expected.keys() ^ remapped.keys())
        mismatch = nonfinite = 0
        for coord in common:
            left, right = expected[coord], remapped[coord]
            if not all(map(math.isfinite, left + right)):
                nonfinite += 1
            elif not all(math.isclose(a, b, abs_tol=1e-4, rel_tol=1e-5)
                         for a, b in zip(left, right)):
                mismatch += 1
        report[name] = {
            "jointly_written": len(common), "coverage_mismatches": coverage,
            "numeric_mismatches": mismatch, "nonfinite_pixels": nonfinite,
            "full_match": bool(common) and coverage == mismatch == nonfinite == 0,
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    args = parser.parse_args()
    try:
        if not (1 <= args.width <= 2048 and 1 <= args.height <= 2048):
            raise ValueError("Invalid fixture extent")
        size = args.width * args.height * PIXEL.size
        result = analyze(read_image(args.reference, size), read_image(args.candidate, size),
                         args.width, args.height)
    except (OSError, ValueError):
        parser.exit(2, "Invalid private FFT capture pair\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
