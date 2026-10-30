#!/usr/bin/env python3
"""Avoid duplicate original managed DLL vs AssetRipper-generated asmdef names.

Compilation-diagnostic only: keeps original MonoScript .cs.meta GUIDs and
renames only disposable asmdef JSON. Not a gameplay-correct SDK port.
"""
from pathlib import Path
import argparse
import hashlib
import json

def reconcile(project:Path,*,apply:bool)->dict:
    assets=project/"Assets"
    plugin=assets/"Plugins/RaftManagedReferences"
    if not plugin.is_dir():raise FileNotFoundError("Expected staged private managed plugins")
    dlls={p.stem for p in plugin.glob("*.dll")}
    rows=[]
    for file in sorted((assets/"Scripts").rglob("*.asmdef")):
        data=json.loads(file.read_text(encoding="utf8"))
        name=data.get("name")
        if not name or name not in dlls:continue
        prefix=hashlib.sha256(str(file.relative_to(assets)).encode()).hexdigest()[:9]
        renamed="RaftStub."+prefix+"."+name
        rows.append({"original":name,"replacement":renamed,"path":str(file.relative_to(assets))})
        if apply:
            data["name"]=renamed
            # Prevent disposable type stubs from shadowing original SDK types in
            # main Assembly-CSharp when precompiled DLLs provide the same classes.
            data["autoReferenced"]=False
            file.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    print("SDK asmdef name collisions avoided:",len(rows))
    for item in rows:print("Assembly collision:",item)
    return {"renamed":len(rows),"assemblies":rows}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    args=p.parse_args()
    reconcile(args.project,apply=args.apply)
