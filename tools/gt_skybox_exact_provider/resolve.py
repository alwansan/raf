"""Resolve exactly the authenticated level24 Skybox material provider.
Catalog is metadata, not an instruction to fetch all listed assets. Only the
one name derived from the exact native external file slot is eligible.
"""
import argparse
import contextlib
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from tools.gt_ambient_same_export import audit as a
from scripts.w1_stage_zip2_owners import ZIP2_SHA, stage, fingerprint, safe
from tools.gt_remaining_scene_lighting.audit import hash_file,kind,tree
from tools.gt_light_same_export.audit import require,Rejected

CATALOG=Path(__file__).with_name("provider-catalog.json")
MAX_EXTRA=128*1024*1024
NAME=re.compile(r"(?:sharedassets(?:[0-9]|[1-3][0-9])|resources|globalgamemanagers)\.assets\Z")
HEX40=re.compile(r"[0-9a-f]{40}\Z")
HEX64=re.compile(r"[0-9a-f]{64}\Z")

def catalog():
    safe(CATALOG)
    data=json.loads(CATALOG.read_text())
    require(data["source_commit"]==ZIP2_SHA and data["manifest_blob"]==a.MANIFEST,"catalog_pin")
    rows=data["providers"]
    require(set(rows)=={"resources.assets","globalgamemanagers.assets",*(f"sharedassets{i}.assets" for i in range(40))},"catalog_population")
    for name,p in rows.items():
        require(NAME.fullmatch(name) and p["kind"] in ("plain","split") and type(p["bytes"]) is int and 0<p["bytes"]<=MAX_EXTRA and HEX40.fullmatch(p["git_object"]) and HEX64.fullmatch(p["sha256"]),"catalog_schema")
        if p["kind"]=="plain":require("parts" not in p,"unexpected_plain_parts")
        else:
            parts=p["parts"]
            require(2<=len(parts)<=4 and [x["name"] for x in parts]==[f"part-{i:05d}" for i in range(len(parts))] and sum(x["bytes"] for x in parts)==p["bytes"],"catalog_chunk_order")
            require(all(type(x["bytes"]) is int and 0<x["bytes"]<=80*1024**2 and HEX40.fullmatch(x["blob"]) for x in parts),"catalog_chunk_pin")
    return rows

def authenticate_manifest(source):
    safe(source)
    require(subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()==ZIP2_SHA,"source_commit")
    m=source/"RAFT_FILE_MANIFEST.tsv"
    hash_file(m,m.stat().st_size,a.MANIFEST)
    with m.open(newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        require(reader.fieldnames==["kind","bytes","sha256","mode","relative_path_under_Raft"],"manifest_schema")
        rows=list(reader)
    for name,p in catalog().items():
        h=[r for r in rows if r["relative_path_under_Raft"]=="Raft_Data/"+name]
        require(len(h)==1 and (h[0]["kind"],h[0]["bytes"],h[0]["sha256"])==(p["kind"],str(p["bytes"]),p["sha256"]),"catalog_manifest_drift")

def external_owner(env,data,rows):
    p=a.source_pointer(data.get("m_SkyboxMaterial"))
    require(p is not None and p[0]>0,"expected_unresolved_external_skybox")
    external=getattr(env.file,"externals",None)
    require(isinstance(external,(list,tuple)) and p[0]<=len(external),"source_external_slot_missing")
    raw=getattr(external[p[0]-1],"path",None)
    require(isinstance(raw,str) and 0<len(raw)<=4096 and not any(ord(c)<32 or ord(c)==127 for c in raw),"external_path_schema")
    name=raw.replace("\\","/").rsplit("/",1)[-1]
    require(NAME.fullmatch(name) and name in rows and name not in a.PINS,"external_provider_outside_exact_new_scope")
    return name,p[1]

def selection(root):
    with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
        env,i,d=a.read_source(root)
        name,private_id=external_owner(env,d,catalog())
    return name,private_id

def make_plan(source,root):
    authenticate_manifest(source)
    with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
        name,_=selection(root)
    p=catalog()[name]
    # All sparse patterns are generated from pre-reviewed metadata, never a raw source path.
    paths=["/Raft/Raft_Data/"+name] if p["kind"]=="plain" else ["/Raft/Raft_Data/"+name+"/"+x["name"] for x in p["parts"]]
    return {"source_commit":ZIP2_SHA,"manifest_blob":a.MANIFEST,"provider":name,"pin":p,"sparse_paths":paths}

def check_tree(source,rel,oid,typ):
    raw=subprocess.check_output(["git","-C",str(source),"ls-tree","HEAD","--",rel],text=True).rstrip("\n")
    header,sep,path=raw.partition("\t")
    modes={"040000"} if typ=="tree" else {"100644","100755"}
    fields=header.split()
    require(sep and path==rel and len(fields)==3 and fields[0] in modes and fields[1:]==[typ,oid],"pinned_tree_entry_mismatch")

def verify_payload(source,plan):
    p=plan["pin"];name=plan["provider"]
    rel="Raft/Raft_Data/"+name
    path=source/rel
    safe(path)
    check_tree(source,rel,p["git_object"],"blob" if p["kind"]=="plain" else "tree")
    if p["kind"]=="plain":
        require(hash_file(path,p["bytes"],p["git_object"])==p["sha256"],"selected_provider_digest")
    else:
        require(path.is_dir() and sorted(x.name for x in path.iterdir() if x.name!="README.txt")==[x["name"] for x in p["parts"]],"selected_chunk_population")
        for x in p["parts"]:
            check_tree(source,rel+"/"+x["name"],x["blob"],"blob")
            hash_file(path/x["name"],x["bytes"],x["blob"])

def stage_selected(source,root,dest,plan):
    require(make_plan(source,root)==plan,"plan_changed_since_resolution")
    verify_payload(source,plan)
    p=plan["pin"];name=plan["provider"]
    result=stage(source,dest,{"Raft_Data/"+name:(p["bytes"],p["sha256"])})
    require(result["verified_bytes"]==p["bytes"] and not result["lfs_used"],"selected_provider_stage")
    verify_typed(root,plan)
    return {"source_commit":ZIP2_SHA,"manifest_blob":a.MANIFEST,"selected_provider":name,"provider_kind":p["kind"],
            "provider_bytes":p["bytes"],"provider_sha256":p["sha256"],"provider_git_object":p["git_object"],
            "verified_chunk_count":len(p.get("parts",[])),"selected_additional_providers":1,
            "typed_material21_target":True,"full_scene_provider_closure_proven":False}

def verify_typed(root,plan):
    import UnityPy
    name,private_id=selection(root)
    require(plan["provider"]==name and plan["pin"]==catalog()[name],"selected_provider_identity")
    path=root/name
    safe(path)
    p=plan["pin"]
    require(path.is_file() and fingerprint(path)==(p["bytes"],p["sha256"]),"staged_extra_digest")
    with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
        env=UnityPy.load(str(path))
        table=env.file.objects
        require(private_id in table and kind(table[private_id])==("Material",21),"source_skybox_target_not_typed_material")
        require(tree(table[private_id]) is not None,"source_skybox_material_typetree_unavailable")

def compare_pointers(expected,actual,material_verified):
    if not material_verified:return {"status":"UNKNOWN","reason":"actual_material_document_unverified"}
    return {"status":"MATCH_TYPED_ACTUAL_MATERIAL" if expected==actual else "DRIFT_MATERIAL_POINTER",
            "typed_source_material":True,"same_export_trace_matched":True,
            "actual_material_document_verified":True}

def compare(x,root,plan):
    report={"source_commit":ZIP2_SHA,"scene_sha256":a.PINS[a.SCENE][1],"selected_provider":plan["provider"],
            "same_export_settings_identity_proven":False,"full_scene_provider_closure_proven":False,
            "Unity_import_verified":False,"device_pixels_proven":False,"original_assets_mutated":False,
            "original_assets_published":False,"XAPK":False}
    phase="source"
    try:
        verify_typed(root,plan)
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            env,i,d=a.read_source(root)
            owner,private_id=external_owner(env,d,catalog())
        phase="trace"
        st,w1,b02=[a.read_trace(p) for p in (x.trace,x.w1,x.b02)]
        guid,fid,_=a.settings_mapping(st,w1,b02,i)
        phase="actual_scene_yaml"
        scene=a.file_for_guid(x.project,guid,{".unity"})
        actual=a.doc_body(scene,104,fid,"RenderSettings")
        report["same_export_settings_identity_proven"]=True
        report["fields"]=a.field_report(d,actual)
        report["sun"]=a.null_sun(d,actual)
        phase="skybox_actual_material"
        try:
            expected=a.material_mapping(w1,owner,private_id)
            mat=a.file_for_guid(x.project,expected[0],{".mat",".asset"})
            a.doc_body(mat,21,expected[1],"Material")
            actual_pointer=a.export_pointer(actual.get("m_SkyboxMaterial"))
            report["skybox"]=compare_pointers(expected,actual_pointer,True)
        except Rejected as e:
            report["skybox"]={"status":"UNKNOWN","reason":str(e)}
        except Exception as e:
            report["skybox"]={"status":"UNKNOWN","reason":type(e).__name__}
        fields=report["fields"]
        statuses=[report["sun"]["status"],report["skybox"]["status"]]
        drift=bool(fields["field_mismatches"]) or any(s.startswith("DRIFT") for s in statuses)
        unknown=bool(fields["field_unknown"]) or "UNKNOWN" in statuses
        report["status"]="FAIL_ACTUAL_DRIFT" if drift else "PARTIAL_UNRESOLVED" if unknown else "PASS_EXACT_SKYBOX_SAME_EXPORT"
    except Exception as e:
        report.update(status="INCONCLUSIVE",phase=phase,reason=str(e) if isinstance(e,Rejected) else type(e).__name__)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_SAME_EXPORT "+json.dumps(report,sort_keys=True,separators=(",",":")))
    return 0 if report["status"]=="PASS_EXACT_SKYBOX_SAME_EXPORT" else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("discover","stage","compare"))
    for x in ("source","destination","plan","report","project","trace","w1","b02"):
        p.add_argument("--"+x,type=Path)
    x=p.parse_args()
    root=x.destination/"Raft_Data"
    try:
        if x.mode=="discover":
            a.auth(x.source,x.destination)
            plan=make_plan(x.source,root)
            with x.plan.open("x") as f:json.dump(plan,f)
            with open(os.environ["GITHUB_OUTPUT"],"a") as f:
                f.write("paths<<GT_SKYBOX_EXACT_PATHS\n/RAFT_FILE_MANIFEST.tsv\n"+"\n".join(plan["sparse_paths"])+"\nGT_SKYBOX_EXACT_PATHS\n")
            r={"status":"SELECTED_ONE_PROVIDER","provider":plan["provider"],"kind":plan["pin"]["kind"],"bytes":plan["pin"]["bytes"],"git_object":plan["pin"]["git_object"],"sha256":plan["pin"]["sha256"],"full_scene_provider_closure_proven":False}
        else:
            plan=json.loads(x.plan.read_text())
            if x.mode=="stage":
                r=stage_selected(x.source,root,x.destination,plan)
                r["status"]="AUTHENTICATED_TYPED_MATERIAL"
            else:
                return compare(x,root,plan)
    except Exception as e:
        # No raw exception text from UnityPy or source paths.
        r={"status":"INCONCLUSIVE","phase":x.mode,"reason":str(e) if isinstance(e,Rejected) else type(e).__name__}
    x.report.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_"+x.mode.upper()+" "+json.dumps(r,sort_keys=True))
    return 2 if r["status"]=="INCONCLUSIVE" else 0
if __name__=="__main__":raise SystemExit(main())
