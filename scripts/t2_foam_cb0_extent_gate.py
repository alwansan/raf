"""Fail-closed source-only Foam CB0 integration readiness gate.

Matching Vulkan descriptor coordinates/classes does not establish constant-buffer
member ABI or Unity material upload semantics. No private shader data is emitted.
"""


def cb0_integration_gate(shared_links, *, member_abi_verified=False,
                         unity_upload_verified=False, expected_pass_count=None):
    """Return a bounded verdict; never infer ABI from equal descriptor extents.

    shared_links is a list of per-pass summaries with integer VS/FS byte
    extents for the *same authenticated CB0 descriptor coordinate*.
    Missing, invalid, or mismatched extents are explicitly non-integrable.
    Set expected_pass_count from independently authenticated original pass count
    to prevent incomplete evidence from satisfying the gate. With an expected\n    count, each row must carry its authenticated zero-based pass_index;\n    duplicates and omissions cannot count as separate original passes.
    """
    if not isinstance(shared_links, list) or not shared_links:
        return {"status": "blocked_missing_authenticated_CB0_links"}
    if type(member_abi_verified) is not bool or type(unity_upload_verified) is not bool:
        return {"status": "blocked_invalid_evidence_flags"}
    if expected_pass_count is not None:
        if type(expected_pass_count) is not int or not 1 <= expected_pass_count <= 64:
            return {"status": "blocked_invalid_expected_pass_count"}
        if len(shared_links) != expected_pass_count:
            return {"status": "blocked_CB0_pass_coverage_mismatch",
                    "observed_pass_count": len(shared_links),
                    "expected_pass_count": expected_pass_count}
    mismatches = 0
    seen_passes = set()
    for row in shared_links:
        if not isinstance(row, dict) or set(row) != ({"vertex_bytes", "fragment_bytes", "authenticated_shared_coordinate"} | ({"pass_index"} if expected_pass_count is not None else set())):
            return {"status": "blocked_invalid_CB0_link"}
        if expected_pass_count is not None:
            index = row["pass_index"]
            if type(index) is not int or not 0 <= index < expected_pass_count:
                return {"status": "blocked_invalid_CB0_pass_identity"}
            if index in seen_passes:
                return {"status": "blocked_duplicate_CB0_pass_identity"}
            seen_passes.add(index)
        v, f = row["vertex_bytes"], row["fragment_bytes"]
        if (type(v) is not int or type(f) is not int or
                not 0 < v <= 65536 or not 0 < f <= 65536 or
                row["authenticated_shared_coordinate"] is not True):
            return {"status": "blocked_invalid_CB0_link"}
        mismatches += v != f
    if mismatches:
        return {"status": "blocked_CB0_byte_extent_mismatch",
                "mismatched_pass_count": mismatches}
    if not member_abi_verified:
        return {"status": "blocked_CB0_member_ABI_unverified"}
    if not unity_upload_verified:
        return {"status": "blocked_Unity_CB0_upload_unverified"}
    return {"status": "source_gate_satisfied_not_Unity_or_device_verified"}
