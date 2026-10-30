#!/usr/bin/env python3
"""Overlay uniquely matched ILSpy C# files onto AssetRipper's script .meta layout.

DO NOT PUBLISH THE INPUTS OR OUTPUT: they contain decompiled proprietary code.
This helper operates on local, independently provided directories; it preserves
Unity .meta identities. It does not claim compilation or runtime validity.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from pathlib import Path
import argparse
import json
import re
import sys

def build_index(files):
    result=defaultdict(list)
    for p in files:
        result[p.name].append(p)
    return result

def map_sources(project:Path, decompiled:Path, apply:bool) -> dict:
    assets=project/"Assets"
    if not assets.is_dir() or not decompiled.is_dir():
        raise FileNotFoundError("Expected Unity ExportedProject/Assets and ILSpy C# directory")
    asset_scripts=list(assets.rglob("*.cs"))
    ilspy_files=list(decompiled.rglob("*.cs"))
    target_index=build_index(asset_scripts)
    source_index=build_index(ilspy_files)
    report={
        "asset_csharp_files":len(asset_scripts),
        "ilspy_csharp_files":len(ilspy_files),
        "asset_csharp_with_metas":sum(p.with_suffix(".cs.meta").is_file() for p in asset_scripts),
        "asset_target_paths_containing_assembly_csharp":sum("Assembly-CSharp" in p.parts for p in asset_scripts),
        "asset_samples":[str(p.relative_to(assets)) for p in asset_scripts[:8]],
        "ilspy_samples":[str(p.relative_to(decompiled)) for p in ilspy_files[:8]],
        "common_unique_names":0,
        "replacements":0,
        "bytes_before":0,
        "bytes_after":0,
        "ambiguous_names":0,
        "unmatched":0,
        "nonclass_sources":0,
        "namespace_mismatches":0,
        "critical_classes":{},
        "missing_meta":0,
        "examples":[],
        "apply":apply,
        "limitations":"Name-unique conservative pairing. Does not prove class serialization, compile or scene correctness.",
    }
    for name,targets in target_index.items():
        srcs=source_index.get(name,[])
        if not srcs:
            report["unmatched"]+=len(targets)
            continue
        if len(targets)!=1 or len(srcs)!=1:
            report["ambiguous_names"]+=len(targets)
            continue
        target,src=targets[0],srcs[0]
        if "Assembly-CSharp" not in target.parts:
            # Never replace code exported from unrelated managed assemblies.
            continue
        if not target.with_suffix(".cs.meta").is_file():
            report["missing_meta"]+=1
            continue
        report["common_unique_names"]+=1
        stem=src.stem
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*",stem):
            report["nonclass_sources"]+=1
            continue
        source=src.read_text(encoding="utf8",errors="replace")
        stub=target.read_text(encoding="utf8",errors="replace")
        def get_namespace(text):
            match=re.search(r"(?m)^\s*namespace\s+([\w.]+)\s*(?:[;{]|$)",text)
            return match.group(1) if match else ""
        if get_namespace(source)!=get_namespace(stub):
            report["namespace_mismatches"]+=1
            continue
        if not re.search(r"\b(?:class|struct|interface|enum)\s+"+re.escape(stem)+r"\b",source):
            report["nonclass_sources"]+=1
            continue
        prior=target.stat().st_size
        report["replacements"]+=1
        report["bytes_before"]+=prior
        report["bytes_after"]+=len(source.encode("utf8"))
        if name in {"Raft_Network.cs","SaveAndLoad.cs","GameManager.cs","SteamManager.cs"}:
            report["critical_classes"][name]={"stub_bytes":prior,"real_bytes":len(source.encode("utf8"))}
        if len(report["examples"])<9:
            report["examples"].append({"filename":name,"stub_bytes":prior,"real_bytes":len(source.encode("utf8"))})
        if apply:
            target.write_text(source,encoding="utf8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--ilspy",type=Path,required=True)
    p.add_argument("--report",type=Path,default=Path("out/code-overlay-report.json"))
    p.add_argument("--apply",action="store_true",help="write only within supplied project directory")
    args=p.parse_args()
    data=map_sources(args.project,args.ilspy,args.apply)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    for k in ("asset_csharp_files","ilspy_csharp_files","asset_csharp_with_metas",
              "asset_target_paths_containing_assembly_csharp","common_unique_names",
              "replacements","bytes_before","bytes_after","ambiguous_names",
              "unmatched","missing_meta","nonclass_sources","namespace_mismatches","apply"):
        print(k+":",data[k])
    print("Representative replacement sizes:",data["examples"])
    print("Important gameplay class source sizes:",data["critical_classes"])
    if not data["replacements"]: raise SystemExit("No safe script overlays identified; inspect path layout")
