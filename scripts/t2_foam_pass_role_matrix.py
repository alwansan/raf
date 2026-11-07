#!/usr/bin/env python3
"""Strict source-free per-pass Foam Blit role evidence gate. Not a renderer."""
import json
import sys
SRC = {"Texture", "RenderTexture", "UNKNOWN"}
DST = {"RenderTexture", "NULL", "UNKNOWN"}
def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result: raise ValueError("duplicate JSON key")
        result[k] = v
    return result
def verify(p):
    if type(p) is not dict or set(p) != {"schema_version", "passes", "aggregates"} or type(p["schema_version"]) is not int or p["schema_version"] != 1:
        raise ValueError("invalid envelope")
    rows = p["passes"]
    if type(rows) is not list or len(rows) != 2: raise ValueError("two passes required")
    for r in rows:
        if type(r) is not dict or set(r) != {"pass", "source", "destination"} or type(r["pass"]) is not int or type(r["source"]) is not str or type(r["destination"]) is not str or r["source"] not in SRC or r["destination"] not in DST:
            raise ValueError("invalid pass role")
    if sorted(r["pass"] for r in rows) != [0, 1]: raise ValueError("pass identity mismatch")
    a = p["aggregates"]
    if type(a) is not dict or set(a) != {"source", "destination"}: raise ValueError("invalid aggregate")
    for field, allowed in (("source", SRC), ("destination", DST)):
        counts = a[field]
        if type(counts) is not dict or set(counts) != allowed or any(type(v) is not int or v < 0 for v in counts.values()) or sum(counts.values()) != 2:
            raise ValueError("invalid counts")
        if any(counts[k] != sum(r[field] == k for r in rows) for k in allowed):
            raise ValueError("aggregate contradicts pass rows")
    return {"status": "SCHEMA_CONSISTENT_NOT_RUNTIME_PROVEN", "passes": sorted(rows, key=lambda r: r["pass"])}
if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("usage: t2_foam_pass_role_matrix.py safe-report.json")
    with open(sys.argv[1], encoding="utf-8") as f: p = json.load(f, object_pairs_hook=unique)
    print(json.dumps(verify(p), sort_keys=True))
