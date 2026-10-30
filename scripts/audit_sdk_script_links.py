#!/usr/bin/env python3
"""Count serialized MonoScript GUID refs to third-party SDK source placeholders.

Never print game contents or modify assets. Helps choose SDK replacement safely.
"""
from pathlib import Path
from collections import Counter
import argparse
import re

ASSEMBLIES=("FMODUnity","PlayFab","com.rlabrecque.steamworks.net",
            "Unity.Netcode.Runtime","Unity.Networking.Transport")
GUID=re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})")
SCRIPT_RE=re.compile(r"m_Script:\s*\{[^\n}]*\bguid:\s*([0-9a-fA-F]{32})")
def audit(project):
    assets=project/"Assets"
    guids={}
    for asm in ASSEMBLIES:
        folder=assets/"Scripts"/asm
        entries=list(folder.rglob("*.cs.meta")) if folder.is_dir() else []
        gids=set()
        for meta in entries:
            m=GUID.search(meta.read_text(errors="replace")[:500])
            if m:gids.add(m.group(1).lower())
        guids[asm]=gids
    byfile=Counter()
    byasm=Counter()
    for path in list(assets.rglob("*.unity"))+list(assets.rglob("*.prefab")):
        txt=path.read_text(errors="replace")
        refs=Counter(m.lower() for m in SCRIPT_RE.findall(txt))
        byfile[path.suffix]+=1
        for asm,gids in guids.items():
            byasm[asm]+=sum(refs[g] for g in gids)
    print("Scanned serialized files:",dict(byfile))
    for asm in ASSEMBLIES:
        print("SDK source GUID coverage:",asm,
              "exported script metas:",len(guids[asm]),
              "scene/prefab m_Script GUID links:",byasm[asm],
              "deleting original scripts safe:",byasm[asm]==0)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    audit(p.parse_args().project)
