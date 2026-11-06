#!/usr/bin/env python3
"""T5: actual original signed APK 206-range SHA, Android badging and apksigner verification.

One original 672,853,870-byte STORED APK, not outer 2.97GB ZIP/2.3GB OBB.
Reports only bounded build metadata; never publishes original signed file,
signed Azure redirect URL, raw cert text, secret or private game asset.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

from scripts.t5_probe_github_artifact_zip_range import (
    ARTIFACTS, PACKAGE, LimitedRangeIO, MAX_MANIFEST,
    ProbeError, _github_request, _http_range_fetcher,
    _kind, _safe_json, _sanitized_manifest,
)
from scripts.t5_probe_signed_nested_zip_range import (
    CHECKPOINT, stored_member_offset,
)

ORIGINAL_RUN = 42058825739
ORIGINAL_SHA = "e9c358eda01785b65e4eb14f18723da426635628"
APK_BYTES = 672853870
MAX_PAYLOAD_BYTES = 700 * 1024 * 1024
CHUNK_BYTES = 4 * 1024 * 1024
MIN_FREE_DISK_BYTES = 1024 * 1024 * 1024
BADGING = re.compile(r"^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']*)'", re.M)
SCHEME = re.compile(r"^Verified using (v[0-9]+(?:\\.[0-9]+)?) scheme[^:]*: (true|false)$", re.M)
CERT_SHA = re.compile(r"^Signer #([0-9]+) certificate SHA-256 digest: ([a-fA-F0-9]{64})$", re.M)
SIG_VERIFIED = re.compile(r"^Verifies$", re.M)
NO_SECRET_ERROR = frozenset({
    "artifact_metadata_changed", "artifact_run_drift", "manifest_member_missing",
    "manifest_zip_inconclusive", "manifest_apk_mismatch",
    "outer_stored_apk_missing_or_ambiguous", "outer_apk_size_mismatch",
    "archive_range_read_budget_exhausted", "remote_range_request_failed",
    "remote_range_incomplete", "signed_artifact_range_inconclusive",
    "remote_apk_size_cap", "downloaded_apk_digest_mismatch",
    "android_build_tools_unavailable", "disk_insufficient",
    "android_aapt_badging_failed", "android_manifest_identity_mismatch",
    "apksigner_verification_failed", "apksigner_output_incomplete",
    "apk_signer_certificate_invalid",
})


def pinned_artifact(artifact, token):
    number, name, expected_size, digest = artifact
    base = ("https://api.github.com/repos/alwansan/raf/actions/artifacts/"
            + str(number))
    metadata = _github_request(base, token)
    if (metadata.get("id") != number or metadata.get("name") != name
            or metadata.get("size_in_bytes") != expected_size
            or metadata.get("digest") != digest
            or metadata.get("expired") is not False):
        raise ProbeError("artifact_metadata_changed")
    source = metadata.get("workflow_run")
    if (source is not None and
            (type(source) is not dict or source.get("id") != ORIGINAL_RUN
             or source.get("head_sha") != ORIGINAL_SHA)):
        raise ProbeError("artifact_run_drift")
    return _github_request(base + "/zip", token, redirect=True)


def delivery_claim(token):
    """Read only the signed-delivery provenance's tiny untrusted manifest, not APK."""
    artifact = ARTIFACTS[0]
    redirected = pinned_artifact(artifact, token)
    stream = LimitedRangeIO(artifact[2], _http_range_fetcher(redirected, artifact[2]),
                            budget=4 * 1024 * 1024)
    try:
        with zipfile.ZipFile(stream) as archive:
            members = [m for m in archive.infolist() if m.filename == "delivery.json"]
            if len(members) != 1 or members[0].file_size > MAX_MANIFEST:
                raise ProbeError("manifest_member_missing")
            with archive.open(members[0]) as item:
                original = _safe_json(item.read(MAX_MANIFEST + 1))
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("manifest_zip_inconclusive") from None
    summary = _sanitized_manifest(original)
    original_apk_rows = [
        row for row in original["files"]
        if type(row) is dict and row.get("name") == "Raft-Android-Test.apk"
    ]
    if (len(original_apk_rows) != 1
            or summary["version_code"] != "89"
            or summary["logical_file_bytes"]["apk"] != APK_BYTES):
        raise ProbeError("manifest_apk_mismatch")
    row = original_apk_rows[0]
    if (type(row["sha256"]) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
        raise ProbeError("manifest_apk_mismatch")
    return row["sha256"], summary["version_code"], stream.transferred


def locate_stored_apk(token):
    """Return a signed-blob URL privately plus actual STORED subfile position."""
    artifact = CHECKPOINT
    location = pinned_artifact(artifact, token)
    stream = LimitedRangeIO(artifact[2], _http_range_fetcher(location, artifact[2]),
                            budget=4 * 1024 * 1024)
    try:
        with zipfile.ZipFile(stream) as archive:
            entries = archive.infolist()
            matches = [m for m in entries if _kind(m.filename) == "apk"]
            if len(entries) != 2 or len(matches) != 1:
                raise ProbeError("outer_stored_apk_missing_or_ambiguous")
            member = matches[0]
            if member.file_size != APK_BYTES:
                raise ProbeError("outer_apk_size_mismatch")
            offset = stored_member_offset(stream, archive, member)
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("signed_artifact_range_inconclusive") from None
    return location, artifact[2], offset, stream.transferred


def stream_bounded_apk(fetcher, offset, length, destination: Path,
                       expected_digest: str, *, max_bytes=MAX_PAYLOAD_BYTES,
                       chunk_bytes=CHUNK_BYTES):
    """Strong SHA comparison of *every* original APK byte; no ZIP meta shortcut."""
    if (type(length) is not int or length != APK_BYTES
            or length > max_bytes or chunk_bytes < 1
            or chunk_bytes > CHUNK_BYTES):
        raise ProbeError("remote_apk_size_cap")
    sha = hashlib.sha256()
    count = 0
    with destination.open("xb") as file:
        while count < length:
            target = min(chunk_bytes, length - count)
            data = fetcher(offset + count, target)
            if type(data) is not bytes or len(data) != target:
                raise ProbeError("remote_range_incomplete")
            file.write(data)
            sha.update(data)
            count += len(data)
    if count != length or sha.hexdigest() != expected_digest:
        raise ProbeError("downloaded_apk_digest_mismatch")
    return {"fully_streamed_signed_apk_bytes": count,
            "original_delivery_manifest_apk_sha256_matched": True,
            "full_original_signed_apk_digest_prefix_12": sha.hexdigest()[:12]}


def android_tools(sdk_directory: Path):
    """Find genuine existing installed Android SDK build-tools; never self-install."""
    root = sdk_directory / "build-tools"
    if not root.is_dir():
        raise ProbeError("android_build_tools_unavailable")
    for folder in sorted(root.iterdir(), reverse=True):
        apksigner, aapt = folder / "apksigner", folder / "aapt"
        if (apksigner.is_file() and os.access(apksigner, os.X_OK)
                and aapt.is_file() and os.access(aapt, os.X_OK)):
            return apksigner, aapt, folder.name
    raise ProbeError("android_build_tools_unavailable")


def parse_aapt_badging(output, expected_version):
    if type(output) is not str:
        raise ProbeError("android_aapt_badging_failed")
    matches = BADGING.findall(output)
    if len(matches) != 1 or matches[0][0] != PACKAGE or matches[0][1] != expected_version:
        raise ProbeError("android_manifest_identity_mismatch")
    return {"package_from_signed_binary_AndroidManifest": PACKAGE,
            "version_code_from_signed_binary_AndroidManifest": matches[0][1],
            "binary_manifest_identity_matches_original_delivery": True}


def parse_apksigner(output: str):
    if type(output) is not str or not SIG_VERIFIED.search(output):
        raise ProbeError("apksigner_output_incomplete")
    schemes = dict((name, state == "true") for name, state in SCHEME.findall(output))
    signer = CERT_SHA.findall(output)
    if len(signer) != 1 or signer[0][0] != "1":
        raise ProbeError("apk_signer_certificate_invalid")
    if not any(schemes.values()):
        raise ProbeError("apksigner_output_incomplete")
    return {
        "apksigner_crypto_verified": True,
        "apksigner_signature_schemes_verified": schemes,
        "apksigner_signer_count": 1,
        "apksigner_certificate_sha256_prefix_12": signer[0][1].lower()[:12],
    }


def inspect_android_tools(apk: Path, version_code: str, sdk_directory: Path):
    apksigner, aapt, tool_version = android_tools(sdk_directory)
    def execute(command, timeout):
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace",
                                    timeout=timeout, check=False)
            return result
        except (OSError, subprocess.TimeoutExpired):
            return None
    aapt_response = execute([str(aapt), "dump", "badging", str(apk)], 90)
    if aapt_response is None or aapt_response.returncode != 0:
        raise ProbeError("android_aapt_badging_failed")
    identity = parse_aapt_badging(aapt_response.stdout, version_code)
    signer_response = execute([str(apksigner), "verify", "--verbose",
                               "--print-certs", str(apk)], 180)
    if signer_response is None or signer_response.returncode != 0:
        raise ProbeError("apksigner_verification_failed")
    signature = parse_apksigner(signer_response.stdout)
    return {"android_build_tools_version": tool_version, **identity, **signature}


def run_actual(token, sdk_dir):
    original_digest, original_version, manifest_range_bytes = delivery_claim(token)
    url, envelope_bytes, offset, checkpoint_range_bytes = locate_stored_apk(token)
    if shutil.disk_usage(tempfile.gettempdir()).free < MIN_FREE_DISK_BYTES:
        raise ProbeError("disk_insufficient")
    with tempfile.TemporaryDirectory(prefix="t5-original-apk-private-") as directory:
        apk = Path(directory) / "Raft-Android-Test.apk"
        fetch = _http_range_fetcher(url, envelope_bytes)
        full = stream_bounded_apk(fetch, offset, APK_BYTES, apk, original_digest)
        validated = inspect_android_tools(apk, original_version, sdk_dir)
        # APK automatically deleted on success or failures, never uploaded.
    return {
        "source_run": ORIGINAL_RUN,
        "source_commit": ORIGINAL_SHA,
        "real_signed_apk_full_byte_sha_verified": True,
        **full, **validated,
        "manifest_original_range_bytes": manifest_range_bytes,
        "checkpoint_original_range_metadata_bytes": checkpoint_range_bytes,
        "raw_apk_published": False,
        "original_obb_fully_hashed": False,
        "unity_obb_guid_verified": False,
        "actual_android_device_tested": False,
        "current_branch_unity_android_game_ready": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Allow read-only original signed archive byte ranges")
    opts = parser.parse_args()
    if not opts.live:
        parser.error("explicit --live required")
    token = os.environ.get("GITHUB_TOKEN", "")
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT") or ""
    if len(token) < 8 or not sdk:
        print("T5_REAL_SIGNED_APK status=BLOCKED reason=token_or_android_sdk_missing")
        raise SystemExit(2)
    try:
        result = run_actual(token, Path(sdk))
    except ProbeError as error:
        reason = str(error)
        if reason not in NO_SECRET_ERROR:
            reason = "source_or_remote_input_inconclusive"
        print("T5_REAL_SIGNED_APK status=BLOCKED reason=" + reason)
        raise SystemExit(2) from None
    except Exception:
        print("T5_REAL_SIGNED_APK status=BLOCKED reason=unexpected_exception_redacted")
        raise SystemExit(2) from None
    print("T5_REAL_SIGNED_APK " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
