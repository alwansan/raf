#!/usr/bin/env python3
"""T5: authenticate ALL original main OBB bytes against the original delivery manifest.

Pin both owner GitHub artifacts; read original 2.30GB OBB STORED member through
strict HTTP 206 only, streaming SHA-256 + ZIP outer CRC32. No OBB disk copy,
outer artifact download, Unity runtime, device test or proprietary byte logging.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import zlib
import zipfile

from scripts.t5_probe_github_artifact_zip_range import (
    ARTIFACTS, PACKAGE, MAX_MANIFEST, LimitedRangeIO, ProbeError,
    _http_range_fetcher, _kind, _safe_json, _sanitized_manifest,
)
from scripts.t5_probe_signed_nested_zip_range import CHECKPOINT, stored_member_offset
from scripts.t5_verify_real_signed_apk import pinned_artifact

ORIGINAL_RUN = 42058825739
ORIGINAL_SHA = "e9c358eda01785b65e4eb14f18723da426635628"
OBB_BYTES = 2301256312
APK_BYTES = 672853870
MAX_OBB_TRANSFER = 2400000000
RANGE_CHUNK = 4 * 1024 * 1024
METADATA_BUDGET = 4 * 1024 * 1024
EXPECTED_OBB_NAME = "main.89." + PACKAGE + ".obb"
EXPECTED_OBB_PARTS = 3
# Do not echo remote exception/URL, auth data, original names or binary bytes.
SAFE_ERRORS = frozenset({
    "github_token_missing", "artifact_metadata_changed", "artifact_run_drift",
    "manifest_obb_missing", "manifest_obb_metadata_drift",
    "manifest_member_missing", "manifest_zip_inconclusive",
    "outer_signed_members_incorrect", "outer_obb_missing_or_ambiguous",
    "outer_obb_size_drift", "outer_stored_member_inconclusive",
    "original_obb_stream_cap", "remote_range_incomplete",
    "remote_range_content_mismatch", "remote_range_length_mismatch",
    "server_does_not_support_bounded_ranges", "remote_range_request_unavailable",
    "sha256_obb_mismatch", "outer_zip_obb_crc32_mismatch",
})


def original_manifest_obb_claim(token: str):
    """Read actual old delivery.json from trusted GitHub artifact metadata.

    This artifact is pinned, but its JSON file is NOT independently
    publisher-signed. Preserve that security distinction in result flags.
    """
    artifact = ARTIFACTS[0]
    url = pinned_artifact(artifact, token)
    reader = LimitedRangeIO(artifact[2], _http_range_fetcher(url, artifact[2]),
                            budget=METADATA_BUDGET)
    try:
        with zipfile.ZipFile(reader) as envelope:
            names = [x for x in envelope.infolist() if x.filename == "delivery.json"]
            if len(names) != 1 or names[0].file_size <= 0 or names[0].file_size > MAX_MANIFEST:
                raise ProbeError("manifest_member_missing")
            with envelope.open(names[0]) as document:
                raw = _safe_json(document.read(MAX_MANIFEST + 1))
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("manifest_zip_inconclusive") from None

    summary = _sanitized_manifest(raw)
    rows = [f for f in raw["files"] if type(f) is dict and _kind(f.get("name", "")) == "obb"]
    if (len(rows) != 1 or
        summary["version_code"] != "89" or
        summary["package"] != PACKAGE or
        summary["logical_file_bytes"]["obb"] != OBB_BYTES or
        summary["logical_transport_part_counts"]["obb"] != EXPECTED_OBB_PARTS or
        rows[0].get("name") != EXPECTED_OBB_NAME):
        raise ProbeError("manifest_obb_metadata_drift")
    expected_digest = rows[0].get("sha256")
    if type(expected_digest) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_digest) is None:
        raise ProbeError("manifest_obb_metadata_drift")
    return expected_digest, reader.transferred


def locate_actual_signed_obb(token: str):
    artifact = CHECKPOINT
    url = pinned_artifact(artifact, token)
    reader = LimitedRangeIO(artifact[2], _http_range_fetcher(url, artifact[2]),
                            budget=METADATA_BUDGET)
    try:
        with zipfile.ZipFile(reader) as archive:
            members = archive.infolist()
            if len(members) != 2:
                raise ProbeError("outer_signed_members_incorrect")
            files = {}
            for member in members:
                kind = _kind(member.filename)
                if kind not in ("apk", "obb") or kind in files:
                    raise ProbeError("outer_signed_members_incorrect")
                files[kind] = member
            if set(files) != {"apk", "obb"}:
                raise ProbeError("outer_obb_missing_or_ambiguous")
            if files["apk"].file_size != APK_BYTES or files["obb"].file_size != OBB_BYTES:
                raise ProbeError("outer_obb_size_drift")
            member = files["obb"]
            offset = stored_member_offset(reader, archive, member)
            crc32 = member.CRC
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("outer_stored_member_inconclusive") from None
    return url, artifact[2], offset, crc32, reader.transferred


def hash_original_obb(fetcher, start, length, manifest_sha, expected_outer_crc,
                      *, max_transfer=MAX_OBB_TRANSFER, chunk_bytes=RANGE_CHUNK,
                      authentic_length=OBB_BYTES):
    """Stream entire OBB, compute SHA256 + CRC32, never retain file on disk."""
    if (type(start) is not int or start < 0 or
            type(length) is not int or length != authentic_length or
            length <= 0 or length > max_transfer or
            not 1 <= chunk_bytes <= RANGE_CHUNK or
            type(expected_outer_crc) is not int or
            not 0 <= expected_outer_crc <= 0xFFFFFFFF or
            type(manifest_sha) is not str or
            re.fullmatch(r"[0-9a-f]{64}", manifest_sha) is None):
        raise ProbeError("original_obb_stream_cap")
    full_sha = hashlib.sha256()
    crc = 0
    count = 0
    requests = 0
    while count < length:
        desired = min(chunk_bytes, length - count)
        try:
            piece = fetcher(start + count, desired)
        except ProbeError:
            raise
        except Exception:
            raise ProbeError("remote_range_incomplete") from None
        if type(piece) is not bytes or len(piece) != desired:
            raise ProbeError("remote_range_incomplete")
        full_sha.update(piece)
        crc = zlib.crc32(piece, crc) & 0xFFFFFFFF
        count += desired
        requests += 1
    if full_sha.hexdigest() != manifest_sha:
        raise ProbeError("sha256_obb_mismatch")
    if crc != expected_outer_crc:
        raise ProbeError("outer_zip_obb_crc32_mismatch")
    return {
        "real_obb_bytes_fully_hashed": count,
        "real_obb_full_sha256_matches_original_delivery_manifest": True,
        "real_obb_sha256_prefix_12": full_sha.hexdigest()[:12],
        "real_obb_stream_crc32_matches_signed_checkpoint_central_directory": True,
        "real_obb_range_requests": requests,
        "real_obb_range_payload_bytes": count,
        "original_obb_raw_file_published": False,
    }


def run_original_obb(token):
    declared, delivery_metadata_bytes = original_manifest_obb_claim(token)
    url, archive_size, offset, crc, checkpoint_metadata_bytes = locate_actual_signed_obb(token)
    original = hash_original_obb(
        _http_range_fetcher(url, archive_size), offset, OBB_BYTES,
        declared, crc)
    return {
        "original_source_run": ORIGINAL_RUN,
        "original_source_commit": ORIGINAL_SHA,
        "signed_checkpoint_artifact_id": CHECKPOINT[0],
        "actual_manifest_read_from_original_delivery": True,
        "original_delivery_manifest_crypto_signature_independently_verified": False,
        "original_signed_checkpoint_full_zip_sha_verified": False,
        "source_actual_signed_apk_sha_apksigner_verified_in_independent_CI42228262902": True,
        "delivery_manifest_metadata_range_bytes": delivery_metadata_bytes,
        "signed_checkpoint_metadata_range_bytes": checkpoint_metadata_bytes,
        **original,
        "unity_original_obb_guid_verified": False,
        "actual_android_obb_mount_verified": False,
        "current_android_build_gpu_water_shader_ready": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        parser.error("The original remote ZIP read requires explicit --live")
    token = os.environ.get("GITHUB_TOKEN", "")
    if len(token) < 8:
        print("T5_REAL_SIGNED_OBB status=BLOCKED reason=github_token_missing")
        raise SystemExit(2)
    try:
        result = run_original_obb(token)
        print("T5_REAL_SIGNED_OBB " + json.dumps(result, sort_keys=True))
    except ProbeError as exc:
        cause = str(exc)
        if cause not in SAFE_ERRORS:
            cause = "original_source_or_remote_inconclusive"
        print("T5_REAL_SIGNED_OBB status=BLOCKED reason=" + cause)
        raise SystemExit(2) from None
    except Exception:
        print("T5_REAL_SIGNED_OBB status=BLOCKED reason=unexpected_exception_redacted")
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
