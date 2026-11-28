"""Particle108 original explicit-route draw using exact exported Material and
both actual texture references. Authored quad is diagnostic, not original emitter.
Only aggregates leave the runner; no pixel or source data publication.
"""
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import numpy as np
from scripts import b05_verify_material_texenv_bindings as b05
from scripts import gt_material_route_values as values
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import gt_texture_route_payload as payload
from scripts.gt_original_921_all_variants import stage_parameter_records
from scripts.w1_recover_graphics_programs import translate
from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures
from scripts.t3_original_particle_shader_state import inspect_parsed
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.w1_depth_shaderlab import quoted,tags,render_state
from tools.gt_particle108_native_mips import probe as native
from tools.gt_top_resource_closure.selected_source_abi import combined_candidate
from tools.gt_particle108_native_route import probe as route
from scripts.gt_particle108_local_texture_document import strict_mapping

SIZES=(64,128)
BACKGROUNDS=2
CASES=("clear","dummy","renderer_native","native","repeat","source_block","clone","zero","one")
PROBE_CASES=("native","clone","zero","one")
PROBE_LEVELS=(0,3)
PROBE_MODES=("load","sample")
PROBE_SIZE=8
TOL=1/255
class DrawError(ValueError):pass
def need(ok,code):
    if not ok:raise DrawError(code)
def sha(data):return sha256(data).hexdigest()
def dump(path,obj):
    with path.open("x") as f:json.dump(obj,f,sort_keys=True,allow_nan=False)
def locate(project,guids):
    paths={}
    for meta in (project/"Assets").rglob("*.meta"):
        need(not meta.is_symlink() and meta.stat().st_size<=4*1024*1024,"draw_export_meta_guard")
        ids=b05.GUID.findall(meta.read_text("utf-8-sig"))
        if len(ids)==1 and ids[0].lower() in guids:
            g=ids[0].lower()
            need(g not in paths and meta.with_suffix("").is_file() and not meta.with_suffix("").is_symlink(),"draw_asset_identity")
            paths[g]=meta.with_suffix("")
    need(set(paths)==set(guids),"draw_asset_meta_coverage")
    return paths
def make_shader(parsed,table,links,private,out):
    pair={"subshader":0,"pass":0};dirs={}
    p=parsed["m_SubShaders"][0]["m_Passes"][0]
    passes=[{"subshader":0,"pass":0,"original_state":p["m_State"],
                 "original_name_indices":p["m_NameIndices"],"original_vertex_program":p["progVertex"],
                 "original_fragment_program":p["progFragment"]}]
    for stage,role,link in ((1,"vs",links[0]),(0,"fs",links[1])):
        dxbc,bucket,ordinal=link
        ident=(stage,sha(dxbc));folder=private/role;folder.mkdir()
        proof=translate(dxbc,stage,folder)
        need(proof["dxbc_sha256"]==ident[1] and all(proof[k] is True for k in
             ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),"draw_stage_translation")
        dirs[ident]=role
        pair[role]=dict(program_ref=ident,player_bucket=bucket,bucket_ordinal=ordinal)
    out["stage_ABI"]=stage_parameter_records([pair],[],passes,table,private,dirs)
    rows=json.loads((private/"original-private-parameter-records.json").read_text())["stage_records"]
    out["combined_candidate"]=combined_candidate(private,rows,pair,dirs)
    wrapper=(private/"combined-explicit-wrapper.txt").read_text()
    signature=read_original_dxbc_signatures(links[0][0])["input"]
    # The test mesh has authored position, normal, tangent, color and UV0..7.
    # Stop if another original semantic would have to be guessed.
    user=[r for r in signature if not r["system_value"]]
    need(all((r["semantic"].upper() in ("POSITION","NORMAL","TANGENT","COLOR") and r["index"]==0)
             or (r["semantic"].upper()=="TEXCOORD" and 0<=r["index"]<=7) for r in user),
         "draw_authored_vertex_semantic_unhandled")
    out["authored_vertex_semantics_supported"]=len(user)
    props,counts=serialize_properties(parsed)
    state=render_state(p["m_State"],allow_selective_color_mask=True)
    need("ColorMask RGB" in state,"draw_original_rgb_mask")
    sub=parsed["m_SubShaders"][0]
    shader="\n".join(["Shader "+quoted(parsed["m_Name"])+" {",props,"SubShader {",
        "LOD "+str(sub["m_LOD"]),tags(sub["m_Tags"]),"Pass {",state,wrapper,"}","}","Fallback Off","}",""])
    out["source_render_state"]=inspect_parsed(parsed)
    return shader.encode()
def stage(a,out,slots,targets,selected,parsed,table,pairs,switches,routes,uses,source_docs,exported,shader_ptr,mat_ptrs):
    out["draw_stage_phase"]="exact_selected_material_route"
    eligible=[key for key,entries in slots.items() if any((key[0],ptr[1])==selected and ptr[0]==0 for ptr,_ in entries.values())]
    need(len(eligible)==1,"draw_unique_native_material")
    key=eligible[0];mat=source_docs[key];dst=exported[key]
    route_id=route.choose_route(route.keywords(mat)[0]|route.keywords(mat)[1],switches,routes)
    need(route_id==route.choose_route(route.keywords(dst)[0],switches,routes),"draw_export_saved_route_mismatch")
    labels=[name for name,(ptr,uv) in slots[key].items() if ptr[0]==0 and (key[0],ptr[1])==selected]
    need(len(labels)==1 and uses[route_id][labels[0]]>0,"draw_sampled_native_slot")
    prop=labels[0]
    need(values.normalize(mat)==values.normalize(dst,exported=True),"draw_material_saved_numeric_drift")
    b02=json.loads(a.b02.read_text())
    texture_ptrs=route.traced(b02,28,set(targets))
    selected_ptr=texture_ptrs[selected];material_ptr=mat_ptrs[key]
    need(shader_ptr[0]==4800000 and shader_ptr[2]==3 and material_ptr[0]==2100000,"draw_shader_material_identity")
    target_keys={(key[0],ptr[1]) for ptr,_ in slots[key].values()}
    need(len(target_keys)==2 and selected in target_keys,"draw_two_texture_targets")
    guids={shader_ptr[1],material_ptr[1],*(texture_ptrs[k][1] for k in target_keys)}
    need(len(guids)==4,"draw_asset_guid_alias")
    paths=locate(a.project,guids)
    project=a.draw_project;private=a.draw_private
    need(not project.exists() and not private.exists() and a.run_id,"draw_fresh_project")
    private.mkdir(mode=0o700);project.mkdir()
    out["draw_stage_phase"]="selected_original_stage_ABI"
    route_cfg=None
    with tempfile.TemporaryDirectory(prefix="particle-stage-",dir=private) as td:
        if os.environ.get("GT_PARTICLE_KEYWORD_ROUTED")=="1":
            from tools.gt_particle108_native_route import emitter_keyword_candidate as kc
            shader,route_cfg=kc.stage(parsed,table,pairs,switches,routes,route_id,Path(td),project,out,make_shader)
        else:shader=make_shader(parsed,table,pairs[route_id],Path(td),out)
    assets=[]
    def add(ptr,raw=None):
        fid,g,kind=ptr;path=paths[g]
        rel="Assets/GTParticle/"+str(len(assets))+"/"+path.name
        data=path.read_bytes() if raw is None else raw
        meta=path.with_name(path.name+".meta").read_bytes()
        blob="asset-"+str(len(assets));(private/(blob+".bytes")).write_bytes(data);(private/(blob+".meta.bytes")).write_bytes(meta)
        assets.append(dict(path=rel,blob=blob,guid=g,file_id=fid,sha=sha(data),meta_sha=sha(meta)))
        return rel
    out["draw_stage_phase"]="private_asset_bundle"
    shader_path=add(shader_ptr,shader);material_path=add(material_ptr)
    need(paths[shader_ptr[1]].suffix==".shader" and paths[material_ptr[1]].suffix==".mat","draw_native_shader_material_extensions")
    tex_path=add(selected_ptr)
    body=native.actual_body(a.project,selected_ptr)
    raw=bytes.fromhex(body["_typelessdata"])
    need(len(raw)==21844,"draw_exact_native_mip_extent")
    (private/"native-rgba.bytes").write_bytes(raw)
    companion=next(iter(target_keys-{selected}));cp=texture_ptrs[companion]
    other=paths[cp[1]]
    # Preserve exact companion export and importer even if source RGB/alpha
    # differs; record parity independently and never infer it from GUID.
    companion_parity=False
    if other.suffix.lower()==".png" and cp[2]==3 and cp[0]==2800000:
        im,_=pixels.decode_original_texture(a.original,a.manifest,companion)
        parity=pixels.compare_pixels(im,pixels.read_export_png(other))
        companion_parity=parity["rgba8_samples_equal"]
        out["companion_source_export_pixel_observation"]={k:parity[k] for k in ("dimensions_match","rgba8_samples_equal","alpha_samples_equal","rgb_samples_equal","pixel_coordinates_compared")}
    elif cp[2]==2 and other.suffix in (".asset",".texture2D"):
        # Native companion can be imported as exact exported bytes; its
        # source-byte parity is deliberately not asserted by this lane.
        native.actual_body(a.project,cp)
        out["companion_native_source_byte_parity_verified"]=False
    else:raise DrawError("draw_companion_storage_unsupported")
    other_path=add(cp)
    dst_slots=b05.normalize_texenvs(dst["m_SavedProperties"]["m_TexEnvs"],exported=True)
    slot_rows=[]
    for name,(ptr,uv) in slots[key].items():
        expected=texture_ptrs[(key[0],ptr[1])]
        need(dst_slots[name][0]==expected and len(uv)==4,"draw_saved_texture_pointer")
        slot_rows.append(dict(name=name,guid=expected[1],file_id=expected[0],uv=list(uv)))
    normalized=values.normalize(mat)
    def f32(x):return struct.unpack("<f",struct.pack("<I",x))[0]
    numbers=[dict(name=n,kind="float",value=[f32(v)]) for n,v in normalized["m_Floats"].items()]
    numbers.extend(dict(name=n,kind="color",value=[f32(x) for x in v]) for n,v in normalized["m_Colors"].items())
    need(not normalized["m_Ints"],"draw_int_upload_schema")
    sampler=body["m_TextureSettings"]
    cfg=dict(run_id=a.run_id,assets=assets,shader_path=shader_path,material_path=material_path,texture_path=tex_path,
             shader_guid=shader_ptr[1],material_guid=material_ptr[1],texture_guid=selected_ptr[1],texture_id=selected_ptr[0],
             selected_property=prop,slots=slot_rows,numbers=numbers,raw_sha=sha(raw),
             sampler=[sampler[k] for k in ("m_FilterMode","m_Aniso","m_WrapU","m_WrapV","m_WrapW")],
             bias=sampler["m_MipBias"],companion_source_export_rgba_match=companion_parity,
             sizes=list(SIZES),backgrounds=BACKGROUNDS,probe_size=PROBE_SIZE,probe_levels=list(PROBE_LEVELS))
    if route_cfg is not None:cfg["route_candidate"]=route_cfg
    # Private selected VS semantic masks are needed for the separate emitter geometry lane.
    cfg["vertex_requirements"]=[dict(semantic=x["semantic"],index=x["index"],mask=x["mask"],used_mask=x["used_mask"],component_type=x["type"])
         for x in read_original_dxbc_signatures(pairs[route_id][0][0])["input"] if not x["system_value"]]
    here=Path(__file__).parent
    files={"Assets/Editor/ParticleDraw.cs":(here/"ParticleDraw.cs").read_bytes(),
           "Assets/GTParticleControl.shader":(here/"ParticleControl.shader").read_bytes(),
           "Assets/GTParticleCloneProbe.shader":(here/"ParticleCloneProbe.shader").read_bytes(),
           "Packages/manifest.json":b'{"dependencies":{}}\n',
           "ProjectSettings/ProjectVersion.txt":b"m_EditorVersion: 2021.3.45f2\n",
           "ProjectSettings/ProjectSettings.asset":b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTValidation\n  productName: GTParticleDraw\n  m_ActiveColorSpace: 1\n"}
    for path,data in files.items():
        dst_path=project/path;dst_path.parent.mkdir(parents=True,exist_ok=True);dst_path.write_bytes(data)
    dump(private/"expected.json",cfg);(project/"GTInput.json").write_bytes((private/"expected.json").read_bytes())
    out["draw_stage"]={"selected_original_explicit_route":route_cfg is None,"original_keyword_routed_candidate":route_cfg is not None,"source_material_numeric_parity":True,
                       "actual_export_asset_identities":4,"same_export_texture_slots":2,
                       "source_native_bytes":21844,"source_native_mips":7,
                       "companion_source_export_rgba_match":companion_parity,
                       "original_emitter_geometry_verified":False,"private_payload_guarded":True}
def read_pixels(path,size):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size==size*size*16,"draw_pixel_extent")
    v=np.fromfile(path,dtype="<f4").reshape(size,size,4)
    need(np.isfinite(v).all(),"draw_nonfinite_pixels")
    return v
def diff(a,b,*,rgb=False):
    need(a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all(),"draw_pixel_schema")
    if rgb:a,b=a[...,:3],b[...,:3]
    d=np.max(np.abs(a-b),axis=-1)
    return dict(over_tolerance=int(np.count_nonzero(d>TOL)),exactly_different=int(np.count_nonzero(d>0)),max_error=float(d.max()))
def summarize(rows):
    need(set(rows)==set(CASES),"draw_readback_cases")
    need(len({v.shape for v in rows.values()})==1 and all(np.isfinite(v).all() for v in rows.values()),"draw_readback_schema")
    def d(a,b):return diff(rows[a],rows[b],rgb=True)["over_tolerance"]
    marker=np.array([.91,.07,.61,1],dtype=np.float32)
    mask=np.max(np.abs(rows["dummy"]-marker),axis=-1)<=TOL
    return dict(dummy_visible=d("dummy","clear"),dummy_marker_pixels=int(mask.sum()),
                renderer_native_visible=d("renderer_native","clear"),native_visible=d("native","clear"),
                renderer_vs_command=d("renderer_native","native"),native_vs_dummy=d("native","dummy"),
                native_vs_repeat=d("native","repeat"),native_vs_source_block=d("native","source_block"),
                native_vs_exact_clone=d("native","clone"),zero_vs_one=d("zero","one"),
                native_vs_zero=d("native","zero"),native_vs_one=d("native","one"),
                zero_vs_clear=d("zero","clear"),one_vs_clear=d("one","clear"),
                source_alpha_channel_mask_preserved=all(np.max(np.abs(rows[x][...,3]-rows["clear"][...,3]))<=TOL for x in ("renderer_native","native","repeat","source_block","clone","zero","one")))
def summarize_probe(rows):
    need(set(rows)==set(PROBE_CASES),"clone_probe_cases")
    need(len({v.shape for v in rows.values()})==1 and all(np.isfinite(v).all() for v in rows.values()),"clone_probe_schema")
    exact=rows["clone"];zero=rows["zero"];one=rows["one"]
    return dict(native_vs_clone=diff(rows["native"],exact),
                zero_rgb_vs_clone=diff(zero,exact,rgb=True),
                one_rgb_vs_clone=diff(one,exact,rgb=True),
                zero_alpha_max_error=float(np.max(np.abs(zero[...,3]))),
                one_alpha_max_error=float(np.max(np.abs(one[...,3]-1))),
                clone_alpha_distinguished_from_controls=int(np.count_nonzero((exact[...,3]>TOL)&(exact[...,3]<1-TOL))))
def probe_pass(row):
    return (all(row[k]["over_tolerance"]==0 for k in ("native_vs_clone","zero_rgb_vs_clone","one_rgb_vs_clone"))
            and row["zero_alpha_max_error"]<=TOL and row["one_alpha_max_error"]<=TOL)
def alpha_effect_without_dummy(row):
    # Independent observation, not acceptance of the strict full draw gate.
    return (row["native_visible"]>0 and row["native_vs_repeat"]==0 and
            row["native_vs_source_block"]==0 and row["native_vs_exact_clone"]==0 and
            row["renderer_vs_command"]==0 and row["zero_vs_one"]>0 and
            row["source_alpha_channel_mask_preserved"])
def dummy_marker(pixels):
    marker=np.array([.91,.07,.61,1],dtype=np.float32)
    return int(np.count_nonzero(np.max(np.abs(pixels-marker),axis=-1)<=TOL))
def classify_draw(row):
    if not (row["dummy_marker_pixels"]>0 and row["dummy_visible"]>0 and row["native_visible"]>0 and
            row["native_vs_dummy"]>0 and row["native_vs_repeat"]==0 and row["source_alpha_channel_mask_preserved"]):
        return ("DUMMY_CAMERA_EVENT_UNCALIBRATED" if row.get("dummy_direct_marker_pixels",0)>0
                and row["dummy_marker_pixels"]==0 else "COMMAND_DRAW_CONTROL_UNCALIBRATED")
    if row["native_vs_source_block"]!=0:
        return "SAME_NATIVE_TEXTURE_PROPERTY_BLOCK_CHANGED_DRAW"
    if row["native_vs_exact_clone"]!=0:
        return "EXACT_GPU_CLONE_OVERRIDE_CHANGED_DRAW"
    if row["zero_vs_one"]==0:
        return "ALPHA_OVERRIDE_NOT_OBSERVED_IN_FINAL_DRAW"
    if row["renderer_vs_command"]!=0:
        return "ISOLATED_COMMAND_ALPHA_EFFECT_RENDERER_BASELINE_DIFFERS"
    return "CALIBRATED_SOURCE_ROUTE_ALPHA_EFFECT"
def verify(a):
    out=dict(status="INCONCLUSIVE",phase="editor_receipt",original_shader_draw_verified=False,
             isolated_explicit_route_alpha_effect_observed=False,black_fire_restored=False,
             Android_device=False,production=False,XAPK=False,original_emitter_geometry_verified=False,
             runtime_keyword_selection_verified=False,private_payload_published=False,
             clone_gpu_probe_verified=False,command_material_property_block_verified=False,
             independent_alpha_effect_without_dummy_cases=0,dummy_scene_lifetime_verified=False)
    try:
        cfg=json.loads((a.private/"expected.json").read_text())
        need(cfg["run_id"]==a.run_id and cfg==json.loads((a.project/"GTInput.json").read_text()),"draw_run_identity")
        need((a.private/"editor-output-private").read_text().strip()==a.run_id and (a.private/"editor.log").is_file(),"draw_private_log_guard")
        r=json.loads((a.private/"draw-receipt.json").read_text())
        need(r["run_id"]==a.run_id and r["private_log_guard"] is True,"draw_editor_identity")
        out["editor_phase"]=r.get("phase") if r.get("phase") in ("environment","guard","import","materials","scene_lifetime_calibration","controls","clone_gpu_probe","draw","complete") else "unknown"
        out["editor_failure_category"]=r.get("failure_category") if r.get("failure_category") in ("InvalidOperationException","ArgumentException","IOException","NullReferenceException","UnityException") else "other"
        flags=("shader_identity","material_identity","material_shader_identity","native_identity","native_descriptor","native_sampler",
               "texture_refs","uv_matches","numbers_match","clone_sampler_match","clone_payload_verified",
               "clone_graphics_format_match","source_material_unchanged_after_draw","override_blocks_verified",
               "prescene_dummy_alive","actual_dummy_alive_after_scene")
        out.update({k:r.get(k) is True for k in flags})
        out["postscene_dummy_alive"]=r.get("postscene_dummy_alive") is True
        out["postscene_dummy_managed_reference_present"]=r.get("postscene_dummy_managed_reference_present") is True
        out["dummy_scene_lifetime_verified"]=(out["prescene_dummy_alive"] and out["postscene_dummy_managed_reference_present"] and out["actual_dummy_alive_after_scene"])
        out["prescene_material_destroyed_by_scene_transition"]=(out["dummy_scene_lifetime_verified"] and not out["postscene_dummy_alive"])
        for k in ("asset_identities","asset_bytes_unchanged","meta_bytes_unchanged","shader_errors","numbers_declared","numbers_matched","draw_cases","probe_draw_cases","dummy_shader_errors","probe_shader_errors",
                  "dummy_camera_submissions","dummy_direct_submissions","explicit_command_submissions"):
            if type(r.get(k)) is int:out[k]=r[k]
        out["companion_source_export_rgba_match"]=cfg["companion_source_export_rgba_match"]
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear","draw_environment")
        need(a.exit_code==0 and r["status"]=="OBSERVED","draw_editor_incomplete")
        need(all(out[k] for k in flags) and out["asset_identities"]==out["asset_bytes_unchanged"]==out["meta_bytes_unchanged"]==4 and out["shader_errors"]==out["dummy_shader_errors"]==out["probe_shader_errors"]==0,"draw_identity_gate")
        need(out["dummy_scene_lifetime_verified"] and out["dummy_camera_submissions"]==4 and
             out["dummy_direct_submissions"]==4 and out["explicit_command_submissions"]==28 and
             out["draw_cases"]==36 and out["probe_draw_cases"]==17,"draw_submission_population")
        out["phase"]="independent_clone_gpu_probe"
        marker=read_pixels(a.private/"probe-marker.f32",PROBE_SIZE)
        out["probe_marker_pixels"]=int(np.count_nonzero(np.max(np.abs(marker-np.array([.125,.375,.625,1.])),axis=-1)<=TOL))
        probes=[]
        for level in PROBE_LEVELS:
            for mode in PROBE_MODES:
                rows={case:read_pixels(a.private/f"probe-{level}-{mode}-{case}.f32",PROBE_SIZE) for case in PROBE_CASES}
                probes.append(dict(level=level,mode=mode,**summarize_probe(rows)))
        out["clone_gpu_probes"]=probes
        out["clone_gpu_probe_verified"]=(out["probe_marker_pixels"]==PROBE_SIZE**2 and all(probe_pass(x) for x in probes)
            and any(x["clone_alpha_distinguished_from_controls"]>0 for x in probes))
        out["phase"]="independent_pixels"
        observations=[]
        for size in SIZES:
            for bg in range(BACKGROUNDS):
                rows={case:read_pixels(a.private/f"draw-{size}-{bg}-{case}.f32",size) for case in CASES}
                direct=read_pixels(a.private/f"direct-{size}-{bg}-dummy.f32",size)
                observations.append(dict(size=size,background=bg,dummy_direct_marker_pixels=dummy_marker(direct),**summarize(rows)))
        out["observations"]=observations
        for row in observations:row["classification"]=classify_draw(row)
        out["draw_classification_counts"]={k:sum(x["classification"]==k for x in observations) for k in sorted({x["classification"] for x in observations})}
        out["command_material_property_block_verified"]=all(x["native_vs_source_block"]==0 and x["native_visible"]>0 for x in observations)
        out["independent_alpha_effect_without_dummy_cases"]=sum(
            out["clone_gpu_probe_verified"] and alpha_effect_without_dummy(x) for x in observations)
        out["dummy_direct_calibrated_cases"]=sum(x["dummy_direct_marker_pixels"]>0 for x in observations)
        out["dummy_camera_calibrated_cases"]=sum(x["dummy_marker_pixels"]>0 for x in observations)
        passed=[x for x in observations if x["classification"]=="CALIBRATED_SOURCE_ROUTE_ALPHA_EFFECT"
                and x["dummy_direct_marker_pixels"]>0]
        out["calibrated_alpha_effect_cases"]=len(passed)
        need(out["clone_gpu_probe_verified"],"clone_gpu_texture_control_not_calibrated")
        need(out["dummy_direct_calibrated_cases"]==len(SIZES)*BACKGROUNDS,"dummy_direct_draw_not_calibrated")
        need(len(passed)==len(SIZES)*BACKGROUNDS,"draw_alpha_causality_not_established")
        out.update(status="OBSERVED_ISOLATED_PARTICLE108_EXPLICIT_ROUTE_ALPHA_EFFECT",phase="complete",
                   isolated_explicit_route_alpha_effect_observed=True)
    except Exception as exc:
        out["failure_type"]=type(exc).__name__
        if type(exc) is DrawError:out["failure_reason"]=str(exc)
    dump(a.safe,out);print("GT_PARTICLE108_ORIGINAL_DRAW "+json.dumps(out,sort_keys=True))
    return 0 if out["isolated_explicit_route_alpha_effect_observed"] else 2
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("project","private","safe"):p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,required=True)
    raise SystemExit(verify(p.parse_args()))
