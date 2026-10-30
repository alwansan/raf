#!/usr/bin/env python3
"""Safely inspect Unity serialized MonoScript identities in a non-LFS sample.

Reports aggregate counts only, not original game assets or reconstructed source.
The read-only analysis is intended to test whether standalone serialized data
retains script identities that were lost during Unity YAML export.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import json
import sys

import UnityPy

def inspect(root:Path) -> dict:
    paths=[root/n for n in (
        "globalgamemanagers","level0","level1","level37","level38","level39",
        "sharedassets1.assets","sharedassets37.assets","sharedassets38.assets","sharedassets39.assets")]
    report={"UnityPy_version":getattr(UnityPy,"__version__","unknown"),"samples":[]}
    all_types=Counter()
    for path in paths:
        if not path.is_file():continue
        if path.stat().st_size < 200 and path.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise RuntimeError(f"Refusing to parse Git LFS pointer: {path}")
        counts=Counter()
        externals=[]
        mono_scripts=[]
        mono_behaviours=[]
        parse_errors=Counter()
        try:
            env=UnityPy.load(str(path))
            for obj in env.objects:
                if not externals:
                    externals=[e.path for e in getattr(obj.assets_file,"externals",[])]
                typename=getattr(obj.type,"name","unknown")
                counts[typename]+=1
                if typename=="MonoScript" and len(mono_scripts)<40:
                    try:
                        raw=obj.read()
                        cls=str(getattr(raw,"m_ClassName",""))
                        ns=str(getattr(raw,"m_Namespace",""))
                        asm=str(getattr(raw,"m_AssemblyName",""))
                        mono_scripts.append({"class":cls,"namespace":ns,"assembly":asm,
                                             "path_id":str(obj.path_id)})
                    except Exception as exc:
                        parse_errors["MonoScript:"+type(exc).__name__]+=1
                if typename=="MonoBehaviour" and len(mono_behaviours)<80:
                    try:
                        raw=obj.read()
                        script=getattr(raw,"m_Script",None)
                        fid=getattr(script,"m_FileID",None) if script is not None else None
                        pid=getattr(script,"m_PathID",None) if script is not None else None
                        mono_behaviours.append({"file_id":fid,"path_id":pid})
                    except Exception as exc:
                        parse_errors["MonoBehaviour:"+type(exc).__name__]+=1
        except Exception as exc:
            parse_errors["Asset:"+type(exc).__name__]+=1
        all_types.update(counts)
        report["samples"].append({
            "file":path.name,"size_bytes":path.stat().st_size,
            "counts":{"all":sum(counts.values()),"MonoScript":counts["MonoScript"],
                      "MonoBehaviour":counts["MonoBehaviour"]},
            "external_dependencies":externals,
            "script_identities":mono_scripts,
            "behavior_pointer_examples":mono_behaviours[:10],
            "parse_errors":dict(parse_errors),
        })
    report["overall"]={
        "files":len(report["samples"]),
        "MonoScript":all_types["MonoScript"],
        "MonoBehaviour":all_types["MonoBehaviour"],
        "all_objects":sum(all_types.values()),
    }
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("Raft/Raft_Data"))
    p.add_argument("--out",type=Path,default=Path("out/unitypy-monoscripts.json"))
    args=p.parse_args()
    report=inspect(args.root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("UnityPy version:",report["UnityPy_version"])
    print("SUMMARY:",report["overall"])
    for f in report["samples"]:
        print("FILE:",f["file"],"object counts:",f["counts"],
              "identity count sample:",len(f["script_identities"]),"errors:",f["parse_errors"])
        print("Serialized file external dependencies (first 12):",f["external_dependencies"][:12])
        print("Script sample (max 5):",f["script_identities"][:5])
        print("Behaviour PPtr sample (max 3):",f["behavior_pointer_examples"][:3])
    if not report["samples"]:
        raise SystemExit("No Unity serialized source files inspected")
