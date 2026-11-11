"""Stage original indexed positions, influences, matrices and CPU references for the APK."""
import argparse
import json
import struct
from pathlib import Path

from gfxlab.tools.gfx107_source_bindpose_math import mul
from gfxlab.tools.gfx108_original_indexed_skin_cpu import audit
from gfxlab.tools.original_model_probe import stage_originals

EXPECTED = {"M00": (375, 3), "M01": (5095, 100), "M02": (1666, 8),
            "M04": (2445, 100), "M05": (4452, 2)}


def write_case(path, positions, weights, world, bindposes, reference):
    palette = [mul(w, b) for w, b in zip(world, bindposes, strict=True)]
    with path.open("xb") as out:
        out.write(struct.pack("<4sII", b"G109", len(positions), len(palette)))
        # GLSL matrices are column-major. Source and CPU math are row-major.
        for matrix in palette:
            out.write(struct.pack("<16f", *(matrix[4*r+c] for c in range(4) for r in range(4))))
        for point, influences, expected in zip(positions, weights, reference, strict=True):
            padded = influences + [(0.0, 0)] * (4 - len(influences))
            out.write(struct.pack("<3f4f4I3f", *point, *(w for w, _ in padded),
                                  *(i for _, i in padded), *expected))


def main():
    ap = argparse.ArgumentParser()
    for name in ("zip2", "stage", "assets", "safe"):
        ap.add_argument("--" + name, type=Path, required=True)
    args = ap.parse_args()
    args.assets.mkdir(parents=True, exist_ok=True)
    seen = {}

    def consume(model, positions, weights, world, bindposes, reference):
        shape = len(positions), len(world)
        if EXPECTED.get(model) != shape:
            raise ValueError(f"Unexpected source vertex/palette counts for {model}")
        write_case(args.assets / (model + ".bin"), positions, weights, world, bindposes, reference)
        seen[model] = shape

    audit(stage_originals(args.zip2, args.stage), consume)
    if seen != EXPECTED:
        raise ValueError("Incomplete source case set")
    args.safe.write_text(json.dumps({"experiment": "GFX109", "source_shapes": seen,
                                    "gpu_result_pending": True, "phase_closed": False}, indent=2) + "\n")


if __name__ == "__main__":
    main()
