#!/usr/bin/env python3
"""B15: source-pinned, READ-ONLY Texture2D sampler -> TextureImporter parity.

The explicit identity sidecar MUST be from the same exporter invocation;
its presence is not independent proof of that provenance. This checks only
serialized settings, never ShaderLab/pixels or any edit to game assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

from scripts.verify_targeted_lfs_compute_sources import EXPECTED as SOURCE_PINS

ZIP2_COMMIT = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
GUID = re.compile(r"[0-9a-f]{32}\Z")
FIELDS = (
    ("m_FilterMode", "filterMode"),
    ("m_Aniso", "aniso"),
    ("m_MipBias", "mipBias"),
    ("m_WrapU", "wrapU"),
    ("m_WrapV", "wrapV"),
    ("m_WrapW", "wrapW"),
)
MAX_META_BYTES = 256_000


def regular_child(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("unsafe path")
    p = PurePosixPath(relative)
    if p.is_absolute() or any(s in ("", ".", "..") for s in relative.split("/")):
        raise ValueError("unsafe path")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("unsafe root")
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("linked asset/ancestor")
    if not cursor.is_file() or not cursor.resolve().is_relative_to(root.resolve()):
        raise ValueError("missing or external asset")
    return cursor


def check_rows(sidecar: dict) -> list[dict]:
    if (not isinstance(sidecar, dict) or sidecar.get("schema_version") != 1
            or sidecar.get("source_commit") != ZIP2_COMMIT
            or not isinstance(sidecar.get("export_instance"), str)
            or not GUID.fullmatch(sidecar["export_instance"])):
        raise ValueError("missing pinned same-export sidecar identity")
    rows = sidecar.get("textures")
    if not isinstance(rows, list) or not rows:
        raise ValueError("missing per-object identity rows")
    original_ids, export_ids, guids = set(), set(), set()
    keys = {"source_owner", "source_path_id", "source_bytes", "source_sha256",
            "export_asset", "export_guid"}
    for row in rows:
        if not isinstance(row, dict) or set(row) != keys:
            raise ValueError("incomplete identity row")
        owner = row["source_owner"]
        if owner not in SOURCE_PINS:
            raise ValueError("untrusted original owner")
        size, digest = SOURCE_PINS[owner]
        if (type(row["source_bytes"]) is not int or row["source_bytes"] != size
                or row["source_sha256"] != digest):
            raise ValueError("source fingerprint not pinned")
        if type(row["source_path_id"]) is not int or row["source_path_id"] <= 0:
            raise ValueError("invalid original pathID")
        if (not isinstance(row["export_guid"], str)
                or not GUID.fullmatch(row["export_guid"])):
            raise ValueError("invalid export GUID")
        rel = row["export_asset"]
        if not isinstance(rel, str) or not rel or not rel.endswith((".png", ".tga", ".jpg", ".jpeg", ".exr", ".asset", ".dds")):
            raise ValueError("missing export asset path")
        # Path validation is repeated at the actual file read.
        if "\\" in rel or ":" in rel or PurePosixPath(rel).is_absolute() or any(x in ("", ".", "..") for x in rel.split("/")):
            raise ValueError("unsafe export path")
        oid = (owner, row["source_path_id"])
        if oid in original_ids or rel in export_ids or row["export_guid"] in guids:
            raise ValueError("ambiguous original/export texture identity")
        original_ids.add(oid)
        export_ids.add(rel)
        guids.add(row["export_guid"])
    return rows


def original_sampler(tree: dict) -> tuple:
    settings = tree.get("m_TextureSettings") if isinstance(tree, dict) else None
    if not isinstance(settings, dict):
        raise ValueError("original Texture2D has no sampler settings")
    return normalize(settings, original=True)


def normalize(settings: dict, *, original: bool) -> tuple:
    values = []
    for source_key, export_key in FIELDS:
        if original:
            if source_key not in settings:
                raise ValueError("original sampler field missing")
            value = settings[source_key]
        else:
            available = [name for name in (export_key, source_key) if name in settings]
            if len(available) != 1:
                raise ValueError("absent/ambiguous exported sampler field")
            value = settings[available[0]]
        if source_key == "m_MipBias":
            if type(value) not in (float, int) or not math.isfinite(value):
                raise ValueError("non-finite sampler mip bias")
            value = float(value)
        else:
            if type(value) is not int:
                raise ValueError("sampler enum must be integer")
            if original and (value < 0 or value > (16 if source_key == "m_Aniso" else 3)):
                raise ValueError("invalid original sampler enum")
            if not original and (value < -1 or value > (16 if source_key == "m_Aniso" else 3)):
                raise ValueError("invalid importer sampler enum")
        values.append(value)
    return tuple(values)


def read_importer(meta: Path) -> tuple[str, tuple]:
    if meta.stat().st_size > MAX_META_BYTES:
        raise ValueError("oversized importer metadata")
    import yaml

    class UniqueSafeLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            result = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, (str, int)) or key in result:
                    raise ValueError("duplicate/unhashable Unity YAML key")
                result[key] = self.construct_object(value_node, deep=deep)
            return result

    doc = yaml.load(meta.read_text(encoding="utf-8-sig"), Loader=UniqueSafeLoader)
    if not isinstance(doc, dict) or type(doc.get("fileFormatVersion")) is not int or doc["fileFormatVersion"] != 2:
        raise ValueError("not Unity importer meta")
    guid, importer = doc.get("guid"), doc.get("TextureImporter")
    if not isinstance(guid, str) or not GUID.fullmatch(guid) or not isinstance(importer, dict):
        raise ValueError("missing unique TextureImporter/GUID")
    settings = importer.get("textureSettings")
    if not isinstance(settings, dict):
        raise ValueError("missing TextureImporter.textureSettings")
    return guid, normalize(settings, original=False)


def _authenticate(path: Path, size: int, digest: str) -> None:
    if path.stat().st_size != size:
        raise ValueError("original owner byte size mismatch")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    if h.hexdigest() != digest:
        raise ValueError("original owner SHA256 mismatch")


def inspect(original_root: Path, project: Path, sidecar: dict) -> dict:
    rows = check_rows(sidecar)
    assets = project / "Assets"
    if project.is_symlink() or not project.is_dir() or assets.is_symlink() or not assets.is_dir():
        raise ValueError("unsafe exported Unity project")
    import UnityPy

    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_owner"], []).append(row)
    original = {}
    for owner, items in grouped.items():
        path = regular_child(original_root, owner)
        _authenticate(path, *SOURCE_PINS[owner])
        needed = {row["source_path_id"] for row in items}
        for obj in UnityPy.load(str(path)).objects:
            if obj.path_id not in needed:
                continue
            key = (owner, obj.path_id)
            if key in original or obj.type.name != "Texture2D":
                raise ValueError("missing unique original Texture2D identity")
            original[key] = original_sampler(obj.read_typetree())
        if len([key for key in original if key[0] == owner]) != len(needed):
            raise ValueError("missing original Texture2D pathID")
    field_mismatches = {field: 0 for field, _ in FIELDS}
    unknown_importer_fields = {field: 0 for field, _ in FIELDS}
    matched = 0
    for row in rows:
        asset = regular_child(assets, row["export_asset"])
        meta = regular_child(assets, row["export_asset"] + ".meta")
        guid, exported = read_importer(meta)
        if guid != row["export_guid"]:
            raise ValueError("export GUID differs from same-export sidecar")
        expected = original[row["source_owner"], row["source_path_id"]]
        for i, (field, _) in enumerate(FIELDS):
            target = exported[i]
            # -1 is Unity import override sentinel; do not infer original.
            if field != "m_MipBias" and target == -1:
                unknown_importer_fields[field] += 1
            elif (not math.isclose(expected[i], target, rel_tol=0, abs_tol=1e-6)
                  if field == "m_MipBias" else expected[i] != target):
                field_mismatches[field] += 1
        matched += 1
    return {
        "schema_version": 1,
        "source_commit": ZIP2_COMMIT,
        "source_owners_authenticated": len(grouped),
        "linked_textures_compared": matched,
        "field_mismatches": field_mismatches,
        "unresolved_importer_defaults": unknown_importer_fields,
        "metadata_fields_faithful": not any(field_mismatches.values()) and not any(unknown_importer_fields.values()),
        "same_export_provenance_independently_verified": False,
        "unity_or_android_pixels_verified": False,
        "modified_assets": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original-root", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--sidecar", type=Path, required=True)
    args = ap.parse_args()
    # Never write repairs or reveal original object names/path IDs in output.
    report = inspect(args.original_root, args.project,
                     json.loads(args.sidecar.read_text(encoding="utf-8")))
    print("RAFT_B15_TEXTURE_SAMPLER_PARITY " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
