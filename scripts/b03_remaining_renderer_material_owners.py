#!/usr/bin/env python3
"""B03: authenticate only the remaining original source Material owner(s).

The first B03 owner experiment authenticated 1609 external Material targets.
This complements it using the same six pinned original scene bytes without
re-downloading resources.assets/sharedassets0.assets, and never publishes
original object paths/IDs, Materials or byte payloads.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil

from scripts.b03_original_renderer_materials import (
    ORIGINAL_PIN, RENDERER_CLASSES, SourceError, analyze_scene,
    declared_provider_kind, pointer_shape,
)
from scripts.b03_original_renderer_target_resolution import (
    OWNER_PINS, resolve_scene_targets, select_original_objects, verify_owner,
)
from scripts.b21_scene_lightmap_links import PIN, verify_source

MANIFEST_COLUMNS = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
HEX = re.compile(r"[0-9a-f]{64}\Z")
MAX_SELECTED_BYTES = 400 * 1024 * 1024
MAX_PROVIDERS = 5


def read_manifest(manifest: Path) -> dict[str, dict]:
    if not manifest.is_file() or manifest.is_symlink() or manifest.stat().st_size > 1024 * 1024:
        raise SourceError("unsafe_or_missing_original_manifest")
    found = {}
    with manifest.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != MANIFEST_COLUMNS:
            raise SourceError("original_manifest_column_mismatch")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise SourceError("original_manifest_row_malformed")
            rel = row["relative_path_under_Raft"]
            if not rel.startswith("Raft_Data/"):
                continue
            parts = rel.split("/")
            if any(not part or part in (".", "..") or "\\" in part or "\x00" in part for part in parts):
                raise SourceError("unsafe_original_manifest_relative_path")
            name = PurePosixPath(rel).name
            if name in found:
                # Multiple providers with same basename must not be collapsed.
                found[name] = None
                continue
            try:
                count = int(row["bytes"])
            except ValueError as exc:
                raise SourceError("bad_original_manifest_size") from exc
            if count <= 0 or not HEX.fullmatch(row["sha256"]) or row["kind"] not in ("plain", "split"):
                raise SourceError("bad_original_manifest_identity")
            found[name] = {"name": name, "relative": rel, "kind": row["kind"],
                           "bytes": count, "sha256": row["sha256"]}
    return found


def select_residual(original_objects: list, external_paths: list, manifest: dict) -> Counter:
    """Select only valid external Material PPtrs not already SHA-confirmed by B03."""
    local = select_original_objects(original_objects)
    analyze_scene(original_objects, len(external_paths))
    chosen = Counter()
    for obj in original_objects:
        if str(obj.type.name) not in RENDERER_CLASSES:
            continue
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            continue
        if not isinstance(tree, dict) or not isinstance(tree.get("m_Materials"), list):
            continue
        for raw in tree["m_Materials"]:
            status, fid, _ = pointer_shape(raw, local, len(external_paths))
            if status != "external_target_unverified":
                continue
            raw_owner = external_paths[fid - 1]
            if not isinstance(raw_owner, str) or not raw_owner or "\x00" in raw_owner:
                raise SourceError("unknown_original_external_owner_name")
            name = PurePosixPath(raw_owner.replace("\\", "/")).name
            if name in OWNER_PINS:
                continue  # 1609 links authenticated in independent first run
            if name not in manifest or manifest[name] is None:
                raise SourceError("external_owner_unmatched_or_ambiguous_original_manifest")
            chosen[name] += 1
    return chosen


def determine_plan(source: Path, manifest: Path, loader=None) -> dict:
    if not source.is_dir() or any(p.is_symlink() for p in (source, *source.parents)):
        raise SourceError("unsafe_original_scene_root")
    for name, pin in PIN.items():
        verify_source(source / name, pin)
    entries = read_manifest(manifest)
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))
    refs = Counter()
    for name in PIN:
        env = loader(source / name)
        ext_paths = [getattr(x, "path", None) for x in env.file.externals]
        refs.update(select_residual(list(env.file.objects.values()), ext_paths, entries))
        del env
    if not refs or len(refs) > MAX_PROVIDERS:
        raise SourceError("residual_provider_count_outside_budget")
    total = sum(entries[name]["bytes"] for name in refs)
    if total > MAX_SELECTED_BYTES:
        raise SourceError("residual_provider_source_bytes_exceed_budget")
    return {"schema_version": 1, "source_commit": ORIGINAL_PIN,
            "selected": [{**entries[name], "source_references": refs[name]} for name in sorted(refs)],
            "reference_count": sum(refs.values()), "expected_original_bytes": total}


def restore_provider(zip2: Path, record: dict, stage: Path) -> Path:
    if record.get("kind") not in ("plain", "split") or record.get("name") != PurePosixPath(record["relative"]).name:
        raise SourceError("invalid_original_provider_plan")
    if record["name"] in OWNER_PINS:
        raise SourceError("refuse_duplicate_already_authenticated_provider")
    if any(x in (".", "..", "") or "\\" in x for x in record["relative"].split("/")):
        raise SourceError("unsafe_original_provider_path")
    source = zip2 / "Raft" / record["relative"]
    result = stage / record["name"]
    if stage.is_symlink() or not stage.is_dir() or result.exists() or result.is_symlink():
        raise SourceError("unsafe_staging_directory_or_existing_output")
    if source.is_symlink():
        raise SourceError("source_provider_symlink")
    temp = stage / (".b03-incomplete-" + record["name"])
    if temp.exists() or temp.is_symlink():
        raise SourceError("existing_staging_temporary_file")
    try:
        digest = hashlib.sha256()
        size = 0
        with temp.open("xb") as out:
            if record["kind"] == "plain":
                if not source.is_file():
                    raise SourceError("missing_immutable_plain_original_provider")
                inputs = [source]
            else:
                if not source.is_dir():
                    raise SourceError("missing_immutable_split_original_provider")
                inputs = sorted(source.glob("part-*"))
                if len(inputs) < 2 or any(p.name != f"part-{i:05d}" for i, p in enumerate(inputs)):
                    raise SourceError("missing_or_invalid_original_chunk_sequence")
            for part in inputs:
                if part.is_symlink() or not part.is_file():
                    raise SourceError("invalid_original_chunk_or_plain_file")
                with part.open("rb") as f:
                    while piece := f.read(1024 * 1024):
                        size += len(piece)
                        if size > record["bytes"]:
                            raise SourceError("original_provider_size_overflow")
                        digest.update(piece)
                        out.write(piece)
        if size != record["bytes"] or digest.hexdigest() != record["sha256"]:
            raise SourceError("original_provider_sha256_or_size_mismatch")
        os.link(temp, result)
    finally:
        temp.unlink(missing_ok=True)
    return result


def verify_selected(source: Path, manifest: Path, zip2: Path, stage: Path, plan: dict, loader=None) -> dict:
    current = determine_plan(source, manifest, loader)
    if plan != current:
        raise SourceError("source_residual_plan_changed")
    if any(p.is_symlink() for p in (zip2, *zip2.parents, stage, *stage.parents)):
        raise SourceError("unsafe_stage_or_zip2_checkout_ancestor")
    if not zip2.is_dir():
        raise SourceError("missing_pinned_zip2_checkout")
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))
    original_owners = {}
    for record in plan["selected"]:
        path = restore_provider(zip2, record, stage)
        verify_owner(path, (record["bytes"], record["sha256"]))
        env = loader(path)
        original_owners[record["name"]] = select_original_objects(list(env.file.objects.values()))
        del env
    entries = read_manifest(manifest)
    basename_counts = Counter({name: 2 if row is None else 1 for name, row in entries.items()})
    scene_counts = {}
    total = Counter()
    for name in PIN:
        env = loader(source / name)
        externals = [getattr(x, "path", None) for x in env.file.externals]
        r = resolve_scene_targets(list(env.file.objects.values()), externals, original_owners, basename_counts)
        scene_counts[name] = r["counts"]
        total.update(r["counts"])
        del env
    if total.get("external_staged_material_target_verified", 0) != plan["reference_count"]:
        raise SourceError("selected_original_provider_object_links_not_fully_verified")
    if total.get("external_staged_provider_missing_object", 0) or total.get("external_staged_provider_wrong_object_type", 0):
        raise SourceError("original_selected_provider_target_invalid")
    return {
        "schema_version": 1, "original_source_commit": ORIGINAL_PIN,
        "original_six_scene_sha256_verified": True,
        "new_original_provider_sha256_verified": True,
        "new_original_provider_count": len(plan["selected"]),
        "new_verified_provider_original_bytes": sum(x["bytes"] for x in plan["selected"]),
        "selected_original_material_links_verified": total["external_staged_material_target_verified"],
        "other_external_links_not_retested_in_this_run": total["external_other_zip2_provider_unverified"],
        "source_null_material_slots": total["original_null_slots"],
        "original_target_class_errors": 0,
        "previously_verified_providers_not_reloaded": True,
        "original_to_export_material_assignment_verified": False,
        "on_device_colors_or_gameplay_verified": False,
        "game_or_source_modified": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase", choices=("plan", "verify"), required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--checkout", type=Path)
    p.add_argument("--stage", type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--sparse-paths", type=Path)
    args = p.parse_args()
    if args.phase == "plan":
        result = determine_plan(args.source, args.manifest)
        args.plan.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.sparse_paths:
            args.sparse_paths.write_text(
                "".join("Raft/" + x["relative"] + "\n" for x in result["selected"]), encoding="utf-8")
        print("RAFT_B03_REMAINING_PLAN " + json.dumps({
            "source_sha": ORIGINAL_PIN, "provider_count": len(result["selected"]),
            "references": result["reference_count"], "bytes": result["expected_original_bytes"],
            "private_plan_only": True, "names_published": False}, sort_keys=True))
        return 0
    if args.checkout is None or args.stage is None:
        p.error("--checkout and --stage required for verify")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = verify_selected(args.source, args.manifest, args.checkout, args.stage, plan)
    if args.report:
        path = args.report.resolve()
        if path.is_relative_to(args.source.resolve()) or path.is_relative_to(args.stage.resolve()):
            raise SourceError("public_report_inside_original_assets_refused")
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RAFT_B03_REMAINING_SOURCE_TARGETS " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
