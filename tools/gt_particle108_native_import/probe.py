"""Exact native Texture2D import and explicit-mip Vulkan alpha gate.
All original payload, hashes, identities and per-pixel observations stay private.
Only aggregate result is suitable for the Actions log/artifact.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

LENGTHS=(16384,4096,1024,256,64,16,4)
TOL=0.0002
BG_ALPHA=.25
PASS="EXACT_ORIGINAL_NATIVE_SEVEN_MIP_UNITY_VULKAN_ALPHA"

def need(value,reason):
    if not value: raise ValueError(reason)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")

def native_asset_path(asset):
    need(asset.suffix in (".asset",".texture2D") and asset.name not in (".","..")
         and "\\" not in asset.name and "\x00" not in asset.name,"unsafe_native_asset_filename")
    return "Assets/GTSource/"+asset.name

def stage(original,manifest,export,w1,b02,project,private,run_id):
    from tools.gt_particle108_native_mips import probe as p
    from scripts import b05_verify_material_texenv_bindings as b05
    from scripts import gt_texture_route_payload as native
    from scripts import gt_particle108_source_pixel_parity as pixels
    need(not project.exists() and not private.exists(),"fresh_stage_required")
    _,_,key,source,sampler=p.select_source(original,manifest)
    receipt=p.verify(original,manifest,export,w1,b02)
    need(receipt["status"]==p.STATUS and receipt["mip_levels_equal"]==7 and receipt["material_texture_pptr_matches"]==10,"same_export_not_admitted")
    rows=[r for r in json.loads(b02.read_text())["objects"] if b05._trace_source(r)==key]
    need(len(rows)==1,"selected_trace_not_unique")
    ptr=b05._trace_export(rows[0])
    body=p.actual_body(export,ptr)
    actual=native.proof(body,exported=True)
    need(native.compare(source,actual)==(21844,7),"source_native_parity")
    anchor,guid,kind=ptr
    hits=[]
    for meta in (export/"Assets").rglob("*.meta"):
        raw=pixels.bounded_snapshot(meta,256*1024).decode("utf-8-sig")
        if guid in {x.lower() for x in b05.GUID.findall(raw)}: hits.append(meta)
    need(len(hits)==1 and not hits[0].is_symlink(),"stage_meta_not_unique")
    meta=hits[0]
    asset=meta.with_suffix("")
    need(asset.is_file() and not asset.is_symlink(),"stage_asset_missing")
    # Keep exact exported basename, bytes, GUID and local anchor. Do not
    # expose it to Unity's startup importer until the private log guard is
    # proved by the executing editor. No original payload inside Assets yet.
    path=native_asset_path(asset)
    asset_bytes,meta_bytes=asset.read_bytes(),meta.read_bytes()
    out={}
    raw=bytes.fromhex(body["_typelessdata"])
    need(digest(raw)==source.sha256 and tuple(source.mip_lengths)==LENGTHS,"stage_original_hash")
    mips=[];pos=0
    for i,length in enumerate(LENGTHS):
        data=raw[pos:pos+length];pos+=length
        need(digest(data)==source.mip_sha256[i],"stage_original_mip_hash")
        mips.append(dict(level=i,size=64>>i,sha256=digest(data),alpha=list(data[3::4])))
    cfg=dict(run_id=run_id,asset_path=path,guid=guid,file_id=anchor,mips=mips,
             source_sampler=sampler,source_color_space=1,
             asset_sha256=digest(asset_bytes),meta_sha256=digest(meta_bytes),
             export_basename_preserved=True,
             export_stem_matches_serialized_name=asset.stem==body.get("m_Name"))
    here=Path(__file__).parent
    out["Assets/Editor/NativeMipValidation.cs"]=(here/"NativeMipValidation.cs").read_bytes()
    out["Assets/GTNativeMipAlpha.shader"]=(here/"NativeMipAlpha.shader").read_bytes()
    out["Packages/manifest.json"]=b'{"dependencies":{}}\n'
    out["ProjectSettings/ProjectVersion.txt"]=b"m_EditorVersion: 2021.3.45f2\n"
    out["ProjectSettings/ProjectSettings.asset"]=b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTValidation\n  productName: GTNativeMip\n  m_ActiveColorSpace: 1\n"
    for name,data in out.items():
        f=project/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
    private.mkdir(mode=0o700)
    (private/"native.asset.bytes").write_bytes(asset_bytes)
    (private/"native.meta.bytes").write_bytes(meta_bytes)
    dump(project/"GTInput.json",cfg)
    dump(private/"expected.json",cfg)
    print("GT_NATIVE_MIP_UNITY_STAGE "+json.dumps({"source_native_mips":7,"source_native_bytes":21844,"same_export_PPtr":10,"export_basename_preserved":True,"export_stem_matches_serialized_name":cfg["export_stem_matches_serialized_name"],"asset_withheld_until_private_editor_log_guard":True,"private_payload_published":False,"status":"PREPARED_ONLY"},sort_keys=True))

def alpha_error(values,expected):
    need(type(values) is list and len(values)==len(expected) and len(values)>0,"readback_population")
    need(all(type(v) in (int,float) and math.isfinite(v) for v in values),"nonfinite_readback")
    return max(abs(a-b) for a,b in zip(values,expected))

def blend(alpha):
    return BG_ALPHA+(1-BG_ALPHA)*alpha/255

def evaluate(cfg,r,unchanged,exit_code):
    report=dict(status="INCONCLUSIVE",source_native_mips=7,source_native_bytes=21844,
        native_asset_and_meta_unchanged=unchanged,unity_import_verified=False,
        imported_cpu_mips_equal=0,actual_vulkan_mips_equal=0,original_alpha_texels_checked=0,
        original_shader_verified=False,android_pixels_verified=False,black_fire_restored=False,
        private_payload_published=False,production=False,player=False,XAPK=False)
    try:
        report["unity_step_exit"]=exit_code
        phases=("start","environment","input","private_log_guard","private_stage","refresh","texture_load",
                "identity_query","importer_kind","descriptor","guid_match","file_id_match","width_height",
                "mip_count","texture_format","adapter","all_mips","calibration","controls","complete")
        if r.get("phase") in phases: report["editor_phase"]=r["phase"]
        category=r.get("failure_category")
        if category in ("InvalidOperationException","ArgumentException","IOException","FileNotFoundException",
                        "UnauthorizedAccessException","UnityException","NullReferenceException"):
            report["editor_failure_category"]=category
        need(r["run_id"]==cfg["run_id"],"editor_receipt_run_mismatch")
        report["private_editor_log_guard_verified"]=r.get("private_log_guard") is True
        report["export_basename_preserved"]=cfg.get("export_basename_preserved") is True
        report["export_stem_matches_serialized_name"]=cfg.get("export_stem_matches_serialized_name") is True
        need(report["private_editor_log_guard_verified"],"private_editor_log_guard_missing")
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear" and r["device"],"actual_vulkan_environment")
        report.update(backend=r["backend"],device=r["device"],unity_texture_loaded=r.get("texture_loaded") is True,
                      imported_guid_matches=r.get("guid")==cfg["guid"],imported_file_id_matches=r.get("file_id")==cfg["file_id"],
                      native_importer_type_matches=r.get("native_importer") is True,
                      actual_width=r.get("width",0),actual_height=r.get("height",0),actual_mip_count=r.get("mip_count",0),
                      actual_texture_format=r.get("texture_format") if r.get("texture_format") in ("RGBA32","ARGB32","BGRA32","RGB24","DXT1","DXT5","Alpha8") else "other_or_unobserved")
        if r.get("importer_kind") in ("native_format","generic_asset","other","missing"):
            report["actual_importer_kind"]=r["importer_kind"]
        identity=report["unity_texture_loaded"] and report["imported_guid_matches"] and report["imported_file_id_matches"]
        descriptor=(r.get("width"),r.get("height"),r.get("mip_count"),r.get("texture_format"))==(64,64,7,"RGBA32")
        s=cfg["source_sampler"]
        sampler=all(type(r.get(k)) is int and r[k]==s[v] for k,v in (("filter_mode","m_FilterMode"),("aniso","m_Aniso"),("wrap_u","m_WrapU"),("wrap_v","m_WrapV"),("wrap_w","m_WrapW")))
        bias=type(r.get("mip_bias")) in (int,float) and math.isfinite(r["mip_bias"]) and abs(r["mip_bias"]-s["m_MipBias"])<=1e-6
        report.update(imported_descriptor_matches=descriptor,imported_sampler_fields_match=sampler and bias,
                      unity_import_verified=identity and descriptor and sampler and bias and r.get("native_importer") is True,
                      actual_texture_graphics_format=r.get("graphics_format"),
                      actual_srgb=r.get("srgb"),source_serialized_color_space=cfg["source_color_space"],readable=r.get("readable"))
        need(identity and descriptor,"imported_identity_or_descriptor_drift")
        need(exit_code==0 and r["status"]=="OBSERVED","editor_receipt_not_successful")
        need(len(cfg["mips"])==7 and len(r["mips"])==7,"mip_population")
        rows=[];cpu=0;gpu=0;texels=0
        for i,(expected,observed) in enumerate(zip(cfg["mips"],r["mips"])):
            need(expected["level"]==observed["level"]==i and expected["size"]==observed["size"]==64>>i,"mip_order_or_size")
            a=expected["alpha"];need(len(a)==(64>>i)**2,"source_alpha_population")
            target=[blend(x) for x in a]
            err=alpha_error(observed["alpha"],target)
            exact=r["readable"] is True and observed["cpu_bytes"]==LENGTHS[i] and observed["cpu_sha256"]==expected["sha256"]
            cpu+=int(exact);gpu+=int(err<=TOL);texels+=len(a)
            rows.append(dict(level=i,size=64>>i,texels=len(a),cpu_byte_match=exact,alpha_max_error=err,
                             alpha_mismatches=sum(abs(x-y)>TOL for x,y in zip(observed["alpha"],target))))
        report.update(imported_cpu_mips_equal=cpu,actual_vulkan_mips_equal=gpu,original_alpha_texels_checked=texels,mips=rows)
        # Both forced alpha values are rendered separately at mip6. At least
        # one must disagree with the correct baseline, even if fully opaque.
        a=blend(cfg["mips"][6]["alpha"][0])
        zero=alpha_error(r["force_zero"],[BG_ALPHA]);one=alpha_error(r["force_one"],[1.])
        separation=max(abs(r["force_zero"][0]-a),abs(r["force_one"][0]-a))
        report["controls"]=dict(force_zero_error=zero,force_one_error=one,max_wrong_baseline_separation=separation)
        need(zero<=TOL and one<=TOL and separation>=.37,"alpha_controls_not_discriminating")
        need(unchanged,"native_asset_or_meta_changed")
        need(gpu==7 and texels==5461,"vulkan_original_alpha_mismatch")
        need(cpu==7,"cpu_original_mip_bytes_unproved_or_drift")
        need(report["unity_import_verified"],"native_importer_or_sampler_unproved")
        report["status"]=PASS
    except (ValueError,KeyError,TypeError,IndexError) as e:
        # Do not echo arbitrary data from the private receipt.
        report["reason"]=str(e) if type(e) is ValueError else type(e).__name__
    return report

# This is a distinct observation gate, never a full restoration PASS.
DIAGNOSTIC="OBSERVED_ORIGINAL_ALPHA_LOAD_POINT_SAMPLER_COMPARISON"

def diagnostic(cfg,r,base):
    out={"status":"INCONCLUSIVE","original_texture_modified":False,
         "private_payload_published":False,"full_native_acceptance":False,
         "android_pixels_verified":False,"black_fire_restored":False}
    try:
        need(base.get("unity_step_exit")==0 and r.get("status")=="OBSERVED"
             and r.get("run_id")==cfg["run_id"] and base.get("private_editor_log_guard_verified") is True
             and base.get("native_asset_and_meta_unchanged") is True
             and base.get("backend")=="Vulkan" and base.get("unity_texture_loaded") is True
             and base.get("imported_guid_matches") is True and base.get("imported_file_id_matches") is True
             and base.get("imported_descriptor_matches") is True and base.get("imported_sampler_fields_match") is True,
             "original_import_identity_or_environment")
        need(r.get("sampler_unchanged_after_draws") is True and r.get("original_texture_rebound") is True,
             "original_sampler_or_binding_changed")
        # Explicit Load and inline point must reproduce an independent authored
        # asymmetric 8x8 chain with distinct levels, including actual wrong-LOD control.
        cal=r["calibration"];need(len(cal)==4,"calibration_population")
        cal_errors=[]
        for i,m in enumerate(cal):
            size=8>>i;need(m["level"]==i and m["size"]==size,"calibration_level")
            target=[blend(11+41*i+7*x+3*y) for y in range(size) for x in range(size)]
            le=alpha_error(m["load_alpha"],target)
            pe=alpha_error(m["point_alpha"],target)
            cal_errors.append({"level":i,"texels":size*size,"load_max_error":le,"point_max_error":pe})
            need(le<=TOL and pe<=TOL,"authored_load_or_point_calibration_failed")
        wrong=alpha_error(r["calibration_wrong_mip"],[blend(11)])
        sep=alpha_error(r["calibration_wrong_mip"],[blend(11+41*3)])
        need(wrong<=TOL and sep>.3,"wrong_mip_control_not_discriminating")
        controls=base.get("controls",{})
        need(controls.get("force_zero_error",1)<=TOL and controls.get("force_one_error",1)<=TOL
             and controls.get("max_wrong_baseline_separation",0)>=.37,"alpha_controls_not_discriminating")
        out.update(calibration_mips=4,calibration_texels=85,calibration=cal_errors,
                   wrong_mip_expected_error=wrong,wrong_mip_separation=sep)
        need(len(cfg["mips"])==len(r["mips"])==7,"original_mip_population")
        rows=[];load=point=original=agree=texels=0
        for i,(e,m) in enumerate(zip(cfg["mips"],r["mips"])):
            size=64>>i
            need(e["level"]==m["level"]==i and e["size"]==m["size"]==size,"original_mip_level")
            need(len(e["alpha"])==size*size,"original_source_alpha_population")
            target=[blend(v) for v in e["alpha"]]
            le=alpha_error(m["load_alpha"],target)
            pe=alpha_error(m["point_alpha"],target)
            oe=alpha_error(m["alpha"],target)
            lp=alpha_error(m["load_alpha"],m["point_alpha"])
            load+=le<=TOL;point+=pe<=TOL;original+=oe<=TOL;agree+=lp<=TOL;texels+=size*size
            rows.append(dict(level=i,size=size,texels=size*size,load_max_error=le,point_max_error=pe,
                             original_sampler_max_error=oe,load_vs_point_max_error=lp,
                             load_mismatches=sum(abs(a-b)>TOL for a,b in zip(m["load_alpha"],target)),
                             point_mismatches=sum(abs(a-b)>TOL for a,b in zip(m["point_alpha"],target))))
        need(texels==5461,"original_texel_population")
        if load==point==7 and original<7:
            interpretation="EXACT_GPU_ALPHA_VIA_LOAD_AND_POINT_ORIGINAL_SAMPLER_DIFFERS"
        elif load==point==original==7:
            interpretation="ALL_THREE_GPU_ALPHA_ROUTES_MATCH_SOURCE"
        elif agree==7 and load<7:
            interpretation="GPU_LOAD_AND_POINT_AGREE_BUT_SOURCE_ALPHA_DIFFERS"
        else:
            interpretation="LOAD_POINT_OR_SOURCE_DISAGREEMENT_UNRESOLVED"
        out.update(status=DIAGNOSTIC,interpretation=interpretation,original_texels_per_route=texels,
                   actual_original_alpha_readbacks=3*texels,load_mips_matching_source=load,
                   point_mips_matching_source=point,original_sampler_mips_matching_source=original,
                   load_point_agree_mips=agree,mips=rows,
                   cpu_readback_available=r.get("readable") is True,
                   source_alpha_gpu_load_exact=load==7,
                   original_sampler_settings_unchanged=True,
                   rgba_or_raw_cpu_byte_parity_claimed=False)
    except (KeyError,TypeError,ValueError,IndexError) as e:
        out["reason"]=str(e) if type(e) is ValueError else type(e).__name__
    return out

def verify(project,private,safe,run_id,exit_code):
    result={"status":"INCONCLUSIVE","reason":"receipt_absent","private_payload_published":False,
            "unity_import_verified":False,"android_pixels_verified":False,"black_fire_restored":False,"production":False,"XAPK":False}
    try:
        cfg=json.loads((private/"expected.json").read_text())
        need(cfg["run_id"]==run_id,"stage_run_mismatch")
        asset=project/cfg["asset_path"]
        meta=Path(str(asset)+".meta")
        unchanged=all(p.is_file() and not p.is_symlink() for p in (asset,meta)) and digest(asset.read_bytes())==cfg["asset_sha256"] and digest(meta.read_bytes())==cfg["meta_sha256"]
        raw=json.loads((private/"raw.json").read_text())
        marker=private/"editor-output-private"
        guard=marker.is_file() and not marker.is_symlink() and marker.read_text().strip()==run_id and (private/"editor.log").is_file()
        raw["private_log_guard"]=raw.get("private_log_guard") is True and guard
        result=evaluate(cfg,raw,unchanged,exit_code)
        result["alpha_route_diagnostic"]=diagnostic(cfg,raw,result)
        result["cpu_mip_readback_available"]=raw.get("readable") is True
    except Exception as e:
        result["failure_category"]=type(e).__name__
    dump(safe,result)
    print("GT_NATIVE_MIP_UNITY_RESULT "+json.dumps(result,sort_keys=True))
    # Success means the distinct observation is complete, NOT that the
    # original native acceptance or Android fire restoration has passed.
    return 0 if result.get("alpha_route_diagnostic",{}).get("status")==DIAGNOSTIC else 2

def main():
    q=argparse.ArgumentParser();q.add_argument("mode",choices=("stage","verify"))
    for k in ("original","manifest","export","w1","b02","project","private","safe"):
        q.add_argument("--"+k,type=Path)
    q.add_argument("--run-id",required=True);q.add_argument("--exit-code",type=int,default=1)
    a=q.parse_args()
    if a.mode=="verify": return verify(a.project,a.private,a.safe,a.run_id,a.exit_code)
    try:
        stage(a.original,a.manifest,a.export,a.w1,a.b02,a.project,a.private,a.run_id)
        return 0
    except Exception as e:
        print("GT_NATIVE_MIP_UNITY_STAGE_INCONCLUSIVE "+type(e).__name__)
        return 2
if __name__=="__main__":raise SystemExit(main())
