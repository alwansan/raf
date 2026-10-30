#!/usr/bin/env python3
"""Read-only, bounded source geometry experiment after one verified LFS fetch.

No original vertices, indices, names or source bodies are printed or uploaded.
This checks original geometry, not AssetRipper output or Unity collider cooking.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def geometry_counts(vertices, triangles, expected_vertices):
    count = len(vertices)
    bad_vertices = sum(len(v) != 3 or not all(math.isfinite(x) for x in v) for v in vertices)
    bad_triangles = sum(len(t) != 3 or any(type(i) is not int or i < 0 or i >= count for i in t)
                        for t in triangles)
    return {"vertices": count, "nonfinite_or_invalid_vertices": bad_vertices,
            "triangles": len(triangles), "invalid_triangles": bad_triangles,
            "vertex_count_mismatch": count != expected_vertices,
            "valid": bool(count and triangles) and not (bad_vertices or bad_triangles)
                and count == expected_vertices}


def probe(root, ledger, stream):
    import UnityPy
    from UnityPy.helpers.MeshHelper import MeshHandler

    providers = [p for p in ledger["providers"] if p["stream"] == stream]
    if len(providers) != 1:
        raise ValueError("Expected exactly one prevalidated stream provider")
    provider = providers[0]
    path = root / stream
    if path.stat().st_size != provider["lfs_declared_bytes"]:
        raise ValueError("Stream byte count differs from original LFS pointer")
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != provider["lfs_sha256"]:
        raise ValueError("Stream SHA256 differs from original LFS pointer")
    selected = {(r["source"], r["original_path_id"]): r for r in provider["meshes"]}
    results, errors = [], Counter()
    seen = set()
    for header in sorted({key[0] for key in selected}):
        env = UnityPy.load(str(root / header))
        for obj in env.objects:
            key = (header, obj.path_id)
            if key not in selected:
                continue
            seen.add(key)
            try:
                mesh = obj.read()
                row = selected[key]
                data = mesh.m_StreamData
                if (data.path != stream or data.offset != row["stream_offset"] or
                        data.size != row["stream_size"]):
                    raise ValueError("Original range identity changed")
                handler = MeshHandler(mesh)
                handler.process()
                triangles = []
                for submesh, faces in zip(mesh.m_SubMeshes, handler.get_triangles()):
                    base = submesh.baseVertex or 0
                    triangles.extend(tuple(int(i) + base for i in face) for face in faces)
                expected = mesh.m_VertexData.m_VertexCount
                results.append(geometry_counts(handler.m_Vertices or [], triangles, expected))
            except Exception as exc:
                errors[type(exc).__name__] += 1
    report = {"stream": stream, "verified_lfs_bytes": path.stat().st_size,
              "requested_original_meshes": len(selected), "found_original_meshes": len(seen),
              "decoded_meshes": len(results), "valid_geometry_meshes": sum(r["valid"] for r in results),
              "nonfinite_or_invalid_vertices": sum(r["nonfinite_or_invalid_vertices"] for r in results),
              "invalid_triangles": sum(r["invalid_triangles"] for r in results),
              "vertex_count_mismatches": sum(r["vertex_count_mismatch"] for r in results),
              "decode_errors": dict(errors),
              "caveat": "Original source geometry only. No AssetRipper export, Unity cooking, scene or device verification."}
    print("RAFT_VERIFIED_SOURCE_GEOMETRY " + json.dumps(report, sort_keys=True))
    if not selected or len(results) != len(selected) or not all(r["valid"] for r in results):
        raise SystemExit("Source geometry validation incomplete or invalid; no recovery claimed")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--stream", choices=["sharedassets29.assets.resS", "sharedassets24.assets.resS"], required=True)
    args = parser.parse_args()
    probe(args.root, json.loads(args.ledger.read_text()), args.stream)
