#!/usr/bin/env python3
"""Verify a retained GitHub Actions *archive* for one immutable Raft delivery.

This is a streaming, read-only ZIP verifier. Does not extract game files,
verify APK signature or Unity OBB GUID, or claim device success.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

PACKAGE = "com.alwansan.raft.androidtest"
APK = "Raft-Android-Test.apk"
XAPK = "Raft-Android-Test.xapk"
SMALL = {"delivery.json": 100_000, "SHA256SUMS": 32_000}
AUX = {"delivery.json", "SHA256SUMS", "reassemble.py",
       "INSTALL_AR.md", "RECORDED_LIMITATIONS.json"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
SAFE = re.compile(r"[A-Za-z0-9_.-]+\Z")
BUFFER = 4 * 1024 * 1024
MAX_ZIP_ENTRIES = 32
MAX_PART_BYTES = 2_147_483_648


def _sha_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BUFFER), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_file(name: str) -> bool:
    return (isinstance(name, str) and SAFE.fullmatch(name) is not None
            and name not in (".", "..") and PurePosixPath(name).name == name)


def _record(value, label: str) -> dict:
    if type(value) is not dict:
        raise ValueError("Invalid " + label)
    return value


def _sha(value) -> bool:
    return isinstance(value, str) and HEX.fullmatch(value) is not None


def verify_archive(path: Path, *, expected_size: int, expected_sha: str,
                   expected_version: str) -> dict:
    if not path.is_file() or path.is_symlink() or path.stat().st_size != expected_size:
        raise ValueError("Actions archive is missing or its byte size differs")
    if not _sha(expected_sha):
        raise ValueError("Expected archive SHA256 is malformed")
    if _sha_path(path) != expected_sha:
        raise ValueError("Actions archive SHA256 differs from immutable API claim")
    obb = "main." + expected_version + "." + PACKAGE + ".obb"
    if not re.fullmatch(r"[1-9][0-9]*", expected_version):
        raise ValueError("Expected versionCode malformed")
    logical_names = [APK, obb, XAPK]
    with zipfile.ZipFile(path, "r") as archive:
        entries = archive.infolist()
        names = [z.filename for z in entries]
        if (not 5 <= len(names) <= MAX_ZIP_ENTRIES
                or len(set(names)) != len(names)
                or any(not _safe_file(x) for x in names)):
            raise ValueError("Archive member count, duplicate or path unsafe")
        info_by_name = {e.filename: e for e in entries}
        for name, limit in SMALL.items():
            member = info_by_name.get(name)
            if member is None or not 0 < member.file_size <= limit:
                raise ValueError("Missing/oversize small release metadata " + name)
        try:
            delivery = _record(json.loads(archive.read("delivery.json")), "delivery")
            sums = archive.read("SHA256SUMS").decode("ascii")
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Malformed delivery.json or SHA256SUMS") from exc
        if (delivery.get("schema") != 1 or delivery.get("package") != PACKAGE
                or delivery.get("version_code") != expected_version
                or delivery.get("companion_required") is not True
                or delivery.get("transport_only_parts") is not True
                or delivery.get("device_install_verified") is not False):
            raise ValueError("Actual delivery package/version contract differs from pinned build")
        files = delivery.get("files")
        if type(files) is not list or len(files) != 3:
            raise ValueError("Delivery must contain exactly APK, OBB and XAPK")
        transport = []
        logical_total = 0
        parts_set = set()
        for row, expected_name in zip(files, logical_names):
            row = _record(row, "logical output")
            size = row.get("bytes")
            logical_sha = row.get("sha256")
            if (row.get("name") != expected_name or type(size) is not int
                    or size < 1 or not _sha(logical_sha)):
                raise ValueError("Delivery logical output identity or digest invalid")
            parts = row.get("parts")
            if type(parts) is not list or not 1 <= len(parts) <= 16:
                raise ValueError("Delivery part list invalid")
            whole = hashlib.sha256()
            actual_bytes = 0
            for index, part in enumerate(parts, start=1):
                part = _record(part, "transport part")
                name = expected_name if len(parts) == 1 else expected_name + ".part" + str(index).zfill(3)
                declared = part.get("bytes")
                digest = part.get("sha256")
                if (part.get("name") != name or not _safe_file(name) or name in parts_set
                        or type(declared) is not int or not 0 < declared < MAX_PART_BYTES
                        or not _sha(digest)):
                    raise ValueError("Part order, identity, SHA or size invalid")
                member = info_by_name.get(name)
                if member is None or member.is_dir() or member.file_size != declared:
                    raise ValueError("Missing or wrong-size actual ZIP part " + name)
                observed = hashlib.sha256()
                actual_part_bytes = 0
                # ZIP open validates member CRC when read to EOF. No extracted files.
                with archive.open(member, "r") as stream:
                    for chunk in iter(lambda: stream.read(BUFFER), b""):
                        observed.update(chunk)
                        whole.update(chunk)
                        actual_part_bytes += len(chunk)
                if observed.hexdigest() != digest or actual_part_bytes != declared:
                    raise ValueError("Actual part bytes disagree with delivery SHA " + name)
                parts_set.add(name)
                transport.append((name, digest))
                actual_bytes += actual_part_bytes
            if actual_bytes != size or whole.hexdigest() != logical_sha:
                raise ValueError("Reconstructed logical output SHA/size differs " + expected_name)
            logical_total += size
        if set(names) - AUX != parts_set:
            raise ValueError("Unexpected or missing payload ZIP members")
        actual_lines = sums.splitlines(keepends=True)
        expected_lines = [digest + "  " + name + "\n" for name, digest in transport]
        if actual_lines != expected_lines:
            raise ValueError("SHA256SUMS disagrees with actual verified part stream")
        return {
            "source_native_run": 42058825739,
            "expected_version_code": expected_version,
            "archive_sha256_authenticated_to_pinned_claim": True,
            "logical_file_whole_hashes_verified": len(files),
            "actual_transport_part_hashes_verified": len(parts_set),
            "transport_total_bytes_read": logical_total,
            "apk_signature_verified": False,
            "android_obb_mounted": False,
            "unity_obb_internal_guid_verified": False,
            "device_render_fft_verified": False,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--expected-archive-bytes", type=int, required=True)
    parser.add_argument("--expected-archive-sha", required=True)
    parser.add_argument("--version-code", required=True)
    args = parser.parse_args()
    report = verify_archive(args.archive, expected_size=args.expected_archive_bytes,
                            expected_sha=args.expected_archive_sha,
                            expected_version=args.version_code)
    print("T5_RETAINED_NATIVE_DELIVERY " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
