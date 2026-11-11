#!/usr/bin/env python3
"""GT: resolve original Renderer Material slots against 82 authenticated owners.

Object identity: (original serialized container, pathID, Unity type).
Usage identity: (Renderer owner, Renderer pathID, material-slot index).
Never publish game object names, pathIDs, original content or single-edge hashes.
Only aggregate counts and one commitment to the sorted full reference graph.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path, PurePosixPath

from scripts.gt_stage_serialized_owners import OWNERS, read_expected, InventoryError
from scripts.gt_serialized_graphics_counts import verify
from scripts.b03_original_renderer_materials import RENDERER_CLASSES

SCENES = frozenset(f"level{i}" for i in range(40))
MAX_SLOTS = 256
MAX_EXTERNAL_TABLE = 65535


def pointer(raw: object) -> tuple[int, int]:
    if (not isinstance(raw, dict) or set(raw) != {"m_FileID", "m_PathID"}):
        raise InventoryError("material_pointer_schema_invalid")
    fid, pid = raw["m_FileID"], raw["m_PathID"]
    if (type(fid) is not int or type(pid) is not int or fid < 0 or pid < 0 or
        fid > MAX_EXTERNAL_TABLE or (pid == 0 and fid != 0)):
        raise InventoryError("material_pointer_values_invalid")
    return fid, pid


def declared_external_owner(raw: object) -> str | None:
    """Return named owner only when well-formed; never infer by display name."""
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        return None
    name = PurePosixPath(raw.replace("\\", "/")).name
    return name if name in OWNERS else None


def audit(root: Path, manifest: Path, selected: list[str] | None = None,
          loader=None) -> dict:
    original = read_expected(manifest)
    owners = sorted(OWNERS if selected is None else selected)
    if not owners or len(owners) != len(set(owners)) or not set(owners) <= set(OWNERS):
        raise InventoryError("invalid_serialized_owner_selection")
    if not root.is_dir() or root.is_symlink():
        raise InventoryError("untrusted_staged_source")
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    object_types = {}
    external_tables = {}
    graph_edges = []
    renderer_objects = Counter()
    scene_renderers = Counter()
    counts = Counter()
    by_source = {}
    for name in owners:
        kind, size, sha = original[name]
        provider = root / name
        verify(provider, size, sha)
        env = loader(provider)
        sf = getattr(env, "file", None)
        if sf is None or not hasattr(sf, "objects") or not hasattr(sf, "externals"):
            raise InventoryError("invalid_original_owner_reader")
        external = [getattr(item, "path", None) for item in sf.externals]
        if len(external) > MAX_EXTERNAL_TABLE:
            raise InventoryError("external_table_overflow")
        external_tables[name] = external
        identities = {}
        source_counts = Counter()
        for obj in sf.objects.values():
            pid = getattr(obj, "path_id", None)
            if type(pid) is not int or pid <= 0 or pid in identities:
                raise InventoryError("duplicate_or_invalid_original_object_identity")
            typ = str(obj.type.name)
            identities[pid] = typ
            if typ not in RENDERER_CLASSES:
                continue
            source_counts["renderers"] += 1
            try:
                tree = obj.read_typetree(check_read=False)
            except Exception as error:
                raise InventoryError("original_renderer_material_array_undecodable") from error
            if not isinstance(tree, dict) or not isinstance(tree.get("m_Materials"), list):
                raise InventoryError("original_renderer_material_array_invalid")
            slots = tree["m_Materials"]
            if len(slots) > MAX_SLOTS:
                raise InventoryError("material_slot_limit_exceeded")
            source_counts["slots"] += len(slots)
            renderer_objects[typ] += 1
            if name in SCENES:
                scene_renderers[typ] += 1
            for i, entry in enumerate(slots):
                file_id, path_id = pointer(entry)
                graph_edges.append((name, pid, i, file_id, path_id))
                if name in SCENES:
                    counts["scene_material_slots"] += 1
                    if path_id == 0:
                        counts["scene_null_material_slots"] += 1
                    elif file_id:
                        counts["scene_external_material_slots"] += 1
        object_types[name] = identities
        by_source[name] = dict(sorted(source_counts.items()))
        del env, sf
        gc.collect()

    usages = Counter()
    used_materials = set()
    digest_lines = []
    for source_name, renderer_pid, slot, fid, pid in graph_edges:
        if pid == 0:
            usages["null_material_slot"] += 1
            digest_lines.append((source_name, str(renderer_pid), str(slot), "null", "0"))
            continue
        if fid == 0:
            target = source_name
            usages["local_material_slot"] += 1
        else:
            ext = external_tables[source_name]
            if fid > len(ext):
                raise InventoryError("original_material_external_index_out_of_bounds")
            target = declared_external_owner(ext[fid - 1])
            usages["external_material_slot"] += 1
        if target is None or target not in object_types:
            usages["unresolved_external_provider"] += 1
            digest_lines.append((source_name, str(renderer_pid), str(slot), "unresolved-provider", str(fid)))
            continue
        target_type = object_types[target].get(pid)
        if target_type == "Material":
            usages["material_identity_verified"] += 1
            used_materials.add((target, pid))
            digest_lines.append((source_name, str(renderer_pid), str(slot), target, str(pid)))
        elif target_type is None:
            usages["missing_material_target_object"] += 1
            digest_lines.append((source_name, str(renderer_pid), str(slot), "missing-target", target))
        else:
            usages["wrong_material_target_class"] += 1
            digest_lines.append((source_name, str(renderer_pid), str(slot), "wrong-class", target))
    counts.update(usages)
    counts["total_renderer_objects"] = sum(renderer_objects.values())
    counts["total_original_material_objects"] = sum(
        sum(kind == "Material" for kind in table.values()) for table in object_types.values())
    counts["distinct_referenced_material_objects"] = len(used_materials)
    counts["all_original_material_slots"] = len(graph_edges)
    counts["scene_renderer_objects"] = sum(scene_renderers.values())
    commitment = hashlib.sha256(
        "\n".join("\t".join(row) for row in sorted(digest_lines)).encode("utf-8")
    ).hexdigest()
    # Each bucket is mutually exclusive except "external/local" are source
    # partition classifications and "material_identity_verified" is resolved.
    if (counts["null_material_slot"] + counts["local_material_slot"] +
        counts["external_material_slot"] != len(graph_edges)):
        raise InventoryError("material_slot_partition_mismatch")
    return {
        "schema": "GT_ORIGINAL_RENDERER_MATERIAL_GRAPH_V1",
        "original_owners_authenticated": len(owners),
        "all_82_original_owners_authenticated": len(owners) == len(OWNERS),
        "source_only": True,
        "counts": dict(sorted(counts.items())),
        "renderer_classes": dict(sorted(renderer_objects.items())),
        "source_owner_slot_counts": by_source,
        "original_edge_graph_sha256": commitment,
        "all_original_material_targets_class_verified": (
            not any(counts[key] for key in ("unresolved_external_provider",
                  "missing_material_target_object", "wrong_material_target_class"))),
        "same_export_guid_lineage_verified": False,
        "unity_android_render_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.resolve().is_relative_to(args.source.resolve()):
        raise InventoryError("report_inside_original_stage_refused")
    result = audit(args.source, args.manifest)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {
        "source_owners": result["original_owners_authenticated"],
        "counts": result["counts"],
        "all_links_verified": result["all_original_material_targets_class_verified"],
        "android_render_verified": False,
    }
    print("GT_ORIGINAL_MATERIAL_LINK_GRAPH " + json.dumps(summary, sort_keys=True))
    if not result["all_original_material_targets_class_verified"]:
        raise SystemExit("Material target coverage incomplete; inspect original aggregate evidence")


if __name__ == "__main__":
    main()
