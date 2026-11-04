#!/usr/bin/env python3
"""B02: fail-closed original Texture2D -> exported TextureImporter sRGB fidelity.

This is NOT an asset linker. The caller must supply a SAME-EXPORT explicit
identity sidecar; names, colors and hashes never become invented GUID links.
Only aggregate counts are printed. Original source verification is mandatory
for --repair. Nothing in this tool establishes rendered pixels or GPU behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

from scripts.verify_targeted_lfs_compute_sources import EXPECTED as PINNED_SOURCE
\nZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
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


def _parse_importer(data: str) -> tuple[str, int, re.Match[str]]:
    if len(TYPE.findall(data)) != 1 or not re.search(r"^fileFormatVersion:[ \t]*2[ \t]*$", data, re.M):
        raise ValueError("not an unambiguous Unity TextureImporter meta")
    ids, values = GUID.findall(data), list(SRGB.finditer(data))
    raw_srgb = re.findall(r"^\s*sRGBTexture\s*:", data, re.M)
    if len(ids) != 1 or len(values) != 1 or len(raw_srgb) != 1:
        raise ValueError("missing/duplicate GUID or sRGBTexture importer field")
    return ids[0].lower(), int(values[0].group(1)), values[0]


def _source_verified(rows: list[dict], root: Path) -> None:
    # A supplied source directory must contain BYTE-MATCHING owners. The
    # sidecar's claimed source pathIDs/color flags are independently reread.
    import UnityPy

    by_owner: dict[str, list[dict]] = {}
    for row in rows:
        by_owner.setdefault(row["source_owner"], []).append(row)
    for owner, member_rows in by_owner.items():
        path = _safe_child(root, owner)
        size, digest = _sha256(path)
        if any(size != r["source_owner_bytes"] or digest != r["source_owner_sha256"] for r in member_rows):
            raise ValueError("original owner size/SHA256 mismatch")
        env = UnityPy.load(str(path))
        indexed = {}
        needed = {r["source_path_id"] for r in member_rows}
        for obj in env.objects:
            if obj.path_id in needed:
                if obj.path_id in indexed or obj.type.name != "Texture2D":
                    raise ValueError("original source identity is not unique Texture2D")
                indexed[obj.path_id] = obj.read_typetree().get("m_ColorSpace")
        for row in member_rows:
            color = indexed.get(row["source_path_id"])
            if type(color) is not int or color != row["source_color_space"]:
                raise ValueError("source Texture2D color space disagrees with sidecar")


def inspect(project: Path, sidecar: dict, original: Path | None = None, repair: bool = False) -> dict:
    rows = load_map(sidecar)
    if repair and original is None:
        raise ValueError("--repair requires original SHA-verified source")
    if original is not None:
        _source_verified(rows, original)
    assets = project / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("Unity Assets root missing or unsafe")
    edits = []
    same = 0
    for row in rows:
        asset = _safe_child(assets, row["export_asset"])
        meta = _safe_child(assets, row["export_asset"] + ".meta")
        if asset.parent != meta.parent:
            raise ValueError("unexpected importer parent")
        content = meta.read_text(encoding="utf-8-sig")
        guid, actual, span = _parse_importer(content)
        if guid != row["export_guid"]:
            raise ValueError("sidecar export GUID does not match importer")
        expected = 1 if row["source_color_space"] == 0 else 0
        if actual == expected:
            same += 1
        else:
            replacement = content[:span.start(1)] + str(expected) + content[span.end(1):]
            edits.append((meta, content, replacement))
    changed = 0
    if repair:
        staged = []
        try:
            for meta, old, new in edits:
                fd, name = tempfile.mkstemp(prefix=".b02-srgb-", dir=meta.parent)
                tmp = Path(name)
                os.fchmod(fd, meta.stat().st_mode & 0o777)
                with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                    stream.write(new)
                staged.append((meta, tmp, old))
            for meta, tmp, old in staged:
                os.replace(tmp, meta)
                changed += 1
        except BaseException:
            # Fail closed: restore exact original contents for prior replacements.
            for meta, tmp, old in staged[:changed]:
                meta.write_text(old, encoding="utf-8", newline="")
            raise
        finally:
            for _, tmp, _ in staged:
                tmp.unlink(missing_ok=True)
    return {
        "schema_version": 1,
        "rows": len(rows),
        "matching_before": same,
        "mismatched_before": len(edits),
        "repaired": changed,
        "source_bytes_and_colorspace_verified": original is not None,
        "same_export_linkage_independently_verified": False,
        "unity_compile_or_gpu_verified": False,
        "android_device_verified": False,
        "no_raw_source_or_guid_in_output": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--map", type=Path, required=True, help="Explicit same-export identity sidecar (never guessed from names)")
    ap.add_argument("--original", type=Path, help="SHA-authenticated original data root, mandatory for --repair")
    ap.add_argument("--repair", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    report = inspect(args.project, json.loads(args.map.read_text(encoding="utf-8")), args.original, args.repair)
    print("RAFT_B02_TEXTURE_IMPORT_FIDELITY " + json.dumps(report, sort_keys=True))
    if args.strict and report["mismatched_before"] and not args.repair:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
