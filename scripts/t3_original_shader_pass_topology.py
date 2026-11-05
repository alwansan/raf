#!/usr/bin/env python3
"""T3 original ten Material-referenced Shader48 parsed Pass/SubShader topology.

Requires exact SHA pins for all four source shader owners. Only data from
serialized original m_ParsedForm is counted. Shader names, PathIDs, source
programs and raw serialized bytes never leave private CI staging.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

from scripts import t3_material_shader_same_export as t3
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint


def summarize(rows,expected=t3.SHADER_COUNT):
    if not isinstance(rows,dict) or len(rows)!=expected:
        raise ValueError("incomplete_authentic_selected_original_Shader_scope")
    counts=Counter()
    pass_hist=Counter()
    subsh_hist=Counter()
    per_owner=defaultdict(Counter)
    for key,parsed in rows.items():
        if (not isinstance(key,tuple) or len(key)!=2 or key[0] not in t3.TARGET_OWNERS
            or type(key[1]) is not int or key[1]<=0 or not isinstance(parsed,dict)):
            raise ValueError("invalid_original_selected_Shader_identity")
        subshaders=parsed.get("m_SubShaders")
        if not isinstance(subshaders,list):raise ValueError("invalid_original_SubShader_list")
        n=0
        for entry in subshaders:
            if not isinstance(entry,dict) or not isinstance(entry.get("m_Passes"),list):
                raise ValueError("invalid_original_Shader_Pass_schema")
            if not all(isinstance(p,dict) for p in entry["m_Passes"]):
                raise ValueError("invalid_original_Shader_Pass_record")
            n+=len(entry["m_Passes"])
        counts["selected_original_shader_count"]+=1
        counts["original_total_subshader_records"]+=len(subshaders)
        counts["original_total_pass_records"]+=n
        counts["original_shaders_with_more_than_one_pass"]+=int(n>1)
        counts["original_shaders_with_no_passes"]+=int(n==0)
        pass_hist[n]+=1
        subsh_hist[len(subshaders)]+=1
        per_owner[key[0]]["original_shaders"]+=1
        per_owner[key[0]]["original_subshaders"]+=len(subshaders)
        per_owner[key[0]]["original_passes"]+=n
    return {"schema_version":1,
        "experiment":"T3-authentic-original-selected-10-Shader48-parsed-Pass-topology",
        "selected_original_shader_count":counts["selected_original_shader_count"],
        "original_total_subshader_records":counts["original_total_subshader_records"],
        "original_total_pass_records":counts["original_total_pass_records"],
        "original_shaders_with_more_than_one_pass":counts["original_shaders_with_more_than_one_pass"],
        "original_shaders_with_no_passes":counts["original_shaders_with_no_passes"],
        "original_shader_pass_record_histogram":dict(sorted(pass_hist.items())),
        "original_shader_subshader_record_histogram":dict(sorted(subsh_hist.items())),
        "by_authenticated_original_owner":{k:dict(sorted(v.items())) for k,v in sorted(per_owner.items())},
        "selected_original_material_shader_edges_sha_authenticated":True,
        "original_parsed_pass_records_not_executable_programs":True,
        "real_same_export_shaderlab_pass_equivalence_verified":False,
        "android_device_pixels_or_game_ready_verified":False,
        "status":"SOURCE_10_SHADER_PASS_TOPOLOGY_VERIFIED"}


def run(original:Path):
    import UnityPy
    # Reuse prior exact original source graph and four SHA-pinned providers.
    edges,selected=t3.original_source(original)
    if len(edges)!=t3.MATERIAL_COUNT or len(selected)!=t3.SHADER_COUNT:
        raise ValueError("original_41_Materials_or_10_Shaders_missing")
    records={}
    for owner in t3.TARGET_OWNERS:
        path=original/"Raft_Data"/owner
        if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("original_Shader_source_modified")
        env=UnityPy.load(str(path))
        for obj in env.file.objects.values():
            key=(owner,obj.path_id)
            if key not in selected:continue
            if obj.type.name!="Shader" or key in records:
                raise ValueError("original_Shader_class_or_identity_changed")
            tree=obj.read_typetree()
            records[key]=tree.get("m_ParsedForm")
    if set(records)!=selected:raise ValueError("missing_typed_original_Shader_pass_records")
    return summarize(records)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("cannot_write_inside_private_original_source")
    try:out=run(a.original)
    except Exception as exc:
        out={"schema_version":1,
             "experiment":"T3-authentic-original-selected-10-Shader48-parsed-Pass-topology",
             "status":"INCONCLUSIVE","exception_type":type(exc).__name__,
             "real_same_export_shaderlab_pass_equivalence_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_ORIGINAL_SELECTED_SHADER_PASS_TOPOLOGY "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]=="SOURCE_10_SHADER_PASS_TOPOLOGY_VERIFIED" else 2
if __name__=="__main__":raise SystemExit(main())
