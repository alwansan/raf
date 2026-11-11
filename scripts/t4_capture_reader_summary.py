#!/usr/bin/env python3
"""Summarize aggregate Android pointer-capture and Unity legacy reader markers.

Does not infer gameplay success from telemetry. Use one build/process log only.
"""
import argparse
import json
import re
import zipfile
from contextlib import contextmanager
from pathlib import Path
import io

CALLBACK = "physical_mouse_captured_action_callbacks"
READER = "physical_mouse_legacy_reader_evidence"
MARKER_BOUNDARY = re.compile(r"(?<![A-Za-z0-9_])(?:%s)(?![A-Za-z0-9_])" % "|".join((CALLBACK, READER)))
NUM = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]*)=(\d+)(?=;|\s|$)")


def summarize(lines):
    counts = {CALLBACK: 0, READER: 0}
    last = {CALLBACK: {}, READER: {}}
    maxima = {CALLBACK: {}, READER: {}}
    first = {CALLBACK: {}, READER: {}}
    monotonic_increases = {CALLBACK: {}, READER: {}}
    resets = {CALLBACK: 0, READER: 0}
    for line in lines:
        for match in MARKER_BOUNDARY.finditer(line):
            marker = match.group(0)
            counts[marker] += 1
            # Stop at another marker: never attribute its counters to this report.
            next_marker = MARKER_BOUNDARY.search(line, match.end())
            tail = line[match.end():next_marker.start() if next_marker else len(line)]
            snapshot = {k: int(v) for k, v in NUM.findall(tail)}
            for key, value in snapshot.items():
                if key not in first[marker]:
                    first[marker][key] = value
                if key in last[marker] and value > last[marker][key]:
                    monotonic_increases[marker][key] = monotonic_increases[marker].get(key, 0) + value - last[marker][key]
                if key in last[marker] and value < last[marker][key]:
                    resets[marker] += 1
                maxima[marker][key] = max(maxima[marker].get(key, 0), value)
            # Reports may omit unchanged counters. Preserve their last observed
            # values instead of treating omission as a reset or zero.
            # Snapshots are cumulative, never sum them across reports.
            last[marker].update(snapshot)
    if not counts[CALLBACK]:
        verdict = "no_callback_marker_observed"
    elif not counts[READER]:
        verdict = "callbacks_observed_readers_not_observed"
    else:
        verdict = "both_markers_observed_no_gameplay_proof"
    return {
        "callback_reports": counts[CALLBACK],
        "reader_reports": counts[READER],
        "last_callback_counters": last[CALLBACK],
        "last_reader_counters": last[READER],
        "first_callback_counters": first[CALLBACK],
        "first_reader_counters": first[READER],
        "monotonic_callback_increases": monotonic_increases[CALLBACK],
        "monotonic_reader_increases": monotonic_increases[READER],
        "max_callback_counters": maxima[CALLBACK],
        "max_reader_counters": maxima[READER],
        "callback_counter_decreases": resets[CALLBACK],
        "reader_counter_decreases": resets[READER],
        "diagnostic_state": verdict,
        "gameplay_success_proven": False,
        "note": "Monotonic increases exclude first observations and reset drops; they are not proof of causal delivery. Missing markers may reflect logging thresholds, absent instrumentation, or different app sessions. Compare only the same build/process.",
    }


@contextmanager
def open_log(path, member=None):
    """Read one bounded text member, never combine sessions from an archive."""
    if not zipfile.is_zipfile(path):
        if member:
            raise ValueError('--member requires a ZIP archive')
        with path.open(encoding='utf-8', errors='replace') as handle:
            yield handle
        return
    with zipfile.ZipFile(path) as archive:
        candidates = [entry for entry in archive.infolist()
                      if not entry.is_dir() and entry.filename.lower().endswith(('.log', '.txt'))]
        if member:
            candidates = [entry for entry in candidates if entry.filename == member]
        if len(candidates) != 1:
            raise ValueError('ZIP requires exactly one .log/.txt member; select with --member')
        entry = candidates[0]
        if entry.file_size > 64 * 1024 * 1024:
            raise ValueError('ZIP log member exceeds 64 MiB safety limit')
        with archive.open(entry) as raw:
            with io.TextIOWrapper(raw, encoding='utf-8', errors='replace') as handle:
                yield handle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--member", help="Exact .log/.txt member path inside ZIP")
    args = parser.parse_args()
    with open_log(args.log, args.member) as handle:
        print(json.dumps(summarize(handle), indent=2))


if __name__ == "__main__":
    main()
