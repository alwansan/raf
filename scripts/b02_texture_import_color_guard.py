#!/usr/bin/env python3
"""B02: READ-ONLY source/export sRGB audit with unresolved color semantics.

This is NOT an asset linker. The caller must supply a SAME-EXPORT explicit
identity sidecar; names, colors and hashes never become invented GUID links.
Only aggregate counts are printed. Repair is DISABLED until trustworthy same-export
linkage and correct semantics are established. This is not GPU/pixel evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from scripts.verify_targeted_lfs_compute_sources import EXPECTED as PINNED_SOURCE

ZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
GUID = re.compile(r"^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*$", re.M)
SRGB = re.compile(r"^  sRGBTexture:[ \t]*([01])[ \t]*$", re.M)
TYPE = re.compile(r"^TextureImporter:[ \t]*$", re.M)


def _safe_child(root: Path, raw: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw:
        raise ValueError("unsafe relative source/export path")
    rel = PurePosixPath(raw)
    if rel.is_absolute() or any(p in ("", ".", "..") for p in raw.split("/")):
        raise ValueError("unsafe relative source/export path")
    base = root.resolve(strict=True)
    target = root.joinpath(*rel.parts)
    cursor = root
    if root.is_symlink():
        raise ValueError("symlinked root")
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink in source/export path")
    resolved = target.resolve(strict=True)
    if not resolved.is_relative_to(base) or not resolved.is_file():
        raise ValueError("source/export path escapes root or is not file")
    return resolved


def _sha256(path: Path) -> tuple[int, str]:
    size = 0
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda: stream.read(1 << 20), b""):
            size += len(piece)
            digest.update(piece)
    return size, digest.hexdigest()


def load_map(payload: dict) -> list[dict]:
    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or payload.get("source_commit") != ZIP2_SHA:
        raise ValueError("sidecar source commit/schema missing or wrong")
    rows = payload.get("textures")
    if not isinstance(rows, list) or not rows:
        raise ValueError("explicit same-export texture map is required")
    original, exported, guids = set(), set(), set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "source_owner", "source_owner_bytes", "source_owner_sha256",
            "source_path_id", "source_color_space", "export_asset", "export_guid"
        }:
            raise ValueError("incomplete/ambiguous texture identity record")
        if not isinstance(row["source_path_id"], int) or isinstance(row["source_path_id"], bool):
            raise ValueError("source path ID must be integer")
        if row["source_color_space"] not in (0, 1) or isinstance(row["source_color_space"], bool):
            raise ValueError("invalid original texture colorspace enum")
        if not isinstance(row["source_owner_bytes"], int) or isinstance(row["source_owner_bytes"], bool) or row["source_owner_bytes"] <= 0:
            raise ValueError("invalid original owner byte count")
        if not isinstance(row["source_owner_sha256"], str) or not HEX64.fullmatch(row["source_owner_sha256"]):
            raise ValueError("invalid original SHA256")
        expected_pin = PINNED_SOURCE.get(row["source_owner"])
        if expected_pin != (row["source_owner_bytes"], row["source_owner_sha256"]):
            raise ValueError("source owner is not in the original SHA/size trusted pinset")
        if not isinstance(row["export_guid"], str) or not HEX32.fullmatch(row["export_guid"]):
            raise ValueError("invalid exported GUID")
        for key in ("source_owner", "export_asset"):
            if not isinstance(row[key], str) or not row[key] or row[key].startswith("/") or "\\" in row[key] or ":" in row[key] or any(x in (".", "..", "") for x in row[key].split("/")):
                raise ValueError("unsafe sidecar path")
        identity = (row["source_owner"], row["source_path_id"])
        if identity in original or row["export_asset"] in exported or row["export_guid"] in guids:
            raise ValueError("duplicate/ambiguous texture mapping")
        original.add(identity)
        exported.add(row["export_asset"])
        guids.add(row["export_guid"])
    return rows


def _parse_importer(data: str) -> tuple[str, int]:
    """Read exactly the nested importer field emitted by pinned AssetRipper.

    ImporterFactory.GenerateTextureImporter writes instance.MipMaps.SRGBTexture,
    not a TextureImporter-level scalar.  Duplicate YAML keys must not silently
    select an attacker-controlled value.  No meta data is ever rewritten.
    """
    import yaml

    if len(data.encode("utf-8")) > 256_000:
        raise ValueError("oversized TextureImporter metadata")

    class UniqueLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            result = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, (str, int)) or key in result:
                    raise ValueError("duplicate/unhashable TextureImporter YAML key")
                result[key] = self.construct_object(value_node, deep=deep)
            return result

    parsed = yaml.load(data, Loader=UniqueLoader)
    if not isinstance(parsed, dict) or type(parsed.get("fileFormatVersion")) is not int or parsed["fileFormatVersion"] != 2:
        raise ValueError("not a unique Unity TextureImporter meta")
    guid = parsed.get("guid")
    importer = parsed.get("TextureImporter")
    if not isinstance(guid, str) or not HEX32.fullmatch(guid.lower()) or not isinstance(importer, dict):
        raise ValueError("missing/invalid TextureImporter GUID")
    if "sRGBTexture" in importer:
        raise ValueError("ambiguous legacy top-level sRGBTexture; expected mipmaps")
    mipmaps = importer.get("mipmaps")
    if not isinstance(mipmaps, dict):
        raise ValueError("missing TextureImporter.mipmaps")
    value = mipmaps.get("sRGBTexture")
    if type(value) is not int or value not in (0, 1):
        raise ValueError("missing/invalid TextureImporter.mipmaps.sRGBTexture")
    return guid.lower(), value


def _authenticated_original_colors(rows: list[dict], root: Path) -> dict[tuple[str, int], int]:
    """Authenticate exact original owner bytes and independently read typed colors.

    Caller-provided color enum never overrides the original serialized value.
    """
    import UnityPy

    by_owner = {}
    for row in rows:
        by_owner.setdefault(row["source_owner"], []).append(row)
    colors = {}
    for owner, member_rows in by_owner.items():
        if owner not in PINNED_SOURCE:
            raise ValueError("original owner outside trusted pinset")
        path = _safe_child(root, owner)
        size, digest = _sha256(path)
        if (size, digest) != PINNED_SOURCE[owner]:
            raise ValueError("original owner byte count/SHA256 mismatch")
        needed = {r["source_path_id"] for r in member_rows}
        for obj in UnityPy.load(str(path)).objects:
            if obj.path_id not in needed:
                continue
            key = (owner, obj.path_id)
            if key in colors or obj.type.name != "Texture2D":
                raise ValueError("source object not a unique Texture2D")
            color = obj.read_typetree().get("m_ColorSpace")
            if type(color) is not int or color not in (0, 1):
                raise ValueError("invalid original Texture2D color-space enum")
            colors[key] = color
        if any((owner, r["source_path_id"]) not in colors for r in member_rows):
            raise ValueError("missing original Texture2D pathID")
    return colors


def _source_verified(rows: list[dict], root: Path) -> None:
    colors = _authenticated_original_colors(rows, root)
    for row in rows:
        if colors[row["source_owner"], row["source_path_id"]] != row["source_color_space"]:
            raise ValueError("source Texture2D color space disagrees with sidecar")


def map_from_export_trace(project: Path, original_root: Path, trace: dict) -> dict:
    """Reuse the exact B15 exporter-trace GUID bridge, never a filename guess.

    Crucially colors are reread from SHA-verified original owners; unlike an
    authored B02 map the trace cannot supply original color flags itself.
    """
    from scripts import b15_texture_sampler_parity as b15

    if not isinstance(trace, dict) or not isinstance(trace.get("objects"), list):
        raise ValueError("invalid exporter trace")
    for item in trace["objects"]:
        if not isinstance(item, dict) or item.get("class_id") != 28:
            continue
        source = item.get("source")
        if not isinstance(source, dict) or not isinstance(source.get("owner"), str):
            raise ValueError("invalid trace source owner")
        name = PurePosixPath(source["owner"]).name
        if name in PINNED_SOURCE and source["owner"] not in (
            name, "Raft_Data/" + name, "Raft/Raft_Data/" + name
        ):
            raise ValueError("untrusted trace source collection path")
    bridge = b15.sidecar_from_export_trace(project, trace)
    rows = b15.check_rows(bridge)
    colors = _authenticated_original_colors(rows, original_root)
    result = {
        "schema_version": 1,
        "source_commit": ZIP2_SHA,
        "textures": [{
            "source_owner": row["source_owner"],
            "source_owner_bytes": row["source_bytes"],
            "source_owner_sha256": row["source_sha256"],
            "source_path_id": row["source_path_id"],
            "source_color_space": colors[row["source_owner"], row["source_path_id"]],
            "export_asset": row["export_asset"],
            "export_guid": row["export_guid"],
        } for row in rows],
    }
    load_map(result)  # Ensure B02's own identity and trusted pin contract.
    return result


def inspect(project: Path, sidecar: dict, original: Path | None = None, repair: bool = False) -> dict:
    # DO NOT WRITE: Pinned AssetRipper ImporterFactory has
    # SRGBTexture = (Texture2D.ColorSpace_C28E == ColorSpace.Linear),
    # which conflicts with naïve Unity Gamma->sRGB assumptions.
    # The serialized m_ColorSpace's meaning in the original game's full
    # rendering context and same-export mapping have not been proven.
    if repair:
        raise ValueError("--repair disabled: unproven original/export linkage and color-space semantics")
    rows = load_map(sidecar)
    if original is not None:
        _source_verified(rows, original)
    assets = project / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("Unity Assets root missing or unsafe")
    upstream_matches = gamma_hypothesis_matches = 0
    for row in rows:
        _safe_child(assets, row["export_asset"])
        meta = _safe_child(assets, row["export_asset"] + ".meta")
        content = meta.read_text(encoding="utf-8-sig")
        guid, actual = _parse_importer(content)
        if guid != row["export_guid"]:
            raise ValueError("sidecar export GUID does not match importer")
        # Original AssetRipper branch 036098ab (ImporterFactory.cs):
        # original m_ColorSpace = Linear(1) => sRGBTexture true.
        upstream = int(row["source_color_space"] == 1)
        # Alternative Unity GAMMA-data interpretation remains a hypothesis
        # rather than a verified interpretation of original serialized bits.
        gamma_hypothesis = 1 - upstream
        upstream_matches += int(actual == upstream)
        gamma_hypothesis_matches += int(actual == gamma_hypothesis)
    return {
        "schema_version": 2,
        "rows": len(rows),
        "assetripper_pinned_policy_matches": upstream_matches,
        "assetripper_pinned_policy_mismatches": len(rows) - upstream_matches,
        "gamma_semantic_hypothesis_matches": gamma_hypothesis_matches,
        "gamma_semantic_hypothesis_mismatches": len(rows) - gamma_hypothesis_matches,
        "semantic_policy_verified_for_original": False,
        "same_export_linkage_independently_verified": False,
        "source_bytes_and_colorspace_verified": original is not None,
        "repair_available": False,
        "repaired": 0,
        "unity_compile_or_gpu_verified": False,
        "android_device_verified": False,
        "no_raw_source_or_guid_in_output": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", type=Path, required=True)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--map", type=Path, help="private explicit same-export sidecar")
    source.add_argument("--trace", type=Path, help="B15-compatible same-export object trace")
    ap.add_argument("--original", type=Path, help="SHA-authenticated original owner directory; required for --trace")
    ap.add_argument("--repair", action="store_true", help="DISABLED: semantics and provenance unproven")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    if args.repair:
        raise ValueError("--repair disabled: original/export semantics unproven")
    if args.trace and args.original is None:
        raise ValueError("--trace needs SHA-authenticated --original bytes")
    witness = args.trace if args.trace else args.map
    if witness.is_symlink() or not witness.is_file() or witness.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("unsafe/oversized private exporter witness")
    payload = json.loads(witness.read_text(encoding="utf-8"))
    sidecar = (map_from_export_trace(args.project, args.original, payload)
               if args.trace else payload)
    report = inspect(args.project, sidecar, args.original)
    report["same_export_trace_structurally_consumed"] = bool(args.trace)
    print("RAFT_B02_TEXTURE_IMPORT_FIDELITY " + json.dumps(report, sort_keys=True))
    # A caller-supplied trace is not independent proof of export provenance.
    # Until an actual original/export/pixel witness is validated, strict fails.
    if args.strict and not (report["source_bytes_and_colorspace_verified"] and
                            report["same_export_linkage_independently_verified"] and
                            report["semantic_policy_verified_for_original"] and
                            report["assetripper_pinned_policy_mismatches"] == 0):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
