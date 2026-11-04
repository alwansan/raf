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

from scripts.verify_targeted_lfs_compute_sources import EXPECTED as COMPUTE_SOURCE_PINS

# Extra small original owner independently SHA-confirmed in B05 real ZIP2
# CI41929077930, also consistent with W2 original inventory (87 textures).
# Keep the global compute-source pinset unchanged.
SOURCE_PINS = {
    **COMPUTE_SOURCE_PINS,
    "sharedassets6.assets": (
        6_607_272,
        "0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632",
    ),
}

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
# Unity TextureImporter.mipMapBias documents -100 as an INVALID/UNSET importer
# override. Comparing it numerically to source Texture2D would fabricate drift.
MIP_BIAS_UNSET = -100.0


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
            # Unity importer -1 enum overrides and -100 mipMapBias are
            # UNSET defaults (not evidence of source mismatch or equivalence).
            if (field != "m_MipBias" and target == -1) or (field == "m_MipBias" and target == MIP_BIAS_UNSET):
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



def sidecar_from_export_trace(project: Path, trace: dict) -> dict:
    """Derive GUID->file mapping from ONE exporter trace, never from names.

    The trace remains a caller-supplied witness. Its export_instance label
    cannot independently establish provenance or visual equivalence.
    """
    if (not isinstance(trace, dict) or trace.get("schema_version") != 1
            or not isinstance(trace.get("export_instance"), str)
            or not GUID.fullmatch(trace["export_instance"])
            or not isinstance(trace.get("objects"), list)):
        raise ValueError("invalid same-instance exporter trace")
    rows = []
    wanted_guids = set()
    for item in trace["objects"]:
        if not isinstance(item, dict) or item.get("class_id") != 28:
            continue  # Only Texture2D; never infer other texture class settings.
        source, target = item.get("source"), item.get("export")
        if (not isinstance(source, dict) or set(source) != {"owner", "path_id"}
                or not isinstance(target, dict) or set(target) != {"file_id", "guid", "type"}):
            raise ValueError("incomplete original/export Texture2D trace")
        original_owner = source["owner"]
        if not isinstance(original_owner, str) or "\\" in original_owner or ":" in original_owner:
            raise ValueError("unsafe trace owner")
        pure = PurePosixPath(original_owner)
        if pure.is_absolute() or any(p in ("", ".", "..") for p in original_owner.split("/")):
            raise ValueError("unsafe trace owner")
        owner = pure.name
        if pure.parts not in ((owner,), ("Raft_Data", owner)):
            raise ValueError("unrecognized original source owner path")
        if owner not in SOURCE_PINS:
            continue  # Unsupported original owner; do not guess its bytes.
        if type(source["path_id"]) is not int or source["path_id"] <= 0:
            raise ValueError("invalid original path ID")
        guid = target["guid"]
        if (type(target["file_id"]) is not int or target["file_id"] <= 0
                or type(target["type"]) is not int or target["type"] not in (2, 3)
                or not isinstance(guid, str) or not GUID.fullmatch(guid)):
            raise ValueError("unsafe exported Texture2D PPtr")
        size, digest = SOURCE_PINS[owner]
        rows.append({
            "source_owner": owner, "source_path_id": source["path_id"],
            "source_bytes": size, "source_sha256": digest,
            "export_asset": None, "export_guid": guid,
        })
        wanted_guids.add(guid)
    if not rows:
        raise ValueError("no pinned Texture2D identities in exporter trace")
    assets = project / "Assets"
    if project.is_symlink() or assets.is_symlink() or not assets.is_dir():
        raise ValueError("unsafe exported Unity project")
    guid_paths = {}
    for meta in assets.rglob("*.meta"):
        rel = meta.relative_to(assets).as_posix()
        regular_child(assets, rel)  # Reject linked meta or ancestor.
        if meta.stat().st_size > MAX_META_BYTES:
            raise ValueError("oversized exported metadata")
        contents = meta.read_text(encoding="utf-8-sig")
        hits = re.findall(r"^guid:\s*([0-9a-f]{32})\s*$", contents, re.MULTILINE)
        if len(hits) != 1:
            if any(g in contents for g in wanted_guids):
                raise ValueError("ambiguous target export metadata GUID")
            continue
        guid = hits[0]
        if guid not in wanted_guids:
            continue
        candidate_rel = rel[:-5]  # Strip .meta only, preserve .png/.asset.
        regular_child(assets, candidate_rel)
        # Only an actual TextureImporter for the exact target GUID qualifies.
        found_guid, _ = read_importer(meta)
        if found_guid != guid or guid in guid_paths:
            raise ValueError("duplicate/wrong TextureImporter GUID mapping")
        guid_paths[guid] = candidate_rel
    if guid_paths.keys() != wanted_guids:
        raise ValueError("missing exact exported TextureImporter GUID target")
    for row in rows:
        row["export_asset"] = guid_paths[row["export_guid"]]
    return {
        "schema_version": 1,
        "source_commit": ZIP2_COMMIT,
        "export_instance": trace["export_instance"],
        "textures": rows,
    }


def validate_export_pair(texture_trace: dict, companion_trace: dict) -> None:
    """Check B02 Texture2D28 and W1 Material21/Shader48 trace session IDs.

    Equal UUIDs are necessary for a joint same-export analysis, but caller
    supplied metadata is NOT independently attested process provenance.
    """
    if (not isinstance(texture_trace, dict) or not isinstance(companion_trace, dict)
            or texture_trace.get("schema_version") != 1
            or companion_trace.get("schema_version") != 1):
        raise ValueError("invalid paired export trace schemas")
    a, b = texture_trace.get("export_instance"), companion_trace.get("export_instance")
    if not isinstance(a, str) or not GUID.fullmatch(a) or a != b:
        raise ValueError("Texture2D and Material/Shader traces from different export instances")
    objects = companion_trace.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("missing W1 companion Material/Shader objects")
    for row in objects:
        if not isinstance(row, dict) or row.get("class_id") not in (21, 48):
            raise ValueError("companion trace contains non-W1 object type")
        source = row.get("source")
        if (not isinstance(source, dict) or set(source) != {"owner", "path_id"}
                or not isinstance(source["owner"], str) or not source["owner"]
                or type(source["path_id"]) is not int or source["path_id"] <= 0):
            raise ValueError("malformed W1 companion source identity")


def read_private_trace(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("missing, linked or oversized private trace")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("private trace must be a JSON object")
    return obj


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original-root", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True)
    inputs = ap.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--sidecar", type=Path)
    inputs.add_argument("--trace", type=Path, help="private SAME-EXPORT object trace; never emitted")
    ap.add_argument("--companion-trace", type=Path, help="optional private W1 Material/Shader trace; requires --trace")
    args = ap.parse_args()
    # Never write repairs or reveal original object names/path IDs in output.
    if args.companion_trace and not args.trace:
        raise ValueError("--companion-trace requires --trace")
    path = args.trace if args.trace else args.sidecar
    witness = read_private_trace(path)
    paired = False
    if args.companion_trace:
        validate_export_pair(witness, read_private_trace(args.companion_trace))
        paired = True
    sidecar = sidecar_from_export_trace(args.project, witness) if args.trace else witness
    report = inspect(args.original_root, args.project, sidecar)
    report["same_export_trace_structurally_consumed"] = bool(args.trace)
    report["companion_export_instance_matched"] = paired
    report["paired_trace_provenance_independently_verified"] = False
    print("RAFT_B15_TEXTURE_SAMPLER_PARITY " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
