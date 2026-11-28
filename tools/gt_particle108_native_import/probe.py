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
    # Keep the original native asset and meta byte-for-byte, including the
    # source-linked GUID and local object anchor. Only neutralize filename.
    path="Assets/GTOriginal"+asset.suffix
    out={path:asset.read_bytes(),path+".meta":meta.read_bytes()}
    raw=bytes.fromhex(body["_typelessdata"])
    need(digest(raw)==source.sha256 and tuple(source.mip_lengths)==LENGTHS,"stage_original_hash")
    mips=[];pos=0
    for i,length in enumerate(LENGTHS):
        data=raw[pos:pos+length];pos+=length
        need(digest(data)==source.mip_sha256[i],"stage_original_mip_hash")
        mips.append(dict(level=i,size=64>>i,sha256=digest(data),alpha=list(data[3::4])))
    cfg=dict(run_id=run_id,asset_path=path,guid=guid,file_id=anchor,mips=mips,
             source_sampler=sampler,source_color_space=1,
             asset_sha256=digest(out[path]),meta_sha256=digest(out[path+".meta"]))
    here=Path(__file__).parent
    out["Assets/Editor/NativeMipValidation.cs"]=(here/"NativeMipValidation.cs").read_bytes()
    out["Assets/GTNativeMipAlpha.shader"]=(here/"NativeMipAlpha.shader").read_bytes()
    out["Packages/manifest.json"]=b'{"dependencies":{}}\n'
    out["ProjectSettings/ProjectVersion.txt"]=b"m_EditorVersion: 2021.3.45f2\n"
    out["ProjectSettings/ProjectSettings.asset"]=b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTValidation\n  productName: GTNativeMip\n  m_ActiveColorSpace: 1\n"
    for name,data in out.items():
        f=project/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
    private.mkdir(mode=0o700)
    dump(project/"GTInput.json",cfg)
    dump(private/"expected.json",cfg)
    print("GT_NATIVE_MIP_UNITY_STAGE "+json.dumps({"source_native_mips":7,"source_native_bytes":21844,"same_export_PPtr":10,"private_payload_published":False,"status":"PREPARED_ONLY"},sort_keys=True))

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
        if r.get("phase") in ("start","environment","import","adapter","all_mips","controls","complete"):
            report["editor_phase"]=r["phase"]
        need(exit_code==0 and r["status"]=="OBSERVED" and r["run_id"]==cfg["run_id"],"editor_receipt_not_successful")
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear" and r["device"],"actual_vulkan_environment")
        need(r["guid"]==cfg["guid"] and r["file_id"]==cfg["file_id"] and r["native_importer"] is True,"imported_native_guid_file_id")
        need((r["width"],r["height"],r["mip_count"],r["texture_format"])==(64,64,7,"RGBA32"),"imported_descriptor_drift")
        s=cfg["source_sampler"]
        need(all(type(r[k]) is int and r[k]==s[v] for k,v in (("filter_mode","m_FilterMode"),("aniso","m_Aniso"),("wrap_u","m_WrapU"),("wrap_v","m_WrapV"),("wrap_w","m_WrapW"))),"imported_sampler_drift")
        need(math.isfinite(r["mip_bias"]) and abs(r["mip_bias"]-s["m_MipBias"])<=1e-6,"imported_bias_drift")
        report.update(unity_import_verified=True,backend=r["backend"],device=r["device"],actual_texture_graphics_format=r["graphics_format"],
                      actual_srgb=r["srgb"],source_serialized_color_space=cfg["source_color_space"],readable=r["readable"])
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
        report["status"]=PASS
    except (ValueError,KeyError,TypeError,IndexError) as e:
        # Do not echo arbitrary data from the private receipt.
        report["reason"]=str(e) if type(e) is ValueError else type(e).__name__
    return report

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
        result=evaluate(cfg,raw,unchanged,exit_code)
    except Exception as e:
        result["failure_category"]=type(e).__name__
    dump(safe,result)
    print("GT_NATIVE_MIP_UNITY_RESULT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==PASS else 2

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
