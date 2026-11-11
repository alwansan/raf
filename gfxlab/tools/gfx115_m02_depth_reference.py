"""Independent nearest-depth oracle for the M02 indexed GLES draw."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from gfxlab.tools.gfx112_animated_payload import EXPECTED
from gfxlab.tools.gfx114_m02_raster_reference import SIZE, camera, edge, pose_positions


def depth_camera(poses):
    matrix = camera(poses)
    axis = np.array([0.6, 0, 0.8], dtype=np.float64)
    depths = np.concatenate(poses) @ axis
    lo, hi = depths.min(), depths.max()
    if hi <= lo:
        raise ValueError("Zero depth range")
    scale = 1.6 / (hi - lo)
    matrix[2, :3] = axis * scale
    matrix[2, 3] = -(hi + lo) * 0.5 * scale
    return matrix


def depth_image(points, triangles, matrix):
    ndc = points.astype(np.float64) @ matrix[:3, :3].T + matrix[:3, 3]
    xy = (ndc[:, :2] + 1) * SIZE / 2
    z = (ndc[:, 2] + 1) / 2
    if not (np.all(z > 0) and np.all(z < 1)):
        raise ValueError("Geometry clipped by depth range")
    closest = np.full((SIZE, SIZE), np.inf)
    last = closest.copy()
    for face in triangles.reshape(-1, 3):
        a, b, c = xy[face]
        za, zb, zc = z[face]
        area = edge(a, b, *c)
        if area == 0:
            continue
        if area < 0:
            b, c = c, b
            zb, zc = zc, zb
            area = -area
        low = np.maximum(0, np.ceil(np.minimum(np.minimum(a, b), c)-0.5).astype(int))
        high = np.minimum(SIZE-1, np.floor(np.maximum(np.maximum(a, b), c)-0.5).astype(int))
        if np.any(low > high):
            continue
        x = np.arange(low[0], high[0]+1)[None, :] + 0.5
        y = np.arange(low[1], high[1]+1)[:, None] + 0.5
        wa, wb, wc = edge(b,c,x,y), edge(c,a,x,y), edge(a,b,x,y)
        inside = (wa >= 0) & (wb >= 0) & (wc >= 0)
        window = np.s_[low[1]:high[1]+1, low[0]:high[0]+1]
        depth = (wa*za + wb*zb + wc*zc)/area
        closest[window] = np.where(inside, np.minimum(closest[window], depth), closest[window])
        last[window] = np.where(inside, depth, last[window])
    covered = np.isfinite(closest)
    nearest = np.zeros((SIZE, SIZE), dtype="<u2")
    nearest[covered] = np.floor(closest[covered]*65534 + 0.5).astype(np.uint16) + 1
    final_fragment = np.floor(last[covered]*65534 + 0.5).astype(np.uint16) + 1
    hidden = np.count_nonzero(nearest[covered] != final_fragment)
    return nearest[::-1].copy(), int(hidden)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--safe", type=Path, required=True)
    args = parser.parse_args()
    geometry = args.assets / "raster114.bin"
    indices = geometry.read_bytes()[64:]
    triangles = np.frombuffer(indices, dtype="<u2")
    poses = [pose_positions(args.assets / (name + ".bin")) for name in EXPECTED]
    matrix = depth_camera(poses)
    (args.assets / "raster115.bin").write_bytes(matrix.T.tobytes() + indices)
    rows = {}
    for name, points in zip(EXPECTED, poses, strict=True):
        depths, hidden = depth_image(points, triangles, matrix)
        mask = (args.assets / (name + ".mask")).read_bytes()
        if (depths != 0).astype(np.uint8).tobytes() != mask or hidden == 0:
            raise ValueError("Depth oracle changed coverage or lacks occlusion")
        data = depths.tobytes()
        (args.assets / (name + ".depth")).write_bytes(data)
        rows[name] = {"covered_pixels":int(np.count_nonzero(depths)),
                      "last_fragment_control_differs_pixels":hidden,
                      "sha256":hashlib.sha256(data).hexdigest()}
    args.safe.write_text(json.dumps({"experiment":"GFX115","size":SIZE,"poses":rows,
                                     "phase_closed":False},indent=2)+"\n")


if __name__ == "__main__":
    main()
