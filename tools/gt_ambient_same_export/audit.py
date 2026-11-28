"""Actual source-authenticated RenderSettings104 -> same-export Unity scene.
Scope: selected scalar/color ambient/fog/reflection fields, null Sun and typed
Skybox Material21 reference when resolvable in six pinned original providers.
No raw scene objects, field values, identifiers or export files are published.
"""
import argparse
import contextlib
import json
import math
import os
from pathlib import Path
import re
from subprocess import check_output
from scripts.w1_stage_zip2_owners import stage,ZIP2_SHA
from scripts.b21_compare_export_lights import DOC,META_GUID,safe_root
from tools.gt_remaining_scene_lighting.audit import hash_file,int64,kind,tree
from tools.gt_light_same_export.audit import Rejected,require,pid,read_trace,vector,num,f,close

SCENE="level24"
MANIFEST="4201fda426d80caba36c275ceaddb440b05c5b4e"
PINS={
    "level24":(2803016,"6a06f3e95da765e89ded81c13837cd3de5844969c131ea02e59c38dbda22fc5d","a23575b75541b4045860e2e7d172fa6d836a2d7c"),
    "globalgamemanagers":(1914356,"6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5","ca92aec8af79dc1d315e5df4ccaafa4f6fe0898f"),
    "globalgamemanagers.assets":(758412,"b549af329d48244d80f28cb3cce6cd0b17769176081c249dc4646e1d62c58e28","4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9"),
    "sharedassets6.assets":(6607272,"0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632","abfd708f9bb5f5b7287ce4e1df524f816ed5d456"),
    "sharedassets24.assets":(7987136,"a28921562b0d64a0c5aeddfabd7a50c2695d9e9422725c19df9c786f8fdd6bdc","73c5f924b78cc0567eb8b8a707839930dc723841"),
    "sharedassets25.assets":(17611892,"b29ec028607fe74f9b0ac6fe55d0e565e26b29ac520bd80732c5a3bc851f7f67","20b830a4e809d94b53e2620f1de77b8d42731fa3"),
}
COLORS=("m_AmbientSkyColor","m_AmbientEquatorColor","m_AmbientGroundColor","m_SubtractiveShadowColor","m_FogColor")
NUMBERS=("m_AmbientIntensity","m_FogDensity","m_LinearFogStart","m_LinearFogEnd","m_ReflectionIntensity",
         "m_HaloStrength","m_FlareStrength","m_FlareFadeSpeed")
ENUMS={"m_AmbientMode":{0,1,3},"m_FogMode":{1,2,3},"m_DefaultReflectionMode":{0,1}}
INTS=("m_DefaultReflectionResolution","m_ReflectionBounces")
FIELDS=(*COLORS,*NUMBERS,*ENUMS,*INTS,"m_Fog")
GUID=re.compile(r"[0-9a-f]{32}\Z")
def scalar(field,value):
    if field in COLORS:return vector(value,("r","g","b","a"))
    if field in NUMBERS:return num(value)
    if field in ENUMS:
        require(type(value) is int and value in ENUMS[field],"enum_unrecognized")
        return value
    if field in INTS:
        require(type(value) is int and 0<=value<=65536,"integer_unrecognized")
        return value
    if field=="m_Fog":return f(value)
    raise Rejected("field_not_in_scope")

def field_report(source,actual):
    checked=[]; drift=[]; unknown={}
    for k in FIELDS:
        if k not in source:unknown[k]="source_field_missing";continue
        if k not in actual:unknown[k]="export_field_missing";continue
        try:a=scalar(k,source[k])
        except Rejected:unknown[k]="source_schema_unknown";continue
        try:b=scalar(k,actual[k])
        except Rejected:unknown[k]="export_schema_unknown";continue
        checked.append(k)
        if not close(a,b):drift.append(k)
    return {"fields_in_scope":len(FIELDS),"fields_checked":checked,"fields_equal":len(checked)-len(drift),
            "field_mismatches":drift,"field_unknown":unknown}

def auth(source,destination):
    require(check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()==ZIP2_SHA,"source_commit")
    manifest=source/"RAFT_FILE_MANIFEST.tsv"
    hash_file(manifest,manifest.stat().st_size,MANIFEST)
    for k,(size,sha,blob) in PINS.items():
        require(hash_file(source/"Raft/Raft_Data"/k,size,blob)==sha,"provider_digest")
    r=stage(source,destination,{"Raft_Data/"+k:v[:2] for k,v in PINS.items()})
    require(not r["lfs_used"] and len(r["owners"])==len(PINS),"source_stage")
    return {"source_commit":ZIP2_SHA,"manifest_blob":MANIFEST,"verified_files":len(PINS),
            "verified_bytes":r["verified_bytes"],"scene_sha256":PINS[SCENE][1]}

def read_source(root):
    import UnityPy
    for k,(size,sha,blob) in PINS.items():
        require(hash_file(root/k,size,blob)==sha,"staged_provider_digest")
    env=UnityPy.load(str(root/SCENE))
    objects=list(env.file.objects.values())
    rs=[o for o in objects if kind(o)==("RenderSettings",104)]
    require(len(rs)==1 and pid(rs[0].path_id),"source_render_settings_population")
    d=tree(rs[0]);require(d is not None,"source_render_settings_typetree")
    return env,rs[0].path_id,d

def source_pointer(raw):
    require(isinstance(raw,dict) and type(raw.get("m_FileID")) is int and int64(raw.get("m_PathID")),"source_pointer_schema")
    f,i=raw["m_FileID"],raw["m_PathID"]
    require(0<=f<(1<<31),"source_pointer_schema")
    if i==0:
        require(f==0,"source_null_external")
        return None
    return f,i

def export_pointer(raw):
    require(isinstance(raw,dict) and int64(raw.get("fileID")),"export_pointer_schema")
    fid=raw["fileID"]
    if fid==0:
        require(set(raw)=={"fileID"},"ambiguous_export_null")
        return None
    if set(raw)=={"fileID"}:return ("local",fid,0)
    require(set(raw)=={"fileID","guid","type"} and isinstance(raw["guid"],str) and GUID.fullmatch(raw["guid"].lower()) and raw["guid"]!="0"*32 and type(raw["type"]) is int and raw["type"] in (2,3),"export_pointer_schema")
    return raw["guid"].lower(),fid,raw["type"]

def trace_pointer(row):
    require(isinstance(row,dict) and set(row)=={"guid","file_id","type"},"trace_pointer_schema")
    p=export_pointer({"guid":row["guid"],"fileID":row["file_id"],"type":row["type"]})
    require(p is not None and p[0]!="local","trace_pointer_not_external")
    return p

def same_instance(settings,w1,b02):
    instance=settings.get("export_instance")
    require(isinstance(instance,str) and GUID.fullmatch(instance),"invalid_export_instance")
    for x in (settings,w1,b02):
        require(x.get("schema_version")==1 and x.get("export_instance")==instance and isinstance(x.get("objects"),list),"different_export_instance")
    require(any(isinstance(x,dict) and x.get("class_id") in (21,48) for x in w1["objects"]),"missing_w1_material_shader_graph")

def settings_mapping(settings,w1,b02,source_id):
    same_instance(settings,w1,b02)
    rows=settings["objects"]
    require(len(rows)==1,"settings_trace_population")
    r=rows[0]; require(r.get("class_id")==104 and r.get("source")=={"owner":SCENE,"path_id":source_id},"settings_trace_identity")
    require(settings.get("nonexportable_render_settings_skipped")==0,"settings_nonexportable")
    return trace_pointer(r.get("export"))

def material_mapping(w1,owner,i):
    rows=[r for r in w1["objects"] if r.get("class_id")==21 and r.get("source")=={"owner":owner,"path_id":i}]
    require(len(rows)==1,"skybox_material_trace_missing_or_duplicate")
    row=rows[0]
    require(row.get("exportable") is True,"skybox_material_nonexportable")
    p=trace_pointer(row.get("export"))
    other=[r for r in w1["objects"] if r.get("class_id")==21 and r.get("export")==row["export"]]
    require(len(other)==1,"skybox_material_trace_collapsed")
    return p

def file_for_guid(project,guid,extensions):
    hits=[]
    for meta in safe_root(project/"Assets").rglob("*.meta"):
        require(meta.is_file() and not meta.is_symlink() and meta.stat().st_size<=1024*1024,"unsafe_export_meta")
        gids=META_GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if guid in [x.lower() for x in gids]:
            require(len(gids)==1,"ambiguous_export_guid")
            hits.append(Path(str(meta)[:-5]))
    require(len(hits)==1,"missing_or_duplicate_actual_guid")
    path=hits[0]
    require(path.suffix in extensions and path.is_file() and not path.is_symlink() and path.stat().st_size<=128*1024*1024,"unexpected_export_document")
    return path

def doc_body(path,cid,fid,kind_name):
    import yaml
    class StrictLoader(yaml.SafeLoader):pass
    def mapping(loader,node):
        d={}
        for k,v in node.value:
            key=loader.construct_object(k,deep=True)
            require(key not in d,"duplicate_yaml_field")
            d[key]=loader.construct_object(v,deep=True)
        return d
    StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
    raw=path.read_text(encoding="utf-8-sig")
    require(raw.startswith("%YAML"),"not_yaml")
    hs=list(DOC.finditer(raw))
    ids=[int(h[2]) for h in hs]
    require(all(pid(i) for i in ids) and len(ids)==len(set(ids)),"bad_yaml_anchors")
    rows=[(n,h) for n,h in enumerate(hs) if int(h[2])==fid]
    require(len(rows)==1 and int(rows[0][1][1])==cid and "stripped" not in rows[0][1].group(0),"actual_native_document_missing_or_wrong_class")
    n,h=rows[0]
    end=hs[n+1].start() if n+1<len(hs) else len(raw)
    d=yaml.load(raw[h.end():end],Loader=StrictLoader)
    require(isinstance(d,dict) and set(d)=={kind_name} and isinstance(d[kind_name],dict),"actual_native_document_schema")
    return d[kind_name]

def skybox_binding(root,env,source,actual,w1):
    import UnityPy
    if "m_SkyboxMaterial" not in source or "m_SkyboxMaterial" not in actual:
        return {"status":"UNKNOWN","reason":"skybox_field_missing"}
    try:
        sp=source_pointer(source["m_SkyboxMaterial"])
        ap=export_pointer(actual["m_SkyboxMaterial"])
        if sp is None:return {"status":"MATCH_NULL" if ap is None else "DRIFT_NULL_TO_NON_NULL","typed_source_material":False}
        file_id,path_id=sp
        owner=SCENE
        if file_id:
            ex=getattr(env.file,"externals",None)
            require(isinstance(ex,(list,tuple)) and file_id<=len(ex),"source_external_slot_missing")
            name=getattr(ex[file_id-1],"path",None)
            require(isinstance(name,str) and bool(name),"source_external_name_unknown")
            owner=name.replace("\\","/").rsplit("/",1)[-1]
            require(owner in PINS,"source_skybox_provider_not_staged")
            loaded=UnityPy.load(str(root/owner))
            table=loaded.file.objects
        else:
            table=env.file.objects
        require(path_id in table and kind(table[path_id])==("Material",21),"source_skybox_target_not_typed_material")
        target=material_mapping(w1,owner,path_id)
        if ap!=target:return {"status":"DRIFT_MATERIAL_POINTER","typed_source_material":True,"same_export_trace_matched":True}
        return {"status":"MATCH_MATERIAL_TRACE","typed_source_material":True,"same_export_trace_matched":True,"target":target}
    except Rejected as e:
        return {"status":"UNKNOWN","reason":str(e)}
    except Exception as e:
        return {"status":"UNKNOWN","reason":type(e).__name__}

def null_sun(source,actual):
    try:
        sp=source_pointer(source.get("m_Sun"));ap=export_pointer(actual.get("m_Sun"))
        if sp is not None:return {"status":"UNKNOWN","reason":"source_sun_nonnull_outside_scope"}
        return {"status":"MATCH_NULL" if ap is None else "DRIFT_NULL_TO_NON_NULL"}
    except Rejected as e:return {"status":"UNKNOWN","reason":str(e)}

def run(a):
    report={"source_commit":ZIP2_SHA,"scene_sha256":PINS[SCENE][1],"same_export_settings_identity_proven":False,
            "Unity_import_verified":False,"original_assets_mutated":False,"original_assets_published":False,
            "device_pixels_proven":False,"XAPK":False}
    phase="source"
    try:
        root=a.source/"Raft_Data"
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            env,i,source=read_source(root)
        phase="trace"
        st,w1,b02=[read_trace(p) for p in (a.trace,a.w1,a.b02)]
        guid,fid,_=settings_mapping(st,w1,b02,i)
        phase="actual_yaml"
        scene=file_for_guid(a.project,guid,{".unity"})
        actual=doc_body(scene,104,fid,"RenderSettings")
        report["same_export_settings_identity_proven"]=True
        report["fields"]=field_report(source,actual)
        report["sun"]=null_sun(source,actual)
        phase="skybox"
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            sky=skybox_binding(root,env,source,actual,w1)
        target=sky.pop("target",None)
        if target:
            try:
                mat=file_for_guid(a.project,target[0],{".mat",".asset"})
                doc_body(mat,21,target[1],"Material")
                sky["status"]="MATCH_TYPED_ACTUAL_MATERIAL"
                sky["actual_material_document_verified"]=True
            except Rejected as e:
                sky.update(status="UNKNOWN",reason=str(e),actual_material_document_verified=False)
        report["skybox"]=sky
        statuses=[report["sun"]["status"],sky["status"]]
        drift=bool(report["fields"]["field_mismatches"]) or any(x.startswith("DRIFT") for x in statuses)
        unknown=bool(report["fields"]["field_unknown"]) or "UNKNOWN" in statuses
        report["status"]="FAIL_ACTUAL_DRIFT" if drift else "PARTIAL_UNRESOLVED" if unknown else "PASS_SELECTED_AMBIENT_SAME_EXPORT"
    except Rejected as e:report.update(status="INCONCLUSIVE",phase=phase,reason=str(e))
    except Exception as e:report.update(status="INCONCLUSIVE",phase=phase,reason=type(e).__name__)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_AMBIENT_SAME_EXPORT "+json.dumps(report,sort_keys=True,separators=(",",":")))
    return 0 if report["status"]=="PASS_SELECTED_AMBIENT_SAME_EXPORT" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("source","project","trace","w1","b02","output"):p.add_argument("--"+k,type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
