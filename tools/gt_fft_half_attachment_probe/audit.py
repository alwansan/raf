"""Localize exact half attachment conversion; isolated only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import struct
from tools.gt_fft_formatless_dxc import audit as prior
from tools.gt_fft_compiler_directive import audit as directive
from tools.gt_fft_indexed_dxc import audit as chain
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_indexed_pair import audit as old
from scripts.probe_fft_spirv_operation_profile import image_operation_profile

FORMATS={k:prior.FORMATS[k] for k in ("RGHalf","ARGBHalf")}
STATUS="OBSERVED_HALF_ATTACHMENT_PROBE"
STAGED="STAGED_HALF_ATTACHMENT_PROBE"
need=old.need
sha=old.sha
dump=old.dump
replace=n.replace
SLOTS=live.SLOTS
PINS={"indexed-6":"453df94664de8c840ce170a56a4a3bffd06ef422db622c10e3a9e462ec6a918f","indexed-7":"fe2444f22e3449da185db9d69ed3f36ad166e060534b771ee6c8d8e692be3390","indexed-16":"c427f7ea65e223533b6c4bba3eb73aeadd40b4ca1674921887cea99b0aca9116","indexed-17":"a061fabcb33a54c8fc82b8bffd504fa66a955f30e0df6528d7a6ffe35f78afce"}
PINS.update({"standalone-"+slot:digest for slot,digest in chain.STANDALONE_PINS.items()})

def pack_table(raw,half):return prior.pack_table(raw,half)
def compare(raw,ref,fmt):return prior.compare(raw,ref,fmt)
def scratch_to_half(raw,fmt):
    need(len(raw)==n.IMAGE_BYTES,"scratch_extent")
    lanes=FORMATS[fmt][1]
    out=bytearray()
    for pixel in struct.iter_unpack("<4f",raw):
        need(all(math.isfinite(x) for x in pixel),"scratch_nonfinite")
        try:out.extend(struct.pack("<"+"e"*lanes,*pixel[:lanes]))
        except OverflowError as e:raise ValueError("scratch_half_overflow") from e
    return bytes(out)

def canary_source():
    out=bytearray()
    # Asymmetric XY values and binary16 tie/neighbor cases of both signs.
    for y in range(n.SIZE):
        for x in range(n.SIZE):
            a=(x+1)/512;b=-(y+1)/1024
            # Put tie and immediate-neighbor values in the stored RG lanes as well.
            def near_tie(v,offset):
                _,e=math.frexp(abs(v))
                return math.copysign(abs(v)+2**(e-12)+offset*2**(e-24),v)
            a=near_tie(a,y%3-1);b=near_tie(b,x%3-1)
            c=(1.0+(x%7)*2**-10+2**-11+(y%3-1)*2**-23)
            d=-(.5+(y%7)*2**-11+2**-12+(x%3-1)*2**-24)
            out.extend(struct.pack("<4f",a,b,c,d))
    return bytes(out)

def diagnostic(raw,expected,fmt):
    lanes=FORMATS[fmt][1];size=n.SIZE;stride=lanes*2
    need(len(raw)==len(expected)==size*size*stride,"diagnostic_extent")
    same=compare(raw,expected,fmt)
    mismatch=[0]*lanes;zeros=[0]*lanes;negative_zero=[0]*lanes;sentinels=[0]*lanes
    code="<"+"H"*lanes
    for a,b in zip(struct.iter_unpack(code,raw),struct.iter_unpack(code,expected),strict=True):
        for c in range(lanes):
            mismatch[c]+=int(a[c]!=b[c]);zeros[c]+=int(a[c]==0);negative_zero[c]+=int(a[c]==0x8000);sentinels[c]+=int(a[c]==0x7000)
    # Compare the entire raw attachment against fixed coordinate transforms of
    # the independently generated authored expected bytes; no raw pixels leave CI.
    transforms={}
    for fx,fy in ((False,False),(True,False),(False,True),(True,True)):
        count=0
        for y in range(size):
            sy=size-1-y if fy else y
            for x in range(size):
                sx=size-1-x if fx else x
                i=(y*size+x)*stride;j=(sy*size+sx)*stride
                count+=int(raw[i:i+stride]!=expected[j:j+stride])
        transforms[f"x{int(fx)}y{int(fy)}"]=count
    return dict(**same,per_lane_mismatch=mismatch,zero_lanes=zeros,negative_zero_lanes=negative_zero,
                sentinel_lanes=sentinels,coordinate_pixel_mismatch=transforms)

def methods(private,fmt):
    expected=(private/"conversion-expected.raw").read_bytes();rows=[]
    for i in range(16):
        row=dict(method=i,draw="blit" if i&8 else "procedural",flip_x=bool(i&1),flip_y=bool(i&2),pre_round=bool(i&4),sources={})
        for k,name in ((0,"texture2d"),(1,"render_texture")):
            p=private/f"conversion-method-{i}-{k}.raw"
            if p.is_file() and not p.is_symlink():
                row["sources"][name]=diagnostic(p.read_bytes(),expected,fmt)
        if row["sources"]:rows.append(row)
    return rows

def exact_methods(rows):
    return [r["method"] for r in rows if set(r["sources"])=={"texture2d","render_texture"} and
            all(s["raw_bit_different"]==s["nonfinite_lanes"]==0 and s["written_pixels"]==n.COUNT for s in r["sources"].values())]

def stage(src,managed,project,private,run_id,fmt):
    need(fmt in FORMATS,"format")
    # Reuse the already verified native formatless oracle setup. Reverse
    # the unsuccessful attribute experiment BEFORE any Unity import.
    s=prior.stage(src,managed,project,private,run_id,fmt)
    cfg=private/"config.json";m=json.loads(cfg.read_text());records=[]
    for record in s["source_records"]:
        name=record["name"];count=record["count"];p=private/name
        need(sha(p)==record["candidate_sha"],"prior_source_pin")
        original=prior.reverse(p.read_bytes(),count)
        need(directive.digest(original)==record["original_sha"],"original_source_pin")
        data=chain.indexed_source(original) if count==20 else directive.directive(original)
        need((chain.strip_indexed(data) if count==20 else directive.strip_directive(data))==original,"source_reversal")
        p.write_bytes(data);records.append(dict(name=name,count=count,original_sha=record["original_sha"],candidate_sha=sha(p)))
        if count==20:m["indexed_sha"]=sha(p)
        else:next(row for row in m["rows"] if row["file"]==name)["sha256"]=sha(p)
    dump(cfg,m)
    editor=project/"Assets/Editor/IndexedPair.cs"
    text=replace(Path(__file__).with_name("IndexedPair.cs").read_text(),"__FORMAT__",fmt)
    editor.write_text(replace(text,"__CONTROL_FORMAT__",fmt))
    shader=project/"Assets/Editor/ExactStore.shader";shutil.copyfile(Path(__file__).with_name("ExactStore.shader"),shader)
    copy=project/"Assets/Editor/CopyExact.compute";shutil.copyfile(Path(__file__).with_name("CopyExact.compute"),copy)
    raw=canary_source();expected=scratch_to_half(raw,fmt)
    (private/"conversion-source.rgba32f").write_bytes(raw);(private/"conversion-expected.raw").write_bytes(expected)
    s.update(status=STAGED,private_config_sha256=sha(cfg),source_records=records,editor_sha=sha(editor),store_shader_sha=sha(shader),copy_shader_sha=sha(copy),
             conversion_source_sha=sha(private/"conversion-source.rgba32f"),conversion_expected_sha=sha(private/"conversion-expected.raw"),
             prior_live_module_pins=PINS)
    return s

def verify(project,private,s,run_id,outcome,fmt):
    _,lanes,width=FORMATS[fmt]
    need(s["status"]==STAGED and s["format"]==fmt,"stage_format")
    cfg=private/"config.json";p=old.bounded_progress(private,run_id)
    need(outcome=="success" and sha(cfg)==s["private_config_sha256"] and p.get("private_launch_marker_matches") is True and p["editor_native_exit"]==0 and p["last_managed_checkpoint"]["phase"]=="complete","editor_progress")
    r=json.loads((private/"receipt.json").read_text());m=json.loads(cfg.read_text())
    need(r["status"]=="PASS" and r["run_id"]==run_id and r["config_sha256"]==s["private_config_sha256"] and r["private_guard"] is True and r["vulkan"] is True and r["registration_count"]==20 and r["private_source_hashes_match"] is True,"editor_identity")
    need(r["coordinate_control_verified"] is True and r["coordinate_control_pixels"]==n.COUNT and sha(project/"Assets/Editor/Coordinate.compute")==s["coordinate_sha"] and sha(project/"Assets/Editor/IndexedPair.cs")==s["editor_sha"],"coordinate_control")
    tablepath=private/("table-half.f32" if width==2 else "table-float.f32")
    need(sha(tablepath)==m["table_half_sha" if width==2 else "table_float_sha"] and (private/"table-native.raw").read_bytes()==pack_table(tablepath.read_bytes(),width==2) and sha(private/"table-native.raw")==s["table_native_sha"],"table_identity")
    records={r["name"]:r for r in s["source_records"]}
    for name,digest in [("indexed.compute",m["indexed_sha"])]+[(x["file"],x["sha256"]) for x in m["rows"]]:
        p=private/name;rec=records[name];need(sha(p)==sha(project/"Assets/Private"/name)==digest==rec["candidate_sha"] and directive.digest(chain.strip_indexed(p.read_bytes()) if rec["count"]==20 else directive.strip_directive(p.read_bytes()))==rec["original_sha"],"source_identity")
    for name,digest in s["oracle_commitments"].items():need(sha(private/name)==digest,"oracle_commitment")
    trace=private/"vktrace"
    need(s["prior_live_module_pins"]==PINS and not (private/"replacements").exists(),"capture_only")
    need(r["conversion_control_verified"] is True and r["scratch_control_copy_exact"] is True and r["conversion_control_pixels"]==n.COUNT and sha(project/"Assets/Editor/ExactStore.shader")==s["store_shader_sha"] and sha(project/"Assets/Editor/CopyExact.compute")==s["copy_shader_sha"],"conversion_control")
    trials=methods(private,fmt);passing=exact_methods(trials)
    need(r["conversion_methods_tested"]==len(trials)==16 and all(len(x["sources"])==2 for x in trials) and passing and r["conversion_method"]==passing[0],"conversion_method_selection")
    source=private/"conversion-source.rgba32f";expected=private/"conversion-expected.raw";actual=private/"conversion-actual.raw"
    need(sha(source)==s["conversion_source_sha"] and source.read_bytes()==canary_source() and sha(expected)==s["conversion_expected_sha"] and expected.read_bytes()==scratch_to_half(source.read_bytes(),fmt)==actual.read_bytes(),"conversion_canary_bytes")
    need({x.name for x in trace.iterdir()}=={f"{label}.{ext}" for label in live.LABELS for ext in ("spv","meta")},"trace_population")
    control=live.captured(trace,"control");need(control["module"]["validator_exit"]==0,"control_validator")
    modules=[]
    for slot in SLOTS:
        for variant in ("indexed","standalone"):
            label=f"{variant}-{slot}";cap=live.captured(trace,label)
            mod=cap["module"];ops=image_operation_profile((trace/(label+".spv")).read_bytes())
            outputs=[x for x in mod["images"] if x["sampled_enum"]==2]
            need(mod["validator_exit"]==0 and cap["specialization_entries"]==cap["specialization_bytes"]==0 and len(outputs)==1 and outputs[0]["format_enum"]==1 and not ops["storage_image_write_without_format_capability_declared"] and ops["op_image_read_count"]==0 and mod["sha256"]==PINS[label],"scratch_module_pin")
            modules.append(dict(slot=slot,variant=variant,capture=cap,generator=directive.generator(trace/(label+".spv")),scratch_rgba32f=True,prior_pin_exact=True))
    cases=r["cases"];need([(c["first_slot"],c["input_mode"]) for c in cases]==[(s,m) for s in (6,16) for m in ("signed","zero")],"case_population")
    rows=[]
    for c in cases:
        slot=c["first_slot"];mode=c["input_mode"]
        need(c["outcome"]=="OBSERVED" and c["format"]==fmt and c["dispatches"]==4 and c["bindings"]==12 and c["sentinel_checks"]==8 and c["snapshots"]==4 and c["scratch_snapshots"]==4 and c["conversion_passes"]==4 and all(c[k] is True for k in ("input_gpu_exact","table_gpu_exact","target_format_exact","scratch_format_exact")),"case_identity")
        out={}
        for label in ("indexed0","standalone0","indexed-chain","standalone-chain"):
            raw=(private/f"unity-{slot}-{mode}-{label}.raw").read_bytes()
            oracle=(private/f"cpu-{slot}-{mode}-p{0 if label.endswith('0') else 1}.raw").read_bytes()
            scratch=(private/f"scratch-{slot}-{mode}-{label}.raw").read_bytes()
            profile=n.profile(scratch)
            need(profile["written_pixels"]==n.COUNT and all(v==0 for i,v in enumerate(profile["class_counts"]) if i%4),"scratch_finite_coverage")
            out[label]=compare(raw,oracle,fmt)
            out[label]["scratch_to_half"]=compare(raw,scratch_to_half(scratch,fmt),fmt)
        rows.append(dict(slot=slot,mode=mode,outputs=out))
    exact=sum(v["raw_bit_different"]==0 and v["nonfinite_lanes"]==0 and v["written_pixels"]==n.COUNT for row in rows for v in row["outputs"].values())
    gen=sum(m["generator"]["tool_id"]==14 for m in modules)
    converted=sum(v["scratch_to_half"]["raw_bit_different"]==0 for row in rows for v in row["outputs"].values())
    return dict(status=STATUS,format=fmt,stored_lanes=lanes,component_bits=width*8,registered_kernels=20,
        conversion_control_pixels=n.COUNT,conversion_method=r["conversion_method"],conversion_method_candidates=trials,exact_control_methods=passing,validated_pinned_scratch_modules=len(modules),generator_14_modules=gen,exact_scratch_to_half_outputs=converted,
        exact_outputs=exact,observed_outputs=16,rows=rows,modules=modules,isolated_format_numeric_parity=(exact==16 and converted==16 and gen==8),
        actual_descriptor_resource_mapping_verified=False,original_runtime_kernel_mapping_proven=False,
        original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage");v=sub.add_parser("verify")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    for q in (st,v):q.add_argument("--run-id",required=True);q.add_argument("--format",choices=FORMATS,required=True)
    v.add_argument("--outcome",required=True)
    a=p.parse_args();result=dict(status="INCONCLUSIVE",format=a.format,water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id,a.format)
        else:result=verify(a.project,a.private,json.loads(a.stage.read_text()),a.run_id,a.outcome,a.format)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
        if a.action=="verify":
            result.update(directive.failure_receipt(a.private,a.run_id))
            trace=a.private/"vktrace";result["conversion_actual_present"]=(a.private/"conversion-actual.raw").is_file()
            if result["conversion_actual_present"]:
                try:result["conversion_control_comparison"]=compare((a.private/"conversion-actual.raw").read_bytes(),(a.private/"conversion-expected.raw").read_bytes(),a.format)
                except Exception:pass
            try:
                result["conversion_method_candidates"]=methods(a.private,a.format)
                result["exact_control_methods"]=exact_methods(result["conversion_method_candidates"])
            except Exception:pass
            result["observed_modules"]=[]
            for label in live.LABELS:
                try:result["observed_modules"].append(dict(label=label,capture=live.captured(trace,label)))
                except Exception:pass
    dump(a.out,result);print("GT_FFT_HALF_ATTACHMENT_PROBE_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
