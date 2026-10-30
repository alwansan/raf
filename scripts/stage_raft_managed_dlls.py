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
import re
from pathlib import Path
import shutil

# Unity 2021 UGUI/TMP packages should supply their own compatible assemblies.
# Original Windows UI/TMP DLLs conflict with those packages (CS1704).
EDITOR_PROVIDED_ASSEMBLIES = frozenset({"UnityEngine.UI.dll", "Unity.TextMeshPro.dll", "Unity.InputSystem.dll"})

ESSENTIALS=(
    "FMODUnity.dll",
    "FMODUnityResonance.dll",
    "PlayFab.dll",
    "Unity.Netcode.Runtime.dll",
    "Unity.Netcode.Components.dll",
    "Unity.Networking.Transport.dll",
    "Newtonsoft.Json.dll",
    # Compilation bridge only; original Steam native transport is not Android-safe.
    "com.rlabrecque.steamworks.net.dll",
    # Original metadata closure for BitField32 and ConfigResponse.
    "Unity.Collections.dll",
    "Unity.Collections.LowLevel.ILSupport.dll",
    "Unity.Mathematics.dll",
    "Unity.Burst.dll",
    "Unity.Burst.Unsafe.dll",
    "Unity.Services.RemoteConfig.dll",
    "Unity.Services.Core.Internal.dll",
    "Unity.Services.Core.dll",
    "PathCreator.dll",
    "NavMeshComponents.dll",
    "Tayx.Graphy.dll",
    "Unity.Analytics.DataPrivacy.dll",
    "MeshExtension.dll",
)
OPTIONAL=(
    "Sirenix.OdinInspector.Attributes.dll",
    "JBooth.MicroSplat.Core.dll",
)
def stage(managed:Path,project:Path,*,apply:bool,extended:bool=False, dependency_plan:dict|None=None)->dict:
    if not managed.is_dir() or not (project/"Assets").is_dir():
        raise FileNotFoundError("Original managed DLL directory or project Assets missing")
    out=project/"Assets"/"Plugins"/"RaftManagedReferences"
    selected=ESSENTIALS+(OPTIONAL if extended else ())
    if dependency_plan is not None:
        if extended: raise ValueError("Choose a dependency plan or extended mode, not both")
        selected=dependency_plan.get("libraries")
        if not isinstance(selected,list) or not selected or len(selected)!=len(set(selected)):
            raise ValueError("Dependency plan must contain unique library filenames")
        try:
            from scripts.resolve_managed_closure import provided
        except ModuleNotFoundError:
            from resolve_managed_closure import provided
        for name in selected:
            if not isinstance(name,str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9.-]*\.dll",name):
                raise ValueError("Invalid dependency plan filename")
            asm=name[:-4]
            if provided(asm) or asm.startswith("UnityEditor") or asm=="PlayFab_o":
                raise ValueError("Refusing an engine/package/editor/overlapping DLL: "+name)
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
    # Validate every dependency before writing any plugin.
    if apply:
        out.mkdir(parents=True,exist_ok=True)
        for row in rows:
            shutil.copyfile(managed/row["name"],out/row["name"])
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
    a.add_argument("--plan",type=Path,help="Validated SDK metadata closure plan")
    a.add_argument("--extended",action="store_true")
    a.add_argument("--apply",action="store_true")
    args=a.parse_args()
    result=stage(args.managed,args.project,apply=args.apply,extended=args.extended,
                 dependency_plan=json.loads(args.plan.read_text()) if args.plan else None)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
