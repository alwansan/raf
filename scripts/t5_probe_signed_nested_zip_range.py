#!/usr/bin/env python3
"""T5: actual signed APK+OBB nested ZIP central scan using bounded HTTP 206 only.

Reuses source-verified Actions artifact REST pin and strict redirect handler.
This is archive *structure*, not complete SHA/CRC/signature or phone verification.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import struct
import sys
import zipfile

from scripts.t5_probe_github_artifact_zip_range import (
    ARTIFACTS, MAX_MEMBERS, LimitedRangeIO, ProbeError, _github_request,
    _http_range_fetcher, _kind, _safe_member,
)

CHECKPOINT = ARTIFACTS[1]
MAX_TOTAL_TRANSFER = 16 * 1024 * 1024
MAX_FILENAME_BYTES = 4096
MAX_APK_MEMBERS = 200000
MAX_OBB_MEMBERS = 100000


class MemberSliceIO(io.RawIOBase):
    """Local seekable view over one STORED member, charged to parent's budget."""
    def __init__(self, parent: LimitedRangeIO, start: int, length: int):
        super().__init__()
        if not 0 <= start < parent.length or length <= 0 or start + length > parent.length:
            raise ProbeError("nested_stored_member_bounds_invalid")
        self.parent = parent
        self.start = start
        self.length = length
        self.position = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            next_pos = offset
        elif whence == io.SEEK_CUR:
            next_pos = self.position + offset
        elif whence == io.SEEK_END:
            next_pos = self.length + offset
        else:
            raise ValueError("bad_seek_mode")
        if type(next_pos) is not int or next_pos < 0 or next_pos > self.length:
            raise ProbeError("nested_member_seek_outside_bounds")
        self.position = next_pos
        return self.position

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.length - self.position
        size = min(size, self.length - self.position)
        if size <= 0:
            return b""
        self.parent.seek(self.start + self.position)
        out = self.parent.read(size)
        self.position += len(out)
        return out


def stored_member_offset(parent: LimitedRangeIO, archive: zipfile.ZipFile,
                         info: zipfile.ZipInfo) -> int:
    if (info.is_dir() or info.compress_type != zipfile.ZIP_STORED
            or info.compress_size != info.file_size or info.flag_bits & 1):
        raise ProbeError("outer_signed_member_not_stored")
    position = info.header_offset
    if position < 0 or position + 30 > archive.start_dir:
        raise ProbeError("outer_local_header_outside_bounds")
    parent.seek(position)
    raw = parent.read(30)
    if len(raw) != 30:
        raise ProbeError("outer_local_header_missing")
    sig, _ver, flags, method, _time, _date, crc, compressed, size, name_len, extra_len = (
        struct.unpack("<IHHHHHIIIHH", raw))
    if (sig != 0x04034B50 or flags != info.flag_bits or method != 0
            or name_len > MAX_FILENAME_BYTES):
        raise ProbeError("outer_local_header_drift")
    try:
        expected = info.filename.encode("utf-8" if flags & 0x800 else "cp437")
    except UnicodeEncodeError:
        raise ProbeError("outer_local_name_encoding_invalid") from None
    if len(expected) != name_len or parent.read(name_len) != expected:
        raise ProbeError("outer_local_member_name_mismatch")
    if not flags & 8 and (crc != info.CRC or
                          (compressed != 0xFFFFFFFF and compressed != info.compress_size) or
                          (size != 0xFFFFFFFF and size != info.file_size)):
        raise ProbeError("outer_local_member_size_or_crc_mismatch")
    data_start = position + 30 + name_len + extra_len
    if data_start + info.file_size > archive.start_dir:
        raise ProbeError("outer_member_overlaps_central")
    return data_start


def _guard_inner(archive: zipfile.ZipFile, *, apk: bool):
    members = archive.infolist()
    max_count = MAX_APK_MEMBERS if apk else MAX_OBB_MEMBERS
    if not 1 <= len(members) <= max_count:
        raise ProbeError("nested_member_count_invalid")
    names = set()
    count_unity = 0
    native_arm64_count = 0
    unity_asset_count = 0
    unity_resource_count = 0
    has_obb_payload = False
    for info in members:
        name = info.filename
        _safe_member(name)
        if name in names:
            raise ProbeError("nested_duplicate_name")
        names.add(name)
        if info.flag_bits & 1:
            raise ProbeError("nested_encrypted_member")
        mode = (info.external_attr >> 16) & 0xffff
        if info.create_system == 3 and (mode & 0o170000) == 0o120000:
            raise ProbeError("nested_symlink_member")
        if info.is_dir() or info.file_size <= 0:
            continue
        if name.startswith("assets/bin/Data/"):
            count_unity += 1
        if apk and name.startswith("lib/arm64-v8a/") and name.endswith(".so"):
            native_arm64_count += 1
        if name.endswith(".assets"):
            unity_asset_count += 1
        if name.endswith((".resS", ".resource")):
            unity_resource_count += 1
        if name.startswith("assets/"):
            has_obb_payload = True
    if apk:
        required = (
            "AndroidManifest.xml", "classes.dex",
            "lib/arm64-v8a/libil2cpp.so",
            "lib/arm64-v8a/libunity.so",
        )
        if any(name not in names for name in required):
            raise ProbeError("actual_apk_arm64_core_missing")
        if native_arm64_count < 2:
            raise ProbeError("actual_apk_arm64_library_count_low")
    elif not has_obb_payload:
        raise ProbeError("actual_obb_has_no_asset_payload")
    return {
        "zip_members": len(members),
        "unity_assets_bin_data_member_count": count_unity,
        "arm64_so_member_count": native_arm64_count,
        "unity_assets_extension_count": unity_asset_count,
        "unity_resources_extension_count": unity_resource_count,
        "required_apk_core_entries_present": True if apk else None,
        "has_obb_assets_prefix": has_obb_payload if not apk else None,
    }


def _read_small_prefix(archive: zipfile.ZipFile, name: str, limit: int):
    info = archive.getinfo(name)
    if info.file_size <= 0:
        raise ProbeError("required_core_member_empty")
    with archive.open(info, "r") as stream:
        return stream.read(limit)


def scan_signed_checkpoint(parent: LimitedRangeIO, *, expected_apk_bytes=672853870, expected_obb_bytes=2301256312):
    try:
        with zipfile.ZipFile(parent, "r", allowZip64=True) as envelope:
            members = envelope.infolist()
            if len(members) != 2:
                raise ProbeError("signed_checkpoint_outer_members_not_two")
            info = {}
            for candidate in members:
                _safe_member(candidate.filename)
                kind = _kind(candidate.filename)
                if kind not in ("apk", "obb") or kind in info:
                    raise ProbeError("signed_checkpoint_unexpected_member")
                info[kind] = candidate
            if set(info) != {"apk", "obb"}:
                raise ProbeError("signed_checkpoint_missing_apk_or_obb")
            if (info["apk"].file_size != expected_apk_bytes or
                    info["obb"].file_size != expected_obb_bytes):
                raise ProbeError("signed_checkpoint_manifest_size_drift")
            apk_start = stored_member_offset(parent, envelope, info["apk"])
            obb_start = stored_member_offset(parent, envelope, info["obb"])
            regions = sorted([
                (apk_start, apk_start + info["apk"].file_size),
                (obb_start, obb_start + info["obb"].file_size),
            ])
            if regions[0][1] > regions[1][0]:
                raise ProbeError("stored_outer_members_overlap")

            with zipfile.ZipFile(MemberSliceIO(parent, apk_start, info["apk"].file_size),
                                 "r", allowZip64=True) as apk:
                apk_report = _guard_inner(apk, apk=True)
                android_manifest = _read_small_prefix(apk, "AndroidManifest.xml", 8)
                dex = _read_small_prefix(apk, "classes.dex", 8)
                il2cpp = _read_small_prefix(apk, "lib/arm64-v8a/libil2cpp.so", 64)
                libunity = _read_small_prefix(apk, "lib/arm64-v8a/libunity.so", 64)
                apk_report["android_manifest_binary_xml_magic"] = (
                    len(android_manifest) >= 4 and android_manifest[:4] == b"\x03\x00\x08\x00")
                apk_report["dex_magic"] = (len(dex) >= 8 and dex[:4] == b"dex\n")
                apk_report["arm64_elf64_magic_both_libraries"] = all(
                    len(h) >= 64 and h[:7] == b"\x7fELF\x02\x01\x01" and
                    struct.unpack_from("<H", h, 18)[0] == 183
                    for h in (il2cpp, libunity))
                if not (apk_report["android_manifest_binary_xml_magic"] and
                        apk_report["dex_magic"] and
                        apk_report["arm64_elf64_magic_both_libraries"]):
                    raise ProbeError("signed_apk_core_binary_magic_missing")
            with zipfile.ZipFile(MemberSliceIO(parent, obb_start, info["obb"].file_size),
                                 "r", allowZip64=True) as obb:
                obb_report = _guard_inner(obb, apk=False)

            return {
                "actual_signed_checkpoint_nested_apk_zip_central_inspected": True,
                "actual_signed_checkpoint_nested_obb_zip_central_inspected": True,
                "original_checkpoint_apk_bytes": info["apk"].file_size,
                "original_checkpoint_obb_bytes": info["obb"].file_size,
                "apk": apk_report,
                "obb": obb_report,
                "remote_ranged_bytes": parent.transferred,
                "remote_ranged_request_count": parent.requests,
                "actual_inner_apk_obb_sha256_verified": False,
                "actual_apk_cryptographic_signature_verified": False,
                "actual_obb_unity_guid_verified": False,
                "actual_device_tested": False,
            }
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("signed_nested_zip_metadata_inconclusive") from None


def live():
    token = os.environ.get("GITHUB_TOKEN", "")
    if len(token) < 8:
        raise ProbeError("github_token_missing")
    number, label, length, digest = CHECKPOINT
    base = "https://api.github.com/repos/alwansan/raf/actions/artifacts/" + str(number)
    metadata = _github_request(base, token)
    if (metadata.get("id") != number or metadata.get("name") != label
            or metadata.get("size_in_bytes") != length
            or metadata.get("digest") != digest
            or metadata.get("expired") is not False):
        raise ProbeError("original_checkpoint_metadata_changed")
    workflow = metadata.get("workflow_run")
    if workflow is not None and (workflow.get("id") != 42058825739 or
                                 workflow.get("head_sha") !=
                                 "e9c358eda01785b65e4eb14f18723da426635628"):
        raise ProbeError("original_checkpoint_source_drift")
    location = _github_request(base + "/zip", token, redirect=True)
    parent = LimitedRangeIO(length, _http_range_fetcher(location, length),
                            budget=MAX_TOTAL_TRANSFER)
    result = scan_signed_checkpoint(parent)
    result.update({
        "source_run_id": 42058825739,
        "source_commit": "e9c358eda01785b65e4eb14f18723da426635628",
        "github_zip_artifact_id": number,
        "artifact_metadata_digest_not_rehashed": digest,
        "real_outer_zip_stored_members_verified": True,
        "original_full_artifact_downloaded": False,
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    opts = parser.parse_args()
    if not opts.live:
        parser.error("Requires explicit --live with read-only Actions token")
    try:
        print("T5_SIGNED_NESTED_ZIP_RANGE " + json.dumps(live(), sort_keys=True))
    except ProbeError as exc:
        print("T5_SIGNED_NESTED_ZIP_RANGE status=BLOCKED reason=" + str(exc))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
