#!/usr/bin/env python3
"""T4: replay real CL shared-lab mouse events, preserve raw/unique/capture boundaries.

No proprietary data is copied into raf. Results are an Android View callback
diagnostic, never proof that Unity Legacy Input or Raft gameplay received input.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

MOUSE_SOURCES = (0x2002, 0x20004)
BUTTON_BITS = {1: "left", 2: "right", 4: "middle"}
EDGE_ACTIONS = {"ACTION_BUTTON_PRESS", "ACTION_BUTTON_RELEASE"}
MAX_ROWS = 150000
MAX_BYTES = 20 * 1024 * 1024


def fields(text):
    if not isinstance(text, str):
        raise ValueError("Non-string Android mouse event")
    result = {}
    for token in text.split():
        if "=" in token:
            k, v = token.split("=", 1)
            result[k] = v
    return result


def physical_mouse(source):
    if source is None:
        return False
    try:
        value = int(source, 0)
    except (TypeError, ValueError):
        return False
    return any((value & m) == m for m in MOUSE_SOURCES)


def finite_axis(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.0
    return n if math.isfinite(n) else 0.0



def correlate_implicit_down_up(unique):
    """Match ACTION_DOWN/UP actionButton=0 to explicit edges at the SAME time.

    This reports duplicated Android callbacks, not additional clicks. A
    buttonState transition alone is only ambiguous candidate evidence.
    Multi-device identity is absent in this older log, so no Unity success
    or inferred click may be claimed from a correlated pair.
    """
    explicit = {}
    for rec in unique.values():
        f = rec["event"]
        act = f.get("action")
        if act not in EDGE_ACTIONS:
            continue
        try:
            bit = int(f.get("actionButton", "0"), 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid explicit actionButton mask") from exc
        if bit not in BUTTON_BITS or not f.get("eventTime"):
            continue
        edge = "press" if act == "ACTION_BUTTON_PRESS" else "release"
        key = (f["eventTime"], f.get("source"), f.get("captured"), edge)
        explicit.setdefault(key, set()).add(bit)

    matched = Counter()
    ambiguous = Counter()
    zero = Counter()
    for rec in unique.values():
        f = rec["event"]
        act = f.get("action")
        if act not in ("ACTION_DOWN", "ACTION_UP"):
            continue
        try:
            action_bit = int(f.get("actionButton", "0"), 0)
            state = int(f.get("buttonState", "0"), 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid implicit button state") from exc
        if action_bit != 0:
            continue
        edge = "press" if act == "ACTION_DOWN" else "release"
        zero[edge] += 1
        time = f.get("eventTime")
        key = (time, f.get("source"), f.get("captured"), edge)
        bits = explicit.get(key, set()) if time else set()
        # Pair only a unique named explicit button; never infer button
        # identity from ACTION_UP state=0 or from a MOVE held state.
        if len(bits) == 1:
            bit = next(iter(bits))
            if (edge == "press" and (state & bit)) or (
                    edge == "release" and not (state & bit)):
                matched[edge + "_" + BUTTON_BITS[bit]] += 1
                continue
        ambiguous[edge] += 1
    return {
        "actionbutton_zero": dict(sorted(zero.items())),
        "matched_to_explicit_same_eventtime": dict(sorted(matched.items())),
        "unpaired_ambiguous_not_click_proof": dict(sorted(ambiguous.items())),
        "additional_clicks_inferred": 0,
        "unity_delivery_proven": False,
    }

def count_events(events, summary=None):
    """Return strictly aggregate proof, deduplicating a MotionEvent across routes.

    "Duplicate" means same Android eventTime+action+source+button fields+
    axes/captured state. Distinct routes showing the same event count once.
    EventTime is device elapsed uptime, *not* a unique physical gesture ID.
    """
    inputs = []
    capture_requests = Counter()
    kinds = Counter()
    rejected_sources = 0
    for row in events:
        if not isinstance(row, dict):
            raise ValueError("Expected JSONL event object")
        kind = row.get("event")
        kinds[kind] += 1
        if kind == "capture_request":
            if row.get("detail") in ("ON", "OFF"):
                capture_requests[row["detail"]] += 1
            continue
        if kind != "input":
            continue
        f = fields(row.get("detail"))
        if not physical_mouse(f.get("source")):
            rejected_sources += 1
            continue
        if f.get("action") is None or f.get("route") is None:
            raise ValueError("Physical mouse source without route/action")
        inputs.append(f)
    # The source code logs events at Activity and at View independently.
    # Count a matching observed Android event once, but retain route context.
    unique = {}
    for f in inputs:
        # View-local x/y differ from Activity/global coordinates for the
        # very same MotionEvent; including them would fail route dedup.
        key = tuple(f.get(z) for z in ("eventTime", "action", "source",
                    "buttonState", "actionButton", "vscroll", "hscroll",
                    "captured"))
        unique.setdefault(key, {"event": f, "routes": set()})["routes"].add(f["route"])

    actions_raw = Counter(f["action"] for f in inputs)
    actions_unique = Counter()
    press = Counter()
    release = Counter()
    wheel = Counter()
    routes = Counter()
    captured_event_count = 0
    captured_callback_count = 0
    multi_route_count = 0
    for rec in unique.values():
        f, seen_routes = rec["event"], rec["routes"]
        action = f["action"]
        actions_unique[action] += 1
        if len(seen_routes) > 1:
            multi_route_count += 1
        for route in seen_routes:
            routes[route] += 1
        if f.get("captured") == "true":
            captured_event_count += 1
            if "captured" in seen_routes:
                captured_callback_count += 1
        if action in EDGE_ACTIONS:
            try:
                mask = int(f.get("actionButton", "0"), 0)
            except ValueError:
                raise ValueError("Invalid actionButton mask")
            if mask not in BUTTON_BITS:
                continue
            name = BUTTON_BITS[mask]
            (press if action == "ACTION_BUTTON_PRESS" else release)[name] += 1
        if action == "ACTION_SCROLL":
            v = finite_axis(f.get("vscroll"))
            h = finite_axis(f.get("hscroll"))
            if v > 0:
                wheel["vertical_positive"] += 1
            if v < 0:
                wheel["vertical_negative"] += 1
            if h > 0:
                wheel["horizontal_positive"] += 1
            if h < 0:
                wheel["horizontal_negative"] += 1

    user_status = None
    provenance = None
    if summary:
        if not isinstance(summary, dict):
            raise ValueError("Expected shared summary JSON")
        provenance = {
            "session": summary.get("session"),
            "app_source": summary.get("app_source"),
            "pack_sha256": summary.get("pack_sha256"),
        }
        for case in summary.get("results", []):
            if case.get("case_id") == "T4-09":
                user_status = case.get("result", {}).get("status")

    return {
        "status": "CL_ANDROID_MOUSE_INPUT_OBSERVED_NOT_UNITY",
        "raw_physical_mouse_callback_records": len(inputs),
        "unique_android_motion_events": len(unique),
        "multi_route_duplicates_removed": len(inputs) - len(unique),
        "unique_events_seen_from_multiple_routes": multi_route_count,
        "input_route_counts_unique": dict(sorted(routes.items())),
        "action_counts_raw": dict(sorted(actions_raw.items())),
        "action_counts_unique": dict(sorted(actions_unique.items())),
        "implicit_down_up_correlation": correlate_implicit_down_up(unique),
        "press_edges_action_button": dict(sorted(press.items())),
        "release_edges_action_button": dict(sorted(release.items())),
        "scroll_axes_unique": dict(sorted(wheel.items())),
        "capture_requests": dict(sorted(capture_requests.items())),
        "captured_true_unique": captured_event_count,
        "captured_callback_unique": captured_callback_count,
        "rejected_nonmouse_input_records": rejected_sources,
        "test_begin_count": kinds["test_begin"],
        "t4_09_saved_status": user_status,
        "t4_09_game_bridge_accepted": False,
        "unity_legacy_mouse_delivery_proven": False,
        "gameplay_fixed": False,
        "device_input_capture_verified": captured_callback_count > 0,
        "provenance": provenance,
        "limitations": "No captured=true callbacks or game Unity Input state in this CL snapshot; test result EVIDENCE_READY is not Raft gameplay PASS.",
    }


def read_jsonl(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Unsafe or oversized physical-mouse log")
    rows = []
    with path.open(encoding="utf-8") as stream:
        for i, line in enumerate(stream, 1):
            if i > MAX_ROWS:
                raise ValueError("Mouse JSONL row budget exceeded")
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--assert-owner-snapshot", action="store_true")
    args = ap.parse_args()
    result = count_events(read_jsonl(args.events),
                          json.loads(args.summary.read_text(encoding="utf-8")))
    if args.assert_owner_snapshot:
        assert result["provenance"]["app_source"] == "cbe7a038bad2c7ca5ad587b242e8baf7128ecb8b"
        assert result["provenance"]["pack_sha256"] == "6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f"
        assert result["raw_physical_mouse_callback_records"] == 413
        assert result["unique_android_motion_events"] == 373
        assert result["press_edges_action_button"] == {"left": 13}
        assert result["implicit_down_up_correlation"] == {
            "actionbutton_zero": {"press": 13, "release": 13},
            "matched_to_explicit_same_eventtime": {"press_left": 13, "release_left": 13},
            "unpaired_ambiguous_not_click_proof": {},
            "additional_clicks_inferred": 0,
            "unity_delivery_proven": False,
        }
        assert result["release_edges_action_button"] == {"left": 13}
        assert sum(result["scroll_axes_unique"].get(k, 0) for k in
                   ("vertical_positive", "vertical_negative")) == 55
        assert result["captured_true_unique"] == 0
        assert result["captured_callback_unique"] == 0
        assert not result["capture_requests"]
        assert result["t4_09_saved_status"] == "EVIDENCE_READY"
        assert not result["t4_09_game_bridge_accepted"]
        assert not result["gameplay_fixed"]
    print("T4_CL_ACTUAL_OWNER_MOUSE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
