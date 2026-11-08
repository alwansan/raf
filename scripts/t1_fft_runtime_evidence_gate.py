#!/usr/bin/env python3
"""Validate sanitized Unity FFT runtime binding evidence; never infer runtime IDs from DXBC slots."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
GUID = re.compile(r"^[0-9a-f]{32}$")
MAX_BYTES = 1024 * 1024

def validate(record):
    if not isinstance(record, dict) or set(record) != {"build_sha", "device_session", "dispatches"}:
        raise ValueError("invalid evidence envelope")
    if not isinstance(record["build_sha"], str) or not SHA.fullmatch(record["build_sha"]):
        raise ValueError("missing immutable build SHA")
    if not isinstance(record["device_session"], str) or not 1 <= len(record["device_session"]) <= 128:
        raise ValueError("missing device session")
    entries = record["dispatches"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 128:
        raise ValueError("missing bounded runtime dispatch sequence")
    for index, row in enumerate(entries):
        fields = {"shader_guid", "kernel_name", "find_kernel_result", "dispatch_kernel",
                  "groups", "fft_size", "bank", "pass_index", "bindings"}
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"dispatch {index}: incomplete runtime identity")
        if not isinstance(row["shader_guid"], str) or not GUID.fullmatch(row["shader_guid"]):
            raise ValueError(f"dispatch {index}: invalid shader GUID")
        if not isinstance(row["kernel_name"], str) or not 1 <= len(row["kernel_name"]) <= 128:
            raise ValueError(f"dispatch {index}: missing named Unity kernel")
        for key in ("find_kernel_result", "dispatch_kernel", "fft_size", "bank", "pass_index"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError(f"dispatch {index}: invalid {key}")
        if row["find_kernel_result"] != row["dispatch_kernel"]:
            raise ValueError(f"dispatch {index}: FindKernel/Dispatch mismatch")
        if not isinstance(row["groups"], list) or len(row["groups"]) != 3 or any(
            type(v) is not int or v < 1 for v in row["groups"]
        ):
            raise ValueError(f"dispatch {index}: invalid group counts")
        if not isinstance(row["bindings"], list) or not row["bindings"] or len(row["bindings"]) > 32 or any(
            not isinstance(v, str) or not 1 <= len(v) <= 128 for v in row["bindings"]
        ):
            raise ValueError(f"dispatch {index}: missing resource binding names")
    return {"runtime_dispatches": len(entries), "binding_contract_complete": True,
            "device_session": record["device_session"], "build_sha": record["build_sha"]}

def no_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate evidence key")
        out[k] = v
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("private_manifest", type=Path)
    a = p.parse_args()
    try:
        if a.private_manifest.is_symlink() or a.private_manifest.stat().st_size > MAX_BYTES:
            raise ValueError("invalid manifest size or symlink")
        data = json.loads(a.private_manifest.read_text(encoding="utf-8"),
                          object_pairs_hook=no_duplicate_keys)
        print(json.dumps(validate(data), sort_keys=True))
    except (OSError, ValueError, TypeError) as e:
        p.exit(2, "Incomplete FFT runtime evidence: " + type(e).__name__ + "\n")

if __name__ == "__main__":
    main()
