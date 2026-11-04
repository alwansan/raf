#!/usr/bin/env python3
"""B03: SHA-verified original Renderer -> Material source-pointer baseline.

Six immutable original Unity scene blobs from ZIP2 are read with UnityPy.
No original object names, paths, PPtrs or payload bytes are published. This
only establishes source-side reference shape; export and phone remain unknown.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath

from scripts.b21_scene_lightmap_links import PIN, SourceError, verify_source

ORIGINAL_PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
RENDERER_CLASSES = frozenset({
    "MeshRenderer", "SkinnedMeshRenderer", "ParticleSystemRenderer",
    "TrailRenderer", "LineRenderer", "SpriteRenderer",
})
MAX_OBJECTS = 100_000
MAX_RENDERERS = 50_000
MAX_MATERIAL_SLOTS = 256
MANIFEST_COLUMNS = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]


def manifest_provider_basename_counts(manifest: Path) -> Counter:
    """Index immutable ZIP2 manifest owner basename shapes, never source bytes."""
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 1024 * 1024:
        raise SourceError("unsafe_or_oversize_original_manifest")
    result = Counter()
    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        rows = csv.DictReader(f, delimiter="\t")
        if rows.fieldnames != MANIFEST_COLUMNS:
            raise SourceError("unexpected_original_manifest_columns")
        for row in rows:
            if None in row or any(x is None for x in row.values()):
                raise SourceError("malformed_original_manifest_entry")
            path = row["relative_path_under_Raft"]
            if ("\\" in path or not path.startswith("Raft_Data/") or
                any(x in ("", ".", "..") for x in path.split("/"))):
                # Root executable and non-data entries can exist; only Raft_Data
                # members are candidates. Unsafe Raft_Data paths are never used.
                if path.startswith("Raft_Data/"):
                    raise SourceError("unsafe_original_manifest_owner_path")
                continue
            if not row["sha256"] or len(row["sha256"]) != 64:
                raise SourceError("invalid_original_manifest_digest")
            result[PurePosixPath(path).name] += 1
    if not result:
        raise SourceError("manifest_lacks_original_data_providers")
    return result


def declared_provider_kind(path: object, manifest: Counter) -> str:
    """A manifest filename match is NOT a proven Material target identity."""
    if not isinstance(path, str) or not path or "\x00" in path:
        return "unknown_original_external_name"
    name = PurePosixPath(path.replace("\\", "/")).name
    if not name or name in (".", ".."):
        return "unknown_original_external_name"
    matches = manifest.get(name, 0)
    if matches == 1:
        return "provider_name_declared_in_zip2_manifest"
    if matches > 1:
        return "ambiguous_manifest_provider_basename"
    return "provider_name_not_in_zip2_manifest"


def pointer_shape(pointer: object, known_local: dict[int, str], external_count: int) -> tuple[str, int, int]:
    """Fail closed on wrong PPtr fields; do not infer external target identity."""
    if not isinstance(pointer, dict) or set(pointer) != {"m_FileID", "m_PathID"}:
        raise SourceError("original_material_pointer_schema_invalid")
    file_id, path_id = pointer["m_FileID"], pointer["m_PathID"]
    if type(file_id) is not int or type(path_id) is not int or file_id < 0 or path_id < 0:
        raise SourceError("original_material_pointer_component_invalid")
    if path_id == 0:
        if file_id:
            raise SourceError("nonzero_external_file_id_for_null_pointer")
        return "null_material_slot", file_id, path_id
    if file_id:
        if file_id > external_count:
            raise SourceError("external_reference_index_out_of_bounds")
        return "external_target_unverified", file_id, path_id
    if path_id not in known_local:
        raise SourceError("missing_local_material_target")
    if known_local[path_id] != "Material":
        raise SourceError("wrong_local_material_target_type")
    return "local_material_target_verified", file_id, path_id


def analyze_scene(objects: list, external_count: int, external_paths=None, manifest_names=None) -> dict:
    """Read only real original serialized headers and bounded material PPtrs."""
    if type(external_count) is not int or external_count < 0 or external_count > 65535:
        raise SourceError("invalid_externals_count")
    if len(objects) > MAX_OBJECTS:
        raise SourceError("original_scene_object_count_over_budget")
    if (external_paths is None) != (manifest_names is None):
        raise SourceError("partial_provider_verification_configuration")
    if external_paths is not None and (len(external_paths) != external_count or
                                       not isinstance(manifest_names, Counter)):
        raise SourceError("externals_table_schema_mismatch")
    identities = {}
    for obj in objects:
        pid = getattr(obj, "path_id", None)
        if type(pid) is not int or pid <= 0:
            raise SourceError("bad_original_object_path_id")
        if pid in identities:
            raise SourceError("duplicate_original_scene_object_id")
        identities[pid] = str(obj.type.name)
    counts = Counter()
    edges = []
    referenced_external_ids = set()
    referenced_provider_names = set()
    for obj in objects:
        kind = str(obj.type.name)
        if kind not in RENDERER_CLASSES:
            continue
        counts["original_renderer_objects"] += 1
        counts["renderer_class_" + kind] += 1
        if counts["original_renderer_objects"] > MAX_RENDERERS:
            raise SourceError("original_renderers_over_budget")
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            counts["renderer_typetree_undecodable"] += 1
            continue
        if not isinstance(tree, dict):
            counts["renderer_typetree_undecodable"] += 1
            continue
        slots = tree.get("m_Materials")
        if not isinstance(slots, list):
            counts["renderer_material_array_schema_unknown"] += 1
            continue
        if len(slots) > MAX_MATERIAL_SLOTS:
            raise SourceError("renderer_material_slot_count_over_budget")
        counts["renderer_with_decoded_material_array"] += 1
        if not slots:
            counts["renderer_with_empty_material_array"] += 1
        for i, raw in enumerate(slots):
            status, fid, pid = pointer_shape(raw, identities, external_count)
            counts["original_material_slots"] += 1
            counts[status] += 1
            if fid:
                referenced_external_ids.add(fid)
                if external_paths is not None:
                    owner_name = external_paths[fid - 1]
                    shape = declared_provider_kind(owner_name, manifest_names)
                    counts["external_" + shape] += 1
                    if shape == "provider_name_declared_in_zip2_manifest":
                        referenced_provider_names.add(PurePosixPath(owner_name.replace("\\", "/")).name)
            # SHA commitment to the full original source identity graph: no IDs
            # or names emitted, and no single-edge hashes to facilitate guessing.
            edges.append((str(obj.path_id), kind, str(i), str(fid), str(pid), status))
    if not counts["original_renderer_objects"]:
        raise SourceError("no_original_renderer_objects")
    digest = hashlib.sha256(
        "\n".join("\t".join(row) for row in sorted(edges)).encode("utf-8")
    ).hexdigest() if edges else None
    unknown = counts["renderer_typetree_undecodable"] + counts["renderer_material_array_schema_unknown"]
    counts["distinct_referenced_external_table_indices"] = len(referenced_external_ids)
    counts["distinct_manifest_declared_external_provider_names"] = len(referenced_provider_names)
    return {
        "counts": dict(sorted(counts.items())),
        "original_renderer_material_edges_sha256": digest,
        "original_material_array_decoded_for_all_renderers": unknown == 0,
        "original_references_structurally_valid": True,
        "external_material_target_object_verified": False,
        "same_export_renderer_material_lineage_verified": False,
        "shader_program_or_device_pixels_verified": False,
    }


def probe(root: Path, loader=None, manifest: Path | None = None) -> dict:
    """Reject mutable/bad sources before parsing, even if data would decode."""
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise SourceError("unsafe_original_scene_root")
    for name, expected in PIN.items():
        verify_source(root / name, expected)
    manifest_names = manifest_provider_basename_counts(manifest) if manifest is not None else None
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    scenes = {}
    for name in PIN:
        env = loader(root / name)
        source_file = env.file
        # Ext table ownership is per serialized file, not global or path guessed.
        if not hasattr(source_file, "externals") or not hasattr(source_file, "objects"):
            raise SourceError("original_scene_reader_incomplete")
        objects = list(source_file.objects.values())
        external_paths = [getattr(entry, "path", None) for entry in source_file.externals]
        output = analyze_scene(objects, len(external_paths), external_paths if manifest_names is not None else None, manifest_names)
        output["original_sha256"] = PIN[name][1]
        output["original_bytes"] = PIN[name][0]
        scenes[name] = output
        del env, source_file, objects
    return {
        "source_commit": ORIGINAL_PIN,
        "selected_original_scenes": len(PIN),
        "source_sha256_verified": True,
        "original_manifest_provider_names_checked": manifest_names is not None,
        "external_owner_file_bytes_sha256_verified": False,
        "source_only": True,
        "scenes": scenes,
        "all_40_scenes_checked": False,
        "original_to_export_renderer_material_mapping_verified": False,
        "exported_unity_game_or_device_executed": False,
        "game_source_or_assets_mutated": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--manifest", type=Path, help="Immutable ZIP2 manifest from pinned checkout, not an untrusted release listing")
    args = p.parse_args()
    result = probe(args.source, manifest=args.manifest)
    # Stop if none of the six originals produced any decoded material arrays.
    decoded = sum(x["counts"].get("renderer_with_decoded_material_array", 0)
                  for x in result["scenes"].values())
    if decoded == 0:
        raise SourceError("original_renderer_material_arrays_never_decoded")
    if args.report is not None:
        target = args.report.resolve()
        if target.is_relative_to(args.source.resolve()):
            raise SourceError("report_inside_original_source_refused")
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RAFT_B03_ORIGINAL_RENDERER_MATERIAL_BASELINE " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
