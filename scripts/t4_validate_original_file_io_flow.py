"""Strict, privacy-safe schema gate for T4 compiled original FileManager IO facts.

The original managed DLL is checked by the separate Cecil oracle. This
validator accepts only structural categories, never method/IL/source text.
No actual file roundtrip/Unity/device success is inferred from compiled IL.
"""
import argparse
import json
from pathlib import Path

ROOT = {
    "schema_version", "source", "exact_dll_size_sha_verified",
    "read_target_unique", "write_target_unique", "original_methods_distinct",
    "read", "write", "actual_file_io_invoked", "real_rgd_reopened",
    "android_or_unity_executed", "original_source_or_private_symbols_published",
}
EDGE = {
    "parameter_count", "parameter_categories", "return_category",
    "direct_io_intent", "direct_io_call_count", "catch_handler_count",
    "finally_handler_count", "catch_contains_leave",
    "catch_contains_explicit_throw", "catch_contains_null_literal",
    "catch_can_exit_normally", "exception_swallow_on_device_proven",
}
CATEGORIES = {"void", "string", "bool", "byte_array", "stream", "io_enum",
              "integer", "byref_other", "other"}
INTENTS = {
    "file_open", "file_create", "file_exists", "file_read_all",
    "file_write_all", "file_delete", "filestream_construct",
    "other_filestream_api", "create_directory",
    "other_directory_api", "other_file_api", "other_io_api",
}


def validate(report):
    if not isinstance(report, dict) or set(report) != ROOT:
        raise ValueError("root_schema")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("version")
    if report["source"] != "IMMUTABLE_ORIGINAL_COMPILED_IL":
        raise ValueError("source")
    if any(report[key] is not True for key in
           ("exact_dll_size_sha_verified", "read_target_unique",
            "write_target_unique", "original_methods_distinct")):
        raise ValueError("unverified_original")
    if any(report[key] is not False for key in
           ("actual_file_io_invoked", "real_rgd_reopened",
            "android_or_unity_executed", "original_source_or_private_symbols_published")):
        raise ValueError("fabricated_runtime")
    for label, param_count in (("read", 2), ("write", 1)):
        row = report[label]
        if not isinstance(row, dict) or set(row) != EDGE:
            raise ValueError("edge_schema")
        if type(row["parameter_count"]) is not int or row["parameter_count"] != param_count:
            raise ValueError("method_signature")
        params = row["parameter_categories"]
        if not isinstance(params, list) or len(params) != param_count or any(
                type(x) is not str or x not in CATEGORIES for x in params):
            raise ValueError("parameter_categories")
        if row["return_category"] not in CATEGORIES or type(row["return_category"]) is not str:
            raise ValueError("return_category")
        if row["direct_io_intent"] not in INTENTS or type(row["direct_io_intent"]) is not str:
            raise ValueError("direct_io_intent")
        if any(type(row[k]) is not int or row[k] != n for k, n in
               (("direct_io_call_count", 1), ("catch_handler_count", 1),
                ("finally_handler_count", 0))):
            raise ValueError("io_handler_cardinality")
        for k in ("catch_contains_leave", "catch_contains_explicit_throw",
                  "catch_contains_null_literal", "catch_can_exit_normally",
                  "exception_swallow_on_device_proven"):
            if type(row[k]) is not bool:
                raise ValueError("handler_flags")
        if row["catch_can_exit_normally"] != (
                row["catch_contains_leave"] and not row["catch_contains_explicit_throw"]):
            raise ValueError("incoherent_handler_exit")
        if row["exception_swallow_on_device_proven"] is not False:
            raise ValueError("fabricated_swallow")
    return {
        "status": "AUTHENTIC_COMPILED_IO_CONTROL_FLOW_CLASSIFIED",
        "original_binary_proven": True,
        "read_io_intent": report["read"]["direct_io_intent"],
        "write_io_intent": report["write"]["direct_io_intent"],
        "read_normal_catch_exit_possible": report["read"]["catch_can_exit_normally"],
        "write_normal_catch_exit_possible": report["write"]["catch_can_exit_normally"],
        "original_device_file_io_executed": False,
        "rgd_reopen_proven": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    p = args.report
    try:
        if any(s.is_symlink() for s in (p, *p.parents)):
            raise ValueError("symlink")
        if not p.is_file() or p.stat().st_size > 20000 or p.stat().st_nlink != 1:
            raise ValueError("unverified_report_path")
        report = json.loads(p.read_text(encoding="utf-8"),
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        safe = validate(report)
    except (OSError, UnicodeError, ValueError, TypeError):
        print("T4_IO_FLOW_VALIDATION status=FAIL_CLOSED private_details_logged=false")
        return 2
    print("T4_IO_FLOW_VALIDATION " + json.dumps(safe, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
