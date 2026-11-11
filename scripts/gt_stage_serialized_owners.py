#!/usr/bin/env python3
"""GT: reconstruct only 82 ZIP2 serialized Unity owners, preserving source bytes.

No .resS streams, banks, original game bytes or credentials are published.
Verification occurs against the manifest in the immutable ZIP2 checkout.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil

from scripts.gt_scene_graphics_inventory import MANIFEST_COLUMNS, SOURCE_COMMIT, InventoryError

PART = re.compile(r"part-(\d{5})\Z")
OWNERS = (tuple(f"level{i}" for i in range(40)) +
          tuple(f"sharedassets{i}.assets" for i in range(40)) +
          ("globalgamemanagers.assets", "resources.assets"))


def read_expected(manifest: Path) -> dict[str, tuple]:
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 1_000_000:
        raise InventoryError("unsafe_manifest")
    out = {}
    with manifest.open(encoding="utf-8-sig", newline="") as f:
        table = csv.DictReader(f, delimiter="\t")
        if table.fieldnames != MANIFEST_COLUMNS:
            raise InventoryError("manifest_schema_changed")
        for row in table:
            if None in row or any(v is None for v in row.values()):
                raise InventoryError("malformed_manifest")
            path = row["relative_path_under_Raft"]
            if ("\\" in path or path.startswith("/") or
                    any(x in ("", ".", "..") for x in path.split("/"))):
                raise InventoryError("unsafe_manifest_path")
            parts = PurePosixPath(path).parts
            if len(parts) != 2 or parts[0] != "Raft_Data" or parts[1] not in OWNERS:
                continue
            name = parts[1]
            if name in out:
                raise InventoryError("duplicate_manifest_owner")
            sz = int(row["bytes"])
            sha = row["sha256"]
            kind = row["kind"]
            if kind not in ("plain", "split") or sz <= 0 or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise InventoryError("invalid_owner_manifest_record")
            out[name] = (kind, sz, sha)
    if set(out) != set(OWNERS):
        raise InventoryError("manifest_missing_serialized_owners")
    return out


def parts_for(source: Path, kind: str):
    if source.is_symlink():
        raise InventoryError("symlink_owner_source")
    if kind == "plain":
        if not source.is_file() or source.stat().st_nlink != 1:
            raise InventoryError("unsafe_plain_owner")
        return [source]
    if not source.is_dir():
        raise InventoryError("missing_split_owner")
    entries = list(source.iterdir())
    parts = sorted((p for p in entries if PART.fullmatch(p.name)),
                   key=lambda p: p.name)
    if (not parts or [p.name for p in parts] !=
            [f"part-{i:05d}" for i in range(len(parts))] or
            any(p.is_symlink() or not p.is_file() or p.stat().st_nlink != 1 for p in parts)
            or any(p.name != "README.txt" or p.is_symlink() for p in entries if p not in parts)):
        raise InventoryError("unsafe_split_parts")
    return parts


def stage(source: Path, manifest: Path, dest: Path, selected=None) -> dict:
    if any(p.is_symlink() for p in (source, *source.parents)):
        raise InventoryError("unsafe_source")
    if not source.is_dir():
        raise InventoryError("missing_source")
    if dest.resolve() == source.resolve() or dest.resolve().is_relative_to(source.resolve()):
        raise InventoryError("destination_inside_original_source")
    expected = read_expected(manifest)
    names = sorted(selected if selected is not None else OWNERS)
    if not names or len(names) != len(set(names)) or not set(names) <= set(OWNERS):
        raise InventoryError("invalid_owner_selection")
    dest.mkdir(parents=True, exist_ok=True)
    result = {}
    for name in names:
        kind, size, sha = expected[name]
        chunks = parts_for(source / name, kind)
        target = dest / name
        if target.exists() or target.is_symlink():
            raise InventoryError("destination_collision")
        tmp = dest / (name + ".part-gt")
        if tmp.exists() or tmp.is_symlink():
            raise InventoryError("stale_temporary_output")
        h = hashlib.sha256()
        length = 0
        try:
            with tmp.open("xb") as out:
                for chunkfile in chunks:
                    with chunkfile.open("rb") as inp:
                        for block in iter(lambda: inp.read(1024 * 1024), b""):
                            length += len(block)
                            if length > size:
                                raise InventoryError("manifest_size_exceeded")
                            h.update(block)
                            out.write(block)
            if length != size or h.hexdigest() != sha:
                raise InventoryError("manifest_original_sha256_mismatch")
            tmp.replace(target)
            result[name] = {"sha256_verified": True, "source_bytes": size,
                            "kind": kind}
        finally:
            if tmp.exists():
                tmp.unlink()
    return {"source_commit": SOURCE_COMMIT, "selected_owners": len(names),
            "all_82_serialized_owners": len(names) == len(OWNERS),
            "verified_bytes": sum(row["source_bytes"] for row in result.values()),
            "items": result, "game_device_verified": False}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--destination", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.report.resolve().is_relative_to(args.source.resolve()):
        raise InventoryError("report_inside_original_source")
    result = stage(args.source, args.manifest, args.destination)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("GT_SERIALIZED_OWNERS " + json.dumps({
        "authenticated": result["selected_owners"], "bytes": result["verified_bytes"],
        "all_82": result["all_82_serialized_owners"], "device": False
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
