"""Compare audited same-mode Cull results and classify residual pixels by geometry."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from gfxlab.tools.gfx144_coplanar_face_audit import closest_pairs, png_readback, project
from gfxlab.tools.gfx148_cull_batch import HASHES, SLOT, audit


def inspect(apk_path, logs):
    first, second = logs
    result = audit(first, apk_path)
    if result != audit(second, apk_path):
        raise ValueError("Device export metrics disagree")
    with ZipFile(first) as a, ZipFile(second) as b, ZipFile(apk_path) as apk:
        identical = a.namelist() == b.namelist() and all(a.read(n) == b.read(n) for n in a.namelist())
        if not identical:
            raise ValueError("Device export bytes disagree")
        _, screen, depths = project(apk.read(SLOT+"mesh.bin"), apk.read(SLOT+"light-2.bin"),
                                    apk.read(SLOT+"light-3.bin"))
        indices = np.frombuffer(apk.read(SLOT+"indices.bin"), dtype="<u2").reshape(-1, 3)
        x, y = screen[indices[:, 1]] - screen[indices[:, 0]], screen[indices[:, 2]] - screen[indices[:, 0]]
        winding = x[:, 0]*y[:, 1] - x[:, 1]*y[:, 0]
        mode_triangles = {"off": indices, "back": indices[winding > 0], "front": indices[winding < 0]}
        outliers = {}
        for mode in HASHES:
            raw = png_readback(a.read(f"M03-1-{mode}.png"))
            ref = np.frombuffer(apk.read(SLOT+f"cull-{mode}.rgba"), dtype=np.uint8).reshape(256, 256, 4)
            error = np.abs(raw[:, :, :3].astype(np.int16) - ref[:, :, :3]).max(axis=2)
            ys, xs = np.where((raw[:, :, 3] == 255) & (ref[:, :, 3] == 255) & (error > 10))
            points = np.column_stack((xs+0.5, ys+0.5))
            depth, faces, weights, hits = closest_pairs(screen, depths, mode_triangles[mode], points)
            both = faces[:, 1] >= 0
            ties = np.zeros(len(points), dtype=bool)
            ties[both] = np.abs(depth[both, 0] - depth[both, 1]) < 1e-7
            outliers[mode] = {"pixels": len(points), "cpu_nearest_depth_ties": int(ties.sum()),
                              "cpu_single_hit": int((hits == 1).sum()),
                              "cpu_no_hit": int((hits == 0).sum()),
                              "cpu_nearest_edge_weight_below_0_001": int(
                                  ((faces[:, 0] >= 0) & (weights[:, 0].min(axis=1) < 0.001)).sum())}
    result.update(experiment="GFX149", exports_byte_identical=True, cpu_outlier_classification=outliers,
                  apk_sha256=hashlib.sha256(apk_path.read_bytes()).hexdigest(),
                  owner_zip_sha256=[hashlib.sha256(p.read_bytes()).hexdigest() for p in logs])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("apk", type=Path)
    parser.add_argument("logs", nargs=2, type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.apk, args.logs), indent=2))
