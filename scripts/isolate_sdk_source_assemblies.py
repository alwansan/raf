#!/usr/bin/env python3
"""Isolate only generated SDK templates; real runtime script bindings are mandatory."""
import argparse
import json
from pathlib import Path
import re
def isolate(project: Path, manifest: Path, *, apply: bool):
    data=json.loads(manifest.read_text(encoding="utf8"))
    names=sorted({row["assemblyName"] for row in data["scripts"]})
    plans=[]
    for name in names:
        if name in {"Assembly-CSharp","Assembly-CSharp-Extras"} or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9.-]*",name):
            raise ValueError("Unsafe SDK source assembly identity")
        root=project/"Assets/Scripts"/name
        definitions=sorted(root.rglob("*.asmdef"))
        if not definitions: raise FileNotFoundError("SDK source asmdef missing: "+name)
        for path in definitions:
            contents=json.loads(path.read_text(encoding="utf8"))
            contents["includePlatforms"]=["Editor"]
            contents["excludePlatforms"]=[]
            contents["autoReferenced"]=False
            meta=path.with_name(path.name+".meta")
            if meta.exists() and not meta.is_file():
                raise ValueError("SDK asmdef metadata is not a file")
            # AssetRipper may emit a new assembly definition without its import
            # metadata. No original GUID exists to preserve in that case; leave
            # creation to Unity, while retaining every existing metadata byte.
            plans.append((path,contents,meta,meta.read_bytes() if meta.is_file() else None))
    for path,contents,meta,before in plans:
        if apply:
            path.write_text(json.dumps(contents,indent=2)+"\n",encoding="utf8")
            if (before is None and meta.exists()) or (before is not None and meta.read_bytes()!=before):
                raise RuntimeError("SDK metadata changed")
    result={"sdk_folders":len(names),"asmdefs":len(plans),"asmdefs_without_original_meta":sum(before is None for _,_,_,before in plans),"applied":apply}
    print("Generated SDK source isolation:",result)
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    isolate(a.project,a.manifest,apply=a.apply)
