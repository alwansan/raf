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


def _meta_hashes(root: Path) -> dict:
    import hashlib
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*.cs.meta")}


def _audit_original_source_coverage(scripts: Path, ilspy: Path) -> dict:
    """Verify unique gameplay identities, real source content and original namespaces."""
    from collections import defaultdict
    index=defaultdict(list)
    for p in scripts.rglob("*.cs"):
        if "Assembly-CSharp" in p.parts or "Assembly-CSharp-Extras" in p.parts:
            index[_source_identity(p)].append(p)
    originals=defaultdict(list)
    for p in sorted(ilspy.rglob("*.cs")):
        rel=p.relative_to(ilspy)
        if rel.parts[0] in ("Properties","obj","bin") or p.name.lower() in ("assemblyinfo.cs","globalusings.cs"):
            continue
        if not VALID_FILE.fullmatch(p.name):
            continue
        content=p.read_text(encoding="utf-8-sig",errors="replace")
        if ASSEMBLY_ATTR.search(content) or not TYPE_DECL.search(content):
            continue
        originals[_source_identity(p)].append(p)
    if not originals:
        raise ValueError("No eligible original gameplay source types")
    ident=re.compile(r"[A-Za-z_]\w*")
    decl=re.compile(r"\b(?:class|struct|interface|enum|record)\s+([A-Za-z_]\w*)")
    ignored=set("public private protected internal static readonly sealed partial abstract virtual override new class struct interface enum record delegate namespace using return this base true false null void int bool float double string object var get set value if else for foreach while do switch case break continue default try catch finally throw in out ref params async await where global System UnityEngine".split())
    def symbols(code):
        return {x for x in ident.findall(code) if len(x)>=3 and x not in ignored}
    for key,sources in originals.items():
        targets=index.get(key,[])
        if len(sources)!=1 or len(targets)!=1:
            raise ValueError(f"Original game source identity missing or ambiguous: {key}; original={len(sources)}, exported={len(targets)}")
        original=sources[0].read_text(encoding="utf-8-sig",errors="replace")
        exported=targets[0].read_text(encoding="utf-8-sig",errors="replace")
        types=set(decl.findall(original))
        if not TYPE_DECL.search(exported) or (types and not (types & set(decl.findall(exported)))):
            raise ValueError(f"Missing original type declaration: {key}")
        expected=symbols(original)
        shared=len(expected & symbols(exported))
        if len(expected)>=12 and shared<max(5,int(len(expected)*0.40)):
            raise ValueError(f"Source body missing/truncated: {key}, shared {shared}/{len(expected)} identifiers")
    return {"verified_eligible_sources":len(originals),"unique_original_identities":len(originals)}


def _source_identity(path: Path) -> tuple:
    code=path.read_text(encoding="utf-8-sig",errors="replace")
    match=re.search(r"(?m)^\s*namespace\s+([\w.]+)\s*(?:[;{]|$)",code)
    return path.name, match.group(1) if match else ""


def supplement(project: Path, ilspy: Path, *, apply: bool, coverage_mode: str = 'legacy') -> dict:
    if coverage_mode not in ("legacy","decompiled"):
        raise ValueError("Unknown ILSpy coverage mode")
    scripts=project/"Assets"/"Scripts"
    original_metas=_meta_hashes(scripts)
    primary=scripts/"Assembly-CSharp"
    extras=scripts/"Assembly-CSharp-Extras"
    if not primary.is_dir() or not ilspy.is_dir():
        raise FileNotFoundError("Expected existing Unity Assets/Scripts/Assembly-CSharp and ILSpy sources")
    # No duplicate filename additions: preserve every original Unity .cs and .cs.meta path,
    # regardless of whether an earlier overlay could not match a source namespace.
    def identity(path):
        text=path.read_text(encoding="utf-8-sig",errors="replace")
        match=re.search(r"(?m)^\s*namespace\s+([\w.]+)\s*(?:[;{]|$)",text)
        return (path.name, match.group(1) if match else "")
    existing={identity(p) for p in scripts.rglob("*.cs")}
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
        if identity(source) in existing:
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
        existing.add(identity(source))
    if coverage_mode=="decompiled" and counters.get("added",0):
        raise ValueError(f"Decompiled exporter omitted {counters['added']} original types")
    if apply and _meta_hashes(scripts)!=original_metas:
        raise ValueError("CSharp .meta/GUID bytes changed during supplementation")
    if apply:
        counters.update(_audit_original_source_coverage(scripts,ilspy))
    report={"statistics":dict(counters),"coverage_mode":coverage_mode,"example_added_files":samples,
            "notes":"Only file-unique missing helper type sources, not compiled/released original game code; Unity Editor still required."}
    print("Supplement helper CSharp:",report)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True,type=Path)
    p.add_argument("--ilspy",required=True,type=Path)
    p.add_argument("--report",type=Path,default=Path("out/supplement-report.json"))
    p.add_argument("--apply",action="store_true")
    p.add_argument("--coverage-mode",choices=("legacy","decompiled"),default="legacy")
    p.add_argument("--min-original-sources",type=int,default=0)
    p.add_argument("--min-added",type=int,default=0)
    args=p.parse_args()
    report=supplement(args.project,args.ilspy,apply=args.apply,coverage_mode=args.coverage_mode)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    if args.min_original_sources and report["statistics"].get("verified_eligible_sources",0)<args.min_original_sources:
        raise SystemExit("Incomplete original CSharp type coverage")
    if report["statistics"].get("added",0)<args.min_added:
        raise SystemExit("Too few additional ILSpy helper types; inspect source filename mapping")
