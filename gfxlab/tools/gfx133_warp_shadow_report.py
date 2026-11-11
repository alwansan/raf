"""Validate controlled ShadowCaster depth masks from Windows."""
import argparse
import hashlib
import json
from pathlib import Path

CONTROLS = ("native", "solid", "transparent", "depth-off")


def audit(captures, mesa):
    rows = {}
    expected = json.loads(mesa.read_text())
    for name in CONTROLS:
        raw = (captures / (name + ".mask")).read_bytes()
        if len(raw) != 256 * 256 or not set(raw) <= {0, 255}:
            raise ValueError("Unexpected shadow depth mask")
        digest = hashlib.sha256(raw).hexdigest()
        rows[name] = {"covered_pixels": raw.count(255), "coverage_sha256": digest,
                      "mesa_coverage_exact": digest == expected[name]}
    if not (100 <= rows["native"]["covered_pixels"] <= rows["solid"]["covered_pixels"]
            and rows["transparent"]["covered_pixels"] == rows["depth-off"]["covered_pixels"] == 0):
        raise ValueError("Windows shadow depth controls failed")
    return {"experiment": "GFX133", "renderer": "Windows D3D11 WARP", "controls": rows,
            "unity_variant_selection_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("captures", "mesa", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.captures, args.mesa)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
