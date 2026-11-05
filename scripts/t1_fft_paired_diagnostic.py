"""Emit bounded diagnostics for private paired pass-zero readbacks."""
import argparse
import json
from pathlib import Path

from scripts.t1_fft_first_pass_channel_diagnostic import analyze as analyze_channels
from scripts.t1_fft_pass0_spatial_diagnostic import analyze as analyze_spatial
from scripts.t1_fft_readback_parity import PIXEL, SENTINEL, read_image


def diagnose(reference: bytes, candidate: bytes, width: int, height: int) -> dict:
    spatial = analyze_spatial(reference, candidate, width, height)
    joint = [(a, b) for a, b in zip(PIXEL.iter_unpack(reference), PIXEL.iter_unpack(candidate))
             if a != SENTINEL and b != SENTINEL]
    channel = None
    if joint:
        left, right = zip(*joint)
        result = analyze_channels(left, right, atol=1e-4, rtol=1e-5)
        channel = {
            "jointly_written": len(joint),
            "identity_mismatch_components": result["identity_mismatch_count"],
            "best_mismatch_components": result["best_mismatch_count"],
            "best_nonfinite_components": result["best_nonfinite_count"],
            "permutation_improves": result["permutation_improves"],
            "full_match": spatial["identity"]["coverage_mismatches"] == 0
                and result["best_mismatch_count"] == result["best_nonfinite_count"] == 0,
        }
    return {"spatial": spatial, "channel": channel}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    args = parser.parse_args()
    try:
        if not (1 <= args.width <= 2048 and 1 <= args.height <= 2048):
            raise ValueError("Invalid extent")
        size = args.width * args.height * PIXEL.size
        result = diagnose(read_image(args.reference, size), read_image(args.candidate, size),
                          args.width, args.height)
    except (OSError, ValueError):
        parser.exit(2, "Invalid private paired FFT capture\n")
    print("RAFT_T1_PAIRED_DIAGNOSTIC " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
