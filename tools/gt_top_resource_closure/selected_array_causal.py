"""Bounded private diagnostic of selected array sample versus final draw.
The tap is an intentionally modified shader. It never proves original-game
pixels, exact global bindings, runtime routes, or a production repair.
"""
import re
from pathlib import Path
import numpy as np
from scripts.gt_resource_register_contract import mask_noncode

MODE="_GTSelectedTapMode"
HIT=(.25,.5,.75,1.)
MISS=(.75,.5,.25,1.)
CAL=(.125,.375,.625,1.)
RED=(1.,0.,0.,1.)
GREEN=(0.,1.,0.,1.)
BASE_CASES=("override_source","override_red","override_green")
TAP_CASES=("tap_cal","tap_hit_source","tap_hit_red","tap_hit_green","tap_source","tap_red","tap_green")

class CausalError(ValueError): pass
def need(ok,code):
    if not ok:raise CausalError(code)

def matching(code,start,left,right):
    need(start<len(code) and code[start]==left,"tap_delimiter_anchor")
    depth=0
    for i in range(start,len(code)):
        if code[i]==left:depth+=1
        elif code[i]==right:
            depth-=1
            if depth==0:return i
    raise CausalError("tap_unclosed_delimiter")

def instrument(wrapper,prop):
    need(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}",prop) is not None,"tap_property_name")
    need(not any(x in wrapper for x in (MODE,"GTSelectedTapCapture","gt_selected_tap_")),
         "tap_authored_identifier_collision")
    code=mask_noncode(wrapper)
    ident=re.escape(prop)
    decl=re.findall(r"\bTexture2DArray\s*<\s*float4\s*>\s+"+ident+r"\s*;",code)
    need(len(decl)==1,"tap_array_declaration_anchor")
    calls=list(re.finditer(r"\b"+ident+r"\s*\.\s*([A-Za-z_]\w*)\s*\(",code))
    need(0<len(calls)<=64,"tap_sample_population")
    spans=[]
    for m in calls:
        need(m[1] in ("Sample","SampleLevel","SampleBias","SampleGrad","Load","Gather","GatherRed","GatherGreen","GatherBlue","GatherAlpha"),"tap_unsupported_array_method")
        end=matching(code,m.end()-1,"(",")")+1
        need(not spans or m.start()>=spans[-1][1],"tap_nested_array_call")
        spans.append((m.start(),end))
    for lo,hi in reversed(spans):
        wrapper=wrapper[:lo]+"GTSelectedTapCapture("+wrapper[lo:hi]+")"+wrapper[hi:]
    code=mask_noncode(wrapper)
    entries=list(re.finditer(r"\b([A-Za-z_]\w*)\s+gt_fs_main\s*\([^;{}]*\)\s*(?::\s*SV_Target0?)?\s*\{",code))
    need(len(entries)==1,"tap_fragment_entry_anchor")
    entry=entries[0];start=entry.end()-1;end=matching(code,start,"{","}")
    output=entry[1]
    body=wrapper[start+1:end]
    clean=mask_noncode(body)
    returns=list(re.finditer(r"\breturn\s+([A-Za-z_]\w*)\s*;",clean))
    need(len(returns)==1 and len(re.findall(r"\breturn\b",clean))==1,"tap_fragment_return_anchor")
    ret=returns[0]
    # SPIRV-Cross emits a named struct output with SV_Target0. A plain
    # float4 entry is also supported, but never guess a multi-target field.
    if output=="float4":
        lhs=ret[1]
    else:
        structures=list(re.finditer(r"\bstruct\s+"+re.escape(output)+r"\s*\{([^{}]*)\}\s*;",code))
        need(len(structures)==1,"tap_fragment_output_structure")
        fields=re.findall(r"\bfloat4\s+([A-Za-z_]\w*)\s*:\s*SV_Target0?\s*;",structures[0][1],re.I)
        need(len(fields)==1 and len(re.findall(r":\s*SV_Target\d*",structures[0][1],re.I))==1,"tap_fragment_target_anchor")
        lhs=ret[1]+"."+fields[0]
    value=("("+MODE+">1.5 ? float4(0.125,0.375,0.625,1.0) : "
           "("+MODE+"<0.5 ? (gt_selected_tap_hit>0.5 ? float4(0.25,0.5,0.75,1.0) : float4(0.75,0.5,0.25,1.0)) : "
           "(gt_selected_tap_hit>0.5 ? gt_selected_tap_value : float4(0.75,0.5,0.25,1.0))))")
    body=(" \n gt_selected_tap_hit=0.0; gt_selected_tap_value=float4(0,0,0,0);\n"+
          body[:ret.start()]+lhs+"="+value+";\n"+body[ret.start():])
    wrapper=wrapper[:start+1]+body+wrapper[end:]
    anchor="#pragma fragment gt_fs_main\n"
    need(wrapper.count(anchor)==1,"tap_pragma_anchor")
    helper=("float "+MODE+";\nstatic float4 gt_selected_tap_value;\nstatic float gt_selected_tap_hit;\n"
            "float4 GTSelectedTapCapture(float4 v) { gt_selected_tap_value=v; gt_selected_tap_hit=1.0; return v; }\n")
    wrapper=wrapper.replace(anchor,anchor+helper,1)
    return wrapper,len(spans)

def stage_tap(root,parsed,passes,wrapper,prop,shader_factory):
    from scripts.gt_original_921_shaderlab import verify_entrypoints
    from hashlib import sha256
    try:
        tap,count=instrument(wrapper,prop)
        verify_entrypoints(tap,root,routes=[[[]]])
        raw,_=shader_factory(parsed,passes,tap,diagnostic=True)
        (root/"array-tap-shader.bytes").write_bytes(raw)
        return {"tap_available":True,"tap_shader_sha":sha256(raw).hexdigest(),
                "tap_source_sample_sites":count,"tap_stage_status":"PREPARED"}
    except CausalError as exc:
        return {"tap_available":False,"tap_stage_status":str(exc)}
    except Exception as exc:
        # Never print compiler messages or source identifiers.
        return {"tap_available":False,"tap_stage_status":"tap_compile_or_layout_unproven",
                "tap_failure_type":type(exc).__name__}

def diff(a,b):
    need(a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all(),"causal_pixel_schema")
    delta=np.max(np.abs(a-b),axis=-1)
    return {"exactly_different":int(np.count_nonzero(delta>0)),
            "different_over_1_div_255":int(np.count_nonzero(delta>1/255))}

def near(a,value):
    return np.max(np.abs(a-np.asarray(value,dtype=np.float32)),axis=-1)<=1/255

def summarize(pixels,base,tap):
    need(set(pixels)==set(BASE_CASES+(TAP_CASES if tap else ())),"causal_pixel_population")
    out={"override_source_vs_saved":diff(pixels["override_source"],base),
         "original_red_vs_green":diff(pixels["override_red"],pixels["override_green"]),
         "tap_calibrated":False}
    if not tap:return out
    cal=near(pixels["tap_cal"],CAL)
    masks={name:near(pixels["tap_hit_"+name],HIT)&cal for name in ("source","red","green")}
    misses={name:near(pixels["tap_hit_"+name],MISS)&cal for name in ("source","red","green")}
    both=masks["red"]&masks["green"]
    red_ok=near(pixels["tap_red"],RED)&both
    green_ok=near(pixels["tap_green"],GREEN)&both
    expected=red_ok&green_ok
    n=int(both.sum())
    out.update(calibration_pixels=int(cal.sum()),sample_hit_pixels={k:int(v.sum()) for k,v in masks.items()},
               sample_miss_pixels={k:int(v.sum()) for k,v in misses.items()},
               shared_authored_sample_hit_pixels=n,authored_sample_color_matches=int(expected.sum()),
               source_sample_hit_pixels=int(masks["source"].sum()),
               tap_calibrated=n>0 and int(expected.sum())==n,
               all_visible_marker_fragments_miss=bool(cal.any()) and all(np.array_equal(v,cal) for v in misses.values()))
    return out

def classify(rows):
    valid=[r for r in rows if r["override_source_vs_saved"]["different_over_1_div_255"]==0]
    calibrated=[r for r in valid if r["tap_calibrated"]]
    responsive=[r for r in valid if r["original_red_vs_green"]["different_over_1_div_255"]>0]
    if responsive:
        kind="ORIGINAL_CANDIDATE_RESPONDS_TO_AUTHORED_ARRAY_SUBSTITUTION"
    elif calibrated:
        kind="INSTRUMENTED_SAMPLE_CALIBRATED_FINAL_CANDIDATE_INSENSITIVE_IN_TEST_SCENE"
    elif any(r.get("all_visible_marker_fragments_miss") for r in valid):
        kind="TAP_MARKER_OBSERVED_NO_SAMPLE_AT_VISIBLE_FRAGMENTS_IN_TEST_VIEW"
    else:
        kind="INCONCLUSIVE_SAMPLE_CAUSALITY"
    return {"status":kind,"override_source_matches_saved_views":len(valid),
            "calibrated_tap_views":len(calibrated),"original_authored_substitution_responsive_views":len(responsive),
            "diagnostic_only":True,"original_game_global_resources_verified":False}
