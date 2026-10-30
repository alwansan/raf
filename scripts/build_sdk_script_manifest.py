#!/usr/bin/env python3
"""Record SDK MonoScript metadata before diagnostic template renames; no source bodies."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
try:
    from scripts.overlay_ilspy_gameplay import get_namespace
except ModuleNotFoundError:
    from overlay_ilspy_gameplay import get_namespace

GUID=re.compile(r"(?m)^guid:\s*([0-9a-fA-F]{32})")
DECL=re.compile(r"(?m)^[ \t]*(?:(?:public|private|protected|internal|sealed|abstract|partial|static|unsafe|readonly)\s+)*(?:class|struct|interface|enum)\s+([A-Za-z_]\w*)")
def build(project: Path) -> dict:
    assets=project/"Assets"
    scripts=assets/"Scripts"
    rows=[]
    seen=set()
    for meta in sorted(scripts.rglob("*.cs.meta")):
        relative=meta.relative_to(scripts)
        assembly=relative.parts[0]
        if assembly in {"Assembly-CSharp","Assembly-CSharp-Extras"}: continue
        match=GUID.search(meta.read_text(encoding="utf-8-sig")[:1000])
        if not match: raise ValueError("SDK source metadata has no valid GUID: "+str(relative))
        guid=match.group(1).lower()
        if guid in seen: raise ValueError("Duplicate SDK source GUID; resolve ambiguity first.")
        seen.add(guid)
        source=meta.with_name(meta.name[:-5])
        content=source.read_text(encoding="utf-8-sig")
        declaration=DECL.search(content)
        name=declaration.group(1) if declaration else ""
        namespace=get_namespace(content)
        full=(namespace+"." if namespace else "")+name if name else ""
        rows.append({"sourceGuid":guid,"assemblyName":assembly,
                     "fullTypeName":full,"simpleTypeName":name,
                     "sourcePath":source.relative_to(assets).as_posix()})
    refs=Counter()
    script_ref=re.compile(r"(?m)^[ \t]*m_Script:[ \t]*\{[^}\r\n]*\bguid:[ \t]*([0-9a-fA-F]{32})")
    for asset in assets.rglob("*"):
        if asset.is_file() and asset.suffix in {".unity",".prefab",".asset"}:
            refs.update(g.lower() for g in script_ref.findall(asset.read_text(encoding="utf8",errors="replace")))
    for row in rows:
        row["references"]=refs[row["sourceGuid"]]
    providers=sorted({row["assemblyName"] for row in rows if row["references"]})
    return {"scripts":rows,"referencedAssemblies":providers,
            "statistics":{"sdk_source_identities":len(rows),
                          "sdk_references":sum(row["references"] for row in rows),
                          "referenced_sdk_assemblies":len(providers)}}
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    report=build(args.project)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("SDK MonoScript identity manifest:",report["statistics"])
