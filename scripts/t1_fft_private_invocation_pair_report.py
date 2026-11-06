"""Private evidence gate for *two actual* FFT Vulkan invocation trace buffers.

Input bytes are attested by actual source/butterfly readback SHA256 from each
host run; dispatch SHA256 is computed from one fixed canonical specification.
The source shader/trace/input hashes remain PRIVATE (never printed). Matching
keyed samples prove only this same-Mesa-Vulkan fixture, not Unity/Adreno.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from scripts.t1_fft_invocation_pair_gate import (
    analyze as strict_pair, SCHEMA as PAIR_SCHEMA
)
from scripts.t1_fft_private_input_evidence import SCHEMA as EVIDENCE_SCHEMA
from scripts.t1_fft_trace_compare import CAPACITY

MAX_METADATA = 4096
HEX = set("0123456789abcdef")


def _no_duplicate(fields):
    result = {}
    for key, value in fields:
        if key in result:
            raise ValueError("Duplicate private evidence key")
        result[key] = value
    return result


def _read(path):
    with Path(path).open("rb") as stream:
        buffer = stream.read(MAX_METADATA + 1)
    if len(buffer) > MAX_METADATA:
        raise ValueError("Oversized private evidence")
    return json.loads(buffer.decode("utf-8"), object_pairs_hook=_no_duplicate)


def _sha(value):
    if not isinstance(value, str) or len(value) != 64 or any(x not in HEX for x in value):
        raise ValueError("Private SHA256 syntax invalid")
    return value


def _contract(path, expected):
    obj = _read(path)
    if not isinstance(obj, dict) or set(obj) != {
            "schema", "stage", "input_sha256", "dispatch_sha256",
            "shader_sha256", "trace_sha256", "records_by_site"}:
        raise ValueError("Private input evidence schema invalid")
    if obj["schema"] != EVIDENCE_SCHEMA or obj["stage"] != expected:
        raise ValueError("Private shader producer stage unproven")
    for name in ("input_sha256", "dispatch_sha256", "shader_sha256", "trace_sha256"):
        _sha(obj[name])
    counts = obj["records_by_site"]
    if not isinstance(counts, list) or len(counts) != 3 or (
            any(type(x) is not int or x <= 0 for x in counts)
            or sum(counts) > CAPACITY):
        raise ValueError("Private trace site census unproven")
    return obj


def analyze(original_trace, candidate_trace, original_evidence, candidate_evidence):
    original = _contract(original_evidence, "original_spirv")
    translated = _contract(candidate_evidence, "hlsl_roundtrip_spirv")
    if original["input_sha256"] != translated["input_sha256"]:
        raise ValueError("Actual source/butterfly GPU input bytes differ")
    if original["dispatch_sha256"] != translated["dispatch_sha256"]:
        raise ValueError("Original and translated shader dispatch config differs")
    if original["records_by_site"] != translated["records_by_site"]:
        raise ValueError("Actual original/candidate site coverage differs")

    manifest = {
        "schema": PAIR_SCHEMA,
        "expected_records_by_site": original["records_by_site"],
        "reference": {name: original[name] for name in
                      ("input_sha256", "dispatch_sha256", "shader_sha256", "trace_sha256")},
        "candidate": {name: translated[name] for name in
                      ("input_sha256", "dispatch_sha256", "shader_sha256", "trace_sha256")},
    }
    manifest["reference"]["role"] = "original_spirv"
    manifest["candidate"]["role"] = "hlsl_roundtrip_spirv"
    # The strict gate verifies distinct physical files, their actual SHA,
    # exact size and unique invocation records in addition to the contracts.
    with tempfile.TemporaryDirectory(prefix="t1-pair-private-") as d:
        p = Path(d) / "manifest.json"
        p.write_text(json.dumps(manifest), encoding="utf-8")
        result = strict_pair(p, original_trace, candidate_trace)
    return {
        "status": "original_spirv_vs_hlsl_actual_keyed_vulkan_comparison",
        "original_and_candidate_distinct_captures_verified": True,
        "actual_GPU_input_bytes_match": True,
        "same_dispatch_configuration_verified": True,
        "trace_byte_SHA_and_site_keys_verified": True,
        "by_site_expected_reads": original["records_by_site"],
        "same_vulkan_fixture_numeric_match": result["comparison"]["match"],
        "site_comparison": result["comparison"]["sites"],
        "independent_source_authenticity_verified_by_manifest": False,
        "authored_Unity_kernel_runtime_identity_proven": False,
        "android_water_Adreno_proven": False,
        "private_hashes_invocation_coordinates_or_values_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-trace", type=Path, required=True)
    p.add_argument("--candidate-trace", type=Path, required=True)
    p.add_argument("--original-evidence", type=Path, required=True)
    p.add_argument("--candidate-evidence", type=Path, required=True)
    args = p.parse_args()
    try:
        result = analyze(args.original_trace, args.candidate_trace,
                         args.original_evidence, args.candidate_evidence)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "Invalid private original-and-candidate FFT same-input evidence\n")
    # Mismatch is a VALID diagnostic result, not a CI failure.
    print("RAFT_T1_ACTUAL_PAIRED_FFT_KEYED " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
