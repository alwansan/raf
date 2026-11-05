"""T5: fail-closed public schema gate for original compiled FileManager call edges.

No raw DLL, method names, decompiler source or game save data are handled here.
It validates a SHA-gated private Cecil probe's bounded aggregate, NOT persistence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT_KEYS = {
    "schema_version", "source", "original_dll_sha256_verified",
    "original_dll_bytes", "read_direct_call_count", "write_direct_call_count",
    "same_target_metadata_token", "read", "write", "both_target_bodies_resolved",
    "inspected_compiled_il_not_decompiler_text", "file_write_readback_executed",
    "rgd_reopen_or_android_device_proven", "private_identifiers_or_il_published",
}
EDGE_KEYS = {
    "resolved", "declared_in_filemanager", "static_target", "has_il_body",
    "parameter_count", "il_instruction_count", "direct_system_io_call_sites",
    "exception_handler_count",
}
ORIGINAL_SIZE = 3211776

def verify_report(doc: dict) -> dict:
    if not isinstance(doc, dict) or set(doc) != ROOT_KEYS:
        raise ValueError("invalid_report_schema")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        raise ValueError("invalid_report_version")
    if doc["source"] != "SHA_PINNED_ORIGINAL_MANAGED_DLL":
        raise ValueError("invalid_source_claim")
    if type(doc["original_dll_bytes"]) is not int or doc["original_dll_bytes"] != ORIGINAL_SIZE:
        raise ValueError("wrong_original_length")
    required_true = ("original_dll_sha256_verified", "both_target_bodies_resolved",
                     "inspected_compiled_il_not_decompiler_text")
    required_false = ("same_target_metadata_token", "file_write_readback_executed",
                      "rgd_reopen_or_android_device_proven", "private_identifiers_or_il_published")
    if any(doc[k] is not True for k in required_true) or any(doc[k] is not False for k in required_false):
        raise ValueError("unproven_or_overstated_original_call_contract")
    if any(type(doc[k]) is not int or doc[k] != 1
           for k in ("read_direct_call_count", "write_direct_call_count")):
        raise ValueError("call_edge_count_mismatch")
    for role in ("read", "write"):
        edge = doc[role]
        if not isinstance(edge, dict) or set(edge) != EDGE_KEYS:
            raise ValueError("invalid_edge_schema")
        for key in ("resolved", "declared_in_filemanager", "static_target", "has_il_body"):
            if edge[key] is not True:
                raise ValueError("unresolved_or_nonstatic_original_target")
        for key in ("parameter_count", "il_instruction_count",
                    "direct_system_io_call_sites", "exception_handler_count"):
            value = edge[key]
            if type(value) is not int or value < (1 if key == "il_instruction_count" else 0):
                raise ValueError("invalid_or_unknown_il_count")
    return {
        "status": "VALIDATED_COMPILED_IL_CALL_EDGES",
        "read_target_resolved": True,
        "write_target_resolved": True,
        "original_dll_sha256_verified": True,
        "rgd_save_or_device_proven": False,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    path = args.report
    try:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("unsafe_symlink")
        if not path.is_file() or path.stat().st_size > 65536 or path.stat().st_nlink != 1:
            raise ValueError("invalid_report_file")
        doc = json.loads(path.read_text(encoding="utf8"),
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        safe = verify_report(doc)
    except (OSError, UnicodeError, ValueError, TypeError):
        print("T5_FILEMANAGER_METADATA_VALIDATION status=FAIL_CLOSED identifiers_published=false")
        return 2
    print("T5_FILEMANAGER_METADATA_VALIDATION " + json.dumps(safe, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
