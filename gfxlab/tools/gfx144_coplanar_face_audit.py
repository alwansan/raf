"""GFX144 — source-original M03-1 coplanar opposing-face hotspot audit.

Never upload a user's capture ZIP or original game APK to public CI.
Reports contain aggregates only. This controlled test is not proof of
original Unity ShaderLab Cull selection or full-game pixel parity.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

from gfxlab.tools.gfx124_batch_zip_audit import audit as audit_owner

SIDE = 256
DEPTH_TOLERANCE = 1e-7
ATTRIBUTE_TOLERANCE = 1e-5


def project(mesh: bytes, cb2: bytes, cb3: bytes):
    """Reproduce the original M03-1 controlled GLES vertex transform."""
    if len(mesh) % 48 or len(cb2) != 160 or len(cb3) != 336:
        raise ValueError("Unexpected original M03-1 vertex/UBO layout")
    vertices = np.frombuffer(mesh, dtype="<f4").reshape(-1, 12).astype(np.float64)
    a = np.frombuffer(cb2, dtype="<f4").reshape(10, 4).astype(np.float64)
    b = np.frombuffer(cb3, dtype="<f4").reshape(21, 4).astype(np.float64)
    if not np.isfinite(vertices).all() or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Nonfinite source geometry or projection")
    source = np.column_stack((vertices[:, :3], np.ones(len(vertices))))
    transformed = (source @ a[:4]) @ b[17:21]
    if np.any(abs(transformed[:, 3]) < 1e-8):
        raise ValueError("Degenerate source clip w")
    ndc = transformed[:, :3] / transformed[:, 3, None]
    return vertices, (ndc[:, :2] + 1) * (SIDE / 2), (ndc[:, 2] + 1) / 2


def closest_pairs(screen: np.ndarray, depths: np.ndarray, triangles: np.ndarray,
                  xy: np.ndarray):
    """Rasterize original triangles at GLES pixel centers; retain nearest two."""
    count = len(xy)
    nearest = np.full((count, 2), np.inf)
    ids = np.full((count, 2), -1, dtype=np.int32)
    weights = np.zeros((count, 2, 3), dtype=np.float64)
    hits = np.zeros(count, dtype=np.int32)
    for ti, t in enumerate(triangles):
        a, b, c = screen[t]
        area = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
        if abs(area) < 1e-12:
            continue
        subset = np.flatnonzero(
            (xy[:, 0] >= min(a[0], b[0], c[0]) - 1e-9) &
            (xy[:, 0] <= max(a[0], b[0], c[0]) + 1e-9) &
            (xy[:, 1] >= min(a[1], b[1], c[1]) - 1e-9) &
            (xy[:, 1] <= max(a[1], b[1], c[1]) + 1e-9))
        if not len(subset):
            continue
        p = xy[subset]
        w0 = ((b[0]-p[:, 0])*(c[1]-p[:, 1]) - (c[0]-p[:, 0])*(b[1]-p[:, 1])) / area
        w1 = ((c[0]-p[:, 0])*(a[1]-p[:, 1]) - (a[0]-p[:, 0])*(c[1]-p[:, 1])) / area
        w2 = 1-w0-w1
        valid = (w0 >= -1e-8) & (w1 >= -1e-8) & (w2 >= -1e-8)
        subset = subset[valid]
        if not len(subset):
            continue
        w = np.stack((w0[valid], w1[valid], w2[valid]), axis=1)
        hits[subset] += 1
        at = w @ depths[t]
        first = at < nearest[subset, 0]
        chosen = subset[first]
        nearest[chosen, 1] = nearest[chosen, 0]
        nearest[chosen, 0] = at[first]
        ids[chosen, 1] = ids[chosen, 0]
        ids[chosen, 0] = ti
        weights[chosen, 1] = weights[chosen, 0]
        weights[chosen, 0] = w[first]
        other = subset[~first]
        second = at[~first] < nearest[other, 1]
        chosen = other[second]
        nearest[chosen, 1] = at[~first][second]
        ids[chosen, 1] = ti
        weights[chosen, 1] = w[~first][second]
    return nearest, ids, weights, hits


def paired_faces(vertices, screen, triangles, ids, weights, valid):
    """Same position and UV, but opposite interpolated normal, winding and handedness."""
    paired = np.zeros(len(ids), dtype=bool)
    for pixel in np.flatnonzero(valid):
        t1, t2 = triangles[ids[pixel]]
        w1, w2 = weights[pixel]
        p1, p2 = w1 @ vertices[t1, :3], w2 @ vertices[t2, :3]
        uv1, uv2 = w1 @ vertices[t1, 10:12], w2 @ vertices[t2, 10:12]
        n1, n2 = w1 @ vertices[t1, 3:6], w2 @ vertices[t2, 3:6]
        norm = np.linalg.norm(n1) * np.linalg.norm(n2)
        a1, b1, c1 = screen[t1]
        a2, b2, c2 = screen[t2]
        area1 = (b1[0]-a1[0])*(c1[1]-a1[1])-(c1[0]-a1[0])*(b1[1]-a1[1])
        area2 = (b2[0]-a2[0])*(c2[1]-a2[1])-(c2[0]-a2[0])*(b2[1]-a2[1])
        paired[pixel] = bool(
            np.max(abs(p1-p2)) < ATTRIBUTE_TOLERANCE and
            np.max(abs(uv1-uv2)) < ATTRIBUTE_TOLERANCE and
            norm > 1e-9 and np.dot(n1,n2) / norm < -0.99 and
            area1 * area2 < 0 and
            (w1 @ vertices[t1,9]) * (w2 @ vertices[t2,9]) < 0)
    return paired


def png_readback(data):
    with Image.open(io.BytesIO(data)) as png:
        if png.format != "PNG" or png.size != (SIDE, SIDE):
            raise ValueError("Unexpected Android source PNG")
        return np.array(png.convert("RGBA"))[::-1].copy()


def inspect(apk_path: Path, log_path: Path, expected_sha: str):
    if sha256(apk_path.read_bytes()).hexdigest() != expected_sha:
        raise ValueError("APK differs from owner installed original reference")
    production = audit_owner(log_path, apk_path)
    if production["completed_tests"] != 9 or len(production["tests"]) != 9:
        raise ValueError("Original GFX124 owner batch incomplete")
    folder = "assets/M03-1/"
    with ZipFile(apk_path) as apk, ZipFile(log_path) as logs:
        vertices, screen, depths = project(
            apk.read(folder+"mesh.bin"), apk.read(folder+"light-2.bin"),
            apk.read(folder+"light-3.bin"))
        raw_indices = apk.read(folder+"indices.bin")
        if len(raw_indices) % 6:
            raise ValueError("Invalid M03-1 indexed geometry")
        triangles = np.frombuffer(raw_indices, dtype="<u2").reshape(-1, 3)
        if triangles.size == 0 or triangles.max() >= len(vertices):
            raise ValueError("M03-1 index out of range")
        ref = np.frombuffer(apk.read(folder+"light.rgba"), np.uint8).reshape(SIDE,SIDE,4)
        dev = png_readback(logs.read("M03-1-light.png"))
        if not np.array_equal(ref[:,:,3],dev[:,:,3]):
            raise ValueError("Geometry coverage differs before analysis")
        ys, xs = np.where(ref[:,:,3] == 255)
        points = np.column_stack((xs+0.5, ys+0.5))
        z, face_ids, weights, hits = closest_pairs(screen,depths,triangles,points)
        if np.any(hits==0) or np.any(face_ids[:,0]<0):
            raise ValueError("Original projection did not cover source readbacks")
        tie = (face_ids[:,1]>=0) & (abs(z[:,1]-z[:,0]) < DEPTH_TOLERANCE)
        mirrored = paired_faces(vertices,screen,triangles,face_ids,weights,tie)
        if np.any(tie & ~mirrored):
            raise ValueError("Unexpected different coplanar nearest surfaces")
        controls = {}
        for mode in ("light","dark","flat","nonmetal"):
            device = png_readback(logs.read("M03-1-"+mode+".png"))
            reference = np.frombuffer(apk.read(folder+mode+".rgba"),np.uint8).reshape(SIDE,SIDE,4)
            if not np.array_equal(device[:,:,3],reference[:,:,3]):
                raise ValueError("Source coverage changed under material control")
            diff = np.max(abs(device[:,:,:3].astype(np.int16) -
                              reference[:,:,:3].astype(np.int16)),axis=2)[ys,xs]
            controls[mode] = {
                "rgb_outlier_gt10": int((diff>10).sum()),
                "rgb_outlier_gt30": int((diff>30).sum()),
                "gt10_on_coplanar_opposite_face_pixels": int(((diff>10)&mirrored).sum()),
                "gt10_on_other_pixels": int(((diff>10)&~mirrored).sum()),
                "gt30_on_coplanar_opposite_face_pixels": int(((diff>30)&mirrored).sum()),
                "maximum_rgb_channel_error": int(diff.max())}
    return {
        "experiment":"GFX144","signed_original_apk_sha256":expected_sha,
        "owner_zip_sha256":sha256(log_path.read_bytes()).hexdigest(),
        "renderer":production["renderer"],"gles":production["gles"],
        "original_mesh_vertices":len(vertices),"source_submesh_triangles":len(triangles),
        "covered_pixels":len(xs),"source_nearest_depth_tie_pixels":int(tie.sum()),
        "exactly_coplanar_opposite_winding_normals_uv_pos_handedness_pixels":int(mirrored.sum()),
        "non_coplanar_covered_pixels":int((~tie).sum()),"controls":controls,
        "fixture_culling":"disabled in GFX124 and original Mesa reference",
        "original_Unity_shader_cull_property_resolved":False,
        "cause":"Original M03-1 has coincident opposite-normal faces at identical source depth; driver-dependent selection is strongly supported but requires Cull differential testing",
        "root_cause_certified_by_differential_cull_test":False,
        "original_raft_game_scene_parity":False,"phase_closed":False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apk",type=Path,required=True)
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--expected-apk-sha256",required=True)
    parser.add_argument("--safe",type=Path,required=True)
    args=parser.parse_args()
    report=inspect(args.apk,args.zip,args.expected_apk_sha256)
    args.safe.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
