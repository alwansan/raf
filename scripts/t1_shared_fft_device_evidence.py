"""T1-05 shared Mini Android15 synthetic-GLES readback audit; NOT original Raft FFT."""
import json
import math
import re
from pathlib import Path

SOURCE = "2d7c268248b505e4dd9ad1daa9491787df07665c"
PACK = "9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6"
APK = "0.2.14-shared"
IDS = {f"T1-{i:02}" for i in range(1, 6)}
PAT = re.compile(
    r"PASS fft_synthetic_two_pass_local512 checked_floats=(\d+) "
    r"max_abs_error=([0-9.eE+\-]+) tolerance=([0-9.eE+\-]+) "
    r"first_mismatch=(-?\d+) unmap=(true|false) gl_error=(0x[0-9a-fA-F]+) "
    r"original_raft_compute_executed=(true|false)")


def no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key")
        d[k] = v
    return d


def read_json(path):
    p = Path(path)
    if p.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("input too large")
    return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def read_events(path):
    p = Path(path)
    if p.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("input too large")
    lines = p.read_text(encoding="utf-8").splitlines()
    if len(lines) > 5000:
        raise ValueError("too many rows")
    return [json.loads(line, object_pairs_hook=no_duplicates) for line in lines if line.strip()]


def audit(summary, events):
    session = summary.get("session")
    if (not isinstance(session, str) or
            not re.fullmatch(r"\d{8}-\d{6}-\d+", session) or
            summary.get("app_source") != SOURCE or
            summary.get("pack_sha256") != PACK or
            summary.get("pack_id") != "raft-shared-t1-t5-v1"):
        raise ValueError("summary provenance mismatch")
    saved = {}
    for obj in summary.get("results", []):
        case = obj.get("case_id")
        if case in IDS:
            if case in saved or obj.get("worker") != "T1":
                raise ValueError("duplicate/wrong worker summary")
            saved[case] = obj["result"]
    if set(saved) != IDS:
        raise ValueError("missing T1 summary")
    begun = completed = False
    starts, fresh, reused = {}, {}, set()
    for idx, row in enumerate(events):
        if (row.get("session"), row.get("source"), row.get("pack_sha256"),
                row.get("apk")) != (session, SOURCE, PACK, APK):
            raise ValueError("mixed events provenance")
        time = row.get("time_ms")
        if not isinstance(time, int):
            raise ValueError("bad event time")
        kind, detail = row.get("event"), row.get("detail")
        if not isinstance(detail, str):
            raise ValueError("bad event detail")
        if kind == "auto_start" and detail == "worker=T1 total=5 force=false":
            if begun:
                raise ValueError("duplicate worker launch")
            begun = True
        elif kind == "auto_case_start":
            case = detail.split(" ", 1)[0]
            if case in IDS:
                if not begun or completed or case in starts or detail != case+" driver=t1_compute":
                    raise ValueError("invalid fresh case start")
                starts[case] = (idx, time)
        elif kind == "case_result":
            r = json.loads(detail, object_pairs_hook=no_duplicates)
            case = r.get("id")
            if case in IDS:
                if case not in starts or case in fresh or idx <= starts[case][0]:
                    raise ValueError("result not fresh")
                if r != saved[case] or r.get("status") != "PASS" or r.get("worker") != "T1" or r.get("pack_sha256") != PACK:
                    raise ValueError("summary/event result mismatch")
                if not re.fullmatch(r"[0-9a-f]{64}", str(r.get("fingerprint", ""))):
                    raise ValueError("fingerprint invalid")
                timestamp = r.get("utc_ms")
                if not isinstance(timestamp, int) or not starts[case][1] <= timestamp <= time <= timestamp+20000:
                    raise ValueError("invalid case time")
                fresh[case] = r
        elif kind == "auto_reuse":
            case = detail.split(" ", 1)[0]
            if case in IDS:
                if case not in fresh:
                    raise ValueError("reuse without fresh execution")
                reused.add(case)
        elif kind == "auto_complete" and detail == "count=5":
            if not begun or completed or set(fresh) != IDS:
                raise ValueError("premature/duplicate completion")
            completed = True
    if not begun or not completed or set(starts) != IDS or set(fresh) != IDS:
        raise ValueError("missing fresh T1 execution")
    m = PAT.fullmatch(fresh["T1-05"].get("observed", ""))
    if not m:
        raise ValueError("missing T1-05 numeric contract")
    n, error, tol, mismatch, unmap, gl, original = m.groups()
    error, tol = float(error), float(tol)
    if (int(n) != 1024 or not math.isfinite(error) or error < 0 or
            not math.isfinite(tol) or tol != 3e-5 or error > tol or
            int(mismatch) != -1 or unmap != "true" or int(gl, 16) != 0 or
            original != "false"):
        raise ValueError("T1-05 numerical contract rejected")
    return {"verdict": "PASS_SYNTHETIC_DEVICE_GLES_ONLY",
            "session": session, "source": SOURCE, "pack": PACK,
            "t105_checked_floats": 1024, "max_abs_error": error,
            "later_reuse_is_not_second_execution": "T1-05" in reused,
            "original_raft_fft_proven": False, "water_001_closed": False}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("summary_json")
    p.add_argument("events_jsonl")
    args = p.parse_args()
    try:
        print(json.dumps(audit(read_json(args.summary_json),
                               read_events(args.events_jsonl)), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as ex:
        p.exit(2, "EVIDENCE_REJECTED: " + str(ex) + "\n")
