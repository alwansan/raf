"""Fail-closed bundle provenance check for T1 LogRaft water summaries.

Run the existing t1_device_water_summary_gate first. Session labels are
not cryptographic proof of original CL capture identity.
"""
import argparse
import json
import re
from pathlib import Path

SESSION_RE = re.compile(r"^LogRaft-\d{8}-\d{6}-\d{3}$")


def validate_bundle(records, expected_sessions):
    if not expected_sessions or len(expected_sessions) != len(set(expected_sessions)):
        raise ValueError("expected sessions must be nonempty and unique")
    if not all(isinstance(s, str) and SESSION_RE.fullmatch(s) for s in expected_sessions):
        raise ValueError("invalid expected session identifier")
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("summary must be an object")
        session = record.get("session")
        if not isinstance(session, str) or not SESSION_RE.fullmatch(session):
            raise ValueError("invalid session identifier")
        if session in seen:
            raise ValueError("duplicate summary session")
        seen.add(session)
        for key in ("kernel_index_6_is_fft_proven", "source_to_unity_kernel_mapping_proven",
                    "android_water_rendering_restored"):
            if record.get(key) is not False:
                raise ValueError("unproven runtime claim")
        for key in ("invalid_pass_total", "invalid_kernel_total"):
            if type(record.get(key)) is not int or record[key] < 0:
                raise ValueError("invalid total")
        for total, breakdown in (("invalid_pass_total", "invalid_pass_by_material"),
                                 ("invalid_kernel_total", "invalid_kernel_by_index")):
            data = record.get(breakdown)
            if not isinstance(data, dict) or not data:
                raise ValueError("missing breakdown")
            values = list(data.values())
            if any(type(v) is not int or v < 0 for v in values) or sum(values) != record[total]:
                raise ValueError("inconsistent breakdown")
    if seen != set(expected_sessions):
        raise ValueError("session set mismatch")
    return {"validated_sessions": sorted(seen),
            "provenance": "summary labels only; original capture linkage not proven",
            "device_water_restored": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("bundle", type=Path, help="JSON list from t1_device_water_summary_gate")
    p.add_argument("--expected-session", action="append", required=True)
    args = p.parse_args()
    try:
        if args.bundle.is_symlink() or not args.bundle.is_file() or args.bundle.stat().st_size > 2_000_000:
            raise ValueError("invalid bundle")
        records = json.loads(args.bundle.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("bundle must be list")
        result = validate_bundle(records, args.expected_session)
    except (OSError, ValueError, TypeError) as exc:
        p.exit(2, f"Invalid water summary bundle: {type(exc).__name__}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
