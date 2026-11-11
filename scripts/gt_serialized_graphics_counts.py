#!/usr/bin/env python3
"""GT: aggregate every graphics object owned by the 82 SHA-pinned Unity files.

Source object identity is (serialized owner, original pathID, Unity type).
No dependency expansion, image bytes, object names, pathIDs or vertex data are
published. This is NOT proof of Unity export, Material GUIDs or Android render.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path

from scripts.gt_stage_serialized_owners import OWNERS, read_expected, InventoryError

GRAPHICS = frozenset((
    "Mesh", "Material", "Texture2D", "Cubemap", "Texture2DArray",
    "CubemapArray", "Texture3D", "RenderTexture", "Shader",
    "ComputeShader", "MeshFilter", "MeshRenderer", "SkinnedMeshRenderer",
    "ParticleSystemRenderer", "LineRenderer", "TrailRenderer",
    "SpriteRenderer", "Light", "ReflectionProbe", "Camera",
    "Terrain", "TerrainData", "ParticleSystem", "AnimationClip",
))
# Some Unity objects (e.g. Renderer refs) are scene-owned usage, not assets.

def verify(path: Path, size: int, digest: str) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise InventoryError("untrusted_staged_owner")
    h = hashlib.sha256()
    length = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
            length += len(chunk)
    if length != size or h.hexdigest() != digest:
        raise InventoryError("staged_owner_fingerprint_mismatch")


def inspect(root: Path, manifest: Path, selected=None, loader=None):
    if not root.is_dir() or root.is_symlink():
        raise InventoryError("invalid_staged_root")
    known = read_expected(manifest)
    names = sorted(OWNERS if selected is None else selected)
    if not names or len(names) != len(set(names)) or not set(names) <= set(OWNERS):
        raise InventoryError("invalid_owner_selection")
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    total = Counter()
    own = {}
    format_cs = Counter()
    mesh_submesh = Counter()
    errors = Counter()
    for name in names:
        kind, size, digest = known[name]
        path = root / name
        verify(path, size, digest)
        env = loader(path)
        sf = getattr(env, "file", None)
        if sf is None or not hasattr(sf, "objects"):
            raise InventoryError("missing_serialized_owner_object_table")
        objects = list(sf.objects.values())
        ids = [getattr(o, "path_id", None) for o in objects]
        if any(type(pid) is not int or pid <= 0 for pid in ids) or len(ids) != len(set(ids)):
            raise InventoryError("duplicate_or_invalid_source_object_identity")
        types = Counter(str(o.type.name) for o in objects)
        graphics = {k: types[k] for k in GRAPHICS if types[k]}
        total.update(graphics)
        total["all_owned_serialized_objects"] += len(objects)
        extra = Counter()
        for obj in objects:
            typ = str(obj.type.name)
            if typ not in ("Mesh", "Texture2D"):
                continue
            try:
                tree = obj.read_typetree(check_read=False)
                if not isinstance(tree, dict):
                    raise ValueError("invalid_typetree")
                if typ == "Mesh":
                    submesh = tree.get("m_SubMeshes")
                    if isinstance(submesh, list):
                        mesh_submesh[len(submesh)] += 1
                        extra["mesh_with_decoded_submesh_count"] += 1
                    else:
                        extra["mesh_submesh_schema_unavailable"] += 1
                elif typ == "Texture2D":
                    fmt, cs = tree.get("m_TextureFormat"), tree.get("m_ColorSpace")
                    if type(fmt) is int and type(cs) is int and cs in (0, 1):
                        format_cs[(fmt, cs)] += 1
                        extra["texture_format_color_decoded"] += 1
                    else:
                        extra["texture_format_color_unavailable"] += 1
            except Exception:
                extra["mesh_or_texture_typetree_decode_error"] += 1
        errors.update(extra)
        own[name] = {"sha256_verified": True, "bytes": size,
                     "total_owned_objects": len(objects),
                     "graphics_counts": dict(sorted(graphics.items())),
                     "header_decode_counts": dict(sorted(extra.items()))}
        del env, sf, objects
        gc.collect()
    return {
        "original_serialized_owners": len(names),
        "all_82_owners_authenticated": len(names) == len(OWNERS),
        "scope": "source-owned object metadata only, not streamed mesh/texture payload",
        "counts": dict(sorted(total.items())),
        "mesh_submesh_count_distribution": {str(k): v for k, v in sorted(mesh_submesh.items())},
        "texture_format_colorspace_pairs": [
            {"format": fmt, "color_space": cs, "count": n}
            for (fmt, cs), n in sorted(format_cs.items())
        ],
        "decode_counts": dict(sorted(errors.items())),
        "per_owner": own,
        "source_pixels_or_vertices_verified": False,
        "exported_unity_guid_links_verified": False,
        "android_render_verified": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.report.resolve().is_relative_to(args.source.resolve()):
        raise InventoryError("report_inside_original_source")
    result = inspect(args.source, args.manifest)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("GT_ALL_ORIGINAL_GRAPHICS_OBJECTS " + json.dumps({
        "source_owners": result["original_serialized_owners"],
        "all_82_sha256_verified": result["all_82_owners_authenticated"],
        "counts": result["counts"], "decode_counts": result["decode_counts"],
        "device_verified": False
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
