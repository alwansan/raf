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

# This tool runs both as a package module in unit tests and directly via
# "python3 scripts/audit_android_expansion.py" in the native delivery workflow.
if __package__:
    from scripts.probe_haptics_asset_manifest import (
        PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA, verify_manifest_blob)
else:
    from probe_haptics_asset_manifest import (
        PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA, verify_manifest_blob)

# Google Play's documented maximum is 2 GB for EACH APK expansion file.
# This is a distribution constraint, not a proof of Android sideload failure.
PLAY_EXPANSION_FILE_LIMIT_BYTES = 2_000_000_000
JAVA_ARRAY_LIMIT_BYTES = 2_147_483_647


def _names(archive):
    names = set()
    for item in archive.infolist():
        name = item.filename
        path = PurePosixPath(name)
        # PurePosixPath silently collapses /./ and repeated slashes, but a
        # Unity/Android ZIP lookup uses the *literal* archive entry name.
        # Check raw components so the auditor cannot accept a member that
        # is differently spelled from the resource requested by the app.
        parts = name.split("/")
        if item.is_dir():
            # A single trailing slash is the normal ZIP directory marker.
            parts = parts[:-1]
        if (not name or name.startswith("/") or "\\" in name or ":" in name or
                any(part in ("", ".", "..") for part in parts) or
                path.is_absolute() or name in names):
            raise ValueError("Unsafe or duplicate APK/OBB ZIP member")
        names.add(name)
    return names



def _audit_original_haptics(expansion, manifest_path, trusted_manifest_blob_sha):
    """Validate the *archive* URLs used by HapticAudio, not merely source staging.

    Old device traces request jar:file:/...obb!/assets/Haptics/<name>.wav.
    The pinned manifest names the original Git blobs. Read each member
    incrementally (no WAV extraction, payload logging or extra huge buffer).
    """
    import re

    manifest = json.loads(verify_manifest_blob(
        Path(manifest_path), trusted_manifest_blob_sha).decode("utf-8"))
    if (manifest.get("schema_version") != 1 or
            manifest.get("path_prefix") != "Raft/Raft_Data/StreamingAssets/Haptics/"):
        raise ValueError("Invalid original Haptics manifest schema")
    files = manifest.get("files")
    if not isinstance(files, dict) or len(files) != 29:
        raise ValueError("Expected exactly 29 pinned original Haptics WAV identities")
    seen_casefold = set()
    total = 0
    for name, expected in files.items():
        if (not isinstance(name, str) or
                re.fullmatch(r"[A-Za-z0-9_-]+\.wav", name) is None or
                name.casefold() in seen_casefold or
                not isinstance(expected, dict) or
                set(expected) != {"bytes", "git_blob_sha"} or
                type(expected["bytes"]) is not int or expected["bytes"] <= 0 or
                not isinstance(expected["git_blob_sha"], str) or
                re.fullmatch(r"[0-9a-f]{40}", expected["git_blob_sha"]) is None):
            raise ValueError("Unsafe or malformed original Haptics manifest")
        seen_casefold.add(name.casefold())
        # This exact entry is requested by the historical Android OBB URL.
        # assets/bin/Data/StreamingAssets/Haptics/ is NOT equivalent.
        target = "assets/Haptics/" + name
        try:
            entry = expansion.getinfo(target)
        except KeyError:
            raise ValueError("Original Haptics entry absent at Android jar URL") from None
        if entry.is_dir() or entry.file_size != expected["bytes"]:
            raise ValueError("Original Haptics entry size/type mismatch")
        h = hashlib.sha1()
        h.update(("blob " + str(expected["bytes"])).encode("ascii") + b"\0")
        size = 0
        try:
            with expansion.open(entry) as stream:
                for data in iter(lambda: stream.read(256 * 1024), b""):
                    size += len(data)
                    if size > expected["bytes"]:
                        raise ValueError("Original Haptics entry exceeded pinned size")
                    h.update(data)
        except (zipfile.BadZipFile, EOFError, RuntimeError, OSError, zlib.error):
            raise ValueError("Original Haptics OBB ZIP member corrupted") from None
        if size != expected["bytes"] or h.hexdigest() != expected["git_blob_sha"]:
            raise ValueError("Original Haptics OBB Git blob identity mismatch")
        total += size
    return {"hapticsOriginalMembers": len(files),
            "hapticsOriginalBytes": total,
            "hapticsJarPathsAndOriginalGitBlobsVerified": True}


def audit_companion(apk: Path, obb: Path, *, digest: bool = True,
                    play_limit_bytes: int = PLAY_EXPANSION_FILE_LIMIT_BYTES,
                    java_array_limit_bytes: int = JAVA_ARRAY_LIMIT_BYTES,
                    verify_crc: bool = False, haptics_manifest: Path = None,
                    haptics_manifest_blob_sha: str = PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA):
    if not apk.is_file() or not obb.is_file() or obb.stat().st_size == 0:
        raise FileNotFoundError("Both nonempty APK and matching OBB are required")
    with zipfile.ZipFile(apk) as app, zipfile.ZipFile(obb) as expansion:
        app_names = _names(app)
        expansion_names = _names(expansion)
        haptics = (_audit_original_haptics(expansion, haptics_manifest,
                                            haptics_manifest_blob_sha)
                   if haptics_manifest is not None else None)
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
            "hapticsJarPathsAndOriginalGitBlobsVerified": haptics is not None,
            "hapticsOriginalManifestPinned": haptics is not None,
        }
    if haptics is not None:
        result.update(haptics)
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
    parser.add_argument("--haptics-manifest", type=Path,
                        help="Strict original 29-WAV final OBB jar path/Git blob audit")
    parser.add_argument("--haptics-manifest-blob",
                        default=PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA,
                        help="Audited original manifest Git blob SHA, never read from a mutable manifest")
    parser.add_argument("--verify-crc", action="store_true",
                        help="Stream-validate APK and OBB ZIP member CRCs")
    args = parser.parse_args()
    report = audit_companion(args.apk, args.obb, verify_crc=args.verify_crc,
                             haptics_manifest=args.haptics_manifest,
                             haptics_manifest_blob_sha=args.haptics_manifest_blob)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("RAFT_ANDROID_OBB_AUDIT " + json.dumps(report, sort_keys=True))
