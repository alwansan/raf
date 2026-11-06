"""Fail-closed, source-free attestation for the pinned original MonoScript join.

This checks only a tiny aggregate JSON result. It does not verify raw asset
SHA by itself, reconstruct original fields, or establish Foam runtime binding.
It MUST run after the SHA-authentic original-source job has produced the JSON.
No private strings/identifiers are accepted or echoed.
"""
import argparse
import json
from pathlib import Path

EXPECTED_COUNTS = {
    "original_scene_SHA_authenticated_file_count": 40,
    "original_scene_SHA_authenticated_bytes": 233237972,
    "script_refs_from_opaque_original_MonoBehaviours": 55328,
    "source_external_path_variants": 1,
    "original_unique_basename_candidate_ref_rows": 55328,
    "original_missing_manifest_candidate_ref_rows": 0,
    "original_ambiguous_manifest_candidate_ref_rows": 0,
    "original_unique_manifest_candidate_target_files": 1,
    "source_target_rows_budget_skipped": 0,
    "original_typed_target_files_SHA_staged": 1,
    "original_typed_target_bytes_SHA_staged": 758412,
    "original_opaque_m_Script_rows_typed_target_checked": 55328,
    "script_refs_to_SHA_original_typed_MonoScript_objects": 55328,
    "script_refs_to_SHA_original_absent_or_other_type_PathIDs": 0,
    "sum_per_original_provider_distinct_typed_MonoScript_targets": 473,
    "sum_per_original_provider_distinct_non_MonoScript_targets": 0,
}
EXPECTED_FLAGS = {
    "original_zip2_SHA_authenticated": True,
    "original_MonoScript_source_TypeName_published": False,
    "source_external_basename_proves_Unity_GUID": False,
    "original_MonoScript_field_layout_reconstructed": False,
    "original_Foam_Runtime_Shader_binding_verified": False,
    "Android_water_pixels_verified": False,
    "private_original_script_object_ids_paths_or_hashes_exported": False,
}
EXPECTED_STATUS = "source_original_opaque_m_Script_target_type_join"
EXPECTED_KEYS = frozenset(EXPECTED_COUNTS) | frozenset(EXPECTED_FLAGS) | {"status"}


def validate_safe_report(report):
    """Enforce complete positive typed coverage, exact known source scope and privacy.

    Immutable source is ZIP2@15964ea8... and the upstream workflow verifies SHA.
    A passing synthetic JSON is NOT independently authenticated source evidence.
    """
    if type(report) is not dict or set(report) != EXPECTED_KEYS:
        raise ValueError("safe_attestation_unknown_or_missing_fields")
    if type(report["status"]) is not str or report["status"] != EXPECTED_STATUS:
        raise ValueError("safe_attestation_wrong_stage")
    for key, value in EXPECTED_COUNTS.items():
        if type(report[key]) is not int or report[key] != value:
            raise ValueError("safe_attestation_wrong_count")
    for key, value in EXPECTED_FLAGS.items():
        if type(report[key]) is not bool or report[key] is not value:
            raise ValueError("safe_attestation_wrong_flag")
    # Separate semantic checks prevent a future change to pinned counts from
    # silently weakening positive-coverage requirements.
    refs = report["script_refs_from_opaque_original_MonoBehaviours"]
    checked = report["original_opaque_m_Script_rows_typed_target_checked"]
    typed = report["script_refs_to_SHA_original_typed_MonoScript_objects"]
    if (refs <= 0 or checked <= 0 or typed <= 0 or
            checked != refs or typed != checked or
            report["source_target_rows_budget_skipped"] != 0 or
            report["original_missing_manifest_candidate_ref_rows"] != 0 or
            report["original_ambiguous_manifest_candidate_ref_rows"] != 0 or
            report["script_refs_to_SHA_original_absent_or_other_type_PathIDs"] != 0 or
            report["original_typed_target_files_SHA_staged"] <= 0 or
            report["original_typed_target_bytes_SHA_staged"] <= 0):
        raise ValueError("safe_attestation_no_full_positive_proof")
    return checked


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("safe_attestation_duplicate_json_key")
        result[key] = value
    return result


def parse_safe_json(text):
    if type(text) is not str or len(text.encode("utf-8")) > 16384:
        raise ValueError("safe_attestation_json_size")
    return json.loads(text, object_pairs_hook=_unique_keys)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        path = args.input
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size > 16384):
            raise ValueError("safe_attestation_untrusted_file")
        report = parse_safe_json(path.read_text(encoding="utf-8"))
        checked = validate_safe_report(report)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
        # No untrusted JSON, raw source, filenames or private identifiers emitted.
        print("T2_MONOSCRIPT_POSITIVE_ATTESTATION_FAIL")
        return 2
    print(f"T2_MONOSCRIPT_POSITIVE_ATTESTATION_PASS checked={checked} typed={checked} skipped=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
