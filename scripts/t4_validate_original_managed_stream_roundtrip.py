"""Privacy-safe original FileManager managed synthetic stream I/O report gate.

Only accepts positive evidence from real original method invocation. A .rgd
extension on synthetic fixture is explicitly NOT a serialized real game save.
"""
import argparse
import json
from pathlib import Path

KEYS = {
    "schema_version", "source", "original_managed_dll_authenticated",
    "original_read_write_edges_verified", "original_create_method_executed",
    "stream_closed_before_original_open", "original_open_method_executed",
    "synthetic_bytes_equal_after_reopen", "synthetic_file_size_equal",
    "temporary_file_cleanup_verified", "synthetic_filename_extension",
    "real_game_rgd_serialization_executed", "actual_android_app_storage_tested",
    "unity_or_il2cpp_executed", "private_game_data_or_identifiers_published",
}


def verify(report):
    if not isinstance(report, dict) or set(report) != KEYS:
        raise ValueError("invalid_report_shape")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("wrong_schema_version")
    if report["source"] != "SHA_PINNED_ORIGINAL_FILEMANAGER_INVOKED":
        raise ValueError("not_original_method_execution")
    expected_true = (
        "original_managed_dll_authenticated", "original_read_write_edges_verified",
        "original_create_method_executed", "stream_closed_before_original_open",
        "original_open_method_executed", "synthetic_bytes_equal_after_reopen",
        "synthetic_file_size_equal", "temporary_file_cleanup_verified",
    )
    expected_false = (
        "real_game_rgd_serialization_executed", "actual_android_app_storage_tested",
        "unity_or_il2cpp_executed", "private_game_data_or_identifiers_published",
    )
    if any(report[k] is not True for k in expected_true):
        raise ValueError("unverified_original_io_roundtrip")
    if any(report[k] is not False for k in expected_false):
        raise ValueError("false_gameplay_or_device_proof")
    if report["synthetic_filename_extension"] != ".rgd":
        raise ValueError("unexpected_synthetic_file_extension")
    return {
        "status": "AUTHENTIC_ORIGINAL_MANAGED_FILE_IO_ROUNDTRIP",
        "original_create_open_invoked": True,
        "bytes_compared_after_stream_closed": True,
        "real_rgd_game_save_proven": False,
        "android_device_proven": False,
        "unity_il2cpp_proven": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args(argv)
    report_path = args.report
    try:
        if any(node.is_symlink() for node in (report_path, *report_path.parents)):
            raise ValueError("linked_report")
        if not report_path.is_file() or report_path.stat().st_size > 20000 or report_path.stat().st_nlink != 1:
            raise ValueError("unsafe_report")
        report = json.loads(report_path.read_text(encoding="utf-8"),
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        result = verify(report)
    except (OSError, UnicodeError, ValueError, TypeError):
        print("T4_ORIGINAL_STREAM_VALIDATION status=FAIL_CLOSED raw_source_published=false")
        return 2
    print("T4_ORIGINAL_STREAM_VALIDATION " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
