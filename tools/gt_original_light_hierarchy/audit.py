#!/usr/bin/env python3
"""Bounded original Light -> GameObject -> Transform hierarchy, source only.
Numeric aggregate output; no original IDs, names, transforms or payloads emitted.
"""
import argparse
import contextlib
from collections import Counter
import json
import math
import os
from pathlib import Path
import tempfile

from tools.gt_remaining_scene_lighting.audit import (
    PIN, MAX_OBJECTS, AuditError, need, safe, load_pins, verified_scene, int64, kind, tree,
)

LEVELS = (24, 30, 38)
MAX_DEPTH = 256
MAX_COMPONENTS = 4096
MAX_CHILDREN = 100000
TRANSFORMS = {("Transform",4), ("RectTransform",224)}
EXPECTED = {24: {"lights":9,"enabled":3,"disabled":6,"sha256":"6a06f3e95da765e89ded81c13837cd3de5844969c131ea02e59c38dbda22fc5d","bytes":2803016}, 30: {"lights":107,"enabled":106,"disabled":1,"sha256":"53eb88c75c3a7d63333536e26b199dbfdcfd5ba8fb656ce843f24e45c3d9c94f","bytes":70435196}, 38: {"lights":1,"enabled":1,"disabled":0,"sha256":"205515429d83c0e502987f6c917fadd56bf3e8d5af18f6b38e95059db54a2932","bytes":178892}}

class Unresolved(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Unresolved(reason)

def flag(v):
    # UnityPy can return bool for a serialized bool and int for UInt8.
    # Do not coerce arbitrary strings, float, missing or nonbinary integers.
    if type(v) is bool:
        return v, "bool"
    if type(v) is int and v in (0,1):
        return v == 1, "int01"
    return None, "missing" if v is None else "other"

def ref(p, allow_null=False):
    require(isinstance(p,dict),"pointer_schema")
    f,i=p.get("m_FileID"),p.get("m_PathID")
    require(type(f) is int and 0<=f<(1<<31) and int64(i),"pointer_schema")
    require(f==0,"external_pointer")
    if allow_null and i==0:
        return None
    require(i!=0,"null_pointer")
    return i

def local(p, table, types, allow_null=False):
    i=ref(p,allow_null)
    if i is None:
        return None
    require(i in table,"local_target_missing")
    require(kind(table[i]) in types,"local_target_wrong_class")
    return i

def component_ids(go, table):
    arr=go.get("m_Component")
    require(isinstance(arr,list) and len(arr)<=MAX_COMPONENTS,"component_array_schema")
    out=[]
    for e in arr:
        require(isinstance(e,dict) and "component" in e,"component_entry_schema")
        i=ref(e["component"])
        require(i in table,"component_missing")
        out.append(i)
    require(len(out)==len(set(out)),"duplicate_component")
    return out

def vec(obj, keys):
    require(isinstance(obj,dict),"transform_vector_schema")
    vals=tuple(obj.get(k) for k in keys)
    require(all(type(v) in (int,float) and math.isfinite(v) and abs(v)<=1e20 for v in vals),"transform_nonfinite")
    return tuple(float(v) for v in vals)

def qnorm(q):
    n=math.sqrt(sum(v*v for v in q))
    require(.99<=n<=1.01,"nonunit_serialized_quaternion")
    return tuple(v/n for v in q)

def qmul(a,b):
    x,y,z,w=a; X,Y,Z,W=b
    return (w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)

def rotate(q,v):
    x,y,z,w=q
    a=qmul(qmul(q,(*v,0.)),(-x,-y,-z,w))
    return a[:3]

def rotation_chain(chain):
    # Root-to-leaf normalized local rotations. This is not an observation of
    # Unity's runtime transform, or a claim about scaled/sheared matrix axes.
    q=(0.,0.,0.,1.)
    for _,local_q,_,_ in reversed(chain):
        q=qnorm(qmul(q,local_q))
    f=rotate(q,(0.,0.,1.))
    require(abs(sum(x*x for x in f)-1)<1e-8,"forward_not_unit")
    return f

class Graph:
    def __init__(self,objects):
        need(len(objects)<=MAX_OBJECTS,"scene_object_budget")
        self.table={}
        self.cache={}
        self.components={}
        self.nodes={}
        for o in objects:
            i=getattr(o,"path_id",None)
            need(int64(i) and i!=0 and i not in self.table,"bad_or_duplicate_object_id")
            self.table[i]=o
    def body(self,i):
        if i not in self.cache:
            self.cache[i]=tree(self.table[i])
        d=self.cache[i]
        require(d is not None,"typetree_unknown")
        return d
    def ids(self,go):
        if go not in self.components:
            self.components[go]=component_ids(self.body(go),self.table)
        return self.components[go]
    def transform_for(self,go):
        t=[i for i in self.ids(go) if kind(self.table[i]) in TRANSFORMS]
        require(len(t)==1,"missing_or_ambiguous_transform")
        return t[0]
    def node(self,i):
        if i in self.nodes:
            return self.nodes[i]
        require(i in self.table and kind(self.table[i]) in TRANSFORMS,"transform_wrong_class")
        d=self.body(i)
        go=local(d.get("m_GameObject"),self.table,{("GameObject",1)})
        require(self.transform_for(go)==i,"transform_owner_component_mismatch")
        active,schema=flag(self.body(go).get("m_IsActive"))
        parent=local(d.get("m_Father"),self.table,TRANSFORMS,True)
        children=d.get("m_Children")
        require(isinstance(children,list) and len(children)<=MAX_CHILDREN,"children_schema")
        # Only validate the relevant parent-child edge when traversed, but
        # refuse duplicate entries and nonlocal targets in this array.
        kids=[local(x,self.table,TRANSFORMS) for x in children]
        require(len(kids)==len(set(kids)),"duplicate_child")
        self.nodes[i]=(go,active,schema,parent,set(kids),d)
        return self.nodes[i]
    def chain(self,start,owner):
        seen=set(); chain=[]; i=start; child=None
        while i is not None:
            require(i not in seen,"hierarchy_cycle")
            require(len(chain)<MAX_DEPTH,"hierarchy_depth_budget")
            seen.add(i)
            go,a,s,p,kids,d=self.node(i)
            if not chain:
                require(go==owner,"light_transform_owner_mismatch")
            if child is not None:
                require(child in kids,"parent_child_not_reciprocal")
            chain.append((a,s,d))
            child=i
            i=p
        return chain

def classify(objects):
    g=Graph(objects)
    c=Counter()
    depths=Counter()
    for i,o in g.table.items():
        if kind(o)!=("Light",108):
            continue
        c["light_headers"]+=1
        try:
            d=g.body(i)
            c["light_decoded"]+=1
            enabled,es=flag(d.get("m_Enabled"))
            c["light_enabled_schema_"+es]+=1
            c["light_enabled_"+("yes" if enabled is True else "no" if enabled is False else "unknown")]+=1
            owner=local(d.get("m_GameObject"),g.table,{("GameObject",1)})
            c["typed_local_light_owner"]+=1
            a,s=flag(g.body(owner).get("m_IsActive"))
            c["owner_active_schema_"+s]+=1
            c["owner_self_active_"+("yes" if a is True else "no" if a is False else "unknown")]+=1
            if s=="bool":
                c["prior_int_only_would_be_unknown"]+=1
            require(i in g.ids(owner),"light_owner_component_mismatch")
            c["reciprocal_light_owner_membership"]+=1
            t=g.transform_for(owner)
            c["owner_unique_transform"]+=1
            chain=g.chain(t,owner)
            c["complete_hierarchy"]+=1
            depths[str(len(chain)-1)]+=1
            for _,schema,_ in chain:
                c["hierarchy_node_active_schema_"+schema]+=1
            known=all(x[0] is not None for x in chain)
            if not known:
                c["hierarchy_activation_unknown"]+=1
            else:
                c["hierarchy_active_"+("yes" if all(x[0] for x in chain) else "no")]+=1
                if a is True and any(x[0] is False for x in chain[1:]):
                    c["self_active_but_ancestor_inactive"]+=1
                if enabled is not None:
                    c["serialized_light_and_hierarchy_"+("active" if enabled and all(x[0] for x in chain) else "inactive")]+=1
            try:
                trs=[]
                for aa,ss,td in chain:
                    q=qnorm(vec(td.get("m_LocalRotation"),("x","y","z","w")))
                    pos=vec(td.get("m_LocalPosition"),("x","y","z"))
                    scale=vec(td.get("m_LocalScale"),("x","y","z"))
                    trs.append((aa,q,pos,scale))
                f=rotation_chain(trs)
                c["finite_local_trs_and_composed_forward"]+=1
                if any(any(s<0 for s in v[3]) for v in trs):
                    c["negative_scale_on_chain"]+=1
                if any(any(s==0 for s in v[3]) for v in trs):
                    c["zero_scale_on_chain"]+=1
                if any(max(v[3])-min(v[3])>1e-6 for v in trs):
                    c["nonuniform_scale_on_chain"]+=1
                # Only counts, never emit original quaternion, position, name or forward.
                if all(abs(x-y)<1e-5 for x,y in zip(f,(0.,0.,1.))):
                    c["composed_forward_is_local_positive_z"]+=1
                else:
                    c["composed_forward_differs_from_positive_z"]+=1
            except Unresolved as exc:
                c["trs_unresolved_"+str(exc)]+=1
        except Unresolved as exc:
            c["unresolved_"+str(exc)]+=1
    return {"counts":dict(sorted(c.items())),"root_depth_histogram":dict(sorted(depths.items(),key=lambda kv:int(kv[0])))}

def run(source,pins,output):
    import UnityPy
    source=safe(source,True)
    rows={r["level"]:r for r in load_pins(pins,source)}
    out={"source_commit":PIN,"levels":{},"source_export_mapping_proven":False,
         "runtime_active_hierarchy_observed":False,"runtime_world_transform_observed":False,
         "device_pixels_proven":False,"original_assets_modified":False,
         "unitypy_version":getattr(UnityPy,"__version__","unknown")}
    with tempfile.TemporaryDirectory(prefix="gt-light-hierarchy-") as td,open(os.devnull,"w") as quiet:
        for n in LEVELS:
            r=rows[n];e=EXPECTED[n]
            need(r["sha256"]==e["sha256"] and r["bytes"]==e["bytes"],"historical_scene_pin_mismatch")
            item={"sha256":r["sha256"],"bytes":r["bytes"],"source_verified":False,"status":"UNKNOWN"}
            try:
                with verified_scene(source,r,Path(td)) as path:
                    item["source_verified"]=True
                    with contextlib.redirect_stdout(quiet),contextlib.redirect_stderr(quiet):
                        env=UnityPy.load(str(path))
                        item.update(classify(list(env.file.objects.values())))
                        del env
                c=item["counts"]
                need(c.get("light_headers",0)==e["lights"] and c.get("light_enabled_yes",0)==e["enabled"]
                    and c.get("light_enabled_no",0)==e["disabled"],"historical_light_population_mismatch")
                item["status"]="OBSERVED"
            except AuditError as exc:
                item["reason"]=str(exc)
            except Exception as exc:
                item["reason"]="reader_"+type(exc).__name__
            out["levels"][str(n)]=item
    observed=[v for v in out["levels"].values() if v["status"]=="OBSERVED"]
    total=Counter()
    for v in observed:total.update(v["counts"])
    out.update(observed_scenes=len(observed),source_verified_scenes=sum(x["source_verified"] for x in out["levels"].values()),aggregate_counts=dict(sorted(total.items())),
               status="OBSERVED_ALL_SELECTED" if len(observed)==len(LEVELS) else "PARTIAL_INCONCLUSIVE")
    output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("GT_ORIGINAL_LIGHT_HIERARCHY "+json.dumps(out,sort_keys=True,separators=(",",":")))
    return 0 if len(observed)==len(LEVELS) else 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--pins",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    raise SystemExit(run(a.source,a.pins,a.output))
