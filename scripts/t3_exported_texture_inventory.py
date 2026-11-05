#!/usr/bin/env python3
"""T3: enumerate ALL actual bounded AssetRipper TextureImporter/image outputs.

This follows the genuine 106/106 selected Texture2D trace GUID metadata gaps
observed in CI 41944064897. It distinguishes absent image files from files
under unrelated GUIDs and possible embedded Unity Texture2D YAML documents.
No original names, GUIDs, game pixels or raw metadata leave runner-private RAM.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import t3_texture_importer_presence as source_probe

IMAGE_SUFFIXES = frozenset((".png", ".jpg", ".jpeg", ".tga", ".dds", ".exr",
                           ".hdr", ".bmp", ".tiff", ".tif", ".webp", ".psd",
                           ".ktx", ".pvr"))
YAML_SUFFIXES = frozenset((".asset", ".unity", ".prefab"))
YAML_TEXTURE2D = re.compile(rb"(?m)^---[ \t]+!u!28[ \t]+&-?[0-9]+(?:[ \t]+stripped)?[ \t]*$")
HEX_GUID = re.compile(r"[0-9a-f]{32}\Z")
MAX_YAML = 64 * 1024 * 1024


def aggregate_output(root: Path, selected: dict) -> dict:
    """One-pass bounded read-only output inventory and exact GUID correlation."""
    if not root.is_dir() or root.is_symlink() or any(p.is_symlink() for p in root.parents):
        raise ValueError("missing_or_redirected_actual_export_Assets")
    rows = selected.get("objects") if isinstance(selected, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("missing_selected_same_export_Texture2D_trace")
    source_guids = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("class_id") != 28:
            raise ValueError("unexpected_selected_source_class")
        ptr = row.get("export")
        if (not isinstance(ptr, dict) or set(ptr) != {"file_id", "guid", "type"}
            or type(ptr["file_id"]) is not int or ptr["file_id"] <= 0
            or type(ptr["type"]) is not int or ptr["type"] not in (2, 3)
            or not isinstance(ptr["guid"], str) or not HEX_GUID.fullmatch(ptr["guid"])):
            raise ValueError("invalid_original_exported_Texture2D_pointer")
        if ptr["guid"] in source_guids:
            raise ValueError("distinct_linked_texture_objects_share_export_GUID")
        source_guids.add(ptr["guid"])

    entries = sorted(root.rglob("*"))
    if len(entries) > source_probe.MAX_FILES or any(p.is_symlink() for p in entries):
        raise ValueError("linked_or_oversize_Unity_export_file_collection")

    outputs = Counter()
    owner_guids = Counter()
    target_importers = Counter()
    for file in entries:
        if not file.is_file():
            continue
        extension = file.suffix.lower()
        if extension != ".meta":
            outputs["exported_regular_files"] += 1
            if extension in IMAGE_SUFFIXES:
                outputs["image_file_candidates"] += 1
                outputs["images_" + extension.removeprefix(".")] += 1
                if file.stat().st_size == 0:
                    outputs["zero_byte_image_candidates"] += 1
            if extension in YAML_SUFFIXES and file.stat().st_size <= MAX_YAML:
                with file.open("rb") as fd:
                    if fd.read(16).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
                        outputs["unity_yaml_containers"] += 1
                        fd.seek(0)
                        raw = fd.read(MAX_YAML + 1)
                        outputs["embedded_Texture2D_YAML_documents"] += len(YAML_TEXTURE2D.findall(raw))
            continue
        outputs["meta_files"] += 1
        if file.stat().st_size > source_probe.MAX_META_BYTES:
            raise ValueError("oversized_export_meta")
        content = file.read_text(encoding="utf-8-sig")
        found = source_probe.GUID_LINE.findall(content)
        if len(found) != 1:
            outputs["metadata_invalid_GUID_cardinality"] += 1
            continue
        guid = found[0].lower()
        if guid == "0" * 32:
            outputs["metadata_zero_GUID"] += 1
            continue
        owner_guids[guid] += 1
        kind = source_probe.safe_kind(content)
        outputs["all_meta_" + kind] += 1
        corresponding = Path(str(file)[:-5])
        asset_exists = (corresponding.is_file() or corresponding.is_dir()) and not corresponding.is_symlink()
        if not asset_exists:
            outputs["orphan_meta_no_exported_asset"] += 1
        if corresponding.suffix.lower() in IMAGE_SUFFIXES:
            outputs["image_candidate_meta_files"] += 1
            outputs["image_meta_" + kind] += 1
        if guid in source_guids:
            target_importers[kind] += 1
            outputs["selected_source_GUID_meta_records"] += 1
    outputs["distinct_export_meta_GUIDs"] = len(owner_guids)
    outputs["duplicate_global_meta_GUIDs"] = sum(n - 1 for n in owner_guids.values() if n > 1)

    matched_guid_count = sum(1 for guid in source_guids if owner_guids.get(guid) == 1)
    all_output_importer_count = outputs["all_meta_TextureImporter"]
    all_output_image_count = outputs["image_file_candidates"]
    if matched_guid_count == len(source_guids):
        outcome = "ALL_SELECTED_GUIDS_IN_EXPORT_META"
    elif all_output_importer_count == 0 and all_output_image_count == 0 and outputs["embedded_Texture2D_YAML_documents"] == 0:
        outcome = "NO_TEXTURE_ASSET_FILES_IN_BOUNDED_EXPORT"
    elif all_output_importer_count or all_output_image_count or outputs["embedded_Texture2D_YAML_documents"]:
        outcome = "TEXTURE_ASSETS_PRESENT_GUID_CORRESPONDENCE_UNPROVEN"
    else:
        outcome = "OUTPUT_ASSET_KINDS_INCONCLUSIVE"

    return {
        "schema_version": 1,
        "experiment": "T3-authentic-bounded-export-texture-asset-GUID-closure",
        "source_linked_distinct_Texture2D_objects": len(rows),
        "source_linked_distinct_export_pointer_GUIDs": len(source_guids),
        "exact_source_linked_GUIDs_present_once_in_meta": matched_guid_count,
        "exact_source_linked_GUIDs_absent_from_meta": sum(owner_guids.get(g) == 0 for g in source_guids),
        "exact_source_linked_GUIDs_duplicate_meta": sum(owner_guids.get(g, 0) > 1 for g in source_guids),
        "all_output": dict(sorted(outputs.items())),
        "selected_importer_kinds": dict(sorted(target_importers.items())),
        "bounded_export_texture_asset_assessment": outcome,
        "real_Unity_editor_import_or_device_pixels_verified": False,
        "game_original_assets_modified": False,
        "all_source_or_output_ids_redacted": True,
    }


def real(original: Path, manifest: Path, project: Path, w1: Path, b02: Path) -> dict:
    from scripts import t3_linked_texture_sampler_export as linked
    import UnityPy
    from scripts import b05_verify_material_texenv_bindings as b05
    from scripts.b03_original_renderer_materials import manifest_provider_basename_counts

    originals = b05.original_texenvs(original, owner_names={linked.OWNER})
    env = UnityPy.load(str(original/"Raft_Data"/linked.OWNER))
    owners = [o.path for o in env.file.externals]
    names, counts = linked.source_targets(originals, owners, manifest_provider_basename_counts(manifest))
    w1trace = json.loads(w1.read_text(encoding="utf8"))
    b02trace = json.loads(b02.read_text(encoding="utf8"))
    selected = linked.subset_same_export(names, w1trace, b02trace)
    output = aggregate_output(project/"Assets", selected)
    if output["source_linked_distinct_Texture2D_objects"] != counts["unique_linked_source_Texture2D_candidates"]:
        raise ValueError("actual_exported_Texture2D_trace_population_drift")
    return output


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original", "manifest", "project", "w1-trace", "b02-trace", "out"):
        p.add_argument("--"+name, type=Path, required=True)
    a = p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()) or a.out.resolve().is_relative_to(a.project.resolve()):
        raise ValueError("unsafe_public_aggregate_destination")
    try:
        report = real(a.original, a.manifest, a.project, a.w1_trace, a.b02_trace)
    except Exception as err:
        report = {
            "schema_version": 1, "experiment": "T3-authentic-bounded-export-texture-asset-GUID-closure",
            "status": "INCONCLUSIVE", "exception_type": type(err).__name__,
            "real_Unity_editor_import_or_device_pixels_verified": False}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf8")
    print("T3_EXPORT_ALL_TEXTURE_ASSETS_AGGREGATE "+json.dumps(report, sort_keys=True))
    return 0 if report.get("bounded_export_texture_asset_assessment") else 2

if __name__ == "__main__":
    raise SystemExit(main())
