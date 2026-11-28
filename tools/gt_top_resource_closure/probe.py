"""Rank-one original renderer: exact mesh, material, TexEnv and texture closure.

A new export only rematerializes the private identities needed for this distinct
resource gate. No recovered shader is installed or rendered. Report only counts,
fixed classifications, and known field names; no original payloads or IDs.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import struct
import subprocess

from tools.gt_top_original_renderer import probe as previous
from tools.gt_shader_fanout import audit
from scripts import gt_verify_original_mesh_export as mesh
from scripts import gt_material_route_values as values
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import gt_particle108_local_texture_document as native_texture
from scripts import gt_zip2_payloads as zip2
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.w1_probe_original_shader_links import resolve_pointer

STATUS="GT_TOP_ORIGINAL_RENDERER_RESOURCE_CLOSURE_DIAGNOSTIC"
CAP=512*1024**2

class Blocked(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise Blocked(code)

def classify(exc):
    # Only our fixed codes may escape; arbitrary parser/OS/decoder text may
    # include an original object name or path.
    if isinstance(exc,Blocked):
        return str(exc)
    return type(exc).__name__

def select(a):
    queue,_=previous.priority.real_authenticated_queue(a.original,a.manifest,a.project,a.w1,a.b02)
    top=[v for v in queue if v["program_status"]=="dummy" and v["original_scene_renderer_material_slots"]==921]
    need(len(top)==1,"rank_one_source_identity")
    top=top[0]
    shader=top["original_owner"],top["original_shader_path_id"]
    sg=top["exported_Shader_GUID"]
    w,b,r=[json.loads(p.read_text()) for p in (a.w1,a.b02,a.renderer_trace)]
    need(w["schema_version"]==b["schema_version"]==r["schema_version"]==1
         and previous.GUID.fullmatch(w["export_instance"])
         and w["export_instance"]==b["export_instance"]==r["export_instance"],
         "different_export_instances")
    mt=previous.trace_map(w,{21,48})
    rr=previous.trace_map(r,{23,33,43})
    need(mt[(48,*shader)]==(4800000,sg,"3"),"shader_trace_pointer_drift")
    candidates,counts=previous.source_candidates(a.original,shader,mt,rr)
    need(len(candidates)==855 and counts["original_mesh_renderer_slots_to_top_shader"]==914
         and counts["original_single_slot_mesh_renderers"]==898,"prior_candidate_population_drift")
    wanted=defaultdict(set)
    for _,_,keys,_ in candidates:
        for guid,fid in keys:
            wanted[guid].add(fid)
    actual=previous.actual_docs(a.project,wanted)
    valid=[]
    for matkey,rkey,keys,source_mat in candidates:
        need(all(k in actual and actual[k][0]==cls for k,cls in zip(keys,(23,33,21,43))),
             "prior_native_graph_drift")
        rk,fk,mk,xk=keys
        previous.check_links(actual[rk][1],actual[fk][1],actual[mk][1],
                             rk[0],fk[0],mk,(sg,4800000),xk)
        need(previous.keywords(source_mat)==previous.keywords(actual[mk][1]),
             "prior_material_keyword_drift")
        valid.append((matkey,rkey,keys,source_mat))
    freq=Counter(v[0] for v in valid)
    selected=min(valid,key=lambda v:(-freq[v[0]],v[0],v[1]))
    need(freq[selected[0]]==118 and len(previous.keywords(selected[3]))==3,"prior_selected_material_population_drift")
    return selected,rr,previous.trace_map(b,{28}),sg

class Source:
    def __init__(self,a):
        self.a=a
        self.records=zip2.manifest(a.manifest.parent)
        self.cache={}
        self.extra=a.out.parent/"gt-top-private-streams"
        self.staged=set()
        self.total=0

    def file(self,owner):
        import UnityPy
        need(type(owner) is str and re.fullmatch(r"[A-Za-z0-9_.-]+",owner)
             and owner not in (".",".."),"invalid_source_owner")
        if owner not in self.cache:
            path=self.a.original/"Raft_Data"/owner
            rec=self.records.get("Raft_Data/"+owner)
            need(rec is not None and path.is_file(),"original_serialized_owner_outside_staging")
            need(zip2.fingerprint(path)==(rec[1],rec[2]),"source_owner_SHA_drift")
            self.cache[owner]=UnityPy.load(str(path)).file
        return self.cache[owner]

    def obj(self,key,cls):
        o=self.file(key[0]).objects.get(key[1])
        need(o is not None and o.type.name==cls,"wrong_original_object_class")
        return o

    def resolve(self,owner,ptr):
        return resolve_pointer(owner,[x.path for x in self.file(owner).externals],ptr)

    def stream(self,name):
        need(type(name) is str and re.fullmatch(r"[A-Za-z0-9_.-]+\.(?:resS|resource)",name),
             "invalid_source_stream_name")
        rel="Raft_Data/"+name
        rec=self.records.get(rel)
        need(rec is not None and rec[1]>0,"source_stream_not_pinned")
        dst=self.extra/"Raft"/"Raft_Data"
        if rel in self.staged:
            return dst
        need(self.total+rec[1]<=CAP,"selected_stream_budget_exceeded")
        # Only this exact manifest-selected provider, not an owner-wide resource
        # checkout. Both Git checkout and staged bytes remain pinned and private.
        pattern="/Raft/"+rel+("/*" if rec[0]=="split" else "")
        cp=subprocess.run(["git","-C",str(self.a.manifest.parent),"sparse-checkout","add","--no-cone","--",pattern],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240,check=False)
        need(cp.returncode==0,"exact_stream_sparse_checkout_failed")
        zip2.stage(self.a.manifest.parent,self.extra,[rel],byte_budget=CAP)
        self.staged.add(rel)
        self.total+=rec[1]
        return dst

def file_index(project,guids):
    paths,_=audit.registry.physical_entries(project/"Assets")
    found={}
    for p in paths:
        if p.suffix!=".meta":
            continue
        meta=audit.snapshot(p,4*1024*1024).decode("utf-8-sig").replace("\r\n","\n")
        g,folder=audit.registry.meta_identity(meta)
        if g not in guids:
            continue
        target=p.with_suffix("")
        need(not folder and target in paths and g not in found,"invalid_or_duplicate_export_meta")
        found[g]=(target,meta)
    return found

def document(path,fid,cls):
    raw=audit.snapshot(path,audit.MAX_FILE)
    need(raw.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"),"target_not_serialized_YAML")
    text=raw.decode("utf-8-sig").replace("\r\n","\n")
    heads=list(re.finditer(r"(?m)^---[^\n]*$",text))
    matches=[]
    seen=set()
    for i,h in enumerate(heads):
        m=audit.HEAD.fullmatch(h.group())
        need(m is not None,"invalid_actual_YAML_header")
        native,anchor=int(m[1]),audit.integer(m[2])
        need(anchor and anchor not in seen,"duplicate_or_zero_anchor")
        seen.add(anchor)
        if anchor==fid:
            need(native==cls and not m[3],"wrong_actual_native_class")
            matches.append(text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)])
    need(len(matches)==1,"actual_document_missing")
    return matches[0]

def uv_equal(a,b):
    return a is not None and b is not None and len(a)==len(b)==4 and all(
        struct.pack("<f",x)==struct.pack("<f",y) for x,y in zip(a,b))

def check_texture_slot(src,exp,material_owner,export_material_guid,resolve,trace):
    """Resolve the exact source slot; null is not a substitute for missing target."""
    source_ptr,source_uv=src
    export_ptr,export_uv=exp
    need(uv_equal(source_uv,export_uv),"texture_UV_transform_drift")
    fid,guid,kind=export_ptr
    fileid,pathid=source_ptr
    if not pathid:
        need(fileid==0 and fid==0 and guid=="0"*32 and kind==0,"null_texture_pointer_drift")
        return None
    source=resolve(material_owner,{"m_FileID":fileid,"m_PathID":pathid})
    need(source is not None and (28,*source) in trace,"texture_source_trace_unavailable")
    expected=trace[(28,*source)]
    ef,eg,et=expected
    if kind==0:
        need(guid=="0"*32 and fid!=0 and (fid,export_material_guid)==(ef,eg)
             and et in ("2","3"),"local_texture_pointer_drift")
    else:
        need((fid,guid,str(kind))==expected and kind in (2,3),"texture_pointer_drift")
    return source,(eg,ef),kind

def mesh_check(source,key,export_path,export_fid):
    tree=source.obj(key,"Mesh").read_typetree(check_read=False)
    name,_,size=mesh.source_stream_descriptor(tree["m_StreamData"])
    provider=source.stream(name) if size else source.a.original/"Raft_Data"
    before=mesh.source_geometry(tree,provider,source.records,set())
    after=mesh.export_geometry(export_path,export_fid)
    diff,zero=mesh.compare_geometry(before,after)
    return {"status":"MATCH" if not diff else "MISMATCH",
            "geometry_fields":len(before),"matched_geometry_fields":len(before)-len(diff),
            "different_geometry_fields":sorted(diff),"bind_pose_signed_zero_only":zero,
            "source_vertex_bytes":before["vertex_buffer"][0],"export_vertex_bytes":after["vertex_buffer"][0],
            "source_index_bytes":before["index_buffer"][0],"export_index_bytes":after["index_buffer"][0],
            "source_stream_used":bool(size),"source_vertex_count":before["vertex_count"],
            "source_submesh_count":len(before["submesh_ranges"])}

def texture_check(source,key,path,meta,fid,kind):
    tex=source.obj(key,"Texture2D").read()
    stream=getattr(tex,"m_StreamData",None)
    folder=source.a.original/"Raft_Data"
    if stream is not None and stream.size:
        n=Path(stream.path.replace("\\","/")).name
        folder=source.stream(n)
    payload,storage=pixels.exact_payload(tex,folder,source.a.manifest)
    before=pixels.decode_payload(tex,payload)
    if kind==3 and path.suffix.lower()==".png":
        need(fid==2800000 and len(re.findall(r"(?m)^TextureImporter:[ \t]*$",meta))==1,
             "texture_importer_identity_unproved")
        after=pixels.read_export_png(path)
        export_kind="png"
    elif kind in (0,2,3) and path.suffix.lower() in (".asset",".mat",".unity",".prefab"):
        after,_=native_texture.decode_export_body(document(path,fid,28))
        export_kind="native"
    else:
        raise Blocked("unsupported_export_texture_storage")
    result=pixels.compare_pixels(before,after)
    return {"status":"MATCH" if result["rgba8_samples_equal"] else "MISMATCH",
            "source_storage":storage,"export_storage":export_kind,
            "source_payload_bytes":len(payload),
            "pixel_coordinates_compared":result["pixel_coordinates_compared"],
            "alpha_mismatch_pixels":result["alpha_mismatch_pixels"],
            "rgb_mismatch_pixels":result["rgb_mismatch_pixels"],
            "dimensions_match":result["dimensions_match"]}

def run(a,report):
    selected,rr,tt,sg=select(a)
    matkey,rkey,keys,source_mat=selected
    rk,fk,mk,xk=keys
    report["selected_exact_graph_reproduced"]=True
    report["selected_material_eligible_source_renderers"]=118
    source=Source(a)
    # Resolve actual original sibling MeshFilter through the typed source trace,
    # not an inverse filename or a guessed export pathID.
    renderer=source.obj(rkey,"MeshRenderer").read_typetree(check_read=False)
    go=source.resolve(rkey[0],renderer["m_GameObject"])
    filters=[]
    for o in source.file(rkey[0]).objects.values():
        if o.type.name!="MeshFilter":
            continue
        t=o.read_typetree(check_read=False)
        if source.resolve(rkey[0],t["m_GameObject"])==go:
            filters.append((o.path_id,t))
    need(len(filters)==1 and previous.native_key(rr[(33,rkey[0],filters[0][0])])==fk,
         "original_meshfilter_identity_drift")
    srcmesh=source.resolve(rkey[0],filters[0][1]["m_Mesh"])
    need(srcmesh is not None and previous.native_key(rr[(43,*srcmesh)])==xk,"original_mesh_trace_drift")
    need(source.resolve(rkey[0],renderer["m_Materials"][0])==matkey,"original_material_edge_drift")
    source_mat=source.obj(matkey,"Material").read_typetree(check_read=False)
    index=file_index(a.project,{mk[0],xk[0],sg})
    need(set(index)=={mk[0],xk[0],sg},"selected_export_asset_missing")
    matpath,_=index[mk[0]]
    meshpath,_=index[xk[0]]
    report["phase"]="mesh_payload_and_material_values"
    try:
        report["mesh"]=mesh_check(source,srcmesh,meshpath,xk[1])
    except Exception as exc:
        report["mesh"]={"status":"UNPROVEN","reason":classify(exc)}
    mat=native_texture.strict_mapping(document(matpath,mk[1],21))
    need(set(mat)=={"Material"} and type(mat["Material"]) is dict,"actual_material_root")
    mat=mat["Material"]
    try:
        report["material_values"]={"status":"MATCH","counts":values.compare(source_mat,mat)}
    except values.Mismatch:
        report["material_values"]={"status":"MISMATCH"}
    except Exception as exc:
        report["material_values"]={"status":"UNPROVEN","reason":classify(exc)}
    report["phase"]="texture_pointer_and_top_mip"
    before=normalize_texenvs(source_mat["m_SavedProperties"]["m_TexEnvs"])
    after=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"],exported=True)
    report["texture_slots"]={"source":len(before),"export":len(after),
                             "missing":len(before.keys()-after.keys()),
                             "extra":len(after.keys()-before.keys())}
    rows=Counter()
    linked={}
    for name in sorted(before.keys()&after.keys()):
        try:
            target=check_texture_slot(before[name],after[name],matkey[0],mk[0],source.resolve,tt)
            if target is None:
                rows["null_slots_matched"]+=1
            else:
                key,exp,kind=target
                source.obj(key,"Texture2D")
                rows["nonnull_slots_with_exact_typed_trace_and_UV"]+=1
                old=linked.setdefault(key,(exp,kind))
                need(old==(exp,kind),"texture_target_pointer_inconsistency")
        except Exception as exc:
            rows["slot_"+classify(exc)]+=1
    report["texture_slots"]["counts"]=dict(rows)
    targets=file_index(a.project,{v[0][0] for v in linked.values()})
    observed=[]
    for key,(exp,kind) in sorted(linked.items()):
        try:
            need(exp[0] in targets,"traced_texture_asset_missing")
            path,meta=targets[exp[0]]
            observed.append(texture_check(source,key,path,meta,exp[1],kind))
        except Exception as exc:
            observed.append({"status":"UNPROVEN","reason":classify(exc)})
    report["texture_unique_targets"]=len(linked)
    # Anonymous result order only, with no source/export identifiers.
    report["texture_top_mip_results"]=observed
    report["texture_top_mip_status_counts"]=dict(Counter(v["status"] for v in observed))
    report["private_extra_source_stream_count"]=len(source.staged)
    report["private_extra_source_stream_bytes"]=source.total
    report["serialized_mesh_fields_match"]=report["mesh"]["status"]=="MATCH"
    report["serialized_material_values_match"]=report["material_values"]["status"]=="MATCH"
    report["all_saved_TexEnv_edges_and_UV_match"]=(
        set(before)==set(after) and rows["null_slots_matched"]+rows["nonnull_slots_with_exact_typed_trace_and_UV"]==len(before)
        and not any(k.startswith("slot_") for k in rows))
    report["all_linked_Texture2D_top_mips_match"]=bool(linked) and all(v["status"]=="MATCH" for v in observed)
    report["bounded_mesh_material_texture_top_mip_closure"]=(
        report["serialized_mesh_fields_match"] and report["serialized_material_values_match"]
        and report["all_saved_TexEnv_edges_and_UV_match"]
        and report["all_linked_Texture2D_top_mips_match"])
    report["status"]=STATUS
    report["phase"]="complete_resource_observation"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","project","w1","b02","renderer-trace","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    report={"status":"INCONCLUSIVE","phase":"select_prior_exact_native_graph",
            "full_mip_sampler_importer_or_shader_ABI_closure_verified":False,
            "unity_gpu_pixels_verified":False,"white_mesh_repair_verified":False,
            "production":False,"android_device":False,"XAPK":False}
    try:
        run(a,report)
    except Exception as exc:
        report["failure_category"]=classify(exc)
    with a.out.open("x") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    print("GT_TOP_ORIGINAL_RENDERER_RESOURCE_CLOSURE "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
