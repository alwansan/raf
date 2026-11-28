"""Isolated native class187 BC3 payload preservation and independent Vulkan readback.
No original shader draw, Android, or production integration is admitted here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import numpy as np
from scripts import gt_compare_original_bc3_to_flipbook_pixels as layout
from scripts.gt_bc3_array_layout import mip_bytes
from tools.gt_top_resource_closure import selected_array_unity as old

def need(ok,code):
    if not ok: raise old.Failure(code)

def sha(b): return hashlib.sha256(b).hexdigest()

def ranges(w,h,d,n):
    cursor=0
    for layer in range(d):
        for mip in range(n):
            offset,size=layout.mip_range(w,h,d,n,layer,mip,"slice_major")
            need(offset==cursor and size==mip_bytes(w,h,mip),"native_range_extent")
            yield layer,mip,offset,size
            cursor+=size

def cal_payload():
    # Pure RGB565 endpoints and alpha 0/255 avoid interpolation ambiguity.
    # Asymmetric indices and distinct layer/mip/block endpoints are controls.
    palette=(0xf800,0x07e0,0x001f,0xffe0,0xf81f,0x07ff,0xffff)
    out=bytearray()
    for l,m,_,size in ranges(8,8,2,4):
        for block in range(size//16):
            a=b=0
            for y in range(4):
                for x in range(4):
                    i=y*4+x
                    a |= ((x+y)%2) << (3*i)
                    b |= ((y+x//2)%2) << (2*i)
            k=(3*l+m+block)%len(palette)
            out.extend(bytes((255,0))+a.to_bytes(6,"little")+
                       struct.pack("<HHI",palette[k],palette[(k+1)%len(palette)],b))
    return bytes(out)

def stage_native(raw,root,cfg,tree,kind):
    rr=list(ranges(1024,1024,2,11))
    need(len(rr)==22 and rr[-1][2]+rr[-1][3]==len(raw)==2796256,"native_selected_payload_extent")
    name=tree.get("m_Name")
    need(isinstance(name,str) and 0<len(name)<=1024 and kind in (2,3),"native_source_name_or_reference_type")
    cal=cal_payload()
    cfg.update(native_payload_sha256=sha(raw),native_payload_bytes=len(raw),
               calibration_sha256=sha(cal),native_mip_ranges=22,source_name=name,
               source_ref_type=kind,source_graphics_format=100)
    (root/"array.bc3.bytes").write_bytes(raw)
    (root/"authored.bc3.bytes").write_bytes(cal)

def decoded(raw,w,h,d,n):
    rr=list(ranges(w,h,d,n))
    need(len(rr)==d*n and rr[-1][2]+rr[-1][3]==len(raw),"native_decode_extent")
    result=[[] for _ in range(n)]
    for l,m,off,size in rr:
        img=layout.dds_bc3(raw[off:off+size],max(1,w>>m),max(1,h>>m))
        result[m].append(np.asarray(img,dtype=np.uint8))
    return [old.expected_linear(np.stack(v)) for v in result]

def orient(x,mode):
    need(mode in ("raw_first","flipped"),"unknown_native_orientation")
    return x if mode=="raw_first" else x[:,::-1]

def calibrate(actual,expected):
    need(len(actual)==len(expected)==4,"native_calibration_mips")
    modes=[]
    for mode in ("raw_first","flipped"):
        if all(a.shape==e.shape and np.isfinite(a).all() and
               np.max(np.abs(a-orient(e,mode)))<=1e-5 for a,e in zip(actual,expected,strict=True)):
            modes.append(mode)
    need(len(modes)==1,"native_BC3_calibration_orientation_unproven")
    mode=modes[0]
    top=orient(expected[0],mode)
    need(np.max(np.abs(actual[0]-top[::-1]))>0.05,"native_wrong_layer_control")
    need(np.max(np.abs(actual[0]-top[:,::-1]))>0.05,"native_wrong_orientation_control")
    need(np.max(np.abs(actual[1]-top[:,::2,::2]))>0.05,"native_wrong_mip_control")
    return mode

def summarize(actual,expected,mode):
    per=[]
    for m,(a,e) in enumerate(zip(actual,expected,strict=True)):
        target=orient(e,mode)
        rows=old.compare(a,target)
        wrong=old.compare(a,target[::-1])
        vertical=old.compare(a,target[:,::-1])
        per.append({"mip":m,"width":int(a.shape[2]),"height":int(a.shape[1]),
                    "per_layer":rows,"reversed_layer_control":wrong,
                    "reversed_rows_control":vertical})
    return per

TRANSFER_PHASES={"not_started","scratch_create","scratch_identity","target_write","target_import","target_identity","target_descriptor","target_rejected","complete"}
TRANSFER_FLAGS=("scratch_id_matches","scratch_name_matches","meta_guid_anchor","meta_written",
                "path_guid_matches","guid_path_matches","loaded_array","object_guid_matches","object_id_matches",
                "native_meta","importer_reports_native","name_matches","dimensions_match","mips_match","format_matches","srgb","readable",
                "serialized_bytes_unchanged","accepted")
FAILURE_TYPES={"","InvalidOperationException","ArgumentException","IOException","UnityException","NullReferenceException",
               "FileNotFoundException","UnauthorizedAccessException","NotSupportedException","OverflowException"}

def safe_transfer(record):
    need(isinstance(record,dict),"native_transfer_record_missing")
    phase=record.get("phase")
    failure=record.get("failure_category")
    return {"phase":phase if phase in TRANSFER_PHASES else "unknown",
            "failure_category":failure if failure in FAILURE_TYPES else "other",
            **{key:record.get(key) is True for key in TRANSFER_FLAGS}}

def raw_matches(source,back,w,h,d,n):
    need(len(source)==len(back),"native_raw_extent")
    rr=list(ranges(w,h,d,n))
    need(rr[-1][2]+rr[-1][3]==len(source),"native_raw_range_extent")
    return sum(source[off:off+size]==back[off:off+size] for _,_,off,size in rr)

def gpu_summary(actual,expected,mode):
    rows=summarize(actual,expected,mode)
    correct=[x for m in rows for x in m["per_layer"]]
    wrong=[x for m in rows for x in m["reversed_layer_control"]]
    return {"per_mip":rows,"coordinates":sum(x["coordinates"] for x in correct),
            "RGBA_mismatches_over_1_div_255":sum(x["RGBA_mismatches_over_1_div_255"] for x in correct),
            "correct_layer_order_lower_error":sum(x["RGBA_mismatches_over_2_div_255"] for x in correct)<
              sum(x["RGBA_mismatches_over_2_div_255"] for x in wrong),
            "all_mip_GPU_RGBA_within_1e_5":all(x["rgb_mismatches_over_1e_5"]==0 and x["alpha_mismatches_over_1e_5"]==0 for x in correct)}

def read_reference_cases(rows):
    from tools.gt_top_resource_closure.selected_material_reference import CASES
    if not isinstance(rows,list) or len(rows)!=4 or [x.get("name") for x in rows]!=list(CASES):
        return {"status":"INCONCLUSIVE_CASES_MISSING"}
    flags=("material_loaded","shader_matches","has_property","serialized_texture_matches","runtime_texture_matches","source_yaml_unchanged")
    cases={row["name"]:{k:row.get(k) is True for k in flags} for row in rows}
    def base(row): return all(row[k] for k in ("material_loaded","shader_matches","has_property","source_yaml_unchanged"))
    good=[key for key,row in cases.items() if base(row) and row["runtime_texture_matches"] and row["serialized_texture_matches"]]
    negative=all(base(cases[k]) and not cases[k]["runtime_texture_matches"] and not cases[k]["serialized_texture_matches"] for k in ("wrong_guid","wrong_fileid"))
    return {"status":"OBSERVED" if all(base(x) for x in cases.values()) else "INCONCLUSIVE_IMPORT",
            "cases":cases,"both_negative_controls_rejected":negative,
            "native_type2_only_resolves":negative and good==["type2"],
            "original_type3_resolves":negative and "type3" in good,
            "positive_cases":good}

def srgb_transfer(x):
    y=x.copy()
    rgb=y[...,:3]
    y[...,:3]=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4)
    return y

def verify(a):
    result={"status":"INCONCLUSIVE","native_class187_identity":False,
            "native_all_22_ranges_exact":False,"actual_GPU_observation":False,
            "authored_reference_probe":False,"original_shader_draw_verified":False,
            "white_mesh_repair_verified":False,"Android_device":False,"production":False,
            "XAPK":False,"private_payload_published":False}
    try:
        root=a.private
        cfg=json.loads((root/"expected.json").read_text())
        need(cfg==json.loads((a.unity_project/"GTInput.json").read_text()) and cfg["run_id"]==a.run_id,
             "native_stage_run_mismatch")
        need((root/"editor-output-private").read_text().strip()==a.run_id and
             (root/"editor.log").is_file(),"native_private_log_guard")
        r=json.loads((root/"receipt.json").read_text())
        need(r["run_id"]==a.run_id and r["private_log_guard"],"native_receipt_run_mismatch")
        phase=r.get("phase")
        result["editor_phase"]=phase if phase in ("environment","private_guard","source","calibration","presave","authored_transfer","original_transfer","raw","gpu","reference","complete") else "unknown"
        result["editor_failure_category"]=r.get("failure_category") if r.get("failure_category") in FAILURE_TYPES else "other"
        result["original_transfer"]=safe_transfer(r.get("original_transfer"))
        result["authored_transfer"]=safe_transfer(r.get("authored_transfer"))
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear",
             "native_environment_not_admitted")
        src=(root/"array.bc3.bytes").read_bytes()
        need(len(src)==cfg["native_payload_bytes"]==2796256 and sha(src)==cfg["native_payload_sha256"],
             "native_raw_extent_or_stage_hash")
        cal=(root/"authored.bc3.bytes").read_bytes()
        need(cal==cal_payload() and sha(cal)==cfg["calibration_sha256"],"native_calibration_bytes_drift")
        if r.get("presave_raw_written") is True:
            matches=raw_matches(src,(root/"presave.bc3.bytes").read_bytes(),1024,1024,2,11)
            result.update(presave_native_ranges_exact=matches,presave_all_22_ranges_exact=matches==22)
        if r.get("authored_reload_raw_written") is True:
            matches=raw_matches(cal,(root/"authored-reload.bc3.bytes").read_bytes(),8,8,2,4)
            result.update(authored_reload_ranges_exact=matches,authored_reload_all_8_ranges_exact=matches==8)
        if r.get("calibration_written") is True:
            try:
                expected_cal=decoded(cal,8,8,2,4)
                cal_actual=[old.readback(root/("cal-%d.f32"%m),2,max(1,8>>m),max(1,8>>m)) for m in range(4)]
                mode=calibrate(cal_actual,expected_cal)
                result.update(BC3_calibration_orientation=mode,authored_wrong_mip_layer_orientation_distinguished=True)
                if r.get("authored_reload_gpu_written") is True:
                    loaded_cal=[old.readback(root/("authored-reload-%d.f32"%m),2,max(1,8>>m),max(1,8>>m)) for m in range(4)]
                    result["authored_reload_GPU_exact"]=all(np.max(np.abs(x-orient(y,mode)))<=1e-5 for x,y in zip(loaded_cal,expected_cal,strict=True))
                if r.get("presave_gpu_written") is True:
                    pre=[old.readback(root/("pre-mip-%d.f32"%m),2,max(1,1024>>m),max(1,1024>>m)) for m in range(11)]
                    result["presave_GPU"]=gpu_summary(pre,decoded(src,1024,1024,2,11),mode)
                    result["presave_GPU_observed"]=True
            except Exception as exc:
                result["presave_GPU_reason"]=str(exc) if isinstance(exc,old.Failure) else type(exc).__name__
        # Retain independent pre-save evidence even when post-save transfer fails.
        need(a.exit_code==0 and r["status"]=="OBSERVED","native_Unity_observation_inconclusive")
        need(result["original_transfer"]["accepted"] and r["guid"]==cfg["guid"] and r["file_id"]==cfg["file_id"]==18700000
             and r["native_importer"] and r["name_matches"] and (r["width"],r["height"],r["depth"],r["mip_count"])==(1024,1024,2,11)
             and r["graphics_format"]==100 and r["srgb"],"native_identity_descriptor_mismatch")
        result.update(native_class187_identity=True,source_format="BC3_SRGB",actual_graphics_format=r["graphics_format"],
                      actual_dimensions=[1024,1024,2],actual_mip_count=11,
                      source_ref_type=cfg["source_ref_type"],authored_reference_probe=r["reference_probe"],
                      authored_wrong_reference_rejected=r["wrong_reference_rejected"])
        back=(root/"native-readback.bc3.bytes").read_bytes()
        matches=raw_matches(src,back,1024,1024,2,11)
        result.update(native_ranges_compared=22,native_ranges_exact=matches,
                      native_all_22_ranges_exact=matches==22,native_original_bytes_compared=len(src))
        need(matches==22,"native_source_bytes_not_preserved")
        need(result["authored_transfer"]["accepted"] and result.get("authored_reload_all_8_ranges_exact") is True
             and result.get("authored_reload_GPU_exact") is True and result.get("presave_all_22_ranges_exact") is True
             and result.get("presave_GPU_observed") is True,"native_authored_transfer_or_presave_control_failed")
        mode=result["BC3_calibration_orientation"]
        actual=[old.readback(root/("mip-%d.f32"%m),2,max(1,1024>>m),max(1,1024>>m)) for m in range(11)]
        summary=gpu_summary(actual,decoded(src,1024,1024,2,11),mode)
        result.update(status="OBSERVED_NATIVE_BC3_ARRAY_ALL_MIPS",actual_GPU_observation=True,
                      actual_GPU_coordinates=summary["coordinates"],**{k:v for k,v in summary.items() if k!="coordinates"})
        # Compare actual per-coordinate float bytes, not just error totals.
        presave=[old.readback(root/("pre-mip-%d.f32"%m),2,max(1,1024>>m),max(1,1024>>m)) for m in range(11)]
        result["presave_postsave_GPU_exact_coordinates"]=sum(int(np.count_nonzero(np.all(x==y,axis=-1))) for x,y in zip(presave,actual,strict=True))
        result["selected_material_reference_differential"]=read_reference_cases(r.get("selected_material_cases"))
        if r.get("unorm_raw_written") is True:
            result["unorm_all_22_ranges_exact"]=raw_matches(src,(root/"unorm.bc3.bytes").read_bytes(),1024,1024,2,11)==22
        if result.get("unorm_all_22_ranges_exact") is True and r.get("unorm_gpu_written") is True:
            linear=[old.readback(root/("unorm-%d.f32"%m),2,max(1,1024>>m),max(1,1024>>m)) for m in range(11)]
            need(all(np.isfinite(x).all() and np.min(x)>=-1e-5 and np.max(x)<=1+1e-5 for x in linear),"unorm_samples_invalid")
            # Independent CPU UNorm reference: use raw BC3 DDS decoding without
            # sRGB transfer; keep GPU->GPU sRGB and CPU->UNorm errors distinct.
            cpu=[[] for _ in range(11)]
            for layer,m,off,size in ranges(1024,1024,2,11):
                img=layout.dds_bc3(src[off:off+size],max(1,1024>>m),max(1,1024>>m))
                cpu[m].append(np.asarray(img,dtype=np.float32)/255)
            cpu=[np.stack(x) for x in cpu]
            result["unorm_GPU_vs_CPU"]=gpu_summary(linear,cpu,mode)
            # Orient already-GPU-indexed values only once: both arrays are in
            # the same actual GPU order, not Pillow's coordinate order.
            result["srgb_GPU_vs_transferred_unorm_GPU"]=gpu_summary(actual,[srgb_transfer(x) for x in linear],"raw_first")
    except Exception as exc:
        result["reason"]=str(exc) if isinstance(exc,old.Failure) else type(exc).__name__
    old.write(a.safe,result)
    print("GT_SELECTED_NATIVE_ARRAY_RESULT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="OBSERVED_NATIVE_BC3_ARRAY_ALL_MIPS" else 2

def main():
    p=argparse.ArgumentParser()
    for k in ("private","unity-project","safe"): p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,default=1)
    return verify(p.parse_args())

if __name__=="__main__": raise SystemExit(main())
