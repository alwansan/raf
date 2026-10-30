#!/usr/bin/env python3
"""Read-only Unity source mesh PPtr dependency audit: aggregate counts only."""
from collections import Counter
from pathlib import Path
import argparse
import json

import UnityPy

TARGETS={"MeshFilter","MeshCollider","SkinnedMeshRenderer"}
FILES=tuple(f"level{i}" for i in range(40)) + (
       "sharedassets1.assets","sharedassets35.assets","globalgamemanagers.assets")

def analyze(root:Path):
    totals=Counter()
    destination_counts=Counter()
    unique_ptrs=set()
    examples=[]
    perfile={}
    for name in FILES:
        p=root/name
        if not p.exists():continue
        if p.stat().st_size<200 and p.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
            continue
        seen=Counter()
        errors=Counter()
        env=UnityPy.load(str(p))
        for obj in env.objects:
            kind=str(getattr(obj.type,"name","unknown"))
            if kind not in TARGETS:continue
            seen[kind]+=1
            totals[kind]+=1
            try:
                data=obj.read()
                ptr=getattr(data,"m_Mesh",None)
                if ptr is None:
                    errors["no_m_Mesh"]+=1
                    continue
                fid=int(getattr(ptr,"m_FileID",0))
                pid=int(getattr(ptr,"m_PathID",0))
                externals=getattr(obj.assets_file,"externals",[])
                path="local:"+name if fid==0 else (str(externals[fid-1].path) if fid-1<len(externals) else "INVALID_FILEID")
                destination_counts[path]+=1
                unique_ptrs.add((path,pid))
                if len(examples)<12 and path not in [x["target"] for x in examples]:
                    examples.append({"source":name,"kind":kind,"target":path,"file_id":fid,"path_id":str(pid)})
            except Exception as e:
                errors[type(e).__name__]+=1
        perfile[name]={"classes":dict(seen),"errors":dict(errors)}
    return {
        "source_files":list(perfile),
        "components":dict(totals),
        "by_target_file":dict(destination_counts.most_common(28)),
        "distinct_pointer_targets":len(unique_ptrs),
        "example_pointers":examples,
        "by_source":perfile,
        "caveat":"Mesh PPtrs are parsed from original Unity data, but input may omit external files. This cannot prove object content or link resolution."
    }

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,default=Path("Raft/Raft_Data"))
    a.add_argument("--out",type=Path,default=Path("out/mesh-source-pointers.json"))
    args=a.parse_args()
    r=analyze(args.root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2)+"\n")
    for k in ("source_files","components","by_target_file","distinct_pointer_targets","example_pointers","by_source"):
        print(k+":",r[k])
