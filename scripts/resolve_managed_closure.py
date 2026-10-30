#!/usr/bin/env python3
"""Plan the original managed SDK reference closure without executing assemblies.
Core/framework/package assemblies stay supplied by Unity, never by Windows copies.
"""
import argparse
import json
from pathlib import Path
import re
try:
    from scripts.stage_raft_managed_dlls import ESSENTIALS
except ModuleNotFoundError:
    from stage_raft_managed_dlls import ESSENTIALS

PACKAGES={"UnityEngine.UI","Unity.TextMeshPro","Unity.InputSystem","Unity.InputSystem.ForUI"}
FRAMEWORK={"mscorlib","netstandard","System","Mono.Security","UnityEngine","Assembly-CSharp"}
NAME=re.compile(r"^[A-Za-z_][A-Za-z_0-9.-]*$")

def provided(name):
    return (name in PACKAGES or name in FRAMEWORK or name.startswith("System.") or
            (name.startswith("UnityEngine.") and name.endswith("Module")))

def refs(path):
    import dnfile
    pe=dnfile.dnPE(str(path))
    try:
        if pe.net is None:
            raise ValueError("Not a managed SDK assembly: "+path.name)
        table=pe.net.mdtables.AssemblyRef
        return [str(row.Name) for row in table.rows] if table else []
    finally:
        pe.close()

def plan(managed: Path, seeds=None, *, sdk_manifest=None, reader=refs):
    seeds=list(ESSENTIALS if seeds is None else seeds)
    if sdk_manifest is not None:
        data=json.loads(Path(sdk_manifest).read_text(encoding="utf8"))
        seeds.extend(name+".dll" for name in data.get("referencedAssemblies",[]))
    queue=list(seeds)
    seen=set()
    selected=[]
    supplied=set()
    graph={}
    while queue:
        filename=queue.pop(0)
        if not filename.endswith(".dll") or not NAME.fullmatch(filename[:-4]):
            raise ValueError("Invalid assembly identity in SDK dependency plan")
        assembly=filename[:-4]
        if assembly.startswith("UnityEditor"):
            raise ValueError("Editor-only dependency cannot be staged for Android: "+assembly)
        if assembly=="PlayFab_o":
            raise ValueError("Overlapping PlayFab_o SDK is not a valid additional provider")
        if provided(assembly):
            supplied.add(assembly)
            continue
        if filename in seen: continue
        seen.add(filename)
        path=managed/filename
        if not path.is_file(): raise FileNotFoundError("Original SDK dependency missing: "+filename)
        dependencies=sorted(set(reader(path)))
        if any(not NAME.fullmatch(name) for name in dependencies):
            raise ValueError("Invalid metadata reference in "+filename)
        graph[assembly]=dependencies
        selected.append(filename)
        queue.extend(name+".dll" for name in dependencies)
    return {"libraries":selected,"staged":len(selected),
            "total_bytes":sum((managed/name).stat().st_size for name in selected),
            "supplied_by_unity_or_reconstructed_game":sorted(supplied),
            "reference_graph":graph,
            "note":"Metadata plan only; not Android native/runtime compatibility proof."}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--managed",required=True,type=Path)
    parser.add_argument("--sdk-manifest",type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    result=plan(args.managed,sdk_manifest=args.sdk_manifest)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("Original SDK closure count:",result["staged"])
    print("Original SDK closure bytes:",result["total_bytes"])
    print("Original SDK closure libraries:",result["libraries"])
    print("Unity/framework references left external:",result["supplied_by_unity_or_reconstructed_game"])
