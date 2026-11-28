"""Independent same-image replay of exact live Unity VkComputePipeline modules.

No rewritten module, source data, actual runtime mapping or game acceptance.
Each slot uses four independent dispatches with the same exact source and table.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from scripts.probe_original_fft_software_vulkan import private_command
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_same_image import audit as same

STATUS="OBSERVED_LIVE_UNITY_MODULE_REPLAY"
STAGED="STAGED_LIVE_UNITY_MODULE_REPLAY"
need=live.need
sha=live.sha
dump=live.dump
MARKER="GT_FFT_LIVE_REPLAY exact_mapped_inputs=true independent_dispatches=4 four_raw_outputs=true"
FILES=("native0","round0","native1","round1")

def render_host(source):
    s=n.render_host(source)
    s=n.replace(s,"const std::array<int,4> passSource={0,0,2,4};","const std::array<int,4> passSource={0,0,0,0};")
    # Keep exactly the original four destination images, host-write and
    # compute-to-host barriers. No chained stage/intermediate reads.
    start=s.index("        if(i==2) {")
    end=s.index("        vkCmdBindPipeline",start)
    need(s[start:end].count("vkCmdPipelineBarrier")==1,"host_chain_anchor")
    s=s[:start]+s[end:]
    s=n.replace(s,'stage.pName="main";',r'''stage.pName="main";
        std::ifstream entryFile("entry-"+std::to_string(i)+".txt");
        std::string entry,extra;
        require(bool(entryFile>>entry) && !(entryFile>>extra) && !entry.empty() && entry.size()<=128,"Exact replay entry file");
        stage.pName=entry.c_str();''')
    s=n.replace(s,"GT_FFT_NATIVE_HOST exact_mapped_inputs=true intermediate_barrier=true four_raw_outputs=true",MARKER)
    return s

def stage(src,managed,project,private,run_id):
    s=live.stage(src,managed,project,private,run_id)
    s.update(status=STAGED,editor_image_id=same.image_id())
    return s

def run_capture(runner,root,modules,entries,source,table):
    need(len(modules)==len(entries)==4 and len(source)==n.IMAGE_BYTES and len(table)==n.TABLE_BYTES,"replay_inputs")
    need(all(re.fullmatch(r"[A-Za-z0-9_-]{1,128}",x) is not None for x in entries),"replay_entries")
    root.mkdir(mode=0o700)
    commits=[sha(p) for p in modules]
    (root/"source.rgba32f").write_bytes(source);(root/"butterfly.rgba32f").write_bytes(table)
    for i,entry in enumerate(entries):(root/f"entry-{i}.txt").write_text(entry+"\n")
    with (root/"driver.log").open("wb") as log:
        p=subprocess.run([str(runner),*[str(x) for x in modules],"512","512","19","512","rgba32f"],
                         cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    need(p.returncode==0,"independent_replay_process")
    need((root/"driver.log").read_text(errors="replace").count(MARKER)==1,"independent_replay_marker")
    need([sha(x) for x in modules]==commits and (root/"source.rgba32f").read_bytes()==source and (root/"butterfly.rgba32f").read_bytes()==table,"replay_commitments")
    need(all((root/f"entry-{i}.txt").read_text()==e+"\n" for i,e in enumerate(entries)),"replay_entry_changed")
    outputs=[]
    for name in FILES:
        file=root/(name+".rgba32f")
        need(file.is_file() and not file.is_symlink() and file.stat().st_size==n.IMAGE_BYTES,"replay_extent")
        data=file.read_bytes()
        need(n.profile(data)["written_pixels"]==n.COUNT,"replay_unwritten")
        outputs.append(data)
    return outputs

def canary(root,runner):
    # Same source and table to all four destinations. Distinct wrong program
    # must be detected; duplicate references must be exact, not merely finite.
    modules=[]
    for name,code in (("add",n.GLSL),("sub",n.GLSL.replace(" + texelFetch"," - texelFetch"))):
        p=root/(name+".comp");q=root/(name+".spv");p.write_text(code)
        private_command(["glslangValidator","-V","-S","comp","-o",str(q),str(p)])
        private_command(["spirv-val","--target-env","vulkan1.1",str(q)])
        modules.append(q)
    add,sub=modules
    table=struct.pack("<4f",.25,.5,.75,1)*n.SIZE*n.STAGES
    src=n.input_bytes("zero")
    raw=run_capture(runner,root/"canary",[add,sub,add,add],["main"]*4,src,table)
    plus=struct.pack("<4f",.25,.5,.75,1)*n.COUNT
    minus=struct.pack("<4f",-.25,-.5,-.75,-1)*n.COUNT
    need(raw==[plus,minus,plus,plus],"replay_control_values")
    wrong=n.compare(raw[0],raw[1])
    need(wrong["finite_over_tolerance"]==n.COUNT*4,"replay_wrong_program_control")
    return dict(status="PASS",independent_outputs=4,exact_pixels_each=n.COUNT,wrong_program_lanes=wrong["finite_over_tolerance"])

def mount_modules(root,slot,modules):
    # Docker sees only this scratch root, never the project/private tree.
    # Preserve exact bytes including entry strings and original module hashes.
    folder=root/f"modules-{slot}";folder.mkdir(mode=0o700)
    result={}
    for variant,source in modules.items():
        need(variant in ("reference","indexed","standalone"),"replay_module_role")
        dest=folder/(variant+".spv")
        data=source.read_bytes()
        need(20<=len(data)<=1048576,"replay_copy_extent")
        dest.write_bytes(data)
        need(sha(dest)==sha(source),"replay_copy_identity")
        result[variant]=dest
    return result

def replay_slot(root,runner,private,slot,rows):
    first=slot-slot%2
    stage=slot-first
    source=(private/("source-signed.rgba32f" if stage==0 else f"cpu-{first}-signed-p0.rgba32f")).read_bytes()
    expected=(private/f"cpu-{first}-signed-p{stage}.rgba32f").read_bytes()
    table=(private/"table-float.f32").read_bytes()
    need(hashlib.sha256(table).hexdigest()==n.TABLE_SHA,"replay_table_identity")
    modules={"reference":private/f"glslang-{slot}.spv"}
    entries={"reference":"main"}
    for variant in ("indexed","standalone"):
        row=rows[variant];label=f"{variant}-{slot}"
        trace=private/"vktrace"
        mod=trace/f"{label}.spv"
        groups,count,size,entry=live.meta((trace/f"{label}.meta").read_text(),label)
        need(count==size==0 and groups==(1,512,1),"replay_specialization_or_groups")
        need(row["image_abi_exact"] and row["capture"]["module"]["validator_exit"]==0 and sha(mod)==row["capture"]["module"]["sha256"],"replay_live_module_identity")
        modules[variant]=mod;entries[variant]=entry
    need(sha(modules["reference"])==rows["indexed"]["reference"]["sha256"]==rows["standalone"]["reference"]["sha256"],"replay_reference_identity")
    original_modules=modules
    modules=mount_modules(root,slot,original_modules)
    orders=[("reference","indexed","standalone","reference"),("reference","standalone","indexed","reference")]
    results=[]
    for repeat,order in enumerate(orders):
        data=run_capture(runner,root/f"slot-{slot}-{repeat}",[modules[v] for v in order],[entries[v] for v in order],source,table)
        need(data[0]==data[3]==expected,"replay_reference_oracle")
        results.append(dict(zip(order,data,strict=True)))
    need(all(sha(modules[v])==sha(original_modules[v]) for v in modules),"replay_original_module_changed")
    variants={}
    for variant in ("indexed","standalone"):
        label=("indexed0" if variant=="indexed" else "standalone0") if stage==0 else f"{variant}-cpu"
        unity=(private/f"unity-{first}-signed-{label}.rgba32f").read_bytes()
        a,b=[r[variant] for r in results]
        variants[variant]=dict(module_sha256=sha(modules[variant]),profile=n.profile(a),
            vs_reference=n.compare(a,expected),vs_unity=n.compare(a,unity),
            repeat=n.compare(a,b),second_profile=n.profile(b),
            second_vs_reference=n.compare(b,expected),second_vs_unity=n.compare(b,unity))
    return dict(slot=slot,input_role="signed" if stage==0 else "reference_first_stage",
                reference_outputs_exact=4,dispatches=8,variants=variants,
                indexed_vs_standalone=n.compare(results[0]["indexed"],results[0]["standalone"]))

def verify(project,private,s,run_id,outcome,receipt=None):
    if receipt is None:receipt=live.verify(project,private,s,run_id,outcome)
    need(receipt["status"]==live.STATUS and receipt["recorded_compute_dispatches"]==8,"live_capture_incomplete")
    image=same.image_id();need(image==s["editor_image_id"],"editor_image_changed")
    with tempfile.TemporaryDirectory(prefix="gt-fft-live-replay-") as tmp:
        root=Path(tmp)
        (root/"host.cpp").write_text(render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()))
        runner,device=same.image_runner(root,image)
        need(device["deviceName"].strip().lower()==receipt["unity_device"].strip().lower(),"editor_replay_device")
        control=canary(root,runner)
        rows=[]
        for slot in live.SLOTS:
            selected={r["variant"]:r for r in receipt["rows"] if r["slot"]==slot}
            need(set(selected)=={"indexed","standalone"},"live_row_population")
            rows.append(replay_slot(root,runner,private,slot,selected))
    return dict(status=STATUS,live_capture=receipt,editor_image_id=image,replay_device=device,
                canary=control,rows=rows,observed_slots=len(rows),independent_dispatches=sum(r["dispatches"] for r in rows),
                reference_outputs_exact=sum(r["reference_outputs_exact"] for r in rows),
                actual_descriptor_resource_mapping_verified=False,compiler_causality_proven=False,
                original_runtime_kernel_mapping_proven=False,original_fft_numeric_parity_verified=False,
                water_rendering_verified=False,android_device=False,production=False,XAPK=False)

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
        else:
            staged=json.loads(a.stage.read_text())
            receipt=live.verify(a.project,a.private,staged,a.run_id,a.outcome)
            result["live_capture"]=receipt
            result=verify(a.project,a.private,staged,a.run_id,a.outcome,receipt)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    dump(a.out,result);print("GT_FFT_LIVE_REPLAY_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2

if __name__=="__main__":raise SystemExit(main())
