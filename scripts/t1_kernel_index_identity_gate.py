#!/usr/bin/env python3
"""Source-only gate for claims that LogRaft kernel index identifies a Unity FFT kernel.

This does NOT run Unity or establish GPU correctness. No raw assets required.
"""
import argparse
import json
import re
import sys

SHA = re.compile(r"^[0-9a-f]{40}$")
GUID = re.compile(r"^[0-9a-f]{32}$")

def check(record):
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    for key in ("source_sha", "compute_shader_guid", "kernel_name", "find_kernel_index",
                "dispatch_kernel_index", "dispatch_groups", "original_program_sha256",
                "resource_binding_sha256"):
        if key not in record:
            errors.append("missing " + key)
    if errors:
        return errors
    if not isinstance(record["source_sha"], str) or not SHA.fullmatch(record["source_sha"]):
        errors.append("source_sha must be a pinned 40-character lowercase SHA")
    if not isinstance(record["compute_shader_guid"], str) or not GUID.fullmatch(record["compute_shader_guid"]):
        errors.append("compute_shader_guid must be 32 lowercase hex digits")
    if not isinstance(record["kernel_name"], str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", record["kernel_name"]):
        errors.append("kernel_name must be a named Unity kernel")
    for key in ("find_kernel_index", "dispatch_kernel_index"):
        if type(record[key]) is not int or record[key] < 0:
            errors.append(key + " must be a nonnegative integer")
    if type(record["find_kernel_index"]) is int and type(record["dispatch_kernel_index"]) is int:
        if record["find_kernel_index"] != record["dispatch_kernel_index"]:
            errors.append("FindKernel/Dispatch index mismatch")
    groups = record["dispatch_groups"]
    if not isinstance(groups, list) or len(groups) != 3 or any(type(x) is not int or x <= 0 for x in groups):
        errors.append("dispatch_groups must be three positive integers")
    for key in ("original_program_sha256", "resource_binding_sha256"):
        if not isinstance(record[key], str) or not re.fullmatch(r"[0-9a-f]{64}", record[key]):
            errors.append(key + " must be a SHA-256 digest")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_json", help="metadata only; do not include raw game resources")
    args = parser.parse_args()
    with open(args.evidence_json, encoding="utf-8") as f:
        record = json.load(f)
    errors = check(record)
    print(json.dumps({"status": "REJECTED" if errors else "STRUCTURAL_ONLY",
                      "errors": errors, "gpu_proven": False, "device_proven": False},
                     sort_keys=True))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
