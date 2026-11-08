#!/usr/bin/env python3
"""Validate one unified T1-T5 testpack; imported data cannot invent executable drivers."""
import argparse, json, re, hashlib
from pathlib import Path

WORKERS={f"T{i}" for i in range(1,6)}
ROOT={"schema_version","pack_id","revision","source_sha","tests"}
CASE={"id","worker","driver","revision","mode","screenshot","title","instructions","expected"}
SCREEN={"auto","manual","none","optional"}
MODE={"auto","assisted","manual"}
DRIVERS={"t1_compute","t2_gles","t3_visual","mouse_manual","file_sha256","system_identity","note_manual"}

def audit(raw:bytes):
    if len(raw)>262144: raise ValueError("pack > 256KiB")
    p=json.loads(raw)
    if type(p) is not dict or set(p)!=ROOT: raise ValueError("root keys")
    if type(p["schema_version"]) is not int or p["schema_version"]!=2:raise ValueError("schema v2 required")
    if not isinstance(p["pack_id"],str) or not re.fullmatch("[a-z0-9][a-z0-9._-]{0,79}",p["pack_id"]):raise ValueError("pack_id")
    if type(p["revision"]) is not int or p["revision"]<1:raise ValueError("pack revision")
    sha=p["source_sha"]
    if sha is not None and (not isinstance(sha,str) or not re.fullmatch("[a-f0-9]{40}",sha)):raise ValueError("source sha")
    cases=p["tests"]
    if type(cases) is not list or not 1<=len(cases)<=100:raise ValueError("case count")
    seen=set();by={w:0 for w in WORKERS}
    for c in cases:
        if type(c) is not dict or set(c)!=CASE:raise ValueError("case fields")
        id,w,d=c["id"],c["worker"],c["driver"]
        if w not in WORKERS or not isinstance(id,str) or not re.fullmatch("T[1-5]-[0-9]{2,3}",id) or not id.startswith(w+"-") or id in seen:raise ValueError("case ID/owner")
        seen.add(id);by[w]+=1
        if type(c["revision"]) is not int or c["revision"]<1:raise ValueError("case revision")
        if d not in DRIVERS or c["mode"] not in MODE or c["screenshot"] not in SCREEN:raise ValueError("case routing")
        if d=="t1_compute" and not (re.fullmatch("T1-0[1-4]",id) and c["mode"]=="auto"):raise ValueError("invalid T1 executable mapping")
        if d=="t2_gles" and not (re.fullmatch("T2-0[1-4]",id) and c["mode"]=="auto"):raise ValueError("invalid T2 executable mapping")
        if d=="t3_visual" and not (re.fullmatch("T3-0[1-6]",id) and c["mode"]=="assisted"):raise ValueError("invalid T3 executable mapping")
        if d=="mouse_manual" and (w!="T4" or c["mode"]!="manual"):raise ValueError("mouse must require real input")
        if d=="system_identity" and (w!="T5" or c["mode"]!="auto"):raise ValueError("system driver restriction")
        if d in ("file_sha256","note_manual") and c["mode"]!="manual":raise ValueError("manual driver restriction")
        for k in ("title","instructions","expected"):
            if type(c[k]) is not str or not 1<=len(c[k].strip())<=1200:raise ValueError("case text")
    return {"pack_id":p["pack_id"],"cases":len(seen),"per_worker":by,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "note":"Data-only manifest; device execution and screenshots unverified"}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("path",type=Path)
    args=ap.parse_args()
    try:print(json.dumps(audit(args.path.read_bytes()),ensure_ascii=False,indent=2));return 0
    except Exception as e:print(json.dumps({"error":str(e)}));return 2
if __name__=="__main__":raise SystemExit(main())
