"""Extend the reviewed private B02 capture to all five exact Texture classes."""
import argparse
from pathlib import Path
from tools.gt_top_original_renderer.stage import render as base_render

ANCHOR="if (asset.ClassID != 28) // Exact Unity Texture2D class, no inference."
REPLACE="if (asset.ClassID is not (28 or 84 or 89 or 117 or 187)) // Exact supported texture classes."

def render(base):
    text=base_render(base).decode("utf-8")
    if text.count(ANCHOR)!=1:
        raise ValueError("unreviewed_private_texture_capture_anchor")
    return text.replace(ANCHOR,REPLACE).encode("utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-helper",type=Path,required=True)
    p.add_argument("--destination",type=Path,required=True)
    a=p.parse_args()
    if a.base_helper.is_symlink() or a.destination.is_symlink() or a.destination.exists():
        raise ValueError("unsafe_private_stage")
    with a.destination.open("xb") as f:
        f.write(render(a.base_helper.read_bytes()))
    print("GT_TOP_TYPED_RESOURCE_CAPTURE_STAGED=true")

if __name__=="__main__":
    main()
