"""Make private M02 mesh frames from authenticated clip samples and source vertex streams."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from gfxlab.tools.gfx111_m02_clip_pose import run


def normalized(vectors):
    length = np.linalg.norm(vectors, axis=1)
    if (length < 1e-8).any() or not np.isfinite(length).all():
        raise ValueError("Degenerate skinned direction")
    return vectors / length[:, None]


def prepare(stage, mesh_file, out):
    source = np.frombuffer(mesh_file.read_bytes(), dtype="<f4").reshape(-1, 12)
    out.mkdir(parents=True, exist_ok=False)
    samples = []

    def consume(clip, sample, time, positions, weights, world, bindposes, reference):
        if not np.array_equal(np.asarray(positions, dtype=np.float32), source[:, :3]):
            raise ValueError("Animated source vertex order differs from Forward")
        pose = source.copy()
        pose[:, :3] = reference
        affine = np.asarray(world).reshape(-1, 4, 4) @ np.asarray(bindposes).reshape(-1, 4, 4)
        # Linear blend of source direction vectors for this controlled render.
        linear = np.stack([sum(weight * affine[bone, :3, :3] for weight, bone in influences)
                           for influences in weights])
        normals = normalized(np.einsum("nij,nj->ni", linear, source[:, 3:6]))
        tangents = np.einsum("nij,nj->ni", linear, source[:, 6:9])
        tangents = normalized(tangents - (tangents * normals).sum(axis=1)[:, None] * normals)
        pose[:, 3:6] = normals
        pose[:, 6:9] = tangents
        if not np.isfinite(pose).all() or not np.array_equal(pose[:, 9:], source[:, 9:]):
            raise ValueError("Nonfinite skin or altered UV/handedness")
        name = f"C{clip}P{sample}"
        raw = pose.tobytes()
        (out / (name + ".bin")).write_bytes(raw)
        samples.append({"sample": name, "clip_index": clip, "pose_index": sample,
                        "time_s": time, "vertex_sha256": hashlib.sha256(raw).hexdigest()})

    result = run(stage, consume)
    if len(samples) != 15:
        raise ValueError("Unexpected pose count")
    return {"experiment": "GFX129", "source_sha": result["source_sha"], "samples": samples,
            "original_unity_animation_player_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "mesh", "private", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.stage, args.mesh, args.private)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
