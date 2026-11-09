#!/usr/bin/env python3
"""T4 source-only triage: correlate captured callbacks with ORIGINAL Unity getters.

Input is one process-local chronological Raft log excerpt, NOT aggregated
mini-lab JSON. Epochs reset between app launches, so never concatenate runs.
The script never reports physical gameplay PASS or proves APK provenance.
"""
import argparse
import json
from pathlib import Path
import re

OPS = (
    "physical_mouse_capture_requested",
    "physical_mouse_capture_retry",
    "physical_mouse_capture_released",
    "physical_mouse_captured_action_callbacks",
    "physical_mouse_captured_action_callbacks_final",
    "physical_mouse_legacy_reader_evidence",
    "physical_mouse_legacy_reader_evidence_final",
)
OP_RE = re.compile(r"(?<![A-Za-z_])(" + "|".join(OPS) + r")(?![A-Za-z_])")
EPOCH_RE = re.compile(r"(?<![A-Za-z_])epoch=(\d+)(?!\d)")
MAX_BYTES = 16 * 1024 * 1024
MAX_LINES = 200000


def decode_record(line):
    """Decode a source marker and its PersistentDiagnosticLog provenance.

    The actual C# sink emits JSONL session + sequence for *every* record.
    An older text excerpt without those fields remains legacy/unattributed;
    it cannot combine with an attributed logger record. No session ID leaks.
    """
    if isinstance(line, dict):
        op = line.get("operation")
        detail = line.get("detail", "")
        fields = ("session", "sequence", "utc", "thread")
        if any(key in line for key in fields):
            session, seq = line.get("session"), line.get("sequence")
            valid = (isinstance(session, str) and 1 <= len(session) <= 128
                     and type(seq) is int and 0 < seq < 2**63)
            scope = ("jsonl", session) if valid else ("invalid", "")
            seq = seq if valid else None
        else:
            valid = True
            scope = ("legacy", "")
            seq = None
        if op not in OPS:
            return None, "", scope, seq, valid
        if (not isinstance(detail, str) or
                ("area" in line and line["area"] != "input")):
            return op, "", scope, seq, False
        return op, detail, scope, seq, valid
    if not isinstance(line, str):
        return None, "", ("invalid", ""), None, False
    if line.lstrip().startswith("{"):
        try:
            return decode_record(json.loads(line))
        except (json.JSONDecodeError, TypeError, ValueError):
            return None, "", ("invalid", ""), None, False
    hits = OP_RE.findall(line)
    if len(hits) == 1:
        return hits[0], line, ("legacy", ""), None, True
    return None, "", ("legacy", ""), None, True


def decode(line):
    """Legacy two-value decoder retained for existing read-only callers."""
    op, detail, _, _, valid = decode_record(line)
    return (op, detail) if valid else (None, "")


def parse_counter(detail, field):
    matches = re.findall(r"(?<![A-Za-z_])" + re.escape(field) +
                         r"=(\d+)(?!\d)", detail)
    if len(matches) != 1:
        return None
    return int(matches[0])


def parse_bool(detail, field):
    matches = re.findall(r"(?<![A-Za-z_])" + re.escape(field) +
                         r"=(true|false)(?![A-Za-z_])", detail)
    return matches[0] == "true" if len(matches) == 1 else None


def triage(lines):
    attempts = []
    active = None
    unpaired = 0
    invalid = 0
    provenance_mismatches = 0
    last_sequence = {}
    poisoned_logger_sessions = set()
    for raw in lines:
        op, detail, scope, sequence, valid = decode_record(raw)
        if scope[0] == "jsonl" and valid:
            # One actual logger session has strictly increasing sequence IDs
            # even across rotated segments; duplicated startup/raft records
            # or mixed app-process logs must never become one proof.
            prior = last_sequence.get(scope)
            if prior is not None and sequence <= prior:
                poisoned_logger_sessions.add(scope)
                invalid += 1
            else:
                last_sequence[scope] = sequence
        if active is not None and scope != active["scope"]:
            # Even unrelated JSONL operations can mark an app-logger
            # session transition, so close the prior open capture attempt.
            provenance_mismatches += 1
            active = None
        if not valid:
            if op is not None:
                invalid += 1
            continue
        if not op:
            continue
        if op == "physical_mouse_capture_released":
            active = None
            continue
        epochs = EPOCH_RE.findall(detail)
        if len(epochs) != 1:
            invalid += 1
            continue
        epoch = int(epochs[0])
        if op in OPS[:2]:
            # Retried capture supersedes an earlier generation, even if it
            # had unread evidence. Preserve it as a separate attempt.
            active = {"epoch": epoch, "scope": scope,
                      "callbacks": None, "readers": None,
                      "invalid": False, "operation": op}
            attempts.append(active)
            continue
        if active is None or active["epoch"] != epoch:
            unpaired += 1
            continue
        if op.startswith("physical_mouse_captured_action_callbacks"):
            wanted = ("capturedCallbackEvents", "pressCallbacks", "releaseCallbacks",
                      "verticalScrollCallbacks", "horizontalScrollCallbacks")
            data = {key: parse_counter(detail, key) for key in wanted}
            if any(value is None for value in data.values()) or (
                    "unityButtonsAndWheelVerified=false" not in detail):
                active["invalid"] = True
                invalid += 1
                continue
            old = active["callbacks"]
            if old is not None and any(data[key] < old[key] for key in wanted):
                active["invalid"] = True
                invalid += 1
            else:
                active["callbacks"] = data
        elif op.startswith("physical_mouse_legacy_reader_evidence"):
            wanted = ("getterCalls", "positiveLegacy", "positiveFallback",
                      "positiveEdges", "positiveScroll")
            data = {key: parse_counter(detail, key) for key in wanted}
            if (any(value is None for value in data.values()) or
                    parse_bool(detail, "captureRequested") is not True or
                    parse_bool(detail, "captureObserved") is not True or
                    parse_bool(detail, "unityGameplayVerified") is not False or
                    parse_bool(detail, "countersAreGetterCallsNotClicks") is not True):
                active["invalid"] = True
                invalid += 1
                continue
            if data["positiveFallback"] + data["positiveLegacy"] > data["getterCalls"]:
                active["invalid"] = True
                invalid += 1
                continue
            old = active["readers"]
            if old is not None and any(data[key] < old[key] for key in wanted):
                active["invalid"] = True
                invalid += 1
            else:
                active["readers"] = data

    eligible = [a for a in attempts if not a["invalid"] and
                a["scope"] not in poisoned_logger_sessions]
    matched = [a for a in eligible if a["callbacks"] is not None
               and a["readers"] is not None and a["callbacks"]["capturedCallbackEvents"] > 0
               and a["readers"]["getterCalls"] > 0]
    matching_fallback = [
        a for a in matched if a["readers"]["positiveFallback"] > 0
    ]
    callbacks_only = sum(bool(a["callbacks"] and
                              a["callbacks"]["capturedCallbackEvents"] > 0 and
                              not a["readers"]) for a in eligible)
    reader_only = sum(bool(a["readers"] and
                           a["readers"]["getterCalls"] > 0 and
                           not a["callbacks"]) for a in attempts if not a["invalid"])
    if matching_fallback:
        status = "SAME_EPOCH_CAPTURED_CALLBACK_AND_FALLBACK_GETTER"
    elif matched:
        status = "SAME_EPOCH_CALLBACK_AND_GETTER_NO_FALLBACK"
    elif callbacks_only:
        status = "CAPTURED_CALLBACK_WITHOUT_SAME_EPOCH_GETTER"
    elif reader_only:
        status = "UNITY_GETTER_WITHOUT_SAME_EPOCH_CALLBACK"
    else:
        status = "NO_SAME_EPOCH_CORRELATION"
    # A malformed attempt cannot be silently outweighed by a later snapshot.
    if invalid and not matching_fallback and not matched:
        status = "INVALID_OR_INCOMPLETE_CAPTURE_PROVENANCE"
    return {
        "status": status,
        "attempts": len(attempts),
        "same_epoch_callback_and_getter_attempts": len(matched),
        "same_epoch_positive_fallback_attempts": len(matching_fallback),
        "callback_only_attempts": callbacks_only,
        "getter_only_attempts": reader_only,
        "unpaired_epoch_markers": unpaired,
        "invalid_markers": invalid,
        "logger_sessions_scanned": len(last_sequence),
        "poisoned_logger_sessions": len(poisoned_logger_sessions),
        "provenance_scope_mismatches": provenance_mismatches,
        "matched_jsonl_scoped_attempts": sum(
            a["scope"][0] == "jsonl" for a in matched),
        "matched_unattributed_legacy_attempts": sum(
            a["scope"][0] == "legacy" for a in matched),
        "epochs_with_both": sorted({a["epoch"] for a in matched}),
        "unity_gameplay_verified": False,
        "device_pass": False,
        "limitations": ("Single chronological app-process log only; epoch may repeat across "
                        "launches. PersistentDiagnosticLog session plus strictly increasing "
                        "sequence prevents cross-logger false positives but does not prove "
                        "process identity, APK signature or gameplay. Counters are getter "
                        "invocations, not unique physical clicks; device acceptance unverified."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path,
                        help="One process-local chronological Raft text/JSONL log")
    args = parser.parse_args()
    path = args.log
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        parser.error("log missing, linked or beyond size budget")
    def lines():
        with path.open(encoding="utf-8", errors="replace") as stream:
            for idx, line in enumerate(stream, 1):
                if idx > MAX_LINES:
                    raise ValueError("log row budget exceeded")
                yield line
    print(json.dumps(triage(lines()), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
