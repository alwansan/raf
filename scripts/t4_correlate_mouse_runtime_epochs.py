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
# Unity's epoch is a signed C# int, callback counters are C# int, and
# aggregate Legacy getter counters use C# long. Numeric spelling in the
# original logger is ASCII decimal, terminated by ';', ',' or whitespace.
EPOCH_RE = re.compile(r"(?<![A-Za-z0-9_])epoch=([0-9]{1,10})(?=$|[;,\s])")
EPOCH_KEY_RE = re.compile(r"(?<![A-Za-z0-9_])epoch=")
MAX_INT32 = 2**31 - 1
MAX_INT64 = 2**63 - 1
MAX_BYTES = 16 * 1024 * 1024
MAX_LINES = 200000
SLOT_NAMES = ("held0", "held1", "held2", "down0", "down1", "down2",
              "up0", "up1", "up2", "scrollAxis", "scrollVector")
BUTTON_NAMES = ("left", "right", "middle")


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
            # Attributed evidence must carry the complete original JSONL
            # envelope, not merely caller-supplied session/sequence labels.
            valid = (isinstance(session, str) and 1 <= len(session) <= 128
                     and type(seq) is int and 0 < seq < 2**63
                     and isinstance(line.get("utc"), str)
                     and bool(line["utc"].strip())
                     and type(line.get("thread")) is int
                     and line["thread"] >= 0
                     and line.get("area") == "input")
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
    # Bound before int(): a multi-thousand-digit JSONL token must become
    # invalid evidence, not an interpreter ValueError or giant integer.
    prefix = r"(?<![A-Za-z0-9_])" + re.escape(field) + r"="
    if len(re.findall(prefix, detail)) != 1:
        return None
    match = re.search(prefix + r"([0-9]{1,19})(?=$|[;,\s])", detail)
    if match is None:
        return None
    value = int(match.group(1))
    return value if value <= MAX_INT64 else None


def parse_bool(detail, field):
    # Actual C# Boolean.ToString() emits True/False for concatenated
    # runtime fields; the original source's *literal* flags are lowercase.
    # Accept only those two source spellings, with strict token boundaries.
    prefix = r"(?<![A-Za-z0-9_])" + re.escape(field) + r"="
    if len(re.findall(prefix, detail)) != 1:
        return None
    match = re.search(prefix + r"(True|False|true|false)(?=$|[;,\s])", detail)
    return match.group(1) in ("True", "true") if match else None


def parse_reader_slots(detail, totals):
    """Verify the complete original C# Report() ledger; never infer missing slots.

    Returns (slots, invalid). Old abbreviated logs stay eligible for aggregate
    triage, but can never produce channel-specific correlation.
    """
    result = {}
    for name in SLOT_NAMES:
        prefix = r"(?<![A-Za-z0-9_])" + re.escape(name) + r"Calls="
        occurrences = len(re.findall(prefix, detail))
        if occurrences > 1:
            return None, True
        if not occurrences:
            return None, False
        pattern = (prefix + r"([0-9]{1,10}),legacy=([0-9]{1,10}),"
                   r"fallback=([0-9]{1,10})(?=$|[;,\s])")
        matches = re.findall(pattern, detail)
        if len(matches) != 1:
            return None, True
        values = tuple(int(item) for item in matches[0])
        if any(v > MAX_INT32 for v in values) or values[1] + values[2] > values[0]:
            return None, True
        result[name] = {"calls": values[0], "legacy": values[1],
                        "fallback": values[2]}
    if (sum(v["calls"] for v in result.values()) != totals["getterCalls"] or
            sum(v["legacy"] for v in result.values()) != totals["positiveLegacy"] or
            sum(v["fallback"] for v in result.values()) != totals["positiveFallback"] or
            sum(result[n][k] for n in SLOT_NAMES[3:9]
                for k in ("legacy", "fallback")) != totals["positiveEdges"] or
            sum(result[n][k] for n in SLOT_NAMES[9:]
                for k in ("legacy", "fallback")) != totals["positiveScroll"]):
        return None, True
    return result, False


def parse_callback_masks(detail, callbacks):
    """Optional exact press/release masks emitted by the real Android logger."""
    present = ("pressMask=" in detail, "releaseMask=" in detail)
    if not any(present):
        return None, False
    press = parse_counter(detail, "pressMask")
    release = parse_counter(detail, "releaseMask")
    if press is None or release is None or press > 7 or release > 7:
        return None, True
    if ((callbacks["pressCallbacks"] == 0 and press != 0) or
            (callbacks["releaseCallbacks"] == 0 and release != 0)):
        return None, True
    return {"press": press, "release": release}, False


def triage(lines):
    attempts = []
    active = None
    # Real ReleaseCapture() logs the release marker FIRST, then at most one
    # action _final and one Legacy reader _final BEFORE epoch++ and reset.
    # Preserve only this narrow terminal tail, never ordinary post-release
    # callbacks or readers, and never a next capture's epoch.
    pending_final = None
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
        if pending_final is not None and scope != pending_final["attempt"]["scope"]:
            # Never join the final snapshot to another app logger session.
            provenance_mismatches += 1
            pending_final = None
        if not valid:
            pending_final = None
            if op is not None:
                invalid += 1
            continue
        if not op:
            if pending_final is not None:
                # Unrelated logger threads can interleave between C# release
                # and its final snapshots; bound this to prevent late joins.
                pending_final["interleaving"] += 1
                if pending_final["interleaving"] > 8:
                    pending_final = None
            continue
        if op == "physical_mouse_capture_released":
            pending_final = ({"attempt": active, "seen_actions": False,
                              "seen_readers": False, "interleaving": 0}
                             if active is not None else None)
            active = None
            continue
        epochs = EPOCH_RE.findall(detail)
        if len(epochs) != 1 or len(EPOCH_KEY_RE.findall(detail)) != 1:
            # An invalid final record from the just-released logger cannot
            # be followed by a different well-formed final that restores
            # trust in this terminal snapshot.
            if pending_final is not None and op.endswith("_final"):
                pending_final["attempt"]["invalid"] = True
                pending_final = None
            invalid += 1
            continue
        epoch = int(epochs[0])
        if epoch > MAX_INT32:
            if pending_final is not None and op.endswith("_final"):
                pending_final["attempt"]["invalid"] = True
                pending_final = None
            invalid += 1
            continue
        if op in OPS[:2]:
            # Retried capture supersedes an earlier generation, even if it
            # had unread evidence. Preserve it as a separate attempt.
            pending_final = None
            active = {"epoch": epoch, "scope": scope,
                      "callbacks": None, "readers": None,
                      "invalid": False, "operation": op}
            attempts.append(active)
            continue
        if op.endswith("_final"):
            # These two *exact* operation names can follow the release in
            # original C#, but normal callbacks/readers cannot. Action final
            # must precede reader final if both are emitted. Missing one is OK.
            if pending_final is None:
                unpaired += 1
                continue
            if (pending_final["attempt"]["epoch"] != epoch or
                    pending_final["attempt"]["scope"] != scope):
                pending_final["attempt"]["invalid"] = True
                pending_final = None
                invalid += 1
                unpaired += 1
                continue
            if op == "physical_mouse_captured_action_callbacks_final":
                accepted_final = (not pending_final["seen_actions"] and
                                  not pending_final["seen_readers"])
                pending_final["seen_actions"] = True
            elif op == "physical_mouse_legacy_reader_evidence_final":
                accepted_final = not pending_final["seen_readers"]
                pending_final["seen_readers"] = True
            else:
                accepted_final = False
            if not accepted_final:
                pending_final["attempt"]["invalid"] = True
                invalid += 1
                pending_final = None
                continue
            target = pending_final["attempt"]
        else:
            # Non-final operations after ReleaseCapture are not part of its
            # terminal snapshot; close the limited final-only opportunity.
            pending_final = None
            if active is None or active["epoch"] != epoch:
                unpaired += 1
                continue
            target = active
        if op.startswith("physical_mouse_captured_action_callbacks"):
            wanted = ("capturedCallbackEvents", "pressCallbacks", "releaseCallbacks",
                      "verticalScrollCallbacks", "horizontalScrollCallbacks")
            data = {key: parse_counter(detail, key) for key in wanted}
            # Per ORIGINAL PhysicalMouseActionEvidence.Record, every
            # press/release is one distinct callback. Vertical and horizontal
            # scroll can co-occur on ONE ACTION_SCROLL, hence max not sum.
            if (any(value is None or value > MAX_INT32
                    for value in data.values()) or
                    data["pressCallbacks"] + data["releaseCallbacks"] +
                    max(data["verticalScrollCallbacks"],
                        data["horizontalScrollCallbacks"]) >
                    data["capturedCallbackEvents"] or
                    "unityButtonsAndWheelVerified=false" not in detail):
                target["invalid"] = True
                invalid += 1
                continue
            masks, invalid_masks = parse_callback_masks(detail, data)
            if invalid_masks:
                target["invalid"] = True
                invalid += 1
                continue
            data["masks"] = masks
            old = target["callbacks"]
            if old is not None and any(data[key] < old[key] for key in wanted):
                target["invalid"] = True
                invalid += 1
            elif (old is not None and old["masks"] is not None and
                  masks is not None and
                  ((old["masks"]["press"] & masks["press"]) != old["masks"]["press"] or
                   (old["masks"]["release"] & masks["release"]) != old["masks"]["release"])):
                target["invalid"] = True
                invalid += 1
            else:
                target["callbacks"] = data
        elif op.startswith("physical_mouse_legacy_reader_evidence"):
            wanted = ("getterCalls", "positiveLegacy", "positiveFallback",
                      "positiveEdges", "positiveScroll")
            data = {key: parse_counter(detail, key) for key in wanted}
            if (any(value is None for value in data.values()) or
                    parse_bool(detail, "captureRequested") is not True or
                    parse_bool(detail, "captureObserved") is not True or
                    parse_bool(detail, "unityGameplayVerified") is not False or
                    parse_bool(detail, "countersAreGetterCallsNotClicks") is not True):
                target["invalid"] = True
                invalid += 1
                continue
            # One original getter reports at most one positive path;
            # edge and scroll are disjoint subsets of those positives.
            if (data["positiveFallback"] + data["positiveLegacy"] >
                    data["getterCalls"] or
                    data["positiveEdges"] + data["positiveScroll"] >
                    data["positiveFallback"] + data["positiveLegacy"]):
                target["invalid"] = True
                invalid += 1
                continue
            slots, invalid_slots = parse_reader_slots(detail, data)
            if invalid_slots:
                target["invalid"] = True
                invalid += 1
                continue
            data["slots"] = slots
            old = target["readers"]
            if old is not None and any(data[key] < old[key] for key in wanted):
                target["invalid"] = True
                invalid += 1
            elif (old is not None and old["slots"] is not None and
                  slots is not None and
                  any(slots[name][key] < old["slots"][name][key]
                      for name in SLOT_NAMES for key in ("calls", "legacy", "fallback"))):
                target["invalid"] = True
                invalid += 1
            else:
                target["readers"] = data

    eligible = [a for a in attempts if not a["invalid"] and
                a["scope"] not in poisoned_logger_sessions]
    matched = [a for a in eligible if a["callbacks"] is not None
               and a["readers"] is not None and a["callbacks"]["capturedCallbackEvents"] > 0
               and a["readers"]["getterCalls"] > 0]
    matching_fallback = [
        a for a in matched if a["readers"]["positiveFallback"] > 0
    ]
    # Channel co-observation is weaker than causal delivery or gameplay. A
    # primary ACTION_DOWN may buffer an edge without an explicit pressMask;
    # never manufacture an explicit press or infer horizontal scroll from a
    # ScrollVector getter (the vector may be vertical-only).
    channel = [a for a in matched if a["callbacks"]["masks"] is not None and
               a["readers"]["slots"] is not None]
    down = {name: 0 for name in BUTTON_NAMES}
    up = {name: 0 for name in BUTTON_NAMES}
    for a in channel:
        for idx, name in enumerate(BUTTON_NAMES):
            if (a["callbacks"]["masks"]["press"] & (1 << idx) and
                    a["readers"]["slots"]["down" + str(idx)]["fallback"] > 0):
                down[name] += 1
            if (a["callbacks"]["masks"]["release"] & (1 << idx) and
                    a["readers"]["slots"]["up" + str(idx)]["fallback"] > 0):
                up[name] += 1
    vertical_axis = sum(a["callbacks"]["verticalScrollCallbacks"] > 0 and
                        a["readers"]["slots"]["scrollAxis"]["fallback"] > 0
                        for a in channel)
    wheel_vector = sum((a["callbacks"]["verticalScrollCallbacks"] > 0 or
                        a["callbacks"]["horizontalScrollCallbacks"] > 0) and
                       a["readers"]["slots"]["scrollVector"]["fallback"] > 0
                       for a in channel)
    callbacks_only = sum(bool(a["callbacks"] and
                              a["callbacks"]["capturedCallbackEvents"] > 0 and
                              not a["readers"]) for a in eligible)
    reader_only = sum(bool(a["readers"] and
                           a["readers"]["getterCalls"] > 0 and
                           not a["callbacks"]) for a in attempts if not a["invalid"] and
                      a["scope"] not in poisoned_logger_sessions)
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
        "complete_per_channel_scoped_attempts": len(channel),
        "captured_press_with_matching_fallback_down": down,
        "captured_release_with_matching_fallback_up": up,
        "captured_vertical_wheel_with_fallback_scroll_axis_attempts": vertical_axis,
        "captured_wheel_with_fallback_scroll_vector_attempts": wheel_vector,
        "horizontal_wheel_getter_independently_proven": False,
        "unity_gameplay_verified": False,
        "device_pass": False,
        "limitations": ("Single chronological app-process log only; epoch may repeat across "
                        "launches. PersistentDiagnosticLog session plus strictly increasing "
                        "sequence prevents cross-logger false positives but does not prove "
                        "process identity, APK signature or gameplay. Counters are getter "
                        "invocations, not unique physical clicks. Per-channel "
                        "fields are only same-epoch co-observation, not gesture "
                        "causality, horizontal-only scroll, Unity gameplay or "
                        "device acceptance."),
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
