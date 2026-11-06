"""Fail-closed, source-free admission for two FFT invocation-keyed traces.

This tool requires independently stored captures, matching declared dispatch and
input fingerprints, digest-bound trace bytes and complete expected site counts.
The metadata is an UNSIGNED PRODUCER DECLARATION, not source authentication.
A successful gate does NOT prove a Unity build used the claimed shader.
Never log binary contents, shader hashes, literal coordinates or sample values.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from scripts.t1_fft_trace_compare import (
    CAPACITY, INVOCATION_SIZE, compare_invocations, decode_invocations,
)

MAX_METADATA_BYTES = 8192
SCHEMA = "t1-fft-invocation-pair-v1"
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
CANDIDATE_ROLES = {"hlsl_roundtrip_spirv", "unity_compute_spirv"}
CAPTURE_FIELDS = {"role", "shader_sha256", "trace_sha256",
                  "input_sha256", "dispatch_sha256"}


def _json_no_duplicates(pairs):
    item = {}
    for key, value in pairs:
        if key in item:
            raise ValueError("duplicate manifest field")
        item[key] = value
    return item


def _hex(value):
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise ValueError("invalid declared SHA256")
    return value


def _read_manifest(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_METADATA_BYTES + 1)
    if len(data) > MAX_METADATA_BYTES:
        raise ValueError("paired metadata exceeds bounded size")
    manifest = json.loads(data.decode("utf-8"),
                          object_pairs_hook=_json_no_duplicates,
                          parse_constant=lambda x: (_ for _ in ()).throw(
                              ValueError("invalid JSON constant")))
    if not isinstance(manifest, dict) or set(manifest) != {
            "schema", "reference", "candidate", "expected_records_by_site"}:
        raise ValueError("unexpected pair manifest fields")
    if manifest["schema"] != SCHEMA:
        raise ValueError("unsupported paired trace schema")
    counts = manifest["expected_records_by_site"]
    if (not isinstance(counts, list) or len(counts) != 3
            or any(type(v) is not int or v <= 0 for v in counts)
            or sum(counts) > CAPACITY):
        raise ValueError("invalid declared site record coverage")
    for role, obj in (("reference", manifest["reference"]),
                      ("candidate", manifest["candidate"])):
        if not isinstance(obj, dict) or set(obj) != CAPTURE_FIELDS:
            raise ValueError("invalid capture provenance manifest")
        for name in CAPTURE_FIELDS - {"role"}:
            _hex(obj[name])
    reference, candidate = manifest["reference"], manifest["candidate"]
    if reference["role"] != "original_spirv":
        raise ValueError("invalid original source stage")
    if candidate["role"] not in CANDIDATE_ROLES:
        raise ValueError("invalid candidate stage")
    if (reference["input_sha256"] != candidate["input_sha256"] or
            reference["dispatch_sha256"] != candidate["dispatch_sha256"]):
        raise ValueError("mismatched declared input/dispatch provenance")
    return manifest


def _read_trace(path):
    with Path(path).open("rb") as stream:
        data = stream.read(INVOCATION_SIZE + 1)
    if len(data) != INVOCATION_SIZE:
        raise ValueError("invalid bounded invocation trace byte size")
    return data


def analyze(metadata_path, reference_path, candidate_path):
    manifest = _read_manifest(metadata_path)
    ref, candidate = Path(reference_path), Path(candidate_path)
    # samefile catches hardlinks and symlinks as well as identical paths.
    if ref.samefile(candidate):
        raise ValueError("identical underlying reference and candidate trace file")
    raw_reference, raw_candidate = _read_trace(ref), _read_trace(candidate)
    for raw, stage in ((raw_reference, manifest["reference"]),
                       (raw_candidate, manifest["candidate"])):
        if hashlib.sha256(raw).hexdigest() != stage["trace_sha256"]:
            raise ValueError("trace does not match declared digest")

    # Decode performs strict total-size, nonempty, site presence and duplicate
    # invocation checks; declarations are separately checked for exact counts.
    decoded = [decode_invocations(raw) for raw in
               (raw_reference, raw_candidate)]
    expected = manifest["expected_records_by_site"]
    for captures in decoded:
        if [len(s) for s in captures] != expected:
            raise ValueError("declared site coverage does not match trace")
    result = compare_invocations(raw_reference, raw_candidate)
    return {
        "status": "bounded_paired_invocation_comparison",
        "independent_trace_files_verified": True,
        "trace_digests_verified": True,
        "declared_input_and_dispatch_match": True,
        "declared_expected_site_counts_verified": True,
        "source_roles": ["original_spirv", manifest["candidate"]["role"]],
        "source_authenticity_verified_by_gate": False,
        "producer_manifest_is_unsigned": True,
        "comparison": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = analyze(args.manifest, args.original, args.candidate)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        parser.exit(2, "Invalid paired FFT invocation evidence\n")
    print("RAFT_T1_PAIRED_INVOCATION_GATE " + json.dumps(result, sort_keys=True))
    if not result["comparison"]["match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
