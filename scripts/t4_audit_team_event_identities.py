#!/usr/bin/env python3
"""T4 support for T2: enumerate ALL inherited B_TEAM event identity blockers.

Read-only diagnostic. The canonical refresh_b_team.py remains authoritative.
This scanner does not synthesize missing event IDs, modify events, or imply
that a successfully executed audit means the ledger is clean.
"""
from collections import defaultdict
import argparse
import json
from pathlib import Path

MAX_FILES = 15000
MAX_BYTES = 1024 * 1024
MAX_REPORT = 15000


def audit_events(root: Path) -> dict:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("event directory missing or symlink")
    paths = sorted(root.rglob("*.json"))
    if len(paths) > MAX_FILES:
        raise ValueError("event file budget exceeded")
    problems = []
    identities = defaultdict(list)

    def issue(path, reason, **extra):
        if len(problems) >= MAX_REPORT:
            raise ValueError("identity finding budget exceeded")
        problems.append({"path": path.relative_to(root).as_posix(),
                         "code": reason, **extra})

    for path in paths:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            issue(path, "NONREGULAR_OR_OVERSIZED")
            continue
        try:
            raw = path.read_bytes()
            # Canonical refresh treats duplicate JSON keys permissively;
            # the audit marks them independently, never silently chooses one.
            duplicates = []
            def pairs(items):
                record = {}
                for k, value in items:
                    if k in record:
                        duplicates.append(k)
                    record[k] = value
                return record
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            issue(path, "UNREADABLE_OR_INVALID_JSON")
            continue
        if duplicates:
            issue(path, "DUPLICATE_JSON_KEYS", total=len(duplicates))
        if not isinstance(data, dict):
            issue(path, "NON_OBJECT_JSON")
            continue
        event_id = data.get("event_id")
        canonical_id = data.get("id")
        if "event_id" in data:
            if not isinstance(event_id, str) or not event_id.strip():
                issue(path, "INVALID_EVENT_ID")
                continue
            if "id" in data and canonical_id != event_id:
                issue(path, "CONFLICTING_EVENT_IDS")
                continue
            canonical_id = event_id
        if not isinstance(canonical_id, str) or not canonical_id.strip():
            issue(path, "MISSING_RECORD_ID")
            continue
        identities[canonical_id].append(path)

    for identity_paths in identities.values():
        if len(identity_paths) > 1:
            for path in identity_paths:
                issue(path, "DUPLICATE_RECORD_ID")
    problems.sort(key=lambda x: (x["path"], x["code"]))
    counts = {}
    for item in problems:
        counts[item["code"]] = counts.get(item["code"], 0) + 1
    return {
        "status": "LEDGER_IDENTITY_CLEAN" if not problems else "LEDGER_IDENTITY_REVIEW_NEEDED",
        "audit_completed": True,
        "canonical_summary_generation_proven": False,
        "event_files_examined": len(paths),
        "records_with_valid_identity": sum(len(x) for x in identities.values()),
        "finding_count": len(problems),
        "finding_categories": dict(sorted(counts.items())),
        "findings": problems,
        "record_content_published": False,
        "repair_performed": False,
        "note": ("Read-only exhaustive event identity preflight; even a clean result "
                 "does not prove full B_TEAM resource/issue schema or readiness. "
                 "Event file owners must add their own stable id/event_id."),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("prompt/coordination/B_TEAM/events"))
    p.add_argument("--output", type=Path, help="Optional JSON output; never writes to event ledger")
    p.add_argument("--strict", action="store_true",
                   help="Exit 2 when any finding; default always reports and exits 0")
    args = p.parse_args()
    data = audit_events(args.root)
    serialized = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        if args.output.is_symlink() or args.output.resolve().is_relative_to(args.root.resolve()):
            p.error("output must be outside event ledger")
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    if args.strict and data["finding_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
