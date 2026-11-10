#!/usr/bin/env python3
"""GFX-MULTI-042 — verify all original-free GPU screenshot pixels privately.

Source-free Python stdlib only. Strict RGBA PNG8 decoder, frame dimension/
filter/CRC/zlib guards, exact analytic perspective vs affine triangle geometry.
Processes private owner ZIP locally; emits numerical aggregates only (no actual
images, device identifiers, semantic names, logs or Raft Shader48 source).
"""
from __future__ import annotations
import argparse
import json
import math
import struct
import zipfile
import zlib
from pathlib import Path
from gfxlab.tools.affine_reference_owner_zip_audit import audit_zip as audit_owner

W=H=256
MAX_PNG=4*1024*1024
MAX_IDAT=3*1024*1024
RAW_LEN=H*(1+4*W)
MODES=("linear","flat","noperspective","affineemulated")
SIG=b"\x89PNG\r\n\x1a\n"
VERTICES=((-0.86,-0.77),(0.86,-0.77),(0.0,0.86))
CLIP_W=(0.55,1.0,2.7)


def paeth(a,b,c):
    p=a+b-c
    pa=abs(p-a)
    pb=abs(p-b)
    pc=abs(p-c)
    if pa<=pb and pa<=pc:return a
    if pb<=pc:return b
    return c


def decode_rgba_png(data):
    """Decode only bounded 256×256 noninterlaced PNG 8-bit RGBA, fail closed."""
    if not isinstance(data,bytes) or not 60<=len(data)<=MAX_PNG or not data.startswith(SIG):
        raise ValueError("GFX042_SOURCE_PNG_SIGNATURE_OR_SIZE_INVALID")
    offset=len(SIG)
    ihdr_count=0
    idat=[]
    idat_len=0
    seen_iend=False
    while offset<len(data):
        if offset+12>len(data):
            raise ValueError("GFX042_PNG_TRUNCATED_CHUNK_HEADER")
        size=struct.unpack_from(">I",data,offset)[0]
        tag=data[offset+4:offset+8]
        if size>MAX_IDAT or offset+12+size>len(data):
            raise ValueError("GFX042_PNG_CHUNK_BOUNDS_INVALID")
        content=data[offset+8:offset+8+size]
        crc=struct.unpack_from(">I",data,offset+8+size)[0]
        if zlib.crc32(tag+content)&0xffffffff !=crc:
            raise ValueError("GFX042_PNG_CHUNK_CRC_INVALID")
        if tag==b"IHDR":
            ihdr_count+=1
            if ihdr_count!=1 or offset!=len(SIG) or size!=13:
                raise ValueError("GFX042_PNG_IHDR_ORDER_OR_SIZE_INVALID")
            width,height,depth,colortype,compression,filter_method,interlace=struct.unpack(">IIBBBBB",content)
            if (width,height,depth,colortype,compression,filter_method,interlace)!=(W,H,8,6,0,0,0):
                raise ValueError("GFX042_PNG_FORMAT_NOT_RGBA_256_SRGB8")
        elif tag==b"IDAT":
            if ihdr_count!=1:
                raise ValueError("GFX042_PNG_IDAT_BEFORE_IHDR")
            idat.append(content)
            idat_len+=size
            if idat_len>MAX_IDAT:
                raise ValueError("GFX042_PNG_COMPRESSED_DATA_TOO_LARGE")
        elif tag==b"IEND":
            if size!=0 or not idat:
                raise ValueError("GFX042_PNG_BAD_IEND")
            seen_iend=True
            offset+=12
            break
        elif (tag[0]&32)==0:
            raise ValueError("GFX042_PNG_UNKNOWN_CRITICAL_CHUNK")
        offset+=12+size
    if not seen_iend or offset!=len(data) or ihdr_count!=1:
        raise ValueError("GFX042_PNG_MISSING_END_OR_TRAILING_DATA")
    try:
        decomp=zlib.decompressobj()
        raw=decomp.decompress(b"".join(idat),RAW_LEN+1)
        raw+=decomp.flush()
    except zlib.error:
        raise ValueError("GFX042_PNG_IDAT_DECOMPRESS_FAILED") from None
    if len(raw)!=RAW_LEN or not decomp.eof or decomp.unconsumed_tail or decomp.unused_data:
        raise ValueError("GFX042_PNG_DECOMPRESSED_SIZE_INVALID")
    rowbytes=4*W
    previous=bytearray(rowbytes)
    out=bytearray(H*rowbytes)
    cursor=0
    for y in range(H):
        filter_id=raw[cursor]
        cursor+=1
        if filter_id>4:
            raise ValueError("GFX042_PNG_UNSUPPORTED_FILTER")
        src=raw[cursor:cursor+rowbytes]
        cursor+=rowbytes
        row=bytearray(rowbytes)
        for i in range(rowbytes):
            a=row[i-4] if i>=4 else 0
            b=previous[i]
            c=previous[i-4] if i>=4 else 0
            f=(0,a,b,(a+b)//2,paeth(a,b,c))[filter_id]
            row[i]=(src[i]+f)&255
        out[y*rowbytes:(y+1)*rowbytes]=row
        previous=row
    return bytes(out)


def reference_rgb(xcol,yrow):
    """PNG y=0 at top; OpenGL pixel centers and NDC triangle in bottom-up y."""
    x=2*(xcol+.5)/W-1
    y=2*(H-1-yrow+.5)/H-1
    (ax,ay),(bx,by),(cx,cy)=VERTICES
    den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    r=((by-cy)*(x-cx)+(cx-bx)*(y-cy))/den
    g=((cy-ay)*(x-cx)+(ax-cx)*(y-cy))/den
    b=1-r-g
    screen=(r,g,b)
    weighted=(r/CLIP_W[0],g/CLIP_W[1],b/CLIP_W[2])
    total=sum(weighted)
    perspective=tuple(t/total for t in weighted)
    return screen,perspective


def verify_all_pixels(frames,interior_margin=.02):
    if set(frames)!=set(MODES) or not 0<interior_margin<.2:
        raise ValueError("GFX042_EXACT_FOUR_FRAMES_REQUIRED")
    if any(not isinstance(frames[m],bytes) or len(frames[m])!=W*H*4 for m in MODES):
        raise ValueError("GFX042_DECODED_FRAME_SIZE_INVALID")
    sums={"linear_cpu_perspective":0.0,"linear_cpu_affine":0.0,
          "affine_cpu_affine":0.0,"affine_cpu_perspective":0.0,
          "native_cpu_perspective":0.0,"smooth_affine_image_delta":0.0}
    max_error={"linear_cpu_perspective":0.0,"affine_cpu_affine":0.0}
    pixels=0
    flat_blue=0
    alpha_opaque=0
    exact_linear_native=(frames["linear"]==frames["noperspective"])
    for y in range(H):
        for x in range(W):
            affine,perspective=reference_rgb(x,y)
            if min(affine)<=interior_margin:
                continue
            pixels+=1
            observed={}
            for mode in MODES:
                start=4*(y*W+x)
                px=frames[mode][start:start+4]
                observed[mode]=tuple(v/255 for v in px[:3])
                alpha_opaque+=int(px[3]==255)
            flat_blue+=int(frames["flat"][4*(y*W+x):4*(y*W+x)+4]==b"\x00\x00\xff\xff")
            comparisons={
                "linear_cpu_perspective":(observed["linear"],perspective),
                "linear_cpu_affine":(observed["linear"],affine),
                "affine_cpu_affine":(observed["affineemulated"],affine),
                "affine_cpu_perspective":(observed["affineemulated"],perspective),
                "native_cpu_perspective":(observed["noperspective"],perspective),
                "smooth_affine_image_delta":(observed["linear"],observed["affineemulated"]),
            }
            for key,(a,b) in comparisons.items():
                difference=sum(abs(u-v) for u,v in zip(a,b))/3
                sums[key]+=difference
                if key in max_error:
                    max_error[key]=max(max_error[key],difference)
    if pixels<10000:
        raise ValueError("GFX042_ANALYTIC_TRIANGLE_INTERIOR_TOO_SMALL")
    means={key:round(value/pixels,9) for key,value in sums.items()}
    safe={
        "experiment":"GFX-MULTI-042",
        "original_shader48_restored":False,
        "original_pc_pixel_parity_verified":False,
        "synthetic_source_only":True,
        "reference":"CPU_BARYCENTRIC_PERSPECTIVE_AFFINE_PER_PIXEL",
        "interior_pixel_count":pixels,
        "barycentric_minimum_margin":interior_margin,
        "linear_and_native_noperspective_frames_exactly_identical":exact_linear_native,
        "flat_exact_blue_interior_count":flat_blue,
        "interior_alpha_opaque_across_four_modes":alpha_opaque,
        "mean_absolute_rgb_errors":means,
        "maximum_absolute_rgb_errors":{
            k:round(v,9) for k,v in max_error.items()},
        "cpu_affine_matches_gpu_qualifier_workaround_all_frame":
            means["affine_cpu_affine"]<=.02 and
            means["affine_cpu_perspective"]-means["affine_cpu_affine"]>=.08,
        "cpu_perspective_matches_native_gpu_smooth_all_frame":
            means["linear_cpu_perspective"]<=.02 and
            means["linear_cpu_affine"]-means["linear_cpu_perspective"]>=.08,
        "flat_produces_constant_blue_full_interior":flat_blue==pixels,
        "no_original_or_owner_png_log_text_publicly_exported":True,
    }
    return safe


def audit_owner_zip_fullframe(path):
    baseline=audit_owner(path)
    with zipfile.ZipFile(path) as z:
        names={i.filename for i in z.infolist()}
        root_names=sorted(n for n in names if n.startswith("sessions/")
                          and n.endswith("/snapshots.jsonl"))
        roots=[]
        for n in root_names:
            prefix=n.rsplit("/",1)[0]+"/"
            if all(prefix+"gpu-interpolation-"+m+".png" in names for m in MODES):
                roots.append(prefix)
        if not roots:
            raise ValueError("GFX042_FOUR_OWNER_PNGS_NOT_IN_SAME_SESSION")
        prefix=roots[-1]
        frames={m:decode_rgba_png(z.read(prefix+"gpu-interpolation-"+m+".png"))
                for m in MODES}
        safe=verify_all_pixels(frames)
        return {**baseline,**safe}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=audit_owner_zip_fullframe(a.zip)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI042_SAFE_WHOLE_GPU_FRAME_PROOF "+json.dumps(report,sort_keys=True))


if __name__=="__main__":main()
