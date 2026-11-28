"""Provider context follow-up, bound to five nonfinite source rows from 46156037577.
A real Unity reflection-probe context is an authored experiment, not the game.
Never infer original probe selection from scene inventory or synthetic captures.
"""
import re
from collections import Counter
from hashlib import sha256
import numpy as np
from tools.gt_top_resource_closure import selected_stage_provider as p, selected_array_causal as c

TARGET=(22,23,26,27,32)
SCENARIOS=("baseline","local_probes","restored")
REFLECTION={
    "unity_SpecCube"+str(i)+"_"+suffix:"reflection_"+kind
    for i in (0,1)
    for suffix,kind in (("BoxMin","box_min"),("BoxMax","box_max"),("ProbePosition","position"),("HDR","hdr"))
}
LIGHT_VOLUME={"unity_ProbeVolumeMin":"light_volume_min","unity_ProbeVolumeSizeInv":"light_volume_size_inverse",
              "unity_ProbeVolumeParams":"light_volume_params","unity_ProbeVolumeWorldToObject":"light_volume_matrix"}
TEXTURE={"unity_SpecCube0":"reflection_cube","unity_SpecCube1":"reflection_cube",
         "unity_ProbeVolumeSH":"light_volume_texture"}
def semantic(name):
    if name in REFLECTION:return REFLECTION[name]
    if name in LIGHT_VOLUME:return LIGHT_VOLUME[name]
    if name in TEXTURE:return TEXTURE[name]
    return "other_unresolved"

def select_rows(rows):
    c.need(len(rows)==40,"probe_previous_population")
    c.need(all(rows[i]["role"]=="fs" and rows[i]["kind"]=="unresolved" for i in TARGET),
           "probe_previous_nonfinite_rows_drift")
    selected=[]
    for i,row in enumerate(rows):
        tag=semantic(row["name"])
        if i not in TARGET and tag=="other_unresolved" and row["kind"]!="texture_dimensions":continue
        q=dict(row,source_ordinal=i,semantic=tag,previous_nonfinite=i in TARGET,mode=len(selected)+2)
        selected.append(q)
    c.need(sum(x["previous_nonfinite"] for x in selected)==5 and len(selected)<=40,"probe_selected_population")
    return selected

def pointer_state(value):
    if value is None:return "absent"
    if type(value) is not dict or type(value.get("m_PathID")) is not int or type(value.get("m_FileID")) is not int:
        return "unknown"
    return "nonnull" if value["m_PathID"] else "null"

def source_context(source,plan):
    key=tuple(plan["renderer"]);owner=key[0]
    renderer=source.obj(key,"MeshRenderer").read_typetree(check_read=False)
    def enum(name,allowed):
        v=renderer.get(name)
        return v if type(v) is int and v in allowed else "unknown"
    census=Counter();refs=Counter()
    for obj in source.file(owner).objects.values():
        name=obj.type.name
        if name not in ("ReflectionProbe","LightProbeGroup","LightProbeProxyVolume","RenderSettings"):continue
        census[name]+=1
        try:r=obj.read_typetree(check_read=False)
        except Exception:census[name+"_unreadable"]+=1;continue
        enabled=r.get("m_Enabled")
        if enabled in (0,1):census[name+"_enabled" if enabled else name+"_disabled"]+=1
        else:census[name+"_enabled_unknown"]+=1
        if name=="ReflectionProbe":
            box=r.get("m_BoxProjection")
            census["reflection_box_projection_on" if box==1 else "reflection_box_projection_off" if box==0 else "reflection_box_projection_unknown"]+=1
            for field in ("m_BakedTexture","m_CustomBakedTexture","m_Texture"):
                refs["reflection_"+field+"_"+pointer_state(r.get(field))]+=1
        elif name=="RenderSettings":
            for field in ("m_CustomReflection","m_DefaultReflection","m_SkyboxMaterial"):
                refs["settings_"+field+"_"+pointer_state(r.get(field))]+=1
    return dict(selected_renderer_reflection_probe_usage=enum("m_ReflectionProbeUsage",{0,1,2,3}),
                selected_renderer_light_probe_usage=enum("m_LightProbeUsage",{0,1,2,3}),
                selected_renderer_probe_anchor=pointer_state(renderer.get("m_ProbeAnchor")),
                selected_renderer_light_probe_volume_override=pointer_state(renderer.get("m_LightProbeVolumeOverride")),
                same_serialized_scene_component_counts=dict(census),same_scene_pointer_state_counts=dict(refs),
                original_runtime_probe_selection_verified=False,original_scene_reconstructed=False)

def stage(root,parsed,passes,wrapper,rows,mat,texenvs,shader_factory):
    from scripts.gt_original_921_shaderlab import verify_entrypoints
    private=select_rows(p.private_rows(rows,mat,texenvs,parsed,wrapper))
    body=p.instrument(wrapper,private)
    verify_entrypoints(body,root,routes=[[[]]])
    raw,_=shader_factory(parsed,passes,body,diagnostic=True)
    (root/"array-tap-shader.bytes").write_bytes(raw)
    return dict(provider_probe=True,probe_context=True,provider_transport_version=2,tap_available=True,
                tap_shader_sha=sha256(raw).hexdigest(),provider_rows=[{k:v for k,v in r.items() if k!="expression"} for r in private])

def summarize(cfg,receipt,read):
    rows=cfg["provider_rows"]
    c.need(sum(r.get("previous_nonfinite") is True for r in rows)==5 and
           tuple(r["source_ordinal"] for r in rows if r.get("previous_nonfinite") is True)==TARGET,
           "probe_target_coverage")
    c.need(len(receipt["scenarios"])==3,"probe_scenario_population")
    outputs={}
    for name,s in zip(SCENARIOS,receipt["scenarios"],strict=True):
        c.need(s["scenario"]==name,"probe_scenario_order")
        c.need(len(s["views"])==3 and len(s["selected_local_counts"])==3,"probe_view_population")
        counts=s["selected_local_counts"]
        c.need(all(type(n) is int and 0<=n<=2 for n in counts),"probe_selection_counts")
        c.need(all(n==0 for n in counts) if name!="local_probes" else all(n>0 for n in counts),
               "probe_engine_selection_not_established")
        def load(file):return read(name+"-"+file)
        result=p.summarize(cfg,{"views":s["views"]},load)
        c.need(result["status"]=="OBSERVED_SOURCE_STAGE_PROVIDER_DIAGNOSTIC","probe_transport_inconclusive")
        outputs[name]=dict(result,selected_local_counts=counts)
    baseline=outputs["baseline"]["row_observations"]
    local=outputs["local_probes"]["row_observations"]
    restored=outputs["restored"]["row_observations"]
    response=[];restored_count=0
    for i,r in enumerate(rows):
        if not r["previous_nonfinite"]:continue
        def verdict(x):
            obs=x[i]["observations"]
            return (obs.get("shader_nonfinite",0),obs.get("finite_uniform",0))
        b,l,z=map(verdict,(baseline,local,restored))
        # Old run and same-run baseline must agree before testing response.
        c.need(b==(3,0),"probe_prior_nonfinite_not_reproduced")
        same=b==z
        restored_count+=int(same)
        response.append(dict(source_ordinal=r["source_ordinal"],semantic=r["semantic"],baseline_nonfinite_views=b[0],
                             local_nonfinite_views=l[0],local_finite_views=l[1],restored_nonfinite_views=z[0],
                             finite_with_local_probes=l==(0,3) and same,restored=same))
    final=[]
    for v in range(3):
        images={name:read(name+"-final-"+str(v)+".f32") for name in SCENARIOS}
        c.need(all(np.isfinite(a).all() for a in images.values()),"probe_final_nonfinite")
        final.append(dict(local_vs_baseline=c.diff(images["local_probes"],images["baseline"]),
                          restored_vs_baseline=c.diff(images["restored"],images["baseline"])))
    reversible=restored_count==5 and all(x["restored_vs_baseline"]["exactly_different"]==0 for x in final)
    return dict(status="OBSERVED_AUTHORED_PROBE_CONTEXT" if reversible else "INCONCLUSIVE_PROBE_REVERSIBILITY",
                target_rows=response,scenarios={name:{"counts":x["counts"],"selected_local_counts":x["selected_local_counts"]}
                                                for name,x in outputs.items()},
                source_target_semantics=dict(Counter(x["semantic"] for x in response)),
                finite_with_local_probes=sum(x["finite_with_local_probes"] for x in response),
                restored_target_rows=restored_count,final_color_comparison=final,
                source_shader_final_responsive_views=sum(x["local_vs_baseline"]["different_over_1_div_255"]>0 for x in final),
                original_game_global_resources_verified=False,original_game_probe_selection_verified=False,
                white_mesh_repair_verified=False,diagnostic_only=True)
