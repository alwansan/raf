"""Actual particle renderer and unchanged baked geometry draw observations.
Both paths use the same restored explicit original route, independently framed.
Separate actual-emitter alpha-only override causality; no full scene/runtime/phone admission.
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
CASES=("reference","clear","native","repeat","marker","source","clone","zero","one","restored")
PHASES=("start","frame","reference","clear","native","repeat","marker","source","clone","zero","one","restored","post_draw","complete")
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
    reference_ok=not neq(rows["reference"],BACKGROUNDS[bg]).any()
    clear_ok=not neq(rows["clear"],BACKGROUNDS[bg]).any()
    clear_reference_ok=not neq(rows["clear"],rows["reference"]).any()
    clear_uniform=not neq(rows["clear"],rows["clear"][0,0]).any()
    marker=np.max(np.abs(rows["marker"]-MARKER),axis=-1)<=TOL
    native=neq(rows["native"],rows["clear"],True)
    repeat=neq(rows["native"],rows["repeat"],True)
    alpha=max(float(np.max(np.abs(rows[k][...,3]-rows["clear"][...,3]))) for k in ("native","repeat"))
    distinct=neq(rows["native"],rows["marker"],True)&native
    overlap=marker&native
    result=dict(reference_matches_background=bool(reference_ok),clear_matches_background=bool(clear_ok),
                clear_matches_independent_reference=bool(clear_reference_ok),clear_uniform=bool(clear_uniform),
                reference_rgb_matches=not bool(neq(rows["reference"],BACKGROUNDS[bg],True).any()),
                reference_alpha_matches=bool(np.max(np.abs(rows["reference"][...,3]-BACKGROUNDS[bg][3]))<=TOL),
                clear_rgb_matches=not bool(neq(rows["clear"],BACKGROUNDS[bg],True).any()),
                clear_alpha_matches=bool(np.max(np.abs(rows["clear"][...,3]-BACKGROUNDS[bg][3]))<=TOL),marker_pixels=int(marker.sum()),native_visible_pixels=int(native.sum()),
                native_distinct_from_marker_pixels=int(distinct.sum()),native_marker_overlap_pixels=int(overlap.sum()),
                native_outside_marker_pixels=int((native&~marker).sum()),repeat_rgb_difference_pixels=int(repeat.sum()),
                source_rgb_mask_alpha_preserved=alpha<=TOL)
    result["calibrated_original_rgb_observed"]=bool(reference_ok and clear_ok and clear_reference_ok and clear_uniform and marker.sum()>=4 and overlap.any() and distinct.any() and not repeat.any() and alpha<=TOL)
    # Exact native/clone controls and alpha-only intervention on the SAME particle state.
    source_diff=int(neq(rows["source"],rows["native"]).sum())
    clone_diff=int(neq(rows["clone"],rows["native"]).sum())
    restored_diff=int(neq(rows["restored"],rows["native"]).sum())
    zero_diff=int(neq(rows["zero"],rows["clear"],True).sum())
    one_visible=neq(rows["one"],rows["clear"],True)
    effect=neq(rows["zero"],rows["one"],True)
    override_mask=all(np.max(np.abs(rows[k][...,3]-rows["clear"][...,3]))<=TOL
                      for k in ("source","clone","zero","one","restored"))
    result.update(source_block_difference_pixels=source_diff,exact_clone_difference_pixels=clone_diff,
                  restored_difference_pixels=restored_diff,zero_alpha_visible_pixels=zero_diff,
                  one_alpha_visible_pixels=int(one_visible.sum()),zero_one_rgb_difference_pixels=int(effect.sum()),
                  alpha_effect_inside_marker_pixels=int((effect&marker).sum()),
                  override_rgb_mask_alpha_preserved=bool(override_mask))
    result["calibrated_actual_alpha_effect"]=bool(result["calibrated_original_rgb_observed"] and
        source_diff==clone_diff==restored_diff==zero_diff==0 and one_visible.any() and (effect&marker).any() and override_mask)
    return result

def inspect(root,index,mode,expected):
    j=json.loads((root/f"emitter-{index}-{mode}.json").read_text())
    need(j.get("index")==index and j.get("mode")==mode,"draw_identity")
    n=expected.get("particles")
    need(type(n) is int and 0<n<=256 and expected.get("vertices")==4*n and expected.get("indices")==6*n
         and j.get("particles")==n and j.get("vertices")==4*n and j.get("indices")==6*n,"draw_same_bake_geometry")
    clone_ok=j.get("clone_payload_verified") is True and j.get("clone_format_sampler_verified") is True
    paths=j.get("paths")
    need(type(paths) is list and len(paths)==2 and {x.get("path") for x in paths}==set(PATHS),"draw_path_population")
    result=[]
    for r in paths:
        path=r["path"]
        safe=dict(path=path,phase=r.get("phase") if r.get("phase") in PHASES else "other",
                  failure_category=r.get("failure_category") if r.get("failure_category") in EXCEPTIONS else "other",
                  submissions=r.get("submissions") if type(r.get("submissions")) is int and 0<=r["submissions"]<=20 else 0,
                  completed=r.get("completed") is True,material_restored=r.get("material_restored") is True,
                  streams_unchanged=r.get("streams_unchanged") is True,particles_unchanged=r.get("particles_unchanged") is True,
                  blocks_restored=r.get("blocks_restored") is True,
                  override_submissions=r.get("override_submissions") if type(r.get("override_submissions")) is int and 0<=r["override_submissions"]<=8 else 0,
                  backgrounds=[])
        for bg in range(2):
            try:
                rows={k:read_pixels(root/f"emitter-{index}-{mode}-{path}-{bg}-{k}.f32",SIZE) for k in CASES}
                safe["backgrounds"].append(dict(background=bg,**classify(rows,bg)))
            except Exception as e:
                safe["backgrounds"].append(dict(background=bg,failure_type=type(e).__name__))
        safe["path_verified"]=(safe["submissions"]==20 and all(safe[k] for k in ("completed","material_restored","streams_unchanged","particles_unchanged")) and all(x.get("calibrated_original_rgb_observed") is True for x in safe["backgrounds"]))
        safe["alpha_path_verified"]=(safe["path_verified"] and clone_ok and safe["blocks_restored"] and safe["override_submissions"]==8 and all(x.get("calibrated_actual_alpha_effect") is True for x in safe["backgrounds"]))
        result.append(safe)
    return dict(index=index,mode=mode,particles=n,vertices=4*n,indices=6*n,clone_payload_and_sampler_verified=clone_ok,paths=result)

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
    alpha_counts={f"{mode}_{path}_alpha_verified":sum(x["mode"]==mode and any(v["path"]==path and v["alpha_path_verified"] for v in x["paths"]) for x in results) for mode in MODES for path in PATHS}
    return dict(isolated_actual_emitter_original_explicit_route_draw_verified=len(results)==24 and all(v==12 for v in counts.values()),
                isolated_actual_emitter_alpha_causality_verified=len(results)==24 and all(v==12 for v in alpha_counts.values()),
                alpha_counts=alpha_counts,clone_verified_modes=sum(x["clone_payload_and_sampler_verified"] for x in results),
                observed_emitter_modes=len(results),counts=counts,cases=results,failures=failures,
                separate_diagnostic_camera_framing=True,renderer_framed_from_live_world_particles=True,
                explicit_camera_clear_and_direct_reference=True,original_full_scene_draw_verified=False,
                original_mesh_payload_modified=False,actual_emitter_alpha_only_intervention=True,runtime_keyword_selection_verified=False,
                black_fire_restored=False,Android_device=False,production=False,XAPK=False)
