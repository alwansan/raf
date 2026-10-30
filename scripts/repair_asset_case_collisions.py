#!/usr/bin/env python3
"""Disambiguate exported non-code assets on Unity's case-insensitive asset index.
Move paired .meta files unchanged so serialized GUID references remain valid.
Never rename code or Resources assets whose string lookup path could change.
"""
import argparse
from collections import defaultdict
import hashlib
from pathlib import Path
import re

def repair(project: Path, *, apply: bool) -> dict:
    assets=project/"Assets"
    groups=defaultdict(list)
    occupied=set()
    for p in assets.rglob("*"):
        if p.is_file():
            occupied.add(p.relative_to(assets).as_posix().casefold())
            if not p.name.endswith(".meta"):
                groups[p.relative_to(assets).as_posix().casefold()].append(p)
    plans=[]
    for paths in groups.values():
        if len(paths)<2: continue
        paths.sort(key=lambda p:p.as_posix())
        for p in paths[1:]:
            if p.suffix not in {".asset",".anim"} or any(part.casefold()=="resources" for part in p.relative_to(assets).parts):
                raise ValueError("Case collision requires manual path-sensitive repair: "+str(p.relative_to(assets)))
            meta=p.with_name(p.name+".meta")
            raw=meta.read_bytes()
            match=re.search(rb"(?m)^guid:\s*([0-9a-fA-F]{32})",raw)
            if not match: raise ValueError("Case-colliding asset has no valid metadata GUID")
            guid=match.group(1).decode().lower()
            target=p.with_name(p.stem+"__case_"+guid[:12]+p.suffix)
            key=target.relative_to(assets).as_posix().casefold()
            if key in occupied or key+".meta" in occupied:
                raise FileExistsError("Refusing a collision-repair destination overwrite")
            occupied.update({key,key+".meta"})
            plans.append((p,meta,target,target.with_name(target.name+".meta"),guid))
    # Finish validation before moving anything.
    for source,meta,target,target_meta,guid in plans:
        if apply:
            before=hashlib.sha256(source.read_bytes()).digest()
            meta_before=meta.read_bytes()
            source.rename(target)
            meta.rename(target_meta)
            if hashlib.sha256(target.read_bytes()).digest()!=before or target_meta.read_bytes()!=meta_before:
                raise RuntimeError("Asset or GUID metadata changed during rename")
    result={"case_collisions_repaired":len(plans),"applied":apply,
            "moves":[{"from":str(a.relative_to(assets)),"to":str(c.relative_to(assets)),"guid":g} for a,b,c,d,g in plans]}
    print("Exported asset case collisions:",result)
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",required=True,type=Path)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    repair(args.project,apply=args.apply)
