#!/usr/bin/env python3
"""Fail-closed advisory checker for T1-T5 trial build votes.

Does NOT create a native request, start Actions, or determine project READY.
T5 must independently verify current source diffs, tests, runs, artifacts, and safety gates.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md"
NAMES = tuple(f"T{i}" for i in range(1, 6))
STATUSES = {"يحتاج", "لا يحتاج", "لم يحدد"}
TIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
ROUND_RE = re.compile(r"\*\*round_id:\*\*\s*([\w-]+)")
STATE_RE = re.compile(r"\*\*round_state:\*\*\s*([A-Z_]+)")


def audit(text: str, *, now: datetime | None = None) -> dict:
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    m_round, m_state = ROUND_RE.search(text), STATE_RE.search(text)
    if not m_round or not m_state:
        raise ValueError("round_id or round_state missing")
    round_id, state = m_round.group(1), m_state.group(1)
    if state not in ("COLLECTING", "REQUESTED", "RUNNING", "FAILED", "DELIVERED"):
        raise ValueError("unknown round state")
    a, b = "<!-- TRIAL_VOTES_BEGIN -->", "<!-- TRIAL_VOTES_END -->"
    if text.count(a) != 1 or text.count(b) != 1:
        raise ValueError("expected one vote table")
    section = text.split(a, 1)[1].split(b, 1)[0]
    rows = {}
    for line in section.splitlines():
        if not re.match(r"^\s*\|\s*T[1-5]\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            raise ValueError("row must have six columns; no literal | in cells")
        who, vote, reason, evidence, updated, vote_round = cells
        if who in rows:
            raise ValueError("duplicate worker vote")
        if vote not in STATUSES:
            raise ValueError(f"{who}: invalid vote")
        if vote_round != round_id:
            fresh = False
            problem = "different_round"
        elif vote == "لم يحدد":
            fresh = False
            problem = "not_voted"
        elif reason in ("", "—") or len(reason) < 10:
            fresh = False
            problem = "missing_reason"
        elif vote == "يحتاج" and not re.search(r"https://github\.com/alwansan/raf/(commit/|actions/runs/)", evidence):
            fresh = False
            problem = "missing_github_evidence"
        elif not TIME_RE.fullmatch(updated):
            fresh = False
            problem = "missing_utc_timestamp"
        else:
            stamp = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age = now - stamp
            fresh = timedelta(minutes=-5) <= age <= timedelta(hours=48)
            problem = None if fresh else "stale_or_future"
        rows[who] = {"vote": vote, "fresh": fresh, "reason": problem}
    if set(rows) != set(NAMES):
        raise ValueError("exactly T1,T2,T3,T4,T5 required")
    all_yes = state == "COLLECTING" and all(
        rows[n]["vote"] == "يحتاج" and rows[n]["fresh"] for n in NAMES
    )
    return {
        "round_id": round_id,
        "round_state": state,
        "yes_count": sum(rows[n]["vote"] == "يحتاج" and rows[n]["fresh"] for n in NAMES),
        "all_five_fresh_yes": all_yes,
        "eligible_for_T5_manual_review": all_yes,
        "votes": rows,
        "note": "Consensus is NOT authorization to bypass checks and does NOT mean READY. No build dispatched.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", type=Path, default=DEFAULT)
    p.add_argument("--require-consensus", action="store_true",
                   help="exit 2 unless five fresh YES votes in COLLECTING round")
    args = p.parse_args()
    try:
        data = audit(args.file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 3
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 2 if args.require_consensus and not data["all_five_fresh_yes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
