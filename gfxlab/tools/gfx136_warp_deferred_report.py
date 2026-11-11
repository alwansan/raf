"""Validate the original Deferred shader's four controlled Windows MRT outputs."""
import argparse
import json
from pathlib import Path

import numpy as np

from gfxlab.tools.gfx125_batch_warp_report import capture_hashes


def audit(captures, mesa):
    reference = json.loads(mesa.read_text())["deferred"]["reference_hashes"]
    modes = ("native", "flat", "nonmetal")
    rows, images = {}, {}
    for mode in modes:
        for target in range(4):
            name = f"{mode}-rt{target}"
            raw = (captures / (name + ".rgba")).read_bytes()
            hashes = capture_hashes(raw)
            images[name] = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4)
            rows[name] = {"rgba_sha256": hashes["rgba_sha256"],
                          "mesa_rgba_exact": hashes["rgba_sha256"] == reference[name]}
    changes = {
        mode: [int(np.any(images[f"native-rt{target}"] != images[f"{mode}-rt{target}"], axis=1).sum())
               for target in range(4)] for mode in modes[1:]
    }
    alpha = images["native-rt0"][:, 3]
    covered = int((alpha == 255).sum())
    if (set(alpha) != {0, 255} or covered < 100 or changes["flat"][:2] != [0, 0]
            or changes["flat"][2] < 100 or changes["nonmetal"][1] < 100 or changes["nonmetal"][2] != 0):
        raise ValueError(f"Deferred material controls failed: {covered=} {changes=}")
    return {"experiment": "GFX136", "renderer": "Windows D3D11 WARP", "targets": rows,
            "covered_pixels": covered, "target0_coverage_sha256": capture_hashes(
                (captures / "native-rt0.rgba").read_bytes())["coverage_sha256"],
            "material_control_changed_pixels": changes, "unity_runtime_gbuffer_layout_verified": False,
            "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("captures", "mesa", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.captures, args.mesa)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
