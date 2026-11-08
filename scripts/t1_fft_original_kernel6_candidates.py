#!/usr/bin/env python3
"""Classify source-only numeric FFT index-6 cases from authentic Raft managed C#.

Do NOT identify Unity runtime kernel id 6 with serialized compiled program #6.
The input decompiled original source, names, expressions and DLL stay private.
"""
import argparse
import json
from pathlib import Path

from scripts.probe_original_fft_kernel_callsites import analyze_source, sha
from scripts.probe_original_fft_inherited_seed import prove, BASE_SHA256
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256

DERIVED_SHA256 = ORIGINAL_SOURCE_SHA256["Dx11FFT"]
MIN_N, MAX_N = 5, 9
MAX_PRIVATE_TEXT = 700_000


def compatible_source_numeric_cases(index):
    """Invert the original proven selector for integer exponent examples ONLY.

    The actual runtime uses Mathf float log/truncate; no device floating-point
    result, caller resolution, or Unity FindKernel ID is inferred here.
    """
    if type(index) is not int or not (0 <= index < 20):
        raise ValueError("reported kernel index outside original candidate selector domain")
    matches = []
    for n in range(MIN_N, MAX_N + 1):
        for bank in (0, 1):
            base = ((n - 5) << 1) + bank * 10
            for pass_offset in (0, 1):
                if index == base + pass_offset:
                    matches.append({
                        "assumed_power_of_two_size": 1 << n,
                        "assumed_bank_flag": bank,
                        "source_pass_offset": pass_offset,
                        "source_numeric_argument": index,
                    })
    if len(matches) != 1:
        # This should never happen for exact 20-candidate source formula.
        raise ValueError("ambiguous or missing source numeric selector case")
    return matches


def audit_sources(derived, inherited, derived_hash=DERIVED_SHA256,
                  inherited_hash=BASE_SHA256, observed_index=6):
    if (not isinstance(derived, str) or not isinstance(inherited, str)
            or len(derived) > MAX_PRIVATE_TEXT or len(inherited) > MAX_PRIVATE_TEXT
            or sha(derived) != derived_hash or sha(inherited) != inherited_hash):
        raise ValueError("original private managed CSharp SHA mismatch")
    proof = prove(derived, inherited, derived_hash, inherited_hash)
    if not proof["inherited_seed_dataflow_verified"]:
        raise ValueError("original inherited kernel selector seed not proven")
    if proof["first_pass_source_selector"] != "((n-5)<<1) + (fourth_bool ? 10 : 0)":
        raise ValueError("original selector expression shape changed")
    if proof["second_pass_relative_offset"] != 1:
        raise ValueError("original second FFT pass must use adjacent index")

    calls = analyze_source(derived, derived_hash)
    rows = calls["compute_api_callsites"]
    dispatch = [row for row in rows if row["call_kind"] == "Dispatch"]
    textures = [row for row in rows if row["call_kind"] == "SetTexture"]
    if len(dispatch) != 2 or len(textures) != 6:
        raise ValueError("original FFT two Dispatch / six SetTexture callsites changed")
    if ([row["kernel_index_affine_offset_from_first_dispatch"] for row in dispatch]
            != [0, 1]):
        raise ValueError("original first/second Dispatch relative selector changed")
    if sorted(row["kernel_index_affine_offset_from_first_dispatch"] for row in textures) != [0, 0, 0, 1, 1, 1]:
        raise ValueError("original SetTexture selector offsets no longer match two passes")
    receivers = {row["receiver_identifier_sha256"] for row in dispatch + textures}
    if len(receivers) != 1 or None in receivers:
        raise ValueError("original compute receiver identity no longer structurally stable")
    for row in dispatch:
        if row["argument_count"] != 4:
            raise ValueError("original Dispatch call argument count changed")
    source_cases = compatible_source_numeric_cases(observed_index)

    return {
        "schema_version": 1,
        "original_derived_source_sha256_verified": derived_hash,
        "original_inherited_source_sha256_verified": inherited_hash,
        "derived_source_authenticated": True,
        "inherited_seed_dataflow_verified": True,
        "selector_expression_proven": "(n-5)<<1 + (bank?10:0) + pass_offset",
        "source_integer_exponent_case_only": True,
        "source_numeric_index_checked": observed_index,
        "compatible_source_numeric_cases": source_cases,
        "source_dispatch_calls": len(dispatch),
        "source_settexture_calls": len(textures),
        "source_two_pass_affine_offsets": [0, 1],
        "source_shader_receiver_sha_only_consistent": True,
        "original_source_findkernel_call_count_in_Dx11FFT": calls["calls_by_api"].get("FindKernel", 0),
        "actual_original_resolution_or_bank_at_error_observed": False,
        "actual_Unity_Mathf_log_float_result_on_device_observed": False,
        "Unity_FindKernel_runtime_id_mapped": False,
        "original_serialized_compiled_slot_index_mapped_to_runtime_id": False,
        "same_ComputeShader_asset_at_owner_error_verified": False,
        "Android_GLES_or_Vulkan_dispatch_executed": False,
        "original_source_code_or_private_names_exported": False,
        "FFT_water_rendering_fixed": False,
    }


def _read_pinned(root, stem, expected):
    matches = list(root.rglob(stem + ".cs"))
    if (len(matches) != 1 or matches[0].is_symlink() or
            not matches[0].is_file() or matches[0].stat().st_size > MAX_PRIVATE_TEXT * 4):
        raise ValueError("original private CSharp file missing/ambiguous")
    private = matches[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if len(private) > MAX_PRIVATE_TEXT or sha(private) != expected:
        raise ValueError("original private CSharp file SHA mismatch")
    return private


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-managed", required=True, type=Path)
    p.add_argument("--reported-index", default=6, type=int)
    a = p.parse_args()
    try:
        derived = _read_pinned(a.original_managed, "Dx11FFT", DERIVED_SHA256)
        inherited = _read_pinned(a.original_managed, "GpuFFT", BASE_SHA256)
        report = audit_sources(derived, inherited, observed_index=a.reported_index)
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        p.exit(2, "T1 original FFT numeric index evidence rejected: " +
               type(exc).__name__ + "\n")
    print("RAFT_T1_AUTHENTIC_FFT_NUMERIC_INDEX_CANDIDATES " +
          json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
