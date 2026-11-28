"""Diagnostic actual generated mesh GPU vertex input vs CPU payload, not original shader execution."""
import json
from pathlib import Path
import numpy as np

SIZE=16
CLEAR=np.array([-19,-23,-29,-31],dtype=np.float32)
MARKER=np.array([.125,.375,.625,1],dtype=np.float32)
DEFAULT=np.array([0,0,0,1],dtype=np.float32)
class Reject(ValueError):pass
def need(ok,reason):
    if not ok:raise Reject(reason)
def signature(req):
    need(type(req) is list and len(req)==3,"signature_population")
    seen=set();out=[]
    for r in req:
        s=r["semantic"];i=r["index"];mask=r["mask"];used=r["used_mask"]
        need(s in ("POSITION","NORMAL","TANGENT","COLOR","TEXCOORD") and type(i) is int and (i==0 or s=="TEXCOORD" and 0<=i<=7),"semantic")
        need(r["component_type"]==3 and type(mask) is int and 1<=mask<=15 and type(used) is int and 0<=used<=15 and not used&~mask,"signature_mask_type")
        need((s,i) not in seen,"duplicate_semantic");seen.add((s,i))
        out.append((s,i,used or mask))
    return out

def shader(req):
    rows=signature(req)
    fields="\n".join(f"float4 a{n}:{s}{i};" for n,(s,i,_) in enumerate(rows))
    branches="\n".join(f"if (_GTInputIndex=={n}.0) o.v=a.a{n};" for n in range(len(rows)))
    return """Shader "Hidden/GTEmitterLaneProbe" {
Properties { _GTInputIndex ("Input index", Float) = -1 }
SubShader { Pass {
Cull Off ZWrite Off ZTest Always Blend Off ColorMask RGBA
HLSLPROGRAM
#pragma target 5.0
#pragma vertex vert
#pragma fragment frag
float _GTInputIndex;
struct A {
"""+fields+"""
uint id:SV_VertexID;
};
struct V { float4 pos:SV_POSITION; nointerpolation float4 v:TEXCOORD0; };
V vert(A a) {
 V o;
 float2 xy=float2((a.id&1u)!=0u?0.75:-0.75,(a.id&2u)!=0u?0.75:-0.75);
 o.pos=float4(xy,0.5,1);
 o.v=float4(.125,.375,.625,1);
"""+branches+"""
 return o;
}
float4 frag(V v):SV_Target { return v.v; }
ENDHLSL
} }
Fallback Off
}
"""

def read(path):
    need(path.is_file() and path.stat().st_size==SIZE*SIZE*16,"pixel_extent")
    p=np.fromfile(path,dtype="<f4").reshape(-1,4)
    need(np.isfinite(p).all(),"nonfinite_pixels")
    return p
def close(a,b):
    return np.isclose(a,b,rtol=1e-5,atol=2e-5)
def coverage(marker):
    visible=np.all(close(marker,MARKER),axis=-1)
    need(int(visible.sum())>=16 and np.all(np.all(close(marker[~visible],CLEAR),axis=-1)),"marker_calibration")
    return visible
def classify(cpu,width,mask,pixels):
    need(cpu.shape==(4,4) and np.isfinite(cpu).all() and 1<=width<=4 and 1<=mask<=15 and pixels.ndim==2 and pixels.shape[1]==4 and len(pixels)>0,"lane_input")
    # nointerpolation: each covered fragment must match a single source vertex
    # on all physically supplied components. Default fill assessed separately.
    physical=np.all(close(pixels[:,None,:width],cpu[None,:,:width]),axis=-1).any(axis=-1)
    missing=[i for i in range(width,4) if mask&(1<<i)]
    defaults=[int(np.count_nonzero(close(pixels[:,i],DEFAULT[i]))) for i in missing]
    return dict(width=width,required_mask=mask,used_lanes_missing=len(missing),physical_pixels_matching=int(physical.sum()),
        coverage_pixels=len(pixels),missing_default_lanes_matched=sum(x==len(pixels) for x in defaults),
        physical_values_match=bool(physical.all()),used_missing_defaults_match=all(x==len(pixels) for x in defaults))

def inspect(root,index,req):
    path=root/f"lane-{index}.json"
    need(path.is_file() and path.stat().st_size<=65536,"private_probe_receipt")
    j=json.loads(path.read_text())
    need(j.get("index")==index and j.get("completed") is True and j.get("vertices")==4 and j.get("indices")==6,"probe_editor_incomplete")
    lanes=j.get("lanes")
    need(type(lanes) is list and len(lanes)==3 and {x.get("index") for x in lanes}==set(range(3)),"lane_population")
    vis=coverage(read(root/f"lane-{index}--1.f32"))
    result=[]
    for lane in sorted(lanes,key=lambda x:x["index"]):
        i=lane["index"];w=lane["width"];fmt=lane["format"]
        need(type(w) is int and 1<=w<=4 and type(fmt) is int and 0<=fmt<=32,"lane_schema")
        cpu=np.array([[x[k] for k in ("x","y","z","w")] for x in lane["cpu"]],dtype=np.float32)
        data=read(root/f"lane-{index}-{i}.f32")
        need(np.all(np.all(close(data[~vis],CLEAR),axis=-1)),"outside_marker_changed")
        r=classify(cpu,w,req[i][2],data[vis])
        result.append(dict(index=i,format=fmt,**r))
    return dict(index=index,coverage_pixels=int(vis.sum()),lanes=result,all_physical_values_match=all(x["physical_values_match"] for x in result),
                all_used_defaults_match=all(x["used_missing_defaults_match"] for x in result))

def verify(root,requirements,control_completed):
    req=signature(requirements)
    results=[];failures=[]
    for i in range(-1,12):
        try:results.append(inspect(root,i,req))
        except Reject as e:failures.append(dict(index=i,reason=str(e)))
        except Exception as e:failures.append(dict(index=i,type=type(e).__name__))
    control=next((x for x in results if x["index"]==-1),None)
    original=[x for x in results if x["index"]>=0]
    control_ok=bool(control_completed and control and control["all_physical_values_match"] and control["all_used_defaults_match"])
    physical=sum(x["all_physical_values_match"] for x in original)
    defaults=sum(x["all_used_defaults_match"] for x in original)
    return dict(control_verified=control_ok,actual_meshes_observed=len(original),physical_values_match_cases=physical,used_missing_default_match_cases=defaults,
                gpu_vertex_lane_probe_verified=control_ok and len(original)==12 and physical==defaults==12,
                original_shader_execution_verified=False,vertexid_diagnostic_placement=True,original_mesh_payload_modified=False,
                cases=results,failures=failures)
