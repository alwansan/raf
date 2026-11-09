#!/usr/bin/env python3
"""Classify exact Unity Android expansion-OBB GUID warnings, without suppressing them.

Read-only analysis of LogRaft raw log lines. Output *counts only*; never print
device paths, timestamps, user identifiers or proprietary asset names.
A missing optional PATCH lookup is not evidence that MAIN OBB was corrupt.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

PACKAGE = "com.alwansan.raft.androidtest"
WARN = re.compile(r"Unable to load GUID for '([^'\r\n]+)'")
OBB = re.compile(
    r"\A(?:/storage/emulated/[0-9]+|/sdcard)/Android/obb/([^/]+)/(?:(main|patch))\.([1-9][0-9]*)\.([^/]+)\.obb\Z")
SAFE = re.compile(r"[a-z0-9][a-z0-9._]*\Z")
CODE = re.compile(r"[1-9][0-9]*\Z")


def _unique_json_pairs(pairs):
    """Fail closed on ambiguous delivery metadata at every JSON nesting level."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate delivery JSON key")
        result[key] = value
    return result


def load_delivery_json(raw: str) -> dict:
    return json.loads(raw, object_pairs_hook=_unique_json_pairs)


def _manifest(manifest):
    if (type(manifest) is not dict or manifest.get("package") != PACKAGE
            or type(manifest.get("version_code")) is not str
            or CODE.fullmatch(manifest["version_code"]) is None):
        raise ValueError("Invalid original native package/version metadata")
    records = manifest.get("files")
    if type(records) is not list or not 1 <= len(records) <= 20:
        raise ValueError("Invalid logical native files inventory")
    names = []
    for record in records:
        if type(record) is not dict or type(record.get("name")) is not str:
            raise ValueError("Invalid logical file name")
        name = record["name"]
        if name in names or "/" in name or "\\" in name or name in ("", ".", ".."):
            raise ValueError("Unsafe or repeated logical filename")
        names.append(name)
    main = "main." + manifest["version_code"] + "." + PACKAGE + ".obb"
    if main not in names:
        raise ValueError("Authentic delivery manifest does not declare required MAIN OBB")
    return manifest["version_code"], set(names)


def classify_line(line: str, *, code: str, logical_files: set[str]) -> str | None:
    if type(line) is not str:
        raise ValueError("Log line must be text")
    match = WARN.search(line)
    if match is None:
        return None
    path = match[1]
    # The raw warning may mention arbitrary filesystem locations; we do not
    # treat them as a known Android OBB probe unless shape is exact.
    found = OBB.search(path)
    if found is None:
        return "other_guid_warning"
    parent, kind, version, package = found.groups()
    if (parent != PACKAGE or package != PACKAGE or version != code
            or not SAFE.fullmatch(parent) or not SAFE.fullmatch(package)):
        return "foreign_or_different_version_obb_guid_warning"
    filename = kind + "." + version + "." + package + ".obb"
    if kind == "main":
        return "declared_main_obb_guid_warning"
    if filename in logical_files:
        return "declared_patch_obb_guid_warning"
    return "optional_patch_probe_not_packaged"


def classify_streams(streams, *, delivery: dict) -> dict:
    code, names = _manifest(delivery)
    counts = Counter()
    streams_processed = 0
    for stream in streams:
        streams_processed += 1
        for line in stream:
            category = classify_line(line, code=code, logical_files=names)
            if category is not None:
                counts[category] += 1
    return {
        "package": PACKAGE,
        "version_code": code,
        "log_segments_processed": streams_processed,
        "total_guid_warning_lines": sum(counts.values()),
        "warning_categories": dict(sorted(counts.items())),
        "main_obb_guid_warning_count": counts["declared_main_obb_guid_warning"],
        "optional_patch_lookup_not_packaged_count": counts["optional_patch_probe_not_packaged"],
        "actual_main_obb_content_verified": False,
        "actual_device_main_obb_mount_verified": False,
        "patch_file_physically_absent_on_device_proven": False,
        "unity_warning_suppressed": False,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--delivery", required=True, type=Path,
                     help="Trusted delivery.json for the exact installed build")
    cli.add_argument("--log", required=True, action="append", type=Path,
                     help="One or more LogRaft raw .log.txt files; read only")
    args = cli.parse_args()
    if (args.delivery.is_symlink() or not args.delivery.is_file()
            or not 0 < args.delivery.stat().st_size < 100_000):
        raise ValueError("Missing or unsafe source delivery.json")
    data = load_delivery_json(args.delivery.read_text(encoding="utf8"))
    inputs = []
    try:
        for path in args.log:
            if path.is_symlink() or not path.is_file():
                raise ValueError("Unsafe, missing or linked raw phone log")
            inputs.append(path.open("r", encoding="utf8", errors="replace"))
        print("T5_OBB_GUID_CLASSIFICATION " + json.dumps(
            classify_streams(inputs, delivery=data), sort_keys=True))
    finally:
        for stream in inputs:
            stream.close()


if __name__ == "__main__":
    main()
