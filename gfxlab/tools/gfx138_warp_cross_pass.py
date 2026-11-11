"""GFX138: fail-closed original Windows WARP Forward/Deferred coverage comparison.

Only lossless alpha masks and source-safe aggregate hashes leave the private CI
runner.  This tests a controlled draw, not Unity pass-selection or its G-buffer.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

SIZE = 256
BYTES = SIZE * SIZE * 4
FORWARD = ("light", "dark", "flat", "nonmetal")
DEFERRED = ("native-rt0", "flat-rt0", "nonmetal-rt0")


def coverage(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != BYTES:
        raise ValueError("Wrong WARP RGBA readback length: " + path.name)
    alpha = data[3::4]
    if set(alpha) != {0, 255}:
        raise ValueError("Nonbinary WARP coverage: " + path.name)
    return alpha


def audit(forward: Path, deferred: Path, source: Path, mesa: Path) -> dict:
    evidence = json.loads(source.read_text())
    reference = json.loads(mesa.read_text())
    if (evidence.get("experiment") != "GFX121"
            or evidence.get("source_dxbc_draw_completed") is not True
            or reference.get("deferred", {}).get("same_coverage_as_forward") is not True):
        raise ValueError("Wrong original Forward or Mesa evidence")
    prior = evidence["captures"]
    expected = reference["deferred"]["covered_pixels"]
    if expected != reference["covered_pixels"] or expected <= 0 or expected >= SIZE * SIZE:
        raise ValueError("Mesa reference count drift")

    masks = {}
    for name in FORWARD:
        current = coverage(forward / (name + ".rgba"))
        prior_row = prior[name]
        if (sha256(current).hexdigest() != prior_row["coverage_sha256"]
                or current.count(255) != prior_row["covered_pixels"]):
            raise ValueError("Original Forward WARP reference changed: " + name)
        masks["forward-" + name] = current
    for name in DEFERRED:
        masks["deferred-" + name] = coverage(deferred / (name + ".rgba"))

    base = masks["forward-light"]
    if base.count(255) != expected:
        raise ValueError("Forward/Mesa covered pixel count drift")
    mismatches = {
        name: sum(a != b for a, b in zip(mask, base, strict=True))
        for name, mask in masks.items()
    }
    if any(mismatches.values()):
        raise ValueError("Forward/Deferred pixel-location coverage mismatch: " + str(mismatches))
    digest = sha256(base).hexdigest()
    return {
        "experiment": "GFX138",
        "renderer": "Windows Direct3D 11 WARP",
        "original_dxbc_forward_deferred_mask_exact": True,
        "cases_checked": list(masks),
        "covered_pixels": expected,
        "coverage_sha256": digest,
        "pixel_location_mismatch_counts": mismatches,
        "comparison_against_original_forward_capture": True,
        "mesa_reference_coverage_count_matched": True,
        "unity_original_pass_selection_verified": False,
        "unity_original_gbuffer_format_verified": False,
        "original_game_pixel_parity": False,
        "phase_closed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for field in ("forward", "deferred", "source", "mesa", "safe"):
        parser.add_argument("--" + field, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.forward, args.deferred, args.source, args.mesa)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
