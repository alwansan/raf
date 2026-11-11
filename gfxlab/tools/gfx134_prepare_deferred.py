"""Prepare the exact M02 Deferred pair for an offscreen G-buffer test."""
import argparse
import json
from pathlib import Path
import shutil

from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.gfx119_prepare_draw import fixture_consumer


def prepare(stage, base, out, *, direct3d=False):
    result = audit(stage, not direct3d, fixture_consumer(out, direct3d=direct3d), pass_name="DEFERRED", engine_keywords=())
    for name in ("mesh.bin", "indices.bin"):
        shutil.copyfile(base / name, out / name)
    if direct3d:
        from gfxlab.tools.gfx121_prepare_warp import finalize_draw
        finalize_draw(out, deferred=True)
    return {"experiment": "GFX134", "source_sha": result["source_sha"],
            "exact_source_pair_count": result["exact_source_pair_count"],
            "gles_offline_link_passed": result["gles_offline_link_passed"],
            "stages": result["stages"], "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "base", "private", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--direct3d", action="store_true")
    args = parser.parse_args()
    result = prepare(args.stage, args.base, args.private, direct3d=args.direct3d)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
