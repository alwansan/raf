#!/usr/bin/env python3
"""Overlay real ILSpy C# into AssetRipper gameplay scripts while preserving .meta GUIDs.

DO NOT PUBLISH THE INPUTS OR OUTPUT: they contain decompiled proprietary code.
This helper operates on local, independently provided directories; it preserves
Unity .meta identities. It does not claim compilation or runtime validity.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from pathlib import Path
import argparse
import json
import re
import sys

def get_namespace(text):
    text=text.lstrip("\ufeff")
    match=re.search(r"(?m)^\s*namespace\s+([\w.]+)\s*(?:[;{]|$)",text)
    return match.group(1) if match else ""

def build_index(files):
    result=defaultdict(list)
    for p in files:
        result[(p.name, get_namespace(p.read_text(encoding="utf8", errors="replace")))].append(p)
    return result

def map_sources(project:Path, decompiled:Path, apply:bool, *,
                recover_unqualified_stubs:bool=False,
                recover_unlinked_decompiled:bool=False) -> dict:
    assets=project/"Assets"
    if not assets.is_dir() or not decompiled.is_dir():
        raise FileNotFoundError("Expected Unity ExportedProject/Assets and ILSpy C# directory")
    asset_scripts=list(assets.rglob("*.cs"))
    gameplay_scripts=[p for p in asset_scripts if "Assembly-CSharp" in p.parts]
    ilspy_files=list(decompiled.rglob("*.cs"))
    target_index=build_index(gameplay_scripts)
    source_index=build_index(ilspy_files)
    # All existing .meta GUID identities are immutable; no .meta is synthesized.
    import hashlib
    def meta_hashes():
        return {p.relative_to(assets).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in assets.rglob("*.cs.meta")}
    original_meta_hashes=meta_hashes()
    report={
        "asset_csharp_files":len(asset_scripts),
        "ilspy_csharp_files":len(ilspy_files),
        "asset_csharp_with_metas":sum(p.with_suffix(".cs.meta").is_file() for p in asset_scripts),
        "asset_target_paths_containing_assembly_csharp":sum("Assembly-CSharp" in p.parts for p in asset_scripts),
        "asset_samples":[str(p.relative_to(assets)) for p in asset_scripts[:8]],
        "ilspy_samples":[str(p.relative_to(decompiled)) for p in ilspy_files[:8]],
        "common_unique_names":0,
        "replacements":0,
        "source_files_with_bom":sum(p.read_bytes().startswith(b"\xef\xbb\xbf") for p in ilspy_files),
        "recovered_generic_sources":0,
        "recovered_interface_sources":0,
        "bytes_before":0,
        "bytes_after":0,
        "ambiguous_names":0,
        "unmatched":0,
        "nonclass_sources":0,
        "namespace_mismatches":0,
        "unqualified_stubs_recovered":0,
        "critical_classes":{},
        "missing_meta":0,
        "recovered_unlinked_decompiled":0,
        "meta_hashes_unchanged":False,
        "examples":[],
        "apply":apply,
        "limitations":"Assembly-scoped, namespace-and-filename-unique conservative pairing. Does not prove class serialization, compile or scene correctness.",
    }
    for (name,namespace),targets in target_index.items():
        srcs=source_index.get((name,namespace),[])
        recovered_unqualified=False
        if not srcs and recover_unqualified_stubs and not namespace and len(targets)==1:
            candidates=[p for (filename,ns),paths in source_index.items() if filename==name and ns and (filename,ns) not in target_index for p in paths]
            stub=targets[0].read_text(encoding="utf8",errors="replace")
            # AssetRipper exported non-component types as unqualified MonoBehaviour
            # placeholders. Only recover field-only templates, never real method bodies.
            template=re.search(r"\bclass\s+"+re.escape(targets[0].stem)+r"\s*:\s*(?:UnityEngine\.)?MonoBehaviour\s*\{",stub)
            has_callable=re.search(r"\b\w+\s*\([^;{}]*\)\s*(?:\{|=>)",stub)
            if len(candidates)==1 and template and not has_callable:
                srcs=candidates
                recovered_unqualified=True
        if not srcs:
            report["unmatched"]+=len(targets)
            if any(key[0]==name for key in source_index):
                report["namespace_mismatches"]+=len(targets)
            continue
        if len(targets)!=1 or len(srcs)!=1:
            report["ambiguous_names"]+=len(targets)
            continue
        target,src=targets[0],srcs[0]
        if "Assembly-CSharp" not in target.parts:
            # Never replace code exported from unrelated managed assemblies.
            continue
        has_meta=target.with_suffix(".cs.meta").is_file()
        if not has_meta:
            report["missing_meta"]+=1
            if not recover_unlinked_decompiled:
                continue
        else:
            report["common_unique_names"]+=1
        stem=src.stem
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*",stem):
            report["nonclass_sources"]+=1
            continue
        source=src.read_text(encoding="utf8",errors="replace")
        stub=target.read_text(encoding="utf8",errors="replace")
        if get_namespace(source)!=get_namespace(stub) and not recovered_unqualified:
            report["namespace_mismatches"]+=1
            continue
        declared=re.search(r"\b(?:class|struct|interface|enum|record)\s+"+re.escape(stem)+r"\b",source)
        delegated=re.search(r"\bdelegate\b[^;{}]*\b"+re.escape(stem)+r"\s*(?:<[^;{}]*>)?\s*\(",source)
        if not (declared or delegated):
            report["nonclass_sources"]+=1
            continue
        prior=target.stat().st_size
        report["replacements"]+=1
        if not has_meta:
            report["recovered_unlinked_decompiled"]+=1
        if recovered_unqualified: report["unqualified_stubs_recovered"]+=1
        if re.search(r"\b(?:class|struct|interface)\s+"+re.escape(stem)+r"\s*<",source):
            report["recovered_generic_sources"]+=1
        if re.search(r"\binterface\s+"+re.escape(stem)+r"\b",source):
            report["recovered_interface_sources"]+=1
        report["bytes_before"]+=prior
        report["bytes_after"]+=len(source.encode("utf8"))
        if name in {"Raft_Network.cs","SaveAndLoad.cs","GameManager.cs","SteamManager.cs"}:
            report["critical_classes"][name]={"stub_bytes":prior,"real_bytes":len(source.encode("utf8"))}
        if len(report["examples"])<9:
            report["examples"].append({"filename":name,"stub_bytes":prior,"real_bytes":len(source.encode("utf8"))})
        if apply:
            target.write_text(source,encoding="utf8")
    report["meta_hashes_unchanged"]=(meta_hashes()==original_meta_hashes)
    if not report["meta_hashes_unchanged"]:
        raise ValueError("Original Unity CSharp .meta GUIDs changed during source overlay")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--ilspy",type=Path,required=True)
    p.add_argument("--report",type=Path,default=Path("out/code-overlay-report.json"))
    p.add_argument("--apply",action="store_true",help="write only within supplied project directory")
    p.add_argument("--recover-unqualified-stubs",action="store_true",help="Recover field-only unqualified AssetRipper MonoBehaviour placeholders using a unique original source")
    p.add_argument("--recover-unlinked-decompiled",action="store_true",
                   help="Opt in for Decompiled exporter: overlay original type bodies in unlinked CSharp sources without .cs.meta; never synthesize/replace Unity GUID metadata")
    args=p.parse_args()
    data=map_sources(args.project,args.ilspy,args.apply,
                     recover_unqualified_stubs=args.recover_unqualified_stubs,
                     recover_unlinked_decompiled=args.recover_unlinked_decompiled)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    for k in ("asset_csharp_files","ilspy_csharp_files","asset_csharp_with_metas",
              "asset_target_paths_containing_assembly_csharp","common_unique_names",
              "replacements","source_files_with_bom","recovered_generic_sources","recovered_interface_sources","bytes_before","bytes_after","ambiguous_names",
              "unmatched","missing_meta","recovered_unlinked_decompiled","meta_hashes_unchanged",
              "nonclass_sources","namespace_mismatches","unqualified_stubs_recovered","apply"):
        print(k+":",data[k])
    print("Representative replacement sizes:",data["examples"])
    print("Important gameplay class source sizes:",data["critical_classes"])
    if not data["replacements"]: raise SystemExit("No safe script overlays identified; inspect path layout")
