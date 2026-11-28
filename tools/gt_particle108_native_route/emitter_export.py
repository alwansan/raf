"""Same-instance original billboard emitter component export fidelity.
The private lineage and source documents never leave the disposable runner.
A matching serialized component is not a live particle simulation or a phone fix.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
from scripts import b05_verify_material_texenv_bindings as b05
from scripts.gt_particle108_local_texture_document import strict_mapping
from tools.gt_particle108_native_route import emitter
from tools.gt_particle108_native_mips import probe as native

STATUS="EXACT_PARTICLE108_BILLBOARD_EMITTER_SAME_EXPORT"
class Reject(ValueError):pass
def need(ok,code):
    if not ok:raise Reject(code)

def patch_helper(path):
    """Change only the private optional B21 capture filter, after SHA-pinned composition."""
    s=path.read_text()
    changes=(
        ('Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE")',
         'Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_EMITTER_LINEAGE")',1),
        ("CaptureLightObjects(","CaptureEmitterObjects(",2),
        ("asset.ClassID is not (1 or 108)","asset.ClassID is not (1 or 198 or 199)",1),
        ("if (asset.ClassID == 108) nonExportable++;","if (asset.ClassID is 198 or 199) nonExportable++;",1),
        ('"nonexportable_light_objects_skipped"','"nonexportable_emitter_components_skipped"',1),
    )
    for a,b,n in changes:
        need(s.count(a)==n,"private_helper_capture_anchor")
        s=s.replace(a,b)
    path.write_text(s)
    return {"private_optional_emitter_capture_classes":[1,198,199],"production_helper_changed":False}

def stream_bytes(v):
    if isinstance(v,(bytes,bytearray)):out=bytes(v)
    elif type(v) is list:
        need(all(type(i) is int and 0<=i<=255 for i in v),"invalid_stream_byte")
        out=bytes(v)
    elif type(v) is str:
        need(len(v)%2==0 and re.fullmatch(r"[0-9a-fA-F]*",v) is not None,"invalid_stream_hex")
        out=bytes.fromhex(v)
    else:raise Reject("unknown_stream_schema")
    need(len(out)<=256,"stream_budget")
    return out

def read_doc(body):
    # A digit-only hex blob must not become a YAML integer and lose leading zeros.
    body=re.sub(r"(?m)^(  m_VertexStreams: )([0-9a-fA-F]+)[ \t]*$",r'\1"\2"',body)
    return strict_mapping(body)

def scalar_equal(a,b):
    if type(a) is bool or type(b) is bool:
        return type(a) in (bool,int) and type(b) in (bool,int) and a in (0,1) and b in (0,1) and int(a)==int(b)
    if type(a) is int and type(b) is int:return a==b
    if type(a) in (float,int) and type(b) in (float,int):
        return math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-7)
    if type(a) is dict and type(b) is dict:
        return set(a)==set(b) and all(scalar_equal(a[k],b[k]) for k in a)
    return False

FIELDS=("m_RenderMode","m_RenderAlignment","m_UseCustomVertexStreams","m_Pivot","m_Flip",
        "m_MinParticleSize","m_MaxParticleSize","m_SortMode","m_SortingFudge","m_NormalDirection",
        "m_CameraVelocityScale","m_VelocityScale","m_LengthScale","m_AllowRoll",
        "m_FreeformStretching","m_RotateWithStretchDirection")
MODULES=("InitialModule","ShapeModule","EmissionModule","UVModule","RotationModule",
         "ColorModule","SizeModule","VelocityModule","TrailModule")
def flag(module):
    if type(module) is not dict:return None
    keys=[k for k in ("enabled","m_Enabled") if k in module]
    if len(keys)!=1:return None
    v=module[keys[0]]
    return int(v) if type(v) in (bool,int) and v in (0,1) else None

def compare_settings(src,dst,sp,dp):
    out=Counter()
    for f in FIELDS:
        if f not in src:continue
        out["renderer_fields_declared"]+=1
        if f in dst and scalar_equal(src[f],dst[f]):out["renderer_fields_matched"]+=1
        else:out["renderer_fields_mismatched"]+=1
    need(src.get("m_RenderMode")==0,"source_not_billboard")
    out["billboard_modes_matched"]=int(dst.get("m_RenderMode")==0)
    out["vertex_stream_bytes_matched"]=int("m_VertexStreams" in dst and
           stream_bytes(src["m_VertexStreams"])==stream_bytes(dst["m_VertexStreams"]))
    out["source_stream_bytes"]=len(stream_bytes(src["m_VertexStreams"]))
    for m in MODULES:
        sm=sp.get(m,sp.get("m_"+m));dm=dp.get(m,dp.get("m_"+m))
        if sm is None:continue
        a,b=flag(sm),flag(dm)
        if a is None:
            out["module_flags_source_unclassified"]+=1
            continue
        out["module_flags_declared"]+=1
        if a==b:out["module_flags_matched"]+=1
        else:out["module_flags_mismatched"]+=1
    return out

def trace_map(trace,required):
    out={}
    for r in trace["objects"]:
        cl=r.get("class_id")
        if cl not in required:continue
        key=b05._trace_source(r)
        if key not in required[cl]:continue
        idx=(cl,key)
        need(idx not in out,"duplicate_selected_lineage")
        p=b05._trace_export(r)
        need(p[0]>0 and p[1]!=b05.ZERO_GUID,"scene_lineage_missing_external_identity")
        out[idx]=p
    need(set(out)=={(cl,k) for cl,ks in required.items() for k in ks},"incomplete_selected_lineage")
    need(len({p[:2] for p in out.values()})==len(out),"lineage_pointer_collision")
    return out

def read_selected(project,ptrs):
    wants={(p[0],p[1]):cl for (cl,key),p in ptrs.items()}
    guids={p[1] for p in ptrs.values()};paths={}
    for m in (project/"Assets").rglob("*.meta"):
        need(not m.is_symlink() and m.stat().st_size<=4*1024*1024,"unsafe_meta")
        hits=b05.GUID.findall(m.read_text("utf-8-sig"))
        if len(hits)!=1 or hits[0].lower() not in guids:continue
        g=hits[0].lower();need(g not in paths,"duplicate_scene_meta")
        paths[g]=m.with_suffix("")
    need(set(paths)==guids,"missing_scene_meta")
    names={1:"GameObject",198:"ParticleSystem",199:"ParticleSystemRenderer"}
    docs={}
    for guid,path in paths.items():
        need(path.is_file() and not path.is_symlink() and path.stat().st_size<=256*1024*1024,"scene_document_guard")
        raw=path.read_text("utf-8-sig")
        headers=list(b05.ALL_HEADER.finditer(raw))
        for i,h in enumerate(headers):
            m=b05.DOCUMENT_HEADER.fullmatch(h.group())
            if not m:continue
            key=(int(m.group(2)),guid)
            if key not in wants:continue
            cl=wants[key];need(int(m.group(1))==cl and key not in docs and not m.group(3),"wrong_selected_document_class")
            d=read_doc(raw[h.end():headers[i+1].start() if i+1<len(headers) else len(raw)])
            need(set(d)=={names[cl]} and type(d[names[cl]]) is dict,"selected_document_body")
            docs[key]=d[names[cl]]
    need(set(docs)==set(wants),"missing_selected_scene_documents")
    return {k:docs[v[:2]] for k,v in ptrs.items()}

def local_ref(p,g):
    need(type(p) is dict and "fileID" in p and not set(p)-{"fileID","guid","type"},"export_component_pointer_schema")
    fid=p["fileID"];guid=p.get("guid",b05.ZERO_GUID)
    need(type(fid) is int and fid>0 and guid in (g,b05.ZERO_GUID),"export_component_not_local")
    return fid,g

def reciprocal(go,r,ps,go_ptr,r_ptr,ps_ptr):
    g=go_ptr[1]
    need(g==r_ptr[1]==ps_ptr[1],"export_components_cross_scene")
    members=go.get("m_Component")
    need(type(members) is list,"export_component_list")
    ids=[local_ref(x["component"],g) for x in members]
    need(len(ids)==len(set(ids)),"export_component_duplicate")
    return (r_ptr[:2] in ids and ps_ptr[:2] in ids and
            local_ref(r["m_GameObject"],g)==go_ptr[:2] and local_ref(ps["m_GameObject"],g)==go_ptr[:2])

def ordered_materials(source,export,mat_ptrs):
    need(type(export) is list,"export_material_list")
    expected=[(0,b05.ZERO_GUID,0) if k is None else mat_ptrs[(21,k)] for k in source]
    return expected==[b05._export_pointer(p) for p in export]

def run(a,out):
    out["phase"]="source_emitter_graph"
    private={}
    sr=emitter.census(a.original,a.manifest,private_rows=private)
    need(sr["status"]==emitter.STATUS and len(private)==12,"source_emitter_scope")
    out["source_emitters"]=len(private)
    out["phase"]="same_export_native_identity"
    nr=native.verify(a.original,a.manifest,a.project,a.w1,a.b02)
    need(nr["status"]==native.STATUS and nr["mip_levels_equal"]==7 and nr["mip_bytes_equal"]==21844
         and nr["material_texture_pptr_matches"]==nr["material_uv_matches"]==10,"native_same_export_identity")
    out["native_same_export_verified"]=True
    w1=json.loads(a.w1.read_text());et=json.loads(a.emitter.read_text())
    need(w1.get("schema_version")==et.get("schema_version")==1 and
         isinstance(w1.get("export_instance"),str) and w1["export_instance"]==et.get("export_instance"),"different_export_instances")
    out["phase"]="selected_component_documents"
    keys={1:{x["go_key"] for x in private.values()},198:{x["particle_key"] for x in private.values()},199:set(private)}
    need(all(len(k)==12 for k in keys.values()),"source_component_population")
    ptrs=trace_map(et,keys)
    mats=trace_map(w1,{21:{m for x in private.values() for m in x["materials"] if m is not None}})
    docs=read_selected(a.project,ptrs)
    out["component_documents"]=len(docs)
    out["phase"]="component_graph_and_billboard_settings"
    count=Counter()
    for rk,x in private.items():
        g=(1,x["go_key"]);p=(198,x["particle_key"]);r=(199,rk)
        go,ps,ren=docs[g],docs[p],docs[r]
        count["reciprocal_component_matches"]+=int(reciprocal(go,ren,ps,ptrs[g],ptrs[r],ptrs[p]))
        count["ordered_material_lists_matched"]+=int(ordered_materials(x["materials"],ren["m_Materials"],mats))
        count["material_slots_compared"]+=len(x["materials"])
        count.update(compare_settings(x["renderer"],ren,x["particle"],ps))
    out["counts"]=dict(count)
    need(count["reciprocal_component_matches"]==count["ordered_material_lists_matched"]==12,"emitter_reference_mismatch")
    need(count["material_slots_compared"]==24,"material_slot_coverage")
    need(count["billboard_modes_matched"]==count["vertex_stream_bytes_matched"]==12,"billboard_or_stream_mismatch")
    need(count["renderer_fields_declared"]>0 and count["renderer_fields_mismatched"]==0,"renderer_settings_mismatch")
    need(count["module_flags_declared"]>0 and count["module_flags_mismatched"]==0,"particle_module_flag_mismatch")
    if getattr(a,"geometry_project",None) is not None:
        from tools.gt_particle108_native_route import emitter_geometry
        out["phase"]="private_geometry_fixture_stage"
        out["geometry_stage"]=emitter_geometry.stage(a,private,ptrs,docs)
    out.update(status=STATUS,phase="complete",source_emitter_same_export_verified=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--patch-helper",type=Path)
    for k in ("original","manifest","project","w1","b02","emitter","out"):p.add_argument("--"+k,type=Path)
    p.add_argument("--geometry-project",type=Path)
    p.add_argument("--geometry-private",type=Path)
    p.add_argument("--run-id")
    a=p.parse_args()
    if any(x is not None for x in (a.geometry_project,a.geometry_private,a.run_id)) and not all(x is not None for x in (a.geometry_project,a.geometry_private,a.run_id)):
        p.error("all geometry arguments required together")
    if a.patch_helper:
        print(json.dumps(patch_helper(a.patch_helper)));return 0
    need(all(getattr(a,k) is not None for k in ("original","manifest","project","w1","b02","emitter","out")),"missing_arguments")
    need(not a.out.exists() and not a.out.resolve().is_relative_to(a.original.resolve()),"unsafe_output")
    out=dict(status="INCONCLUSIVE",source_emitter_same_export_verified=False,original_emitter_geometry_verified=False,
             runtime_keyword_selection_verified=False,black_fire_restored=False,Android_device=False,production=False,XAPK=False,private_payload_published=False)
    try:run(a,out)
    except Reject as e:out["failure_category"]=str(e)
    except Exception as e:out["failure_type"]=type(e).__name__
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GT_PARTICLE108_EMITTER_SAME_EXPORT "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STATUS else 2
if __name__=="__main__":raise SystemExit(main())
