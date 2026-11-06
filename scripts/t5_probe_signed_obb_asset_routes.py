#!/usr/bin/env python3
"""T5 authentic old signed OBB ZIP resource-path inventory for Android jar: reads.

Verify original JNI/managed-expected 5 FMOD bank + 29 Haptics WAV ZIP paths and
independent pinned byte lengths through strict HTTP206 central/local headers.
Never extract OBB assets, print content/resource filenames, sign/restore game,
or imply that the phone mounted the original file. Original file SHA verified
separately in existing 42058825739 evidence.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import zipfile

from scripts.probe_haptics_asset_manifest import (
    PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA, verify_manifest_blob,
)
from scripts.t5_probe_github_artifact_zip_range import (
    LimitedRangeIO, ProbeError, _http_range_fetcher, _kind, _safe_member,
)
from scripts.t5_probe_signed_nested_zip_range import (
    CHECKPOINT, MemberSliceIO, stored_member_offset,
)
from scripts.t5_verify_real_signed_apk import pinned_artifact
from scripts.t5_verify_apk_obb_pair import _verify_local_zip_headers

ORIGINAL_RUN = 42058825739
ORIGINAL_SHA = "e9c358eda01785b65e4eb14f18723da426635628"
ORIGINAL_APK_BYTES = 672853870
ORIGINAL_OBB_BYTES = 2301256312
MAX_HTTP_RANGE_BYTES = 16 * 1024 * 1024
ORIGINAL_WAV_TOTAL_BYTES = 32733104
BANK_SIZES = {
    "MasterBank.bank": 101600960,
    "MasterBank.strings.bank": 29530,
    "VO_logs_english.bank": 11455008,
    "VO_npc_english.bank": 8180896,
    "VO_olof_english.bank": 2551104,
}
BANK_TOTAL = sum(BANK_SIZES.values())
MANIFEST = Path(__file__).resolve().parents[1] / "config/original-haptics-manifest.json"
SIGNED_OBB = "main.89.com.alwansan.raft.androidtest.obb"
SIGNED_APK = "Raft-Android-Test.apk"


def pinned_haptic_lengths(path=MANIFEST):
    """Preserve immutable Git-blob anchored source inventory, no source WAV read."""
    try:
        document = json.loads(verify_manifest_blob(
            path, PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA
        ).decode("utf-8"))
    except Exception:
        raise ProbeError("pinned_haptics_manifest_unavailable") from None
    if (type(document) is not dict or
            document.get("schema_version") != 1 or
            document.get("path_prefix") != "Raft/Raft_Data/StreamingAssets/Haptics/"):
        raise ProbeError("pinned_haptics_manifest_schema_drift")
    rows = document.get("files")
    if type(rows) is not dict or len(rows) != 29:
        raise ProbeError("pinned_haptics_manifest_schema_drift")
    result = {}
    for name, item in rows.items():
        if (type(name) is not str or re.fullmatch(r"[A-Za-z0-9_-]+\.wav", name) is None or
                type(item) is not dict or
                set(item) != {"bytes", "git_blob_sha"} or
                type(item["bytes"]) is not int or item["bytes"] < 1 or
                type(item["git_blob_sha"]) is not str or
                re.fullmatch(r"[0-9a-f]{40}", item["git_blob_sha"]) is None):
            raise ProbeError("pinned_haptics_manifest_schema_drift")
        result[name] = item["bytes"]
    if sum(result.values()) != ORIGINAL_WAV_TOTAL_BYTES:
        raise ProbeError("pinned_haptics_manifest_schema_drift")
    return result


def classify_signed_obb_routes(archive, *, haptics, banks=BANK_SIZES):
    """Check the EXACT paths requested by AndroidStreamingAssets.ReadAllBytes.

    This is an indexed ZIP path/type/size parity assertion, not content SHA,
    Unity C++ asset mount, FMOD event playback or Android file permissions.
    """
    if type(haptics) is not dict or not haptics or type(banks) is not dict or not banks:
        raise ProbeError("resource_expectations_invalid")
    names = {}
    for member in archive.infolist():
        _safe_member(member.filename)
        if member.filename in names:
            raise ProbeError("signed_obb_duplicate_zip_member")
        names[member.filename] = member
    try:
        _verify_local_zip_headers(archive, archive.infolist())
    except Exception:
        raise ProbeError("signed_obb_local_header_inconclusive") from None
    if not names:
        raise ProbeError("signed_obb_empty")
    if any(not isinstance(k, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.bank", k) or
           type(v) is not int or not 1 <= v <= 128 * 1024 * 1024
           for k, v in banks.items()):
        raise ProbeError("resource_expectations_invalid")
    if any(not isinstance(k, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.wav", k) or
           type(v) is not int or not 1 <= v <= 128 * 1024 * 1024
           for k, v in haptics.items()):
        raise ProbeError("resource_expectations_invalid")

    def must_match(path, expected_bytes, category):
        entry = names.get(path)
        if entry is None:
            raise ProbeError(category + "_route_absent")
        if (entry.is_dir() or entry.file_size != expected_bytes or
                entry.flag_bits & 1 or
                entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
            raise ProbeError(category + "_route_size_or_encoding_drift")

    for name, size in banks.items():
        must_match("assets/" + name, size, "original_fmod_bank")
    for name, size in haptics.items():
        must_match("assets/Haptics/" + name, size, "original_haptics")

    haptic_rows = [
        x for x in names if x.startswith("assets/Haptics/") and x.lower().endswith(".wav")
    ]
    bank_rows = [
        x for x in names if x.startswith("assets/") and x.endswith(".bank")
    ]
    # Accidental duplicate/renamed WAV or bank shadows make path-based loading
    # ambiguous, even if the expected genuine member also exists.
    if (len(haptic_rows) != len(haptics) or len(bank_rows) != len(banks)):
        raise ProbeError("original_audio_extra_or_unexpected_routes")
    unity = [
        info for path, info in names.items()
        if path.startswith("assets/bin/Data/") and not info.is_dir()
    ]
    if not unity or not any(i.file_size > 0 for i in unity):
        raise ProbeError("original_unity_data_route_absent")
    for info in unity:
        if info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise ProbeError("original_unity_data_route_encoding_drift")

    bank_entries = [names["assets/" + k] for k in banks]
    wav_entries = [names["assets/Haptics/" + k] for k in haptics]
    return {
        "actual_inner_OBB_zip_member_count": len(names),
        "original_FMOD_bank_exact_runtime_jar_routes_present": len(bank_entries),
        "original_FMOD_bank_lengths_match_production_identity": True,
        "original_FMOD_bank_total_uncompressed_bytes": sum(e.file_size for e in bank_entries),
        "original_haptics_exact_runtime_jar_routes_present": len(wav_entries),
        "original_haptics_member_lengths_match_pinned_git_manifest": True,
        "original_haptics_total_uncompressed_bytes": sum(e.file_size for e in wav_entries),
        "original_Unity_data_folder_entries": len(unity),
        "original_Unity_data_largest_entry_over_Java_Int32_array": (
            max(i.file_size for i in unity) > 2_147_483_647
        ),
        "original_Unity_data_largest_entry_over_AndroidStreamingAssets_audio_bound": (
            max(i.file_size for i in unity) > 128 * 1024 * 1024
        ),
        "actual_obb_local_headers_match_central": True,
        "actual_audio_resource_contents_hashed_this_probe": False,
        "original_FMOD_events_played_on_phone_proven": False,
        "original_jar_URL_asset_read_on_phone_proven": False,
        "Unity_engine_OBB_mount_or_GUID_proven": False,
        "render_water_or_shader_game_ready": False,
    }


def inspect_original_checkpoint(parent, *, apk_size=ORIGINAL_APK_BYTES,
                                obb_size=ORIGINAL_OBB_BYTES, haptics=None,
                                banks=BANK_SIZES):
    """Create a bounded seekable subfile for exactly the signed main OBB."""
    if haptics is None:
        haptics = pinned_haptic_lengths()
    try:
        with zipfile.ZipFile(parent, "r", allowZip64=True) as wrapper:
            members = wrapper.infolist()
            if len(members) != 2:
                raise ProbeError("original_signed_checkpoint_member_drift")
            target = {}
            for item in members:
                _safe_member(item.filename)
                kind = _kind(item.filename)
                if kind not in ("apk", "obb") or kind in target:
                    raise ProbeError("original_signed_checkpoint_member_drift")
                target[kind] = item
            if set(target) != {"apk", "obb"} or (
                    target["apk"].file_size != apk_size or
                    target["obb"].file_size != obb_size):
                raise ProbeError("original_signed_checkpoint_member_drift")
            obb_start = stored_member_offset(parent, wrapper, target["obb"])
            with zipfile.ZipFile(MemberSliceIO(parent, obb_start, obb_size), "r") as obb:
                result = classify_signed_obb_routes(obb, haptics=haptics, banks=banks)
            return {
                "source_original_owner_tested_run": ORIGINAL_RUN,
                "source_original_commit": ORIGINAL_SHA,
                "source_original_signed_checkpoint_id": CHECKPOINT[0],
                "outer_signed_apk_member_basename_matches_delivery": target["apk"].filename.rsplit("/", 1)[-1] == SIGNED_APK,
                "outer_signed_obb_member_basename_matches_delivery": target["obb"].filename.rsplit("/", 1)[-1] == SIGNED_OBB,
                "full_actual_original_OBB_SHA_prior_CI": 42230326050,
                **result,
                "real_original_HTTP206_bytes": parent.transferred,
                "real_original_HTTP206_requests": parent.requests,
                "raw_game_bytes_logged_or_uploaded": False,
            }
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("original_signed_audio_routes_zip_inconclusive") from None


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--live", action="store_true")
    options = args.parse_args()
    if not options.live:
        args.error("Requires explicit --live to read original signed source")
    token = os.environ.get("GITHUB_TOKEN", "")
    if len(token) < 8:
        print("T5_SIGNED_OBB_ROUTES status=BLOCKED reason=github_token_missing")
        raise SystemExit(2)
    try:
        expected = pinned_haptic_lengths()
        private_url = pinned_artifact(CHECKPOINT, token)
        parent = LimitedRangeIO(
            CHECKPOINT[2], _http_range_fetcher(private_url, CHECKPOINT[2]),
            budget=MAX_HTTP_RANGE_BYTES)
        proof = inspect_original_checkpoint(parent, haptics=expected)
    except ProbeError as error:
        reason = str(error)
        accepted = {
            "github_token_missing", "artifact_metadata_changed", "artifact_run_drift",
            "pinned_haptics_manifest_unavailable", "pinned_haptics_manifest_schema_drift",
            "resource_expectations_invalid", "signed_obb_duplicate_zip_member",
            "signed_obb_local_header_inconclusive", "signed_obb_empty",
            "original_fmod_bank_route_absent",
            "original_fmod_bank_route_size_or_encoding_drift",
            "original_haptics_route_absent",
            "original_haptics_route_size_or_encoding_drift",
            "original_audio_extra_or_unexpected_routes",
            "original_unity_data_route_absent",
            "original_unity_data_route_encoding_drift",
            "original_signed_checkpoint_member_drift",
            "original_signed_audio_routes_zip_inconclusive",
            "archive_range_read_budget_exhausted",
        }
        print("T5_SIGNED_OBB_ROUTES status=BLOCKED reason=" +
              (reason if reason in accepted else "redacted_source_or_range_error"))
        raise SystemExit(2) from None
    except Exception:
        print("T5_SIGNED_OBB_ROUTES status=BLOCKED reason=unexpected_error_redacted")
        raise SystemExit(2) from None
    print("T5_SIGNED_OBB_ROUTES " + json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    main()
