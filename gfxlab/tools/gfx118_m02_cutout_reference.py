"""Measure the M02 alpha-test coverage expected from the pinned Standard source."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from zipfile import ZipFile

import numpy as np

from gfxlab.tools.gfx114_m02_raster_reference import SIZE, edge, pose_positions
from gfxlab.tools.gfx117_m02_uv_inputs import LOD
from gfxlab.tools.gfx118_m02_original_forward import source_material
from gfxlab.tools.multi_shader_material_cb_payload095 import saved_values_private

POSES = ("C0P0","C1P0","C1P2","C2P0","C2P2")
OFFICIAL_ARCHIVE_SHA = "5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5"


def bilinear_alpha(image, u, v):
    h,w = image.shape
    x, y = u*w-0.5, v*h-0.5
    ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x-ix, y-iy
    low = image[iy % h,ix % w]*(1-fx) + image[iy % h,(ix+1) % w]*fx
    high = image[(iy+1) % h,ix % w]*(1-fx) + image[(iy+1) % h,(ix+1) % w]*fx
    return (low*(1-fy) + high*fy)/255.0


def coverage(points, camera, triangles, uv, alpha, tint_alpha, cutoff):
    screen = ((points.astype(np.float64) @ camera[:2,:3].T + camera[:2,3]) + 1)*SIZE/2
    covered = np.zeros((SIZE,SIZE),dtype=bool)
    after = covered.copy()
    discarded_fragments = 0
    for triangle in triangles:
        a,b,c = screen[triangle]
        ta,tb,tc = uv[triangle]
        area = edge(a,b,*c)
        if area == 0:
            continue
        if area < 0:
            b,c = c,b
            tb,tc = tc,tb
            area = -area
        low = np.maximum(0,np.ceil(np.minimum(np.minimum(a,b),c)-0.5).astype(int))
        high = np.minimum(SIZE-1,np.floor(np.maximum(np.maximum(a,b),c)-0.5).astype(int))
        if np.any(low > high):
            continue
        x = np.arange(low[0],high[0]+1)[None,:]+0.5
        y = np.arange(low[1],high[1]+1)[:,None]+0.5
        wa,wb,wc = edge(b,c,x,y),edge(c,a,x,y),edge(a,b,x,y)
        inside = (wa>=0)&(wb>=0)&(wc>=0)
        u = (wa*ta[0]+wb*tb[0]+wc*tc[0])/area
        v = (wa*ta[1]+wb*tb[1]+wc*tc[1])/area
        sample = bilinear_alpha(alpha,u,v) * tint_alpha
        clipped = sample < cutoff
        discarded_fragments += np.count_nonzero(inside & clipped)
        window = np.s_[low[1]:high[1]+1,low[0]:high[0]+1]
        covered[window] |= inside
        after[window] |= inside & ~clipped
    return {"raster_covered_pixels":int(covered.sum()),"cutout_covered_pixels":int(after.sum()),
            "coverage_pixels_removed":int((covered & ~after).sum()),
            "triangle_fragments_below_cutoff":int(discarded_fragments)}


def main():
    parser = argparse.ArgumentParser()
    for name in ("stage","assets","official","safe"):
        parser.add_argument("--"+name,type=Path,required=True)
    a = parser.parse_args()
    if hashlib.sha256(a.official.read_bytes()).hexdigest() != OFFICIAL_ARCHIVE_SHA:
        raise ValueError("Wrong Unity 2021.3.45f2 built-in source archive")
    with ZipFile(a.official) as z:
        source = z.read("CGIncludes/UnityStandardInput.cginc")
        core = z.read("CGIncludes/UnityStandardCore.cginc")
        if b"tex2D(_MainTex, uv).a * _Color.a" not in source or b"clip (alpha - _Cutoff);" not in core:
            raise ValueError("Official cutout contract not found")
    material, _, _, _ = source_material(a.stage)
    keywords = set(material["m_ValidKeywords"])
    if "_ALPHATEST_ON" not in keywords or "_SMOOTHNESS_TEXTURE_ALBEDO_CHANNEL_A" in keywords:
        raise ValueError("M02 alpha contract changed")
    saved = saved_values_private(material)
    tint_alpha, cutoff = saved["_Color"][1][3],saved["_Cutoff"][1][0]
    raw = (a.assets/"uv117.bin").read_bytes()
    st = struct.unpack_from("<4f",raw)
    uv = np.frombuffer(raw,dtype="<f4",offset=48).reshape(-1,2).astype(np.float64)
    uv = uv*np.asarray(st[:2])+np.asarray(st[2:])
    mesh = (a.assets/"raster115.bin").read_bytes()
    camera = np.frombuffer(mesh[:64],dtype="<f4").reshape(4,4).T
    triangles = np.frombuffer(mesh[64:],dtype="<u2").reshape(-1,3)
    texture = (a.assets/"basecolor.rgba").read_bytes()
    rows = []
    for level in LOD:
        size = 1024>>level
        offset = sum((1024>>i)**2*4 for i in range(level))
        alpha = np.frombuffer(texture,dtype=np.uint8,count=size*size*4,offset=offset).reshape(size,size,4)[:,:,3]
        for pose in POSES:
            result = coverage(pose_positions(a.assets/(pose+".bin")),camera,triangles,uv,alpha,tint_alpha,cutoff)
            rows.append({"pose":pose,"mip":level,**result})
    report = {"experiment":"GFX118-cutout-reference","cases":rows,
              "source_cutout_evaluated_on_cpu":True,"original_shader_gpu_draw_verified":False,
              "phase_closed":False}
    a.safe.write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    main()
