"""T4 LOCAL-005 private authentic original FileManager source/call-edge probe.

The original managed DLL must be SHA/size verified before private ILSpy output
is consumed. Emit structural booleans/counts/hashes only; not raw game code.
"""
import argparse
import json
from pathlib import Path
import re
from scripts.b07_probe_original_world_callbacks import (
    assert_original_dll, _source, fingerprint, method_body, _executable_positions,
)
from scripts.instrument_android_runtime_operations import body_bounds
from scripts.t4_original_rgd_load_contract import _bodies

EDGE = re.compile(r"\bFileManager\s*\.\s*([A-Za-z_]\w*)\s*\(")
CATCH = re.compile(r"\bcatch\s*(?:\([^{}]*\))?\s*\{")
IO = re.compile(r"\b(?:System\s*\.\s*IO\s*\.\s*)?File\s*\.\s*\w+\s*\(|\bnew\s+(?:System\s*\.\s*IO\s*\.\s*)?FileStream\s*\(")
SAVE_SHA = {"b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb",
            "0215aaae188f338c8288294f59cea53a7bd860207371f778416597653519dfd2"}


def inspect(save, manager, save_sha, manager_sha):
    if fingerprint(save) != save_sha or fingerprint(manager) != manager_sha:
        raise ValueError("Unverified source fingerprints")
    if not re.search(r"\bclass\s+FileManager\b", _executable_positions(manager)):
        raise ValueError("FileManager declaration missing")
    begin, end = body_bounds(save, "public static T Load<T>(string filename)")
    load = _executable_positions(save[begin:end])
    return_type, body = method_body(save, "Save")
    if return_type != "void":
        raise ValueError("Original Save return type changed")
    read_edges = EDGE.findall(load)
    write_edges = EDGE.findall(_executable_positions(body))
    if len(read_edges) != 1 or len(write_edges) != 1 or len(CATCH.findall(load)) != 1:
        raise ValueError("Original load/save direct call or catch contract changed")
    methods = _bodies(manager)

    def resolve(name):
        hits = [raw for meth, _, raw, _ in methods if meth == name]
        if not hits:
            raise ValueError("FileManager implementation not found")
        return {
            "possible_overloads": len(hits),
            "unique_target": len(hits) == 1,
            "target_sha256": fingerprint(hits[0]) if len(hits) == 1 else None,
            "direct_io_site_count": len(IO.findall(_executable_positions(hits[0]))) if len(hits) == 1 else None,
            "internal_catch_site_count": len(CATCH.findall(_executable_positions(hits[0]))) if len(hits) == 1 else None,
        }
    read, write = resolve(read_edges[0]), resolve(write_edges[0])
    return {
        "original_save_sha256": save_sha, "original_filemanager_sha256": manager_sha,
        "read": read, "write": write,
        "same_read_write_target_name": read_edges[0] == write_edges[0],
        "authenticated_only_after_verified_dll": True,
        "transitive_file_helpers_proven": False,
        "rgd_create_save_reopen_proven": False,
        "unity_il2cpp_or_device_proven": False,
        "raw_original_code_published": False,
    }


def probe(dll: Path, root: Path):
    # Report a bounded phase identifier on failure, never the private code,
    # filename, extracted symbols or exception message from ILSpy.
    phase = "original_dll_sha"
    try:
        assert_original_dll(dll)
        phase = "private_root"
        if root.is_symlink() or not root.is_dir():
            raise ValueError("Unsafe original ILSpy root")
        phase = "saveandload_source"
        save, save_sha = _source(root, "SaveAndLoad", None)
        if save_sha not in SAVE_SHA:
            raise ValueError("Unknown authenticated SaveAndLoad source variant")
        phase = "independent_save_order"
        if save_sha != "b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb":
            from scripts.b14_original_save_call_order import inspect_original_text, require_authenticated_baseline
            require_authenticated_baseline(inspect_original_text(save, expected_sha=save_sha))
        phase = "filemanager_source"
        manager, manager_sha = _source(root, "FileManager", None)
        phase = "filemanager_edge_contract"
        result = inspect(save, manager, save_sha, manager_sha)
        result["original_managed_dll_sha256_verified"] = True
        return result
    except Exception as exc:
        # Explicitly whitelist classifications controlled by THIS verifier;
        # never forward raw private ILSpy exception text to public CI logs.
        exact = {
            "Unverified source fingerprints": "fingerprint_gate",
            "FileManager declaration missing": "filemanager_type_gate",
            "Original Save return type changed": "save_return_contract",
            "Original load/save direct call or catch contract changed": "load_save_edge_cardinality",
            "FileManager implementation not found": "unresolved_filemanager_method",
        }
        reason = exact.get(str(exc), "unclassified_parser_or_contract")
        if str(exc).startswith("Operation signature must"):
            reason = "load_method_signature"
        elif str(exc).startswith("Expected one original Save"):
            reason = "save_method_signature"
        raise RuntimeError(
            "probe_phase=" + phase + ";cause=" + type(exc).__name__
            + ";reason=" + reason
        ) from None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-managed-dll", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    try:
        report, code = probe(args.original_managed_dll, args.source), 0
    except Exception as exc:
        report, code = {"status": "UNRESOLVED", "error_type": type(exc).__name__,
                        "bounded_failure_phase": str(exc) if isinstance(exc, RuntimeError)
                            and str(exc).startswith("probe_phase=") else "unclassified",
                        "original_source_disclosed": False, "device_tested": False}, 2
    print("T4_ORIGINAL_FILEMANAGER_IO " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
