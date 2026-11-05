#!/usr/bin/env python3
"""Extract only the exact paired APK and OBB from a SHA-pinned GitHub delivery ZIP.

The archived transport parts were previously verified in CI42110297871.
This verifier separately checks the original full archive SHA/byte size and
streams each selected APK/OBB part into no-clobber private staging. It never
extracts or publishes XAPK, Unity assets, or proprietary source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

PACKAGE = "com.alwansan.raft.androidtest"
APK = "Raft-Android-Test.apk"
XAPK = "Raft-Android-Test.xapk"
SAFE = re.compile(r"[A-Za-z0-9_.-]+\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
BUF = 4 * 1024 * 1024


def sha_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(BUF), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _positive(value) -> bool:
    return type(value) is int and value > 0


def _hash(value) -> bool:
    return type(value) is str and HEX.fullmatch(value) is not None


def _safe_name(value) -> bool:
    return type(value) is str and SAFE.fullmatch(value) is not None and value not in (".", "..")


def extract_pair(source_zip: Path, target_dir: Path, *, expected_bytes: int,
                 expected_sha: str, expected_version: str) -> dict:
    if (source_zip.is_symlink() or not source_zip.is_file()
            or not _positive(expected_bytes) or source_zip.stat().st_size != expected_bytes):
        raise ValueError("Original immutable ZIP source file size/path mismatch")
    if not _hash(expected_sha) or sha_path(source_zip) != expected_sha:
        raise ValueError("Original immutable ZIP SHA256 mismatch")
    if not re.fullmatch(r"[1-9][0-9]*", expected_version):
        raise ValueError("Expected versionCode invalid")
    if target_dir.exists() or target_dir.is_symlink():
        raise ValueError("Refusing to overwrite existing extraction directory")
    obb_name = "main." + expected_version + "." + PACKAGE + ".obb"
    selected = (APK, obb_name)
    with zipfile.ZipFile(source_zip, "r") as archive:
        entries = archive.infolist()
        if not 5 <= len(entries) <= 32 or len({i.filename for i in entries}) != len(entries):
            raise ValueError("Delivery archive member count or duplicate names")
        if any(not _safe_name(i.filename) or i.is_dir() for i in entries):
            raise ValueError("Delivery ZIP paths unsafe")
        indexed = {i.filename: i for i in entries}
        manifest = indexed.get("delivery.json")
        if manifest is None or not 0 < manifest.file_size < 100_000:
            raise ValueError("Delivery metadata missing or too large")
        metadata_bytes = archive.read("delivery.json")
        metadata = json.loads(metadata_bytes.decode("utf8"))
        if (type(metadata) is not dict or metadata.get("schema") != 1
                or metadata.get("package") != PACKAGE
                or metadata.get("version_code") != expected_version
                or metadata.get("companion_required") is not True
                or metadata.get("transport_only_parts") is not True
                or metadata.get("device_install_verified") is not False):
            raise ValueError("Authentic ZIP delivery identity mismatch")
        records = metadata.get("files")
        if type(records) is not list or len(records) != 3:
            raise ValueError("Expected APK, OBB and XAPK logical records")
        plans = []
        expected_logical_names = (APK, obb_name, XAPK)
        for row, name in zip(records, expected_logical_names):
            if (type(row) is not dict or row.get("name") != name
                    or not _positive(row.get("bytes")) or not _hash(row.get("sha256"))):
                raise ValueError("Logical output name or SHA/size invalid")
            parts = row.get("parts")
            if type(parts) is not list or not 1 <= len(parts) <= 16:
                raise ValueError("Transport list invalid")
            part_total = 0
            for n, part in enumerate(parts, 1):
                expected_name = name if len(parts) == 1 else name + ".part" + str(n).zfill(3)
                if (type(part) is not dict or part.get("name") != expected_name
                        or not _safe_name(expected_name)
                        or not _positive(part.get("bytes")) or not _hash(part.get("sha256"))):
                    raise ValueError("Transport part identity or digest invalid")
                actual_entry = indexed.get(expected_name)
                if actual_entry is None or actual_entry.file_size != part["bytes"]:
                    raise ValueError("Missing actual signed transport part or wrong size")
                part_total += part["bytes"]
            if part_total != row["bytes"]:
                raise ValueError("Part counts do not add to logical whole")
            if name in selected:
                plans.append(row)
        total = sum(row["bytes"] for row in plans)
        if shutil.disk_usage(target_dir.parent).free < total + 256 * 1024 * 1024:
            raise ValueError("Insufficient disk for selected exact native APK and OBB")
        # Exclusive destination created only after source, ZIP inventory, identity
        # and both selected source sizes pass preflight.
        target_dir.mkdir()
        staged = []
        try:
            (target_dir / "delivery.json").write_bytes(metadata_bytes)
            for row in plans:
                staging = target_dir / (row["name"] + ".staging")
                digest = hashlib.sha256()
                written = 0
                with staging.open("xb") as output:
                    for part in row["parts"]:
                        actual = hashlib.sha256()
                        count = 0
                        # zipfile stream checks ZIP member CRC on complete EOF read
                        with archive.open(indexed[part["name"]]) as source:
                            for block in iter(lambda: source.read(BUF), b""):
                                output.write(block)
                                actual.update(block)
                                digest.update(block)
                                written += len(block)
                                count += len(block)
                        if count != part["bytes"] or actual.hexdigest() != part["sha256"]:
                            raise ValueError("Actual native transport part SHA/size mismatch")
                if written != row["bytes"] or digest.hexdigest() != row["sha256"]:
                    raise ValueError("Actual complete native file SHA/size mismatch")
                staged.append((staging, target_dir / row["name"]))
            # No-clobber local publication on GitHub Ubuntu ext4. If a competing
            # target appears, fail rather than overwrite a separately signed file.
            for temporary, final in staged:
                os.link(temporary, final)
                temporary.unlink()
        except BaseException:
            # The extraction directory was exclusively created by this function.
            # Leave no partial game payload on ordinary exceptions.
            if target_dir.is_dir() and not target_dir.is_symlink():
                shutil.rmtree(target_dir)
            raise
    return {
        "source_zip_sha256_pinned": True,
        "delivery_manifest_bound_to_source_zip": True,
        "signed_pair_files_materialized": len(plans),
        "signed_apk_and_obb_sha256_verified": True,
        "source_version_code": expected_version,
        "pair_total_bytes": total,
        "apk_signature_verified": False,
        "obb_guid_validated": False,
        "device_install_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-archive-bytes", required=True, type=int)
    parser.add_argument("--expected-archive-sha", required=True)
    parser.add_argument("--version-code", required=True)
    args = parser.parse_args()
    print("T5_ACTUAL_PAIR_EXTRACT " + json.dumps(extract_pair(
        args.source_zip, args.output, expected_bytes=args.expected_archive_bytes,
        expected_sha=args.expected_archive_sha, expected_version=args.version_code),
        sort_keys=True))


if __name__ == "__main__":
    main()
