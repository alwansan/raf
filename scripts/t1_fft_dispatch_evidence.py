"""Fail-closed T1 audit of a privately supplied original FFT caller source.

This is a structural triage tool, NOT Unity runtime, binding or numeric proof.
Never print or upload the private source or names.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

CALLS = ("FindKernel", "Dispatch", "SetTexture", "SetBuffer", "SetInt", "SetFloat", "SetVector")


def audit(source: bytes, expected_sha256: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("Expected pinned lowercase SHA256")
    if not source or len(source) > 4_000_000 or hashlib.sha256(source).hexdigest() != expected_sha256:
        raise ValueError("Private caller SHA256 mismatch or size outside bounds")
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Original caller must be UTF-8") from exc
    # Mask strings and comments: names inside diagnostics are not calls.
    masked = re.sub(r'''(?:\$@|@\$|@)"(?:[^"]|"")*"|\$?"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|//[^\n]*|/\*[\s\S]*?\*/''',
                    lambda m: " " * len(m.group()), text)
    counts = {name: len(re.findall(r"\b" + name + r"\s*\(", masked)) for name in CALLS}
    # Even all call families present cannot establish dataflow, kernel identity or runtime behavior.
    return {
        "source_sha256_verified": True,
        "call_families_present": {name: counts[name] > 0 for name in CALLS},
        "findkernel_and_dispatch_syntax_present": counts["FindKernel"] > 0 and counts["Dispatch"] > 0,
        "original_program_to_kernel_mapping_proven": False,
        "resource_binding_dataflow_proven": False,
        "unity_execution_proven": False,
        "android_device_proven": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-original-caller", type=Path, required=True)
    p.add_argument("--sha256", required=True)
    a = p.parse_args()
    if a.private_original_caller.is_symlink() or not a.private_original_caller.is_file():
        p.error("Private caller missing or symlink")
    print("RAFT_T1_FFT_CALLER_AUDIT " + json.dumps(
        audit(a.private_original_caller.read_bytes(), a.sha256), sort_keys=True))


if __name__ == "__main__":
    main()
