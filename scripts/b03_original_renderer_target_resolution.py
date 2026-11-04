#!/usr/bin/env python3
"""B03: resolve original Renderer Material targets against SHA-pinned ZIP2 owners.

Complements six-scene source reference shape audit. Only two selected original
serialized owner files are staged; unresolved other owners stay unverified.
No object paths, material names, IDs, source bytes or per-edge hashes are emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath

from scripts.b03_original_renderer_materials import (
    ORIGINAL_PIN, RENDERER_CLASSES, SourceError, analyze_scene,
    declared_provider_kind, manifest_provider_basename_counts, pointer_shape,
)
from scripts.b21_scene_lightmap_links import PIN, verify_source

OWNER_PINS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}
MAX_MATERIAL_IDS = 200_000


def verify_owner(path: Path, pin: tuple[int, str]) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size != pin[0]:
        raise SourceError("original_selected_owner_size_or_type_mismatch")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    if h.hexdigest() != pin[1]:
        raise SourceError("original_selected_owner_sha256_mismatch")


def select_original_objects(objects: list) -> dict[int, str]:
    if len(objects) > MAX_MATERIAL_IDS:
        raise SourceError("selected_original_owner_object_budget_exceeded")
    result = {}
    for obj in objects:
        pid = getattr(obj, "path_id", None)
        if type(pid) is not int or pid <= 0 or pid in result:
            raise SourceError("bad_original_selected_owner_object_identity")
        result[pid] = str(obj.type.name)
    return result


def resolve_scene_targets(objects: list, external_paths: list[str],
                          owner_types: dict[str, dict[int, str]], manifest_names: Counter) -> dict:
    """Verify staged owner object class, retain other external owners as unknown."""
    if not isinstance(external_paths, list):
        raise SourceError("bad_scene_external_owner_table")
    ext_count = len(external_paths)
    source_counts = analyze_scene(objects, ext_count, external_paths, manifest_names)["counts"]
    local = select_original_objects(objects)
    counts = Counter()
    for obj in objects:
        if str(obj.type.name) not in RENDERER_CLASSES:
            continue
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            continue
        if not isinstance(tree, dict) or not isinstance(tree.get("m_Materials"), list):
            continue
        for item in tree["m_Materials"]:
            state, fid, pid = pointer_shape(item, local, ext_count)
            if state == "null_material_slot":
                counts["original_null_slots"] += 1
            elif state == "local_material_target_verified":
                counts["local_material_object_class_verified"] += 1
            else:
                path = external_paths[fid - 1]
                if declared_provider_kind(path, manifest_names) != "provider_name_declared_in_zip2_manifest":
                    counts["external_owner_name_not_uniquely_verified"] += 1
                    continue
                name = PurePosixPath(path.replace("\\", "/")).name
                selected = owner_types.get(name)
                if selected is None:
                    counts["external_other_zip2_provider_unverified"] += 1
                elif pid not in selected:
                    counts["external_staged_provider_missing_object"] += 1
                elif selected[pid] != "Material":
                    counts["external_staged_provider_wrong_object_type"] += 1
                else:
                    counts["external_staged_material_target_verified"] += 1
    if sum(counts.values()) != source_counts.get("original_material_slots", 0):
        raise SourceError("source_and_target_slot_accounting_mismatch")
    errors = {
        key: counts[key] for key in (
            "external_staged_provider_missing_object",
            "external_staged_provider_wrong_object_type",
            "external_owner_name_not_uniquely_verified",
        ) if counts[key]
    }
    return {
        "counts": dict(sorted(counts.items())),
        "errors": errors,
        "staged_material_object_links_valid": not bool(errors),
        "original_external_other_owners_verified": False,
        "same_instance_export_renderer_identity_verified": False,
        "android_rendering_proven": False,
    }


def probe(source: Path, owners: Path, manifest: Path, loader=None) -> dict:
    for root in (source, owners):
        if not root.is_dir() or any(p.is_symlink() for p in (root, *root.parents)):
            raise SourceError("untrusted_original_source_or_staging_root")
    for name, pin in PIN.items():
        verify_source(source / name, pin)
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))
    basename_counts = manifest_provider_basename_counts(manifest)
    for name in OWNER_PINS:
        if basename_counts.get(name) != 1:
            raise SourceError("ambiguous_or_missing_expected_owner_name")
    owners_by_name = {}
    for name, pin in OWNER_PINS.items():
        path = owners / name
        verify_owner(path, pin)
        original = loader(path)
        owners_by_name[name] = select_original_objects(list(original.file.objects.values()))
        del original
    scenes = {}
    for name in PIN:
        env = loader(source / name)
        source_file = env.file
        external_paths = [getattr(x, "path", None) for x in source_file.externals]
        summary = resolve_scene_targets(list(source_file.objects.values()),
                                        external_paths, owners_by_name, basename_counts)
        summary["scene_sha256"] = PIN[name][1]
        scenes[name] = summary
        del env, source_file
    return {
        "schema_version": 1,
        "source_commit": ORIGINAL_PIN,
        "six_original_scene_sha256_verified": True,
        "selected_original_owner_sha256_verified": True,
        "selected_original_owner_count": len(OWNER_PINS),
        "original_selected_owner_sha256": {name: pin[1] for name, pin in OWNER_PINS.items()},
        "scenes": scenes,
        "full_40_scenes_or_full_owner_graph_checked": False,
        "source_to_export_renderer_material_assignment_proven": False,
        "unity_or_android_device_executed": False,
        "original_data_or_export_modified": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--owners", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    result = probe(args.source, args.owners, args.manifest)
    if args.report:
        out = args.report.resolve()
        if out.is_relative_to(args.source.resolve()) or out.is_relative_to(args.owners.resolve()):
            raise SourceError("report_inside_original_asset_or_staging_refused")
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RAFT_B03_ORIGINAL_MATERIAL_TARGETS " + json.dumps(result, sort_keys=True))
    if any(not data["staged_material_object_links_valid"] for data in result["scenes"].values()):
        raise SystemExit("Some selected original material targets cannot be proven against staged owners")
    if sum(data["counts"].get("external_staged_material_target_verified", 0)
           for data in result["scenes"].values()) == 0:
        raise SystemExit("No original staged-owner material target identity could be verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
