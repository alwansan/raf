#!/usr/bin/env python3
"""Read-only diagnostic for Unity YAML GUID placeholders in private exports.

Only aggregate field names, counts, and serialized file names are printed.
Does not publish asset contents or modify project files.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import re
import json

DEADBEEF="0000000deadbeef15deadf00d0000000"
BUILTIN={
    "0000000000000000e000000000000000",
    "0000000000000000f000000000000000",
}
PATTERN=re.compile(r"guid:\s*([0-9a-fA-F]{32})")
META_PATTERN=re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})")
KEY_PATTERN=re.compile(r"^\s*(?:-\s+)?([A-Za-z_][A-Za-z_0-9.]*)\s*:")

def analyze(project:Path):
    registry=set()
    for meta in project.rglob("*.meta"):
        m=META_PATTERN.search(meta.read_text(encoding="utf8",errors="replace")[:500])
        if m:registry.add(m.group(1).lower())
    scene_files=list(project.rglob("*.unity"))
    if not scene_files:raise ValueError("No Unity scenes")
    refs=Counter()
    placeholder_keys=Counter()
    script_placeholders=0
    unknown=defaultdict(list)
    for scene in scene_files:
        with scene.open("r",encoding="utf8",errors="replace") as f:
            for line in f:
                allguids=PATTERN.findall(line)
                if not allguids:continue
                key=KEY_PATTERN.match(line)
                keyname=key.group(1) if key else "<sequence-or-other>"
                for guid in allguids:
                    guid=guid.lower()
                    refs[guid]+=1
                    if guid==DEADBEEF:
                        placeholder_keys[keyname]+=1
                        if keyname=="m_Script":script_placeholders+=1
                    elif guid not in registry and guid not in BUILTIN and guid!="0"*32 and len(unknown[guid])<3:
                        unknown[guid].append({"scene":scene.name,"field":keyname})
    return {
        "scenes":len(scene_files),
        "total_guids":sum(refs.values()),
        "guid_in_meta_uses":sum(n for g,n in refs.items() if g in registry),
        "deadbeef_uses":refs[DEADBEEF],
        "deadbeef_by_field":dict(placeholder_keys.most_common(30)),
        "deadbeef_script_uses":script_placeholders,
        "builtin_uses":sum(refs[g] for g in BUILTIN),
        "unknown_nonbuiltin":dict(unknown),
        "limitations":"Exported Unity YAML only; placeholders may represent Unity internals, absent game assets or import losses; needs per-field investigation."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("out/unity-guids-classified.json"))
    a=p.parse_args()
    r=analyze(a.project)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf8")
    for key in ("scenes","total_guids","guid_in_meta_uses","deadbeef_uses",
                "deadbeef_script_uses","builtin_uses"):
        print(key+":",r[key])
    print("Placeholder top serialized fields:",list(r["deadbeef_by_field"].items())[:15])
    print("Other unknown GUID and scene+field:",r["unknown_nonbuiltin"])
