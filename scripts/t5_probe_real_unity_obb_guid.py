#!/usr/bin/env python3
"""T5: actual immutable signed Raft APK/OBB unity_obb_guid identity check.

Reads real original owner-tested checkpoint via strict HTTP206 range only, never
downloads 3GB files or emits resource bytes/private GUID or blob redirect.
Checks exact Unity marker only; patch.89 lookup and installed device remain
independent of internal marker result.
"""
from __future__ import annotations

import argparse
import json
import os
import zipfile

from scripts.t5_probe_github_artifact_zip_range import (
    LimitedRangeIO, ProbeError, _http_range_fetcher, _kind, _safe_member,
)
from scripts.t5_probe_signed_nested_zip_range import (
    CHECKPOINT, MemberSliceIO, stored_member_offset,
)
from scripts.t5_verify_real_signed_apk import pinned_artifact
from scripts.t5_verify_apk_obb_pair import _verify_local_zip_headers

MARKER = "assets/unity_obb_guid"
APK_BYTES = 672853870
OBB_BYTES = 2301256312
MAX_MARKER_BYTES = 256
MAX_REMOTE_BYTES = 16 * 1024 * 1024


def _marker(archive: zipfile.ZipFile):
    """Read one exact small marker or return None if genuinely absent.

    Fully reads and CRC checks only the marker. The caller separately checks
    every member's local-vs-central name to authenticate lookup behavior.
    """
    entries = [z for z in archive.infolist() if z.filename == MARKER]
    if not entries:
        return None
    if len(entries) != 1:
        raise ProbeError("unity_guid_marker_duplicate")
    entry = entries[0]
    if (entry.is_dir() or entry.file_size < 1 or
            entry.file_size > MAX_MARKER_BYTES or
            entry.compress_size > MAX_MARKER_BYTES or
            entry.flag_bits & 1):
        raise ProbeError("unity_guid_marker_invalid_size_type")
    try:
        with archive.open(entry, "r") as reader:
            content = reader.read(MAX_MARKER_BYTES + 1)
        if len(content) != entry.file_size:
            raise ProbeError("unity_guid_marker_truncated")
        return content
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("unity_guid_marker_payload_unreadable") from None


def compare_unity_obb_guid(apk: zipfile.ZipFile, obb: zipfile.ZipFile):
    """Do not call two absent GUIDs a match or invent engine-side GUID data."""
    _verify_local_zip_headers(apk, apk.infolist())
    _verify_local_zip_headers(obb, obb.infolist())
    a = _marker(apk)
    o = _marker(obb)
    a_present, o_present = a is not None, o is not None
    if a_present and o_present and a != o:
        raise ProbeError("unity_guid_marker_mismatch")
    if a_present and o_present:
        status = "both_present_byte_identical"
    elif not a_present and not o_present:
        status = "both_absent_identity_unavailable"
    elif a_present:
        status = "apk_only_identity_unavailable"
    else:
        status = "obb_only_identity_unavailable"
    return {
        "real_nested_apk_zip_member_count": len(apk.infolist()),
        "real_nested_obb_zip_member_count": len(obb.infolist()),
        "all_original_APK_OBB_local_headers_match_central": True,
        "apk_unity_obb_guid_marker_present": a_present,
        "obb_unity_obb_guid_marker_present": o_present,
        "unity_obb_guid_marker_identity": status,
        "marker_exact_bytes_compared": len(a) if a_present and o_present else 0,
        "unity_obb_guid_embedded_value_revealed": False,
        "apk_obb_shared_guid_marker_comparison_proven": bool(a_present and o_present),
        "unity_internal_engine_guid_verified": False,
        "actual_installed_phone_obb_mount_verified": False,
        "optional_patch_89_probe_caused_main_corruption": False,
    }


def inspect_checkpoint(parent: LimitedRangeIO, *, expected_apk_bytes=APK_BYTES, expected_obb_bytes=OBB_BYTES):
    try:
        with zipfile.ZipFile(parent, "r", allowZip64=True) as archive:
            entries = archive.infolist()
            if len(entries) != 2:
                raise ProbeError("outer_signed_checkpoint_member_count_drift")
            members = {}
            for entry in entries:
                _safe_member(entry.filename)
                kind = _kind(entry.filename)
                if kind not in ("apk", "obb") or kind in members:
                    raise ProbeError("outer_signed_checkpoint_member_identity_drift")
                members[kind] = entry
            if set(members) != {"apk", "obb"}:
                raise ProbeError("outer_signed_checkpoint_missing_member")
            if (members["apk"].file_size != expected_apk_bytes or
                    members["obb"].file_size != expected_obb_bytes):
                raise ProbeError("outer_original_signed_file_size_drift")
            bounds = {}
            for kind, entry in members.items():
                offset = stored_member_offset(parent, archive, entry)
                bounds[kind] = (offset, offset + entry.file_size)
            if not (bounds["apk"][1] <= bounds["obb"][0] or
                    bounds["obb"][1] <= bounds["apk"][0]):
                raise ProbeError("outer_original_signed_regions_overlap")
            with zipfile.ZipFile(
                MemberSliceIO(parent, bounds["apk"][0], expected_apk_bytes), "r"
            ) as apk, zipfile.ZipFile(
                MemberSliceIO(parent, bounds["obb"][0], expected_obb_bytes), "r"
            ) as obb:
                answer = compare_unity_obb_guid(apk, obb)
            return {
                "original_signed_checkpoint_run": 42058825739,
                "original_signed_checkpoint_source_commit":
                    "e9c358eda01785b65e4eb14f18723da426635628",
                "original_signed_checkpoint_artifact_id": CHECKPOINT[0],
                **answer,
                "real_original_HTTP206_bytes": parent.transferred,
                "real_original_HTTP206_requests": parent.requests,
                "original_apk_obb_full_SHA_verified_elsewhere": True,
                "original_delivery_manifest_independently_signed": False,
                "game_ready_or_GPU_pixels_verified": False,
            }
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("unity_guid_real_nested_zip_inconclusive") from None


def inspect_live():
    token = os.environ.get("GITHUB_TOKEN", "")
    if len(token) < 8:
        raise ProbeError("github_token_missing")
    url = pinned_artifact(CHECKPOINT, token)
    parent = LimitedRangeIO(
        CHECKPOINT[2], _http_range_fetcher(url, CHECKPOINT[2]),
        budget=MAX_REMOTE_BYTES)
    return inspect_checkpoint(parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        parser.error("read-only original source proof requires explicit --live")
    try:
        report = inspect_live()
    except ProbeError as error:
        # A safe local vocabulary only. Do not show source GUID, member names,
        # signed Azure URLs, auth exception or original game bytes.
        safe = {
            "github_token_missing", "artifact_metadata_changed",
            "artifact_run_drift", "unity_guid_marker_duplicate",
            "unity_guid_marker_invalid_size_type",
            "unity_guid_marker_truncated", "unity_guid_marker_payload_unreadable",
            "unity_guid_marker_one_sided", "unity_guid_marker_mismatch",
            "outer_original_signed_file_size_drift",
            "outer_signed_checkpoint_member_count_drift",
            "outer_signed_checkpoint_member_identity_drift",
            "outer_signed_checkpoint_missing_member",
            "outer_original_signed_regions_overlap",
            "unity_guid_real_nested_zip_inconclusive",
            "archive_range_read_budget_exhausted",
        }
        why = str(error)
        print("T5_REAL_UNITY_OBB_GUID status=BLOCKED reason=" +
              (why if why in safe else "redacted_remote_or_archive_error"))
        raise SystemExit(2) from None
    except Exception:
        print("T5_REAL_UNITY_OBB_GUID status=BLOCKED reason=unexpected_redacted")
        raise SystemExit(2) from None
    print("T5_REAL_UNITY_OBB_GUID " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
