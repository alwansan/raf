#!/usr/bin/env python3
"""Diagnose duplicate Unity Timeline types after a reconstruct/ILSpy overlay.

Outputs type names and relative file paths, never game source. This script
makes no changes; used on exported private Unity project in CI.
"""
from pathlib import Path
import argparse
from collections import defaultdict
import re

def audit(root: Path):
    if not root.is_dir():raise FileNotFoundError(root)
    names=("AnimationPlayableAsset","AnimationTrack")
    hits=defaultdict(list)
    for p in root.rglob("*.cs"):
        s=p.read_text(encoding="utf8",errors="replace")
        for name in names:
            regex=r"\b(?:class|struct|interface)\s+"+name+r"\b"
            for m in re.finditer(regex,s):
                # Cheap namespace indicator for diagnostic. Path is main ground truth.
                pre=s[:m.start()]
                n=re.findall(r"\bnamespace\s+([\w.]+)",pre)
                hits[name].append({"path":str(p.relative_to(root)),"namespace":n[-1] if n else "(none)","meta":p.with_name(p.name+".meta").is_file(),"bytes":p.stat().st_size})
    for name,records in hits.items():
        print("Duplicate type:",name,"count:",len(records))
        for rec in records:print("  ",rec)
    if not hits: print("No remaining known Timeline type declarations (expected after repairing generated stubs)")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--assets",type=Path,required=True)
    args=ap.parse_args()
    audit(args.assets)
