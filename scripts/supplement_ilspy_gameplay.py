#!/usr/bin/env python3
"""Supplement Unity MonoScript reconstruction with ILSpy helper types not exported by AssetRipper.

AssetRipper emits only script-bearing MonoBehaviour/ScriptableObject templates,
not necessarily every helper type in Assembly-CSharp.dll. The original ILSpy
decompilation contains other enums, interfaces, classes and structs.

This tool copies only previously ABSENT C# filenames to Assets/Scripts/Assembly-CSharp-Extras.
It NEVER replaces existing Unity .cs or .meta files and NEVER publishes the source.
Run only inside a transient private build environment after ILSpy CSharp9 decompile.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil

VALID_FILE = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*\.cs$")
TYPE_DECL = re.compile(r"\b(?:class|struct|interface|enum|delegate|record)\s+[A-Za-z_]\w*\b")
ASSEMBLY_ATTR = re.compile(r"(?m)^\s*\[assembly\s*:")

def supplement(project: Path, ilspy: Path, *, apply: bool) -> dict:
    scripts=project/"Assets"/"Scripts"
    primary=scripts/"Assembly-CSharp"
    extras=scripts/"Assembly-CSharp-Extras"
    if not primary.is_dir() or not ilspy.is_dir():
        raise FileNotFoundError("Expected existing Unity Assets/Scripts/Assembly-CSharp and ILSpy sources")
    # No duplicate filename additions: preserve every original Unity .cs and .cs.meta path,
    # regardless of whether an earlier overlay could not match a source namespace.
    existing={p.name.lower() for p in scripts.rglob("*.cs")}
    counters=Counter()
    samples=[]
    for source in sorted(ilspy.rglob("*.cs")):
        counters["source_total"]+=1
        relative=source.relative_to(ilspy)
        if relative.parts[0] in ("Properties","obj","bin") or source.name.lower() in ("assemblyinfo.cs","globalusings.cs"):
            counters["skipped_project_metadata"]+=1
            continue
        if not VALID_FILE.fullmatch(source.name):
            counters["skipped_non_identifier_filename"]+=1
            continue
        if source.name.lower() in existing:
            counters["skipped_existing_filename"]+=1
            continue
        target=extras/relative
        if target.exists():
            counters["skipped_existing_extra"]+=1
            continue
        content=source.read_text(encoding="utf8",errors="replace")
        if ASSEMBLY_ATTR.search(content):
            counters["skipped_assembly_attributes"]+=1
            continue
        if not TYPE_DECL.search(content):
            counters["skipped_without_type"]+=1
            continue
        counters["added"]+=1
        if len(samples)<15:samples.append(relative.as_posix())
        if apply:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
        # Suppress intra-batch filename duplicates conservatively too.
        existing.add(source.name.lower())
    report={"statistics":dict(counters),"example_added_files":samples,
            "notes":"Only file-unique missing helper type sources, not compiled/released original game code; Unity Editor still required."}
    print("Supplement helper CSharp:",report)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True,type=Path)
    p.add_argument("--ilspy",required=True,type=Path)
    p.add_argument("--report",type=Path,default=Path("out/supplement-report.json"))
    p.add_argument("--apply",action="store_true")
    p.add_argument("--min-added",type=int,default=0)
    args=p.parse_args()
    report=supplement(args.project,args.ilspy,apply=args.apply)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    if report["statistics"].get("added",0)<args.min_added:
        raise SystemExit("Too few additional ILSpy helper types; inspect source filename mapping")
