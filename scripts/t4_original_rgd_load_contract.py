"""T4 LOCAL-005: privacy-safe, SHA-authenticated original RGD load-path contract.

Only counts, booleans and hashes leave the private ILSpy staging directory.
This is not BinaryFormatter execution or a device save/reopen test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.b07_probe_original_world_callbacks import (
    PINS, _executable_positions, _source, assert_original_dll, fingerprint,
)

METHOD = re.compile(
    r"(?m)^[ \t]*(?:public|private|protected|internal)[ \t]+"
    r"(?:(?:static|virtual|override|sealed|new|async)[ \t]+)*"
    r"(?P<return>[\w.<>?,\[\]]+)[ \t]+"
    r"(?P<name>[A-Za-z_]\w*(?:<[^;{}\r\n]+>)?)"
    r"[ \t]*\([^;{}]*\)[ \t]*(?:where[ \t]+[^;{}\r\n]+)?[ \t]*\{"
)
DESERIALIZE = re.compile(r"\b(?:\w+\s*\.\s*)?Deserialize\s*\(")
BINDER = re.compile(r"\b(?:\w+\s*\.\s*)?Binder\s*=")
SAVE = re.compile(r"\b(?:\w+\s*\.\s*)?Serialize\s*\(")
FILE_IO = re.compile(r"\bFileManager\s*\.\s*\w+\s*\(")
CUSTOM_RESOLVE = re.compile(r"\b(?:AssemblyResolve|SerializationBinder|BindToType|FormatterAssemblyStyle)\b")
CATCH = re.compile(r"\bcatch\s*(?:\([^{}]*\))?\s*\{")


def _bodies(source):
    masked = _executable_positions(source)
    found = []
    for match in METHOD.finditer(masked):
        start = match.end() - 1
        depth = 1
        stop = None
        for pos in range(start + 1, len(masked)):
            if masked[pos] == "{":
                depth += 1
            elif masked[pos] == "}":
                depth -= 1
                if depth == 0:
                    stop = pos
                    break
        if stop is None:
            raise ValueError("Unbalanced original method body")
        body = masked[start + 1:stop]
        name = match.group("name").split("<", 1)[0]
        found.append((name, match.group("return"), source[match.start():stop + 1], body))
    return found


def analyze(source, expected_sha=PINS["SaveAndLoad"]):
    if fingerprint(source) != expected_sha:
        raise ValueError("Unknown original SaveAndLoad source SHA256")
    methods = _bodies(source)
    # Include arbitrary-named deserializers, not only Load<T>; fail if the
    # implementation moves to a helper rather than silently reporting zero.
    targets = [(n, t, raw, body) for n, t, raw, body in methods
               if n.lower().startswith("load") or DESERIALIZE.search(body)]
    if not targets:
        raise ValueError("No recognizable original load/deserialization method")
    if len({(n, hashlib.sha256(raw.encode()).hexdigest()) for n, _, raw, _ in targets}) != len(targets):
        raise ValueError("Ambiguous duplicate original loader")
    total_deserialize = sum(len(DESERIALIZE.findall(b)) for _, _, _, b in targets)
    if not total_deserialize:
        raise ValueError("No executable deserialization call inside loader methods")
    return {
        "original_saveandload_sha256": fingerprint(source),
        "loader_method_count": len(targets),
        "loader_method_body_sha256": sorted(fingerprint(raw) for _, _, raw, _ in targets),
        "generic_loader_count": sum("<" in raw.split("(", 1)[0] for _, _, raw, _ in targets),
        "deserialize_calls": total_deserialize,
        "binder_assignments_in_loaders": sum(len(BINDER.findall(b)) for _, _, _, b in targets),
        "serialization_or_assembly_alias_tokens_in_loaders": sum(len(CUSTOM_RESOLVE.findall(b)) for _, _, _, b in targets),
        "file_manager_calls_in_loaders": sum(len(FILE_IO.findall(b)) for _, _, _, b in targets),
        "catch_blocks_in_loaders": sum(len(CATCH.findall(b)) for _, _, _, b in targets),
        "serialize_calls_in_loaders": sum(len(SAVE.findall(b)) for _, _, _, b in targets),
        "loader_methods_with_deserialize": sum(bool(DESERIALIZE.search(b)) for _, _, _, b in targets),
        "names_or_original_source_published": False,
        "original_rgd_deserialized": False,
        "android_unity_or_device_tested": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-managed-dll", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    assert_original_dll(args.original_managed_dll)
    source, observed = _source(args.source, "SaveAndLoad", None)
    if observed != PINS["SaveAndLoad"]:
        print("T4_ORIGINAL_SOURCE_MISMATCH " + json.dumps({
            "observed_sha256": observed,
            "expected_sha256": PINS["SaveAndLoad"],
            "loader_or_device_validated": False,
        }, sort_keys=True))
        raise ValueError("Original source SHA mismatch; refuse unsupported decompiler output")
    print("T4_ORIGINAL_RGD_LOADER " + json.dumps(analyze(source), sort_keys=True))


if __name__ == "__main__":
    main()
