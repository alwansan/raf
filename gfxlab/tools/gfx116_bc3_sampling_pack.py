"""Decode each authenticated BC3 mip independently for GPU comparison."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct

from PIL import Image
from gfxlab.tools.gfx116_m02_bc3_source import mip_layout


def decode_mip(data, width, height, *, fourcc=b"DXT5"):
    flags = 0x81007  # DDSD_CAPS, HEIGHT, WIDTH, PIXELFORMAT, LINEARSIZE
    header = [124, flags, height, width, len(data), 0, 0, *([0]*11),
              32, 4, int.from_bytes(fourcc,"little"), 0, 0, 0, 0, 0,
              0x1000, 0, 0, 0, 0]
    with Image.open(io.BytesIO(b"DDS " + struct.pack("<31I", *header) + data)) as image:
        if image.size != (width,height):
            raise ValueError("DDS decoder shape changed")
        return image.convert("RGBA").tobytes()


def pack(private, source, out):
    report = json.loads(source.read_text())
    out.mkdir(parents=True, exist_ok=False)
    for role, entry in report["textures"].items():
        raw = (private / (role+".bc3")).read_bytes()
        rgba = bytearray()
        for (i,w,h,start,size), meta in zip(mip_layout(1024,1024,11),entry["mips"],strict=True):
            block = raw[start:start+size]
            if hashlib.sha256(block).hexdigest() != meta["sha256"]:
                raise ValueError("Original mip identity mismatch")
            rgba.extend(decode_mip(block,w,h))
        (out / (role+".bc3")).write_bytes(raw)
        (out / (role+".rgba")).write_bytes(rgba)
    return sum(3*max(1,1024>>i)**2 for i in range(11))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("private","source","assets"):
        parser.add_argument("--"+name,type=Path,required=True)
    args = parser.parse_args()
    print("GFX116_REFERENCE_TEXELS",pack(args.private,args.source,args.assets))
