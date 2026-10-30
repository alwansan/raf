#!/usr/bin/env python3
"""Import *unmatched* ILSpy .cs type files into an isolated Unity project.

Preserves every existing .cs and .cs.meta, including original MonoScript GUIDs.
Never commits extracted original gameplay C# and never creates an APK artifact.
Only intended for ephemeral CI reconstruction experiments.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import re
import hashlib

TYPE_RE=re.compile(r"\b(?:class|struct|enum|interface|delegate)\s+([A-Za-z_]\w*)")
VALID_STEM=re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\.cs$")
EXCLUDED={"AssemblyInfo.cs","GlobalUsings.g.cs","Assembly-CSharp.AssemblyInfo.cs",
          "Assembly-CSharp.GlobalUsings.g.cs","TypeForwarders.cs"}

def integrate(project:Path,source_root:Path,apply:bool)->dict:
    root=project/"Assets"
    if not root.is_dir() or not source_root.is_dir():raise FileNotFoundError("Assets or ILSpy source root absent")
    original=list(root.rglob("*.cs"))
    existing_names={p.name for p in original}
    dest=root/"Scripts/Assembly-CSharp/ILSpyOnly"
    sources=sorted(source_root.rglob("*.cs"))
    summary=Counter()
    examples=[]
    for source in sources:
        summary["ilspy_files"]+=1
        if source.name in existing_names:
            summary["name_already_present"]+=1
            continue
        if source.name in EXCLUDED or not VALID_STEM.fullmatch(source.name):
            summary["excluded_or_invalid"]+=1
            continue
        text=source.read_text(encoding="utf8",errors="replace")
        names=TYPE_RE.findall(text)
        if not names:
            summary["no_type_declarations"]+=1
            continue
        # Avoid adding ILSpy-generated internal top-level compiler member files
        # with synthetic angle-bracket names or attribute-only files.
        rel=source.relative_to(source_root)
        safe=Path(*[re.sub(r"[^A-Za-z_0-9.]", "_",part) for part in rel.parts])
        target=dest/safe
        if target.exists():raise FileExistsError(target)
        summary["new_type_sources"]+=1
        summary["bytes"]+=source.stat().st_size
        if len(examples)<16:examples.append(str(rel))
        if apply:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text,encoding="utf8")
    print("Unmatched ILSpy CSharp supplement:",dict(summary))
    print("Representative new source filenames only:",examples)
    return dict(summary)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--ilspy",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("out/ilspy-supplement.json"))
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    report=integrate(args.project,args.ilspy,args.apply)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    if report.get("new_type_sources",0)<10:raise SystemExit("Insufficient extra types; check decompilation layout")
