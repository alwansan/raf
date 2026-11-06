"""Read-only, privacy-safe chronology of pinned real 5-Nov Raft owner JSONL logs.

No filenames, paths, logger session tokens, user identities, exception details,
original .rgd content or source are returned. Log markers are hints, not phone
acceptance or authentic save-deserialization proof.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from scripts.t4_verify_device_world_save_log import (
    EvidenceInputError, _strict_json_object, _strict_json_constant,
    _parse_utc, summarize,
)

# File byte sizes are public fixed non-content provenance checks on the exact
# immutable CL@520c4cf phone snapshot. Nothing is fetched by this module.
PINNED_BYTES = (869991, 499456, 1443270)
PINNED_GIT_BLOBS = (
    "28264b50a5a8aaefefb3bdd0256f0869c79e6116",
    "413932e92fc24cd50b1fae1cbb25120f392e8158",
    "60674be571e4979e329924e5e2679f43e40ec41a",
)

TRACKED = {
    ("world", "WorldHasBeenLoaded.firstMoveNext"): "iterator_first_move_next",
    ("world", "WorldHasBeenLoaded.originalCompletionAssigned"): "world_ready_assignment",
    ("world", "OnWorldRecieved.enter"): "on_world_received_enter",
    ("world", "OnWorldRecieved.exit"): "on_world_received_exit",
    ("save", "SaveGame.enter"): "savegame_enter",
    ("save", "SaveGame.exit"): "savegame_exit",
    ("save", "SaveWorld.enter"): "saveworld_enter",
    ("save", "SaveWorld.exit"): "saveworld_exit",
    ("save", "SaveUser.enter"): "saveuser_enter",
    ("save", "SaveUser.exit"): "saveuser_exit",
    ("save", "Save.enter"): "save_enter",
    ("save", "Save.exit"): "save_exit",
    ("save", "Save.argumentFileSnapshot"): "save_file_snapshot",
    ("save", "Load<T>.enter"): "load_enter",
    ("save", "Load<T>.exit"): "load_exit",
    ("save", "Load.argumentFileSnapshot"): "load_file_snapshot",
    ("save", "Load.caughtException"): "load_caught_exception",
    ("save", "RestoreRGDGame.enter"): "restore_world_enter",
    ("save", "RestoreRGDGame.exit"): "restore_world_exit",
    ("save", "RestoreUser.enter"): "restore_user_enter",
    ("save", "RestoreUser.exit"): "restore_user_exit",
}
EXPECTED_ORIGINAL_ORDER = (
    ("iterator_first_move_next", "world_ready_assignment"),
    ("on_world_received_enter", "on_world_received_exit"),
    ("savegame_enter", "savegame_exit"),
    ("saveworld_enter", "saveworld_exit"),
    ("saveuser_enter", "saveuser_exit"),
    ("load_enter", "load_exit"),
    ("restore_world_enter", "restore_world_exit"),
    ("restore_user_enter", "restore_user_exit"),
)


def analyze(paths, pinned=False):
    files = sorted(Path(p) for p in paths)
    if not files or len(files) > 3 or any(not p.is_file() or p.is_symlink() for p in files):
        raise EvidenceInputError("invalid_owner_log_files")
    if pinned:
        if len(files) != 3 or tuple(p.stat().st_size for p in files) != PINNED_BYTES:
            raise EvidenceInputError("unverified_pinned_owner_log_bytes")
        # Immutable commit in the workflow is the first provenance layer; also
        # authenticate each Git blob independently so a local --pinned call
        # cannot pass a same-sized synthetic JSONL file as genuine owner data.
        for path, expected in zip(files, PINNED_GIT_BLOBS):
            payload = path.read_bytes()
            digest = hashlib.sha1(
                b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
            ).hexdigest()
            if digest != expected:
                raise EvidenceInputError("unverified_pinned_owner_log_git_blob")
    base = summarize(files)
    groups = {}
    for path in files:
        with path.open("rb") as stream:
            for raw in stream:
                record = json.loads(raw, object_pairs_hook=_strict_json_object,
                                    parse_constant=_strict_json_constant)
                # summarize already validated this session-free queue marker.
                if record.get("area") == "logging" and record.get("operation") == "queue_overflow":
                    continue
                session, seq = record["session"], record["sequence"]
                utc = _parse_utc(record["utc"])
                group = groups.setdefault(session, {
                    "first": utc, "last": utc, "seen": set(), "events": [],
                })
                group["first"] = min(group["first"], utc)
                group["last"] = max(group["last"], utc)
                if seq in group["seen"]:
                    continue  # base.summarize rejected conflicting replay lines.
                group["seen"].add(seq)
                marker = TRACKED.get((record["area"], record["operation"]))
                if marker is not None:
                    group["events"].append((seq, marker))
    ordered = sorted(groups.values(), key=lambda g: (g["first"], g["last"]))
    if len(ordered) != base["session_count"]:
        raise EvidenceInputError("inconsistent_session_census")
    sessions = []
    for i, (group, base_row) in enumerate(zip(ordered, base["sessions"]), 1):
        events = sorted(group["events"])
        counts = Counter(marker for _, marker in events)
        first_seq = {key: min(seq for seq, marker in events if marker == key)
                     for key in counts}
        chronological = {
            left + "_before_" + right:
            bool(left in counts and right in counts and first_seq[left] < first_seq[right])
            for left, right in EXPECTED_ORIGINAL_ORDER
        }
        sessions.append({
            "session_index": i,
            "complete_sequence": base_row["sequence_complete"],
            "utc_monotonic": base_row["utc_monotonic"],
            "original_operation_counts": dict(sorted(counts.items())),
            "original_stage_order_hints": chronological,
            "save_nonzero_file_snapshots": base_row["save_argument_file_classes"].get("nonzero", 0),
            "load_nonzero_file_snapshots": base_row["load_argument_file_classes"].get("nonzero", 0),
            "load_caught_exception_count": base_row["marker_counts"].get("load_caught", 0),
            "queue_or_sequence_warning": bool(
                base["logging_queue_overflow_observed"] or not base_row["sequence_complete"]
                or not base_row["utc_monotonic"]),
        })
    return {
        "schema": 1,
        "evidence_type": "pinned_owner_5nov_raw_runtime_marker_census",
        "source_pin": "CL_520c4cf_2026_11_05" if pinned else "unverified_synthetic_source",
        "session_count": len(sessions),
        "sessions": sessions,
        "save_nonzero_in_earlier_session_hint": base["save_nonzero_in_earlier_session"],
        "load_nonzero_in_later_session_hint": base["load_nonzero_in_later_session"],
        "logging_queue_overflow_observed": base["logging_queue_overflow_observed"],
        "same_world_proven": False,
        "process_restart_proven": False,
        "original_rgd_deserialization_success_proven": False,
        "durable_rgd_reopen_proven": False,
        "new_candidate_source_sha_proven": False,
        "current_android_device_acceptance_proven": False,
        "raw_owner_data_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pinned original phone logger marker census")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--pinned", action="store_true")
    args = parser.parse_args(argv)
    try:
        files = sorted(args.root.glob("raft-*.jsonl"))
        result = analyze(files, pinned=args.pinned)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        # Never emit an owner filename, ID, private logging detail or traceback.
        print(json.dumps({"schema": 1, "status": "untrusted_input",
                          "device_acceptance_proven": False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
