"""Audit private Windows ForwardAdd readback and emit safe aggregate metrics."""
import argparse
import json
from pathlib import Path

import numpy as np

from gfxlab.tools.gfx125_batch_warp_report import capture_hashes


def audit(captures, mesa):
    def raw(name):
        return (captures / (name + ".rgba")).read_bytes()

    base, add, combined = (np.frombuffer(raw(name), dtype=np.uint8).reshape(-1, 4)
                           for name in ("light", "add_only", "add_lit"))
    off_exact, reject_exact = (raw(name) == raw("light") for name in ("add_off", "add_reject"))
    expected = np.minimum(base[:, :3].astype(np.int16) + add[:, :3], 255)
    max_delta = int(np.abs(expected - combined[:, :3]).max())
    affected = int(np.any(base[:, :3] != combined[:, :3], axis=1).sum())
    alpha_exact = np.array_equal(base[:, 3], combined[:, 3])
    if not (off_exact and reject_exact and alpha_exact and affected >= 100 and max_delta <= 1):
        raise ValueError(f"ForwardAdd fixture controls failed: {off_exact=} {reject_exact=} "
                         f"{alpha_exact=} {affected=} {max_delta=}")
    hashes = capture_hashes(raw("add_lit"))
    return {"experiment": "GFX128", "renderer": "Windows D3D11 WARP",
            "covered_pixels": int(np.count_nonzero(combined[:, 3])),
            "additional_light_changed_pixels": affected, "max_rgb_delta_from_saturating_sum": max_delta,
            "zero_light_preserved_base": off_exact, "depth_reject_preserved_base": reject_exact,
            "alpha_and_coverage_exact": alpha_exact, "hashes": hashes,
            "mesa_coverage_exact": hashes["coverage_sha256"] == mesa["coverage_sha256"],
            "mesa_rgba_exact": hashes["rgba_sha256"] == mesa["rgba_sha256"],
            "runtime_unity_state_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("captures", "mesa", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.captures, json.loads(args.mesa.read_text()))
    args.safe.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
