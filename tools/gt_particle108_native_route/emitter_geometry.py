"""Exact selected exported emitter documents -> isolated editor fixture and independent count gate."""
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from scripts import b05_verify_material_texenv_bindings as b05
from tools.gt_particle108_native_route import emitter_export as ee

STATUS="OBSERVED_ISOLATED_EXPORTED_PARTICLE108_GENERATED_GEOMETRY"
class Reject(ValueError):pass
def need(ok,code):
    if not ok:raise Reject(code)
def digest(b):return sha256(b).hexdigest()
def write_json(path,obj):
    with path.open("x") as f:json.dump(obj,f,sort_keys=True,allow_nan=False);f.write("\n")

def audit_refs(value,local,external):
    """Reject dangling local or unadmitted external pointers; never rewrite emitter docs."""
    if type(value) is dict:
        if "fileID" in value:
            need(not set(value)-{"fileID","guid","type"} and type(value["fileID"]) is int,"pointer_schema")
            fid=value["fileID"];g=value.get("guid",b05.ZERO_GUID)
            need(type(g) is str and re.fullmatch(r"[0-9a-fA-F]{32}",g) is not None,"pointer_guid")
            g=g.lower()
            if fid==0:need(g==b05.ZERO_GUID,"ambiguous_null_pointer")
            elif g==b05.ZERO_GUID:need(fid in local,"unresolved_local_emitter_dependency")
            else:need((fid,g) in external or g in b05.ENGINE,"unresolved_external_emitter_dependency")
        else:
            for v in value.values():audit_refs(v,local,external)
    elif type(value) is list:
        for v in value:audit_refs(v,local,external)

def scene_docs(path):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size<=256*1024*1024,"scene_file")
    s=path.read_text("utf-8-sig")
    hs=list(b05.ALL_HEADER.finditer(s));rows={}
    for i,h in enumerate(hs):
        m=b05.DOCUMENT_HEADER.fullmatch(h.group())
        need(m is not None,"scene_header_schema")
        fid=int(m.group(2));cl=int(m.group(1))
        need(fid not in rows,"duplicate_scene_document")
        raw=s[h.start():hs[i+1].start() if i+1<len(hs) else len(s)]
        rows[fid]=(cl,m.group(3),raw,s[h.end():hs[i+1].start() if i+1<len(hs) else len(s)])
    return rows

def vec(d,keys):
    need(type(d) is dict and set(d)==set(keys),"transform_vector")
    need(all(type(d[k]) in (int,float) and math.isfinite(d[k]) and abs(d[k])<1e12 for k in keys),"transform_nonfinite")
    return "{"+", ".join(k+": "+str(d[k]) for k in keys)+"}"
def fixture(go,tf,ps,r,tr,layer,transform,ps_raw,r_raw):
    need(len({go,tf,ps,r})==4 and all(type(x) is int and x>0 for x in (go,tf,ps,r)),"fixture_ids")
    p=vec(transform["m_LocalPosition"],("x","y","z"))
    q=vec(transform["m_LocalRotation"],("x","y","z","w"))
    scale=vec(transform["m_LocalScale"],("x","y","z"))
    need(type(layer) is int and 0<=layer<=31,"layer_schema")
    # Fixture GO/Transform authored only to isolate exact component payloads.
    # Original local TRS retained; original parent, unrelated components and play-state deliberately not claimed.
    s=f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{go}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {tf}}}
  - component: {{fileID: {ps}}}
  - component: {{fileID: {r}}}
  m_Layer: {layer}
  m_Name: GTIsolatedOriginalEmitter
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{tf}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go}}}
  m_LocalRotation: {q}
  m_LocalPosition: {p}
  m_LocalScale: {scale}
  m_Children: []
  m_Father: {{fileID: 0}}
  m_RootOrder: 0
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
"""
    need(ps_raw.startswith(f"--- !u!198 &{ps}") and r_raw.startswith(f"--- !u!199 &{r}"),"exact_component_header")
    return (s+ps_raw.rstrip("\n")+"\n"+r_raw.rstrip("\n")+"\n").encode()

def stage(a,private,ptrs,docs):
    from tools.gt_particle108_native_route import draw
    pr=a.geometry_private;project=a.geometry_project
    cfg=json.loads((pr/"expected.json").read_text())
    need(cfg==json.loads((project/"GTInput.json").read_text()) and cfg["run_id"]==a.run_id,"draw_stage_run_identity")
    need(len(cfg["assets"])==4 and len(cfg["vertex_requirements"])>0,"asset_signature_scope")
    paths=draw.locate(a.project,{p[1] for p in ptrs.values()})
    external={(x["file_id"],x["guid"]) for x in cfg["assets"]}
    cache={};rows=[]
    for i,(rk,x) in enumerate(sorted(private.items())):
        gk=(1,x["go_key"]);pk=(198,x["particle_key"]);rr=(199,rk)
        go,ps,r=docs[gk],docs[pk],docs[rr]
        gp,pp,rp=ptrs[gk],ptrs[pk],ptrs[rr];guid=gp[1]
        need(guid==pp[1]==rp[1],"component_cross_scene")
        if guid not in cache:cache[guid]=scene_docs(paths[guid])
        sd=cache[guid];gid,pid,rid=gp[0],pp[0],rp[0]
        comp=[ee.local_ref(v["component"],guid)[0] for v in go["m_Component"]]
        tf=[j for j in comp if j in sd and sd[j][0]==4 and not sd[j][1]]
        need(len(tf)==1,"fixture_transform_not_unique")
        tid=tf[0];transform=ee.read_doc(sd[tid][3])["Transform"]
        need(ee.local_ref(transform["m_GameObject"],guid)==gp[:2],"transform_owner")
        need(sd[pid][0]==198 and sd[rid][0]==199 and not sd[pid][1] and not sd[rid][1],"selected_raw_component")
        for body in (ps,r):audit_refs(body,{gid,tid,pid,rid},external)
        need(all(b05._export_pointer(v)[:2]==(2100000,cfg["material_guid"]) for v in r["m_Materials"]),"fixture_selected_material")
        data=fixture(gid,tid,pid,rid,None,go.get("m_Layer",0),transform,sd[pid][2],sd[rid][2])
        blob=f"emitter-{i}.scene.bytes"
        (pr/blob).write_bytes(data)
        rows.append(dict(index=i,path=f"Assets/GTEmitter/emitter-{i}.unity",blob=blob,sha=digest(data),
                         original_self_active=bool(go.get("m_IsActive")),streams=list(ee.stream_bytes(x["renderer"]["m_VertexStreams"])),
                         custom_streams=bool(x["renderer"].get("m_UseCustomVertexStreams")),material_count=len(r["m_Materials"])))
    need(len(rows)==12 and sum(x["material_count"] for x in rows)==24,"fixture_population")
    fixture_cfg=dict(run_id=a.run_id,scenes=rows,vertex_requirements=cfg["vertex_requirements"])
    write_json(pr/"emitter-input.json",fixture_cfg)
    (project/"GTEmitterInput.json").write_bytes((pr/"emitter-input.json").read_bytes())
    target=project/"Assets/Editor/ParticleDraw.cs"
    need(target.is_file(),"editor_fixture_anchor")
    target.write_bytes((Path(__file__).parent/"EmitterGeometry.cs").read_bytes())
    from tools.gt_particle108_native_route import emitter_vertex_lanes as vl
    (project/"Assets/GTEmitterLaneProbe.shader").write_text(vl.shader(cfg["vertex_requirements"]),encoding="utf-8")
    (project/"Assets/GTEmitterDrawMarker.shader").write_bytes((Path(__file__).parent/"EmitterDrawMarker.shader").read_bytes())
    return dict(fixtures=12,exact_component_documents=24,original_local_transform_retained=12,
                original_parent_hierarchy_retained=False,fixture_self_activated=True,dependency_pointers_admitted=True,
                source_signature_requirements=len(cfg["vertex_requirements"]),authored_quad_used=False)

def valid_bake(b):
    return (type(b) is dict and b.get("bake_completed") is True and b.get("particles")==b.get("particles_read")==b.get("positive_size_lifetime")==1
            and b.get("vertices")==4 and b.get("indices")==6 and b.get("finite") is True and b.get("nondegenerate") is True)
def valid_empty(b):
    return type(b) is dict and b.get("bake_completed") is True and b.get("particles")==b.get("particles_read")==b.get("vertices")==b.get("indices")==0

BAKE_COUNTS=("particles","particles_read","positive_size_lifetime","vertices","indices","submeshes","required_present","required_width")
BAKE_FLAGS=("finite","nondegenerate","bake_completed")
SAFE_EXCEPTIONS=("InvalidOperationException","ArgumentException","IOException","NullReferenceException","UnityException","IndexOutOfRangeException","")
def safe_bake(b):
    if type(b) is not dict:return None
    return {**{k:b[k] for k in BAKE_COUNTS if type(b.get(k)) is int and -1<=b[k]<=10000000},
            **{k:b.get(k) is True for k in BAKE_FLAGS},
            "failure_category":b.get("failure_category") if b.get("failure_category") in SAFE_EXCEPTIONS else "other"}

def calibration_observation(r):
    rows=r.get("calibration_cases")
    if type(rows) is not list or len(rows)>16:return dict(calibration_cases=[],calibration_cases_measured=0,independently_selected_method=-1)
    seen=set();safe=[];passed=set()
    for x in rows:
        need(type(x) is dict and type(x.get("material_kind")) is int and x["material_kind"] in (0,1) and type(x.get("method")) is int and 0<=x["method"]<=7,"calibration_case_schema")
        key=(x["material_kind"],x["method"])
        need(key not in seen,"duplicate_calibration_case");seen.add(key)
        zero=safe_bake(x.get("empty"));one=safe_bake(x.get("one"))
        ok=valid_empty(zero) and valid_bake(one)
        before=safe_bake(x.get("before_roundtrip"))
        preserved=x.get("roundtrip_state_equal") is True
        if key[1]==6:ok=ok and preserved and type(before) is dict and before.get("particles")==1 and before.get("particles_read")==1
        if ok:passed.add(key)
        safe.append(dict(material_kind=key[0],method=key[1],empty=zero,one=one,passed=ok,before_roundtrip=before,roundtrip_state_equal=preserved,
            failure_category=x.get("failure_category") if x.get("failure_category") in SAFE_EXCEPTIONS else "other"))
    selected=next((m for m in (0,1,2,3,5) if (0,m) in passed and (1,m) in passed),-1)
    return dict(calibration_cases=safe,calibration_cases_measured=len(safe),independently_selected_method=selected,
                manual_seed_control_passes=sum((k,4) in passed for k in (0,1)),
                emitted_state_roundtrip_control_passes=sum((k,6) in passed for k in (0,1)),
                natural_burst_control_passes=sum((k,7) in passed for k in (0,1)))

def summarize(cfg,r):
    need(r.get("run_id")==cfg["run_id"] and r.get("private_log_guard") is True,"receipt_run_identity")
    need(r.get("unity_version")=="2021.3.45f2" and r.get("backend")=="Vulkan","editor_environment")
    rows=r.get("rows")
    need(type(rows) is list and len(rows)==len(cfg["scenes"])==12 and {x.get("index") for x in rows}==set(range(12)),"editor_emitter_population")
    out=Counter()
    req=len(cfg["vertex_requirements"])
    for x in rows:
        out["imported_emitter_cases"]+=int(x.get("imported") is True)
        out["material_identity_cases"]+=int(x.get("materials_match") is True)
        out["billboard_cases"]+=int(x.get("billboard") is True)
        out["active_stream_cases"]+=int(x.get("active_streams_read") is True)
        out["exact_serialized_active_stream_cases"]+=int(x.get("streams_match") is True)
        out["custom_stream_cases"]+=int(cfg["scenes"][x["index"]]["custom_streams"])
        out["custom_stream_match_cases"]+=int(cfg["scenes"][x["index"]]["custom_streams"] and x.get("streams_match") is True)
        out["empty_cases"]+=int(x.get("empty_vertices")==0 and x.get("empty_particles")==0)
        out["spontaneous_simulation_nonempty_cases"]+=int(x.get("natural_particles",0)>0 and x.get("natural_vertices",0)>0)
        out["explicit_one_particle_billboard_cases"]+=int(valid_bake(x.get("forced")))
        out["direct_live_but_empty_cases"]+=int(type(x.get("forced")) is dict and x["forced"].get("particles")==1 and x["forced"].get("vertices")==0)
        out["roundtrip_exposed_state_equal_cases"]+=int(x.get("roundtrip_state_equal") is True)
        out["roundtrip_one_particle_billboard_cases"]+=int(x.get("roundtrip_state_equal") is True and valid_bake(x.get("roundtrip")))
        out["roundtrip_recovered_empty_direct_cases"]+=int(type(x.get("forced")) is dict and x["forced"].get("vertices")==0 and x.get("roundtrip_state_equal") is True and valid_bake(x.get("roundtrip")))
        b=x.get("forced") or {}
        out["signature_attribute_presence_cases"]+=int(b.get("required_present")==req)
        out["signature_attribute_width_cases"]+=int(b.get("required_width")==req)
        out["scene_bytes_unchanged_cases"]+=int(x.get("scene_bytes_unchanged") is True)
    return dict(out)

def row_observation(r):
    rows=r.get("rows")
    if type(rows) is not list or len(rows)>12:return []
    return [dict(index=x["index"],direct_method=x.get("direct_method") if x.get("direct_method") in (0,1,2,3,5) else -1,
                 direct=safe_bake(x.get("forced")),natural=safe_bake(x.get("natural")),roundtrip=safe_bake(x.get("roundtrip")),
                 roundtrip_state_equal=x.get("roundtrip_state_equal") is True,
                 imported=x.get("imported") is True,materials_match=x.get("materials_match") is True,
                 streams_match=x.get("streams_match") is True,
                 failure_category=x.get("failure_category") if x.get("failure_category") in SAFE_EXCEPTIONS else "other") for x in rows if type(x.get("index")) is int and 0<=x["index"]<12]

IMPORT_PHASES=("guard","asset_staging","asset_refresh","asset_identity","shader_load","material_texture_load","material_contract","material_identity","texture_descriptor_sampler","texture_refs_uv","numeric_properties","scene_staging","scene_refresh","calibration","vertex_lane_control","geometry","post_geometry_asset_contract","complete")
IMPORT_COUNTERS=("asset_identities","assets_written","scenes_written","scenes_imported","shader_errors","slots_declared","slots_matched","uv_matched","numeric_saved","numeric_declared","numeric_matched","numeric_undeclared")
IMPORT_FLAGS=("shader_supported","material_shader_match","native_identity","native_descriptor","native_sampler","resources_bytes_match","control_verified","source_assets_unchanged")

def import_observation(cfg,r):
    need(r.get("run_id")==cfg["run_id"] and r.get("private_log_guard") is True,"receipt_run_identity")
    need(r.get("unity_version")=="2021.3.45f2" and r.get("backend")=="Vulkan","editor_environment")
    return dict(editor_phase=r.get("phase") if r.get("phase") in IMPORT_PHASES else "other",
        editor_failure_category=r.get("failure_category") if r.get("failure_category") in ("InvalidOperationException","ArgumentException","IOException","NullReferenceException","UnityException") else "other",
        editor_row_count=len(r["rows"]) if type(r.get("rows")) is list and len(r["rows"])<=12 else 0,
        import_counters={k:r[k] for k in IMPORT_COUNTERS if type(r.get(k)) is int and -1<=r[k]<=10000},
        import_flags={k:r.get(k) is True for k in IMPORT_FLAGS})

def verify(a):
    out=dict(status="INCONCLUSIVE",phase="receipt",isolated_exported_emitter_generated_geometry_verified=False,
             original_emitter_geometry_verified=False,runtime_keyword_selection_verified=False,black_fire_restored=False,
             Android_device=False,production=False,XAPK=False,private_payload_published=False)
    try:
        cfg=json.loads((a.private/"emitter-input.json").read_text())
        need(cfg["run_id"]==a.run_id and cfg==json.loads((a.project/"GTEmitterInput.json").read_text()),"fixture_config_identity")
        need((a.private/"editor-output-private").read_text().strip()==a.run_id and (a.private/"editor.log").is_file(),"private_log_guard")
        r=json.loads((a.private/"geometry-receipt.json").read_text())
        out.update(import_observation(cfg,r))
        out.update(calibration_observation(r))
        out["row_observations"]=row_observation(r)
        # Retain the actual failing import predicate and partial counters even
        # when no emitter rows exist. Never replace it with a population error.
        out["editor_exit_code"]=a.exit_code
        if r.get("status")!="OBSERVED" or a.exit_code!=0:
            out["phase"]="editor_incomplete"
            raise Reject("editor_"+out["editor_phase"]+"_incomplete")
        out["counts"]=summarize(cfg,r)
        count=out["counts"]
        out["authored_empty_one_particle_control_verified"]=r.get("control_verified") is True
        out["source_assets_unchanged"]=r.get("source_assets_unchanged") is True
        out["source_asset_identity_count"]=r.get("asset_identities")
        out["roundtrip_diagnostic_only"]=True
        out["same_emitted_state_roundtrip_geometry_observed"]=(out["emitted_state_roundtrip_control_passes"]==2 and count.get("roundtrip_one_particle_billboard_cases",0)>0)
        need(a.exit_code==0 and r.get("status")=="OBSERVED" and out["authored_empty_one_particle_control_verified"],"ordinary_emission_control_unavailable")
        need(out["calibration_cases_measured"]==16 and out["independently_selected_method"] in (0,1,2,3,5) and out["independently_selected_method"]==r.get("selected_calibration_method"),"independent_calibration_method")
        need(out["source_assets_unchanged"] and out["source_asset_identity_count"]==4,"asset_identity")
        ic=out["import_counters"];fl=out["import_flags"]
        need(all(fl.get(k) is True for k in IMPORT_FLAGS) and ic.get("assets_written")==4 and ic.get("scenes_written")==ic.get("scenes_imported")==12 and ic.get("shader_errors")==0 and ic.get("slots_declared")==ic.get("slots_matched")==ic.get("uv_matched")==2 and ic.get("numeric_declared")==ic.get("numeric_matched")==11 and ic.get("numeric_saved")==ic.get("numeric_declared")+ic.get("numeric_undeclared"),"resource_contract")
        need(all(count.get(k)==12 for k in ("imported_emitter_cases","material_identity_cases","billboard_cases","active_stream_cases","empty_cases","explicit_one_particle_billboard_cases","scene_bytes_unchanged_cases")),"original_fixture_geometry_population")
        need(count.get("custom_stream_cases")==count.get("custom_stream_match_cases"),"custom_stream_runtime_mismatch")
        # Attribute width and spontaneous emission are intentionally separately measured, not inferred from a successful bake.
        out["isolated_exported_emitter_generated_geometry_verified"]=True
        out["phase"]="gpu_vertex_lane_readback"
        from tools.gt_particle108_native_route import emitter_vertex_lanes as vl
        out["vertex_lane_probe"]=vl.verify(a.private,cfg["vertex_requirements"],r.get("lane_control_completed") is True)
        need(out["vertex_lane_probe"]["gpu_vertex_lane_probe_verified"],"gpu_vertex_lane_probe_inconclusive")
        out["phase"]="actual_emitter_original_route_draw"
        from tools.gt_particle108_native_route import emitter_original_draw as ed
        out["actual_emitter_draw"]=ed.verify(a.private,out["row_observations"])
        need(out["actual_emitter_draw"]["isolated_actual_emitter_original_explicit_route_draw_verified"],"actual_emitter_draw_inconclusive")
        out.update(status="OBSERVED_ISOLATED_ACTUAL_EMITTER_ORIGINAL_EXPLICIT_ROUTE_DRAW",phase="complete")
    except Reject as e:out["failure_category"]=str(e)
    except Exception as e:out["failure_type"]=type(e).__name__
    write_json(a.safe,out)
    print("GT_PARTICLE108_EMITTER_GEOMETRY "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]=="OBSERVED_ISOLATED_ACTUAL_EMITTER_ORIGINAL_EXPLICIT_ROUTE_DRAW" else 2
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("project","private","safe"):p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,required=True)
    raise SystemExit(verify(p.parse_args()))
