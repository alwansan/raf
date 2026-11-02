#!/usr/bin/env python3
"""Private structural validation of Unity's matching APK/OBB pair.

Never extracts or prints original game assets or member names. This does not
verify that Android mounted the expansion, that gameplay works, or that the
file can be installed from a phone without the required companion.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
import zlib

# Google Play's documented maximum is 2 GB for EACH APK expansion file.
# This is a distribution constraint, not a proof of Android sideload failure.
PLAY_EXPANSION_FILE_LIMIT_BYTES = 2_000_000_000
JAVA_ARRAY_LIMIT_BYTES = 2_147_483_647


def _names(archive):
    names = set()
    for item in archive.infolist():
        name = item.filename
        path = PurePosixPath(name)
        if (not name or name.startswith("/") or "\\" in name or ":" in name or
                ".." in path.parts or path.is_absolute() or name in names):
            raise ValueError("Unsafe or duplicate APK/OBB ZIP member")
        names.add(name)
    return names


def audit_companion(apk: Path, obb: Path, *, digest: bool = True,
                    play_limit_bytes: int = PLAY_EXPANSION_FILE_LIMIT_BYTES,
                    java_array_limit_bytes: int = JAVA_ARRAY_LIMIT_BYTES,
                    verify_crc: bool = False):
    if not apk.is_file() or not obb.is_file() or obb.stat().st_size == 0:
        raise FileNotFoundError("Both nonempty APK and matching OBB are required")
    with zipfile.ZipFile(apk) as app, zipfile.ZipFile(obb) as expansion:
        app_names = _names(app)
        expansion_names = _names(expansion)
        # Stream each ZIP member through Python's bounded reader to check CRC.
        # CRC verifies transport integrity, not original game-byte fidelity.
        if verify_crc:
            try:
                if app.testzip() is not None or expansion.testzip() is not None:
                    raise ValueError("APK/OBB ZIP payload CRC mismatch")
            except (zipfile.BadZipFile, EOFError, RuntimeError, OSError, zlib.error):
                raise ValueError("APK/OBB ZIP payload CRC validation failed") from None
        if not any(x.filename.startswith("assets/bin/Data/") and x.file_size
                   for x in app.infolist()):
            raise ValueError("APK is missing the initial Unity scene/data")
        data = [x for x in expansion.infolist()
                if x.filename.startswith("assets/bin/Data/") and x.file_size]
        if not data:
            raise ValueError("OBB has no original Unity scene/resource data")
        # Unity versions vary in their expansion build-id representation.
        # Only claim a GUID comparison when both archives expose the marker.
        marker = "assets/unity_obb_guid"
        match = "unavailable"
        if marker in app_names and marker in expansion_names:
            if (app.getinfo(marker).file_size > 256 or
                    expansion.getinfo(marker).file_size > 256 or
                    app.read(marker) != expansion.read(marker)):
                raise ValueError("APK/OBB identity mismatch")
            match = "verified"
        # Size-only diagnostics: no asset paths, payloads or proprietary bytes.
        # ZIP member sizes are uncompressed; compressed_size excludes ZIP headers.
        obb_bytes = obb.stat().st_size
        result = {
            "companionRequired": True,
            "obbBytes": obb_bytes,
            "obbPlayLimitBytes": play_limit_bytes,
            "obbPlayLimitExceeded": obb_bytes > play_limit_bytes,
            "obbPlayExcessBytes": max(0, obb_bytes - play_limit_bytes),
            "obbUnityStoredMembers": sum(x.compress_type == zipfile.ZIP_STORED for x in data),
            "obbUnityDeflatedMembers": sum(x.compress_type == zipfile.ZIP_DEFLATED for x in data),
            "obbUnityStoredBytes": sum(x.file_size for x in data
                                       if x.compress_type == zipfile.ZIP_STORED),
            "obbZipContainerOverheadBytes": obb_bytes - sum(
                x.compress_size for x in expansion.infolist()),
            "zipCrcVerified": verify_crc,
            "obbUnityLargestMemberBytes": max(x.file_size for x in data),
            "obbUnityCompressedBytes": sum(x.compress_size for x in data),
            "obbUnityMembersOverJavaArray": sum(
                x.file_size > java_array_limit_bytes for x in data),
            "obbZipMembers": len(expansion.infolist()),
            "obbUnityDataMembers": len(data),
            "obbUnityDataBytes": sum(x.file_size for x in data),
            "expansionIdentityCheck": match,
            "originalBytesVerified": False,
            "deviceMountedVerified": False,
            "assetNamesLogged": False,
        }
    if digest:
        h = hashlib.sha256()
        with obb.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                h.update(block)
        result["obbSha256"] = h.hexdigest()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--obb", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--verify-crc", action="store_true",
                        help="Stream-validate APK and OBB ZIP member CRCs")
    args = parser.parse_args()
    report = audit_companion(args.apk, args.obb, verify_crc=args.verify_crc)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("RAFT_ANDROID_OBB_AUDIT " + json.dumps(report, sort_keys=True))
