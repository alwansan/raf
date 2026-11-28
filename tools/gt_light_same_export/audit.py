"""Source-authenticated level38 Light chain to actual same-export native YAML.
Only safe aggregate counts and mismatch categories leave the private workspace.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import contextlib

from scripts.w1_stage_zip2_owners import stage, ZIP2_SHA
from scripts.b21_compare_export_lights import DOC, META_GUID, safe_root
from tools.gt_original_light_hierarchy.audit import Graph, local, kind, ref, flag, vec, qnorm, TRANSFORMS, Unresolved
from tools.gt_remaining_scene_lighting.audit import hash_file, int64

SCENE="level38"
MANIFEST="4201fda426d80caba36c275ceaddb440b05c5b4e"
PINS={
    "level38":(178892,"205515429d83c0e502987f6c917fadd56bf3e8d5af18f6b38e95059db54a2932","5f409291f6a819c738454111ba3b961be492453d"),
    "globalgamemanagers":(1914356,"6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5","ca92aec8af79dc1d315e5df4ccaafa4f6fe0898f"),
    "globalgamemanagers.assets":(758412,"b549af329d48244d80f28cb3cce6cd0b17769176081c249dc4646e1d62c58e28","4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9"),
    "sharedassets6.assets":(6607272,"0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632","abfd708f9bb5f5b7287ce4e1df524f816ed5d456"),
    "sharedassets38.assets":(4444508,"c9f6f9e5f2910ed830f7e4bd24a67729303cf878da4e2078f587c6568b596012","32a88441422fec1f031635d0d5f4dff335c7684e"),
    "sharedassets39.assets":(4309804,"218564a191697b42304780da2499b35aa923bebaf49cd4010c8e867dbcde793d","c6fa3f4f60274692390900a4b8a63493a3eee97e"),
}
GUID=re.compile(r"[0-9a-f]{32}\Z")
CLASSES={1:"GameObject",4:"Transform",108:"Light",224:"RectTransform"}
T={4,224}
XYZ=("x","y","z"); XYZW=(*XYZ,"w")
FIELDS={"m_LocalPosition":XYZ,"m_LocalRotation":XYZW,"m_LocalScale":XYZ}
LIGHT_NUM=("m_Intensity","m_Range")
class Rejected(ValueError): pass
def require(ok,reason):
    if not ok: raise Rejected(reason)
def pid(i):
    return int64(i) and i!=0
def f(v):
    val,s=flag(v)
    require(val is not None,"invalid_boolean")
    return val
def num(x):
    require(type(x) in (float,int) and math.isfinite(x),"invalid_numeric")
    return float(x)
def vector(x,keys):
    require(isinstance(x,dict) and set(keys)<=set(x),"vector_schema")
    return tuple(num(x[k]) for k in keys)
def enum(x):
    require(type(x) is int and 0<=x<=16,"light_type_schema")
    return x
def light(d):
    return {"m_Enabled":f(d.get("m_Enabled")),"m_Type":enum(d.get("m_Type")),
            "m_Color":vector(d.get("m_Color"),("r","g","b","a")),
            **{k:num(d.get(k)) for k in LIGHT_NUM}}
def source_model(objects):
    g=Graph(objects)
    lights=[i for i,o in g.table.items() if kind(o)==("Light",108)]
    require(len(lights)==1,"source_light_population")
    lid=lights[0]; ld=g.body(lid)
    owner=local(ld.get("m_GameObject"),g.table,{("GameObject",1)})
    require(lid in g.ids(owner),"source_light_reciprocity")
    t=g.transform_for(owner)
    chain=g.chain(t,owner)
    require(len(chain)==3,"source_chain_population")
    out={lid:{"class":108,"owner":owner,"fields":light(ld)}}
    chainids=[]; i=t
    while i is not None:
        chainids.append(i)
        go,active,s,parent,kids,d=g.node(i)
        require(active is True,"source_chain_inactive")
        ordered=[ref(k) for k in d["m_Children"]]
        require(set(ordered)==kids and len(ordered)==len(kids),"source_children_schema")
        trs={k:vector(d.get(k),keys) for k,keys in FIELDS.items()}
        qnorm(trs["m_LocalRotation"])
        out[go]={"class":1,"active":active,"components":[i]+([lid] if go==owner else [])}
        out[i]={"class":kind(g.table[i])[1],"owner":go,"parent":parent,"children":ordered,"trs":trs}
        i=parent
    require(out[lid]["fields"]["m_Enabled"],"source_light_disabled")
    # Full direct child lists of the three chain transforms, including siblings.
    # For adjacent non-chain children verify type and reciprocal parent, not their subtrees.
    for i in chainids:
        for child in out[i]["children"]:
            go,a,s,parent,kids,d=g.node(child)
            require(parent==i,"source_child_parent_not_reciprocal")
            if child not in out:
                out[child]={"class":kind(g.table[child])[1],"parent":parent}
    return out

def authenticate(source,destination):
    from subprocess import check_output
    require(check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()==ZIP2_SHA,"source_commit")
    manifest=source/"RAFT_FILE_MANIFEST.tsv"
    hash_file(manifest,manifest.stat().st_size,MANIFEST)
    for name,(size,sha,blob) in PINS.items():
        require(hash_file(source/"Raft/Raft_Data"/name,size,blob)==sha,"source_file_hash")
    staged=stage(source,destination,{"Raft_Data/"+k:v[:2] for k,v in PINS.items()})
    require(not staged["lfs_used"] and len(staged["owners"])==len(PINS),"source_stage")
    # All selected files exact. Scope does not assert complete scene dependencies.
    return {"source_commit":ZIP2_SHA,"manifest_blob":MANIFEST,"verified_files":len(PINS),
            "verified_bytes":staged["verified_bytes"],"scene_sha256":PINS[SCENE][1]}

def trace_map(model, trace, w1, b02):
    instance=trace.get("export_instance")
    require(isinstance(instance,str) and GUID.fullmatch(instance),"invalid_export_instance")
    for x in (trace,w1,b02):
        require(x.get("schema_version")==1 and x.get("export_instance")==instance and isinstance(x.get("objects"),list),"different_export_instance")
    require(any(isinstance(x,dict) and x.get("class_id") in (21,48) for x in w1["objects"]),"missing_w1_material_shader_trace")
    mapped={}; pointers={}
    for row in trace["objects"]:
        cid=row.get("class_id"); s=row.get("source"); p=row.get("export")
        require(type(cid) is int and cid in CLASSES and isinstance(s,dict) and s.get("owner")==SCENE and pid(s.get("path_id")),"invalid_trace_identity")
        i=s["path_id"]
        require(isinstance(p,dict),"invalid_trace_pointer")
        guid=p.get("guid"); fid=p.get("file_id")
        require(isinstance(guid,str) and GUID.fullmatch(guid.lower()) and guid!="0"*32 and pid(fid) and type(p.get("type")) is int and p["type"] in (2,3),"invalid_trace_pointer")
        target=(guid.lower(),fid)
        require(i not in mapped and target not in pointers,"duplicate_or_collapsed_trace")
        mapped[i]=(cid,target)
        pointers[target]=i
    require(set(model)<=set(mapped),"missing_selected_source_trace")
    result={}
    for i,row in model.items():
        cid,target=mapped[i]
        require(cid==row["class"],"trace_class_mismatch")
        result[i]=target
    require(len({k[0] for k in result.values()})==1,"selected_scene_guid_split")
    return result

def yaml_docs(project,guid,targets):
    import yaml
    class StrictLoader(yaml.SafeLoader): pass
    def mapping(loader,node):
        out={}
        for k,v in node.value:
            key=loader.construct_object(k,deep=True)
            require(key not in out,"duplicate_yaml_field")
            out[key]=loader.construct_object(v,deep=True)
        return out
    StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
    assets=safe_root(project/"Assets")
    hits=[]
    for meta in assets.rglob("*.meta"):
        require(not meta.is_symlink() and meta.is_file() and meta.stat().st_size<=1024*1024,"unsafe_export_meta")
        gids=META_GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if guid in [x.lower() for x in gids]:
            require(len(gids)==1,"ambiguous_export_meta")
            hits.append(Path(str(meta)[:-5]))
    require(len(hits)==1,"missing_or_duplicate_export_guid")
    path=hits[0]
    require(path.suffix==".unity" and path.is_file() and not path.is_symlink() and path.stat().st_size<=128*1024*1024,"selected_export_not_scene")
    raw=path.read_text(encoding="utf-8-sig")
    require(raw.startswith("%YAML"),"scene_not_yaml")
    headers=list(DOC.finditer(raw))
    ids=[int(h[2]) for h in headers]
    require(all(pid(i) for i in ids) and len(ids)==len(set(ids)),"duplicate_or_invalid_yaml_anchor")
    out={}
    for n,h in enumerate(headers):
        i=int(h[2])
        if i not in targets: continue
        cid=int(h[1])
        require(cid in CLASSES and "stripped" not in h.group(0),"wrong_or_stripped_yaml_document")
        end=headers[n+1].start() if n+1<len(headers) else len(raw)
        d=yaml.load(raw[h.end():end],Loader=StrictLoader)
        require(isinstance(d,dict) and set(d)=={CLASSES[cid]} and isinstance(d[CLASSES[cid]],dict),"actual_yaml_class")
        out[i]=(cid,d[CLASSES[cid]])
    require(set(out)==set(targets),"selected_export_yaml_document_missing")
    return out

def ptr(d,allow_null=False):
    require(isinstance(d,dict) and set(d)=={"fileID"} and int64(d["fileID"]),"actual_nonlocal_or_malformed_pointer")
    i=d["fileID"]
    if allow_null and i==0:return None
    require(pid(i),"actual_null_pointer")
    return i

def listptr(v,components=False):
    require(isinstance(v,list),"actual_pointer_list_schema")
    if components:
        require(all(isinstance(d,dict) and set(d)=={"component"} for d in v),"actual_component_schema")
        v=[d["component"] for d in v]
    out=[ptr(x) for x in v]
    require(len(set(out))==len(out),"actual_duplicate_pointer")
    return out

def close(a,b):
    if isinstance(a,tuple):return isinstance(b,tuple) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    if type(a) is bool or type(a) is int:return type(a) is type(b) and a==b
    return math.isclose(a,b,rel_tol=2e-6,abs_tol=2e-5)

def compare(model,mapping,docs):
    misses=Counter(); checked=Counter()
    def eq(name,ok):
        checked[name]+=1
        if not ok: misses[name]+=1
    def target(i):return None if i is None else mapping[i][1]
    for i,s in model.items():
        cid,d=docs[target(i)]
        eq("native_class",cid==s["class"])
        if cid!=s["class"]:continue
        if "owner" in s:
            eq("component_owner",ptr(d.get("m_GameObject"))==target(s["owner"]))
        if "active" in s:
            eq("gameobject_activeSelf",f(d.get("m_IsActive"))==s["active"])
            actual=listptr(d.get("m_Component"),True)
            for comp in s["components"]:
                eq("gameobject_component_membership",target(comp) in actual)
        if "parent" in s:
            eq("transform_parent",ptr(d.get("m_Father"),True)==target(s["parent"]))
        if "children" in s:
            eq("ordered_transform_children",listptr(d.get("m_Children"))==[target(j) for j in s["children"]])
        for k,v in s.get("trs",{}).items():
            actual=vector(d.get(k),FIELDS[k])
            eq(k,close(v,actual))
        if "fields" in s:
            actual=light(d)
            for k,v in s["fields"].items():eq("light_"+k,close(v,actual))
    return {"checks":dict(checked),"mismatches":dict(misses),"same_export_hierarchy_parity":not misses,
            "selected_source_objects":len(model),"mapped_objects":len(mapping),"selected_chain_transforms":sum("trs" in x for x in model.values()),
            "adjacent_child_transforms":sum(x["class"] in T and "trs" not in x for x in model.values()),
            "selected_source_lights":sum(x["class"]==108 for x in model.values()),
            "selected_source_gameobjects":sum(x["class"]==1 for x in model.values())}

def read_trace(path):
    require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=64*1024*1024,"private_trace_missing_or_oversize")
    return json.loads(path.read_text())

def run(a):
    import UnityPy
    result={"source_commit":ZIP2_SHA,"scene_sha256":PINS[SCENE][1],"source_export_mapping_proven":False,
            "Unity_import_verified":False,"Android_device":False,"XAPK":False,"raw_assets_published":False}
    phase="source"
    try:
        path=a.source/"Raft_Data"/SCENE
        size,sha,blob=PINS[SCENE]
        require(hash_file(path,size,blob)==sha,"staged_scene_hash")
        with open(os.devnull,"w") as quiet,contextlib.redirect_stdout(quiet),contextlib.redirect_stderr(quiet):
            env=UnityPy.load(str(path))
            model=source_model(list(env.file.objects.values()))
        phase="same_export_trace"
        m=trace_map(model,*[read_trace(p) for p in (a.trace,a.w1,a.b02)])
        result["private_trace_mapping_matched"]=True
        phase="actual_scene_yaml"
        docs=yaml_docs(a.project,next(iter(m.values()))[0],{k[1] for k in m.values()})
        phase="compare"
        result.update(compare(model,m,docs))
        result["source_export_mapping_proven"]=not result["mismatches"].get("native_class",0)
        result["status"]="PASS_SAME_EXPORT" if result["same_export_hierarchy_parity"] else "FAIL_FIELD_DRIFT"
    except Rejected as e:
        result.update(status="INCONCLUSIVE",phase=phase,reason=str(e))
    except Unresolved as e:
        result.update(status="INCONCLUSIVE",phase=phase,reason="source_graph_"+str(e))
    except Exception as e:
        result.update(status="INCONCLUSIVE",phase=phase,reason=type(e).__name__)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GT_LIGHT_SAME_EXPORT "+json.dumps(result,sort_keys=True,separators=(",",":")))
    return 0 if result["status"]=="PASS_SAME_EXPORT" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--trace",type=Path,required=True)
    p.add_argument("--w1",type=Path,required=True)
    p.add_argument("--b02",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
