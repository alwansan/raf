#!/usr/bin/env python3
"""GT: source-authenticated Unity scene graphics inventory (no export or game build).

Reads the 40 original level headers at the pinned ZIP2 source. Counts only
objects owned by each serialized scene (never dependency-expanded objects).
Missing sharedassets/resources/stream payloads remain explicitly unverified.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gc
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

from scripts.b03_original_renderer_materials import (
    MANIFEST_COLUMNS, RENDERER_CLASSES, analyze_scene,
    manifest_provider_basename_counts,
)

SOURCE_COMMIT = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
SCENES = tuple(f"level{i}" for i in range(40))
PART = re.compile(r"part-(\d{5})\Z")
KINDS = frozenset(("Mesh", "Material", "Texture2D", "Cubemap",
                   "Texture2DArray", "CubemapArray", "Shader",
                   "ComputeShader", "MeshFilter", "MeshRenderer",
                   "SkinnedMeshRenderer", "ParticleSystemRenderer",
                   "TrailRenderer", "LineRenderer", "SpriteRenderer",
                   "Light", "ReflectionProbe", "Camera"))


class InventoryError(ValueError):
    pass


def manifest_scenes(manifest: Path) -> dict:
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 1024 * 1024:
        raise InventoryError("unsafe_manifest")
    result = {}
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != MANIFEST_COLUMNS:
            raise InventoryError("manifest_schema_changed")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise InventoryError("malformed_manifest_row")
            name = row["relative_path_under_Raft"]
            parts = PurePosixPath(name).parts
            if (name.startswith("/") or "\\" in name or
                    any(p in ("", ".", "..") for p in name.split("/"))):
                raise InventoryError("unsafe_manifest_path")
            if len(parts) != 2 or parts[0] != "Raft_Data" or parts[1] not in SCENES:
                continue
            if parts[1] in result:
                raise InventoryError("duplicate_scene_manifest_entry")
            size = int(row["bytes"])
            digest = row["sha256"]
            kind = row["kind"]
            if size <= 0 or not re.fullmatch(r"[0-9a-f]{64}", digest) or kind not in ("plain", "split"):
                raise InventoryError("invalid_scene_manifest_record")
            result[parts[1]] = (kind, size, digest)
    if set(result) != set(SCENES):
        raise InventoryError("manifest_missing_scene_records")
    return result


def checked_stage(source_root: Path, name: str, expected: tuple, staging: Path) -> Path:
    """Use original plain bytes or reassemble split parts; always authenticate SHA256."""
    if name not in SCENES or any(p.is_symlink() for p in (source_root, *source_root.parents)):
        raise InventoryError("unsafe_scene_source_root")
    kind, size, sha = expected
    original = source_root / name
    if original.is_symlink():
        raise InventoryError("symlink_scene_rejected")
    if kind == "plain":
        if not original.is_file():
            raise InventoryError("missing_original_scene")
        path = original
    else:
        if not original.is_dir():
            raise InventoryError("missing_original_split_directory")
        entries = list(original.iterdir())
        parts = sorted((p for p in entries if PART.fullmatch(p.name)),
                       key=lambda p: p.name)
        if (not parts or len(entries) != len(parts) + 1 and len(entries) != len(parts)
                or any(p.is_symlink() or not p.is_file() for p in parts)
                or [p.name for p in parts] != [f"part-{i:05d}" for i in range(len(parts))]
                or any(p.name != "README.txt" for p in entries if p not in parts)):
            raise InventoryError("unsafe_or_incomplete_split_parts")
        staging.mkdir(parents=True, exist_ok=True)
        path = staging / name
        with path.open("xb") as dest:
            for part in parts:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, dest, length=1024 * 1024)
    digest = hashlib.sha256()
    length = 0
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
            length += len(chunk)
    if length != size or digest.hexdigest() != sha:
        raise InventoryError("original_scene_size_or_sha256_mismatch")
    return path


def scan(source_root: Path, manifest: Path, levels: tuple[int, ...], loader=None) -> dict:
    expected = manifest_scenes(manifest)
    names = manifest_provider_basename_counts(manifest)
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    totals, each = Counter(), {}
    with tempfile.TemporaryDirectory(prefix="gt-scene-") as tmp:
        for index in levels:
            if type(index) is not int or not 0 <= index < 40:
                raise InventoryError("level_index_out_of_bounds")
            name = SCENES[index]
            with tempfile.TemporaryDirectory(prefix="owner-", dir=tmp) as temp:
                path = checked_stage(source_root, name, expected[name], Path(temp))
                env = loader(path)
                owner = getattr(env, "file", None)
                if owner is None or not hasattr(owner, "objects") or not hasattr(owner, "externals"):
                    raise InventoryError("incomplete_unity_owner_reader")
                objects = list(owner.objects.values())
                ids = [obj.path_id for obj in objects]
                if any(type(x) is not int or x <= 0 for x in ids) or len(ids) != len(set(ids)):
                    raise InventoryError("invalid_original_object_identity")
                types = Counter(str(obj.type.name) for obj in objects)
                renderers = sum(types[k] for k in RENDERER_CLASSES)
                material_graph = None
                if renderers:
                    external_paths = [getattr(x, "path", None) for x in owner.externals]
                    # B03 bounds renderer/material graphs to 100k nodes. Large
                    # Unity scene owners may contain >100k unrelated MonoBehaviour
                    # and GameObject nodes; they are not material graph vertices.
                    # Keep all original renderer and local Material objects for
                    # the PPtr identity validation, never dependency-expanded ones.
                    graph_objects = [obj for obj in objects
                                     if str(obj.type.name) in RENDERER_CLASSES
                                     or str(obj.type.name) == "Material"]
                    material_graph = analyze_scene(graph_objects, len(external_paths),
                                                   external_paths, names)
                    totals.update(material_graph["counts"])
                counts = {k: types[k] for k in KINDS if types[k]}
                totals.update({"original_owned_" + k: v for k, v in counts.items()})
                totals["original_scene_objects"] += len(objects)
                each[name] = {
                    "source_bytes": expected[name][1], "source_sha256": expected[name][2],
                    "sha256_verified": True, "owned_object_count": len(objects),
                    "graphics_class_counts": dict(sorted(counts.items())),
                    "renderer_material": material_graph,
                }
                del env, owner, objects
                gc.collect()
    return {
        "agent": "GT", "source_commit": SOURCE_COMMIT, "scenes_examined": len(each),
        "all_40_scene_headers_authenticated": set(each) == set(SCENES),
        "source_sha256_verified_for_every_examined_scene": True,
        "source_scope": "scene-owned serialized headers only, not sharedassets/resources or exported Unity",
        "counts": dict(sorted(totals.items())), "scenes": each,
        "external_material_targets_verified": False,
        "textures_pixels_verified": False, "shader_passes_variants_verified": False,
        "rendered_in_android_game_verified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--levels", type=int, nargs="*", default=list(range(40)))
    args = parser.parse_args()
    if not args.levels or len(args.levels) != len(set(args.levels)):
        raise InventoryError("invalid_scene_subset")
    if args.report.resolve().is_relative_to(args.source.resolve()):
        raise InventoryError("report_must_be_outside_original_source")
    result = scan(args.source, args.manifest, tuple(args.levels))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    safe = {"scenes_examined": result["scenes_examined"],
            "all_40_scene_headers_authenticated": result["all_40_scene_headers_authenticated"],
            "counts": result["counts"], "device_verified": False}
    print("GT_ORIGINAL_SCENE_GRAPHICS_INVENTORY " + json.dumps(safe, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
