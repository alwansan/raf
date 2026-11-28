"""Private four-route candidate and independent actual mesh draw classifier.
Only aggregate observations are public. Keyword flag scope is provisional.
"""
import json
import re
from pathlib import Path
import numpy as np
from scripts.gt_original_921_shaderlab import verify_entrypoints
from scripts.gt_original_921_keyword_routes import routed_stage
from scripts.w1_depth_shaderlab import quoted
from tools.gt_particle108_native_route.draw import read_pixels
SIZE=64
TOL=1/255
BG=np.array([.125,.25,.5,.25])
PRAGMAS=("#pragma target 5.0","#pragma vertex gt_vs_main","#pragma fragment gt_fs_main")
class Reject(ValueError):pass
def need(ok,code):
    if not ok:raise Reject(code)
def route_rows(switches,routes):
    need(len(switches)==2 and len(set(switches))==2 and all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",x) for x in switches),"switches")
    need(set(routes)=={(0,0),(0,1),(1,0),(1,1)} and set(routes.values())==set(range(4)),"route_lattice")
    return [dict(index=n,bits=list(bits),enabled=[k for k,b in zip(switches,bits) if b]) for bits,n in sorted(routes.items(),key=lambda x:x[1])]
def split(source):
    a=source.split("HLSLPROGRAM\n");need(len(a)==2,"program_start")
    b=a[1].split("\nENDHLSL");need(len(b)==2,"program_end")
    code=b[0].splitlines();need(tuple(x for x in code if x.startswith("#pragma"))==PRAGMAS,"entrypoint_pragmas")
    return a[0],"\n".join(x for x in code if not x.startswith("#pragma")),b[1]
def switch_pragmas(switches):
    return tuple("#pragma multi_compile_instancing" if x=="INSTANCING_ON" else "#pragma multi_compile __ "+x for x in switches)
def compose(sources,switches,routes):
    rows=route_rows(switches,routes);parts=[split(s) for s in sources]
    need(len(parts)==4 and all((x[0],x[2])==(parts[0][0],parts[0][2]) for x in parts),"envelope")
    clauses=[dict(enabled=x["enabled"],program=x["index"]) for x in rows]
    code=routed_stage(clauses,switches,{i:x[1] for i,x in enumerate(parts)})
    need(code.count("#error Unmapped_original_keyword_set")==1,"no_fallback")
    return parts[0][0]+"HLSLPROGRAM\n"+"\n".join((*PRAGMAS,*switch_pragmas(switches),code))+"\nENDHLSL"+parts[0][2],rows
def marker(switches,rows):
    code=routed_stage([dict(enabled=x["enabled"],program=x["index"]) for x in rows],switches,
        {i:"return float4(%s,.375,.625,1);"%((i+1)/8) for i in range(4)})
    return """Shader "Hidden/GTParticleRouteMarker" {
SubShader { Pass { Cull Off ZWrite Off ZTest Always Blend Off ColorMask RGBA
CGPROGRAM
#pragma target 4.5
#pragma vertex vert
#pragma fragment frag
"""+ "\n".join(switch_pragmas(switches))+"""
#include "UnityCG.cginc"
struct appdata { float4 p:POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
float4 vert(appdata v):SV_POSITION { UNITY_SETUP_INSTANCE_ID(v); return UnityObjectToClipPos(v.p); }
float4 frag():SV_Target {
"""+code+"""
}
ENDCG
} }
Fallback Off
}
"""
def stage(parsed,table,pairs,switches,routes,selected,private,project,out,make_shader):
    need(len(pairs)==4 and selected in range(4),"pair_population")
    need(set(switches)=={"SOFTPARTICLES_ON","INSTANCING_ON"},"unexpected_engine_switch_scope")
    instancing_index=switches.index("INSTANCING_ON")
    sources=[]
    for i in range(4):
        p=private/str(i);p.mkdir()
        sources.append(make_shader(parsed,table,pairs[i],p,{}).decode("utf-8"))
    candidate,rows=compose(sources,switches,routes)
    verify_entrypoints(candidate,private,routes=[[x["enabled"] for x in rows]])
    folder=project/"Assets/GTKeywordDiagnostic";folder.mkdir(parents=True)
    old="Shader "+quoted(parsed["m_Name"])+" {"
    for i,s in enumerate(sources):
        need(s.startswith(old),"original_shader_name_anchor")
        reference='Shader "Hidden/GTParticleExplicit%d" {'%i+s[len(old):]
        if rows[i]["bits"][instancing_index]:
            need(reference.count("#pragma target 5.0")==1,"reference_pragma_anchor")
            reference=reference.replace("#pragma target 5.0","#pragma target 5.0\n#pragma multi_compile_instancing")
        (folder/f"explicit-{i}.shader").write_text(reference)
    (folder/"marker.shader").write_text(marker(switches,rows))
    out["keyword_candidate_stage"]=dict(original_routes=4,paired_entrypoints_validated=8,original_switches=2,strict_no_route_fallback=True,engine_instancing_pragma=True,original_keyword_scope_verified=False)
    return candidate.encode(),dict(switches=list(switches),selected=selected,instancing_index=instancing_index,rows=[dict(index=r["index"],bits=r["bits"]) for r in rows])
def different(a,b):
    return int(np.count_nonzero(np.max(np.abs(a-b),axis=-1)>TOL))
def classify(clear,actual,rows,selected,*,instanced_routes=(),instanced_nonsoft=None):
    need(set(rows)==set(range(4)) and selected in rows and selected not in instanced_routes,"readback_population")
    clear_ok=different(clear,BG)==0
    data=[]
    for i,(route,explicit,mark) in sorted(rows.items()):
        color=np.array([(i+1)/8,.375,.625,1])
        mask=np.max(np.abs(mark-color),axis=-1)<=TOL
        marker_ok=int(mask.sum())>=4 and (not (~mask).any() or different(mark[~mask],BG)==0)
        visible=np.max(np.abs(route[...,:3]-clear[...,:3]),axis=-1)>TOL
        left=int(mask[:,:SIZE//2].sum());right=int(mask[:,SIZE//2:].sum())
        overlap=mask&visible
        left_visible=int(overlap[:,:SIZE//2].sum());right_visible=int(overlap[:,SIZE//2:].sum())
        is_instanced=i in instanced_routes
        two_lobes=bool(is_instanced and marker_ok and left>=4 and right>=4 and not mask[:,SIZE//2-1:SIZE//2+1].any())
        if is_instanced:marker_ok=two_lobes
        data.append(dict(index=i,instanced_draw=is_instanced,marker_pixels=int(mask.sum()),marker_verified=bool(marker_ok),
                         marker_left_pixels=left,marker_right_pixels=right,instanced_marker_two_lobes=two_lobes,
                         routed_explicit_difference_pixels=different(route,explicit),routed_visible_pixels=int(visible.sum()),
                         visible_marker_left_pixels=left_visible,visible_marker_right_pixels=right_visible,
                         routed_alpha_preserved=bool(np.max(np.abs(route[...,3]-clear[...,3]))<=TOL)))
    selected_delta=different(actual,rows[selected][0])
    # Instanced cases use a different camera framing; never count that as a
    # distinguishing pixel alternative to the saved single-draw material.
    normal_alternatives=[i for i in rows if i!=selected and i not in instanced_routes]
    alternatives=sum(different(actual,rows[i][0])>0 for i in normal_alternatives)
    instance_data=[x for x in data if x["instanced_draw"]]
    instance_marker_ok=bool(instance_data and all(x["instanced_marker_two_lobes"] for x in instance_data))
    instance_equal=bool(instance_data and all(x["routed_explicit_difference_pixels"]==0 and x["routed_alpha_preserved"] for x in instance_data))
    nonsoft_visible=bool(instanced_nonsoft is not None and any(x["index"]==instanced_nonsoft and x["visible_marker_left_pixels"]>0 and x["visible_marker_right_pixels"]>0 for x in instance_data))
    ok=clear_ok and selected_delta==0 and different(actual,clear)>0 and all(x["marker_verified"] and x["routed_explicit_difference_pixels"]==0 and x["routed_alpha_preserved"] for x in data)
    if instance_data:ok=ok and instance_marker_ok and instance_equal and nonsoft_visible
    return dict(clear_verified=clear_ok,selected_saved_material_delta_pixels=selected_delta,selected_visible_pixels=different(actual,clear),
                selected_distinct_alternatives=alternatives,normal_alternatives_compared=len(normal_alternatives),
                engine_instancing_marker_verified=instance_marker_ok,instanced_reference_pixel_parity=instance_equal,
                instanced_nonsoft_visible_both_lobes=nonsoft_visible,cases=data,route_probe_verified=bool(ok))
PHASES=("start","configuration","saved_keywords","camera","clear","actual","marker_shader","routed_material","routed_keywords","routed_draw","reference_shader","reference_properties","reference_draw","marker_keywords","marker_draw","post_draw","complete","permutation_incomplete")
EXCEPTIONS=("","InvalidOperationException","ArgumentException","IOException","NullReferenceException","UnityException","IndexOutOfRangeException")
KEYWORD_CATEGORIES=("instancing","fog","soft_particles","stereo","lighting","unity_reserved","other")
def safe_attempt(x):
    if type(x) is not dict:return None
    masks=("requested_mask","engine_mask","expected_mask","before_string_mask","before_local_mask","after_string_mask","after_local_mask","after_enabled_list_mask","global_mask")
    out={k:x[k] if type(x.get(k)) is int and 0<=x[k]<=3 else -1 for k in masks}
    out["declared"]=x["declared"] if type(x.get("declared")) is int and 0<=x["declared"]<=2 else -1
    out["attempted"]=x.get("attempted") is True
    out["failure_category"]=x.get("failure_category") if x.get("failure_category") in EXCEPTIONS else "other"
    out["matched"]=bool(x.get("matched") is True and out["attempted"] and out["failure_category"]=="" and out["declared"]==2 and out["requested_mask"]>=0 and out["engine_mask"] in (1,2) and out["expected_mask"]==(out["requested_mask"]&~out["engine_mask"]) and out["global_mask"]==0 and
        out["after_string_mask"]==out["after_local_mask"]==out["after_enabled_list_mask"]==out["expected_mask"])
    return out
def safe_receipt(j,index):
    need(type(j) is dict and j.get("index")==index,"receipt_identity")
    def bounded(x,k,lo,hi):
        v=x.get(k)
        return v if type(v) is int and lo<=v<=hi else -1
    def state(x):
        return dict(phase=x.get("phase") if x.get("phase") in PHASES else "other",
                    failure_category=x.get("failure_category") if x.get("failure_category") in EXCEPTIONS else "other")
    flags=("completed","saved_keywords_match","material_properties_match","source_keywords_unchanged","source_global_keywords_unchanged","source_instancing_unchanged","device_instancing_supported")
    counts=("source_declared_switches","source_enabled_switches","source_expected_enabled_switches","source_local_bit_matches","source_string_bit_matches","source_overridable_switches","source_global_enabled_switches","source_global_override_conflicts")
    out=dict(index=index,**state(j),submissions=bounded(j,"submissions",0,14),marker_shader_errors=bounded(j,"marker_shader_errors",-1,1000),
             **{k:j.get(k) is True for k in flags},**{k:bounded(j,k,0,2) for k in counts})
    cats=j.get("switch_categories")
    out["switch_categories"]=[v if v in KEYWORD_CATEGORIES else "other" for v in cats] if type(cats) is list and len(cats)==2 else []
    out["source_instancing_enabled"]=j.get("source_instancing_enabled") is True
    variants=j.get("variants")
    if type(variants) is not list:variants=[]
    need(len(variants)<=4 and all(type(x) is dict and type(x.get("index")) is int and 0<=x["index"]<4 for x in variants)
         and len({x["index"] for x in variants})==len(variants),"variant_receipt_population")
    vf=("completed","routed_bits_match","marker_bits_match","copy_properties_match","reference_properties_match","routed_properties_match","typed_copy_needed","routed_drawn","reference_drawn","marker_drawn")
    out["variants"]=[dict(index=x["index"],**state(x),submissions=bounded(x,"submissions",0,3),
                           reference_shader_errors=bounded(x,"reference_shader_errors",-1,1000),
                           marker_shader_errors=bounded(x,"marker_shader_errors",-1,1000),**{k:x.get(k) is True for k in vf}) for x in variants]
    for raw,v in zip(variants,out["variants"]):
        v["instanced_draw"]=raw.get("instanced_draw") is True
        v["draw_instance_count"]=bounded(raw,"draw_instance_count",1,2)
        for role in ("routed","reference","marker"):
            phase=raw.get(role+"_phase")
            failure=raw.get(role+"_failure")
            v[role+"_phase"]=phase if phase in PHASES else "other"
            v[role+"_failure"]=failure if failure in EXCEPTIONS else "other"
        for role in ("routed","marker"):
            v[role+"_keyword_attempt"]=safe_attempt(raw.get(role+"_keyword_attempt"))
    out["strict_editor_receipt"]=bool(all(out[k] for k in flags) and out["submissions"]==14 and out["source_declared_switches"]==out["source_local_bit_matches"]==out["source_string_bit_matches"]==2
         and out["source_global_override_conflicts"]==0 and len(out["switch_categories"])==2 and len(variants)==4 and all(x["completed"] and x["submissions"]==3 and x["routed_bits_match"] and x["marker_bits_match"] and x["reference_properties_match"] and x["routed_properties_match"] and x["reference_shader_errors"]==x["marker_shader_errors"]==0 and x["draw_instance_count"]==(2 if x["instanced_draw"] else 1) and all(x[role+"_drawn"] for role in ("routed","reference","marker")) and all(x[role+"_keyword_attempt"] is not None and x[role+"_keyword_attempt"]["matched"] for role in ("routed","marker")) for x in out["variants"]))
    return out

def verify(root,cfg):
    selected=cfg["selected"];need(type(selected) is int and 0<=selected<4,"selected_route")
    instancing_index=cfg["instancing_index"];need(type(instancing_index) is int and instancing_index in (0,1) and cfg["switches"][instancing_index]=="INSTANCING_ON","instancing_scope")
    engine_mask=1<<instancing_index
    expected={x["index"]:x["bits"][0]+2*x["bits"][1] for x in cfg["rows"]}
    need(set(expected)==set(range(4)) and set(expected.values())==set(range(4)) and not (expected[selected]&engine_mask),"route_config")
    instanced={i for i,m in expected.items() if m&engine_mask};nonsoft=next(i for i in instanced if expected[i]==engine_mask)
    results=[];failures=[];receipts=[]
    for i in range(12):
        try:
            j=json.loads((root/f"route-{i}.json").read_text())
            rec=safe_receipt(j,i);receipts.append(rec)
            def r(name):return read_pixels(root/f"route-{i}-{name}.f32",SIZE)
            # Collect partial comparisons even if a permutation stopped.
            partial=[]
            clear=None;actual=None
            try:clear=r("clear");actual=r("actual")
            except Exception:pass
            for v in rec["variants"]:
                n=v["index"];p=dict(index=n)
                images={}
                for role in ("routed","explicit","marker"):
                    try:images[role]=r(f"{role}-{n}");p[role+"_pixels_read"]=True
                    except Exception as e:p[role+"_readback_failure_type"]=type(e).__name__
                if "routed" in images:
                    x=images["routed"]
                    if clear is not None:p["visible_pixels"]=different(x,clear)
                    if actual is not None:p["actual_difference_pixels"]=different(x,actual)
                    if "explicit" in images:p["routed_explicit_difference_pixels"]=different(x,images["explicit"])
                if "explicit" in images and clear is not None:p["explicit_visible_pixels"]=different(images["explicit"],clear)
                if "marker" in images:
                    col=np.array([(n+1)/8,.375,.625,1]);p["marker_pixels"]=int((np.max(np.abs(images["marker"]-col),axis=-1)<=TOL).sum())
                partial.append(p)
            rec["partial_readbacks"]=partial
            # Independently bind each measured mask to the private source-derived route table.
            rec["route_masks_match"]=len(rec["variants"])==4 and all(v["instanced_draw"]==(v["index"] in instanced) and all(v[role+"_keyword_attempt"] is not None and v[role+"_keyword_attempt"]["requested_mask"]==expected[v["index"]] and v[role+"_keyword_attempt"]["engine_mask"]==engine_mask and v[role+"_keyword_attempt"]["expected_mask"]==(expected[v["index"]]&~engine_mask) for role in ("routed","marker")) for v in rec["variants"])
            if not rec["strict_editor_receipt"] or not rec["route_masks_match"]:
                failures.append(dict(index=i,reason="editor_route_receipt",phase=rec["phase"]));continue
            result=classify(r("clear"),r("actual"),{n:(r(f"routed-{n}"),r(f"explicit-{n}"),r(f"marker-{n}")) for n in range(4)},selected,instanced_routes=instanced,instanced_nonsoft=nonsoft)
            results.append(dict(index=i,**result))
        except Reject as e:failures.append(dict(index=i,reason=str(e)))
        except Exception as e:failures.append(dict(index=i,failure_type=type(e).__name__))
    return dict(observed_meshes=len(results),verified_meshes=sum(x["route_probe_verified"] for x in results),
                distinct_selected_meshes=sum(x["selected_distinct_alternatives"]>0 for x in results),
                engine_instancing_marker_meshes=sum(x["engine_instancing_marker_verified"] for x in results),
                instanced_reference_parity_meshes=sum(x["instanced_reference_pixel_parity"] for x in results),
                instanced_nonsoft_visible_meshes=sum(x["instanced_nonsoft_visible_both_lobes"] for x in results),
                isolated_saved_keyword_candidate_verified=len(results)==12 and all(x["route_probe_verified"] for x in results),
                original_keyword_scope_verified=False,original_game_runtime_keyword_selection_verified=False,
                diagnostic_marker_shader_only=True,cases=results,editor_receipts=receipts,failures=failures)
