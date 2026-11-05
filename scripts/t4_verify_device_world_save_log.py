"""T4 source-free, privacy-preserving Android PersistentDiagnosticLog JSONL verifier.

This tool reports *only evidence*, never game readiness or recovered RGD
compatibility. It deliberately does not output raw filenames, session tokens,
exception strings, identifiers, or game data.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_FILES = 128
MAX_BYTES = 80 * 1024 * 1024
MAX_LINES = 500_000
MAX_LINE = 65_536

MARKERS = {
    ("startup", "logger.ready"): "startup",
    ("world", "WorldHasBeenLoaded.firstMoveNext"): "iterator_entry",
    ("world", "WorldHasBeenLoaded.originalCompletionAssigned"): "original_assignment",
    ("world", "OnWorldRecieved.enter"): "world_callback",
    ("world", "OnWorldRecieved.exception"): "callback_exception",
    ("save", "SaveGame.enter"): "savegame_entry",
    ("save", "SaveWorld.enter"): "saveworld_entry",
    ("save", "SaveUser.enter"): "saveuser_entry",
    ("save", "Save.argumentFileSnapshot"): "save_snapshot",
    ("save", "Save.argumentFileSnapshot.unavailable"): "save_unavailable",
    ("save", "Load.argumentFileSnapshot"): "load_snapshot",
    ("save", "Load.argumentFileSnapshot.unavailable"): "load_unavailable",
    ("save", "Load.caughtException"): "load_caught",
    ("save", "Load<T>.enter"): "load_entry",
    ("save", "Load<T>.exit"): "load_exit",
    ("logging", "queue_overflow"): "queue_overflow",
}
SNAPSHOT_DETAIL = re.compile(
    r"(?:^|;\s*)exists_at_filename_argument=(True|False)"
    r";\s*length_class=(zero|nonzero|not_checked)(?:;|$)"
)


class EvidenceInputError(ValueError):
    pass


def _paths(source):
    p = Path(source)
    if not p.exists() or p.is_symlink():
        raise EvidenceInputError("missing_or_linked_input")
    files = [p] if p.is_file() else sorted(p.rglob("*.jsonl"))
    if not files or len(files) > MAX_FILES:
        raise EvidenceInputError("invalid_file_count")
    if any(not f.is_file() or f.is_symlink() for f in files):
        raise EvidenceInputError("linked_or_invalid_file")
    if any(f.suffix != ".jsonl" for f in files):
        raise EvidenceInputError("only_jsonl_supported")
    if sum(f.stat().st_size for f in files) > MAX_BYTES:
        raise EvidenceInputError("input_bytes_limit")
    return files


def _parse_detail(text):
    if not isinstance(text, str):
        raise EvidenceInputError("invalid_detail_type")
    match = SNAPSHOT_DETAIL.search(text)
    if not match:
        return "unparseable"
    exists, size = match.groups()
    if exists == "False" and size == "not_checked":
        return "absent"
    if exists == "True" and size in ("zero", "nonzero"):
        return size
    return "contradictory"


def _parse_utc(text):
    if not isinstance(text, str):
        raise EvidenceInputError("invalid_timestamp")
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceInputError("invalid_timestamp") from exc
    if dt.tzinfo is None:
        raise EvidenceInputError("naive_timestamp")
    return dt.astimezone(timezone.utc)


def summarize(paths):
    """Never return raw detail, source path, session ID, timestamps or payload."""
    sessions = {}
    invalid_truncation = False
    total_lines = 0
    total_bytes = 0
    for file in paths:
        with file.open("rb") as handle:
            for raw in handle:
                total_lines += 1
                total_bytes += len(raw)
                if total_lines > MAX_LINES or total_bytes > MAX_BYTES or len(raw) > MAX_LINE:
                    raise EvidenceInputError("input_limit")
                try:
                    record = json.loads(raw)
                except (UnicodeDecodeError, ValueError) as exc:
                    raise EvidenceInputError("invalid_jsonl") from exc
                if not isinstance(record, dict):
                    raise EvidenceInputError("invalid_record")
                # Startup and rotated segment files may contain exactly the
                # same event. Duplicate sequence is accepted only if identical.
                if record.get("area") == "logging" and record.get("operation") == "queue_overflow":
                    invalid_truncation = True
                    continue
                session = record.get("session")
                seq = record.get("sequence")
                if not isinstance(session, str) or not session or len(session) > 120:
                    raise EvidenceInputError("missing_session")
                if type(seq) is not int or seq < 1:
                    raise EvidenceInputError("invalid_sequence")
                area = record.get("area")
                operation = record.get("operation")
                if not isinstance(area, str) or not isinstance(operation, str):
                    raise EvidenceInputError("invalid_operation")
                stamp = _parse_utc(record.get("utc"))
                # SHA is used *only internally* to disambiguate replayed lines.
                fp = hashlib.sha256(raw.rstrip(b"\r\n")).digest()
                group = sessions.setdefault(session, {
                    "seen": {}, "events": [], "first": stamp,
                    "last": stamp, "duplicate_count": 0,
                })
                if seq in group["seen"]:
                    if group["seen"][seq] != fp:
                        raise EvidenceInputError("conflicting_replayed_sequence")
                    group["duplicate_count"] += 1
                    continue
                group["seen"][seq] = fp
                group["first"] = min(group["first"], stamp)
                group["last"] = max(group["last"], stamp)
                marker = MARKERS.get((area, operation))
                if marker:
                    classification = (
                        _parse_detail(record.get("detail", ""))
                        if marker in ("save_snapshot", "load_snapshot")
                        else None
                    )
                    group["events"].append((seq, marker, classification))
    if not sessions:
        raise EvidenceInputError("no_session_records")
    ordered = sorted(sessions.values(), key=lambda x: (x["first"], x["last"]))
    out = []
    for index, group in enumerate(ordered, 1):
        ids = sorted(group["seen"])
        sequence_complete = ids[0] == 1 and ids[-1] == len(ids)
        entries = sorted(group["events"])
        counts = Counter(event for _, event, _ in entries)
        save_states = Counter(value for _, event, value in entries if event == "save_snapshot")
        load_states = Counter(value for _, event, value in entries if event == "load_snapshot")
        anomalies = []
        sequence_map = {event: min(seq for seq, m, _ in entries if m == event)
                        for event in counts}
        if "original_assignment" in sequence_map and "iterator_entry" in sequence_map:
            if sequence_map["original_assignment"] < sequence_map["iterator_entry"]:
                anomalies.append("assignment_precedes_iterator")
        if "load_caught" in counts and not counts.get("load_entry"):
            anomalies.append("load_caught_without_observed_load_entry")
        if not sequence_complete:
            anomalies.append("missing_or_rotated_sequence")
        if any(x in ("contradictory", "unparseable") for x in (*save_states, *load_states)):
            anomalies.append("unparseable_snapshot")
        out.append({
            "session_index": index,
            "sequence_complete": sequence_complete,
            "deduplicated_replay_lines": group["duplicate_count"],
            "marker_counts": dict(sorted(counts.items())),
            "save_argument_file_classes": dict(sorted(save_states.items())),
            "load_argument_file_classes": dict(sorted(load_states.items())),
            "anomalies": anomalies,
        })
    save_any = any(x["save_argument_file_classes"].get("nonzero", 0) for x in out[:-1])
    load_after = any(x["load_argument_file_classes"].get("nonzero", 0) for x in out[1:])
    return {
        "schema": 1,
        "analysis_type": "source_free_log_evidence_only",
        "session_count": len(out),
        "sessions": out,
        "at_least_two_logger_sessions": len(out) >= 2,
        "save_nonzero_in_earlier_session": bool(save_any),
        "load_nonzero_in_later_session": bool(load_after),
        "cross_session_same_world_proven": False,
        "process_restart_proven": False,
        "world_playability_proven": False,
        "real_rgd_durability_or_reopen_proven": False,
        "candidate_apk_source_sha_attested_by_logs": False,
        "logging_queue_overflow_observed": invalid_truncation,
        "local005_device_confirmed": False,
        "readiness_review_count": 0,
        "limitations": [
            "source_sha_and_apk_identity_require_external_signed_build_evidence",
            "two_logger_sessions_do_not_prove_process_restart_or_same_world",
            "snapshot_existence_does_not_prove_serialization_or_durability",
            "session_sequence_gaps_or_dropped_events_prevent_negative_inference",
            "owner_verified_playable_create_save_reopen_required",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Source-free Raft Android JSONL evidence classifier")
    parser.add_argument("--input", required=True, help="one JSONL file or a local JSONL directory")
    args = parser.parse_args(argv)
    try:
        result = summarize(_paths(args.input))
    except EvidenceInputError as exc:
        print(json.dumps({"schema": 1, "status": "untrusted_input",
                          "error_category": str(exc), "device_confirmed": False},
                         sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
