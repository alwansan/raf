"""Validate private FFT pass capture manifest provenance before numerical comparison.

JSON input: {"build_sha": "...", "session_id": "...", "passes":
[{"name":"...", "vulkan_sha256":"64hex", "unity_sha256":"64hex",
"vulkan_bytes":16, "unity_bytes":16}]}
Only metadata is processed; no private pixels or assets are emitted.
"""
import json
import re

SHA = re.compile(r"^[0-9a-f]{64}$")
BUILD = re.compile(r"^[0-9a-f]{40}$")


def validate_manifest(data):
    if not isinstance(data, dict) or set(data) != {"build_sha", "session_id", "passes"}:
        raise ValueError("invalid manifest schema")
    if not isinstance(data["build_sha"], str) or not BUILD.fullmatch(data["build_sha"]):
        raise ValueError("invalid immutable build SHA")
    if not isinstance(data["session_id"], str) or not (1 <= len(data["session_id"]) <= 120):
        raise ValueError("invalid session ID")
    if not isinstance(data["passes"], list) or not (1 <= len(data["passes"]) <= 32):
        raise ValueError("invalid pass count")
    seen = set()
    for p in data["passes"]:
        if not isinstance(p, dict) or set(p) != {"name", "vulkan_sha256", "unity_sha256", "vulkan_bytes", "unity_bytes"}:
            raise ValueError("invalid pass schema")
        name = p["name"]
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError("duplicate or invalid pass name")
        seen.add(name)
        for backend in ("vulkan", "unity"):
            digest = p[backend + "_sha256"]
            size = p[backend + "_bytes"]
            if not isinstance(digest, str) or not SHA.fullmatch(digest):
                raise ValueError("invalid capture digest")
            if type(size) is not int or not 16 <= size <= 64 * 1024 * 1024 or size % 16:
                raise ValueError("invalid RGBA32F capture length")
        if p["vulkan_bytes"] != p["unity_bytes"]:
            raise ValueError("backend capture shape mismatch")
    return {"build_sha": data["build_sha"], "session_id": data["session_id"],
            "passes": len(seen), "metadata_valid": True,
            "gpu_execution_proven": False, "original_kernel_binding_proven": False}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    args = parser.parse_args()
    with open(args.manifest, encoding="utf-8") as f:
        data = json.load(f)
    print(json.dumps(validate_manifest(data), indent=2))


if __name__ == "__main__":
    main()
