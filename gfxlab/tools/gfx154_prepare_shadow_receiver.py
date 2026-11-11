"""Stage the original M02 Forward screen-space shadow receiver candidate."""
import argparse
from pathlib import Path
import shutil

from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.gfx119_prepare_draw import fixture_consumer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "base", "private"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.stage, True, fixture_consumer(args.private),
                   engine_keywords=("DIRECTIONAL", "SHADOWS_SCREEN"))
    if not result["gles_offline_link_passed"]:
        raise ValueError("Original shadow receiver pair failed to link")
    for name in ("mesh.bin", "indices.bin"):
        shutil.copyfile(args.base / name, args.private / name)
