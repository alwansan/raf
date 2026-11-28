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
def compose(sources,switches,routes):
    rows=route_rows(switches,routes);parts=[split(s) for s in sources]
    need(len(parts)==4 and all((x[0],x[2])==(parts[0][0],parts[0][2]) for x in parts),"envelope")
    clauses=[dict(enabled=x["enabled"],program=x["index"]) for x in rows]
    code=routed_stage(clauses,switches,{i:x[1] for i,x in enumerate(parts)})
    need(code.count("#error Unmapped_original_keyword_set")==1,"no_fallback")
    return parts[0][0]+"HLSLPROGRAM\n"+"\n".join((*PRAGMAS,*("#pragma multi_compile __ "+x for x in switches),code))+"\nENDHLSL"+parts[0][2],rows
def marker(switches,rows):
    code=routed_stage([dict(enabled=x["enabled"],program=x["index"]) for x in rows],switches,
        {i:"return float4(%s,.375,.625,1);"%((i+1)/8) for i in range(4)})
    return """Shader "Hidden/GTParticleRouteMarker" {
SubShader { Pass { Cull Off ZWrite Off ZTest Always Blend Off ColorMask RGBA
CGPROGRAM
#pragma vertex vert
#pragma fragment frag
"""+ "\n".join("#pragma multi_compile __ "+x for x in switches)+"""
#include "UnityCG.cginc"
float4 vert(float4 p:POSITION):SV_POSITION { return UnityObjectToClipPos(p); }
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
        (folder/f"explicit-{i}.shader").write_text('Shader "Hidden/GTParticleExplicit%d" {'%i+s[len(old):])
    (folder/"marker.shader").write_text(marker(switches,rows))
    out["keyword_candidate_stage"]=dict(original_routes=4,paired_entrypoints_validated=8,original_switches=2,strict_no_route_fallback=True,original_keyword_scope_verified=False)
    return candidate.encode(),dict(switches=list(switches),selected=selected,rows=[dict(index=r["index"],bits=r["bits"]) for r in rows])
def different(a,b):
    return int(np.count_nonzero(np.max(np.abs(a-b),axis=-1)>TOL))
def classify(clear,actual,rows,selected):
    need(set(rows)==set(range(4)) and selected in rows,"readback_population")
    clear_ok=different(clear,BG)==0
    data=[]
    for i,(route,explicit,mark) in sorted(rows.items()):
        color=np.array([(i+1)/8,.375,.625,1])
        mask=np.max(np.abs(mark-color),axis=-1)<=TOL
        marker_ok=int(mask.sum())>=4 and different(mark[~mask],BG)==0 if (~mask).any() else int(mask.sum())>=4
        data.append(dict(index=i,marker_pixels=int(mask.sum()),marker_verified=bool(marker_ok),
                         routed_explicit_difference_pixels=different(route,explicit),
                         routed_visible_pixels=different(route,clear),
                         routed_alpha_preserved=bool(np.max(np.abs(route[...,3]-clear[...,3]))<=TOL)))
    selected_delta=different(actual,rows[selected][0])
    alternatives=sum(different(actual,rows[i][0])>0 for i in rows if i!=selected)
    ok=clear_ok and selected_delta==0 and different(actual,clear)>0 and all(x["marker_verified"] and x["routed_explicit_difference_pixels"]==0 and x["routed_alpha_preserved"] for x in data)
    return dict(clear_verified=clear_ok,selected_saved_material_delta_pixels=selected_delta,selected_visible_pixels=different(actual,clear),
                selected_distinct_alternatives=alternatives,cases=data,route_probe_verified=bool(ok))
def verify(root,cfg):
    selected=cfg["selected"];need(type(selected) is int and 0<=selected<4,"selected_route")
    results=[];failures=[]
    for i in range(12):
        try:
            j=json.loads((root/f"route-{i}.json").read_text())
            need(j.get("index")==i and j.get("completed") is True and j.get("saved_keywords_match") is True and j.get("material_properties_match") is True and j.get("source_keywords_unchanged") is True and j.get("submissions")==14,"editor_route_receipt")
            def r(name):return read_pixels(root/f"route-{i}-{name}.f32",SIZE)
            result=classify(r("clear"),r("actual"),{k:(r(f"routed-{k}"),r(f"explicit-{k}"),r(f"marker-{k}")) for k in range(4)},selected)
            results.append(dict(index=i,**result))
        except Reject as e:failures.append(dict(index=i,reason=str(e)))
        except Exception as e:failures.append(dict(index=i,failure_type=type(e).__name__))
    return dict(observed_meshes=len(results),verified_meshes=sum(x["route_probe_verified"] for x in results),
                distinct_selected_meshes=sum(x["selected_distinct_alternatives"]>0 for x in results),
                isolated_saved_keyword_candidate_verified=len(results)==12 and all(x["route_probe_verified"] for x in results),
                original_keyword_scope_verified=False,original_game_runtime_keyword_selection_verified=False,
                diagnostic_marker_shader_only=True,cases=results,failures=failures)
