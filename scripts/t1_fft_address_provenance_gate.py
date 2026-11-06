"""Fail-closed evidence gate for the 16-category T1 Unity address-provenance carrier canary.

The counts are synthetic, source-free test measurements, not evidence of the
original Raft FFT shader or Android/Adreno behavior. Never publish Unity XML,
compiler logs, per-invocation data, private shader names or pixel values.
"""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

CASE = "T1FftAddressProvenanceTests.ComputedMaskedAndBufferLoadedFloatAddressContextsShareOneDispatch"
MAX_XML = 1024 * 1024
MAX_METRICS = 64
N = 16
CONTROLS = (0, 1, 8, 9, 14, 15)
COMPUTED = (2, 4, 6, 10, 12)
STAGED = (3, 5, 7, 11, 13)
PAIR_NAMES = ("bitcast", "plain_multiply", "precise_multiply", "texture_from_bitcast", "texture_from_precise")
# Exactly sixteen lines of unsigned integers 0..64; one final newline allowed.
_VALUE = rb"(?:0|[1-9]|[1-5][0-9]|6[0-4])"
_REPORT = re.compile(_VALUE + (rb"\n" + _VALUE) * (N - 1) + rb"\n?\Z")


def parse_metrics(payload: bytes) -> tuple[int, ...]:
    if type(payload) is not bytes or not 0 < len(payload) <= MAX_METRICS:
        raise ValueError("Missing or unbounded address provenance metric report")
    if _REPORT.fullmatch(payload) is None:
        raise ValueError("Wrong address provenance metric count or encoding")
    counts = tuple(map(int, payload.split()))
    if len(counts) != N:
        raise ValueError("Wrong address provenance category count")
    return counts


def require_unity_pass(blob: bytes, exit_code: int) -> None:
    if type(blob) is not bytes or not 0 < len(blob) <= MAX_XML:
        raise ValueError("Missing or unbounded Unity NUnit report")
    if type(exit_code) is not int or exit_code != 0:
        raise ValueError("Unity process did not complete successfully")
    if b"<!DOCTYPE" in blob.upper() or b"<!ENTITY" in blob.upper():
        raise ValueError("Unsafe NUnit XML declaration")
    try:
        root = ET.fromstring(blob)
    except ET.ParseError:
        raise ValueError("Malformed private NUnit XML") from None
    if root.tag != "test-run" or root.attrib.get("result") != "Passed":
        raise ValueError("Unity test-run did not pass")
    keys = ("total", "testcasecount", "passed", "failed", "skipped", "inconclusive")
    try:
        counters = {key: int(root.attrib[key]) for key in keys}
    except (KeyError, ValueError, TypeError):
        raise ValueError("Invalid Unity NUnit counters") from None
    if counters != dict(total=1, testcasecount=1, passed=1,
                        failed=0, skipped=0, inconclusive=0):
        raise ValueError("Exact one-case Unity NUnit counts not proven")
    cases = root.findall(".//test-case")
    if len(cases) != 1 or cases[0].attrib.get("fullname") != CASE:
        raise ValueError("Unexpected Unity synthetic test case identity")
    if cases[0].attrib.get("result") != "Passed":
        raise ValueError("Unity synthetic case not passed")
    if any(node.tag in ("failure", "reason") for node in root.iter()):
        raise ValueError("Contradictory Unity failure marker")
    if any(node.attrib.get("result") != "Passed" for node in root.iter("test-suite")):
        raise ValueError("Unity NUnit suite not passed")


def analyze(xml: bytes, exit_code: int, metrics: bytes) -> dict:
    require_unity_pass(xml, exit_code)
    counts = parse_metrics(metrics)
    if any(counts[i] for i in CONTROLS):
        raise ValueError("GPU integer, uploaded-buffer, direct texture or normal-float baseline failed")
    computed = [counts[i] for i in COMPUTED]
    staged = [counts[i] for i in STAGED]
    any_computed = any(computed)
    any_staged = any(staged)
    classification = ("computed_and_buffered_context_differences" if any_computed and any_staged
                      else "computed_only_context_difference" if any_computed
                      else "buffered_only_context_difference" if any_staged
                      else "no_synthetic_context_difference")
    return {
        "sourcefree_unity_nunit_exact_case_passed": True,
        "sourcefree_capture_has_sixteen_bounded_categories": True,
        "synthetic_gpu_words_expected": 1024,
        "synthetic_gpu_invocations_expected": 64,
        "positive_controls_passed": True,
        "synthetic_category_mismatch_counts": list(counts),
        "computed_address_category_mismatches": computed,
        "buffered_address_category_mismatches": staged,
        "pair_names": list(PAIR_NAMES),
        "classification": classification,
        "diagnostic_mismatch_found": any_computed or any_staged,
        "original_raft_shader_compiled_or_compared": False,
        "original_fft_runtime_mapping_proven": False,
        "float32_FTZ_cause_proven": False,
        "android_adreno_water_proven": False,
        "private_results_or_shader_contents_exported": False,
    }

def read_bounded(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe synthetic evidence file")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if not 0 < len(data) <= limit:
        raise ValueError("Unbounded synthetic evidence file")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()
    try:
        result = analyze(read_bounded(args.xml, MAX_XML), args.exit_code,
                         read_bounded(args.metrics, MAX_METRICS))
    except (ValueError, OSError):
        parser.exit(2, "RAFT_T1_ADDRESS_PROVENANCE_GATE invalid_or_failed_private_evidence=true\n")
    print("RAFT_T1_ADDRESS_PROVENANCE_GATE " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
