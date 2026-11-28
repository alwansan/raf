"""Remaining ARGBHalf serialized-size shards, original DXBC oracle and pinned DXC bytes."""
import argparse
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path
from tools.gt_fft_size_matrix import audit as matrix
from tools.gt_fft_bundle_serialized_copy import audit as copy
from tools.gt_fft_compute_bundle import audit as bundle
from tools.gt_fft_half_image_format import audit as half
from tools.gt_fft_typed_dxc import audit as typed
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_operation_profile import image_operation_profile
from scripts.probe_fft_spirv_formatless_repair import restore_formatless_write
from scripts.probe_original_fft_software_vulkan import private_command

FMT="ARGBHalf"
FORMATS={**half.FORMATS,"RGFloat":typed.FORMATS["RGFloat"]}
RG_FORMATS=("RGFloat","RGHalf")
STAGED="STAGED_HALF_SERIALIZED_SIZE"
STATUS="OBSERVED_HALF_SERIALIZED_SIZE"
need=half.need
sha=half.sha

def prior_pins(size):
    _,slots=matrix.dimensions(size)
    p=Path(f"clients/GT/sessions/20261128-fft-size-matrix/actual-46171915719-{size}.json")
    v=json.loads(p.read_text());r=v["receipt"]
    need(v["run"]==46171915719 and v["conclusion"]=="success" and r["size"]==size and r["isolated_shard_numeric_parity"] is True and r["exact_outputs"]==32,"prior_size_receipt")
    pins={}
    for m in r["modules"]:
        mod=m["capture"]["module"];slot=m["slot"];variant=m["variant"]
        need(slot in slots and variant in ("indexed","standalone") and mod["validator_exit"]==0 and mod["local_size"]==[size,1,1],"prior_module")
        need([x["format_enum"] for x in mod["images"] if x["sampled_enum"]==2]==[1],"prior_format")
        key=f"{variant}-{slot}";need(key not in pins and re.fullmatch(r"[0-9a-f]{64}",mod["sha256"]) is not None,"prior_pin")
        pins[key]=mod["sha256"]
    need(len(pins)==8,"prior_population")
    return pins

def host(root,size,contracts):
    stages,_=matrix.dimensions(size)
    source=root/"host.cpp";runner=root/"host"
    source.write_text(copy.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text(),contracts,size,stages))
    private_command(["g++","-std=c++17","-O2",str(source),"-lvulkan","-o",str(runner)],timeout=90)
    return runner

def capture(runner,programs,root,source,table,size,fmt=FMT):
    stages,_=matrix.dimensions(size)
    token,lanes,width=FORMATS[fmt]
    need(len(source)==size*size*16 and len(table)==size*stages*4*width,"typed_inputs_extent")
    root.mkdir(mode=0o700)
    (root/"source.rgba32f").write_bytes(source);(root/"butterfly.rgba32f").write_bytes(table)
    with (root/"driver.log").open("wb") as log:
        p=subprocess.run([str(runner),*[str(x) for x in programs],str(size),str(size),"19",str(size),token],cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    need(p.returncode==0 and (root/"driver.log").read_text(errors="replace").count(matrix.MARKER)==1,"half_native_process")
    need((root/"source.rgba32f").read_bytes()==source and (root/"butterfly.rgba32f").read_bytes()==table,"half_input_identity")
    results=[]
    for name in ("native0","native1","round0","round1"):
        path=root/(name+".rgba32f")
        need(path.is_file() and not path.is_symlink() and path.stat().st_size==size*size*lanes*width,"typed_output_extent")
        raw=path.read_bytes();profile=typed.profile(raw,fmt)
        need(profile["written_pixels"]==size*size and profile["nonfinite_lanes"]==0,"half_output_coverage")
        results.append(raw)
    return results

def authored_control(root,runner,size,stages,fmt=FMT):
    _,lanes,width=FORMATS[fmt]
    glsl=half.replace(half.n.GLSL,"local_size_x=512",f"local_size_x={size}")
    glsl=half.replace(glsl,"xy.y%8",f"xy.y%{stages}")
    glsl=half.replace(glsl,"binding=2,rgba32f","binding=2")
    programs=[]
    for name,code in (("add",glsl),("sub",half.replace(glsl," + texelFetch"," - texelFetch"))):
        src=root/(name+".comp");spv=root/(name+".spv");src.write_text(code)
        private_command(["glslangValidator","-V","-S","comp","-o",str(spv),str(src)])
        private_command(["spirv-val","--target-env","vulkan1.1",str(spv)])
        programs.append(spv)
    add,sub=programs
    packed=lambda values,count,n:struct.pack("<"+("e" if width==2 else "f")*n,*values[:n])*count
    table=packed((.25,.5,.75,1),size*stages,4)
    actual=capture(runner,[add,add,add,sub],root/"control",bytes(size*size*16),table,size,fmt)
    need(actual==[packed((.25,.5,.75,1),size*size,lanes),packed((.5,1,1.5,2),size*size,lanes),packed((.25,.5,.75,1),size*size,lanes),bytes(size*size*lanes*width)],"typed_canary")
    need(typed.compare(actual[1],actual[3],fmt)["raw_bit_different"]==size*size*lanes,"typed_wrong_pass_control")
    return {"exact_control_outputs":4,"wrong_pass_rejected":True}

def stage(source,managed,project,private,run_id,size,fmt=FMT):
    import UnityPy
    stages,slots=matrix.configure(size)
    s=matrix.stage(source,managed,project,private,run_id,size)
    pins=prior_pins(size)
    config=json.loads((private/"config.json").read_text())
    _,lanes,width=FORMATS[fmt]
    tablepath=private/("table-half.f32" if width==2 else "table-float.f32")
    need(sha(tablepath)==config["table_half_sha" if width==2 else "table_float_sha"],"typed_table_pin")
    table=half.pack_table(tablepath.read_bytes(),width==2)
    (private/"table-native.raw").write_bytes(table)
    env=UnityPy.load(str(source/indexed.OWNER));obj=env.file.objects[indexed.PATH_ID]
    raw=obj.get_raw_data()
    need(obj.type.name=="ComputeShader" and bundle.digest(raw)==config["object_sha"]==half.old.OBJECT_SHA,"original_compute")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"program_population")
    commitments={};refs={}
    with tempfile.TemporaryDirectory(prefix="gt-half-size-native-",dir=private.parent) as tmp:
        root=Path(tmp);runner=host(root,size,[("main",[0,1,2])]*4)
        control=authored_control(root,runner,size,stages,fmt)
        programs={}
        for row in config["rows"]:
            slot=row["slot"];rec=containers[slot]
            dx=root/f"slot-{slot}.dxbc";native=root/f"native-{slot}.spv";ref=root/f"ref-{slot}.spv";restored=root/f"restored-{slot}.spv"
            blob=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
            need(bundle.digest(blob)==row["dxbc_sha256"]==rec["binary_sha256"],"source_dxbc_pin")
            dx.write_bytes(blob)
            text=(private/row["file"]).read_bytes()
            original=root/f"original-{slot}.compute"
            original.write_bytes(half.directive.strip_directive(text))
            private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(native),str(dx)])
            private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(ref),str(original)])
            restored.write_bytes(restore_formatless_write(ref.read_bytes(),image_resource_contracts(native.read_bytes()),image_operation_profile(native.read_bytes())))
            for p in (native,restored):
                private_command(["spirv-val","--target-env","vulkan1.1",str(p)])
                images=image_resource_contracts(p.read_bytes())["typed_image_declarations"]
                need([v["format_enum"] for v in images if v["sampled_enum"]==2]==[0],"formatless_oracle")
            programs[slot]=(native,restored)
            refs[str(slot)]={"native_sha":sha(native),"restored_sha":sha(restored)}
        for mode in ("signed","zero"):
            name=f"source-{mode}.rgba32f";data=(private/name).read_bytes()
            need(sha(private/name)==s["oracle_commitments"][name] and data==half.n.input_bytes(mode),"source_bytes")
            commitments[name]=sha(private/name)
            for slot in (slots[0],slots[2]):
                observed=capture(runner,[*programs[slot],*programs[slot+1]],root/f"case-{slot}-{mode}",data,table,size,fmt)
                need(observed[0]==observed[2] and observed[1]==observed[3],"formatless_roundtrip_parity")
                for i in (0,1):
                    name=f"cpu-{slot}-{mode}-p{i}.raw";p=private/name;p.write_bytes(observed[i]);commitments[name]=sha(p)
    source_records=[]
    if fmt in RG_FORMATS:
        # Strip the existing compiler directive and apply only the reversible
        # two-channel declaration/final-store wrapper proven at size 512.
        original_pins={x["slot"]:x["original_sha"] for x in s["source_directive_rows"]}
        for name,count,row in [("indexed.compute",20,None)]+[(x["file"],1,x) for x in config["rows"]]:
            p=private/name;data=p.read_bytes()
            before=half.chain.strip_indexed(data) if count==20 else half.directive.strip_directive(data)
            prior=s["indexed_original_sha"] if count==20 else original_pins[row["slot"]]
            need(bundle.digest(before)==prior,"original_source_pin")
            after=typed.modify(before,count,"RGFloat");need(typed.reverse(after,count,"RGFloat")==before,"typed_source_reversal")
            p.write_bytes(after);pin=sha(p)
            if count==20:config["indexed_sha"]=pin
            else:row["sha256"]=pin
            source_records.append(dict(name=name,count=count,original_sha=prior,typed_sha=pin))
        half.dump(private/"config.json",config)
    editor=project/"Assets/Editor/IndexedPair.cs"
    text=half.replace(Path("tools/gt_fft_compute_bundle/IndexedPair.cs").read_text(),"__FORMAT__",fmt)
    editor.write_text(matrix.render_editor(text,size))
    return dict(status=STAGED,size=size,format=fmt,slots=list(slots),private_config_sha256=sha(private/"config.json"),
                editor_sha=sha(editor),coordinate_sha=s["coordinate_sha"],table_native_sha=sha(private/"table-native.raw"),
                oracle_commitments=commitments,oracle_refs=refs,prior_live_pins=pins,oracle_control=control,oracle_exact_outputs=8,source_records=source_records)

def read_rgfloat(private,root,build,slots):
    # Freshly built typed RGFloat programs are re-read from the committed
    # bundle bytes. These are same-run serialized pins, NOT live dispatch pins.
    root.mkdir();pins={};modules={};records=[]
    for index in range(5):
        p=private/"compiled-bundles"/f"fft-{index}"
        need(p.is_file() and not p.is_symlink() and sha(p)==build["bundle_sha256"][index],"typed_bundle_commitment")
        selected=list(range(20)) if index==0 else [slots[index-1]]
        pid,raw,other,programs=copy.object_inventory(p,selected,index)
        for slot,data in programs.items():
            m=bundle.validate_module(data,root,EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot])
            need([x["format_enum"] for x in m["images"] if x["sampled_enum"]==2]==[6],"typed_storage")
            if slot not in slots:continue
            label=("indexed" if index==0 else "standalone")+f"-{slot}"
            need(label not in pins,"typed_duplicate")
            path=root/(label+".spv");path.write_bytes(data)
            need(sha(path)==m["sha256"],"typed_reread")
            pins[label]=m["sha256"];modules[label]=path
        records.append(dict(index=index,bundle_sha=sha(p),object_sha=bundle.digest(raw),serialized_programs=len(programs)))
    need(len(pins)==8 and sum(x["serialized_programs"] for x in records)==24,"typed_population")
    return records,pins,modules

def verify(project,private,s,run_id,size,fmt=FMT):
    stages,slots=matrix.configure(size)
    need(s["status"]==STAGED and s["size"]==size and s["format"]==fmt and s["slots"]==list(slots),"stage")
    pins=prior_pins(size);need(s["prior_live_pins"]==pins,"pin_identity")
    build=bundle.build_receipt(private,run_id)
    cfg=json.loads((private/"config.json").read_text())
    need(build["config_sha256"]==s["private_config_sha256"]==sha(private/"config.json"),"config_identity")
    need(sha(project/"Assets/Editor/IndexedPair.cs")==s["editor_sha"] and sha(project/"Assets/Private/BundleCoordinate.compute")==s["coordinate_sha"],"build_editor")
    table=(private/"table-native.raw").read_bytes()
    need(bundle.digest(table)==s["table_native_sha"],"table_identity")
    for name,pin in s["oracle_commitments"].items():need(sha(private/name)==pin,"oracle_commitment")
    result={}
    if fmt in RG_FORMATS:
        records=s["source_records"]
        need(len(records)==5 and len({x["name"] for x in records})==5,"typed_source_population")
        need({x["name"]:x["typed_sha"] for x in records}=={"indexed.compute":cfg["indexed_sha"],**{x["file"]:x["sha256"] for x in cfg["rows"]}},"typed_config_identity")
        for rec in records:
            name=rec["name"];p=private/name
            need(sha(p)==sha(project/"Assets/Private"/name)==rec["typed_sha"] and bundle.digest(typed.reverse(p.read_bytes(),rec["count"],"RGFloat"))==rec["original_sha"],"typed_source_identity")
    with tempfile.TemporaryDirectory(prefix="gt-half-size-copy-",dir=private.parent) as tmp:
        root=Path(tmp)
        if fmt in RG_FORMATS:
            original_records,serialized_pins,unpatched=read_rgfloat(private,root/"baseline",build,slots)
            result.update(serialized_pin_scope="same_run_build_not_live_capture",source_reversal_verified=True,baseline_records=original_records,baseline_module_pins=serialized_pins)
            if fmt=="RGFloat":
                records,modules=original_records,unpatched
                result.update(patched_archive_roundtrip=False,serialized_modules=24,one_word_modules=0,unchanged_modules=24,records=records)
            else:
                records,modules=copy.patch_bundles(private,root,fmt,build,slots,serialized_pins)
                result.update(patched_archive_roundtrip=True,serialized_modules=24,one_word_modules=8,unchanged_modules=16,records=records)
        else:
            records,modules=copy.patch_bundles(private,root,fmt,build,slots,pins)
            result.update(serialized_pin_scope="previous_live_capture",patched_archive_roundtrip=True,serialized_modules=24,one_word_modules=8,unchanged_modules=16,records=records)
        rows={x["slot"]:x for x in cfg["rows"]};cases=[]
        for slot in (slots[0],slots[2]):
            labels=[f"{v}-{i}" for i in (slot,slot+1) for v in ("indexed","standalone")]
            contracts=[]
            for label in labels:
                variant,num=label.split("-");row=rows[int(num)]
                props=("_SourceTex","_ButterflyTex","_TargetTex") if variant=="indexed" else (row["source_property"],row["butterfly_property"],row["target_property"])
                contracts.append(copy.resource_contract(modules[label],*props))
            path=root/f"host-{slot}";path.mkdir();runner=host(path,size,contracts)
            for mode in ("signed","zero"):
                data=(private/f"source-{mode}.rgba32f").read_bytes()
                values=capture(runner,[modules[k] for k in labels],root/f"case-{slot}-{mode}",data,table,size,fmt)
                ref=[(private/f"cpu-{slot}-{mode}-p{i}.raw").read_bytes() for i in (0,1)]
                checks=[typed.compare(raw,ref[i%2],fmt) for i,raw in enumerate(values)]
                cases.append(dict(slot=slot,mode=mode,bindings=[c[1] for c in contracts],outputs=checks))
        result["numeric_cases"]=cases
        exact=sum(o["raw_bit_different"]==0 and o["nonfinite_lanes"]==0 and o["written_pixels"]==size*size for c in cases for o in c["outputs"])
        result["exact_outputs"]=exact
        result["direct_native_dispatch_verified"]=exact==16
        result["status"]=STATUS if exact==16 else "INCONCLUSIVE"
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("action",choices=("stage","verify"))
    for key in ("source","managed","project","private","stage","out"):p.add_argument("--"+key,type=Path)
    p.add_argument("--run-id",required=True);p.add_argument("--size",type=int,choices=matrix.SIZES,required=True);p.add_argument("--format",choices=FORMATS,default=FMT)
    a=p.parse_args();r=dict(status="INCONCLUSIVE",size=a.size,format=a.format,unity_bundle_loaded=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)
    try:
        if a.action=="stage":r.update(stage(a.source,a.managed,a.project,a.private,a.run_id,a.size,a.format))
        else:r.update(verify(a.project,a.private,json.loads(a.stage.read_text()),a.run_id,a.size,a.format))
    except Exception as e:
        r["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):r["failure_reason"]=str(e)
    half.dump(a.out,r);print("GT_FFT_HALF_SERIALIZED_SIZE_"+a.action.upper()+" "+json.dumps(r,sort_keys=True))
    return 0 if r["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
