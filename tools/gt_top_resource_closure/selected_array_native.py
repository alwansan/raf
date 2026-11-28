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
        result["editor_phase"]=phase if phase in ("environment","private_guard","source","save","reload","raw","gpu","calibration","reference","complete") else "unknown"
        need(a.exit_code==0 and r["status"]=="OBSERVED" and r["unity_version"]=="2021.3.45f2"
             and r["backend"]=="Vulkan" and r["color_space"]=="Linear","native_Unity_observation_inconclusive")
        need(r["guid"]==cfg["guid"] and r["file_id"]==cfg["file_id"]==18700000 and r["native_importer"]
             and r["name_matches"] and (r["width"],r["height"],r["depth"],r["mip_count"])==(1024,1024,2,11)
             and r["graphics_format"]==100 and r["srgb"],"native_identity_descriptor_mismatch")
        result.update(native_class187_identity=True,source_format="BC3_SRGB",actual_graphics_format=r["graphics_format"],
                      actual_dimensions=[1024,1024,2],actual_mip_count=11,
                      source_ref_type=cfg["source_ref_type"],authored_reference_probe=r["reference_probe"],
                      authored_wrong_reference_rejected=r["wrong_reference_rejected"])
        src=(root/"array.bc3.bytes").read_bytes()
        back=(root/"native-readback.bc3.bytes").read_bytes()
        need(len(src)==len(back)==cfg["native_payload_bytes"]==2796256 and sha(src)==cfg["native_payload_sha256"],
             "native_raw_extent_or_stage_hash")
        rr=list(ranges(1024,1024,2,11))
        matches=sum(src[off:off+size]==back[off:off+size] for _,_,off,size in rr)
        result.update(native_ranges_compared=len(rr),native_ranges_exact=matches,
                      native_all_22_ranges_exact=matches==22,native_original_bytes_compared=len(src))
        need(matches==22,"native_source_bytes_not_preserved")
        cal=(root/"authored.bc3.bytes").read_bytes()
        need(cal==cal_payload() and sha(cal)==cfg["calibration_sha256"],"native_calibration_bytes_drift")
        cal_actual=[old.readback(root/("cal-%d.f32"%m),2,max(1,8>>m),max(1,8>>m)) for m in range(4)]
        mode=calibrate(cal_actual,decoded(cal,8,8,2,4))
        actual=[old.readback(root/("mip-%d.f32"%m),2,max(1,1024>>m),max(1,1024>>m)) for m in range(11)]
        rows=summarize(actual,decoded(src,1024,1024,2,11),mode)
        all_rows=[x for m in rows for x in m["per_layer"]]
        wrong_rows=[x for m in rows for x in m["reversed_layer_control"]]
        result.update(status="OBSERVED_NATIVE_BC3_ARRAY_ALL_MIPS",actual_GPU_observation=True,
                      BC3_calibration_orientation=mode,authored_wrong_mip_layer_orientation_distinguished=True,
                      actual_GPU_coordinates=sum(x["coordinates"] for x in all_rows),per_mip=rows,
                      RGBA_mismatches_over_1_div_255=sum(x["RGBA_mismatches_over_1_div_255"] for x in all_rows),
                      correct_layer_order_lower_error=sum(x["RGBA_mismatches_over_2_div_255"] for x in all_rows)<
                      sum(x["RGBA_mismatches_over_2_div_255"] for x in wrong_rows),
                      all_mip_GPU_RGBA_within_1e_5=all(x["rgb_mismatches_over_1e_5"]==0 and x["alpha_mismatches_over_1e_5"]==0 for x in all_rows))
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
