"""T4: SHA-only repeatability report for two private ILSpy exports of the same original DLL.

Never prints decompiled code, original literals, game bytes or absolute private paths.
This is a source-acquisition diagnostic, not permission to alter production SHA pins.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.b07_probe_original_world_callbacks import (
    _executable_positions, _source, assert_original_dll, fingerprint, method_body,
)

# Independent prior original B07 and T4 source-authenticated whole-project ILSpy
# outputs. Both arise after checking the exact original immutable game binary.
OBSERVED_ORIGINAL_PAIRS = {
    ("080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03",
     "cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140"),
    ("d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef",
     "2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c"),
}


def source_profile(root):
    """Return only hashes and structural counts from exactly one source file."""
    source, digest = _source(root, "Raft_Network", None)
    kind, body = method_body(source, "WorldHasBeenLoaded")
    if kind != "IEnumerator":
        raise ValueError("Original iterator return type has changed")
    lexical = _executable_positions(body)
    import re
    ready = len(re.findall(r"\bWorldHasBeenRecieved\s*=\s*true\s*;", lexical))
    broadcast = len(re.findall(r"\bHelper\s*\.\s*BroadCastToScene\s*\(", lexical))
    if ready != 1 or broadcast < 1:
        raise ValueError("Missing original scene-broadcast / ready-write structure")
    return {
        "class_sha256": digest,
        "coroutine_body_sha256": fingerprint(body),
        "masked_coroutine_sha256": fingerprint(lexical),
        "iterator_return": kind,
        "original_completion_writes": ready,
        "original_scene_broadcast_calls": broadcast,
        "yield_returns": len(re.findall(r"\byield\s+return\b", lexical)),
        "original_source_published": False,
    }


def compare_roots(root_a, root_b, allowed_pairs=None):
    p = source_profile(root_a)
    q = source_profile(root_b)
    if allowed_pairs is not None:
        for row in (p, q):
            pair = (row["class_sha256"], row["coroutine_body_sha256"])
            if pair not in allowed_pairs:
                raise ValueError("Unrecognized exact-DLL decompiler class/body pair")
    return {
        "first": p,
        "second": q,
        "class_sha_equal": p["class_sha256"] == q["class_sha256"],
        "method_body_sha_equal": p["coroutine_body_sha256"] == q["coroutine_body_sha256"],
        "masked_executable_body_sha_equal": p["masked_coroutine_sha256"] == q["masked_coroutine_sha256"],
        "same_original_dll_proven_by_caller": False,
        "source_published": False,
        "unity_compiled": False,
        "device_result": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-managed-dll", type=Path, required=True)
    parser.add_argument("--source-a", type=Path, required=True)
    parser.add_argument("--source-b", type=Path, required=True)
    args = parser.parse_args()
    assert_original_dll(args.original_managed_dll)
    result = compare_roots(args.source_a, args.source_b, OBSERVED_ORIGINAL_PAIRS)
    result["same_original_dll_proven_by_caller"] = True
    result["original_dll_sha256"] = hashlib.sha256(args.original_managed_dll.read_bytes()).hexdigest()
    print("T4_ORIGINAL_ILSPY_REPEATABILITY " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
