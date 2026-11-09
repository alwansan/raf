#!/usr/bin/env python3
"""Validate *source-numeric* Dx11FFT Dispatch observations, NOT Unity kernel lookup proof.

Authentic managed Dx11FFT had two direct integer Dispatch callsites, six
SetTexture callsites, and no FindKernel callsite (CI 42519853981).
A named FindKernel proof gate must not be substituted for this contract.
Every incoming record remains untrusted metadata until independently attested
to a specific native build/device; this gate only checks shape and arithmetic.
"""
import argparse
import json
import re
from pathlib import Path

ORIGINAL_DLL_BLOB_SHA1 = "fc9d4ba920a178fdb89c970d9d772a01051dadc6"
ORIGINAL_DX11FFT_CSHARP9_SHA256 = "8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
MAX_BYTES = 1024 * 1024
ROW_FIELDS = {
    "event_id", "event_timestamp_ms", "caller", "dispatch_origin",
    "fft_size", "mathf_log2_truncated", "bank_flag", "pass_offset",
    "source_numeric_kernel_arg", "dispatch_kernel_arg",
    "compute_shader_present", "supports_compute",
    "groups", "binding_names",
}
ENVELOPE_FIELDS = {
    "schema_version", "build_sha", "device_session",
    "original_dll_blob_sha1", "original_dx11fft_source_sha256",
    "reported_invalid_kernel_index", "correlated_event_id", "dispatches",
}


def _safe_name(value, limit=128):
    return (
        isinstance(value, str) and 1 <= len(value) <= limit
        and value == value.strip() and bool(value.strip())
        and all(ord(ch) >= 32 and not 127 <= ord(ch) <= 159 for ch in value)
    )


def _int(value, minimum, maximum):
    return type(value) is int and minimum <= value <= maximum


def _no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate key in FFT runtime evidence")
        obj[key] = value
    return obj


def validate(record):
    if not isinstance(record, dict) or set(record) != ENVELOPE_FIELDS:
        raise ValueError("direct dispatch evidence envelope invalid")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValueError("unknown direct dispatch evidence schema")
    if not isinstance(record["build_sha"], str) or not SHA40.fullmatch(record["build_sha"]):
        raise ValueError("immutable build SHA absent")
    if not _safe_name(record["device_session"]):
        raise ValueError("unusable device session")
    if record["original_dll_blob_sha1"] != ORIGINAL_DLL_BLOB_SHA1:
        raise ValueError("original managed DLL SHA mismatch")
    if record["original_dx11fft_source_sha256"] != ORIGINAL_DX11FFT_CSHARP9_SHA256:
        raise ValueError("original Dx11FFT source SHA mismatch")
    reported = record["reported_invalid_kernel_index"]
    if reported is not None and not _int(reported, -(2 ** 31), 2 ** 31 - 1):
        raise ValueError("reported invalid index not an integer")
    correlated = record["correlated_event_id"]
    if correlated is not None and (reported is None or not _safe_name(correlated)):
        raise ValueError("correlation requires a reported error and event ID")
    rows = record["dispatches"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 128:
        raise ValueError("bounded direct dispatch observations required")

    events = {}
    last_ms = -1
    selector_mismatches = 0
    dispatch_mismatches = 0
    out_of_candidate_domain = 0
    size_exponent_disagreements = 0
    incomplete_bindings = 0
    for position, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != ROW_FIELDS:
            raise ValueError(f"observation {position}: missing or extra fields")
        event = row["event_id"]
        if not _safe_name(event) or event in events:
            raise ValueError(f"observation {position}: duplicate/invalid event ID")
        ms = row["event_timestamp_ms"]
        if not _int(ms, 0, 2 ** 63 - 1) or ms < last_ms:
            raise ValueError(f"observation {position}: invalid event time ordering")
        last_ms = ms
        if row["caller"] != "Dx11FFT" or row["dispatch_origin"] != "direct_numeric_argument":
            raise ValueError(f"observation {position}: non-original numeric caller")
        size = row["fft_size"]
        exponent = row["mathf_log2_truncated"]
        if not _int(size, 1, 4096) or size & (size - 1):
            raise ValueError(f"observation {position}: invalid FFT size")
        if not _int(exponent, 0, 16):
            raise ValueError(f"observation {position}: invalid observed log exponent")
        if type(row["bank_flag"]) is not bool or not _int(row["pass_offset"], 0, 1):
            raise ValueError(f"observation {position}: invalid bank or pass")
        for key in ("source_numeric_kernel_arg", "dispatch_kernel_arg"):
            if not _int(row[key], -(2 ** 31), 2 ** 31 - 1):
                raise ValueError(f"observation {position}: invalid {key}")
        for key in ("compute_shader_present", "supports_compute"):
            if type(row[key]) is not bool:
                raise ValueError(f"observation {position}: invalid {key}")
        groups = row["groups"]
        if (not isinstance(groups, list) or len(groups) != 3 or
                any(not _int(v, 0, 2 ** 20) for v in groups)):
            raise ValueError(f"observation {position}: invalid dispatch group counts")
        bindings = row["binding_names"]
        if (not isinstance(bindings, list) or len(bindings) > 32 or
                any(not _safe_name(b) for b in bindings) or
                len(bindings) != len(set(bindings))):
            raise ValueError(f"observation {position}: invalid binding names")
        if not bindings:
            incomplete_bindings += 1

        # Keep original source's *observed Mathf integer exponent* separate
        # from the declared FFT size; floating-point/runtime math may diverge.
        expected_arg = ((exponent - 5) << 1) + (10 if row["bank_flag"] else 0) + row["pass_offset"]
        selector_mismatches += expected_arg != row["source_numeric_kernel_arg"]
        dispatch_mismatches += row["source_numeric_kernel_arg"] != row["dispatch_kernel_arg"]
        out_of_candidate_domain += not (5 <= exponent <= 9)
        size_exponent_disagreements += size.bit_length() - 1 != exponent
        # The event-index match alone does NOT prove original source arithmetic.
        # Preserve the claimed row's own selector/domain/precondition predicates
        # so a mismatched or unsupported dispatch can never be called consistent.
        events[event] = {
            "dispatch_index": row["dispatch_kernel_arg"],
            "selector_consistent": (
                row["source_numeric_kernel_arg"] == expected_arg
                and row["source_numeric_kernel_arg"] == row["dispatch_kernel_arg"]
            ),
            "source_context_consistent": (
                5 <= exponent <= 9 and size.bit_length() - 1 == exponent
            ),
            "dispatch_preconditions": (
                row["compute_shader_present"] and row["supports_compute"]
                and all(group > 0 for group in groups) and bool(bindings)
            ),
        }

    correlated_selector_consistent = False
    if correlated is None:
        correlation = "unattributed"
    elif correlated not in events:
        raise ValueError("referenced error event was not captured")
    else:
        entry = events[correlated]
        correlated_selector_consistent = (
            entry["selector_consistent"] and entry["source_context_consistent"]
        )
        if entry["dispatch_index"] != reported:
            correlation = "same_event_index_disagreement"
        elif not entry["selector_consistent"]:
            correlation = "same_event_number_matches_but_source_selector_mismatch"
        elif not entry["source_context_consistent"]:
            correlation = "same_event_number_matches_but_source_context_unverified"
        elif not entry["dispatch_preconditions"]:
            correlation = "same_event_number_matches_but_dispatch_preconditions_unverified"
        else:
            correlation = "same_event_numeric_argument_match_only"

    # NEVER elevate source arithmetic or a caller-supplied correlation ID to
    # original Unity imported-program identity / on-device shader success.
    return {
        "source_numeric_direct_dispatch_record_schema_valid": True,
        "dispatch_observations": len(rows),
        "source_selector_mismatch_count": selector_mismatches,
        "source_to_dispatch_mismatch_count": dispatch_mismatches,
        "outside_original_twenty_candidate_domain_count": out_of_candidate_domain,
        "fft_size_observed_exponent_disagreement_count": size_exponent_disagreements,
        "observations_without_binding_names": incomplete_bindings,
        "reported_error_correlation": correlation,
        "correlated_event_source_selector_consistent": correlated_selector_consistent,
        "correlated_event_numerical_match_is_runtime_identity_proof": False,
        "actual_runtime_trace_independently_attested": False,
        "named_unity_kernel_mapping_proven": False,
        "android_water_rendering_fixed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sanitized_private_trace", type=Path)
    args = p.parse_args()
    try:
        trace = args.sanitized_private_trace
        if trace.is_symlink() or not trace.is_file() or trace.stat().st_size > MAX_BYTES:
            raise ValueError("invalid private trace file or unsafe size")
        data = json.loads(trace.read_text(encoding="utf-8"),
                          object_pairs_hook=_no_duplicate_keys)
        print(json.dumps(validate(data), sort_keys=True))
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        p.exit(2, "Direct FFT evidence incomplete: " + type(exc).__name__ + "\n")


if __name__ == "__main__":
    main()
