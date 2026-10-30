#!/usr/bin/env python3
"""Static-only risk map for reusing Raft Mono DLLs as Unity Editor plugins.

Does not execute original libraries or copy proprietary DLL contents.
"""
import argparse
import json
from pathlib import Path

CANDIDATES=["FMODUnity.dll","PlayFab.dll","Newtonsoft.Json.dll",
            "com.rlabrecque.steamworks.net.dll","Unity.Netcode.Runtime.dll",
            "Unity.Networking.Transport.dll"]
def audit(project,managed):
    assets=project/"Assets"
    asmdefs={}
    for path in assets.rglob("*.asmdef"):
        try:
            name=json.loads(path.read_text(encoding="utf8",errors="replace")).get("name","")
            if name:asmdefs.setdefault(name,[]).append(str(path.relative_to(assets)))
        except (ValueError,OSError):pass
    root=assets/"Scripts"
    for name in CANDIDATES:
        file=managed/name
        stem=file.stem
        source_dir=root/stem
        source_count=sum(1 for _ in source_dir.rglob("*.cs")) if source_dir.is_dir() else 0
        print("External managed plugin:",name,
              "exists:",file.is_file(),"bytes:",file.stat().st_size if file.is_file() else None,
              "recovered source count in same assembly directory:",source_count,
              "asmdef conflict:",asmdefs.get(stem,[]),
              "copy recommended for experiment:",file.is_file() and stem not in asmdefs)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--managed",type=Path,default=Path("Raft/Raft_Data/Managed"))
    a=p.parse_args()
    audit(a.project,a.managed)
