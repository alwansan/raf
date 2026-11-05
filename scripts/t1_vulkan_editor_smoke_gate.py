"""Fail-closed bounded NUnit verdict for a source-free Unity Vulkan compute smoke.

No Unity log or test-case failure body is ever echoed. A green Gate proves
only exact Vulkan Editor backend plus one generated 64-pixel compute workload
because the additional real NUnit assertion enforces graphicsDeviceType.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

EXPECTED = frozenset({
    "T1SourceFreeEditorTest.ExpectedEditorMajorVersionIs2021",
    "T1SourceFreeEditorTest.SyntheticComputeAssetImportsWithoutOriginalRaftData",
    "T1SourceFreeVulkanBackendTests.ActuallyUsesVulkanAndRunsSyntheticCompute",
})
MAX_XML_BYTES = 1_048_576


def evaluate(blob: bytes, editor_exit: int) -> dict:
    if type(blob) is not bytes or not 0 < len(blob) <= MAX_XML_BYTES:
        raise ValueError("Missing or excessive private synthetic NUnit XML")
    if type(editor_exit) is not int or editor_exit < 0 or editor_exit > 255:
        raise ValueError("Unknown Unity process exit code")
    try:
        root = ET.fromstring(blob)
    except ET.ParseError:
        raise ValueError("Malformed private NUnit results") from None
    if root.tag != "test-run":
        raise ValueError("Unexpected private NUnit root")
    try:
        numeric = {k: int(root.attrib[k]) for k in
                   ("total", "testcasecount", "passed", "failed", "skipped", "inconclusive")}
    except (ValueError, KeyError, TypeError):
        raise ValueError("Missing or invalid NUnit counters") from None
    if any(v < 0 or v > 100 for v in numeric.values()):
        raise ValueError("Unbounded private NUnit counts")
    cases = root.findall(".//test-case")
    names = [case.attrib.get("fullname") for case in cases]
    exact = len(cases) == len(EXPECTED) and len(set(names)) == len(EXPECTED) and set(names) == EXPECTED
    passed = (editor_exit == 0 and exact and root.attrib.get("result") == "Passed"
              and numeric == {"total": 3, "testcasecount": 3,
                              "passed": 3, "failed": 0, "skipped": 0, "inconclusive": 0}
              and all(case.attrib.get("result") == "Passed" for case in cases))
    return {
        "source_free": True,
        "exact_unity2021_nunit_cases": exact,
        "reported_case_count": len(cases),
        "passed_count": numeric["passed"],
        "failed_count": numeric["failed"],
        "vulkan_editor_backend_and_synthetic_gpu_dispatch_verified": passed,
        "synthetic_expected_float_texels_checked": 64 if passed else 0,
        "original_raft_data_acquired": False,
        "original_fft_numeric_parity_proven": False,
        "android_adreno_or_water_render_proven": False,
        "private_log_or_test_failure_text_disclosed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xml", required=True, type=Path)
    p.add_argument("--editor-exit", required=True, type=int)
    a = p.parse_args()
    if a.xml.is_symlink() or not a.xml.is_file() or a.xml.stat().st_size > MAX_XML_BYTES:
        raise SystemExit("RAFT_T1_UNITY_VULKAN_SOURCEFREE invalid_or_missing_test_report=true")
    try:
        verdict = evaluate(a.xml.read_bytes(), a.editor_exit)
    except (ValueError, OSError):
        raise SystemExit("RAFT_T1_UNITY_VULKAN_SOURCEFREE bounded_nunit_parser_rejected=true") from None
    print("RAFT_T1_UNITY_VULKAN_SOURCEFREE " + json.dumps(verdict, sort_keys=True))
    if not verdict["vulkan_editor_backend_and_synthetic_gpu_dispatch_verified"]:
        raise SystemExit("Unity 2021 Vulkan backend/compute readiness not verified")


if __name__ == "__main__":
    main()
