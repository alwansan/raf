#!/usr/bin/env python3
"""Check consistency of recorded Unity FFT kernel identity; not proof of original identity."""
import argparse
import json
import os
import stat
from pathlib import Path
from scripts.t1_fft_dispatch_coverage import validate

MAX_OBSERVATIONS = 128
MAX_MANIFEST = 65536

def reject_duplicate_keys(pairs):
    """Do not allow JSON to silently overwrite captured kernel identity fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result

def check(observations):
    if not isinstance(observations, list) or not 1 <= len(observations) <= MAX_OBSERVATIONS:
        raise ValueError("expected 1..128 observations")
    identities = {}
    reverse_identities = {}
    sessions = set()
    for entry in observations:
        if not isinstance(entry, dict) or set(entry) != {
            "session", "compute_shader_guid", "kernel_name", "find_kernel_index",
            "dispatch_kernel_index", "numthreads", "dispatch_groups", "logical_extent"
        }:
            raise ValueError("invalid observation fields")
        session = entry["session"]
        if not isinstance(session, str) or not 1 <= len(session) <= 128 or any(ord(c) < 32 for c in session):
            raise ValueError("invalid session")
        validated = validate({k: v for k, v in entry.items() if k != "session"})
        key = (session, validated["compute_shader_guid"], validated["kernel_name"])
        idx = entry["find_kernel_index"]
        if key in identities and identities[key] != idx:
            raise ValueError("kernel index drift for same session/GUID/name")
        reverse_key = (session, validated["compute_shader_guid"], idx)
        if reverse_key in reverse_identities and reverse_identities[reverse_key] != validated["kernel_name"]:
            raise ValueError("kernel index alias for same session/GUID")
        reverse_identities[reverse_key] = validated["kernel_name"]
        identities[key] = idx
        sessions.add(session)
    return {
        "structural_consistency": True, "observations": len(observations),
        "sessions": len(sessions), "identities": len(identities),
        "original_identity_proven": False, "gpu_execution_proven": False
    }

def read_trace_manifest(path):
    """Read one bounded regular file descriptor; never follow a swapped symlink."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    elif path.is_symlink():
        raise ValueError("invalid manifest")
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_MANIFEST:
            raise ValueError("invalid manifest")
        # A regular-file read is allowed to return fewer bytes than requested.
        # Consume exactly the stat-verified length; reject truncation or growth.
        chunks = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(fd, remaining)
            if not chunk:
                raise ValueError("truncated manifest")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise ValueError("manifest changed during read")
        # A same-length in-place rewrite can otherwise escape the EOF check.
        # Reject descriptor metadata changes observed during the read.
        after = os.fstat(fd)
        if (after.st_size != info.st_size or
                after.st_mtime_ns != info.st_mtime_ns or
                after.st_ctime_ns != info.st_ctime_ns):
            raise ValueError("manifest changed during read")
        raw = b"".join(chunks)
        return json.loads(raw.decode("utf-8", errors="strict"),
                          object_pairs_hook=reject_duplicate_keys)
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        report = check(read_trace_manifest(args.manifest))
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        parser.exit(2, "Invalid FFT trace: " + type(exc).__name__ + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
