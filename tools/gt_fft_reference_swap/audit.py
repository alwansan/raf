"""Private SHA-gated reference intervention, NOT a production shader replacement."""
import argparse
import json
from pathlib import Path
import re
import shutil
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_native_bank_oracle import audit as n

STATUS="OBSERVED_REFERENCE_MODULE_INTERVENTION"
STAGED="STAGED_REFERENCE_MODULE_INTERVENTION"
need=live.need
sha=live.sha
dump=live.dump
PINS={
    "indexed-6": "318274401b9721b27aab52cb9059dbcb631f6bcb8783a90e13981b19ccddff87",
    "standalone-6": "b4a8855a5582783bb3d022acca5bec021115ee585e7f4ed9419ce4a7fde2aa15",
    "indexed-7": "fa3b3a57b0c6209f5027258d7c978c373efdd00f2c042a264c00059208b24ab0",
    "standalone-7": "32546cba35a7ba8a2bc82a1249045adfb9b4a665d210f6d13327080ee6c444ae",
    "indexed-16": "971fe6f45d33ac8b84a9482a3bf6b78dc725e369ad0c85b581f59847b91f1039",
    "standalone-16": "802792ed235a61d8ec470269ef5d4f511d06591bf4f0f875a9a10abd65bd051a",
    "indexed-17": "d40bf6306722063d6624929c06aaab013b76b96332478e190586bd9ea3f8cf8c",
    "standalone-17": "a7e37a98cff58f394bccbfbae6c0169038e2a180e2d0977937d25ad0aea083b7"
}
REFERENCES={
    "6": "48e77448dc7b1680375da32b548f2d1084d4548705ccadf01a609cdf44ac9853",
    "7": "347edc99040311926102fbb0298a48801d490ebe22edda798574955e3a3ea348",
    "16": "ef032bd7551141cdb5e0dc04398195c3e8ddcd5156a38ba3385efc992f512c16",
    "17": "4fffa57637741a49ff2b40900454e59c344c4aba5cf27f80bdf3dd239c635957"
}

def map_lines():
    return "".join(f"{PINS['standalone-'+str(slot)]} {REFERENCES[str(slot)]} {slot}\n" for slot in live.SLOTS)

def stage(src,managed,project,private,run_id):
    result=live.stage(src,managed,project,private,run_id)
    folder=private/"replacements";folder.mkdir(mode=0o700)
    for slot in live.SLOTS:
        path=private/f"glslang-{slot}.spv"
        expected=REFERENCES[str(slot)]
        need(sha(path)==expected==result["reference_profiles"][str(slot)]["sha256"],"reference_pin")
        dest=folder/f"slot-{slot}.spv";shutil.copyfile(path,dest)
        need(sha(dest)==expected,"reference_copy")
    (folder/"map.txt").write_text(map_lines())
    result.update(status=STAGED,swap_map_sha=sha(folder/"map.txt"),reference_pins=REFERENCES,baseline_pins=PINS)
    return result

def verify(project,private,s,run_id,outcome,receipt=None):
    if receipt is None:receipt=live.verify(project,private,s,run_id,outcome)
    need(receipt["recorded_compute_dispatches"]==8 and receipt["status"]==live.STATUS,"live_dispatch_count")
    folder=private/"replacements"
    need(folder.is_dir() and not folder.is_symlink() and (folder/"map.txt").read_text()==map_lines() and sha(folder/"map.txt")==s["swap_map_sha"] and s["reference_pins"]==REFERENCES and s["baseline_pins"]==PINS,"swap_map_identity")
    rows=[]
    for slot in live.SLOTS:
        need(sha(folder/f"slot-{slot}.spv")==REFERENCES[str(slot)],"replacement_bytes")
        indexed,standalone=[next(r for r in receipt["rows"] if r["slot"]==slot and r["variant"]==v) for v in ("indexed","standalone")]
        need(all(r["image_abi_exact"] and r["capture"]["module"]["validator_exit"]==0 and r["capture"]["specialization_entries"]==r["capture"]["specialization_bytes"]==0 for r in (indexed,standalone)),"captured_abi")
        baseline=indexed["capture"]["module"]["sha256"]
        substitute=standalone["capture"]["module"]["sha256"]
        need(baseline==PINS[f"indexed-{slot}"],"baseline_module_changed")
        need(substitute==REFERENCES[str(slot)] and standalone["identical_module_sha"] and substitute!=PINS[f"standalone-{slot}"],"replacement_not_executed")
        a,b=indexed["output"],standalone["output"]
        rows.append(dict(slot=slot,baseline_sha=baseline,replacement_sha=substitute,
                         baseline=a,replacement=b,replacement_bit_exact=b["vs_cpu"]==n.CounterZero(),
                         replacement_finite_and_within_tolerance=b["vs_cpu"]["class_mismatch"]==0 and b["vs_cpu"]["finite_over_tolerance"]==0))
    exact=sum(r["replacement_bit_exact"] for r in rows)
    within=sum(r["replacement_finite_and_within_tolerance"] for r in rows)
    return dict(status=STATUS,live_capture=receipt,unchanged_baseline_modules=4,exact_reference_modules_executed_in_unity=4,
                exact_reference_outputs=exact,within_tolerance_reference_outputs=within,rows=rows,
                isolated_reference_intervention_numeric_parity=(exact==4),
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
            observed=live.verify(a.project,a.private,staged,a.run_id,a.outcome)
            result["live_capture"]=observed
            result=verify(a.project,a.private,staged,a.run_id,a.outcome,observed)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    dump(a.out,result);print("GT_FFT_REFERENCE_SWAP_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
