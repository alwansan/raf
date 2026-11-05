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



def inspect_original_saveandload_scope(source, expected_sha):
    """Bounded executable site inventory when ILSpy method signatures defy parser.

    Counts do NOT prove a deserialize or binder branch executes, nor that an
    older NRBF type can be resolved. Fail closed for absent deserializers.
    """
    if fingerprint(source) != expected_sha:
        raise ValueError("Unknown original SaveAndLoad source SHA256")
    code = _executable_positions(source)
    deserialize_calls = len(DESERIALIZE.findall(code))
    if deserialize_calls < 1:
        raise ValueError("Original SaveAndLoad has no executable deserialize site")
    return {
        "original_saveandload_sha256": fingerprint(source),
        "executable_deserialize_sites_in_file": deserialize_calls,
        "binder_assignments_in_file": len(BINDER.findall(code)),
        "assembly_resolution_tokens_in_file": len(CUSTOM_RESOLVE.findall(code)),
        "file_manager_calls_in_file": len(FILE_IO.findall(code)),
        "generic_load_identifier_tokens_in_file": len(re.findall(r"\\bLoad\\s*<", code)),
        "source_method_parser_resolved": False,
        "binder_proves_old_rgds_compatible": False,
        "original_rgd_deserialized": False,
        "device_unity_tested": False,
        "original_game_code_or_names_published": False,
    }



def inspect_original_project_for_loader(source_root):
    """Find executable deserialization bodies across the *verified DLL* export.

    The historic B37 suggestion names SaveAndLoad.Load<T>; absence from that
    class must not turn into a fabricated compatibility conclusion. No code,
    class names, filenames or data bytes are printed.
    """
    if source_root.is_symlink() or not source_root.is_dir():
        raise ValueError("Unsafe private ILSpy source root")
    source_files, deserialize_files, loader_bodies = 0, 0, 0
    candidate_sha256 = []
    parser_unresolved = 0
    for path in sorted(source_root.rglob("*.cs")):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Unsafe private ILSpy source leaf")
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        source_files += 1
        if not DESERIALIZE.search(_executable_positions(text)):
            continue
        deserialize_files += 1
        bodies = _bodies(text)
        direct = sum(bool(DESERIALIZE.search(body)) for _, _, _, body in bodies)
        if not direct:
            parser_unresolved += 1
        loader_bodies += direct
        candidate_sha256.append(fingerprint(text))
    if source_files < 1 or deserialize_files < 1:
        raise ValueError("No authentic original source deserializer found")
    return {
        "original_source_files_inspected": source_files,
        "files_with_executable_deserialize": deserialize_files,
        "parsed_loader_method_bodies": loader_bodies,
        "unparsed_deserialize_source_files": parser_unresolved,
        "deserializer_source_sha256": sorted(candidate_sha256),
        "saveandload_loader_not_assumed": True,
        "original_binary_sha_verified": True,
        "private_source_published": False,
        "actual_rgd_deserialized": False,
        "unity_or_device_tested": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-managed-dll", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    assert_original_dll(args.original_managed_dll)
    source, observed = _source(args.source, "SaveAndLoad", None)
    # CI41938333418 observed a different, deterministic full-project
    # ILSpy11.2 SaveAndLoad text hash from the exact SHA-verified original DLL.
    # This is a READ-ONLY diagnostic allowance, never a new production
    # adapter pin: an independent B14 save-order contract must also pass.
    alternative_readonly_source = "0215aaae188f338c8288294f59cea53a7bd860207371f778416597653519dfd2"
    if observed != PINS["SaveAndLoad"]:
        if observed != alternative_readonly_source:
            raise ValueError("Unknown original decompiler output; refuse unpinned source")
        from scripts.b14_original_save_call_order import (
            inspect_original_text, require_authenticated_baseline,
        )
        original_save_proof = inspect_original_text(source, expected_sha=observed)
        require_authenticated_baseline(original_save_proof)
        print("T4_ORIGINAL_SOURCE_VARIANT " + json.dumps({
            "observed_sha256": observed,
            "expected_adapter_sha256": PINS["SaveAndLoad"],
            "independent_original_save_contract_passed": True,
            "production_adapter_pin_unchanged": True,
            "readonly": True,
        }, sort_keys=True))
    try:
        report = analyze(source, expected_sha=observed)
        print("T4_ORIGINAL_RGD_LOADER " + json.dumps(report, sort_keys=True))
    except ValueError as exc:
        if str(exc) != "No recognizable original load/deserialization method":
            raise
        result = inspect_original_saveandload_scope(source, expected_sha=observed)
        print("T4_ORIGINAL_RGD_FILE_SCOPE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
