"""Publish only bounded NUnit counts from a private GameCI Unity test run.

Do not print the Unity log, XML body, failures, compiler diagnostics, private
shader names, real DXBC, SPIR-V, HLSL or pixel data.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

KNOWN = {
    "synthetic": frozenset({
        "T1SourceFreeEditorTest.ExpectedEditorMajorVersionIs2021",
        "T1SourceFreeEditorTest.SyntheticComputeAssetImportsWithoutOriginalRaftData",
    }),
    "original_derived": frozenset({
        "T1PrivateFftImportTests.VerifiedTwentyOriginalDerivedCandidatesImportInUnity",
    }),
}
MAX_XML = 1024 * 1024


def classify(xml_bytes: bytes, exit_code: int, stage: str) -> dict:
    if stage not in KNOWN or type(exit_code) is not int:
        raise ValueError("Unknown GameCI stage/return code")
    if not isinstance(xml_bytes, bytes) or not 0 < len(xml_bytes) <= MAX_XML:
        raise ValueError("Missing or unbounded private test results")
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError("Invalid private NUnit XML") from None
    if root.tag != "test-run":
        raise ValueError("Unexpected test result root")
    expected = KNOWN[stage]
    try:
        numeric = {k: int(root.attrib[k]) for k in (
            "total", "passed", "failed", "skipped", "inconclusive", "testcasecount")}
    except (KeyError, ValueError, TypeError):
        raise ValueError("Malformed private NUnit counts") from None
    if any(n < 0 or n > 500 for n in numeric.values()):
        raise ValueError("Unbounded private test result counters")
    tests = root.findall(".//test-case")
    identifiers = [t.attrib.get("fullname") for t in tests]
    authentic = (len(tests) == len(expected) and
                 set(identifiers) == expected and
                 len(set(identifiers)) == len(tests))
    passed = (exit_code == 0 and authentic and
              numeric["total"] == numeric["testcasecount"] == len(expected) and
              numeric["passed"] == len(expected) and
              numeric["failed"] == numeric["skipped"] == numeric["inconclusive"] == 0 and
              root.attrib.get("result") == "Passed" and
              all(t.attrib.get("result") == "Passed" for t in tests))
    return {
        "stage": stage,
        "private_result_xml_parsed": True,
        "source_free_or_pinned_original_scope": stage,
        "expected_test_case_count": len(expected),
        "observed_test_case_count": len(tests),
        "passed_count": numeric["passed"],
        "failed_count": numeric["failed"],
        "skipped_count": numeric["skipped"],
        "all_expected_tests_passed": passed,
        "synthetic_unity_compute_test_verified": stage == "synthetic" and passed,
        "original_derived_twenty_compute_import_groups_verified": stage == "original_derived" and passed,
        "original_authored_compute_source_restored": False,
        "original_runtime_kernel_identity_mapping_proven": False,
        "android_adreno_or_water_pixels_proven": False,
        "private_compiler_logs_or_shader_contents_disclosed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--stage", required=True, choices=sorted(KNOWN))
    parser.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()
    if args.result.is_symlink() or not args.result.is_file() or args.result.stat().st_size > MAX_XML:
        raise SystemExit("RAFT_T1_GAMECI_PRIVATE_RESULT invalid_result_file=true")
    try:
        value = classify(args.result.read_bytes(), args.exit_code, args.stage)
    except (ValueError, OSError):
        raise SystemExit("RAFT_T1_GAMECI_PRIVATE_RESULT invalid_nunit_report=true") from None
    print("RAFT_T1_GAMECI_PRIVATE_RESULT " + json.dumps(value, sort_keys=True))
    if not value["all_expected_tests_passed"]:
        raise SystemExit("Original-free or original-derived Unity pass gate not met")


if __name__ == "__main__":
    main()
