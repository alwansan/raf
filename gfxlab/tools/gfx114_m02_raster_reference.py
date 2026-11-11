"""Stage indexed M02 raster test and compute an independent pixel-center reference."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
from gfxlab.tools.gfx110_original_animation_links import audit
from gfxlab.tools.gfx112_animated_payload import EXPECTED
from gfxlab.tools.original_model_probe import stage_originals

SIZE = 256
VERTICES = 1666


def original_indices(stage):
    indices = None

    def inspect(entry, graph, renderer, bones, animators):
        nonlocal indices
        if entry["id"] != "M02":
            return
        mesh = graph.types[entry["owner"]][entry["mesh_pid"]]
        handler = direct_mesh_handler(mesh)
        source = handler.src.m_SubMeshes
        if any(int(s.topology) != 0 or s.indexCount % 3 for s in source):
            raise ValueError("M02 submesh requires triangle lists")
        faces = handler.get_triangles()
        if len(faces) != len(source):
            raise ValueError("M02 submesh count mismatch")
        indices = [i + getattr(submesh, "baseVertex", 0)
                   for submesh, tris in zip(source, faces, strict=True)
                   for tri in tris for i in tri]
        if (not indices or len(indices) != sum(s.indexCount for s in source)
                or min(indices) < 0 or max(indices) >= VERTICES):
            raise ValueError("M02 index count or range mismatch")

    audit(stage, inspect)
    if indices is None:
        raise ValueError("M02 source not found")
    return np.asarray(indices, dtype="<u2")


def pose_positions(path):
    data = path.read_bytes()
    if struct.unpack_from("<4sII", data) != (b"G109", VERTICES, 8) or len(data) != 12+8*64+VERTICES*56:
        raise ValueError("Unexpected pose shape")
    positions = np.ndarray((VERTICES, 3), dtype="<f4", buffer=data,
                           offset=12+8*64+44, strides=(56, 4))
    if not np.isfinite(positions).all():
        raise ValueError("Pose contains nonfinite positions")
    return positions


def camera(poses):
    # One fixed oblique orthographic camera shared by all frames.
    # Center from the full sequence, with 10% margins.
    axes = np.array([[0.8, 0, -0.6], [0, 1, 0]], dtype=np.float64)
    xy = np.concatenate(poses) @ axes.T
    lo, hi = xy.min(axis=0), xy.max(axis=0)
    span = np.max(hi-lo)
    if span <= 0:
        raise ValueError("Zero screen-space bounds")
    scale = 1.6/span
    matrix = np.zeros((4, 4), dtype="<f4")
    matrix[:2, :3] = axes*scale
    matrix[:2, 3] = -(hi+lo)*0.5*scale
    matrix[3, 3] = 1
    return matrix


def edge(a, b, x, y):
    return (b[0]-a[0])*(y-a[1]) - (b[1]-a[1])*(x-a[0])


def mask(points, triangles, matrix):
    xy = ((points.astype(np.float64) @ matrix[:2, :3].T + matrix[:2, 3]) + 1)*SIZE/2
    result = np.zeros((SIZE, SIZE), dtype=np.uint8)
    for i, j, k in triangles.reshape(-1, 3):
        a, b, c = xy[[i,j,k]]
        area = edge(a,b,*c)
        if area == 0:
            continue
        if area < 0:
            b,c = c,b
        low = np.maximum(0, np.ceil(np.minimum(np.minimum(a,b),c)-0.5).astype(int))
        high = np.minimum(SIZE-1, np.floor(np.maximum(np.maximum(a,b),c)-0.5).astype(int))
        if np.any(low > high):
            continue
        x = np.arange(low[0], high[0]+1)[None,:]+0.5
        y = np.arange(low[1], high[1]+1)[:,None]+0.5
        inside = (edge(a,b,x,y)>=0) & (edge(b,c,x,y)>=0) & (edge(c,a,x,y)>=0)
        result[low[1]:high[1]+1, low[0]:high[0]+1] |= inside
    return result[::-1].copy()  # PNG/image origin at top left.


def main():
    p = argparse.ArgumentParser()
    for name in ("zip2","stage","assets","safe"):
        p.add_argument("--"+name,type=Path,required=True)
    a = p.parse_args()
    indices = original_indices(stage_originals(a.zip2,a.stage))
    poses = [pose_positions(a.assets / (key+".bin")) for key in EXPECTED]
    matrix = camera(poses)
    (a.assets/"raster114.bin").write_bytes(matrix.T.tobytes() + indices.tobytes())
    rows = {}
    for key, points in zip(EXPECTED,poses,strict=True):
        coverage = mask(points,indices,matrix)
        pixels = int(coverage.sum())
        if not 100 < pixels < SIZE*SIZE:
            raise ValueError("Invalid raster coverage")
        data = coverage.tobytes()
        (a.assets/(key+".mask")).write_bytes(data)
        rows[key] = {"covered_pixels":pixels,"sha256":hashlib.sha256(data).hexdigest()}
    unique = [len({rows[key]["sha256"] for key in EXPECTED[i:i+5]}) for i in (0,5,10)]
    if unique[0] != 1 or min(unique[1:]) < 2:
        raise ValueError("Raster test does not distinguish motion")
    a.safe.write_text(json.dumps({"experiment":"GFX114","size":SIZE,
        "triangles":int(len(indices)//3),"unique_masks_by_clip":unique,"poses":rows,
        "phase_closed":False},indent=2)+"\n")


if __name__=="__main__":
    main()
