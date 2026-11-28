"""Same-run Unity versus native Vulkan stage localization, not game acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_software_vulkan import private_command
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_source_format_pair import audit as previous
from tools.gt_fft_indexed_pair import audit as old

STATUS="OBSERVED_FFT_CROSS_BACKEND_LOCALIZATION"
STAGED="STAGED_FFT_CROSS_BACKEND"
PARTIAL="PARTIAL_FFT_CROSS_BACKEND_LOCALIZATION"
CASES=[(s,m) for s in (6,16) for m in ("signed","zero")]
LABELS=("indexed0","standalone0","indexed-chain","standalone-chain","indexed-cpu","standalone-cpu","indexed-replay","standalone-replay")
need=old.need
sha=old.sha
dump=old.dump

def write_exact(path,data):
    need(not path.exists() and len(data)==n.IMAGE_BYTES,"private_write_extent")
    path.write_bytes(data)
    return sha(path)

def classify_pair(raw,expected):
    p=n.profile(raw)
    need(p["written_pixels"]==n.COUNT,"snapshot_unwritten")
    return dict(profile=p,vs_cpu=n.compare(raw,expected))

def compare_case(data,expected):
    need(set(data)==set(LABELS) and len(expected)==2,"snapshot_population")
    out={k:classify_pair(data[k],expected[0 if k.endswith("0") else 1]) for k in LABELS}
    return dict(outputs=out,
        stage1_indexed_vs_standalone=n.compare(data["indexed0"],data["standalone0"]),
        indexed_chain_vs_own_replay=n.compare(data["indexed-chain"],data["indexed-replay"]),
        standalone_chain_vs_own_replay=n.compare(data["standalone-chain"],data["standalone-replay"]),
        indexed_vs_standalone_same_cpu_input=n.compare(data["indexed-cpu"],data["standalone-cpu"]))

def stage(src,managed,project,private,run_id):
    import UnityPy
    staged=previous.stage(src,managed,project,private,run_id)
    cfg=json.loads((private/"config.json").read_text())
    table=(private/"table-float.f32").read_bytes()
    need(hashlib.sha256(table).hexdigest()==n.TABLE_SHA,"table_digest")
    env=UnityPy.load(str(src/indexed.OWNER));obj=env.file.objects[indexed.PATH_ID]
    need(obj.type.name=="ComputeShader","typed_source")
    raw=obj.get_raw_data()
    need(hashlib.sha256(raw).hexdigest()==old.OBJECT_SHA,"object_digest")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"program_count")
    commitments={}
    host_device="unavailable"
    with tempfile.TemporaryDirectory(prefix="gt-fft-cross-") as folder:
        root=Path(folder);runner=n.build_host(root);control=n.canary(root,runner)
        modules={}
        for row in cfg["rows"]:
            i=row["slot"];rec=containers[i]
            blob=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
            need(hashlib.sha256(blob).hexdigest()==row["dxbc_sha256"]==rec["binary_sha256"],"program_digest")
            dx=root/f"slot{i}.dxbc";native=root/f"native{i}.spv";converted=root/f"round{i}.spv";dx.write_bytes(blob)
            private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(native),str(dx)])
            private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(converted),str(private/row["file"])])
            for p in (native,converted):private_command(["spirv-val","--target-env","vulkan1.1",str(p)])
            modules[i]=(native,converted)
        for mode in ("signed","zero"):
            name=f"source-{mode}.rgba32f";commitments[name]=write_exact(private/name,n.input_bytes(mode))
        for slot,mode in CASES:
            source=(private/f"source-{mode}.rgba32f").read_bytes()
            record,data=n.capture(runner,[*modules[slot],*modules[slot+1]],root/f"case-{slot}-{mode}",source,table)
            need(data is not None and all(x==n.CounterZero() for x in record["native_roundtrip"]),"oracle_program_disagreement")
            need(all(p["written_pixels"]==n.COUNT and all(v==0 for i,v in enumerate(p["class_counts"]) if i%4) for p in record["profiles"]),"oracle_nonfinite_or_unwritten")
            for p in (0,1):
                name=f"cpu-{slot}-{mode}-p{p}.rgba32f";commitments[name]=write_exact(private/name,data[p])
        try:
            info=subprocess.run(["vulkaninfo","--summary"],capture_output=True,text=True,timeout=30,check=False).stdout
            for line in info.splitlines():
                if re.match(r"\s*(driverName|driverInfo|deviceName)\s*=",line):
                    host_device=(host_device+"; "+line.strip())[:512]
        except (OSError,subprocess.TimeoutExpired):pass
    shutil.copyfile(Path(__file__).with_name("IndexedPair.cs"),project/"Assets/Editor/IndexedPair.cs")
    staged.update(status=STAGED,oracle_commitments=commitments,oracle_canary=control,host_device=host_device,
                  cross_editor_sha=sha(project/"Assets/Editor/IndexedPair.cs"),oracle_cases=len(CASES))
    return staged

def verify(project,private,s,run_id,outcome):
    cfg=private/"config.json";progress=old.bounded_progress(private,run_id)
    need(outcome=="success" and sha(cfg)==s["private_config_sha256"] and progress["private_launch_marker_matches"] is True and progress["editor_native_exit"]==0 and progress["last_managed_checkpoint"]["phase"]=="complete","editor_progress")
    r=json.loads((private/"receipt.json").read_text());m=json.loads(cfg.read_text())
    need(r["status"]=="PASS" and r["run_id"]==run_id and r["config_sha256"]==s["private_config_sha256"] and r["private_guard"] is True and r["vulkan"] is True and r["registration_count"]==20 and r["private_source_hashes_match"] is True,"editor_identity")
    need(sha(project/"Assets/Editor/IndexedPair.cs")==s["cross_editor_sha"] and sha(private/"table-float.f32")==m["table_float_sha"]==n.TABLE_SHA,"editor_source_table_identity")
    for name,digest in [("indexed.compute",m["indexed_sha"])]+[(x["file"],x["sha256"]) for x in m["rows"]]:
        need(sha(private/name)==sha(project/"Assets/Private"/name)==digest,"editor_program_identity")
    expected_names={f"source-{mode}.rgba32f" for mode in ("signed","zero")}|{f"cpu-{slot}-{mode}-p{p}.rgba32f" for slot,mode in CASES for p in (0,1)}
    need(set(s["oracle_commitments"])==expected_names,"oracle_population")
    for name,digest in s["oracle_commitments"].items():
        p=private/name;need(p.is_file() and not p.is_symlink() and p.stat().st_size==n.IMAGE_BYTES and sha(p)==digest,"oracle_commitment")
    cases=r["cases"];need([(x["first_slot"],x["input_mode"]) for x in cases]==CASES,"case_population")
    rows=[]
    for c in cases:
        slot,mode=c["first_slot"],c["input_mode"]
        need(c["outcome"] in ("OBSERVED","MANAGED_FAILURE","UNSUPPORTED") and c["format"]=="ARGBFloat" and c["seed"]==19,"case_identity")
        flags={k:c[k] for k in ("target_format_exact","input_gpu_exact","table_gpu_exact","injected_gpu_exact","replay_gpu_exact")}
        need(all(type(v) is bool for v in flags.values()),"case_flags")
        counts={k:c[k] for k in ("dispatches","bindings","sentinel_checks","snapshots")}
        need(all(type(v) is int and 0<=v<=(24 if k=="bindings" else 8) for k,v in counts.items()),"case_counts")
        data={}
        for label in LABELS:
            p=private/f"unity-{slot}-{mode}-{label}.rgba32f"
            if not p.exists():continue
            need(p.is_file() and not p.is_symlink() and p.stat().st_size==n.IMAGE_BYTES,"snapshot_extent")
            data[label]=p.read_bytes()
        need(tuple(data)==LABELS[:counts["snapshots"]],"snapshot_order_or_population")
        expected=[(private/f"cpu-{slot}-{mode}-p{p}.rgba32f").read_bytes() for p in (0,1)]
        common=dict(first_slot=slot,input_mode=mode,flags=flags,counts=counts,outcome=c["outcome"],failure_phase=c.get("failure_phase"),failure_type=c.get("failure_type"))
        if c["outcome"]=="OBSERVED":
            need(counts==dict(dispatches=8,bindings=24,sentinel_checks=8,snapshots=8) and all(flags.values()),"case_incomplete")
            rows.append(dict(**common,**compare_case(data,expected)))
        else:
            # Report only the verified prefix. Incomplete replay is NOT a pass.
            if data:need(flags["target_format_exact"] and flags["input_gpu_exact"] and flags["table_gpu_exact"],"partial_input_identity")
            rows.append(dict(**common,outputs={k:classify_pair(raw,expected[0 if k.endswith("0") else 1]) for k,raw in data.items()}))
    complete=sum(x["outcome"]=="OBSERVED" for x in rows)
    return dict(status=STATUS if complete==len(CASES) else PARTIAL,observed_cases=complete,outputs_per_case=len(LABELS),observed_outputs=sum(len(x["outputs"]) for x in rows),rows=rows,host_device=s["host_device"],unity_graphics_device_version=r["graphics_device_version"],oracle_canary=s["oracle_canary"],original_runtime_kernel_mapping_proven=False,original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)

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
    dump(a.out,result);print("GT_FFT_CROSS_BACKEND_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2

if __name__=="__main__":raise SystemExit(main())
