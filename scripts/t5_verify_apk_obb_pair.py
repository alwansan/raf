#!/usr/bin/env python3
"""Offline source-only companion checker for completed native Raft APK and OBB.

Hashes actual files against local delivery.json and runs APK aapt identity probe.
Does not authenticate manifest, APK signature, Unity OBB internal GUID, device mount.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
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


def _unique_json_pairs(pairs):
    """Reject duplicate keys at every level of an unauthenticated delivery manifest."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate delivery JSON key")
        result[key] = value
    return result


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
    # PurePosixPath collapses repeated separators and dot segments: inspect raw ZIP names.
    segments = (name[:-1] if name.endswith("/") else name).split("/")
    return all(segment not in ("", ".", "..") for segment in segments)



def _verify_local_zip_headers(archive: zipfile.ZipFile, entries: list[zipfile.ZipInfo]) -> None:
    """Check every ZIP local header without decompressing multi-GB APK/OBB assets.

    The central directory alone may look valid even if non-core members cannot
    be opened. Compare local names/flags/methods and enforce compressed-data
    bounds and non-overlap. ZIP64 sizes and data descriptors use central sizes.
    """
    stream = archive.fp
    if stream is None:
        raise ValueError("ZIP local member header unavailable")
    regions = []
    for member in entries:
        offset = member.header_offset
        if offset < 0 or offset + 30 > archive.start_dir:
            raise ValueError("ZIP local member header offset invalid")
        stream.seek(offset)
        raw = stream.read(30)
        if len(raw) != 30:
            raise ValueError("ZIP local member header truncated")
        signature, _version, flags, method, _time, _date, crc, compressed, size, name_len, extra_len = (
            struct.unpack("<IHHHHHIIIHH", raw))
        if (signature != 0x04034B50 or flags != member.flag_bits
                or method != member.compress_type):
            raise ValueError("ZIP local member header disagrees with central directory")
        # Ordinary Unity/APK paths do not require enormous local filenames. The
        # cap also bounds per-member metadata reads from untrusted ZIP input.
        if name_len > 4096:
            raise ValueError("ZIP local member header name exceeds safety bound")
        try:
            name = member.filename.encode("utf-8" if flags & 0x800 else "cp437")
        except UnicodeEncodeError as exc:
            raise ValueError("ZIP local member header encoding invalid") from exc
        if name_len != len(name) or stream.read(name_len) != name:
            raise ValueError("ZIP local member header name disagrees with central directory")
        if not flags & 0x8:
            # When a data descriptor is used, local CRC/sizes may be zero.
            # Without it, local and central values must agree; 0xffffffff is
            # the legitimate ZIP64 placeholder for sizes.
            if (crc != member.CRC or
                    (compressed != 0xFFFFFFFF and compressed != member.compress_size) or
                    (size != 0xFFFFFFFF and size != member.file_size)):
                raise ValueError("ZIP local member header CRC/size disagrees with central directory")
        data_start = offset + 30 + name_len + extra_len
        data_end = data_start + member.compress_size
        if data_start > archive.start_dir or data_end > archive.start_dir:
            raise ValueError("ZIP compressed member region exceeds local payload bounds")
        regions.append((offset, data_end))
    regions.sort()
    for (_, end), (next_offset, _) in zip(regions, regions[1:]):
        if end > next_offset:
            raise ValueError("ZIP compressed member regions overlap")


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
                # ZIP external attributes can mark a member as a Unix symlink even
                # when its name looks safe. Never accept such a delivery payload.
                unix_mode = (info.external_attr >> 16) & 0xffff
                if info.create_system == 3 and (unix_mode & 0o170000) == 0o120000:
                    raise ValueError("ZIP member is a symbolic link")
                if info.flag_bits & 0x1:
                    raise ValueError("Encrypted ZIP member is not a usable Unity asset")
                # Python can parse BZIP2/LZMA ZIP entries, but Android APK/OBB
                # asset readers must not be assumed to support these methods.
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise ValueError("Unsupported APK/OBB ZIP compression method")
                if not info.is_dir() and info.file_size > 0:
                    has_asset |= info.filename.startswith(
                        "assets/bin/Data/" if apk else "assets/")
            # Distinct ZIP names can still collide when a regular file is
            # also used as the parent directory of another member.
            regular_files = {info.filename for info in entries if not info.is_dir()}
            for name in names:
                segments = name.rstrip("/").split("/")
                for depth in range(1, len(segments)):
                    if "/".join(segments[:depth]) in regular_files:
                        raise ValueError("ZIP regular file collides with member directory")
            _verify_local_zip_headers(archive, entries)
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
    data = _row(json.loads(delivery.read_text(encoding="utf8"), object_pairs_hook=_unique_json_pairs), "delivery JSON")
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
    # An ambiguous or repeated aapt package declaration cannot attest a single APK.
    # Reject even duplicate identical lines rather than accepting the first match.
    matches = BADGING.findall(badging)
    if len(matches) != 1 or matches[0][0] != PACKAGE or matches[0][1] != code:
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
