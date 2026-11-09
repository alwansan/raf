#!/usr/bin/env python3
"""Read-only PNG color evidence audit for T3. Never treats synthetic lab as Raft proof."""
import argparse
import json
import struct
import zlib
from collections import Counter
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"

def decode_rgb(path):
    data = Path(path).read_bytes()
    if not data.startswith(SIGNATURE):
        raise ValueError("not_png")
    pos = 8
    chunks = []
    while pos + 12 <= len(data):
        size = struct.unpack_from(">I", data, pos)[0]
        typ = data[pos+4:pos+8]
        end = pos + 12 + size
        if end > len(data):
            raise ValueError("truncated_chunk")
        body = data[pos+8:pos+8+size]
        crc = struct.unpack_from(">I", data, pos+8+size)[0]
        if zlib.crc32(typ + body) & 0xffffffff != crc:
            raise ValueError("bad_crc")
        chunks.append((typ, body))
        pos = end
        if typ == b"IEND":
            break
    if not chunks or chunks[-1][0] != b"IEND" or pos != len(data):
        raise ValueError("missing_iend_or_trailing_data")
    ihdr = next((b for t,b in chunks if t == b"IHDR"), None)
    if ihdr is None or len(ihdr) != 13:
        raise ValueError("bad_ihdr")
    width,height,depth,kind,compression,filtering,interlace = struct.unpack(">IIBBBBB", ihdr)
    if not width or not height or width*height > 30000000:
        raise ValueError("invalid_dimensions")
    if depth != 8 or kind not in (2,6) or compression or filtering or interlace:
        raise ValueError("unsupported_png_format")
    channels = 3 if kind == 2 else 4
    stride = width*channels
    # Bound output during inflation; malformed IDAT must not allocate unlimited RAM.
    expected = (stride + 1) * height
    decoder = zlib.decompressobj()
    raw = decoder.decompress(b"".join(b for t,b in chunks if t == b"IDAT"), expected + 1)
    if (len(raw) != expected or not decoder.eof or decoder.unconsumed_tail
            or decoder.unused_data):
        raise ValueError("invalid_scanline_size_or_zlib_stream")
    rows = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filt = raw[offset]
        offset += 1
        row = bytearray(raw[offset:offset+stride])
        offset += stride
        if filt not in range(5):
            raise ValueError("invalid_filter")
        for i in range(stride):
            a = row[i-channels] if i >= channels else 0
            b = previous[i]
            c = previous[i-channels] if i >= channels else 0
            if filt == 1: value = a
            elif filt == 2: value = b
            elif filt == 3: value = (a+b)//2
            elif filt == 4:
                p=a+b-c
                da,db,dc=abs(p-a),abs(p-b),abs(p-c)
                value = a if da<=db and da<=dc else (b if db<=dc else c)
            else: value = 0
            row[i] = (row[i]+value)&255
        rows.append(row)
        previous = row
    return width,height,channels,rows

def audit(path):
    width,height,channels,rows = decode_rgb(path)
    # Center excludes screenshot borders; quadrants expose flat/black capture.
    regions = {"full":Counter(), "center":Counter(), "top_left":Counter(),
               "top_right":Counter(), "bottom_left":Counter(), "bottom_right":Counter()}
    visible = Counter()
    transparent_pixels = 0
    translucent_pixels = 0
    for y,row in enumerate(rows):
        for x in range(width):
            idx=x*channels
            rgb=tuple(row[idx:idx+3])
            if channels == 4:
                alpha = row[idx+3]
                if alpha == 0: transparent_pixels += 1
                elif alpha < 255: translucent_pixels += 1
                else: visible[rgb] += 1
            else:
                visible[rgb] += 1
            regions["full"][rgb]+=1
            if width//4 <= x < 3*width//4 and height//4 <= y < 3*height//4:
                regions["center"][rgb]+=1
            regions[("top_" if y<height//2 else "bottom_")+("left" if x<width//2 else "right")][rgb]+=1
    def summary(c):
        n=sum(c.values())
        return {"pixels":n,"unique_rgb":len(c),
                "black_fraction":round(sum(v for k,v in c.items() if max(k)<=8)/n,6) if n else None,
                "dominant_fraction":round(max(c.values())/n,6) if n else None}
    return {"width":width,"height":height,
            "alpha_zero_fraction":round(transparent_pixels/(width*height),6),
            "alpha_partial_fraction":round(translucent_pixels/(width*height),6),
            "opaque_unique_rgb":len(visible),
            "regions":{k:summary(v) for k,v in regions.items()},
            "evidence":"pixel_distribution_only_not_game_visual_acceptance"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("png",nargs="+",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=[]
    for path in args.png:
        try: result.append({"file":path.name,"result":audit(path)})
        except (ValueError,OSError,zlib.error) as exc:
            result.append({"file":path.name,"error":str(exc)})
    output=json.dumps({"schema":1,"files":result},indent=2,sort_keys=True)
    if args.output: args.output.write_text(output+"\n",encoding="utf-8")
    else: print(output)
    return 1 if any("error" in r for r in result) else 0

if __name__=="__main__":
    raise SystemExit(main())
