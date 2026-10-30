#!/usr/bin/env python3
"""Analyze Unity serialized reference placeholders, without printing assets or code."""
from collections import Counter
from pathlib import Path
import argparse
import json
import re

DEADBEEF="0000000deadbeef15deadf00d0000000"
GUID=re.compile(r"\bguid:\s*([0-9a-fA-F]{32})")
FILE_ID=re.compile(r"\bfileID:\s*(-?\d+)")
PROPERTY=re.compile(r"^\s*(?:-\s*)?([A-Za-z_][\w.]*)\s*:")
OBJ=re.compile(r"^---\s*!u!(\d+)(?:\s|$)")

def audit(project: Path)->dict:
    scenes=list(project.rglob("*.unity"))
    if not scenes:
        raise SystemExit("No .unity scene output to analyze")
    ref_by_property=Counter()
    ref_by_classid=Counter()
    ref_by_fileid=Counter()
    mesh_fileids=Counter()
    sampled_scenes=Counter()
    count=0
    script_count=0
    for scene in scenes:
        class_id="unknown"
        for line in scene.open(encoding="utf8",errors="replace"):
            m=OBJ.match(line)
            if m:
                class_id=m.group(1)
            gids=GUID.findall(line)
            if DEADBEEF not in (g.lower() for g in gids):
                continue
            hits=sum(g.lower()==DEADBEEF for g in gids)
            name=PROPERTY.match(line)
            prop=name.group(1) if name else "<list-or-other>"
            fid=FILE_ID.search(line)
            file_id=fid.group(1) if fid else "<missing>"
            count+=hits
            sampled_scenes[scene.name]+=hits
            ref_by_property[prop]+=hits
            ref_by_classid[class_id]+=hits
            ref_by_fileid[file_id]+=hits
            if prop=="m_Mesh":mesh_fileids[file_id]+=hits
            if prop=="m_Script":script_count+=hits
    return {
      "scenes":len(scenes),
      "deadbeef_total":count,
      "deadbeef_script":script_count,
      "by_property":dict(ref_by_property.most_common(24)),
      "by_yaml_classid":dict(ref_by_classid.most_common(24)),
      "by_pointer_fileid":dict(ref_by_fileid.most_common(24)),
      "mesh_by_pointer_fileid":dict(mesh_fileids.most_common(24)),
      "top_scenes_by_placeholder":dict(sampled_scenes.most_common(8)),
      "caveats":"Placeholder fileID is an exported Unity YAML pointer, not necessarily original input PPtr. Counts are serialized occurrences, not distinct meshes."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("out/mesh-reference-audit.json"))
    args=p.parse_args()
    data=audit(args.project)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2)+"\n")
    for k,v in data.items():
        if k!="caveats":print(k+":",v)
