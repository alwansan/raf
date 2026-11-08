#!/usr/bin/env python3
"""Validate recorded Unity FFT dispatch geometry; never infer kernel identity from an index."""
import argparse
import json
import re
from pathlib import Path

HEX32 = re.compile(r"[0-9a-fA-F]{32}\Z")
MAX_DIM = 1 << 20

def triplet(value, label):
    if not isinstance(value, list) or len(value) != 3 or any(
        type(x) is not int or x < 1 or x > MAX_DIM for x in value
    ):
        raise ValueError(label + " must be three positive bounded integers")
    return value

def validate(entry):
    if not isinstance(entry, dict) or set(entry) != {
        "compute_shader_guid", "kernel_name", "find_kernel_index",
        "dispatch_kernel_index", "numthreads", "dispatch_groups", "logical_extent"
    }:
        raise ValueError("exact dispatch identity fields required")
    guid = entry["compute_shader_guid"]
    if not isinstance(guid, str) or not HEX32.fullmatch(guid):
        raise ValueError("invalid ComputeShader GUID")
    name = entry["kernel_name"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name):
        raise ValueError("invalid kernel name")
    find = entry["find_kernel_index"]
    dispatch = entry["dispatch_kernel_index"]
    if type(find) is not int or type(dispatch) is not int or find < 0 or dispatch < 0:
        raise ValueError("kernel indices must be nonnegative integers")
    if find != dispatch:
        raise ValueError("FindKernel/Dispatch index mismatch")
    threads = triplet(entry["numthreads"], "numthreads")
    groups = triplet(entry["dispatch_groups"], "dispatch_groups")
    extent = triplet(entry["logical_extent"], "logical_extent")
    required = [(n + t - 1) // t for n, t in zip(extent, threads)]
    if groups != required:
        raise ValueError("dispatch geometry differs from exact ceiling coverage")
    return {"structural_geometry_valid": True, "kernel_name": name,
            "compute_shader_guid": guid.lower(), "required_groups": required,
            "note": "Not proof of original resource identity, pixel parity, or GPU execution"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.manifest.is_symlink() or not args.manifest.is_file() or args.manifest.stat().st_size > 65536:
            raise ValueError("invalid manifest")
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate(data)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, "Invalid FFT dispatch evidence: " + type(exc).__name__ + "\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
