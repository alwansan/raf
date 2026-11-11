"""Stage Windows animated Forward and compare safe hashes against Mesa."""
import argparse
import json
from pathlib import Path

from gfxlab.tools.gfx121_prepare_warp import finalize_draw, stage_draw
from gfxlab.tools.gfx125_batch_warp_report import capture_hashes
from gfxlab.tools.gfx129_stage_animated_forward import prepare
from gfxlab.tools.original_model_probe import stage_originals

POSES = tuple(f"C{clip}P{pose}" for clip in range(3) for pose in range(5))


def stage(zip2, root, reference):
    source = stage_originals(zip2, root / "source")
    draw = stage_draw(source, root / "draw")
    poses = root / "poses"
    report = prepare(source, draw / "mesh.bin", poses)
    actual = {row["sample"]: row["vertex_sha256"] for row in report["samples"]}
    expected = json.loads(reference.read_text())
    if tuple(actual) != POSES or any(actual[name] != expected[name]["vertex_sha256"] for name in POSES):
        raise ValueError("Windows source-derived animation input differs from Mesa")
    finalize_draw(draw, camera_mesh=b"".join((poses / (name + ".bin")).read_bytes() for name in POSES))


def audit(root, reference):
    expected = json.loads(reference.read_text())
    captures = {}
    for name in POSES:
        raw = (root / "captures" / (name + ".rgba")).read_bytes()
        hashes = capture_hashes(raw)
        alpha = raw[3::4]
        if set(alpha) != {0, 255} or alpha.count(255) < 100:
            raise ValueError("Invalid animation capture coverage")
        captures[name] = {**hashes, "covered_pixels": alpha.count(255),
                          "mesa_coverage_exact": hashes["coverage_sha256"] == expected[name]["coverage_sha256"],
                          "mesa_rgba_exact": hashes["rgba_sha256"] == expected[name]["rgba_sha256"]}
    unique = [len({captures[name]["rgba_sha256"] for name in POSES[start:start+5]}) for start in (0, 5, 10)]
    if unique != [1, 5, 5]:
        raise ValueError("Animation positive or constant control did not reproduce")
    return {"experiment": "GFX130", "renderer": "Windows D3D11 WARP", "frames": captures,
            "distinct_per_clip": unique, "cross_renderer_rgb_error_measured": False,
            "unity_clip_playback_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("private", "reference"):
        parser.add_argument("--" + name, type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--zip2", type=Path)
    mode.add_argument("--safe", type=Path)
    args = parser.parse_args()
    if args.zip2:
        stage(args.zip2, args.private, args.reference)
    else:
        result = audit(args.private, args.reference)
        args.safe.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))
