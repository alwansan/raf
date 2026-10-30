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
def build(project: Path, *, orphan_check=None) -> dict:
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
    usages={}
    script_ref=re.compile(r"(?m)^[ \t]*m_Script:[ \t]*\{[^}\r\n]*\bguid:[ \t]*([0-9a-fA-F]{32})")
    for asset in assets.rglob("*"):
        if asset.is_file() and asset.suffix in {".unity",".prefab",".asset"}:
            for guid in script_ref.findall(asset.read_text(encoding="utf8",errors="replace")):
                guid=guid.lower()
                refs[guid]+=1
                usages.setdefault(guid,set()).add(asset.relative_to(assets).as_posix())
    for row in rows:
        row["references"]=refs[row["sourceGuid"]]
        row["usagePaths"]=sorted(usages.get(row["sourceGuid"],set()))
    orphans=[]
    for row in rows:
        # A pre-existing unresolved original resource, NOT a runtime SDK substitute.
        # Keep its asset and original script pointer unchanged; no empty Android behaviour.
        if (orphan_check is not None and
            row["assemblyName"]=="Sirenix.Serialization.Config" and
            row["fullTypeName"] in {"GlobalSerializationConfig","Sirenix.Serialization.GlobalSerializationConfig"} and
            row["references"]==1 and len(row["usagePaths"])==1 and
            Path(row["usagePaths"][0]).name=="GlobalSerializationConfig.asset" and
            orphan_check(row["assemblyName"])):
            orphans.append({"sourceGuid":row["sourceGuid"],"usagePath":row["usagePaths"][0],
                            "originalFile":"resources.assets","originalScriptPathId":934,
                            "originalObjectPathId":6381,
                            "reason":"Original registry points to a provider absent from original Managed files and all AssemblyRef tables. Preserve unresolved original data; never fabricate runtime behaviour."})
    orphan_guids={item["sourceGuid"] for item in orphans}
    providers=sorted({row["assemblyName"] for row in rows if row["references"] and row["sourceGuid"] not in orphan_guids})
    return {"scripts":rows,"referencedAssemblies":providers,"preservedOriginalOrphans":orphans,
            "statistics":{"sdk_source_identities":len(rows),
                          "sdk_references":sum(row["references"] for row in rows),
                          "referenced_sdk_assemblies":len(providers)}}
def original_orphan_check(managed: Path):
    import dnfile
    references=set()
    types=set()
    for path in sorted(managed.glob("*.dll")):
        pe=dnfile.dnPE(str(path))
        try:
            if pe.net is None: continue
            table=pe.net.mdtables.AssemblyRef
            if table: references.update(str(row.Name) for row in table.rows)
            table=pe.net.mdtables.TypeDef
            if table:
                types.update((str(row.TypeNamespace),str(row.TypeName)) for row in table.rows)
        finally: pe.close()
    def check(assembly):
        return (not (managed/(assembly+".dll")).exists() and assembly not in references and
                ("Sirenix.Serialization","GlobalSerializationConfig") not in types)
    return check

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--managed",type=Path)
    args=parser.parse_args()
    report=build(args.project,orphan_check=original_orphan_check(args.managed) if args.managed else None)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("SDK MonoScript identity manifest:",report["statistics"])

    print("Preserved pre-existing original unresolved configuration records:",report["preservedOriginalOrphans"])
    print("Referenced SDK providers:",report["referencedAssemblies"])
    for row in report["scripts"]:
        if row["references"] and args.managed and not (args.managed/(row["assemblyName"]+".dll")).exists():
            print("Original serialized provider not physically present:",row)
