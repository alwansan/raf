"""Private same-export selected mesh/material/explicit original shader draw.
Never publish source programs, names, serialized assets or readback pixels.
A diagnostic camera is not a reconstruction of the original game scene.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import numpy as np
from tools.gt_top_resource_closure import probe, recheck, selected_array, selected_material_reference as ref
from scripts import gt_verify_original_mesh_export as mesh, gt_material_route_values as values
from scripts import gt_particle108_local_texture_document as native
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.w1_depth_shaderlab import quoted, tags, render_state

CASES=("type3","type2","wrong_guid","wrong_fileid")
VIEWS=3
SIZE=128
class StageError(ValueError): pass
def need(ok,code):
    if not ok: raise StageError(code)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def write_json(path,data):
    with path.open("x") as f: json.dump(data,f,sort_keys=True,allow_nan=False)

def variants(body,prop,guid,fid,kind,wrong):
    corrected=ref.repair_native_reference(body,prop,guid,fid,kind)
    anchor="{fileID: "+str(fid)+", guid: "+guid+", type: 2}"
    need(corrected.count(anchor)==1 and wrong!=guid,"draw_reference_anchor")
    wrong_guid=corrected.replace(anchor,"{fileID: "+str(fid)+", guid: "+wrong+", type: 2}")
    wrong_id=corrected.replace(anchor,"{fileID: "+str(fid+1)+", guid: "+guid+", type: 2}")
    before=native.strict_mapping(body)["Material"]
    slots=normalize_texenvs(before["m_SavedProperties"]["m_TexEnvs"],exported=True)
    for candidate,pointer in ((corrected,(fid,guid,2)),(wrong_guid,(fid,wrong,2)),(wrong_id,(fid+1,guid,2))):
        after=native.strict_mapping(candidate)["Material"]
        actual=normalize_texenvs(after["m_SavedProperties"]["m_TexEnvs"],exported=True)
        expected=dict(slots);expected[prop]=(pointer,slots[prop][1])
        need(actual==expected and after["m_Shader"]==before["m_Shader"],"draw_control_pointer_drift")
        restored=candidate.replace("{fileID: "+str(pointer[0])+", guid: "+pointer[1]+", type: 2}",
            "{fileID: "+str(fid)+", guid: "+guid+", type: 3}")
        need(restored==body,"draw_control_other_bytes_changed")
    return dict(zip(CASES,(body,corrected,wrong_guid,wrong_id),strict=True))

def source_shader(parsed,passes,wrapper,*,diagnostic=False):
    properties,counts=serialize_properties(parsed,allow_hidden_and_toggle=True)
    rows=[p for p in passes if p["subshader"]==0 and p["pass"]==0]
    need(len(rows)==1,"draw_pass_identity")
    sub=parsed["m_SubShaders"][0]
    # Exact original properties, selected pass render state and SubShader tags.
    # Other passes and runtime route dispatch are deliberately absent.
    if diagnostic:
        from tools.gt_top_resource_closure import selected_array_causal as causal
        need(properties.rstrip().endswith("}") and causal.MODE not in properties,"tap_diagnostic_property_collision")
        properties=properties.rstrip()[:-1]+causal.MODE+' ("GT diagnostic mode", Float) = 0\n}'
    pass_state=(tags(rows[0]["original_state"]["m_Tags"])+"\nCull Off\nZWrite On\nZTest LEqual\nBlend Off\nColorMask RGBA\nAlphaToMask Off" if diagnostic else render_state(rows[0]["original_state"],allow_selective_color_mask=True))
    shader="\n".join(["Shader "+quoted("Hidden/GTSelectedArrayTap" if diagnostic else parsed["m_Name"])+" {",properties,
        "SubShader {","LOD "+str(sub["m_LOD"]),tags(sub["m_Tags"]),
        "Pass {",pass_state,
        wrapper,"}","}","Fallback Off","}",""])
    return shader.encode(),counts["original_authored_property_count"]

def float_from_bits(bits): return struct.unpack("<f",struct.pack("<I",bits))[0]
def prepare(a,out,source,plan,mat,mk,xk,trace,body,mesh_info,prop,edge,parsed,passes,wrapper,*,provider_rows=None):
    root=a.draw_private;project=a.unity_project
    need(not root.exists() and not project.exists() and bool(a.run_id),"fresh_draw_stage")
    root.mkdir(mode=0o700);project.mkdir()
    actual=native.strict_mapping(body)["Material"]
    before=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])
    after=normalize_texenvs(actual["m_SavedProperties"]["m_TexEnvs"],exported=True)
    sp=actual["m_Shader"]
    sg=sp["guid"]
    need(sp["fileID"]==4800000 and sp["type"]==3 and re.fullmatch(r"[0-9a-f]{32}",sg),"draw_source_shader_identity")
    assets=[]
    def stage(rel,raw,metadata,guid,fid):
        need(rel.startswith("Assets/GTDraw/") and "\\" not in rel and ".." not in Path(rel).parts and
             re.fullmatch(r"[0-9a-f]{32}",guid) and all(v["guid"]!=guid for v in assets),"draw_stage_asset_path_identity")
        number=len(assets)
        blob=f"asset-{number}.bytes";meta=f"asset-{number}.meta.bytes"
        (root/blob).write_bytes(raw);(root/meta).write_bytes(metadata)
        assets.append(dict(path=rel,blob=blob,meta_blob=meta,guid=guid,file_id=fid,
                           sha256=sha(raw),meta_sha256=sha(metadata)))
    out["draw_stage_phase"]="source_shader_and_mesh"
    shader,prop_count=source_shader(parsed,passes,wrapper)
    shader_path="Assets/GTDraw/Source/Selected.shader"
    shader_meta=("fileFormatVersion: 2\nguid: "+sg+"\nShaderImporter:\n  externalObjects: {}\n  defaultTextures: []\n  nonModifiableTextures: []\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n").encode()
    stage(shader_path,shader,shader_meta,sg,4800000)
    index=probe.file_index(a.project,{xk[0]})
    path=index[xk[0]][0]
    need(path.suffix.lower()==".asset","draw_mesh_native_asset_extension")
    geo=mesh.export_geometry(path,xk[1])
    mesh_path="Assets/GTDraw/Mesh/"+path.name
    stage(mesh_path,path.read_bytes(),path.with_name(path.name+".meta").read_bytes(),xk[0],xk[1])
    slots=[];nonnull=[];array_source=None;array_guid=None;array_path=None
    out["draw_stage_phase"]="same_export_texture_payloads"
    for name in sorted(before):
        linked=recheck.exact_slot(before[name],after[name],plan["material"][0],mk[0],source,trace,
                                  plan["texture_targets"].get(name))
        uv=before[name][1]
        need(uv is not None and len(uv)==4,"draw_texenv_uv_missing")
        slot=dict(name=name,uv=list(uv),guid="",file_id=0,cls=0)
        if linked is not None:
            key,exp,kind,cls=linked
            slot.update(guid=exp[0],file_id=exp[1],cls=cls)
            nonnull.append(exp[0])
            target,meta=probe.file_index(a.project,{exp[0]})[exp[0]]
            if cls==28:
                observation=probe.texture_check(source,key,target,meta,exp[1],kind,semantic_observation=True)
                need(observation["status"]=="MATCH" or observation.get("source_declared_export_semantics",{}).get("source_declared_transform_match") is True,
                     "draw_texture_source_export_parity")
                need(target.suffix.lower()==".png" and kind==3 and exp[1]==2800000,"draw_texture_importer_identity")
                stage("Assets/GTDraw/Tex"+str(len(slots))+"/"+target.name,target.read_bytes(),
                      target.with_name(target.name+".meta").read_bytes(),exp[0],exp[1])
            elif cls==187:
                need(array_source is None and name==prop and linked==edge,"draw_array_identity")
                array_source=source.obj(key,"Texture2DArray").read_typetree(check_read=False)
                _,raw=selected_array.exact_inline(array_source)
                (root/"array.bc3.bytes").write_bytes(raw)
                array_guid=exp[0];array_path="Assets/GTDraw/Array/"+target.with_suffix(".asset").name
            else: raise StageError("draw_unsupported_texture_class")
        slots.append(slot)
    need(len(slots)==6 and len(nonnull)==4 and len(set(nonnull))==4 and array_source is not None,"draw_selected_slot_population")
    wrong=ref.WRONG_GUID
    need(wrong not in nonnull+[sg,mk[0],xk[0]],"draw_wrong_GUID_collision")
    settings=array_source["m_TextureSettings"]
    sampler=[settings[k] for k in ("m_FilterMode","m_Aniso","m_WrapU","m_WrapV","m_WrapW")]
    bias=settings["m_MipBias"]
    need(all(type(x) is int for x in sampler) and 0<=sampler[0]<=2 and 0<=sampler[1]<=16 and
         all(0<=x<=3 for x in sampler[2:]) and type(bias) in (float,int) and math.isfinite(bias),"draw_array_sampler_schema")
    out["draw_stage_phase"]="source_material_variants"
    bodies=variants(body,prop,array_guid,18700000,3,wrong)
    need(mk[1]==2100000,"draw_material_native_id")
    prefix="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000"
    materials=[]
    for case in CASES:
        data=(prefix+bodies[case]).encode();blob="mat-"+case+".bytes"
        (root/blob).write_bytes(data);materials.append(dict(name=case,blob=blob,sha256=sha(data)))
    normalized=values.normalize(mat)
    numbers=[dict(name=k,kind="float",value=[float_from_bits(v)]) for k,v in normalized["m_Floats"].items()]
    numbers += [dict(name=k,kind="color",value=[float_from_bits(x) for x in v]) for k,v in normalized["m_Colors"].items()]
    need(not normalized["m_Ints"],"draw_int_upload_unimplemented")
    cfg=dict(run_id=a.run_id,assets=assets,shader_path=shader_path,shader_guid=sg,mesh_path=mesh_path,
             mesh_guid=xk[0],mesh_id=xk[1],vertex_count=geo["vertex_count"],vertex_bytes=geo["vertex_buffer"][0],
             vertex_sha=geo["vertex_buffer"][1],index_bytes=geo["index_buffer"][0],index_sha=geo["index_buffer"][1],
             index_format=geo["index_format"],mesh_stride=mesh_info["source_vertex_bytes"]//mesh_info["source_vertex_count"],
             array_guid=array_guid,array_path=array_path,array_name=array_source["m_Name"],array_sha=sha(raw),
             sampler=sampler,mip_bias=bias,selected_property=prop,wrong_guid=wrong,slots=slots,numbers=numbers,
             materials=materials,views=VIEWS,size=SIZE)
    from tools.gt_top_resource_closure import selected_array_causal as causal
    if provider_rows is None:
        tap=causal.stage_tap(root,parsed,passes,wrapper,prop,source_shader)
        out["tap_stage"]={k:v for k,v in tap.items() if k!="tap_shader_sha"}
    else:
        from tools.gt_top_resource_closure import selected_stage_provider as provider
        tap=provider.stage(root,parsed,passes,wrapper,provider_rows,mat,before,source_shader)
        out["provider_stage"]={"prepared":True,"source_probe_rows":len(tap["provider_rows"]),
                               "original_game_context":False,"private_names_published":False}
    cfg.update(tap)
    cfg["tap_expected_properties"]=prop_count
    here=Path(__file__).parent
    prior=(here/"SelectedArrayNative.cs").read_text()
    need(prior.count("public static class SelectedArrayUnity")==1 and prior.count("public static void Run()")==1,"draw_prior_editor_helper_anchor")
    prior=prior.replace("public static class SelectedArrayUnity","public static partial class SelectedArrayUnity").replace("public static void Run()","public static void RunPriorArray()")
    # Only authored scripts/controls are in Assets before the guarded method.
    files={"Assets/Editor/SelectedArrayNativeHelpers.cs":prior.encode(),
           "Assets/Editor/SelectedOriginalDraw.cs":(here/"SelectedOriginalDraw.cs").read_bytes(),
           "Assets/Editor/SelectedArrayCausal.cs":(here/"SelectedArrayCausal.cs").read_bytes(),
           "Assets/Editor/SelectedStageProvider.cs":(here/"SelectedStageProvider.cs").read_bytes(),
           "Assets/GTSelectedArray.compute":(here/"GTSelectedArray.compute").read_bytes(),
           "Assets/GTDrawControl.shader":b'Shader "Hidden/GTDrawControl" {\nSubShader {\nPass {\nCull Off\nZWrite On\nCGPROGRAM\n#pragma vertex vert\n#pragma fragment frag\n#include "UnityCG.cginc"\nfloat4 vert(float4 v:POSITION):SV_POSITION{return UnityObjectToClipPos(v);}\nfloat4 frag():SV_Target{return float4(0.91,0.07,0.61,1);}\nENDCG\n} } Fallback Off }\n',
           "Packages/manifest.json":b'{"dependencies":{}}\n',
           "ProjectSettings/ProjectVersion.txt":b"m_EditorVersion: 2021.3.45f2\n",
           "ProjectSettings/ProjectSettings.asset":b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTValidation\n  productName: GTSelectedDraw\n  m_ActiveColorSpace: 1\n"}
    for rel,data in files.items():
        path=project/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    write_json(root/"expected.json",cfg)
    (project/"GTInput.json").write_bytes((root/"expected.json").read_bytes())
    return dict(staged_exact_shader_GUID=True,source_properties=prop_count,explicit_pass_only=True,
                staged_mesh=True,staged_Texture2D=3,staged_native_BC3=True,material_cases=4,
                private_payload_withheld_until_guard=True,original_game_context=False)

def read_pixels(path,size):
    values=read_provider_pixels(path,size)
    need(np.isfinite(values).all(),"draw_readback_nonfinite")
    return values

def read_provider_pixels(path,size):
    # Transport-only reader: called without finite gate solely by the
    # provider classifier, which checks raw/encoded IEEE classes separately.
    need(path.is_file() and not path.is_symlink() and path.stat().st_size==size*size*16,"draw_readback_extent")
    return np.fromfile(path,dtype="<f4").reshape(size,size,4)

def pixel_summary(pixels):
    # Counts only, never actual RGBA, spatial coordinates or source images.
    need(set(pixels)=={"clear","dummy","type2_repeat",*CASES},"draw_case_population")
    shapes={x.shape for x in pixels.values()}
    need(len(shapes)==1 and all(np.isfinite(x).all() for x in pixels.values()),"draw_readback_schema")
    def difference(x,y): return int(np.count_nonzero(np.max(np.abs(x-y),axis=-1)>1/255))
    covered=np.max(np.abs(pixels["type2"]-pixels["clear"]),axis=-1)>1/255
    rgb=pixels["type2"][...,:3]
    return dict(candidate_near_black_pixels=int(np.count_nonzero(covered&(np.max(np.abs(rgb),axis=-1)<=1/255))),
                candidate_near_white_pixels=int(np.count_nonzero(covered&(np.max(np.abs(rgb-1),axis=-1)<=1/255))),
                candidate_near_magenta_pixels=int(np.count_nonzero(covered&(np.max(np.abs(rgb-np.array([1,0,1])),axis=-1)<=1/255))),
                type2_vs_type3_exact_different_pixels=int(np.count_nonzero(np.any(pixels["type2"]!=pixels["type3"],axis=-1))),
                dummy_vs_clear=difference(pixels["dummy"],pixels["clear"]),
                type2_vs_clear=difference(pixels["type2"],pixels["clear"]),
                type3_vs_clear=difference(pixels["type3"],pixels["clear"]),
                type2_vs_dummy=difference(pixels["type2"],pixels["dummy"]),
                type2_repeat_difference=difference(pixels["type2"],pixels["type2_repeat"]),
                type2_vs_type3=difference(pixels["type2"],pixels["type3"]),
                type2_vs_wrong_guid=difference(pixels["type2"],pixels["wrong_guid"]),
                type2_vs_wrong_fileid=difference(pixels["type2"],pixels["wrong_fileid"]))

TAP_PHASES=frozenset(("not_started","verify_private_bytes","import_shader","validate_shader","shader_ready",
                      "load_imported_shader","typed_source_clone","typed_red_clone","typed_green_clone",
                      "materials_ready","capture_calibration","capture_hit","capture_sample","capture_complete"))
TAP_FAILURES=frozenset(("","InvalidOperationException","IOException","FileNotFoundException",
                        "ArgumentException","UnityException","NullReferenceException","MissingReferenceException"))
def tap_observation(cfg,r):
    # Separate actual editor import from material creation and pixel measurement.
    expected=cfg.get("tap_expected_properties")
    need(type(expected) is int and 0<expected<=1000,"tap_expected_property_schema")
    out={k:r.get(k) is True for k in ("tap_imported","tap_shader_supported","tap_shader_compiled","tap_materials_ready")}
    out["tap_phase"]=r.get("tap_phase") if r.get("tap_phase") in TAP_PHASES else "unknown"
    out["tap_failure_category"]=r.get("tap_failure_category") if r.get("tap_failure_category") in TAP_FAILURES else "other"
    for k in ("tap_shader_errors","tap_shader_passes","tap_copied_properties_source","tap_copied_properties_red","tap_copied_properties_green","causal_tap_views"):
        v=r.get(k)
        need(type(v) is int and -1<=v<=10000,"tap_counter_schema")
        out[k]=v
    out["tap_expected_properties"]=expected
    out["tap_typed_copy_verified"]=all(out[k]==expected for k in ("tap_copied_properties_source","tap_copied_properties_red","tap_copied_properties_green"))
    out["tap_capture_admitted"]=(cfg.get("tap_available") is True and all(out[k] for k in
         ("tap_imported","tap_shader_supported","tap_shader_compiled","tap_materials_ready","tap_typed_copy_verified"))
         and out["tap_shader_errors"]==0 and out["tap_shader_passes"]==1 and out["causal_tap_views"]==VIEWS
         and out["tap_phase"]=="capture_complete" and out["tap_failure_category"]=="")
    return out

def basis_observation(cfg,r,read):
    from tools.gt_top_resource_closure import selected_array_basis as basis
    n=cfg.get("tap_source_sample_sites")
    need(type(n) is int and 1<=n<=8,"basis_site_schema")
    phases={"not_started","prepare","raw_endpoint","original_clone","typed_clone","ready",
            "original_draw","site_calibration","site_hit","site_sample","complete"}
    out=dict(basis_ready=r.get("basis_ready") is True,
             basis_phase=r.get("basis_phase") if r.get("basis_phase") in phases else "unknown",
             basis_failure_category=r.get("basis_failure_category") if r.get("basis_failure_category") in TAP_FAILURES else "other")
    for k in ("basis_array_payloads","basis_original_clones","basis_typed_clones","basis_views","basis_site_pairs"):
        x=r.get(k)
        need(type(x) is int and 0<=x<=10000,"basis_counter")
        out[k]=x
    out["basis_capture_admitted"]=(out["basis_ready"] and out["basis_phase"]=="complete" and
        out["basis_failure_category"]=="" and all(out[k]==10 for k in
        ("basis_array_payloads","basis_original_clones","basis_typed_clones")) and
        out["basis_views"]==VIEWS and out["basis_site_pairs"]==VIEWS*10*n)
    if not out["basis_capture_admitted"]:return out
    rows=[]
    for view in range(VIEWS):
        def load(m,s):return read("view-"+str(view)+"-basis-"+str(m)+"-"+s+".f32")
        final={m:load(m,"final") for m in basis.MASKS}
        cal={m:load(m,"cal") for m in basis.MASKS}
        sites=[{m:(load(m,"hit-"+str(i)),load(m,"sample-"+str(i))) for m in basis.MASKS} for i in range(n)]
        rows.append(basis.summarize(final,cal,sites))
    out["basis_observations"]=rows
    out["basis_classification"]=basis.classify(rows,n)
    return out

def verify(a):
    out=dict(status="INCONCLUSIVE",phase="editor_receipt",original_game_draw_verified=False,
             original_shader_draw_verified=False,isolated_source_candidate_draw_observed=False,
             runtime_keyword_selection_verified=False,merged_binding_offset_parity_verified=False,
             original_game_global_resources_verified=False,android_device=False,white_mesh_repair_verified=False,
             original_reference_pixel_gate_passed=False,array_causal_diagnostic_verified=False,
             production=False,XAPK=False,private_payload_published=False)
    try:
        cfg=json.loads((a.private/"expected.json").read_text())
        need(cfg==json.loads((a.unity_project/"GTInput.json").read_text()) and cfg["run_id"]==a.run_id,
             "draw_stage_run_identity")
        need((a.private/"editor-output-private").read_text().strip()==a.run_id and (a.private/"editor.log").is_file(),"draw_private_log_guard")
        r=json.loads((a.private/"draw-receipt.json").read_text())
        need(r["run_id"]==a.run_id and r["private_log_guard"] is True,"draw_editor_run_identity")
        phases={"environment","private_guard","source_assets","native_array","materials","mesh","render","complete"}
        out["editor_phase"]=r.get("phase") if r.get("phase") in phases else "unknown"
        flags=("shader_identity","shader_supported","mesh_identity","mesh_vertex_bytes_match","mesh_index_bytes_match",
               "mesh_descriptor_match","array_identity","array_raw_bytes_match","array_sampler_match","material_shader_identity",
               "reference_controls_expected","all_four_nonnull_type2","all_six_serialized_UV_type2","all_material_YAML_unchanged")
        out.update({k:r.get(k) is True for k in flags})
        for k in ("shader_errors","shader_passes","source_asset_identities","source_asset_bytes_unchanged",
                  "source_asset_meta_bytes_unchanged","saved_float_runtime_matches","saved_color_runtime_matches",
                  "saved_float_runtime_declared","saved_color_runtime_declared","rendered_views"):
            v=r.get(k)
            if type(v) is int and 0<=v<=10000:out[k]=v
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear","draw_editor_environment")
        need(a.exit_code==0 and r["status"]=="OBSERVED","draw_editor_inconclusive")
        out["phase"]="independent_readback"
        summaries=[pixel_summary({case:read_pixels(a.private/f"view-{v}-{case}.f32",SIZE)
                   for case in ("clear","dummy","type2_repeat",*CASES)}) for v in range(VIEWS)]
        out["views"]=summaries
        out["authored_dummy_visible"]=all(x["dummy_vs_clear"]>0 for x in summaries)
        out["candidate_visible_views"]=sum(x["type2_vs_clear"]>0 for x in summaries)
        out["candidate_distinguished_from_dummy_views"]=sum(x["type2_vs_dummy"]>0 for x in summaries)
        out["reference_pixel_differential_views"]=sum(all(x[k]>0 for k in
               ("type2_vs_type3","type2_vs_wrong_guid","type2_vs_wrong_fileid")) for x in summaries)
        out["repeat_deterministic_views"]=sum(x["type2_repeat_difference"]==0 for x in summaries)
        out["same_view_all_draw_controls_pass"]=sum(x["dummy_vs_clear"]>0 and x["type2_vs_clear"]>0 and
            x["type2_vs_dummy"]>0 and x["type2_repeat_difference"]==0 and all(x[k]>0 for k in
            ("type2_vs_type3","type2_vs_wrong_guid","type2_vs_wrong_fileid")) for x in summaries)
        imports_ok=(all(out[k] for k in flags) and out.get("shader_errors")==0 and out.get("shader_passes")==1
             and out.get("source_asset_identities")==5 and out.get("source_asset_bytes_unchanged")==5 and
             out.get("source_asset_meta_bytes_unchanged")==5)
        need(imports_ok,"draw_exact_import_or_reference_identity_not_established")
        out["original_reference_pixel_gate_passed"]=out["same_view_all_draw_controls_pass"]>0
        out["isolated_source_candidate_draw_observed"]=out["original_reference_pixel_gate_passed"]
        if cfg.get("provider_probe") is True:
            from tools.gt_top_resource_closure import selected_stage_provider as provider
            out["phase"]="independent_source_stage_provider_readback"
            need(r.get("tap_shader_compiled") is True and r.get("tap_shader_errors")==0 and
                 r.get("provider_typed_properties")==cfg["tap_expected_properties"] and
                 r.get("provider_views")==VIEWS and r.get("provider_observations")==VIEWS*len(cfg["provider_rows"]) and
                 r.get("provider_class_captures")==VIEWS*(len(cfg["provider_rows"])+2),
                 "provider_editor_capture_incomplete")
            receipt=json.loads((a.private/"provider-receipt.json").read_text())
            out["provider_observation"]=provider.summarize(cfg,receipt,lambda name:read_provider_pixels(a.private/name,SIZE))
            out["status"]=out["provider_observation"]["status"];out["phase"]="complete"
            write_json(a.safe,out);print("GT_SELECTED_ORIGINAL_DRAW "+json.dumps(out,sort_keys=True))
            return 0 if out["status"]=="OBSERVED_SOURCE_STAGE_PROVIDER_DIAGNOSTIC" else 2
        from tools.gt_top_resource_closure import selected_array_causal as causal
        out["phase"]="independent_causal_readback"
        out["tap_stage_available"]=cfg.get("tap_available") is True
        out.update(tap_observation(cfg,r))
        out["authored_array_overrides_bound"]=r.get("authored_array_overrides_bound") is True
        out["causal_override_views"]=r.get("causal_override_views",0)
        need(out["authored_array_overrides_bound"] and out["causal_override_views"]==VIEWS,
             "causal_override_draw_incomplete")
        tap=out["tap_capture_admitted"]
        diagnostics=[]
        for v in range(VIEWS):
            pixels={case:read_pixels(a.private/f"view-{v}-{case}.f32",SIZE)
                    for case in causal.BASE_CASES+(causal.TAP_CASES if tap else ())}
            diagnostics.append(causal.summarize(pixels,read_pixels(a.private/f"view-{v}-type2.f32",SIZE),tap))
        out["causal_views"]=diagnostics
        out["causal_classification"]=causal.classify(diagnostics)
        out["array_causal_diagnostic_verified"]=out["causal_classification"]["status"]!="INCONCLUSIVE_SAMPLE_CAUSALITY"
        if not out["original_reference_pixel_gate_passed"]:
            out["original_reference_gate_failure"]="draw_reference_pixel_differential_not_established"
        out["phase"]="independent_rgba_endpoint_basis"
        out.update(basis_observation(cfg,r,lambda file:read_pixels(a.private/file,SIZE)))
        need(out.get("basis_classification",{}).get("status")=="OBSERVED_RGBA_ENDPOINT_BASIS","rgba_endpoint_basis_inconclusive")
        out.update(status="OBSERVED_RGBA_ENDPOINT_BASIS",phase="complete")
    except Exception as exc:
        out["failure_type"]=type(exc).__name__
        if type(exc) is StageError:out["failure_reason"]=str(exc)
    write_json(a.safe,out)
    print("GT_SELECTED_ORIGINAL_DRAW "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]=="OBSERVED_RGBA_ENDPOINT_BASIS" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("private","unity-project","safe"):p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,required=True)
    raise SystemExit(verify(p.parse_args()))
