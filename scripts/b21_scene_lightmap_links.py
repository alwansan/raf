#!/usr/bin/env python3
"""B21: bounded, read-only original Unity scene lightmap relationship probe.

This does not repair lightmap data, equate source to AssetRipper export, or infer
white-material causes from synthetic/partial scenes. Only aggregate counts leave
the private analysis context. Source blobs are authenticated against ZIP2 SHA256.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

# Immutable source: raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385,
# RAFT_FILE_MANIFEST.tsv, original Raft_Data/level0..level5 (all plain blobs).
PIN = {
    "level0": (3927436, "33e7855a700ae0d90d04f50d8ea75ab6f14e9d5aa0314a32e91b96fb1f6a3a62"),
    "level1": (2001504, "9ca3a83f4d8841d4052a4899d0855a2bb0fcc87d5378b8d7004bcd7bff33963"),
    "level2": (22204, "3ed1e89bbdb4509af723fd6e7b37c4ffa0e92a8de548940e1fd7db6e90bf7c8b"),
    "level3": (20388, "0bbeece712333cc3119995a7db34abe79a2c1a371825f559dc486b944a5031a4"),
    "level4": (30668, "a62b5ac7b80f8a906c9744ec457be8816663da4a2e8bb2a38924122448522511"),
    "level5": (19496, "28875e384d1c470e9215f89de0ef1bd8f1ef155a78dcfaea47dcd3ca70dbadf1"),
}
RENDERERS = frozenset(("MeshRenderer", "SkinnedMeshRenderer", "Terrain",
                       "TrailRenderer", "LineRenderer", "ParticleSystemRenderer"))
LIGHTMAP_PROPS = ("m_LightmapColor", "m_LightmapDir", "m_ShadowMask")
MAX_OBJECTS = 100000
MAX_LIGHTMAPS = 65535
MAX_BYTES = 12_000_000


class SourceError(ValueError):
    """Untrusted original serialization or source fingerprint."""


def verify_source(path: Path, expected: tuple[int, str]) -> None:
    if path.is_symlink() or not path.is_file():
        raise SourceError("missing_or_linked_original_scene")
    size, digest = expected
    if size < 100 or size > MAX_BYTES or path.stat().st_size != size:
        raise SourceError("original_size_mismatch")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    if h.hexdigest() != digest:
        raise SourceError("original_sha256_mismatch")


def pointer_state(value: object, local_ids: set[int]) -> str:
    if not isinstance(value, dict):
        return "unknown_pointer_schema"
    file_id = value.get("m_FileID")
    path_id = value.get("m_PathID")
    if type(file_id) is not int or type(path_id) is not int:
        return "unknown_pointer_schema"
    if path_id == 0:
        return "null_pointer" if file_id == 0 else "unknown_pointer_schema"
    if path_id < 0 or file_id < 0:
        return "unknown_pointer_schema"
    if file_id:
        return "external_target_unverified"
    return "local_target_present" if path_id in local_ids else "local_target_missing"


def analyze_scene(objects: list) -> dict:
    if len(objects) > MAX_OBJECTS:
        raise SourceError("scene_objects_over_budget")
    counts = Counter()
    ids = []
    for obj in objects:
        pid = getattr(obj, "path_id", None)
        if type(pid) is not int or pid <= 0:
            raise SourceError("invalid_object_path_id")
        ids.append(pid)
    if len(ids) != len(set(ids)):
        raise SourceError("duplicate_object_path_id")
    local_ids = set(ids)
    owners = []
    render_indices = []
    for obj in objects:
        kind = str(obj.type.name)
        if kind not in RENDERERS and kind != "LightmapSettings":
            continue
        counts[kind + "_objects"] += 1
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            counts[kind + "_typetree_unknown"] += 1
            continue
        if not isinstance(tree, dict):
            counts[kind + "_typetree_unknown"] += 1
            continue
        if kind == "LightmapSettings":
            maps = tree.get("m_Lightmaps")
            if not isinstance(maps, list):
                counts["lightmaps_schema_unknown"] += 1
                continue
            if len(maps) > MAX_LIGHTMAPS:
                raise SourceError("lightmap_array_over_budget")
            owners.append(maps)
        else:
            index = tree.get("m_LightmapIndex")
            if type(index) is not int:
                counts["renderer_lightmap_index_schema_unknown"] += 1
            elif index in (-1, 65535):
                counts["renderer_lightmap_unassigned"] += 1
            elif 0 <= index < 65535:
                counts["renderer_lightmap_indices_declared"] += 1
                render_indices.append(index)
            else:
                counts["renderer_lightmap_index_nonstandard_unverified"] += 1
    if len(owners) > 1:
        raise SourceError("multiple_lightmap_settings_in_one_scene")
    if not owners:
        counts["lightmap_settings_absent_or_undecodable"] += 1
        counts["renderer_indices_without_decodable_settings"] = len(render_indices)
    else:
        maps = owners[0]
        counts["serialized_lightmap_entries"] = len(maps)
        for entry in maps:
            if not isinstance(entry, dict):
                counts["lightmap_entry_schema_unknown"] += 1
                continue
            for field in LIGHTMAP_PROPS:
                counts[field + "_" + pointer_state(entry.get(field), local_ids)] += 1
        counts["renderer_indices_in_range"] = sum(i < len(maps) for i in render_indices)
        counts["renderer_indices_out_of_range"] = sum(i >= len(maps) for i in render_indices)
    return {
        "counts": dict(sorted(counts.items())),
        "source_typetree_only": True,
        "source_export_pptr_mapping_proven": False,
        "pixel_shading_or_missing_lightmap_cause_proven": False,
        "original_assets_modified": False,
        "unity_or_device_executed": False,
    }


def probe(root: Path, loader=None) -> dict:
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise SourceError("unsafe_scene_root")
    for name, expected in PIN.items():
        verify_source(root / name, expected)
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    scenes = {}
    for name in PIN:
        env = loader(root / name)
        # UnityPy exposes serialized object headers even if typetree decode fails.
        objects = list(env.file.objects.values())
        scenes[name] = analyze_scene(objects)
        scenes[name]["original_sha256"] = PIN[name][1]
        scenes[name]["source_bytes"] = PIN[name][0]
        del objects, env
    return {
        "source_commit": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        "selected_original_scene_count": len(scenes),
        "scenes": scenes,
        "source_fingerprints_verified": True,
        "full_40_scenes_checked": False,
        "same_export_or_device_lightmaps_verified": False,
        "source_or_export_mutated": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    result = probe(args.source)
    rendered = json.dumps(result, sort_keys=True)
    print("RAFT_B21_ORIGINAL_LIGHTMAPS " + rendered)
    if args.report:
        target = args.report.absolute()
        if target.is_relative_to(args.source.absolute()):
            raise SourceError("report_inside_source_refused")
        target.write_text(rendered + "\n", encoding="utf8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
