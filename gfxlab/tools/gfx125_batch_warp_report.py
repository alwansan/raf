"""Compare source-safe hashes for the controlled Windows and Mesa Forward batches."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from gfxlab.tools.gfx121_warp_safe_report import report

SLOTS = ("M00-0", "M03-0", "M03-1")


def capture_hashes(pixels):
    if len(pixels) != 256 * 256 * 4:
        raise ValueError("Wrong capture size")
    return {"coverage_sha256": hashlib.sha256(pixels[3::4]).hexdigest(),
            "rgba_sha256": hashlib.sha256(pixels).hexdigest()}


def summarize(root, reference):
    mesa = json.loads(reference.read_text())
    slots = {}
    for name in SLOTS:
        current = report(root / "draw" / name, root / "captures" / name)
        slots[name] = {key: current[key] for key in ("dxbc_sha256", "captures", "control_rgb_changed_pixels")}
        for case, row in slots[name]["captures"].items():
            for key, digest in mesa[name][case].items():
                row["mesa_" + key + "_matches"] = row[key] == digest
    def pixels(slot, capture):
        return (root / "captures" / slot / (capture + ".rgba")).read_bytes()
    combined = pixels("M03-0", "combined")
    def rgba(raw):
        return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4)
    first, second, both = [rgba(raw) for raw in (pixels("M03-0", "light"), pixels("M03-1", "light"), combined)]
    a, b, c = [img[:, 3] != 0 for img in (first, second, both)]
    if not np.array_equal(c, a | b) or not np.all(np.all(both == first, axis=1) | np.all(both == second, axis=1)):
        raise ValueError("Windows combined draw disagrees with source material slots")
    exclusive = []
    for mask, img in ((a & ~b, first), (b & ~a, second)):
        if not mask.any() or not np.array_equal(img[mask], both[mask]):
            raise ValueError("Missing exclusive material contribution")
        exclusive.append(int(mask.sum()))
    mix = capture_hashes(combined)
    mix.update(covered_pixels=int(c.sum()), overlap_pixels=int((a & b).sum()), exclusive_pixels=exclusive)
    for key, digest in mesa["M03-combined"].items():
        mix["mesa_" + key + "_matches"] = mix[key] == digest
    return {"experiment": "GFX125", "renderer": "Windows Direct3D 11 WARP", "slots": slots,
            "m03_combined": mix, "cross_renderer_rgb_error_measured": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("private", "reference", "safe"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    result = summarize(args.private, args.reference)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
