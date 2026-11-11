"""GFX146: source-safe Cull Back/Front/Off geometry projection comparison.

This is CPU analysis of the controlled source-original M03-1 mesh,
NOT a GPU Cull differential nor proof of actual Unity runtime Cull state.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from gfxlab.tools.gfx144_coplanar_face_audit import closest_pairs, project

SIDE = 256
TOL = 1e-7


def source_cull_fallback_verified(source: dict) -> bool:
    if source.get("experiment") != "GFX145" or source.get("original_material_slots") != 7:
        raise ValueError("Wrong source-original Cull attestation")
    rows = source.get("all_passes")
    if not isinstance(rows, list) or len(rows) != 7 or any(
        row.get("fallback_cull_enum") != "back" or
        row.get("runtime_unity_effective_cull_verified") is not False or
        row.get("material_slots_with_matching_saved_float") != 0
        for row in rows
    ):
        raise ValueError("Original source Cull fallback or override evidence drift")
    if source.get("original_unity_Cull_runtime_verified") is not False:
        raise ValueError("Cannot claim effective Unity Cull runtime")
    return True


def evaluate(screen, depths, triangles, points):
    """Mirror OpenGL CCW front-face default and GL_CULL_BACK/GL_CULL_FRONT."""
    p0,p1,p2 = screen[triangles[:,0]], screen[triangles[:,1]], screen[triangles[:,2]]
    area = (p1[:,0]-p0[:,0])*(p2[:,1]-p0[:,1])-(p2[:,0]-p0[:,0])*(p1[:,1]-p0[:,1])
    ccw = area > 0
    cw = area < 0
    if not ccw.any() or not cw.any():
        raise ValueError("Fixture has no source front/back face classes")
    off, _, _, hits_off = closest_pairs(screen, depths, triangles, points)
    back, _, _, hits_back = closest_pairs(screen, depths, triangles[ccw], points)
    front, _, _, hits_front = closest_pairs(screen, depths, triangles[cw], points)
    if np.any(hits_off <= 0):
        raise ValueError("GFX124 source coverage mismatch")
    off_depth = off[:,0]
    result = {
        "total_triangles":int(len(triangles)),
        "source_screen_CCW_front_triangles":int(ccw.sum()),
        "source_screen_CW_back_triangles":int(cw.sum()),
        "original_covered_pixels":int(len(points)),
        "CullBack_covered_original_pixels":int((hits_back>0).sum()),
        "CullBack_missing_original_pixels":int((hits_back==0).sum()),
        "CullBack_visible_depth_changed_pixels":int(
            ((hits_back>0)&(abs(back[:,0]-off_depth)>TOL)).sum()),
        "CullFront_covered_original_pixels":int((hits_front>0).sum()),
        "CullFront_missing_original_pixels":int((hits_front==0).sum()),
        "CullFront_visible_depth_changed_pixels":int(
            ((hits_front>0)&(abs(front[:,0]-off_depth)>TOL)).sum()),
        "CullOff_covered_original_pixels":int((hits_off>0).sum()),
    }
    return result


def inspect(apk_path: Path, source_path: Path, expected_sha: str) -> dict:
    if sha256(apk_path.read_bytes()).hexdigest() != expected_sha:
        raise ValueError("Not the exact owner signed original APK")
    source = json.loads(source_path.read_text())
    source_cull_fallback_verified(source)
    with ZipFile(apk_path) as apk:
        prefix="assets/M03-1/"
        vertices,screen,depth = project(apk.read(prefix+"mesh.bin"),
                                        apk.read(prefix+"light-2.bin"),
                                        apk.read(prefix+"light-3.bin"))
        raw=apk.read(prefix+"indices.bin")
        if len(raw)%6:
            raise ValueError("Corrupt M03-1 mesh indices")
        triangles=np.frombuffer(raw,dtype="<u2").reshape(-1,3)
        if triangles.max()>=len(vertices):
            raise ValueError("M03-1 invalid source vertex index")
        rgba=np.frombuffer(apk.read(prefix+"light.rgba"),dtype=np.uint8).reshape(SIDE,SIDE,4)
        y,x=np.where(rgba[:,:,3]==255)
        points=np.column_stack((x+0.5,y+0.5))
        result=evaluate(screen,depth,triangles,points)
    return {
        "experiment":"GFX146",
        "original_signed_apk_sha256":expected_sha,
        "source_cull_fallback":"back",
        "source_shader_passes_with_back_fallback":7,
        "source_material_slots_with_matching_dynamic_cull_override":0,
        "controlled_fixture_current_cull_mode":"off",
        **result,
        "CullBack_CPU_projection_preserves_entire_original_coverage_and_nearest_depth":bool(
            result["CullBack_missing_original_pixels"]==0 and
            result["CullBack_visible_depth_changed_pixels"]==0),
        "original_Unity_dynamic_cull_effective_state_verified":False,
        "GPU_CullBack_Adreno_Mesa_RGB_parity_verified":False,
        "original_game_pc_android_pixel_parity":False,
        "phase_closed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apk",type=Path,required=True)
    p.add_argument("--source-cull-safe",type=Path,required=True)
    p.add_argument("--expected-apk-sha256",required=True)
    p.add_argument("--safe",type=Path,required=True)
    args=p.parse_args()
    result=inspect(args.apk,args.source_cull_safe,args.expected_apk_sha256)
    args.safe.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
