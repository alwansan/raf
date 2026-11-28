"""Actual particle renderer and unchanged baked geometry draw observations.
Both paths use the same restored explicit original route, independently framed.
No full scene, runtime keyword, phone or alpha-causality admission.
"""
import json
import numpy as np
from tools.gt_particle108_native_route.draw import read_pixels

SIZE=64
TOL=1/255
BACKGROUNDS=(np.array([.125,.25,.5,.25]),np.array([.625,.375,.125,.75]))
MARKER=np.array([.91,.07,.61,1.])
PATHS=("renderer","baked")
MODES=("natural","forced")
CASES=("clear","native","repeat","marker")
PHASES=("start","frame","clear","native","repeat","marker","post_draw","complete")
EXCEPTIONS=("","InvalidOperationException","ArgumentException","IOException","NullReferenceException","UnityException")
class Reject(ValueError):pass
def need(ok,code):
    if not ok:raise Reject(code)
def classify(rows,bg):
    need(set(rows)==set(CASES),"draw_cases")
    need(all(v.shape==(SIZE,SIZE,4) and np.isfinite(v).all() for v in rows.values()),"draw_pixels")
    def neq(a,b,rgb=False):
        if rgb:a,b=a[...,:3],b[...,:3]
        return np.max(np.abs(a-b),axis=-1)>TOL
    clear_ok=not neq(rows["clear"],BACKGROUNDS[bg]).any()
    marker=np.max(np.abs(rows["marker"]-MARKER),axis=-1)<=TOL
    native=neq(rows["native"],rows["clear"],True)
    repeat=neq(rows["native"],rows["repeat"],True)
    alpha=max(float(np.max(np.abs(rows[k][...,3]-rows["clear"][...,3]))) for k in ("native","repeat"))
    distinct=neq(rows["native"],rows["marker"],True)&native
    overlap=marker&native
    result=dict(clear_matches_background=bool(clear_ok),marker_pixels=int(marker.sum()),native_visible_pixels=int(native.sum()),
                native_distinct_from_marker_pixels=int(distinct.sum()),native_marker_overlap_pixels=int(overlap.sum()),
                native_outside_marker_pixels=int((native&~marker).sum()),repeat_rgb_difference_pixels=int(repeat.sum()),
                source_rgb_mask_alpha_preserved=alpha<=TOL)
    result["calibrated_original_rgb_observed"]=bool(clear_ok and marker.sum()>=4 and overlap.any() and distinct.any() and not repeat.any() and alpha<=TOL)
    return result

def inspect(root,index,mode,expected):
    j=json.loads((root/f"emitter-{index}-{mode}.json").read_text())
    need(j.get("index")==index and j.get("mode")==mode,"draw_identity")
    n=expected.get("particles")
    need(type(n) is int and 0<n<=256 and expected.get("vertices")==4*n and expected.get("indices")==6*n
         and j.get("particles")==n and j.get("vertices")==4*n and j.get("indices")==6*n,"draw_same_bake_geometry")
    paths=j.get("paths")
    need(type(paths) is list and len(paths)==2 and {x.get("path") for x in paths}==set(PATHS),"draw_path_population")
    result=[]
    for r in paths:
        path=r["path"]
        safe=dict(path=path,phase=r.get("phase") if r.get("phase") in PHASES else "other",
                  failure_category=r.get("failure_category") if r.get("failure_category") in EXCEPTIONS else "other",
                  submissions=r.get("submissions") if type(r.get("submissions")) is int and 0<=r["submissions"]<=8 else 0,
                  completed=r.get("completed") is True,material_restored=r.get("material_restored") is True,
                  streams_unchanged=r.get("streams_unchanged") is True,particles_unchanged=r.get("particles_unchanged") is True,
                  backgrounds=[])
        for bg in range(2):
            try:
                rows={k:read_pixels(root/f"emitter-{index}-{mode}-{path}-{bg}-{k}.f32",SIZE) for k in CASES}
                safe["backgrounds"].append(dict(background=bg,**classify(rows,bg)))
            except Exception as e:
                safe["backgrounds"].append(dict(background=bg,failure_type=type(e).__name__))
        safe["path_verified"]=(safe["submissions"]==8 and all(safe[k] for k in ("completed","material_restored","streams_unchanged","particles_unchanged")) and all(x.get("calibrated_original_rgb_observed") is True for x in safe["backgrounds"]))
        result.append(safe)
    return dict(index=index,mode=mode,particles=n,vertices=4*n,indices=6*n,paths=result)

def verify(root,rows):
    need(type(rows) is list and len(rows)==12 and {x["index"] for x in rows}==set(range(12)),"actual_emitter_population")
    results=[];failures=[]
    for row in rows:
        for mode in MODES:
            try:results.append(inspect(root,row["index"],mode,row["natural" if mode=="natural" else "direct"]))
            except Reject as e:failures.append(dict(index=row["index"],mode=mode,reason=str(e)))
            except Exception as e:failures.append(dict(index=row["index"],mode=mode,type=type(e).__name__))
    counts={f"{mode}_{path}_verified":sum(x["mode"]==mode and any(v["path"]==path and v["path_verified"] for v in x["paths"]) for x in results)
            for mode in MODES for path in PATHS}
    return dict(isolated_actual_emitter_original_explicit_route_draw_verified=len(results)==24 and all(v==12 for v in counts.values()),
                observed_emitter_modes=len(results),counts=counts,cases=results,failures=failures,
                separate_diagnostic_camera_framing=True,original_full_scene_draw_verified=False,
                original_mesh_payload_modified=False,alpha_force_replayed=False,runtime_keyword_selection_verified=False,
                black_fire_restored=False,Android_device=False,production=False,XAPK=False)
