#!/usr/bin/env python3
"""Fail-closed, read-only evidence check for a shared Android Mini Lab JSON summary.

This validates provenance and synthetic T3 capture evidence only. It never
establishes Raft game graphics, APK/OBB identity or on-device visual acceptance.
"""
import argparse
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
T3 = {f"T3-{i:02d}" for i in range(1, 7)}
CAPTURE = "capture=verified-GLSurfaceView-overlay-on-window"
PIXELS = "verified_surface_pixels=true"

def capture_tokens(observed):
    """Exact whitespace-delimited key/value evidence; reject duplicate keys."""
    if not isinstance(observed, str):
        return None
    tokens = {}
    for token in observed.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key in tokens:
            return None
        tokens[key] = value
    return tokens



def verify(data):
    errors = []
    if not isinstance(data, dict):
        return ["summary must be an object"]
    pack = data.get("pack_sha256")
    if not isinstance(pack, str) or not HEX64.fullmatch(pack):
        errors.append("invalid pack SHA-256")
    source = data.get("app_source")
    if not isinstance(source, str) or not HEX40.fullmatch(source):
        errors.append("invalid app source SHA")
    if not isinstance(data.get("session"), str) or not data["session"]:
        errors.append("missing session")
    records = data.get("results")
    if not isinstance(records, list):
        return errors + ["results must be a list"]
    seen = set()
    for n, row in enumerate(records):
        if not isinstance(row, dict):
            errors.append(f"record {n} not an object")
            continue
        key = row.get("case_id")
        if not isinstance(key, str) or not key:
            errors.append(f"record {n} missing case_id")
            continue
        if key in seen:
            errors.append(f"duplicate case {key}")
        seen.add(key)
        result = row.get("result")
        if not isinstance(result, dict):
            errors.append(f"{key} missing result")
            continue
        if result.get("id") != key or row.get("worker") != key.split("-")[0]:
            errors.append(f"{key} identity mismatch")
        if result.get("pack_sha256") != pack:
            errors.append(f"{key} pack mismatch")
        if key in T3:
            observed = result.get("observed", "")
            if result.get("status") != "EVIDENCE_READY":
                errors.append(f"{key} no captured evidence")
            tokens = capture_tokens(observed)
            required = (CAPTURE, PIXELS, "gl_error=0x0", "contract=true")
            if tokens is None or not all(
                tokens.get(k) == v for k, v in (item.split("=", 1) for item in required)
            ):
                errors.append(f"{key} capture/readback parity unverified")
            if tokens is None or not re.fullmatch(
                r"[1-9][0-9]*", tokens.get("png_bytes", "")
            ) or not HEX64.fullmatch(tokens.get("png_sha256", "")):
                errors.append(f"{key} PNG metadata missing")
            if not result.get("image_uri"):
                errors.append(f"{key} image URI missing")
    missing = T3 - seen
    if missing:
        errors.append("missing T3 cases: " + ",".join(sorted(missing)))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    errors = verify(json.loads(args.summary.read_text(encoding="utf-8")))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: six synthetic T3 captures have consistent metadata; human review and Raft game acceptance NOT established")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
