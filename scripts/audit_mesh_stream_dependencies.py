#!/usr/bin/env python3
"""Inspect serialized Unity Mesh streaming dependencies without reading game stream payloads.

Read-only. Uses UnityPy type trees to obtain m_StreamData.path and size;
does not execute original game binaries and does not publish original assets.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
import argparse
import json
import re

import UnityPy

def is_pointer(p):
    return p.stat().st_size<200 and p.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1")

def classify_stream_range(root, reference, offset, size):
    """Only inspect safe relative filename and range metadata; never read stream bytes."""
    normalized=str(reference).replace("\\", "/")
    parts=PurePosixPath(normalized).parts
    if not parts or normalized.startswith("/") or ".." in parts or ":" in normalized:
        return "unsupported-path"
    if not isinstance(offset,int) or not isinstance(size,int) or offset<0 or size<=0:
        return "invalid-range"
    # Typical names are filename.resS. Nested references remain relative to the source root.
    target=root.joinpath(*parts)
    if not target.is_file():
        return "missing-file"
    if is_pointer(target):
        return "lfs-pointer"
    if offset+size > target.stat().st_size:
        return "out-of-bounds"
    return "available-range"

def scan(root,max_per_file):
    result={"files":[],"stream_paths":Counter(),"errors":Counter(),"mesh_count":0,
            "inspected_meshes":0,"meshes_with_stream":0,"claimed_stream_bytes":0,
            "stream_range_status":Counter(),"range_status_by_path":{}}
    for path in sorted(root.glob("sharedassets*.assets"))+sorted(root.glob("resources.assets")):
        if is_pointer(path):
            result["files"].append({"file":path.name,"status":"LFS pointer - skipped"})
            continue
        local=Counter()
        errs=Counter()
        meshes=0
        scanned=0
        try:
            env=UnityPy.load(str(path))
            for obj in env.objects:
                if getattr(obj.type,"name","")!="Mesh":continue
                meshes+=1
                if scanned>=max_per_file:continue
                scanned+=1
                try:
                    tree=obj.read_typetree()
                    stream=tree.get("m_StreamData") or {}
                    ref=stream.get("path") or stream.get("m_Path") or ""
                    size=int(stream.get("size") or stream.get("m_Size") or 0)
                    if ref and size>0:
                        local[ref]+=1
                        result["stream_paths"][ref]+=1
                        result["meshes_with_stream"]+=1
                        result["claimed_stream_bytes"]+=size
                        offset=int(stream.get("offset") if stream.get("offset") is not None else stream.get("m_Offset",0))
                        status=classify_stream_range(root,ref,offset,size)
                        result["stream_range_status"][status]+=1
                        result["range_status_by_path"].setdefault(ref,Counter())[status]+=1
                except Exception as exc:
                    errs[type(exc).__name__]+=1
                    result["errors"][type(exc).__name__]+=1
        except Exception as exc:
            errs["load:"+type(exc).__name__]+=1
            result["errors"]["load:"+type(exc).__name__]+=1
        result["mesh_count"]+=meshes
        result["inspected_meshes"]+=scanned
        result["files"].append({"file":path.name,"mesh_objects":meshes,
                                "inspected":scanned,"stream_paths":dict(local.most_common(5)),
                                "errors":dict(errs)})
    result["stream_paths"]=dict(result["stream_paths"].most_common(30))
    result["errors"]=dict(result["errors"]) 
    result["stream_range_status"]=dict(result["stream_range_status"]) 
    result["range_status_by_path"]={p:dict(c) for p,c in result["range_status_by_path"].items()}
    result["caveat"]="m_StreamData range coverage checks only local source files; an LFS pointer is not a loaded stream. Does not audit texture/animation/audio streams or prove exported Unity geometry integrity. Counts are not distinct bytes needed on device."
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("Raft/Raft_Data"))
    p.add_argument("--max-per-file",type=int,default=80)
    p.add_argument("--out",type=Path,default=Path("out/mesh-streams.json"))
    a=p.parse_args()
    data=scan(a.root,a.max_per_file)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    for k in ("mesh_count","inspected_meshes","meshes_with_stream","claimed_stream_bytes","stream_paths","stream_range_status","errors"):
        print(k+":",data[k])
    print("Per-source Mesh sampled counts:",[(r['file'],r.get('mesh_objects'),r.get('inspected'),r.get('stream_paths')) for r in data['files'] if r.get('stream_paths')][:28])
