#!/usr/bin/env python3
"""GT read-only bounded diagnosis of real AssetRipper Material→Texture targets.

Do not rewrite materials or GUIds. Count all exported Texture PPtrs and explain
why B46 rejects target types/fileIDs, without emitting original paths, names,
GUIDs, property names, texture bytes, or any asset content.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.verify_exported_material_texture_links import (
    BUILTIN, CLASSES, GUID, HEADER, IMAGES, ZERO, GuardError,
    is_texture, material_docs, pointer, read, texenv,
)

YAML_TEXTURE_FILES = frozenset((".asset", ".cubemap", ".rendertexture"))
CODES = frozenset((
    "valid_imported_image", "valid_serialized_texture_object",
    "missing_target_guid", "imported_image_wrong_file_id",
    "imported_image_wrong_importer",
    "serialized_texture_subobject_missing",
    "unsupported_texture_target_file_type", "null",
    "built_in_unverified", "local_embedded_texture",
))
MAX_ENTRIES = 250_000
MAX_SAMPLES = 0


def classify(target: Path, metadata: str, fid: int) -> str:
    """Describe target mismatch using category only, never original identity."""
    if is_texture(target, metadata, fid):
        return ("valid_imported_image" if target.suffix.lower() in IMAGES
                else "valid_serialized_texture_object")
    if target.suffix.lower() in IMAGES:
        if fid != 2800000:
            return "imported_image_wrong_file_id"
        return "imported_image_wrong_importer"
    if target.suffix.lower() in YAML_TEXTURE_FILES:
        return "serialized_texture_subobject_missing"
    return "unsupported_texture_target_file_type"


def inspect(project: Path) -> dict:
    project = project.absolute()
    if any(path.is_symlink() for path in (project, *project.parents)):
        raise GuardError("symlinked_project_root")
    assets = project / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise GuardError("missing_assets_root")
    paths = list(assets.rglob("*"))
    if len(paths) > MAX_ENTRIES or any(path.is_symlink() for path in paths):
        raise GuardError("unsafe_or_excessive_export")
    files = {p for p in paths if p.is_file()}
    targets = {}
    for meta in files:
        if not meta.name.endswith(".meta"):
            continue
        identity = GUID.findall(read(meta))
        if len(identity) != 1:
            raise GuardError("missing_or_duplicate_meta_guid")
        guid = identity[0].lower()
        target = meta.with_name(meta.name[:-5])
        if guid in targets or guid in BUILTIN or guid == ZERO:
            raise GuardError("duplicate_or_reserved_meta_guid")
        if target not in files:
            raise GuardError("orphan_asset_meta")
        targets[guid] = (target, meta)

    mats = sorted(p for p in files if p.suffix.lower() == ".mat")
    if not mats:
        raise GuardError("missing_exported_materials")
    status = Counter()
    unique_refs = set()
    mats_seen = 0
    slots = 0
    checked = {}
    for mat in mats:
        if mat.with_name(mat.name + ".meta") not in files:
            raise GuardError("missing_material_meta")
        docs, local = material_docs(read(mat))
        for doc in docs:
            mats_seen += 1
            for fid, guid, kind in texenv(doc):
                slots += 1
                if fid == 0:
                    if guid is not None and (guid != ZERO or kind != 0):
                        raise GuardError("invalid_null_texture_pointer")
                    status["null"] += 1
                elif fid < 0:
                    raise GuardError("negative_texture_file_id")
                elif guid is None or guid == ZERO:
                    if kind not in (None, 0) or local.get(fid) not in CLASSES:
                        raise GuardError("unresolved_local_texture")
                    status["local_embedded_texture"] += 1
                elif guid in BUILTIN:
                    if kind != 0:
                        raise GuardError("invalid_builtin_texture_type")
                    status["built_in_unverified"] += 1
                else:
                    if kind not in (2, 3):
                        raise GuardError("invalid_external_texture_type")
                    identity = guid, fid
                    unique_refs.add(identity)
                    if identity not in checked:
                        if guid not in targets:
                            checked[identity] = "missing_target_guid"
                        else:
                            target, meta = targets[guid]
                            checked[identity] = classify(target, read(meta), fid)
                    result = checked[identity]
                    if result not in CODES:
                        raise GuardError("unknown_texture_classification")
                    status[result] += 1
    invalid = sum(status[c] for c in (
        "missing_target_guid", "imported_image_wrong_file_id",
        "imported_image_wrong_importer", "serialized_texture_subobject_missing",
        "unsupported_texture_target_file_type"
    ))
    return {
        "schema": "GT_EXPORTED_MATERIAL_TEXTURE_TARGET_AGGREGATE_V1",
        "status": "REJECTED" if invalid else "TARGET_TYPES_VALID",
        "material_files": len(mats),
        "material_objects": mats_seen,
        "texture_slots": slots,
        "distinct_external_texture_target_pairs": len(unique_refs),
        "external_texture_refs_invalid": invalid,
        "counts": {key: status[key] for key in sorted(CODES)},
        "original_source_texture_object_identity_compared": False,
        "original_exported_assets_modified": False,
        "original_guid_or_filename_disclosed": False,
        "shader_program_or_device_pixels_verified": False,
        "asset_ripper_exported_texture_target_classification_only": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    target = args.out.absolute()
    if target.is_relative_to(args.project.absolute()):
        raise GuardError("diagnostic_report_inside_export")
    try:
        report = inspect(args.project)
    except (GuardError, OSError) as error:
        safe_code = str(error) if isinstance(error, GuardError) else "unreadable_export"
        report = {
            "schema": "GT_EXPORTED_MATERIAL_TEXTURE_TARGET_AGGREGATE_V1",
            "status": "INCONCLUSIVE",
            "error_code": safe_code,
            "original_exported_assets_modified": False,
            "shader_program_or_device_pixels_verified": False,
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("GT_ACTUAL_EXPORTED_TEXTURE_TARGETS " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "TARGET_TYPES_VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
