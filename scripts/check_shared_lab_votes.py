#!/usr/bin/env python3
"""Advisory shared mini-lab build-vote gate: ONE fresh legitimate NEED_BUILD is enough.

The 5/5 vote for the full Raft XAPK lives in another file and is not altered.
This gate is NOT an authorization to bypass source/CI/artifact/signature checks.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse, json, re

DEFAULT=Path(__file__).resolve().parents[1]/"apk-for-testing/SHARED_BUILD_READINESS.md"
STATUSES={"NOT_REVIEWED","WAITING_MERGE","NO_BUILD","NEED_BUILD"}
WORKERS=[f"T{i}" for i in range(1,6)]

def analyze(body:str,now=None):
    now=now or datetime.now(timezone.utc)
    match=re.search(r"^\*\*shared_round_id:\*\*\s*([a-z0-9-]+)",body,re.M)
    if not match:raise ValueError("round_id missing")
    round_id=match.group(1)
    found={}
    for line in body.splitlines():
        if not re.match(r"^\| T[1-5] \|",line):continue
        cells=[c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells)!=6:raise ValueError("six columns required")
        name,vote,why,evidence,utc,own_round=cells
        if name in found:raise ValueError("duplicate worker")
        if vote not in STATUSES:raise ValueError("invalid status")
        ok=False
        if vote=="NEED_BUILD" and own_round==round_id and len(why)>15 and (
            "https://github.com/alwansan/raf/commit/" in evidence or
            "https://github.com/alwansan/raf/actions/runs/" in evidence
        ):
            try:
                parsed=datetime.strptime(utc,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                ok=timedelta(minutes=-5)<=now-parsed<=timedelta(hours=48)
            except ValueError:pass
        found[name]={"vote":vote,"fresh_evidence_need":ok}
    if set(found)!=set(WORKERS):raise ValueError("exactly five named worker rows required")
    yes=[n for n in WORKERS if found[n]["fresh_evidence_need"]]
    return {"round_id":round_id,"fresh_needs":yes,"eligible_for_T5_review":bool(yes),
            "all_five_need":len(yes)==5,"votes":found,
            "note":"Review gate only; T5 verifies real integrated changes, running jobs, package and source SHA. NOT full Raft 5/5 readiness."}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--file",type=Path,default=DEFAULT)
    ap.add_argument("--require-need",action="store_true")
    a=ap.parse_args()
    try:out=analyze(a.file.read_text("utf-8"))
    except (OSError,ValueError) as e:print(json.dumps({"error":str(e)}));return 3
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 2 if a.require_need and not out["eligible_for_T5_review"] else 0
if __name__=="__main__":raise SystemExit(main())
