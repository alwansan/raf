"""Redacted bounded NUnit proof gate for private original-derived FFT GPU Dispatch.

The real Unity compiler log and XML test failure contents remain private; only
source-free expected test IDs are recognized. Never print proprietary HLSL.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

KNOWN = frozenset({
    "T1PrivateFftImportTests.VerifiedTwentyOriginalDerivedCandidatesImportInUnity",
    "T1PrivateFftGpuDispatchTests.AuthenticatedFirstPairActuallyDispatchesWithSampledImages",
})
MAX_XML=1024*1024


def classify(blob: bytes, code: int):
    if type(blob) is not bytes or not 0<len(blob)<=MAX_XML or type(code) is not int:
        raise ValueError("Private NUnit payload absent or unbounded")
    try:
        root=ET.fromstring(blob)
    except ET.ParseError:
        raise ValueError("Private NUnit XML invalid") from None
    if root.tag!="test-run":
        raise ValueError("Wrong NUnit root")
    names=[]
    cases=root.findall(".//test-case")
    for case in cases:
        names.append(case.attrib.get("fullname"))
    unique=len(names)==2 and len(set(names))==2 and set(names)==KNOWN
    try:
        fields={k:int(root.attrib[k]) for k in ("total","testcasecount","passed","failed","skipped","inconclusive")}
    except (TypeError,ValueError,KeyError):
        raise ValueError("Private NUnit numeric counters malformed") from None
    if any(x<0 or x>500 for x in fields.values()):
        raise ValueError("Private NUnit numeric bound rejected")
    positive=(code==0 and unique and fields=={
        "total":2,"testcasecount":2,"passed":2,"failed":0,"skipped":0,"inconclusive":0
    } and root.attrib.get("result")=="Passed"
        and all(c.attrib.get("result")=="Passed" for c in cases))
    return {
        "actual_unity_editor_test_cases":len(cases),
        "expected_authentic_original_derived_tests_present":unique,
        "all_private_unity_tests_passed":positive,
        "fft_source_compiled_slot_imports_genuine_unity":positive,
        "fft_derived_two_pass_gpu_dispatch_with_observed_writes":positive,
        "original_author_kernel_names_or_runtime_mapping_proven":False,
        "android_adreno_water_pixels_proven":False,
        "numeric_original_pixel_parity_proven":False,
        "private_original_names_shader_logs_or_pixel_values_exported":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--xml",type=Path,required=True)
    p.add_argument("--exit-code",type=int,required=True)
    args=p.parse_args()
    if args.xml.is_symlink() or not args.xml.is_file() or args.xml.stat().st_size>MAX_XML:
        raise SystemExit("RAFT_T1_GPU_DISPATCH_GATE missing_or_unsafe_private_nunit=true")
    try:
        result=classify(args.xml.read_bytes(),args.exit_code)
    except (ValueError,OSError):
        raise SystemExit("RAFT_T1_GPU_DISPATCH_GATE invalid_private_nunit=true") from None
    print("RAFT_T1_GPU_DISPATCH_GATE "+json.dumps(result,sort_keys=True))
    if not result["all_private_unity_tests_passed"]:
        raise SystemExit("Actual original-derived two-pass Unity GPU test not established")


if __name__=="__main__":
    main()
