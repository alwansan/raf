"""Source-only indexed candidate: 20 original-derived kernel entries, four chained cases."""
import argparse
import json
from pathlib import Path
import re
import shutil
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_compiler_directive import audit as directive
from tools.gt_fft_reference_swap import audit as prior
from tools.gt_fft_cross_backend import audit as cross
from tools.gt_fft_native_bank_oracle import audit as n
from scripts import gt_stage_indexed_fft_candidate as indexed

STATUS="OBSERVED_INDEXED_DXC_CHAIN"
STAGED="STAGED_INDEXED_DXC_CHAIN"
need=live.need
sha=live.sha
dump=live.dump
STANDALONE_PINS={
    "6": "603131440ab8d589188e68e81aadd58bcbd1f9140668100152dd69a1d73898b6",
    "7": "69b3b31d43f4f8bac9bb5ac85a1ff1beee6e5cc27cb34b79b592603b27425427",
    "16": "835a6305b39217df9ec3818741f4559e47f6a4f3e043bca25f942a3f7e79d871",
    "17": "abb004e74422b68771d59b944142a9a4b689ed82fd628fd93b0fd5b55c3014e7"
}

def indexed_source(data):
    need(type(data) is bytes and 0<len(data)<20*524352 and b"\x00" not in data
        and b"#pragma use_dxc" not in data and b"#pragma never_use_dxc" not in data,"indexed_source_extent")
    declarations=b"".join(f"#pragma kernel {indexed.entry(i)} RAFT_FFT_SLOT={i}\n".encode() for i in range(20))
    need(data.startswith(declarations+b"\n") and data.count(b"#pragma kernel ")==20,"indexed_kernel_identity")
    return directive.DIRECTIVE+data

def strip_indexed(data):
    need(data.startswith(directive.DIRECTIVE) and data.count(directive.DIRECTIVE)==1,"indexed_directive_identity")
    original=data[len(directive.DIRECTIVE):]
    need(indexed_source(original)==data,"indexed_reverse")
    return original

def stage(src,managed,project,private,run_id):
    s=directive.stage(src,managed,project,private,run_id)
    cfg=private/"config.json";m=json.loads(cfg.read_text())
    p=private/"indexed.compute";original=p.read_bytes()
    before=sha(p);need(before==m["indexed_sha"],"indexed_original_sha")
    data=indexed_source(original);need(strip_indexed(data)==original,"indexed_source_reversal")
    p.write_bytes(data);m["indexed_sha"]=sha(p);dump(cfg,m)
    shutil.copyfile(Path(__file__).with_name("IndexedPair.cs"),project/"Assets/Editor/IndexedPair.cs")
    s.update(status=STAGED,private_config_sha256=sha(cfg),cross_editor_sha=sha(project/"Assets/Editor/IndexedPair.cs"),
             indexed_original_sha=before,indexed_directive_sha=m["indexed_sha"],standalone_pins=STANDALONE_PINS)
    return s

def verify(project,private,s,run_id,outcome):
    result=cross.verify(project,private,s,run_id,outcome)
    need(result["status"]==cross.STATUS and result["observed_cases"]==4 and result["observed_outputs"]==32,"chained_case_population")
    cfg=json.loads((private/"config.json").read_text())
    p=private/"indexed.compute"
    need(sha(p)==cfg["indexed_sha"]==s["indexed_directive_sha"] and directive.digest(strip_indexed(p.read_bytes()))==s["indexed_original_sha"],"indexed_source_identity")
    need(s["standalone_pins"]==STANDALONE_PINS and s["capture_layer_only"] is True and not (private/"replacements").exists(),"capture_only_guard")
    originals={r["slot"]:r for r in s["source_directive_rows"]}
    for row in cfg["rows"]:
        record=originals[row["slot"]];p=private/row["file"]
        need(sha(p)==record["directive_sha"]==row["sha256"] and directive.digest(directive.strip_directive(p.read_bytes()))==record["original_sha"],"standalone_source_identity")
    r=json.loads((private/"receipt.json").read_text())
    need(r["coordinate_control_verified"] is True and r["coordinate_control_pixels"]==n.COUNT and sha(project/"Assets/Editor/Coordinate.compute")==s["coordinate_sha"],"coordinate_control")
    trace=private/"vktrace"
    need(trace.is_dir() and not trace.is_symlink() and {p.name for p in trace.iterdir()}=={f"{label}.{ext}" for label in live.LABELS for ext in ("spv","meta")},"trace_population")
    control=live.captured(trace,"control")
    need(control["module"]["validator_exit"]==0,"coordinate_module_validator")
    modules=[]
    for slot in live.SLOTS:
        for variant in ("indexed","standalone"):
            label=f"{variant}-{slot}";cap=live.captured(trace,label)
            need(cap["module"]["validator_exit"]==0 and cap["specialization_entries"]==cap["specialization_bytes"]==0,"module_validation")
            gen=directive.generator(trace/(label+".spv"))
            old=prior.PINS[label]
            mod=cap["module"]["sha256"]
            modules.append(dict(slot=slot,variant=variant,capture=cap,generator=gen,changed_from_old=mod!=old,
                prior_standalone_pin_exact=mod==STANDALONE_PINS[str(slot)] if variant=="standalone" else None))
    exact=0;within=0
    for case in result["rows"]:
        for output in case["outputs"].values():
            exact+=int(output["vs_cpu"]==n.CounterZero())
            within+=int(output["vs_cpu"]["class_mismatch"]==0 and output["vs_cpu"]["finite_over_tolerance"]==0)
    comparisons_exact=all(c[k]==n.CounterZero() for c in result["rows"] for k in (
        "stage1_indexed_vs_standalone","indexed_chain_vs_own_replay","standalone_chain_vs_own_replay","indexed_vs_standalone_same_cpu_input"))
    return dict(status=STATUS,chain=result,modules=modules,coordinate_control_pixels=r["coordinate_control_pixels"],
        registered_kernels=r["registration_count"],validated_marked_modules=len(modules),
        generator_14_modules=sum(m["generator"]["tool_id"]==14 for m in modules),
        indexed_modules_changed=sum(m["variant"]=="indexed" and m["changed_from_old"] for m in modules),
        prior_standalone_modules_exact=sum(m["prior_standalone_pin_exact"] is True for m in modules),
        exact_outputs=exact,within_tolerance_outputs=within,all_pair_replay_comparisons_exact=comparisons_exact,
        isolated_indexed_chained_parity=(exact==32 and comparisons_exact),
        original_runtime_kernel_mapping_proven=False,original_fft_numeric_parity_verified=False,
        actual_descriptor_resource_mapping_verified=False,water_rendering_verified=False,
        android_device=False,production=False,XAPK=False)

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
        if a.action=="verify":result.update(directive.failure_receipt(a.private,a.run_id))
    dump(a.out,result);print("GT_FFT_INDEXED_DXC_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
