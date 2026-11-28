"""Capture the actual module at marked Unity Vulkan compute dispatches.

The layer observes command recording, while Unity synchronous readback establishes
completion of its own diagnostic invocation. No full descriptor binding or
compiler causality is inferred. Raw module and input files remain runner-local.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_original_fft_software_vulkan import private_command
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_bank_numeric import audit as numeric
from tools.gt_fft_cross_backend import audit as cross
from tools.gt_fft_indexed_pair import audit as old

STATUS="OBSERVED_LIVE_UNITY_VULKAN_MODULES"
STAGED="STAGED_LIVE_UNITY_MODULE_CAPTURE"
SLOTS=(6,7,16,17)
LABELS=("control",)+tuple(f"{v}-{s}" for s in SLOTS for v in ("indexed","standalone"))
need=old.need
sha=old.sha
dump=old.dump

def meta(text,label):
    parts=text.split()
    need(label in LABELS and len(parts)==6 and re.fullmatch(r"[A-Za-z0-9_-]{1,128}",parts[-1]) is not None,"capture_meta")
    need(all(re.fullmatch(r"[0-9]{1,9}",x) is not None for x in parts[:5]),"capture_meta_number")
    x,y,z,count,size=map(int,parts[:5])
    need((x,y,z)==((64,64,1) if label=="control" else (1,512,1)) and count<=4096 and size<=1048576,"capture_dispatch")
    return (x,y,z),count,size,parts[-1]

def profile(path,entry,group):
    need(path.is_file() and not path.is_symlink() and 20<=path.stat().st_size<=1048576,"module_extent")
    data=path.read_bytes();p=inspect(data)
    need(p["container"]=="SPIR-V" and p["entrypoint_execution_models"]=={5:1} and p["declared_local_workgroup_sizes"]==[list(group)],"module_group")
    val=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(path)],capture_output=True,timeout=30)
    dis=subprocess.run(["spirv-dis",str(path)],capture_output=True,timeout=30,check=True).stdout.decode()
    entries=re.findall(r'(?m)^\s*OpEntryPoint\s+GLCompute\s+%\S+\s+"([^"]+)"',dis)
    need(entries==[entry],"pipeline_entry_identity")
    try:images=image_resource_contracts(data)["typed_image_declarations"];image_status="observed"
    except ValueError:images=[];image_status="unclassified"
    return dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),version=p["version"],
        instructions=p["instruction_count"],local_size=list(group),validator_exit=val.returncode,
        image_status=image_status,images=images,opcode_profile=numeric.opcode_profile(dis))

def stage(src,managed,project,private,run_id):
    s=cross.stage(src,managed,project,private,run_id)
    cfg=json.loads((private/"config.json").read_text());refs={}
    for row in cfg["rows"]:
        slot=row["slot"];out=private/f"glslang-{slot}.spv"
        private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(out),str(private/row["file"])])
        refs[str(slot)]=profile(out,"main",(512,1,1))
        need(refs[str(slot)]["validator_exit"]==0,"reference_validator")
    (private/"vktrace").mkdir(mode=0o700)
    for name in ("IndexedPair.cs","Coordinate.compute"):
        shutil.copyfile(Path(__file__).with_name(name),project/"Assets/Editor"/name)
    s.update(status=STAGED,live_editor_sha=sha(project/"Assets/Editor/IndexedPair.cs"),
             coordinate_sha=sha(project/"Assets/Editor/Coordinate.compute"),reference_profiles=refs)
    return s

def captured(trace,label):
    stem=trace/label
    need(not stem.with_suffix(".duplicate").exists(),"ambiguous_dispatch_capture")
    m=stem.with_suffix(".meta")
    need(m.is_file() and not m.is_symlink() and 0<m.stat().st_size<=512,"missing_dispatch_metadata")
    groups,count,size,entry=meta(m.read_text(),label)
    p=profile(stem.with_suffix(".spv"),entry,(8,8,1) if label=="control" else (512,1,1))
    return dict(dispatch_groups=list(groups),specialization_entries=count,specialization_bytes=size,module=p)

def verify(project,private,s,run_id,outcome):
    cfg=private/"config.json";p=old.bounded_progress(private,run_id)
    need(outcome=="success" and sha(cfg)==s["private_config_sha256"] and p.get("private_launch_marker_matches") is True and p["editor_native_exit"]==0 and p["last_managed_checkpoint"] is not None and p["last_managed_checkpoint"]["phase"]=="complete","editor_progress")
    r=json.loads((private/"receipt.json").read_text());m=json.loads(cfg.read_text())
    need(r["status"]=="PASS" and r["run_id"]==run_id and r["config_sha256"]==s["private_config_sha256"] and r["private_guard"] is True and r["vulkan"] is True and r["registration_count"]==20 and r["private_source_hashes_match"] is True,"editor_identity")
    need(r["coordinate_control_verified"] is True and r["coordinate_control_pixels"]==n.COUNT and sha(project/"Assets/Editor/Coordinate.compute")==s["coordinate_sha"] and sha(project/"Assets/Editor/IndexedPair.cs")==s["live_editor_sha"],"editor_coordinate_control")
    need(sha(private/"table-float.f32")==m["table_float_sha"]==n.TABLE_SHA,"table_identity")
    for name,digest in [("indexed.compute",m["indexed_sha"])]+[(x["file"],x["sha256"]) for x in m["rows"]]:
        need(sha(private/name)==sha(project/"Assets/Private"/name)==digest,"program_source_identity")
    for name,digest in s["oracle_commitments"].items():
        need(sha(private/name)==digest,"oracle_commitment")
    for slot in SLOTS:
        need(sha(private/f"glslang-{slot}.spv")==s["reference_profiles"][str(slot)]["sha256"],"reference_module_commitment")
    trace=private/"vktrace";need(trace.is_dir() and not trace.is_symlink() and not (trace/"capture.marker").exists(),"trace_guard")
    entries={x.name for x in trace.iterdir()}
    allowed={f"{label}.{ext}" for label in LABELS for ext in ("spv","meta")}
    need(entries==allowed,"dispatch_capture_population")
    control=captured(trace,"control")
    need(control["module"]["validator_exit"]==0,"authored_capture_validator")
    cases=r["cases"];need([(c["first_slot"],c["input_mode"]) for c in cases]==[(6,"signed"),(16,"signed")],"case_population")
    rows=[]
    for c in cases:
        slot=c["first_slot"]
        need(c["outcome"]=="OBSERVED" and c["format"]=="ARGBFloat" and c["seed"]==19 and c["dispatches"]==4 and c["bindings"]==12 and c["sentinel_checks"]==4 and c["snapshots"]==4 and all(c[k] is True for k in ("input_gpu_exact","table_gpu_exact","target_format_exact","injected_gpu_exact")),"case_identity")
        for idx,label in enumerate(("indexed0","standalone0","indexed-cpu","standalone-cpu")):
            stage=idx//2;variant="standalone" if idx%2 else "indexed";kernel=slot+stage
            cap=captured(trace,f"{variant}-{kernel}")
            ref=s["reference_profiles"][str(kernel)]
            output=private/f"unity-{slot}-signed-{label}.rgba32f"
            need(output.is_file() and not output.is_symlink() and output.stat().st_size==n.IMAGE_BYTES,"capture_output_extent")
            expected=(private/f"cpu-{slot}-signed-p{stage}.rgba32f").read_bytes()
            measured=cross.classify_pair(output.read_bytes(),expected)
            rows.append(dict(slot=kernel,variant=variant,capture=cap,reference=ref,
                identical_module_sha=cap["module"]["sha256"]==ref["sha256"],
                image_abi_exact=cap["module"]["image_status"]==ref["image_status"]=="observed" and cap["module"]["images"]==ref["images"],
                output=measured))
    return dict(status=STATUS,recorded_compute_dispatches=len(rows),authored_control=control,coordinate_control_pixels=r["coordinate_control_pixels"],rows=rows,
                unity_device=r["graphics_device_name"],unity_api=r["graphics_device_version"],
                actual_descriptor_resource_mapping_verified=False,compiler_causality_proven=False,original_runtime_kernel_mapping_proven=False,
                original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage");v=sub.add_parser("verify")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    for q in (st,v):q.add_argument("--run-id",required=True)
    v.add_argument("--outcome",required=True)
    a=p.parse_args();result=dict(status="INCONCLUSIVE",water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id)
        else:result=verify(a.project,a.private,json.loads(a.stage.read_text()),a.run_id,a.outcome)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
        if a.action=="verify":
            trace=a.private/"vktrace"
            result["bounded_capture_presence"]={label:{ext:(trace/f"{label}.{ext}").is_file() for ext in ("spv","meta","duplicate")} for label in LABELS}
            result["editor_progress"]=old.bounded_progress(a.private,a.run_id)
    dump(a.out,result);print("GT_FFT_LIVE_MODULE_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2

if __name__=="__main__":raise SystemExit(main())
