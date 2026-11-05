#!/usr/bin/env python3
"""Offline source-only companion checker for completed native Raft APK and OBB.

Hashes actual files against local delivery.json and runs APK aapt identity probe.
Does not authenticate manifest, APK signature, Unity OBB internal GUID, device mount.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import zipfile

PACKAGE = "com.alwansan.raft.androidtest"
APK_NAME = "Raft-Android-Test.apk"
XAPK_NAME = "Raft-Android-Test.xapk"
HEX = re.compile(r"[0-9a-f]{64}\Z")
BADGING = re.compile(r"^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']*)'", re.M)
BUFFER = 1024 * 1024


def _valid_file(path: Path, limit: int | None = None) -> None:
    if not path.is_file() or path.is_symlink() or path.stat().st_size <= 0:
        raise ValueError("Missing, empty, or linked input file: " + path.name)
    if limit is not None and path.stat().st_size > limit:
        raise ValueError("Input exceeds metadata size bound: " + path.name)


def _sha(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(BUFFER), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def _row(obj, what: str) -> dict:
    if type(obj) is not dict:
        raise ValueError("Invalid " + what)
    return obj


def _integer(obj) -> bool:
    return type(obj) is int and obj > 0


def _digest(obj) -> bool:
    return type(obj) is str and HEX.fullmatch(obj) is not None


def _safe_zip_name(name: str) -> bool:
    if not name or name.startswith("/") or "\\" in name or ":" in name:
        return False
    return all(part not in (".", "..", "") for part in PurePosixPath(name).parts)


def _zip_structure(path: Path, apk: bool) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if not entries or len(entries) > 200_000:
                raise ValueError("Empty or excessive ZIP member list")
            names = set()
            has_asset = False
            for info in entries:
                if not _safe_zip_name(info.filename) or info.filename in names:
                    raise ValueError("Unsafe or duplicate ZIP member")
                names.add(info.filename)
                if not info.is_dir() and info.file_size > 0:
                    has_asset |= info.filename.startswith(
                        "assets/bin/Data/" if apk else "assets/")
            if not has_asset:
                raise ValueError("No populated Unity APK/OBB asset entry")
            if apk:
                required = ("AndroidManifest.xml", "classes.dex",
                            "lib/arm64-v8a/libil2cpp.so", "lib/arm64-v8a/libunity.so")
                if not set(required) <= names:
                    raise ValueError("APK has no complete ARM64 IL2CPP core")
                for name in required:
                    with archive.open(name) as stream:
                        head = stream.read(64)
                    if not head:
                        raise ValueError("Empty APK core member")
                    if name == "classes.dex" and not head.startswith(b"dex\n"):
                        raise ValueError("APK DEX header missing")
                    if name.endswith(".so"):
                        if len(head) < 64 or head[:7] != b"\x7fELF\x02\x01\x01":
                            raise ValueError("APK native library not ELF64 little-endian")
                        kind, arch, version = struct.unpack_from("<HHI", head, 16)
                        hsize = struct.unpack_from("<H", head, 52)[0]
                        if (kind, arch, version, hsize) != (3, 183, 1, 64):
                            raise ValueError("APK native library not AArch64 shared object")
            return len(entries)
    except (zipfile.BadZipFile, EOFError) as exc:
        raise ValueError("Native APK/OBB ZIP structure invalid") from exc


def verify_pair(delivery: Path, apk: Path, obb: Path, badging: str) -> dict:
    """Verify actual complete files, not transport .part files."""
    _valid_file(delivery, 100_000)
    _valid_file(apk)
    _valid_file(obb)
    if delivery.name != "delivery.json" or apk.name != APK_NAME:
        raise ValueError("Input filename disagrees with native delivery convention")
    data = _row(json.loads(delivery.read_text(encoding="utf8")), "delivery JSON")
    code = data.get("version_code")
    if (data.get("schema") != 1 or data.get("package") != PACKAGE
            or type(code) is not str or not re.fullmatch(r"[1-9][0-9]*", code)
            or data.get("companion_required") is not True
            or data.get("transport_only_parts") is not True):
        raise ValueError("Delivery package/version contract invalid")
    obb_name = "main." + code + "." + PACKAGE + ".obb"
    if obb.name != obb_name:
        raise ValueError("OBB filename/version/package disagree with delivery")
    files = data.get("files")
    if type(files) is not list or len(files) != 3:
        raise ValueError("Expected exactly APK, OBB and XAPK logical records")
    lookup = {}
    for entry in files:
        entry = _row(entry, "logical file")
        name = entry.get("name")
        if type(name) is not str or name in lookup:
            raise ValueError("Missing or repeated logical output name")
        if not _integer(entry.get("bytes")) or not _digest(entry.get("sha256")):
            raise ValueError("Invalid logical file size/digest")
        parts = entry.get("parts")
        if type(parts) is not list or not 1 <= len(parts) <= 200:
            raise ValueError("Invalid transport part count")
        part_total = 0
        for index, part in enumerate(parts, 1):
            part = _row(part, "transport part")
            expected_name = name if len(parts) == 1 else name + ".part" + str(index).zfill(3)
            if (part.get("name") != expected_name or not _integer(part.get("bytes"))
                    or not _digest(part.get("sha256"))):
                raise ValueError("Invalid transport part metadata")
            part_total += part["bytes"]
        if part_total != entry["bytes"]:
            raise ValueError("Transport sizes do not add to whole file")
        if len(parts) == 1 and parts[0]["sha256"] != entry["sha256"]:
            raise ValueError("Single part disagrees with whole digest")
        lookup[name] = entry
    if set(lookup) != {APK_NAME, obb_name, XAPK_NAME}:
        raise ValueError("Incorrect APK/OBB/XAPK logical output names")
    match = BADGING.search(badging)
    if match is None or match[1] != PACKAGE or match[2] != code:
        raise ValueError("Actual aapt APK identity differs from delivery and OBB")
    for path in (apk, obb):
        size, digest = _sha(path)
        expected = lookup[path.name]
        if (size, digest) != (expected["bytes"], expected["sha256"]):
            raise ValueError("Completed " + ("APK" if path == apk else "OBB")
                             + " size/SHA256 differs from delivery manifest")
    apk_members = _zip_structure(apk, apk=True)
    obb_members = _zip_structure(obb, apk=False)
    return {
        "package_name": PACKAGE,
        "version_code": code,
        "completed_apk_and_obb_sha256_match_local_delivery_manifest": True,
        "aapt_apk_package_version_match": True,
        "obb_filename_package_version_match": True,
        "apk_zip_members": apk_members,
        "obb_zip_members": obb_members,
        "xapk_actual_bytes_checked": False,
        "delivery_manifest_authenticated": False,
        "apk_crypto_signature_checked": False,
        "unity_obb_internal_guid_checked": False,
        "android_device_obb_mount_verified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--delivery", required=True, type=Path)
    p.add_argument("--apk", required=True, type=Path)
    p.add_argument("--obb", required=True, type=Path)
    p.add_argument("--aapt", default="aapt")
    opts = p.parse_args()
    try:
        result = subprocess.run([opts.aapt, "dump", "badging", str(opts.apk)],
                                check=True, capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        raise SystemExit("Cannot obtain APK badging: " + str(exc))
    print("T5_APK_OBB_PAIR " + json.dumps(
        verify_pair(opts.delivery, opts.apk, opts.obb, result.stdout), sort_keys=True))


if __name__ == "__main__":
    main()
