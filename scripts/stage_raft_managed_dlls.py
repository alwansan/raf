#!/usr/bin/env python3
"""Stage narrowly allowlisted original managed DLLs for temporary Unity Editor compile tests.

Never execute DLLs. Never copy UnityEngine.CoreModule, System.*, mscorlib,
or full game Assembly-CSharp.dll into exported Assets: that would cause major
engine/core assembly conflicts. The selected game dependencies are known to
exist in original Raft/Raft_Data/Managed, but Unity Editor import compatibility
and Android runtime portability must still be verified.

Only run in a disposable CI Unity project, not in a published repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

# Unity 2021 UGUI/TMP packages should supply their own compatible assemblies.
# Original Windows UI/TMP DLLs conflict with those packages (CS1704).
EDITOR_PROVIDED_ASSEMBLIES = frozenset({"UnityEngine.UI.dll", "Unity.TextMeshPro.dll"})

ESSENTIALS=(
    "FMODUnity.dll",
    "FMODUnityResonance.dll",
    "PlayFab.dll",
    "Unity.Netcode.Runtime.dll",
    "Unity.Netcode.Components.dll",
    "Unity.Networking.Transport.dll",
    "Newtonsoft.Json.dll",
)
OPTIONAL=(
    "com.rlabrecque.steamworks.net.dll",
    "PathCreator.dll",
    "Sirenix.OdinInspector.Attributes.dll",
    "JBooth.MicroSplat.Core.dll",
    "Tayx.Graphy.dll",
)
def stage(managed:Path,project:Path,*,apply:bool,extended:bool=False)->dict:
    if not managed.is_dir() or not (project/"Assets").is_dir():
        raise FileNotFoundError("Original managed DLL directory or project Assets missing")
    out=project/"Assets"/"Plugins"/"RaftManagedReferences"
    selected=ESSENTIALS+(OPTIONAL if extended else ())
    rows=[]
    for name in selected:
        if name in EDITOR_PROVIDED_ASSEMBLIES:
            raise ValueError("Refusing to duplicate a Unity Editor-provided assembly: "+name)
        assert name.endswith(".dll") and "/" not in name
        src=managed/name
        if not src.is_file():
            raise FileNotFoundError("Original managed dependency missing: "+name)
        if src.stat().st_size<1000:
            raise ValueError("Suspiciously small library, refusing to stage: "+name)
        target=out/name
        if target.exists():
            raise FileExistsError("Refusing to overwrite existing managed DLL: "+name)
        rows.append({"name":name,"bytes":src.stat().st_size})
        if apply:
            out.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,target)
    report={"staged":len(rows),"total_bytes":sum(x["bytes"] for x in rows),
            "libraries":rows,"applied":apply,
            "limitations":"Compilation-only managed dependency recovery; may require alternative Android-compatible SDKs or stripping Windows native hooks."}
    print("Staged managed DLLs:",report)
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--managed",required=True,type=Path)
    a.add_argument("--project",required=True,type=Path)
    a.add_argument("--report",required=True,type=Path)
    a.add_argument("--extended",action="store_true")
    a.add_argument("--apply",action="store_true")
    args=a.parse_args()
    result=stage(args.managed,args.project,apply=args.apply,extended=args.extended)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
