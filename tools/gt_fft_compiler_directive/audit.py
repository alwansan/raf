"""Test a Unity compiler selection directive, not a claimed DXC implementation.

The Vulkan layer is the unmodified capture-only layer. Exact original-derived
HLSL is preserved except one pragma. Do not promote a directive or an opcode
profile into proof of compiler identity or Android runtime compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_reference_swap import audit as prior
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_indexed_pair import audit as old

STATUS="OBSERVED_SOURCE_COMPILER_DIRECTIVE"
STAGED="STAGED_SOURCE_COMPILER_DIRECTIVE"
need=live.need
sha=live.sha
dump=live.dump
DIRECTIVE=b"#pragma use_dxc\n"
HEADER=b"#pragma kernel main\n"

def directive(data):
    need(type(data) is bytes and HEADER in data[:len(HEADER)] and data.startswith(HEADER)
         and len(data)<524352 and b"\x00" not in data and b"#pragma use_dxc" not in data
         and b"#pragma never_use_dxc" not in data,"directive_source_anchor")
    return DIRECTIVE+data

def strip_directive(data):
    need(data.startswith(DIRECTIVE+HEADER) and data.count(DIRECTIVE)==1,"directive_identity")
    return data[len(DIRECTIVE):]

def digest(data):return hashlib.sha256(data).hexdigest()

def generator(path):
    data=path.read_bytes()
    need(20<=len(data)<=1048576 and data[:4]==b"\x03\x02\x23\x07","generator_header")
    w=struct.unpack_from("<I",data,8)[0]
    return dict(tool_id=w>>16,tool_version=w&65535)

def stage(src,managed,project,private,run_id):
    s=live.stage(src,managed,project,private,run_id)
    cfg=private/"config.json";m=json.loads(cfg.read_text())
    source_rows=[]
    for row in m["rows"]:
        slot=row["slot"];path=private/row["file"];data=path.read_bytes()
        need(digest(data)==row["sha256"] and s["reference_profiles"][str(slot)]["sha256"]==prior.REFERENCES[str(slot)],"candidate_original_reference_identity")
        changed=directive(data)
        need(strip_directive(changed)==data,"directive_reverse_check")
        before=row["sha256"];path.write_bytes(changed);row["sha256"]=sha(path)
        source_rows.append(dict(slot=slot,original_sha=before,directive_sha=row["sha256"],only_directive=True))
    dump(cfg,m)
    s.update(status=STAGED,private_config_sha256=sha(cfg),source_directive_rows=source_rows,
             reference_pins=prior.REFERENCES,prior_module_pins=prior.PINS,
             capture_layer_only=True)
    return s

def verify(project,private,s,run_id,outcome,receipt=None):
    if receipt is None:receipt=live.verify(project,private,s,run_id,outcome)
    need(receipt["status"]==live.STATUS and receipt["recorded_compute_dispatches"]==8,"editor_capture_count")
    need(not (private/"replacements").exists() and s["capture_layer_only"] is True
         and s["reference_pins"]==prior.REFERENCES and s["prior_module_pins"]==prior.PINS,"capture_only_guard")
    cfg=json.loads((private/"config.json").read_text())
    records={r["slot"]:r for r in s["source_directive_rows"]}
    need(set(records)==set(live.SLOTS) and len(s["source_directive_rows"])==4,"candidate_row_population")
    rows=[]
    for row in cfg["rows"]:
        slot=row["slot"];record=records[slot];p=private/row["file"]
        need(sha(p)==row["sha256"]==record["directive_sha"]
            and digest(strip_directive(p.read_bytes()))==record["original_sha"]
            and record["only_directive"] is True,"candidate_source_reversal")
        indexed,standalone=[next(r for r in receipt["rows"] if r["slot"]==slot and r["variant"]==v) for v in ("indexed","standalone")]
        need(indexed["capture"]["module"]["sha256"]==prior.PINS[f"indexed-{slot}"] and indexed["capture"]["module"]["validator_exit"]==0,"baseline_identity")
        cap=standalone["capture"];module=cap["module"]
        need(module["validator_exit"]==0 and cap["specialization_entries"]==cap["specialization_bytes"]==0,"candidate_module_validity")
        output=standalone["output"];exact=output["vs_cpu"]==n.CounterZero()
        changed=module["sha256"]!=prior.PINS[f"standalone-{slot}"]
        rows.append(dict(slot=slot,baseline=indexed["output"],candidate=output,
            candidate_sha=module["sha256"],old_standalone_sha=prior.PINS[f"standalone-{slot}"],
            bytecode_changed=changed,reference_bytecode_exact=standalone["identical_module_sha"],
            candidate_generator=generator(private/"vktrace"/f"standalone-{slot}.spv"),
            baseline_generator=generator(private/"vktrace"/f"indexed-{slot}.spv"),
            reference_generator=generator(private/f"glslang-{slot}.spv"),
            image_abi_exact=standalone["image_abi_exact"],candidate_bit_exact=exact,
            candidate_within_tolerance=output["vs_cpu"]["class_mismatch"]==0 and output["vs_cpu"]["finite_over_tolerance"]==0))
    changed=sum(r["bytecode_changed"] for r in rows)
    exact=sum(r["candidate_bit_exact"] for r in rows)
    return dict(status=STATUS,live_capture=receipt,rows=rows,unchanged_indexed_baselines=4,
        candidate_modules_changed=changed,candidate_bit_exact_outputs=exact,
        candidate_within_tolerance_outputs=sum(r["candidate_within_tolerance"] for r in rows),
        candidate_image_abi_exact=sum(r["image_abi_exact"] for r in rows),
        source_directive_only=True,isolated_numeric_candidate=(exact==4),
        directive_honored_by_compiler_proven=False,compiler_identity_proven=False,
        actual_descriptor_resource_mapping_verified=False,original_runtime_kernel_mapping_proven=False,
        original_fft_numeric_parity_verified=False,water_rendering_verified=False,
        android_device=False,production=False,XAPK=False)

def failure_receipt(private,run_id):
    # Only authored checkpoints and bounded numeric/boolean fields, never raw
    # editor messages, private shader names or exception text.
    progress=old.bounded_progress(private,run_id)
    out=dict(editor_progress=progress)
    path=private/"receipt.json"
    if path.is_file() and not path.is_symlink() and path.stat().st_size<65536:
        try:
            r=json.loads(path.read_text())
            if r.get("run_id")==run_id:
                out["editor_registered_slots"]=r.get("registration_count")
                out["editor_status_pass"]=r.get("status")=="PASS"
                out["coordinate_control_verified"]=r.get("coordinate_control_verified") is True
                out["case_dispatch_counts"]=[c.get("dispatches") if isinstance(c,dict) else None for c in r.get("cases",[])[:2]]
        except (ValueError,OSError,TypeError):pass
    trace=private/"vktrace"
    out["capture_presence"]={label:{ext:(trace/f"{label}.{ext}").is_file() for ext in ("spv","meta","duplicate")} for label in live.LABELS}
    return out

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
        if a.action=="verify":result.update(failure_receipt(a.private,a.run_id))
    dump(a.out,result);print("GT_FFT_COMPILER_DIRECTIVE_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
