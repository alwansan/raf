#!/usr/bin/env python3
"""Fail-closed declarative Android mini-lab testpack validator. No network or code execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re

class PackError(ValueError): pass
REQ={"schema_version","worker","pack_id","title","version","source_sha","tests"}
TR={"id","type","title","instructions","expected"}
TYPES={"note","mouse","file_sha256","image_preview"}
def validate(p):
    if type(p) is not dict or set(p)!=REQ: raise PackError("invalid root keys")
    if type(p["schema_version"]) is not int or p["schema_version"]!=1: raise PackError("schema must be 1")
    if p["worker"] not in {"T1","T2","T3","T4","T5"}: raise PackError("worker must be T1..T5")
    if not isinstance(p["pack_id"],str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}",p["pack_id"]): raise PackError("unsafe pack ID")
    if p["source_sha"] is not None and (not isinstance(p["source_sha"],str) or not re.fullmatch("[a-f0-9]{40}",p["source_sha"])): raise PackError("invalid source sha")
    for field in ("title","version"):
        if not isinstance(p[field],str) or not 1<=len(p[field].strip())<=120: raise PackError("invalid "+field)
    ts=p["tests"]
    if type(ts) is not list or not 1<=len(ts)<=20: raise PackError("1..20 test cases required")
    seen=set()
    for t in ts:
        if type(t) is not dict or not TR<=set(t) or set(t)-TR-{"asset","sha256"}: raise PackError("invalid test fields")
        if not isinstance(t["id"],str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}",t["id"]) or t["id"] in seen: raise PackError("duplicated/unsafe case id")
        seen.add(t["id"])
        if t["type"] not in TYPES: raise PackError("unsupported type, no executable code allowed")
        for key in ("title","instructions","expected"):
            if not isinstance(t[key],str) or not 1<=len(t[key].strip())<=1500: raise PackError("invalid case text")
        if "asset" in t:
            a=t["asset"]
            if not isinstance(a,str) or not a or len(a)>180 or a.startswith("/") or "\\" in a or "://" in a or any(x in ("",".","..") for x in a.split("/")): raise PackError("unsafe asset path")
        if "sha256" in t and (not isinstance(t["sha256"],str) or not re.fullmatch("[a-f0-9]{64}",t["sha256"])): raise PackError("invalid asset sha")
    return {"worker":p["worker"],"pack_id":p["pack_id"],"cases":len(seen)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("packs",type=Path,nargs="+")
    good=True
    for path in ap.parse_args().packs:
        try:
            if path.stat().st_size>65536: raise PackError("pack over 64KiB")
            buf=path.read_bytes()
            out=validate(json.loads(buf))
            out["sha256"]=hashlib.sha256(buf).hexdigest()
            print(json.dumps(out,ensure_ascii=False))
        except (OSError,ValueError,UnicodeError) as e:
            good=False
            print(json.dumps({"file":str(path),"error":str(e)},ensure_ascii=False))
    return 0 if good else 2
if __name__=="__main__": raise SystemExit(main())
