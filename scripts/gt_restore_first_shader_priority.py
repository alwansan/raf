#!/usr/bin/env python3
"""GT restore-first private priority queue for source-authentic original shaders.

Only the six SHA-pinned original Raft scenes with exactly 1633 typed source
Renderer/Material/Shader48 slots are currently connected to the same-instance
W1/B02 AssetRipper trace. Output has TWO tiers:
  --out: SAFE aggregate count/impact with no source IDs, GUIDs or asset paths.
  --private-queue: original source owner/PathID -> exact exported GUID/path,
                   strictly runner-private and never an Actions artifact.
This ranks actual *serialized Renderer material slots*, not GPU draw calls or
the full game's 770 distinct Material-YAML documents (nor 770 Shader objects).

This action does not restore a shader by itself; it produces an authentic,
actionable and fail-closed source-to-export queue for restoring the highest-
impact original programs *before* any Android XAPK compatibility test.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path

from scripts import t3_audit_exported_material_programs as quality
from scripts import t3_original_renderer_shader_impact as originals
from scripts import t3_source_renderer_shader_to_postvendor_export as lineage
from scripts.verify_export_lineage import identity, pointer

STATUS = "GT_RESTORE_FIRST_AUTHENTIC_SOURCE_RENDERER_SHADER_QUEUE"
SOURCE_SCOPE = "six_SHA_pinned_original_scenes_only"
EXPECTED_TYPED_SOURCE_SHADER48 = lineage.EXPECTED_TYPED_SOURCES
EXPECTED_TYPED_SOURCE_SLOTS = lineage.EXPECTED_TYPED_SLOT_USE

def rank_original_shader_queue(source_use: dict, w1: dict,
                               profiles: dict, verified_source_report: dict):
    """Deterministic private queue; call existing full source↔export proof first."""
    audited = lineage.join(source_use, w1, profiles,
                          verified_source_report=verified_source_report)
    original_to_export = {}
    for row in w1["objects"]:
        if row.get("class_id") != 48:
            continue
        original = identity(row["source"])
        if original not in source_use:
            continue
        if original in original_to_export:
            raise ValueError("duplicate_authenticated_original_shaders")
        original_to_export[original] = pointer(row["export"])
    if set(original_to_export) != set(source_use):
        raise ValueError("source_original_to_export_shader_map_incomplete")

    rows = []
    for original, slots in source_use.items():
        fid, guid, kind = original_to_export[original]
        if fid > 0 and guid in lineage.VALID_BUILTIN_GUIDS and kind == "0":
            status = "unity_builtin"
            guid = None  # an engine GUID is NOT a local .shader/.meta target
        elif fid == 4800000 and kind == "3" and guid in profiles:
            status = "dummy" if profiles[guid]["dummy"] else "vendor_non_dummy"
        else:
            raise ValueError("original_exported_shader_target_missing_or_ambiguous")
        rows.append({
            "original_owner": original[0], "original_shader_path_id": original[1],
            "original_scene_renderer_material_slots": slots,
            "exported_Shader_GUID": guid, "program_status": status,
        })
    rows.sort(key=lambda r:(
        r["program_status"] != "dummy",
        -r["original_scene_renderer_material_slots"],
        r["original_owner"], r["original_shader_path_id"]
    ))
    if sum(row["original_scene_renderer_material_slots"] for row in rows) != EXPECTED_TYPED_SOURCE_SLOTS:
        raise ValueError("original_source_renderer_slot_count_drift")
    dummy = [row for row in rows if row["program_status"] == "dummy"]
    if len(dummy) != audited["source_Shader48_unique_targets_by_actual_postvendor_status"].get(
        "source_Shader48_targets_with_dummy", 0):
        raise ValueError("restoration_queue_dummy_source_count_mismatch")
    if sum(row["original_scene_renderer_material_slots"] for row in dummy) != audited[
        "original_scene_slot_use_by_actual_postvendor_shader_status"].get(
            "scene_renderer_material_slots_to_dummy", 0):
        raise ValueError("restoration_queue_dummy_slot_count_mismatch")

    report = {
        "schema_version": 1,
        "status": STATUS,
        "scope": SOURCE_SCOPE,
        "source_original_6_scene_sha_authenticated": verified_source_report.get(
            "six_original_scenes_sha_verified") is True,
        "same_instance_original_Shader48_export_trace_verified": True,
        "same_instance_original_source_count": len(rows),
        "original_typed_renderer_material_slots": EXPECTED_TYPED_SOURCE_SLOTS,
        "still_dummy_distinct_original_Shader48_targets": len(dummy),
        "still_dummy_original_renderer_material_slots": sum(
            row["original_scene_renderer_material_slots"] for row in dummy),
        "highest_priority_dummy_original_renderer_slots": (
            dummy[0]["original_scene_renderer_material_slots"] if dummy else 0),
        "sorted_dummy_priority_slot_weights_without_ids": [
            row["original_scene_renderer_material_slots"] for row in dummy],
        "other_material_sources_outside_original_6_scene_scope_unverified": True,
        "full_770_dummy_Material_YAML_docs_not_equated_to_distinct_shaders": True,
        "source_original_DXBC_to_complete_ShaderLab_restored_by_queue": False,
        "original_ShaderLab_program_Guid_and_material_texture_parity_proven_by_ranking": False,
        "Unity_Editor_Android_or_Adreno_pixels_verified": False,
        "game_project_files_or_original_meta_modified": False,
        "private_source_ids_guids_or_asset_paths_published": False,
    }
    if not report["source_original_6_scene_sha_authenticated"]:
        raise ValueError("original_shader_priority_source_SHA_not_verified")
    return rows, report


def _strict_destination(path: Path, source: Path, project: Path):
    path = Path(path).absolute()
    if (path.exists() or path.is_symlink() or
            path.is_relative_to(source.absolute()) or
            path.is_relative_to(project.absolute()) or
            not path.parent.is_dir() or
            any(p.is_symlink() for p in (path, *path.parents))):
        raise ValueError("unsafe_GT_priority_report_destination")
    return path


def real_authenticated_queue(original_root: Path, manifest: Path,
                             project: Path, w1_trace: Path,
                             b02_trace: Path):
    # Full original/authentic six-scene and material Shader48 linkage; same
    # export instance, source owner SHA/trace and post-vendor program quality.
    published = lineage.run(original_root,manifest,project,w1_trace,b02_trace)
    if published.get("status") != lineage.STATUS:
        raise ValueError("verified_original_to_export_source_graph_missing")
    exact_slots = {}
    report = originals.load_original(original_root,manifest,
                                     private_slot_counts=exact_slots)
    typed = {key: v for key,v in exact_slots.items()
             if key[0] in originals.SHADER_OWNERS_SELECTED}
    project_assets = project/"Assets"
    entries = sorted(project_assets.rglob("*"))
    profiles = quality._shader_profiles(entries)
    trace = json.loads(w1_trace.read_text(encoding="utf-8"))
    queue, safe = rank_original_shader_queue(typed,trace,profiles,report)
    if (safe["still_dummy_distinct_original_Shader48_targets"]
            != published["source_Shader48_unique_targets_by_actual_postvendor_status"][
                "source_Shader48_targets_with_dummy"]
        or safe["still_dummy_original_renderer_material_slots"]
            != published["original_scene_slot_use_by_actual_postvendor_shader_status"][
                "scene_renderer_material_slots_to_dummy"]):
        raise ValueError("inconsistent_duplicated_source_export_join")
    # Only exact local .shader.meta GUIDs can supply paths for a private
    # source-restoration task. Ambiguity or missing linkage fails closed.
    local_guids = {}
    for path in entries:
        if path.suffix != ".shader" or not path.is_file():
            continue
        meta = Path(str(path)+".meta")
        ids = quality.GUID.findall(quality._read(meta,quality.MAX_META))
        if len(ids) != 1 or ids[0].lower() in local_guids:
            raise ValueError("missing_or_ambiguous_original_export_ShaderImporter_guid")
        local_guids[ids[0].lower()] = path.relative_to(project_assets).as_posix()
    for row in queue:
        if row["program_status"] != "unity_builtin":
            if row["exported_Shader_GUID"] not in local_guids:
                raise ValueError("original_source_priority_target_meta_unresolved")
            row["private_exported_relative_shader_path"] = local_guids[
                row["exported_Shader_GUID"]]
        else:
            row["private_exported_relative_shader_path"] = None
    safe["private_priority_queue_complete"] = True
    return queue, safe


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","project","w1-trace","b02-trace",
                 "private-queue","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args(argv)
    output = _strict_destination(a.out,a.original,a.project)
    private = _strict_destination(a.private_queue,a.original,a.project)
    if output == private:
        raise ValueError("private_and_public_Shader_priority_destination_alias")
    try:
        queue, report = real_authenticated_queue(
            a.original,a.manifest,a.project,a.w1_trace,a.b02_trace)
        # Owner-private actionable file: source IDs/GUIDs/paths. Never print,
        # commit, upload or include in source-free JSON/public artifacts.
        fd=os.open(private,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as stream:
                json.dump({"scope":SOURCE_SCOPE,"priority":queue},stream,
                          sort_keys=True,indent=2)
                stream.write("\n")
        except BaseException:
            private.unlink(missing_ok=True)
            raise
        # Sanitize output through explicit primitive-only aggregate schema.
        with output.open("x",encoding="utf-8") as stream:
            json.dump(report,stream,sort_keys=True,indent=2)
            stream.write("\n")
    except BaseException as error:
        # Do not leak third-party source identifiers through path/exception.
        print("GT_RESTORE_FIRST_SHADER_PRIORITY_BLOCKED "
              +json.dumps({"status":"INCONCLUSIVE",
                           "error_type":type(error).__name__,
                           "original_shader_source_or_ids_published":False}))
        return 2
    print("GT_RESTORE_FIRST_SHADER_PRIORITY_SAFE "+json.dumps(report,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
