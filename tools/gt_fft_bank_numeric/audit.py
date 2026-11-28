"""Separate FFT bank numerical diagnostic: IEEE class vs finite value differences.
Retain the previous original-source table/format result without calling NaN equality
a numeric match. Authored controls do not prove original game inputs or selection.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from scripts import probe_original_fft_caller_graph as caller
from scripts import probe_original_fft_kernel_callsites as calls
from scripts import verify_original_butterfly_numeric as numeric
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.probe_original_compute_containers import scan_blob
from scripts.instrument_android_runtime_operations import body_bounds
from tools.gt_fft_source_format_pair import audit as previous
from tools.gt_fft_indexed_pair import audit as old
STATUS="OBSERVED_FFT_BANK_IEEE_NUMERIC_DIAGNOSTIC"
MODES=("signed","zero","positive","zero_ba","zero_alpha","zero_blue")
SIZE=512
def need(ok,reason):old.need(ok,reason)
def sha(p):return old.sha(p)
def dump(p,o):old.dump(p,o)
def bank_contract(dx,gpu,waves):
    # Read only the authenticated callers. Distinguish direct forwarding,
    # inversion and unresolved expressions, never guess a semantic mapping.
    d=[x for x in caller.source_declarations(dx) if x["name"]=="Dx11FFT"]
    g=[x for x in caller.source_declarations(gpu) if x["name"]=="GpuFFT"]
    need(len(d)==len(g)==1 and len(d[0]["params"])==len(g[0]["params"])==4,"constructor_population")
    def ids(params):
        return [p.strip().split()[-1] for p in params]
    dp,gp=ids(d[0]["params"]),ids(g[0]["params"])
    a,b=body_bounds(waves,"private GpuFFT ChooseBestFFTAlgorithm(bool twoChannels)")
    body=waves[a:b];masked=calls.mask_noncode(body)
    sites=list(re.finditer(r"\bnew\s+Dx11FFT\s*\(",masked))
    need(len(sites)==1,"caller_population")
    args,_=calls.parse_original_args(body,sites[0].end()-1);need(len(args)==4,"caller_arity")
    init=list(re.finditer(r":\s*base\s*\(",calls.mask_noncode(dx)))
    need(len(init)==1,"base_population")
    forwarded,_=calls.parse_original_args(dx,init[0].end()-1);need(len(forwarded)==4,"base_arity")
    def relation(value,name):
        value=re.sub(r"\s+","",value)
        if value==name:return "direct"
        if value=="!"+name:return "inverted"
        if value in ("true","false"):return "constant_"+value
        return "other"
    def base_field(field):
        matches=list(re.finditer(r"\b"+re.escape(field)+r"\s*=\s*([A-Za-z_]\w*)\s*;",calls.mask_noncode(gpu)))
        if len(matches)!=1 or matches[0][1] not in gp:return None
        return gp.index(matches[0][1])
    rel={key:[relation(x,dp[3]) for x in forwarded] for key in ("fourth_to_base",)}
    rel.update(caller_fourth_to_two_channels=relation(args[3],"twoChannels"),
               base_two_channels_parameter=base_field("_TwoChannels"),
               base_high_precision_parameter=base_field("_HighPrecision"))
    for field in ("two_channels","high_precision"):
        pos=rel["base_"+field+"_parameter"]
        rel["bank_to_"+field]=None if pos is None else rel["fourth_to_base"][pos]
    return rel
OPS=("OpBitcast","OpConvertFToS","OpConvertFToU","OpConvertSToF","OpConvertUToF","OpFDiv",
     "OpFAdd","OpFSub","OpFMul","OpImageFetch","OpImageRead","OpImageWrite","OpExtInst",
     "OpShiftLeftLogical","OpShiftRightLogical","OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor")
def opcode_profile(text):
    counts=Counter(re.findall(r"\b(Op[A-Za-z0-9]+)\b",text))
    ext=Counter(re.findall(r"\bOpExtInst\s+%\S+\s+%\S+\s+([A-Za-z0-9]+)\b",text))
    return {"ops":{k:counts[k] for k in OPS},"ext":{k:ext[k] for k in ("Sqrt","InverseSqrt","FMin","FMax","FClamp","FAbs","Fma","Sin","Cos","Exp","Log","Pow","Fract","Floor","Ceil")}}
def source_profiles(src,private):
    import UnityPy
    env=UnityPy.load(str(src/indexed.OWNER));raw=env.file.objects[indexed.PATH_ID].get_raw_data()
    need(hashlib.sha256(raw).hexdigest()==previous.old.OBJECT_SHA,"source_object_digest")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"source_program_count")
    cfg=json.loads((private/"config.json").read_text())
    out=[]
    with tempfile.TemporaryDirectory(prefix="gt-fft-op-profile-",dir=private.parent) as tmp:
        root=Path(tmp)
        for row in cfg["rows"]:
            i=row["slot"];rec=containers[i];data=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
            need(hashlib.sha256(data).hexdigest()==row["dxbc_sha256"]==rec["binary_sha256"],"source_program_digest")
            dx=root/"orig.dxbc";spv=root/"orig.spv";asm=root/"orig.asm";ref=root/"ref.spv";rasm=root/"ref.asm"
            dx.write_bytes(data)
            private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(spv),str(dx)])
            private_command(["spirv-val","--target-env","vulkan1.1",str(spv)])
            private_command(["spirv-dis",str(spv),"-o",str(asm)])
            private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(ref),str(private/row["file"])])
            private_command(["spirv-val","--target-env","vulkan1.1",str(ref)])
            private_command(["spirv-dis",str(ref),"-o",str(rasm)])
            out.append(dict(slot=i,native=opcode_profile(asm.read_text()),roundtrip=opcode_profile(rasm.read_text())))
    return out
def stage(src,managed_root,project,private,run_id):
    dx=previous.source(managed_root,"Dx11FFT",previous.managed.ORIGINAL_SOURCE_SHA256["Dx11FFT"])
    gpu=previous.source(managed_root,"GpuFFT",numeric.PINS["GpuFFT"])
    waves=previous.source(managed_root,"WavesRendererFFT",previous.managed.ORIGINAL_SOURCE_SHA256["WavesRendererFFT"])
    bank=bank_contract(dx,gpu,waves)
    out=previous.stage(src,managed_root,project,private,run_id)
    profiles=source_profiles(src,private)
    shutil.copyfile(Path(__file__).with_name("IndexedPair.cs"),project/"Assets/Editor/IndexedPair.cs")
    shutil.copyfile(Path(__file__).with_name("Classify.compute"),project/"Assets/Editor/Classify.compute")
    out.update(status="STAGED_FFT_BANK_IEEE_DIAGNOSTIC",source_bank_relation=bank,source_opcode_profiles=profiles,
               class_control_sha256=sha(project/"Assets/Editor/Classify.compute"),authored_input_modes=list(MODES))
    return out
def verify(r,s,run_id,outcome,progress):
    need(outcome=="success" and r["status"]=="PASS" and r["run_id"]==run_id and
         r["config_sha256"]==s["private_config_sha256"] and r["private_guard"] is True and
         r["vulkan"] is True and r["registration_count"]==20 and r["private_source_hashes_match"] is True and
         r["class_control_verified"] is True and r["class_control_pixels"]==SIZE*SIZE and
         r["class_control_sha256"]==s["class_control_sha256"] and progress["editor_native_exit"]==0 and
         progress["last_managed_checkpoint"]["phase"]=="complete","editor_identity_or_class_control")
    cases=r["cases"]
    need(len(cases)==12 and [(x["first_slot"],x["input_mode"]) for x in cases]==[(i,m) for i in (6,16) for m in MODES],"case_population")
    good=0;nonfinite=0;class_diff=0
    for c in cases:
        need(c["outcome"] in ("OBSERVED","UNSUPPORTED","MANAGED_FAILURE"),"case_outcome")
        if c["outcome"]!="OBSERVED":continue
        need(c["format"]=="ARGBFloat" and c["target_format_exact"] is True and c["table_gpu_exact"] is True and
             c["input_gpu_exact"] is True and c["dispatches"]==4 and c["bindings"]==12 and c["sentinel_checks"]==4 and
             c["indexed_written"]==c["reference_written"]==[SIZE*SIZE,SIZE*SIZE] and c["coverage_mismatch"]==[0,0],"case_coverage")
        keys=("indexed_class_counts","reference_class_counts")
        for key in keys:
            counts=c[key];need(len(counts)==32 and all(type(x) is int and 0<=x<=SIZE*SIZE for x in counts),"class_count")
            need(all(sum(counts[i:i+4])==SIZE*SIZE for i in range(0,32,4)),"class_partition")
        for key in ("class_mismatch","native_vs_converted_class_mismatch","gpu_vs_native_class_mismatch","finite_different","finite_over_tolerance","raw_bit_different"):
            need(len(c[key])==2 and all(type(x) is int and 0<=x<=4*SIZE*SIZE for x in c[key]),"comparison_count")
        need(c["native_vs_converted_class_mismatch"]==c["gpu_vs_native_class_mismatch"]==[0,0],"class_transport_mismatch")
        for p in range(2):
            n=sum(c["indexed_class_counts"][p*16+i]+c["reference_class_counts"][p*16+i] for i in range(16) if i%4!=0)
            need(c["class_mismatch"][p]<=n and c["finite_over_tolerance"][p]<=c["finite_different"][p],"comparison_bounds")
            nonfinite+=n
        class_diff+=sum(c["class_mismatch"]);good+=1
    need(good>0,"no_bank_cases_observed")
    return dict(status=STATUS,observed_cases=good,cases=cases,total_nonfinite_lane_observations=nonfinite,
                total_class_mismatch_lanes=class_diff,class_control_verified=True,class_control_pixels=r["class_control_pixels"],
                original_game_inputs_verified=False,original_runtime_kernel_mapping_proven=False,
                original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False,
                editor_progress=progress)
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True);st=sub.add_parser("stage")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    st.add_argument("--run-id",required=True);v=sub.add_parser("verify")
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--run-id",required=True);v.add_argument("--outcome",required=True)
    a=p.parse_args();result=dict(status="INCONCLUSIVE",water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id)
        else:
            s=json.loads(a.stage.read_text());cfg=a.private/"config.json";progress=old.bounded_progress(a.private,a.run_id);result["editor_progress"]=progress
            need(sha(cfg)==s["private_config_sha256"] and progress.get("private_launch_marker_matches") is True and progress["private_files_present"]["receipt.json"],"private_editor_commitment")
            r=json.loads((a.private/"receipt.json").read_text());result["editor_receipt"]=r;m=json.loads(cfg.read_text())
            for name,digest in [("indexed.compute",m["indexed_sha"])]+[(x["file"],x["sha256"]) for x in m["rows"]]:
                need(sha(a.private/name)==sha(a.project/"Assets/Private"/name)==digest,"editor_program_bytes_changed")
            need(sha(a.private/"table-float.f32")==m["table_float_sha"] and sha(a.project/"Assets/Editor/Classify.compute")==s["class_control_sha256"],"diagnostic_input_changed")
            result=verify(r,s,a.run_id,a.outcome,progress)
    except Exception as exc:
        result["failure_type"]=type(exc).__name__
        if isinstance(exc,ValueError) and re.fullmatch(r"[a-z_]+",str(exc)):result["failure_reason"]=str(exc)
    dump(a.out,result);print("GT_FFT_BANK_NUMERIC_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("STAGED_FFT_BANK_IEEE_DIAGNOSTIC",STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
