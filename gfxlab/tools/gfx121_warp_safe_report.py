"""Summarize original DXBC WARP readbacks without publishing source pixels."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

CASES = ("light","dark","flat","nonmetal")


def report(draw, captures):
    rgba = {}
    for case in CASES:
        pixels = np.frombuffer((captures/(case+".rgba")).read_bytes(),dtype=np.uint8)
        if pixels.size != 256*256*4:
            raise ValueError("Wrong Windows readback size")
        pixels = pixels.reshape(-1,4)
        if set(np.unique(pixels[:,3])) != {0,255}:
            raise ValueError("Unexpected Windows coverage")
        rgba[case] = pixels
    baseline = rgba["light"]
    controls = {case:int(np.any(baseline[:,:3] != rgba[case][:,:3],axis=1).sum()) for case in CASES[1:]}
    coverage = {case:int((pixels[:,3]==255).sum()) for case,pixels in rgba.items()}
    if min(controls.values()) < 100 or min(coverage.values()) < 100 or np.any(rgba["dark"][:,:3]):
        raise ValueError("Original Windows shader control failed")
    sha = lambda b:hashlib.sha256(b).hexdigest()
    rows = {case:dict(covered_pixels=coverage[case],rgba_sha256=sha(pixels.tobytes()),
        coverage_sha256=sha(pixels[:,3].tobytes())) for case,pixels in rgba.items()}
    return dict(experiment="GFX121",renderer="Windows Direct3D 11 WARP",source_dxbc_draw_completed=True,
                dxbc_sha256={name:sha((draw/(name+".dxbc")).read_bytes()) for name in ("vertex","fragment")},
                captures=rows,control_rgb_changed_pixels=controls,game_scene_matched=False,
                full_adreno_pixel_comparison=False,phase_closed=False)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("draw","captures","safe"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    result=report(a.draw,a.captures)
    a.safe.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
