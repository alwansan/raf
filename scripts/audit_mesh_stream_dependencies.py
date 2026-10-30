#!/usr/bin/env python3
"""Inspect serialized Unity Mesh streaming dependencies without reading game stream payloads.

Read-only. Uses UnityPy type trees to obtain m_StreamData.path and size;
does not execute original game binaries and does not publish original assets.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import re

import UnityPy

def is_pointer(p):
    return p.stat().st_size<200 and p.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1")

def scan(root,max_per_file):
    result={"files":[],"stream_paths":Counter(),"errors":Counter(),"mesh_count":0,
            "inspected_meshes":0,"meshes_with_stream":0,"claimed_stream_bytes":0}
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
    result["caveat"]="Sample up to max_per_file Mesh objects per input file; m_StreamData may not cover texture/animation streams. Counts are not distinct geometry meshes or bytes required on device."
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
    for k in ("mesh_count","inspected_meshes","meshes_with_stream","claimed_stream_bytes","stream_paths","errors"):
        print(k+":",data[k])
    print("Per-source Mesh sampled counts:",[(r['file'],r.get('mesh_objects'),r.get('inspected'),r.get('stream_paths')) for r in data['files'] if r.get('stream_paths')][:28])
