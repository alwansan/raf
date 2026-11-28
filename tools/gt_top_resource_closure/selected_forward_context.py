"""Isolate source-authenticated ForwardBase tag spelling from lighting upload.
No engine keyword route or production repair claim. Only exact source case
normalization in the pass tag, plus uniquely named temporary shader clones.
"""
import re
from collections import Counter
from hashlib import sha256
import numpy as np
from scripts.w1_depth_shaderlab import quoted
from scripts.gt_resource_register_contract import mask_noncode
from tools.gt_top_resource_closure import selected_stage_provider as p, selected_array_causal as c

LIGHT_NAMES={"_LightColor0":"light_color","_WorldSpaceLightPos0":"light_position"}
SCENARIOS=("first","second","restored")
MODES=("raw","canonical")
CANON_FINAL="Hidden/GTSelectedCanonicalPass"
CANON_TAP="Hidden/GTSelectedCanonicalTap"
CONTROL= r'''Shader "Hidden/GTSelectedEngineLightControl" {
Properties { _GTControlMode ("Control mode", Float) = 0 }
SubShader { Pass {
Tags { "LightMode" = "ForwardBase" }
Cull Off ZWrite On ZTest LEqual Blend Off
CGPROGRAM
#pragma target 3.0
#pragma vertex vert
#pragma fragment frag
#pragma multi_compile_fwdbase
#include "UnityCG.cginc"
#include "Lighting.cginc"
float _GTControlMode;
float4 vert(float4 v:POSITION):SV_POSITION { return UnityObjectToClipPos(v); }
float4 frag():SV_Target {
 if(_GTControlMode==0.0)return float4(0.125,0.375,0.625,1.0);
 if(_GTControlMode==1.0)return float4(0.75,0.25,0.5,0.875);
 if(_GTControlMode==2.0)return _LightColor0;
 return _WorldSpaceLightPos0;
}
ENDCG
} } Fallback Off }
'''

def exact_forward_tag(passes):
    records=[r for r in passes if r["subshader"]==0 and r["pass"]==0]
    c.need(len(records)==1,"pass_context_source_pass_identity")
    pairs=records[0]["original_state"]["m_Tags"].get("tags",[])
    match=[(k,v) for k,v in pairs if k.casefold()=="lightmode"]
    c.need(len(match)==1 and match[0][1].casefold()=="forwardbase","pass_context_source_not_forwardbase")
    k,v=match[0]
    return k,v

def rename_and_normalize(raw,original,new,tag):
    text=raw.decode("utf-8")
    start="Shader "+quoted(original)+" {"
    c.need(text.count(start)==1,"pass_context_shader_name_anchor")
    old=quoted(tag[0])+" = "+quoted(tag[1])
    canonical='"LightMode" = "ForwardBase"'
    c.need(text.count(old)==1,"pass_context_tag_anchor")
    changed=text.replace(start,"Shader "+quoted(new)+" {",1).replace(old,canonical,1)
    restored=changed.replace("Shader "+quoted(new)+" {",start,1).replace(canonical,old,1)
    c.need(restored==text,"pass_context_other_bytes_changed")
    return changed.encode()

def stage(root,parsed,passes,wrapper,rows,mat,texenvs,shader_factory):
    from scripts.gt_original_921_shaderlab import verify_entrypoints
    tag=exact_forward_tag(passes)
    prior=p.private_rows(rows,mat,texenvs,parsed,wrapper)
    private=[]
    for item in prior:
        if item["name"] not in LIGHT_NAMES:continue
        c.need(item["numeric_type"]=="float" and item["lanes"] in (3,4),"pass_context_light_member_shape")
        private.append(dict(item,semantic=LIGHT_NAMES[item["name"]],mode=len(private)+2))
    c.need(1<=len(private)<=4,"pass_context_no_source_light_members")
    body=p.instrument(wrapper,private)
    verify_entrypoints(body,root,routes=[[[]]])
    raw_final,count=shader_factory(parsed,passes,wrapper)
    raw_tap,_=shader_factory(parsed,passes,body,diagnostic=True)
    canonical=rename_and_normalize(raw_final,parsed["m_Name"],CANON_FINAL,tag)
    canonical_tap=rename_and_normalize(raw_tap,"Hidden/GTSelectedArrayTap",CANON_TAP,tag)
    files={"array-tap-shader.bytes":raw_tap,"canonical-pass-shader.bytes":canonical,
           "canonical-tap-shader.bytes":canonical_tap,"engine-light-control.bytes":CONTROL.encode()}
    for name,data in files.items():(root/name).write_bytes(data)
    return dict(provider_probe=True,pass_context=True,provider_transport_version=2,
                tap_available=True,tap_shader_sha=sha256(raw_tap).hexdigest(),
                canonical_pass_sha=sha256(canonical).hexdigest(),canonical_tap_sha=sha256(canonical_tap).hexdigest(),
                engine_light_control_sha=sha256(files["engine-light-control.bytes"]).hexdigest(),
                source_tag_already_canonical=tag==("LightMode","ForwardBase"),
                provider_rows=[{k:v for k,v in r.items() if k!="expression"} for r in private])

def read_modes(read,prefix,rows):
    a,b=read(prefix+"-0.f32"),read(prefix+"-1.f32")
    mask=c.near(a,p.CAL_A)
    c.need(mask.any() and np.array_equal(mask,c.near(b,p.CAL_B)),"pass_context_calibration")
    vals=[]
    for mode,lanes in rows:
        value=p.finite_uniform(read(prefix+"-"+str(mode)+".f32"),mask,lanes)
        c.need(value is not None,"pass_context_nonfinite_or_nonuniform")
        vals.append(value)
    return vals,int(mask.sum())

def summarize(cfg,receipt,read):
    c.need(receipt["views"]==3 and receipt["scenarios"]==3 and
           receipt["typed_properties"]==cfg["tap_expected_properties"]*3 and receipt["shader_errors"]==0,
           "pass_context_capture_receipt")
    rows=cfg["provider_rows"]
    c.need(1<=len(rows)<=4 and [r["mode"] for r in rows]==list(range(2,2+len(rows))),"pass_context_population")
    counts=Counter();views=[]
    for v in range(3):
        samples={};finals={}
        for scenario in SCENARIOS:
            base=scenario+"-"+str(v)
            ref,n=read_modes(read,base+"-control",[(2,4),(3,4)])
            counts["control_calibrated_views"]+=1
            samples[scenario]={"control":ref}
            for mode in MODES:
                data,n=read_modes(read,base+"-"+mode,[(r["mode"],r["lanes"]) for r in rows])
                samples[scenario][mode]=data;counts[mode+"_calibrated_views"]+=1
                finals[scenario,mode]=read(base+"-"+mode+"-final.f32")
        # Directional control must demonstrate an actual change in each
        # observed semantic, and restore, before interpreting candidate.
        view_result={"rows":[]}
        for i,r in enumerate(rows):
            index=0 if r["semantic"]=="light_color" else 1
            n=r["lanes"];a,b,z=[samples[s]["control"][index][:n] for s in SCENARIOS]
            c.need(not np.allclose(a,b,atol=1e-4,rtol=1e-4) and np.allclose(a,z,atol=1e-4,rtol=1e-4),
                   "pass_context_control_not_responsive_reversible")
            row={"semantic":r["semantic"],"stage":r["role"]}
            for mode in MODES:
                x,y,w=[samples[s][mode][i] for s in SCENARIOS]
                matches=all(np.allclose(a,b,atol=1e-4,rtol=1e-4) for a,b in ((x,a),(y,b),(w,z)))
                responsive=not np.allclose(x,y,atol=1e-4,rtol=1e-4)
                restored=np.allclose(x,w,atol=1e-4,rtol=1e-4)
                row[mode+"_control_match"]=bool(matches);row[mode+"_responsive"]=bool(responsive);row[mode+"_restored"]=bool(restored)
                counts[mode+"_matching_observations"]+=int(matches)
                counts[mode+"_responsive_observations"]+=int(responsive)
                counts[mode+"_restored_observations"]+=int(restored)
            view_result["rows"].append(row)
        for mode in MODES:
            view_result[mode+"_lighting_delta"]=c.diff(finals["first",mode],finals["second",mode])
            view_result[mode+"_restore_delta"]=c.diff(finals["first",mode],finals["restored",mode])
            counts[mode+"_final_responsive_views"]+=int(view_result[mode+"_lighting_delta"]["different_over_1_div_255"]>0)
            counts[mode+"_final_restored_views"]+=int(view_result[mode+"_restore_delta"]["exactly_different"]==0)
        view_result["raw_vs_canonical_first"]=c.diff(finals["first","raw"],finals["first","canonical"])
        views.append(view_result)
    complete=all(counts[m+"_restored_observations"]==3*len(rows) and counts[m+"_final_restored_views"]==3 for m in MODES)
    return dict(status="OBSERVED_FORWARD_PASS_CONTEXT" if complete else "INCONCLUSIVE_FORWARD_PASS_RESTORE",
                source_tag_already_canonical=cfg["source_tag_already_canonical"],
                source_light_rows=len(rows),source_light_semantics=dict(Counter(r["semantic"] for r in rows)),
                counts=dict(counts),views=views,diagnostic_only=True,original_game_draw_verified=False,
                runtime_keyword_selection_verified=False,white_mesh_repair_verified=False)
