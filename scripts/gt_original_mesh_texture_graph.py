#!/usr/bin/env python3
"""GT source-only Mesh and Material texture-reference audit across pinned ZIP2 owners.

Identity is (original serialized owner, original pathID, Unity object class).
Only aggregate counts and SHA256 commitment to the full original graph leave
the temporary CI workspace. No raw PPtrs, game payloads, or guessed GUIDs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import json
import math
from pathlib import Path

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError, read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_original_material_link_graph import (
    MAX_EXTERNAL_TABLE, SCENES, declared_external_owner, pointer,
)

MESH_USERS = frozenset(("MeshFilter", "SkinnedMeshRenderer"))
TEXTURE_TYPES = frozenset((
    "Texture2D", "Cubemap", "Texture2DArray", "CubemapArray",
    "Texture3D", "RenderTexture",
))
ENGINE_TRANSPORTS = frozenset((
    "Library/unity default resources", "Resources/unity_builtin_extra",
))
MAX_TEXTURE_SLOTS = 256


def texenvs(tree: object) -> list[tuple[str, tuple[int, int], bool]]:
    """Strict original texture binding parser. UV presence is counted, not leaked."""
    if not isinstance(tree, dict):
        raise InventoryError("material_tree_invalid")
    saved = tree.get("m_SavedProperties")
    entries = saved.get("m_TexEnvs") if isinstance(saved, dict) else None
    if not isinstance(entries, list) or len(entries) > MAX_TEXTURE_SLOTS:
        raise InventoryError("material_texenv_array_invalid")
    found = set()
    result = []
    for item in entries:
        if isinstance(item, (tuple, list)) and len(item) == 2:
            name, values = item
        elif isinstance(item, dict) and set(item) == {"m_First", "m_Second"}:
            name, values = item["m_First"], item["m_Second"]
        else:
            raise InventoryError("material_texenv_entry_invalid")
        if (not isinstance(name, str) or not name or name in found
                or not isinstance(values, dict) or "m_Texture" not in values):
            raise InventoryError("duplicate_or_malformed_texenv_property")
        found.add(name)
        pptr = pointer(values["m_Texture"])
        uv_keys = {"m_Scale", "m_Offset"} & set(values)
        if uv_keys not in (set(), {"m_Scale", "m_Offset"}):
            raise InventoryError("partial_source_uv_transform")
        for key in uv_keys:
            pair = values[key]
            if not isinstance(pair, dict) or set(pair) != {"x", "y"}:
                raise InventoryError("invalid_source_uv_transform")
            if any(type(pair[c]) not in (int, float) or
                   not math.isfinite(pair[c]) for c in ("x", "y")):
                raise InventoryError("nonfinite_source_uv_transform")
        result.append((name, pptr, len(uv_keys) == 2))
    return result


def resolve(owner: str, fid: int, external_tables: dict[str, list[str | None]]) -> tuple[str, str | None]:
    if fid == 0:
        return "local", owner
    table = external_tables[owner]
    if fid > len(table):
        raise InventoryError("dependency_external_index_out_of_bounds")
    path = table[fid - 1]
    named = declared_external_owner(path)
    if named:
        return "external", named
    if isinstance(path, str) and path.replace("\\", "/") in ENGINE_TRANSPORTS:
        return "engine", None
    return "unresolved", None


def audit(root: Path, manifest: Path, selected: list[str] | None = None, loader=None) -> dict:
    expected = read_expected(manifest)
    names = sorted(OWNERS if selected is None else selected)
    if not names or len(names) != len(set(names)) or not set(names) <= set(OWNERS):
        raise InventoryError("invalid_selected_source_owners")
    if not root.is_dir() or root.is_symlink():
        raise InventoryError("invalid_authenticated_original_stage")
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))

    type_table: dict[str, dict[int, str]] = {}
    externals: dict[str, list[str | None]] = {}
    edges = []
    counts = Counter()
    per_owner = {}

    for name in names:
        _, size, digest = expected[name]
        source = root / name
        verify(source, size, digest)
        env = loader(source)
        sf = getattr(env, "file", None)
        if sf is None or not hasattr(sf, "objects") or not hasattr(sf, "externals"):
            raise InventoryError("original_owner_reader_invalid")
        paths = [getattr(ext, "path", None) for ext in sf.externals]
        if len(paths) > MAX_EXTERNAL_TABLE:
            raise InventoryError("external_table_too_large")
        externals[name] = paths
        identities = {}
        by_owner = Counter()
        for obj in sf.objects.values():
            pid = getattr(obj, "path_id", None)
            if type(pid) is not int or pid <= 0 or pid in identities:
                raise InventoryError("duplicate_or_invalid_object_pathid")
            typ = str(obj.type.name)
            identities[pid] = typ
            if typ not in MESH_USERS and typ != "Material":
                continue
            try:
                tree = obj.read_typetree(check_read=False)
            except Exception as exc:
                raise InventoryError("original_dependency_typetree_undecodable") from exc
            if typ in MESH_USERS:
                if not isinstance(tree, dict) or "m_Mesh" not in tree:
                    raise InventoryError("original_component_mesh_pointer_missing")
                fid, path_id = pointer(tree["m_Mesh"])
                counts[typ + "_objects"] += 1
                counts["mesh_component_slots"] += 1
                by_owner["mesh_component_slots"] += 1
                if name in SCENES:
                    counts["scene_mesh_component_slots"] += 1
                edges.append(("mesh", name, pid, "m_Mesh", fid, path_id))
            else:
                counts["material_objects"] += 1
                by_owner["materials"] += 1
                for prop, (fid, path_id), has_uv in texenvs(tree):
                    counts["texture_property_slots"] += 1
                    by_owner["texture_property_slots"] += 1
                    counts["source_texture_uv_transforms_present"] += int(has_uv)
                    edges.append(("texture", name, pid, prop, fid, path_id))
        type_table[name] = identities
        per_owner[name] = dict(sorted(by_owner.items()))
        del env, sf
        gc.collect()

    digest_rows = []
    used_mesh = set()
    used_texture = set()
    texture_types = Counter()
    for mode, owner, source_pid, prop, fid, pid in edges:
        if pid == 0:
            counts[mode + "_null"] += 1
            digest_rows.append((mode, owner, str(source_pid), prop, "null", "0"))
            continue
        counts[mode + "_bound"] += 1
        kind, target = resolve(owner, fid, externals)
        counts[mode + "_" + kind + "_references"] += 1
        if target is None or target not in type_table:
            counts[mode + "_" + ("engine" if kind == "engine" else "unresolved_provider")] += 1
            digest_rows.append((mode, owner, str(source_pid), prop, kind, str(fid)))
            continue
        typ = type_table[target].get(pid)
        accepted = typ == "Mesh" if mode == "mesh" else typ in TEXTURE_TYPES
        if accepted:
            counts[mode + "_target_class_verified"] += 1
            if mode == "mesh":
                used_mesh.add((target, pid))
            else:
                used_texture.add((target, pid))
                texture_types[typ] += 1
            digest_rows.append((mode, owner, str(source_pid), prop, target, str(pid)))
        elif typ is None:
            counts[mode + "_target_missing"] += 1
            digest_rows.append((mode, owner, str(source_pid), prop, "missing", target))
        else:
            counts[mode + "_target_wrong_class"] += 1
            digest_rows.append((mode, owner, str(source_pid), prop, "wrong-class", target))

    counts["distinct_referenced_meshes"] = len(used_mesh)
    counts["distinct_referenced_textures"] = len(used_texture)
    if (counts["mesh_null"] + counts["mesh_bound"] != counts["mesh_component_slots"] or
        counts["texture_null"] + counts["texture_bound"] != counts["texture_property_slots"]):
        raise InventoryError("dependency_slot_partition_mismatch")
    for mode in ("mesh", "texture"):
        if (sum(counts[mode + "_" + k + "_references"] for k in
                ("local", "external", "engine", "unresolved")) != counts[mode + "_bound"]):
            raise InventoryError("dependency_transport_partition_mismatch")
    commitment = hashlib.sha256(
        "\n".join("\t".join(r) for r in sorted(digest_rows)).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "GT_ORIGINAL_MESH_TEXTURE_REFERENCE_GRAPH_V1",
        "source_only": True,
        "original_owners_sha256_verified": len(names),
        "all_82_owners_sha256_verified": len(names) == len(OWNERS),
        "counts": dict(sorted(counts.items())),
        "texture_target_class_usage": dict(sorted(texture_types.items())),
        "per_owner_source_counts": per_owner,
        "original_graph_sha256": commitment,
        "all_source_mesh_targets_verified": not any(counts["mesh_" + k] for k in
            ("engine", "unresolved_provider", "target_missing", "target_wrong_class")),
        "all_source_texture_targets_verified": not any(counts["texture_" + k] for k in
            ("engine", "unresolved_provider", "target_missing", "target_wrong_class")),
        "original_stream_pixels_vertices_verified": False,
        "exported_project_same_instance_guid_verified": False,
        "android_gpu_render_verified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.resolve().is_relative_to(args.source.resolve()):
        raise InventoryError("report_inside_source_stage")
    result = audit(args.source, args.manifest)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("GT_ORIGINAL_MESH_TEXTURE_GRAPH " + json.dumps({
        "owners": result["original_owners_sha256_verified"],
        "counts": result["counts"],
        "all_mesh_verified": result["all_source_mesh_targets_verified"],
        "all_texture_verified": result["all_source_texture_targets_verified"],
        "android_verified": False,
    }, sort_keys=True))
    # This audit classifies legitimate engine/unmapped transports. It fails
    # only on broken in-scope class identities, not on *reported* unknowns.
    for mode in ("mesh", "texture"):
        if any(result["counts"].get(mode + "_" + k) for k in
               ("target_missing", "target_wrong_class")):
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
