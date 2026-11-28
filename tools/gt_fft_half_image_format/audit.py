"""Diagnostic one-word typed storage image format intervention, no production layer."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_operation_profile import image_operation_profile
from scripts.probe_fft_spirv_formatless_repair import restore_formatless_write
from tools.gt_fft_source_format_pair import audit as previous
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_compiler_directive import audit as directive
from tools.gt_fft_indexed_dxc import audit as chain
from tools.gt_fft_indexed_pair import audit as old
from tools.gt_fft_typed_dxc import audit as typed

FORMATS={"RGHalf":("rg16f",2,2),"ARGBHalf":("rgba16f",4,2)}
STATUS="OBSERVED_HALF_IMAGE_FORMAT_INTERVENTION"
STAGED="STAGED_HALF_IMAGE_FORMAT_INTERVENTION"
need=old.need
sha=old.sha
dump=old.dump
replace=n.replace
PINS={"RGHalf":{"indexed-6":"6f41c93f685cfee1320b267c49c0555ec0bfea6fb791e39979adffefbeaa2406","standalone-6":"95a00438bb05b3b5f533dbfbb678a6d7ace33d58c0fb173659c9606f47adcdb5","indexed-7":"1adb6fe44c4c28589f8e081ae5c5ccf0a18e9a0de43a70e545c8774f26bc66f7","standalone-7":"7bf8b794b02a31965efff1d6da6dccf2815783077529a46263b35bc103fce6e2","indexed-16":"a714938f4b82bccdd3a17f9947257b1a0f647e303f331ab9e01feb82f6a33ff9","standalone-16":"783dfd77d5907182cdbc21f86f83b171e023346e3fc2728fc8970c67ca778e82","indexed-17":"ed7dc2656718e91f209d84c6d77a57093dacde9693b55c9c1088879b74f5cea6","standalone-17":"434dc39a1de4cfa8be1200c8e7102bed91b8aac5f75449494794774bde5da064"},"ARGBHalf":{"indexed-6":"453df94664de8c840ce170a56a4a3bffd06ef422db622c10e3a9e462ec6a918f","indexed-7":"fe2444f22e3449da185db9d69ed3f36ad166e060534b771ee6c8d8e692be3390","indexed-16":"c427f7ea65e223533b6c4bba3eb73aeadd40b4ca1674921887cea99b0aca9116","indexed-17":"a061fabcb33a54c8fc82b8bffd504fa66a955f30e0df6528d7a6ffe35f78afce","standalone-6":"603131440ab8d589188e68e81aadd58bcbd1f9140668100152dd69a1d73898b6","standalone-7":"69b3b31d43f4f8bac9bb5ac85a1ff1beee6e5cc27cb34b79b592603b27425427","standalone-16":"835a6305b39217df9ec3818741f4559e47f6a4f3e043bca25f942a3f7e79d871","standalone-17":"abb004e74422b68771d59b944142a9a4b689ed82fd628fd93b0fd5b55c3014e7"}}
ENUMS={"RGHalf":(6,7),"ARGBHalf":(1,2)}
SLOTS=live.SLOTS

def map_text(fmt):
    a,b=ENUMS[fmt]
    return f"{a} {b}\n"+"".join(p+"\n" for _,p in sorted(PINS[fmt].items()))

def patch_image_format(data,fmt):
    need(type(data) is bytes and 20<=len(data)<=1048576 and len(data)%4==0,"module_extent")
    a,b=ENUMS[fmt]
    w=list(struct.unpack("<"+"I"*(len(data)//4),data))
    need(w[0]==0x07230203 and w[3]>0 and w[4]==0,"module_header")
    outputs=[];caps=[];i=5
    while i<len(w):
        n,op=w[i]>>16,w[i]&65535
        need(n>0 and i+n<=len(w),"instruction_extent")
        if op==17 and n==2:caps.append(w[i+1])
        if op==25 and n in (9,10) and w[i+7]==2:
            need(w[i+8]==a,"unexpected_before_format")
            outputs.append(i+8)
        i+=n
    need(len(outputs)==1 and 56 not in caps and (b!=7 or 49 in caps),"image_format_contract")
    w[outputs[0]]=b
    out=struct.pack("<"+"I"*len(w),*w)
    return out,outputs[0]

def modify(data,count,fmt):
    if fmt=="RGHalf":return typed.modify(data,count,"RGFloat")
    return chain.indexed_source(data) if count==20 else directive.directive(data)

def reverse(data,count,fmt):
    if fmt=="RGHalf":return typed.reverse(data,count,"RGFloat")
    return chain.strip_indexed(data) if count==20 else directive.strip_directive(data)

def pack_table(raw,half):
    need(len(raw)==n.TABLE_BYTES,"table_extent")
    if not half:return raw
    values=tuple(v[0] for v in struct.iter_unpack("<f",raw))
    out=b"".join(struct.pack("<e",v) for v in values)
    need(all(struct.unpack("<e",struct.pack("<e",v))[0]==v for v in values),"table_half_exact")
    return out

def render_host(s):
    s=n.render_host(s)
    s=replace(s,' && imageFormat.token=="rgba32f"','')
    s=replace(s,"const size_t n=size_t(w)*(i?8:h)*16;","const size_t n=size_t(w)*(i?8:h)*(i&&imageFormat.componentBytes==2?8:16);")
    s=replace(s,"ci.format=imageFormat.vk;\n        uint32_t texH=t==1?8:h;",
       'const auto fmt=t==0?selectFormat("rgba32f"):t==1?selectFormat(imageFormat.componentBytes==2?"rgba16f":"rgba32f"):imageFormat;\n        ci.format=fmt.vk;\n        uint32_t texH=t==1?8:h;')
    s=replace(s,"tex.sub.rowPitch>=w*imageFormat.stride()&&\n                tex.sub.offset+(texH-1)*tex.sub.rowPitch+w*imageFormat.stride()",
              "tex.sub.rowPitch>=w*fmt.stride()&&\n                tex.sub.offset+(texH-1)*tex.sub.rowPitch+w*fmt.stride()")
    s=replace(s,"auto* src=rawInputs[t].data()+size_t(y)*w*16;\n                std::memcpy(dst,src,size_t(w)*16);\n                require(std::memcmp(dst,src,size_t(w)*16)==0",
       "auto* src=rawInputs[t].data()+size_t(y)*w*fmt.stride();\n                std::memcpy(dst,src,size_t(w)*fmt.stride());\n                require(std::memcmp(dst,src,size_t(w)*fmt.stride())==0")
    s=replace(s,"view.format=imageFormat.vk;","view.format=fmt.vk;")
    return replace(s,"out.write(reinterpret_cast<const char*>(ptr),size_t(w)*16);","out.write(reinterpret_cast<const char*>(ptr),size_t(w)*imageFormat.stride());")

def profile(raw,fmt):
    _,lanes,width=FORMATS[fmt]
    need(len(raw)==n.COUNT*lanes*width,"raw_extent")
    sentinel=0x7000 if width==2 else 0x46000000
    code="<"+("H" if width==2 else "I")*lanes
    written=nonfinite=0
    for pixel in struct.iter_unpack(code,raw):
        written+=int(any(x!=sentinel for x in pixel))
        nonfinite+=sum((x&0x7c00)==0x7c00 if width==2 else (x&0x7f800000)==0x7f800000 for x in pixel)
    return dict(written_pixels=written,nonfinite_lanes=nonfinite,stored_lanes=n.COUNT*lanes,component_bits=width*8)

def compare(raw,reference,fmt):
    _,lanes,width=FORMATS[fmt]
    need(len(raw)==len(reference)==n.COUNT*lanes*width,"comparison_extent")
    code="<H" if width==2 else "<I"
    mismatch=sum(x!=y for x,y in zip(struct.iter_unpack(code,raw),struct.iter_unpack(code,reference),strict=True))
    return dict(raw_bit_different=mismatch,**profile(raw,fmt))

def capture(runner,modules,root,source,table,fmt):
    token,lanes,width=FORMATS[fmt]
    need(len(source)==n.IMAGE_BYTES and len(table)==n.SIZE*n.STAGES*(8 if width==2 else 16),"oracle_input_extent")
    root.mkdir(mode=0o700)
    (root/"source.rgba32f").write_bytes(source);(root/"butterfly.rgba32f").write_bytes(table)
    with (root/"driver.log").open("wb") as log:
        rc=subprocess.run([str(runner),*[str(x) for x in modules],"512","512","19","512",token],
                          cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
    need(rc==0 and (root/"driver.log").read_text(errors="replace").count("GT_FFT_NATIVE_HOST exact_mapped_inputs=true intermediate_barrier=true four_raw_outputs=true")==1,"oracle_process")
    need((root/"source.rgba32f").read_bytes()==source and (root/"butterfly.rgba32f").read_bytes()==table,"oracle_input_changed")
    out=[]
    for name in ("native0","native1","round0","round1"):
        p=root/(name+".rgba32f")
        need(p.is_file() and not p.is_symlink() and p.stat().st_size==n.COUNT*lanes*width,"oracle_output_extent")
        raw=p.read_bytes();pr=profile(raw,fmt)
        need(pr["written_pixels"]==n.COUNT and pr["nonfinite_lanes"]==0,"oracle_nonfinite_or_unwritten")
        out.append(raw)
    return out

def canary(root,runner,fmt):
    _,lanes,width=FORMATS[fmt]
    code=replace(n.GLSL,"binding=2,rgba32f","binding=2")
    modules=[]
    for name,text in (("add",code),("sub",replace(code," + texelFetch"," - texelFetch"))):
        p=root/(name+".comp");q=root/(name+".spv");p.write_text(text)
        private_command(["glslangValidator","-V","-S","comp","-o",str(q),str(p)])
        private_command(["spirv-val","--target-env","vulkan1.1",str(q)])
        modules.append(q)
    add,sub=modules;source=n.input_bytes("zero")
    pack=lambda values,count:struct.pack("<"+("e" if width==2 else "f")*count,*values[:count])
    base=(.25,.5,.75,1.)
    table=pack(base,4)*(n.SIZE*n.STAGES)
    raw=capture(runner,[add,add,add,sub],root/"canary",source,table,fmt)
    plus=pack(base,lanes)*n.COUNT
    # On RG sampled image expansion alpha defaults to 1 but only RG is stored.
    double=pack(tuple(v*2 for v in base),lanes)*n.COUNT
    zero=bytes(n.COUNT*lanes*width)
    need(raw==[plus,double,plus,zero],"oracle_canary_values")
    need(compare(raw[1],raw[3],fmt)["raw_bit_different"]==n.COUNT*lanes,"wrong_program_control")
    return dict(status="PASS",pixels=n.COUNT,wrong_program_lanes=n.COUNT*lanes)

def stage(src,managed,project,private,run_id,fmt):
    import UnityPy
    _,lanes,width=FORMATS[fmt]
    s=previous.stage(src,managed,project,private,run_id)
    cfg=private/"config.json";m=json.loads(cfg.read_text())
    tablepath=private/("table-half.f32" if width==2 else "table-float.f32")
    native_table=pack_table(tablepath.read_bytes(),width==2)
    (private/"table-native.raw").write_bytes(native_table)
    env=UnityPy.load(str(src/indexed.OWNER));obj=env.file.objects[indexed.PATH_ID]
    raw=obj.get_raw_data();need(obj.type.name=="ComputeShader" and hashlib.sha256(raw).hexdigest()==old.OBJECT_SHA,"original_object")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"program_count")
    commitments={};module_pins={}
    with tempfile.TemporaryDirectory(prefix="gt-fft-formatless-oracle-",dir=private.parent) as tmp:
        root=Path(tmp);host=root/"host.cpp";runner=root/"host"
        host.write_text(render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()))
        private_command(["g++","-std=c++17","-O2",str(host),"-lvulkan","-o",str(runner)],timeout=90)
        control=canary(root,runner,fmt)
        modules={}
        for row in m["rows"]:
            slot=row["slot"];rec=containers[slot]
            dx=root/f"slot{slot}.dxbc";native=root/f"native{slot}.spv";roundtrip=root/f"round{slot}.spv";restored=root/f"restored{slot}.spv"
            blob=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
            need(hashlib.sha256(blob).hexdigest()==rec["binary_sha256"]==row["dxbc_sha256"],"dxbc_pin")
            dx.write_bytes(blob)
            private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(native),str(dx)])
            private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(roundtrip),str(private/row["file"])])
            restored.write_bytes(restore_formatless_write(roundtrip.read_bytes(),image_resource_contracts(native.read_bytes()),image_operation_profile(native.read_bytes())))
            for p in (native,roundtrip,restored):private_command(["spirv-val","--target-env","vulkan1.1",str(p)])
            modules[slot]=(native,restored);module_pins[str(slot)]=dict(native=sha(native),restored=sha(restored))
        for mode in ("signed","zero"):
            source=n.input_bytes(mode);p=private/f"source-{mode}.rgba32f";p.write_bytes(source);commitments[p.name]=sha(p)
            for slot in (6,16):
                data=capture(runner,[*modules[slot],*modules[slot+1]],root/f"case-{slot}-{mode}",source,native_table,fmt)
                need(data[0]==data[2] and data[1]==data[3],"native_roundtrip_disagreement")
                for p in (0,1):
                    path=private/f"cpu-{slot}-{mode}-p{p}.raw";path.write_bytes(data[p]);commitments[path.name]=sha(path)
    sources=[]
    for name,count in [("indexed.compute",20)]+[(r["file"],1) for r in m["rows"]]:
        p=private/name;original=p.read_bytes();before=sha(p);changed=modify(original,count,fmt)
        need(reverse(changed,count,fmt)==original,"source_change")
        p.write_bytes(changed);sources.append(dict(name=name,count=count,original_sha=before,candidate_sha=sha(p)))
        if count==20:need(m["indexed_sha"]==before,"indexed_pin");m["indexed_sha"]=sha(p)
        else:
            row=next(r for r in m["rows"] if r["file"]==name);need(row["sha256"]==before,"standalone_pin");row["sha256"]=sha(p)
    dump(cfg,m)
    editor=project/"Assets/Editor/IndexedPair.cs"
    editor.write_text(replace(Path(__file__).with_name("IndexedPair.cs").read_text(),"__FORMAT__",fmt))
    coord=project/"Assets/Editor/Coordinate.compute";shutil.copyfile(Path("tools/gt_fft_live_module/Coordinate.compute"),coord)
    (private/"vktrace").mkdir(mode=0o700)
    (private/"half-map.txt").write_text(map_text(fmt))
    s.update(status=STAGED,format=fmt,private_config_sha256=sha(cfg),editor_sha=sha(editor),coordinate_sha=sha(coord),
        table_native_sha=sha(private/"table-native.raw"),source_records=sources,oracle_commitments=commitments,
        oracle_module_pins=module_pins,oracle_canary=control,oracle_exact_outputs=8,half_map_sha=sha(private/"half-map.txt"),baseline_pins=PINS[fmt],storage_enum_pair=list(ENUMS[fmt]))
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
        p=private/name;rec=records[name];need(sha(p)==sha(project/"Assets/Private"/name)==digest==rec["candidate_sha"] and directive.digest(reverse(p.read_bytes(),rec["count"],fmt))==rec["original_sha"],"source_identity")
    for name,digest in s["oracle_commitments"].items():need(sha(private/name)==digest,"oracle_commitment")
    trace=private/"vktrace"
    need((private/"half-map.txt").read_text()==map_text(fmt) and sha(private/"half-map.txt")==s["half_map_sha"] and s["baseline_pins"]==PINS[fmt] and s["storage_enum_pair"]==list(ENUMS[fmt]),"patch_map_identity")
    need(not (trace/"half-blocked").exists() and (trace/"half-patched").read_text()=="1","patch_dispatch_guard")
    feature=(trace/"half-extended-feature").read_text()
    need(feature in ("0","1") and (fmt!="RGHalf" or feature=="1"),"extended_feature")
    need({x.name for x in trace.iterdir()}=={f"{label}.{ext}" for label in live.LABELS for ext in ("spv","meta")}|{f"{label}.before.spv" for label in PINS[fmt]}|{"half-patched","half-extended-feature"},"trace_population")
    control=live.captured(trace,"control");need(control["module"]["validator_exit"]==0,"control_validator")
    modules=[]
    for slot in SLOTS:
        for variant in ("indexed","standalone"):
            label=f"{variant}-{slot}";cap=live.captured(trace,label)
            mod=cap["module"];ops=image_operation_profile((trace/(label+".spv")).read_bytes())
            before=trace/(label+".before.spv");after=trace/(label+".spv")
            groups,count,size,entry=live.meta((trace/(label+".meta")).read_text(),label)
            baseline=live.profile(before,entry,(512,1,1))
            need(baseline["sha256"]==PINS[fmt][label] and baseline["validator_exit"]==0,"baseline_pin")
            patched,word=patch_image_format(before.read_bytes(),fmt)
            need(patched==after.read_bytes() and sha(before)!=sha(after) and before.stat().st_size==after.stat().st_size,"one_word_mutation")
            before_images=baseline["images"];expected_images=[dict(x) for x in before_images]
            outputs=[x for x in expected_images if x["sampled_enum"]==2]
            need(len(outputs)==1 and outputs[0]["format_enum"]==ENUMS[fmt][0],"before_image_contract")
            outputs[0]["format_enum"]=ENUMS[fmt][1]
            need(mod["images"]==expected_images and mod["validator_exit"]==0 and cap["specialization_entries"]==cap["specialization_bytes"]==0 and not ops["storage_image_write_without_format_capability_declared"] and ops["op_image_read_count"]==0 and mod["opcode_profile"]==baseline["opcode_profile"],"patched_module_contract")
            modules.append(dict(slot=slot,variant=variant,capture=cap,baseline=baseline,generator=directive.generator(after),changed_words=1,word_index=word,entry_unchanged=True))
    cases=r["cases"];need([(c["first_slot"],c["input_mode"]) for c in cases]==[(s,m) for s in (6,16) for m in ("signed","zero")],"case_population")
    rows=[]
    for c in cases:
        slot=c["first_slot"];mode=c["input_mode"]
        need(c["outcome"]=="OBSERVED" and c["format"]==fmt and c["dispatches"]==4 and c["bindings"]==12 and c["sentinel_checks"]==4 and c["snapshots"]==4 and all(c[k] is True for k in ("input_gpu_exact","table_gpu_exact","target_format_exact")),"case_identity")
        out={}
        for label in ("indexed0","standalone0","indexed-chain","standalone-chain"):
            raw=(private/f"unity-{slot}-{mode}-{label}.raw").read_bytes()
            oracle=(private/f"cpu-{slot}-{mode}-p{0 if label.endswith('0') else 1}.raw").read_bytes()
            out[label]=compare(raw,oracle,fmt)
        rows.append(dict(slot=slot,mode=mode,outputs=out))
    exact=sum(v["raw_bit_different"]==0 and v["nonfinite_lanes"]==0 and v["written_pixels"]==n.COUNT for row in rows for v in row["outputs"].values())
    gen=sum(m["generator"]["tool_id"]==14 for m in modules)
    return dict(status=STATUS,format=fmt,stored_lanes=lanes,component_bits=width*8,registered_kernels=20,
        actual_enabled_extended_storage_feature=feature=="1",validated_one_word_modules=len(modules),generator_14_modules=gen,storage_enum_pair=list(ENUMS[fmt]),diagnostic_layer_only=True,
        exact_outputs=exact,observed_outputs=16,rows=rows,modules=modules,isolated_format_numeric_parity=(exact==16 and gen==8),
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
            trace=a.private/"vktrace";result["half_blocked"]=(trace/"half-blocked").exists();result["half_patched"]=(trace/"half-patched").exists();result["extended_feature_enabled"]=(trace/"half-extended-feature").read_text()=="1" if (trace/"half-extended-feature").is_file() else None
            result["observed_modules"]=[]
            for label in live.LABELS:
                try:result["observed_modules"].append(dict(label=label,capture=live.captured(trace,label),before_sha=sha(trace/(label+".before.spv")) if (trace/(label+".before.spv")).is_file() else None))
                except Exception:pass
    dump(a.out,result);print("GT_FFT_HALF_IMAGE_FORMAT_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
