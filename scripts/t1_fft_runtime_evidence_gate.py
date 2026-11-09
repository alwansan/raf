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
    if (not isinstance(record["device_session"], str) or not 1 <= len(record["device_session"]) <= 128
            or not record["device_session"].strip() or record["device_session"] != record["device_session"].strip()
            or any(ord(ch) < 32 or 127 <= ord(ch) <= 159 for ch in record["device_session"])):
        raise ValueError("missing device session")
    entries = record["dispatches"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 128:
        raise ValueError("missing bounded runtime dispatch sequence")
    # FindKernel indices must be stable and unambiguous within a shader asset.
    name_to_index = {}
    index_to_name = {}
    for index, row in enumerate(entries):
        fields = {"shader_guid", "kernel_name", "find_kernel_result", "dispatch_kernel",
                  "groups", "fft_size", "bank", "pass_index", "bindings"}
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"dispatch {index}: incomplete runtime identity")
        if not isinstance(row["shader_guid"], str) or not GUID.fullmatch(row["shader_guid"]):
            raise ValueError(f"dispatch {index}: invalid shader GUID")
        if (not isinstance(row["kernel_name"], str) or not 1 <= len(row["kernel_name"]) <= 128
                or not row["kernel_name"].strip() or row["kernel_name"] != row["kernel_name"].strip()
                or any(ord(ch) < 32 or 127 <= ord(ch) <= 159 for ch in row["kernel_name"])):
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
        if any(not v.strip() or v != v.strip() for v in row["bindings"]):
            raise ValueError(f"dispatch {index}: blank or padded resource binding name")
        if len(set(row["bindings"])) != len(row["bindings"]):
            raise ValueError(f"dispatch {index}: duplicate resource binding name")
        if any(any(ord(ch) < 32 or 127 <= ord(ch) <= 159 for ch in value)
               for value in row["bindings"]):
            raise ValueError(f"dispatch {index}: control character in binding name")
        # Only same-build observed Unity identities, never compiled DXBC slot IDs.
        guid, name, number = row["shader_guid"], row["kernel_name"], row["find_kernel_result"]
        name_key, index_key = (guid, name), (guid, number)
        old_number = name_to_index.get(name_key)
        old_name = index_to_name.get(index_key)
        if old_number is not None and old_number != number:
            raise ValueError(f"dispatch {index}: inconsistent index for named kernel")
        if old_name is not None and old_name != name:
            raise ValueError(f"dispatch {index}: inconsistent name for kernel index")
        name_to_index[name_key] = number
        index_to_name[index_key] = name
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
