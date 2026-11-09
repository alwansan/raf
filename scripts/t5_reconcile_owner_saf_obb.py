#!/usr/bin/env python3
"""Read-only comparison: actual owner T5-02 SAF hash vs old, fully hashed v89 OBB.

The pinned old reference SHA prefix comes from verified CI42230326050.
A prefix+size agreement is NOT a full SHA, file location, or mount proof.
Do not print the observed full hash, device paths, or other case data.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

EXPECTED_PACKAGE = "com.alwansan.raft.androidtest"
REFERENCE_VERSION = "89"
REFERENCE_OBB_BYTES = 2301256312
REFERENCE_SHA_PREFIX = "660b6c0909ae"
MAX_SUMMARY = 256 * 1024
MAX_SELECTED_BYTES = 16 * 1024 ** 3
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
OBSERVED = re.compile(r"bytes=([1-9][0-9]*) sha256=([0-9a-f]{64})\Z")
SESSION = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,100}\Z")


class EvidenceError(ValueError):
    pass


def _unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise EvidenceError("duplicate_summary_json_key")
        value[key] = item
    return value


def _bad_constant(_):
    raise EvidenceError("nonstandard_json_constant")


def parse_summary(raw: bytes) -> dict:
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_SUMMARY:
        raise EvidenceError("summary_bytes_invalid")
    try:
        item = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=_bad_constant)
    except (UnicodeError, json.JSONDecodeError):
        raise EvidenceError("summary_json_invalid") from None
    if type(item) is not dict:
        raise EvidenceError("summary_not_object")
    return item


def reconcile(summary: dict, *, expected_session: str | None = None) -> dict:
    if type(summary) is not dict:
        raise EvidenceError("summary_not_object")
    session = summary.get("session")
    rows = summary.get("results")
    if (type(session) is not str or SESSION.fullmatch(session) is None or
            (expected_session is not None and session != expected_session) or
            type(rows) is not list or not 1 <= len(rows) <= 100):
        raise EvidenceError("invalid_session_or_cases")
    selected = [row for row in rows if type(row) is dict and row.get("case_id") == "T5-02"]
    if len(selected) != 1 or selected[0].get("worker") != "T5":
        raise EvidenceError("missing_or_duplicate_t5_case")
    record = selected[0].get("result")
    if type(record) is not dict or record.get("id") != "T5-02" or record.get("worker") != "T5":
        raise EvidenceError("case_result_identity_invalid")
    status = record.get("status")
    if status not in ("EVIDENCE_READY", "PASS", "USER_PASS", "NEEDS_INPUT",
                      "NEEDS_SCREENSHOT", "BLOCKED", "FAIL", "USER_FAIL"):
        raise EvidenceError("unknown_case_status")
    observed = record.get("observed")
    if type(observed) is not str or len(observed) > 2048:
        raise EvidenceError("observed_field_invalid")
    match = OBSERVED.fullmatch(observed)
    report = {
        "case_id": "T5-02",
        "owner_session": session,
        "source_cl_summary_requires_blob_authentication": True,
        "reference_build_version_code": REFERENCE_VERSION,
        "reference_package": EXPECTED_PACKAGE,
        "reference_obb_bytes": REFERENCE_OBB_BYTES,
        "reference_sha256_prefix_only": REFERENCE_SHA_PREFIX,
        "original_reference_full_sha_verified_in_prior_ci": True,
        "source_case_status": status,
        "phone_selected_file_name_recorded": False,
        "phone_selected_file_location_recorded": False,
        "installed_package_version_verified": False,
        "installed_obb_mount_verified": False,
        "phone_corruption_proven": False,
        "full_reference_sha256_equality_proven": False,
    }
    if match is None:
        if status in ("EVIDENCE_READY", "PASS", "USER_PASS"):
            raise EvidenceError("completed_case_has_no_valid_digest")
        report.update({"comparison": "NO_COMPLETED_DIGEST", "selected_file_bytes": None,
                       "selected_sha256_prefix": None, "byte_difference": None})
        return report
    size = int(match[1])
    if not 0 < size <= MAX_SELECTED_BYTES or SHA256.fullmatch(match[2]) is None:
        raise EvidenceError("selected_digest_out_of_bounds")
    prefix = match[2][:len(REFERENCE_SHA_PREFIX)]
    same_size = size == REFERENCE_OBB_BYTES
    same_prefix = prefix == REFERENCE_SHA_PREFIX
    report.update({
        "selected_file_bytes": size,
        "selected_sha256_prefix": prefix,
        "byte_difference": size - REFERENCE_OBB_BYTES,
        "size_matches_old_reference": same_size,
        "sha_prefix_matches_old_reference": same_prefix,
        "comparison": ("SIZE_AND_PREFIX_CONSISTENT_ONLY"
                       if same_size and same_prefix else "DIFFERENT_FROM_OLD_REFERENCE"),
    })
    # Even with matching size/prefix, a SAF-picked file need not be installed.
    return report


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--summary", type=Path, required=True)
    args.add_argument("--expected-session", required=True)
    options = args.parse_args()
    path = options.summary
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_SUMMARY:
        raise SystemExit("T5_OWNER_SAF_OBB status=BLOCKED reason=invalid_file")
    try:
        result = reconcile(parse_summary(path.read_bytes()), expected_session=options.expected_session)
    except EvidenceError as exc:
        print("T5_OWNER_SAF_OBB status=BLOCKED reason=" + str(exc))
        raise SystemExit(2) from None
    print("T5_OWNER_SAF_OBB " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
