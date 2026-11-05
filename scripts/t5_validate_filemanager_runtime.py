"""Fail-closed public verifier for T5 authentic managed FileManager sandbox run.

No raw original CIL, game private names or .rgd bytes are accepted or printed.
A pass proves only synthetic Linux managed CLR I/O, never a game save.
"""
import argparse
import json
from pathlib import Path

FIELDS = {
    "schema_version", "status", "original_sha_verified",
    "static_compiled_call_safety_guard", "original_managed_methods_invoked",
    "synthetic_bytes_exact_readback", "failed_phase", "failure_category",
    "original_rgd_serialization_proven", "original_world_or_unity_or_android_proven",
    "private_method_names_or_original_bytes_disclosed",
}

def verify(report):
    if type(report) is not dict or set(report) != FIELDS:
        raise ValueError("invalid_public_schema")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("unsupported_schema")
    for key in (
        "original_sha_verified", "static_compiled_call_safety_guard",
        "original_managed_methods_invoked", "synthetic_bytes_exact_readback",
        "original_rgd_serialization_proven", "original_world_or_unity_or_android_proven",
        "private_method_names_or_original_bytes_disclosed",
    ):
        if type(report[key]) is not bool:
            raise ValueError("invalid_boolean")
    if any(report[key] for key in (
        "original_rgd_serialization_proven", "original_world_or_unity_or_android_proven",
        "private_method_names_or_original_bytes_disclosed"
    )):
        raise ValueError("overstated_device_or_private_claim")
    if report["status"] != "MANAGED_SYNTHETIC_ROUNDTRIP":
        raise ValueError("original_runtime_inconclusive")
    if (report["failed_phase"], report["failure_category"]) != ("NONE", "NONE"):
        raise ValueError("hidden_failure")
    if not all(report[key] for key in (
        "original_sha_verified", "static_compiled_call_safety_guard",
        "original_managed_methods_invoked", "synthetic_bytes_exact_readback",
    )):
        raise ValueError("missing_exact_original_runtime_evidence")
    return {
        "original_compiled_filemanager_synthetic_managed_roundtrip": True,
        "android_device_or_original_rgd_proven": False,
        "private_payload_exposed": False,
    }

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        file = args.report
        if any(p.is_symlink() for p in (file, *file.parents)):
            raise ValueError("unsafe_symlinked_report")
        if not file.is_file() or file.stat().st_size > 16384 or file.stat().st_nlink != 1:
            raise ValueError("invalid_report_path")
        payload = json.loads(file.read_text(encoding="utf8"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        safe = verify(payload)
        print("T5_ORIGINAL_FILEMANAGER_RUNTIME_GATE " + json.dumps(safe, sort_keys=True))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError):
        print("T5_ORIGINAL_FILEMANAGER_RUNTIME_GATE status=INCONCLUSIVE original_runtime_unproven=true")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
