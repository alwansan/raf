"""V14 authored-only reversible TextureImporter alpha policy experiment.

V13 exact staged source and route identity are retained. GPU Texture2D.Load
does not involve sampler interpolation, mip bias or Graphics.Blit. No
original, Android, source lower-mip or general normal-map parity claim.
"""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import re
from scripts import gt_dxt5nm_unity_reimport as v13

need=v13.need
digest=v13.digest
ROOT=v13.ROOT
V13=ROOT/"clients/GT/sessions/20261127-dxt5nm-unity-v13/actual-pass-45970415390.json"
TOOLS=ROOT/"tools/gt_dxt5nm_texel_policy"
PHASES=("alpha_on","alpha_off","alpha_restored")
DIMS=((5,7),(2,3),(1,1))

def flip(raw,w,h):
    need(len(raw)==w*h*4,"rgba_extent")
    return b"".join(raw[i*w*4:(i+1)*w*4] for i in reversed(range(h)))

def pixels(raw):
    need(len(raw)%4==0,"rgba_alignment")
    return list(zip(*[iter(raw)]*4))

def repack(raw):
    return bytes(c for x,y,z,a in pixels(raw) for c in (255,y,y,x))

def policy_byte(raw):
    hits=list(re.finditer(rb"(?m)^  alphaIsTransparency: (1)(?:\r?$)",raw))
    need(len(hits)==1,"exact_alpha_policy_byte_required")
    pos=hits[0].start(1)
    out=raw[:pos]+b"0"+raw[pos+1:]
    need(len(out)==len(raw) and out[:pos]+b"1"+out[pos+1:]==raw,"other_meta_bytes_changed")
    return out,pos

def stage(project,manifest,out):
    project,manifest,out=map(v13.regular_path,(project,manifest,out))
    m=v13.read(manifest)
    hist=v13.read(V13)
    need(hist["status"]=="PASS_ACTUAL_AUTHORED_UNITY_DXT5NM_ROUTE_OBSERVATION"
         and hist["verified"]["actual_Unity_import_verified"] and m["schema_version"]==13
         and m["synthetic_only"] and m["source_V12_verified"],"V13_actual_baseline_required")
    need((project/"gt-normal-route-manifest.json").read_bytes()==manifest.read_bytes(),"stage_manifest_drift")
    for p,h in m["staged_files"].items():
        need(digest(v13.regular_path(project/p).read_bytes())==h,"V13_staged_file_drift")
    patches=[]
    for t in m["textures"]:
        raw=(project/(t["path"]+".meta")).read_bytes()
        need(digest(raw)==t["meta_sha256"],"V13_texture_meta_drift")
        off,pos=policy_byte(raw)
        patches.append(dict(path=t["path"],guid=t["guid"],baseline_sha256=digest(raw),
            off_sha256=digest(off),changed_byte_offset=pos))
    sources={"Assets/GTNormalProbe/NormalTexelLoad.compute":"NormalTexelLoad.compute",
        "Assets/Editor/SyntheticNormalTexelPolicy.cs":"SyntheticNormalTexelPolicy.cs"}
    additional={}
    for dest,src in sources.items():
        b=(TOOLS/src).read_bytes();p=project/dest
        need(not p.exists(),"fresh_V14_asset");p.write_bytes(b);additional[dest]=digest(b)
    policy=dict(schema_version=14,run_id=m["run_id"],v13_manifest_sha256=digest(manifest.read_bytes()),
        texture_patches=patches,additional_staged_files=additional,
        prior_actual_V13_run=45970415390,synthetic_only=True,original_assets_read=False)
    path=project/"gt-texel-policy-manifest.json"
    v13.write(path,policy)
    need(not out.exists(),"fresh_V14_manifest")
    out.write_bytes(path.read_bytes())
    print(json.dumps(dict(status="PREPARED_V14",texture_patches=patches,policy_manifest_sha256=digest(path.read_bytes()))))

def exact_id(actual,exp,meta=None):
    v13.identity(actual,exp)
    need(actual["meta_sha256"]==(exp["meta_sha256"] if meta is None else meta),"actual_meta_sha256_drift")

def expected_settings(source,alpha):
    sampler=source["sampler"]
    return dict(type=1,shape=1,srgb=False,mipmap=bool(source["mip_enabled"]),readable=bool(source["readable"]),
        streaming=bool(source["streaming"]),priority=source["priority"],filter=sampler[0],aniso=sampler[1],
        wrap_u=sampler[3],wrap_v=sampler[4],wrap_w=sampler[5],max_size=source["max_size"],npot=0,alpha_source=1,
        alpha_transparency=alpha,compression_quality=50,convert_normal=False,height_scale=.25,normal_filter=0,
        platform_format=-1,platform_compression=2,platform_override=False,bias=v13.as_float(sampler[2]),
        runtime_readable=bool(source["readable"]),runtime_streaming=bool(source["streaming"]),runtime_filter=sampler[0],
        runtime_aniso=sampler[1],runtime_wrap_u=sampler[3],runtime_wrap_v=sampler[4],runtime_wrap_w=sampler[5],runtime_bias=v13.as_float(sampler[2]),
        width=5,height=7,mip_count=3,graphics_srgb=False,format="RGBA32",graphics_format="R8G8B8A8_UNorm")

def phase_data(m,policy,phase,alpha):
    need(len(phase["routes"])==2 and len(phase["textures"])==2,"actual_phase_population")
    meta={p["guid"]:p["baseline_sha256" if alpha else "off_sha256"] for p in policy["texture_patches"]}
    for exp,obs in zip(m["routes"],phase["routes"],strict=True):
        need(obs["key"]==exp["key"] and all(obs[k]==exp[k] for k in ("vertex_count","index_counts","base_vertices")),"actual_mesh_layout")
        need(len(obs["uv"])==len(exp["uv"])==8 and all(abs(x-y)<1e-6 for x,y in zip(obs["uv"],exp["uv"],strict=True)),"actual_route_UV")
        exact_id(obs["mesh"],exp["mesh"])
        for key in ("materials","textures","shaders"):
            need(len(obs[key])==len(exp[key])==2,"actual_route_slot_count")
            for a,b in zip(obs[key],exp[key],strict=True):exact_id(a,b,meta[b["guid"]] if key=="textures" else None)
    out=[]
    for exp,obs in zip(m["textures"],phase["textures"],strict=True):
        exact_id(obs["identity"],exp,meta[exp["guid"]])
        settings=expected_settings(exp["expected_source"],alpha)
        need(all(obs.get(k)==v and type(obs.get(k)) is type(v) or type(v) is float and obs.get(k)==v for k,v in settings.items()),"actual_importer_or_runtime_setting_drift")
        need(len(obs["mips"])==3,"actual_mip_count")
        rows=[]
        for n,(mp,(w,h)) in enumerate(zip(obs["mips"],DIMS,strict=True)):
            need((mp["level"],mp["width"],mp["height"])==(n,w,h),"actual_mip_dimensions")
            raw=bytes.fromhex(mp["rgba_hex"]);need(len(raw)==4*w*h,"actual_texel_extent")
            err=mp["max_unorm_error"];need(type(err) in (float,int) and math.isfinite(err) and 0<=err<=1e-6,"actual_unorm_precision")
            rows.append(raw)
        cpu=bytes.fromhex(obs["cpu_top_rgba_hex"])
        if settings["readable"]:
            need(obs["cpu_status"]=="cpu_GetPixels32_observed" and len(cpu)==140,"actual_readable_CPU_population")
        else:need(obs["cpu_status"]=="not_readable_as_imported" and cpu==b"","nonreadable_CPU_bypass")
        out.append((rows,cpu))
    return out

def comparison(expected,actual,source):
    need(len(expected)==len(actual)==len(source)==140,"top_mip_extent")
    mismatches=[]
    for i,(a,b,s) in enumerate(zip(pixels(expected),pixels(actual),pixels(source),strict=True)):
        if a!=b:mismatches.append(dict(x=i%5,y=i//5,source_rgba=list(s),expected_packed=list(a),actual_packed=list(b)))
    return dict(matches=35-len(mismatches),mismatches=mismatches,
        all_mismatches_zero_source_alpha=all(x["source_rgba"][3]==0 for x in mismatches))

def verify(m,policy,r,run_id,exit_code):
    need(exit_code==0 and r.get("status")=="OBSERVED_AUTHORED_UNFILTERED_TEXEL_POLICY","actual_Unity_probe_required:"+str(r.get("error","missing")))
    need(r["run_id"]==m["run_id"]==policy["run_id"]==run_id and r["editor"]==v13.EDITOR_VERSION and r["backend"]=="Vulkan" and r["active_color_space"]=="Linear","actual_run_environment")
    need(r["unfiltered_compute_load"] is True and r["restored_exact_meta"] is True and r["scene_route_replay"] is True and r["shader_adapter"] is True and r["original_assets_read"] is False,"scope_or_restore_flag")
    need(len(policy["texture_patches"])==2 and len(r["phases"])==3 and tuple(p["name"] for p in r["phases"])==PHASES,"actual_phase_order")
    data=[phase_data(m,policy,p,alpha) for p,alpha in zip(r["phases"],(True,False,True),strict=True)]
    # Anchor orientation to the actual readable CPU path, not whichever source
    # orientation gives the lowest error for each texture/phase.
    top,cpu=data[0][0][0][0],data[0][0][1]
    modes=[mode for mode in ("bottom_first","top_first") if (top if mode=="bottom_first" else flip(top,5,7))==cpu]
    need(len(modes)==1,"unique_GPU_CPU_orientation")
    mode=modes[0]
    hist=v13.read(V13)
    need(cpu.hex()==hist["independent"]["readable_texture_actual_CPU_RGBA_bottom_first"],"historical_V13_CPU_baseline_drift")
    rows=[];total=0
    for i,exp in enumerate(m["textures"]):
        a,b,c=[d[i] for d in data]
        need(a==c,"actual_ABA_restoration_drift")
        for gpu,cpu in (a,b,c):
            if cpu:need((gpu[0] if mode=="bottom_first" else flip(gpu[0],5,7))==cpu,"actual_GPU_CPU_texel_drift")
        source=bytes.fromhex(exp["expected_rgba_hex"])
        def source_top(raw):return flip(raw,5,7) if mode=="bottom_first" else raw
        before=comparison(repack(source),source_top(a[0][0]),source)
        after=comparison(repack(source),source_top(b[0][0]),source)
        changes=[sum(x!=y for x,y in zip(pixels(xraw),pixels(yraw),strict=True)) for xraw,yraw in zip(a[0],b[0],strict=True)]
        zero=sum(x[3]==0 for x in pixels(source))
        rows.append(dict(guid=exp["guid"],source_zero_alpha_pixels=zero,alpha_on=before,alpha_off=after,
            actual_mip_dimensions=[list(x) for x in DIMS],changed_texels_by_mip=changes,
            alpha_on_mip_sha256=[digest(x) for x in a[0]],alpha_off_mip_sha256=[digest(x) for x in b[0]],
            alpha_restored_exact=True,actual_cpu_comparison_available=bool(a[1])))
        total+=3*sum(w*h for w,h in DIMS)
    exact=all(x["alpha_off"]["matches"]==35 and len(x["alpha_on"]["mismatches"])==x["source_zero_alpha_pixels"] and x["alpha_on"]["all_mismatches_zero_source_alpha"] for x in rows)
    return dict(status="PASS_ACTUAL_AUTHORED_DXT5NM_ALPHA_POLICY_CAUSAL_TEXEL_WITNESS" if exact else "OBSERVED_AUTHORED_DXT5NM_ALPHA_POLICY_WITH_REMAINING_TEXEL_DRIFT",
        actual_Unity_texel_observation_verified=True,actual_alpha_zero_repack_loss_isolated=exact,unfiltered_GPU_texels=total,
        top_mip_alpha_off_exact_pixels=sum(x["alpha_off"]["matches"] for x in rows),alpha_on_exact_pixels=sum(x["alpha_on"]["matches"] for x in rows),
        actual_GPU_row_orientation=mode,renderer_route_matches_across_phases=6,submesh_material_texture_matches_across_phases=12,
        shader_adapter_identity_matches_across_phases=12,restored_exact_meta_and_texels=True,rows=rows,
        source_lower_mip_parity_verified=False,original_assets_read=False,scene_import_verified=False,
        original_shader_program_parity_verified=False,Android_device=False,XAPK=False)

def controls(m,p,r,run_id):
    results={}
    def reject(name,mutation):
        q=deepcopy(r);mutation(q)
        try:verify(m,p,q,run_id,0)
        except (ValueError,KeyError,TypeError,AssertionError,OverflowError) as e:results[name]=str(e)
        else:raise ValueError("V14_control_not_rejected:"+name)
    reject("wrong_run",lambda q:q.update(run_id="wrong"))
    reject("missing_restore",lambda q:q.update(restored_exact_meta=False))
    reject("phase_swap",lambda q:q["phases"].reverse())
    reject("off_policy_unchanged",lambda q:q["phases"][1]["textures"][0].update(alpha_transparency=True))
    reject("texture_route_swap",lambda q:q["phases"][1]["routes"][0]["textures"].reverse())
    reject("changed_other_sampler",lambda q:q["phases"][1]["textures"][0].update(aniso=999))
    reject("off_meta_wrong",lambda q:q["phases"][1]["textures"][0]["identity"].update(meta_sha256="0"*64))
    reject("restored_texel_drift",lambda q:q["phases"][2]["textures"][1]["mips"][0].update(rgba_hex="00"*140))
    reject("invalid_mip_extent",lambda q:q["phases"][1]["textures"][0]["mips"][1].update(width=99))
    reject("nonreadable_CPU_fabrication",lambda q:q["phases"][1]["textures"][1].update(cpu_top_rgba_hex="00"*140))
    return results

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("stage")
    for n in ("project","manifest","out"):a.add_argument("--"+n,type=Path,required=True)
    a=s.add_parser("verify")
    for n in ("manifest","policy","receipt","out"):a.add_argument("--"+n,type=Path,required=True)
    a.add_argument("--run-id",required=True);a.add_argument("--exit-code",type=int,required=True)
    a=p.parse_args()
    if a.cmd=="stage":stage(a.project,a.manifest,a.out);return
    need(not a.out.exists(),"fresh_output")
    try:
        m,policy,r=map(v13.read,(a.manifest,a.policy,a.receipt))
        need(r["v13_manifest_sha256"]==policy["v13_manifest_sha256"]==digest(a.manifest.read_bytes()) and r["policy_manifest_sha256"]==digest(a.policy.read_bytes()),"actual_manifest_hash_binding")
        result=verify(m,policy,r,a.run_id,a.exit_code)
        result["actual_receipt_negative_controls"]=controls(m,policy,r,a.run_id)
        result["actual_receipt_negative_control_count"]=len(result["actual_receipt_negative_controls"])
    except (ValueError,KeyError,TypeError,AssertionError,OSError,OverflowError) as e:
        result=dict(status="INCONCLUSIVE",reason=str(e),actual_Unity_texel_observation_verified=False,Android_device=False,XAPK=False)
    v13.write(a.out,result);print(json.dumps(result,sort_keys=True))
    if result["status"]=="INCONCLUSIVE":raise SystemExit(2)
if __name__=="__main__":main()
