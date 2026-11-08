#!/usr/bin/env python3
"""Audit only the first owner-phone Logcat roots and their nearby trace hints.

Never disclose original log lines, stack text, game identifiers or private
assets. SHA-pinned CL raw bytes and summary must BOTH match before reporting.
A nearby class/API mention is not a proven C# caller or Unity FFT kernel.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.t1_water_logcat_first_roots import classify
from scripts.t1_water_startup_order import analyze, load_summary

CL_COMMIT = "61f71ceb3b9e6f16c8fb300656f6e6baf32b33e8"
SEGMENT_SHA1 = "bf5db2607e3b46165d39142aa28f6596ed0715d4"
SEGMENT_SIZE = 33549006
SUMMARY_SHA256 = "941d37d4b18a2bf11471098bd0668029add11913d76b0a97086dd9fb185e7ff7"
MAX_LINE = 32768
MAX_SCAN = 35_000_000
NEARBY_LINES = 12
NEARBY_MS = 100
TARGETS = ("kernel_index_6", "pass_spectrum", "pass_foam_global", "pass_other_water")
THREAD_LINE = re.compile(
    rb"(?<!\d)(11-08\x20\d\d:\d\d:\d\d\.\d{3})\s+"
    rb"(\d{1,8})\s+(\d{1,8})\s+[VDIWEF]\s+")
HINTS = {
    "dx11fft": re.compile(rb"\bDx11FFT\b", re.I),
    "unity_compute_dispatch": re.compile(rb"\bComputeShader\s*\.\s*Dispatch\b", re.I),
    "unity_compute_findkernel": re.compile(rb"\bComputeShader\s*\.\s*FindKernel\b", re.I),
    "ultimate_water": re.compile(rb"\bUltimate\s*Water\b|\bUltimateWater\b", re.I),
    "spectrum": re.compile(rb"\bSpectrum\b", re.I),
    "foam_global": re.compile(rb"\bFoam[ _-]*Global\b", re.I),
}
BAGHDAD = timezone(timedelta(hours=3))
# LogRaft's own ISO-date lines often omit canonical Android PID/TID fields.
# Parse their timestamp without inventing a thread identity.
ISO_DATE = re.compile(rb"(?<!\d)2026-11-08[T ](\d\d:\d\d:\d\d\.\d{3})(?!\d)")

# Coarse format and keyword PRESENCE counters only; no extracted raw text.
FORMAT_PROBES = {
    "threadtime": THREAD_LINE,
    "mmdd_clock": re.compile(rb"11-08\s+\d\d:\d\d:\d\d\.\d{3}"),
    "yyyy_mm_dd": re.compile(rb"2026[-/]11[-/]08"),
    "date_hyphen": re.compile(rb"2026-11-08"),
    "date_slash": re.compile(rb"2026/11/08"),
    "date_hms_within_40": re.compile(rb"2026[-/]11[-/]08.{0,40}\d\d:\d\d:\d\d"),
    "slash_date_clock": re.compile(rb"2026/11/08[T ]\d\d:\d\d:\d\d"),
    "local_first_water_clock": re.compile(rb"16:49:17"),
    "utc_first_water_clock": re.compile(rb"13:49:17"),
    "android_unity_tag": re.compile(rb"\bUnity\b"),
    "does_not_have_pass": re.compile(rb"does\s+not\s+have\s+(?:a\s+)?pass", re.I),
    "epoch_unix_ms": re.compile(rb"17941457\d{5}"),
    "iso_clock": re.compile(rb"\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d"),
    "kernel_word": re.compile(rb"\bkernel\b", re.I),
    "invalid_word": re.compile(rb"\binvalid\b", re.I),
    "kernel_and_invalid": re.compile(rb"(?=.*\bkernel\b)(?=.*\binvalid\b)", re.I),
    "index_and_six": re.compile(rb"\bindex\W{0,12}6(?:\D|$)", re.I),
    "dx11fft_token": re.compile(rb"\bDx11FFT\b", re.I),
    "compute_shader_token": re.compile(rb"\bComputeShader\b", re.I),
}



def _regular_fd(path, expected_size):
    path = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    elif path.is_symlink():
        raise ValueError("symlink log source")
    fd = os.open(path, flags)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_size != expected_size or not 0 < expected_size <= MAX_SCAN:
        os.close(fd)
        raise ValueError("invalid log size or file type")
    return fd, info


def _unchanged(fd, before):
    after = os.fstat(fd)
    if ((before.st_size, before.st_mtime_ns, before.st_ctime_ns) !=
            (after.st_size, after.st_mtime_ns, after.st_ctime_ns)):
        raise ValueError("original log changed during read")


def authenticate_raw(path, expected_size=SEGMENT_SIZE, expected_blob=SEGMENT_SHA1):
    """Verify actual Git blob SHA1, not merely a filename or a public URL."""
    if not isinstance(expected_blob, str) or not re.fullmatch(r"[0-9a-f]{40}", expected_blob):
        raise ValueError("bad expected Git blob fingerprint")
    fd, before = _regular_fd(path, expected_size)
    try:
        digest = hashlib.sha1(("blob %d\0" % expected_size).encode("ascii"))
        remaining = expected_size
        while remaining:
            piece = os.read(fd, min(256 * 1024, remaining))
            if not piece:
                raise ValueError("short original log")
            digest.update(piece)
            remaining -= len(piece)
        if os.read(fd, 1):
            raise ValueError("original log grew")
        _unchanged(fd, before)
        if digest.hexdigest() != expected_blob:
            raise ValueError("original Git blob fingerprint mismatch")
    finally:
        os.close(fd)


def _stamp_ms(stamp):
    # LogRaft session and its original Logcat threadtime lines use phone-local
    # Nov 8 timestamps. The timezone conversion is source-specific, not a
    # universal Android log time inference.
    try:
        raw = stamp.decode("ascii")
        dt = datetime.strptime("2026-" + raw, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=BAGHDAD)
        return int(dt.timestamp() * 1000)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("malformed original Logcat timestamp") from exc


def _metadata(line):
    match = THREAD_LINE.search(line[:256])
    if match:
        return _stamp_ms(match.group(1)), int(match.group(2)), int(match.group(3))
    iso = ISO_DATE.search(line[:256])
    if iso:
        # PID/TID unknown, therefore any nearby stack mention remains unpaired.
        return _stamp_ms(b"11-08 " + iso.group(1)), None, None
    return None


def _hintset(line):
    return {label for label, pattern in HINTS.items() if pattern.search(line)}


def classify_first_roots(path, expected_size=SEGMENT_SIZE):
    """Extract only redacted first root metadata and bounded nearby hints.

    Adjacent hints are recorded as UNATTRIBUTED even with the same thread. No
    call chain is assumed from proximity; explicit actual captured stack is
    required to establish the original Unity caller.
    """
    fd, before = _regular_fd(path, expected_size)
    found = {}
    counters = {key: 0 for key in TARGETS}
    malformed_roots = 0
    oversize_lines = 0
    total = 0
    formats = {name: 0 for name in FORMAT_PROBES}
    try:
        with os.fdopen(fd, "rb", buffering=1024 * 128) as stream:
            fd = -1
            for raw in iter(lambda: stream.readline(MAX_LINE + 1), b""):
                if len(raw) > MAX_LINE or (len(raw) == MAX_LINE and not raw.endswith(b"\n")):
                    oversize_lines += 1
                    while raw and not raw.endswith(b"\n"):
                        raw = stream.readline(MAX_LINE + 1)
                    continue
                total += 1
                for name, pattern in FORMAT_PROBES.items():
                    if pattern.search(raw):
                        formats[name] += 1
                metadata = _metadata(raw)
                # Find source-independent, finite adjacency of previously
                # observed root lines on the same Android Logcat thread.
                if metadata is not None:
                    stamp, pid, tid = metadata
                    hints = _hintset(raw)
                    for entry in found.values():
                        delta = stamp - entry["_unix_ms"]
                        if (pid is not None and tid is not None and
                                0 <= total - entry["_source_line"] <= NEARBY_LINES and
                                0 <= delta <= NEARBY_MS and pid == entry["_pid"] and tid == entry["_tid"]):
                            entry["_nearby"].update(hints)
                            if hints:
                                entry["_nearby_lines"] += 1
                # Reuse the existing classifier; do not invent FFT ownership.
                kind = classify(raw.decode("utf-8", "replace"))
                if kind == "pass_other_water" and HINTS["foam_global"].search(raw):
                    kind = "pass_foam_global"
                if kind not in counters:
                    continue
                counters[kind] += 1
                if kind in found:
                    continue
                if metadata is None:
                    malformed_roots += 1
                    continue
                stamp, pid, tid = metadata
                found[kind] = {
                    "_source_line": total, "_unix_ms": stamp, "_pid": pid, "_tid": tid,
                    "_direct": _hintset(raw), "_nearby": set(), "_nearby_lines": 0,
                }
            _unchanged(stream.fileno(), before)
    finally:
        if fd >= 0:
            os.close(fd)
    return {
        "first": {key: {
            "unix_ms": data["_unix_ms"],
            "first_root_line_number": data["_source_line"],
            "android_thread_id_proven": data["_pid"] is not None and data["_tid"] is not None,
            "direct_same_logcat_line_allowlist_hints": {
                hint: hint in data["_direct"] for hint in HINTS
            },
            "nearby_same_pid_tid_100ms_12lines_unattributed_hints": {
                hint: hint in data["_nearby"] for hint in HINTS
            },
            "nearby_allowlist_mention_line_count": data["_nearby_lines"],
        } for key, data in sorted(found.items())},
        "observed_first_segment_category_counts": counters,
        "bounded_logcat_lines_examined": total,
        "oversize_physical_lines_skipped": oversize_lines,
        "unparseable_first_root_lines": malformed_roots,
        "raw_format_token_presence": formats,
        "raw_root_text_exported": False,
        "actual_original_unity_findkernel_proven": False,
        "actual_original_unity_dispatch_caller_proven": False,
        "same_thread_adjacency_is_causality": False,
    }


def combine(root_report, summary, summary_checksum=SUMMARY_SHA256):
    """Compare original raw root timestamps with full-session pinned summary."""
    if summary_checksum != SUMMARY_SHA256:
        raise ValueError("summary SHA256 mismatch")
    source = analyze(summary, source_commit=CL_COMMIT, input_sha256=summary_checksum)
    first = root_report["first"]
    kernel = first.get("kernel_index_6")
    materials = [first.get(name) for name in ("pass_spectrum", "pass_foam_global", "pass_other_water")]
    matched = [m for m in materials if m is not None]
    if kernel is None or not matched:
        raise ValueError("missing first original kernel or water root in first segment")
    expected_water = summary["final_error_category_breakdown"]["ultimate_water_invalid_pass"]["first_observed_unix_ms"]
    expected_kernel = summary["final_error_category_breakdown"]["water_fft_invalid_compute_kernel"]["first_observed_unix_ms"]
    actual_water = min(m["unix_ms"] for m in matched)
    if actual_water != expected_water or kernel["unix_ms"] != expected_kernel:
        raise ValueError("first raw roots disagree with pinned whole-session summary")
    return {
        "schema": 1,
        "cl_commit": CL_COMMIT,
        "raw_first_segment_git_blob_sha1_verified": True,
        "raw_first_segment_expected_sha1": SEGMENT_SHA1,
        "pinned_summary_sha256_verified": True,
        "first_water_unix_ms": actual_water,
        "first_kernel6_unix_ms": kernel["unix_ms"],
        "first_kernel_after_first_water_ms": kernel["unix_ms"] - actual_water,
        "first_water_before_world_loaded_ms": source["timing_ms"]["first_water_before_world_loaded"],
        "first_kernel_before_world_loaded_ms": source["timing_ms"]["first_fft_before_world_loaded"],
        "context": root_report,
        "interpretation": {
            "context_tokens_allowlist_only": True,
            "first_error_hints_are_not_original_kernel_names": True,
            "raw_log_line_neighborhood_not_proof_of_shared_callsite": True,
            "unity_shaders_restored": False,
            "on_phone_runtime_dispatch_proven": False,
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("first_segment", type=Path)
    p.add_argument("summary", type=Path)
    a = p.parse_args()
    phase = "raw-auth"
    try:
        authenticate_raw(a.first_segment)
        phase = "summary-auth"
        summary, ignored, checksum = load_summary(a.summary)
        if checksum != SUMMARY_SHA256:
            raise ValueError("unknown session summary")
        if ignored:
            raise ValueError("non-authoritative summary duplicate changed")
        phase = "raw-root-classification"
        raw_report = classify_first_roots(a.first_segment)
        phase = "raw-summary-crosscheck"
        try:
            report = combine(raw_report, summary, checksum)
        except ValueError:
            # Failure diagnostics contain only fixed category names, observed
            # numeric timestamps and counters; absolutely no original lines,
            # private stack frames, game paths, or raw identifier strings.
            redacted = {
                "observed_first_unix_ms": {
                    name: entry["unix_ms"] for name, entry in raw_report["first"].items()
                },
                "root_counts": raw_report["observed_first_segment_category_counts"],
                "raw_format_token_presence": raw_report["raw_format_token_presence"],
                "unparseable_first_root_lines": raw_report["unparseable_first_root_lines"],
                "expected_water_unix_ms":
                    summary["final_error_category_breakdown"]
                           ["ultimate_water_invalid_pass"]["first_observed_unix_ms"],
                "expected_kernel_unix_ms":
                    summary["final_error_category_breakdown"]
                           ["water_fft_invalid_compute_kernel"]["first_observed_unix_ms"],
            }
            print("RAFT_T1_SAFE_RAW_SUMMARY_MISMATCH " +
                  json.dumps(redacted, sort_keys=True), file=sys.stderr)
            raise
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        # Report only a fixed-phase name and generic exception class, NEVER
        # original proprietary log body or a private stack trace.
        p.exit(2, "T1 first original root context unavailable at " + phase +
               ": " + type(exc).__name__ + "\n")
    print("RAFT_T1_FIRST_RAW_LOGCAT_CONTEXT " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
