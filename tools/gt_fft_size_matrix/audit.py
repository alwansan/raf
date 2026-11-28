"""Isolated matrix shards for remaining original-derived FFT cache sizes.

Existing validated cross-backend comparison helpers run with explicitly scoped
dimensions in this dedicated CLI process; previous workflow files are unchanged.
All source modules, tables, images, entry names and logs remain runner-private.
"""
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
from scripts import t1_stage_original_fft_compute_candidates as original
from scripts.probe_original_fft_resource_bindings import resource_rows
from scripts.t1_fft_unity_gpu_resource_bridge import translated_image_symbols
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_original_fft_software_vulkan import private_command
from tools.gt_fft_source_format_pair import audit as table
from tools.gt_fft_native_bank_oracle import audit as n
from tools.gt_fft_indexed_pair import audit as old
from tools.gt_fft_cross_backend import audit as cross
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_compiler_directive import audit as directive
from tools.gt_fft_indexed_dxc import audit as chain

SIZES=(64,128,256,1024)
STATUS="OBSERVED_INDEXED_DXC_SIZE_SHARD"
STAGED="STAGED_INDEXED_DXC_SIZE_SHARD"
need=old.need
sha=old.sha
dump=old.dump
replace=n.replace
MARKER="GT_FFT_NATIVE_HOST exact_mapped_inputs=true intermediate_barrier=true four_raw_outputs=true"

def dimensions(size):
    need(type(size) is int and size in SIZES,"matrix_size")
    stages=size.bit_length()-2
    start=(stages-5)*2
    return stages,(start,start+1,start+10,start+11)

def configure(size,table_sha=None):
    stages,slots=dimensions(size)
    # The existing raw comparator is intentionally reused with exact byte
    # extent; CLI calls are single-shard, never concurrent within a process.
    n.SIZE=size;n.STAGES=stages;n.COUNT=size*size
    n.IMAGE_BYTES=size*size*16;n.TABLE_BYTES=size*stages*16
    if table_sha is not None:n.TABLE_SHA=table_sha
    table.N=size//2;table.SIZE=size;table.STAGES=stages
    cross.CASES=[(slot,mode) for slot in (slots[0],slots[2]) for mode in ("signed","zero")]
    return stages,slots

def labels(size):
    _,slots=dimensions(size)
    return ("control",)+tuple(f"{v}-{s}" for s in slots for v in ("indexed","standalone"))

def render_layer(source,size):
    s=replace(source,"if(!((x==1&&y==512&&z==1)||(x==64&&y==64&&z==1)))return;",
              f"if(!((x==1&&y=={size}&&z==1)||(x=={size//8}&&y=={size//8}&&z==1)||(x==64&&y==64&&z==1)))return;")
    anchor='if(label!="control"&&label!="indexed-6"&&label!="indexed-7"&&label!="indexed-16"&&label!="indexed-17"&&\n       label!="standalone-6"&&label!="standalone-7"&&label!="standalone-16"&&label!="standalone-17")return;'
    return replace(s,anchor,"if("+"&&".join('label!="'+label+'"' for label in labels(size))+")return;")

def render_editor(source,size):
    stages,slots=dimensions(size)
    s=replace(source,"const int Size=512, Count=Size*Size, Stages=8;",f"const int Size={size}, Count=Size*Size, Stages={stages};")
    s=replace(s,"int[] slots={6,7,16,17};","int[] slots={"+",".join(map(str,slots))+"};")
    s=replace(s,"m.rows[i].group==512","m.rows[i].group==Size")
    s=replace(s,"Need(x==512&&y==1&&z==1);","Need(x==Size&&y==1&&z==1);")
    return s

def render_host(source,size):
    stages,_=dimensions(size)
    s=n.render_host(source)
    s=replace(s,"dispatchGroupY==512",f"dispatchGroupY=={size}")
    s=replace(s,"require(w==512 && h==512",f"require(w=={size} && h=={size}")
    s=replace(s,"size_t(w)*(i?8:h)*16",f"size_t(w)*(i?{stages}:h)*16")
    return replace(s,"uint32_t texH=t==1?8:h;",f"uint32_t texH=t==1?{stages}:h;")

def capture(runner,modules,root,source,lookup):
    need(len(source)==n.IMAGE_BYTES and len(lookup)==n.TABLE_BYTES,"oracle_input_extent")
    root.mkdir(mode=0o700)
    (root/"source.rgba32f").write_bytes(source);(root/"butterfly.rgba32f").write_bytes(lookup)
    with (root/"driver.log").open("wb") as log:
        p=subprocess.run([str(runner),*[str(x) for x in modules],str(n.SIZE),str(n.SIZE),"19",str(n.SIZE),"rgba32f"],
                         cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    need(p.returncode==0 and (root/"driver.log").read_text(errors="replace").count(MARKER)==1,"oracle_process")
    need((root/"source.rgba32f").read_bytes()==source and (root/"butterfly.rgba32f").read_bytes()==lookup,"oracle_input_identity")
    data=[]
    for name in ("native0","native1","round0","round1"):
        file=root/(name+".rgba32f")
        need(file.is_file() and not file.is_symlink() and file.stat().st_size==n.IMAGE_BYTES,"oracle_output_extent")
        raw=file.read_bytes();p=n.profile(raw)
        need(p["written_pixels"]==n.COUNT and all(v==0 for i,v in enumerate(p["class_counts"]) if i%4),"oracle_output_finite_and_written")
        data.append(raw)
    return data

def canary(root,runner):
    glsl=replace(n.GLSL,"local_size_x=512",f"local_size_x={n.SIZE}")
    glsl=replace(glsl,"xy.y%8",f"xy.y%{n.STAGES}")
    modules=[]
    for name,code in (("add",glsl),("sub",replace(glsl," + texelFetch"," - texelFetch"))):
        p=root/(name+".comp");q=root/(name+".spv");p.write_text(code)
        private_command(["glslangValidator","-V","-S","comp","-o",str(q),str(p)])
        private_command(["spirv-val","--target-env","vulkan1.1",str(q)])
        modules.append(q)
    add,sub=modules;source=n.input_bytes("zero")
    lookup=struct.pack("<4f",.25,.5,.75,1)*(n.SIZE*n.STAGES)
    raw=capture(runner,[add,add,add,sub],root/"canary",source,lookup)
    plus=struct.pack("<4f",.25,.5,.75,1)*n.COUNT
    double=struct.pack("<4f",.5,1,1.5,2)*n.COUNT
    need(raw==[plus,double,plus,source],"oracle_canary_values")
    wrong=n.compare(raw[1],raw[3])
    need(wrong["finite_over_tolerance"]==n.COUNT*4,"oracle_wrong_second_rejected")
    return dict(status="PASS",exact_first_pass_pixels=n.COUNT,exact_native_second_pixels=n.COUNT,wrong_second_detected_lanes=n.COUNT*4)

def derive_table(managed,private,size,slots):
    stages,_=dimensions(size);res=size//2
    dx=table.source(managed,"Dx11FFT",table.managed.ORIGINAL_SOURCE_SHA256["Dx11FFT"])
    gpu=table.source(managed,"GpuFFT",table.numeric.PINS["GpuFFT"])
    util=table.source(managed,"ButterflyFFTUtility",table.numeric.PINS["ButterflyFFTUtility"])
    formula=table.selector.prove(dx,gpu,table.managed.ORIGINAL_SOURCE_SHA256["Dx11FFT"],table.numeric.PINS["GpuFFT"])
    entries=[x for x in formula["algebraic_examples_only"] if x["r"]==res]
    contract=table.formats.analyze(gpu)
    need(len(entries)==1 and tuple(entries[0]["bank0"]+entries[0]["bank1"])==slots
         and contract["temporary_cache_width_multiplier"]==contract["temporary_cache_height_multiplier"]==2
         and set(x["render_texture_format"] for x in contract["formats"])==set(table.FORMATS),"source_size_selector")
    pattern=r"protected\s+override\s+void\s+FillButterflyTexture\s*\(\s*Texture2D\s+butterfly\s*,\s*int\[\]\[\]\s+indices\s*,\s*Vector2\[\]\[\]\s+weights\s*\)"
    matches=list(re.finditer(pattern,dx));need(len(matches)==1,"derived_table_body_anchor")
    a,b=table.body_bounds(dx,matches[0].group(0))
    with tempfile.TemporaryDirectory(prefix="gt-fft-size-table-",dir=private.parent) as tmp:
        root=Path(tmp)
        (root/"OriginalUtilityPrivate.cs").write_text(util)
        (root/"ActualDxEncoder.cs").write_text(table.ENCODER.replace("__BODY__",dx[a:b]))
        doubles=table.numeric.DOUBLES.replace("public struct Color { public float r,g,b,a; }","public struct Color { public float r,g,b,a; public Color(float r,float g,float b,float a){this.r=r;this.g=g;this.b=b;this.a=a;} }")
        (root/"UnityDoubles.cs").write_text(doubles)
        (root/"Program.cs").write_text(replace(table.PROGRAM,"const int n=256,stages=8;",f"const int n={res},stages={stages};"))
        (root/"Table.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion></PropertyGroup></Project>')
        with (root/"dotnet-private.log").open("wb") as log:
            rc=subprocess.run(["dotnet","run","--project",str(root/"Table.csproj"),"--configuration","Release","--",str(private.resolve())],stdout=log,stderr=subprocess.STDOUT,timeout=180).returncode
        need(rc==0,"derived_table_body_execution")
    return table.table_check((private/"table-float.f32").read_bytes(),(private/"table-half.f32").read_bytes())

def stage(src,managed,project,private,run_id,size):
    import UnityPy
    stages,slots=configure(size)
    need(re.fullmatch(r"[0-9]+-[0-9]+",run_id) and not project.exists() and not private.exists(),"fresh_stage")
    private.mkdir(mode=0o700)
    lookup=derive_table(managed,private,size,slots)
    n.TABLE_SHA=lookup["table_float_sha256"]
    table_bytes=(private/"table-float.f32").read_bytes()
    need(sha(private/"table-float.f32")==n.TABLE_SHA,"table_commitment")
    env=UnityPy.load(str(src/indexed.OWNER));obj=env.file.objects[indexed.PATH_ID]
    need(obj.type.name=="ComputeShader","typed_source")
    raw=obj.get_raw_data();need(hashlib.sha256(raw).hexdigest()==old.OBJECT_SHA,"source_object_digest")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"compiled_program_count")
    records=resource_rows(obj.read_typetree());need(len(records)==20,"resource_row_count")
    commitments={};ref_profiles={};source_rows=[];selected=[]
    with tempfile.TemporaryDirectory(prefix="gt-fft-size-oracle-",dir=private.parent) as folder:
        root=Path(folder);candidate=root/"source"
        report=original.stage_original_candidates(src,candidate)
        manifest=json.loads((candidate/"Assets/T1OriginalDerived/PrivateCandidates.json").read_text())
        original.validate_import_candidate_manifest(manifest,candidate)
        need(len(manifest["rows"])==20,"source_candidate_population")
        parts=[];modules={}
        for record,entry in zip(records,manifest["rows"],strict=True):
            i=record["compiled_slot"];path=candidate/entry["compute_asset"]
            need(i==entry["compiled_slot"] and sha(path)==entry["candidate_sha256"],"source_slot_identity")
            body=path.read_text();parts.append(indexed.route(body,record))
            if i not in slots:continue
            need(record["workgroup_xyz"]==[size,1,1],"source_size_group")
            symbols=translated_image_symbols(body)
            name=f"reference-{i}.compute";shutil.copyfile(path,private/name)
            selected.append(dict(slot=i,group=size,file=name,sha256=sha(private/name),
                source_property=symbols["source"],butterfly_property=symbols["butterfly"],target_property=symbols["output"],dxbc_sha256=entry["original_dxbc_sha256"]))
            rec=containers[i];blob=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
            need(hashlib.sha256(blob).hexdigest()==entry["original_dxbc_sha256"]==rec["binary_sha256"],"source_dxbc_identity")
            dx=root/f"slot-{i}.dxbc";native=root/f"native-{i}.spv";roundtrip=root/f"round-{i}.spv";dx.write_bytes(blob)
            private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(native),str(dx)])
            private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(roundtrip),str(private/name)])
            for p in (native,roundtrip):
                private_command(["spirv-val","--target-env","vulkan1.1",str(p)])
                need(inspect(p.read_bytes())["declared_local_workgroup_sizes"]==[[size,1,1]],"oracle_group")
            modules[i]=(native,roundtrip)
            ref_profiles[str(i)]={"native_sha256":sha(native),"roundtrip_sha256":sha(roundtrip)}
        need(tuple(x["slot"] for x in selected)==slots,"selected_slots")
        program=private/"indexed.compute"
        program.write_text("".join(f"#pragma kernel {indexed.entry(i)} RAFT_FFT_SLOT={i}\n" for i in range(20))+"\n"+"".join(parts))
        for row in selected:
            i=row["slot"];mod=root/"a.spv";ref=root/"b.spv"
            private_command(["glslangValidator","-V","-D",f"-DRAFT_FFT_SLOT={i}","-S","comp","-e",indexed.entry(i),"-o",str(mod),str(program)])
            private_command(["spirv-val","--target-env","vulkan1.1",str(mod)])
            need(inspect(mod.read_bytes())["declared_local_workgroup_sizes"]==[[size,1,1]],"indexed_group_drift")
            private_command(["glslangValidator","-V","-D","-S","comp","--source-entrypoint","main","-e",indexed.entry(i),"-o",str(ref),str(private/row["file"])])
            for p in (mod,ref):private_command(["spirv-opt","--strip-debug",str(p),"-o",str(p)])
            need(mod.read_bytes()==ref.read_bytes(),"indexed_reference_executable_drift")
        host=root/"host.cpp";runner=root/"host"
        host.write_text(render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text(),size))
        private_command(["g++","-std=c++17","-O2",str(host),"-lvulkan","-o",str(runner)],timeout=90)
        control=canary(root,runner)
        for mode in ("signed","zero"):
            name=f"source-{mode}.rgba32f";commitments[name]=cross.write_exact(private/name,n.input_bytes(mode))
        for slot,mode in cross.CASES:
            inputs=(private/f"source-{mode}.rgba32f").read_bytes()
            data=capture(runner,[*modules[slot],*modules[slot+1]],root/f"case-{slot}-{mode}",inputs,table_bytes)
            need(data[0]==data[2] and data[1]==data[3],"native_roundtrip_disagreement")
            for p in (0,1):
                name=f"cpu-{slot}-{mode}-p{p}.rgba32f";commitments[name]=cross.write_exact(private/name,data[p])
        info=subprocess.run(["vulkaninfo","--summary"],capture_output=True,text=True,timeout=30,check=True).stdout
        host_device="; ".join(line.strip() for line in info.splitlines() if re.match(r"\s*(driverName|driverInfo|deviceName)\s*=",line))[:512]
        need("llvmpipe" in host_device.lower(),"host_device")
    before=sha(program);raw=program.read_bytes();program.write_bytes(chain.indexed_source(raw))
    need(chain.strip_indexed(program.read_bytes())==raw,"indexed_source_reversal")
    for row in selected:
        p=private/row["file"];data=p.read_bytes();original_sha=row["sha256"]
        need(sha(p)==original_sha,"standalone_source_pin")
        p.write_bytes(directive.directive(data));row["sha256"]=sha(p)
        need(directive.strip_directive(p.read_bytes())==data,"standalone_source_reversal")
        source_rows.append(dict(slot=row["slot"],original_sha=original_sha,directive_sha=row["sha256"]))
    cfg=private/"config.json"
    dump(cfg,dict(run_id=run_id,object_sha=old.OBJECT_SHA,indexed_sha=sha(program),rows=selected,table_float_sha=n.TABLE_SHA,table_half_sha=lookup["table_half_sha256"]))
    (project/"Assets/Editor").mkdir(parents=True);(project/"Packages").mkdir();(project/"ProjectSettings").mkdir()
    (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    (project/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    editor=project/"Assets/Editor/IndexedPair.cs"
    editor.write_text(render_editor(Path("tools/gt_fft_indexed_dxc/IndexedPair.cs").read_text(),size))
    coord=project/"Assets/Editor/Coordinate.compute"
    coord.write_text(replace(Path("tools/gt_fft_live_module/Coordinate.compute").read_text(),"id.y%8",f"id.y%{stages}"))
    (private/"vktrace").mkdir(mode=0o700)
    return dict(status=STAGED,size=size,managed_resolution=size//2,stages=stages,slots=list(slots),source_object_sha256=old.OBJECT_SHA,
        translated_program_count=20,selected_route_spirv_exact=4,source_table=lookup,reference_module_pins=ref_profiles,
        private_config_sha256=sha(cfg),indexed_original_sha=before,indexed_directive_sha=sha(program),source_directive_rows=source_rows,
        cross_editor_sha=sha(editor),coordinate_sha=sha(coord),oracle_commitments=commitments,oracle_canary=control,
        host_device=host_device,oracle_cases=4,oracle_exact_outputs=8,capture_only=True)

def captured(trace,label,size):
    need(label in labels(size),"capture_label")
    stem=trace/label
    m=stem.with_suffix(".meta")
    need(m.is_file() and not m.is_symlink() and 0<m.stat().st_size<=512 and not stem.with_suffix(".duplicate").exists(),"capture_meta")
    parts=m.read_text().split()
    need(len(parts)==6 and all(re.fullmatch(r"[0-9]{1,9}",x) for x in parts[:5]) and re.fullmatch(r"[A-Za-z0-9_-]{1,128}",parts[5]),"capture_meta_fields")
    x,y,z,count,extent=map(int,parts[:5])
    expected=(size//8,size//8,1) if label=="control" else (1,size,1)
    need((x,y,z)==expected and count==extent==0,"capture_dispatch_or_specialization")
    p=stem.with_suffix(".spv")
    profile=live.profile(p,parts[5],(8,8,1) if label=="control" else (size,1,1))
    need(profile["validator_exit"]==0,"captured_module_validator")
    return dict(dispatch_groups=list(expected),module=profile,generator=directive.generator(p))

def verify(project,private,s,run_id,outcome,size):
    stages,slots=configure(size,s["source_table"]["table_float_sha256"])
    need(s["status"]==STAGED and s["size"]==size and s["stages"]==stages and s["slots"]==list(slots),"stage_dimensions")
    need(s["capture_only"] is True and not (private/"replacements").exists(),"capture_only")
    lookup=table.table_check((private/"table-float.f32").read_bytes(),(private/"table-half.f32").read_bytes())
    need(lookup==s["source_table"] and lookup["table_float_sha256"]==n.TABLE_SHA,"source_table_identity")
    cfg=json.loads((private/"config.json").read_text())
    p=private/"indexed.compute"
    need(sha(p)==cfg["indexed_sha"]==s["indexed_directive_sha"] and directive.digest(chain.strip_indexed(p.read_bytes()))==s["indexed_original_sha"],"indexed_source_identity")
    records={r["slot"]:r for r in s["source_directive_rows"]}
    for row in cfg["rows"]:
        p=private/row["file"];r=records[row["slot"]]
        need(sha(p)==row["sha256"]==r["directive_sha"] and directive.digest(directive.strip_directive(p.read_bytes()))==r["original_sha"],"standalone_source_identity")
    result=cross.verify(project,private,s,run_id,outcome)
    need(result["status"]==cross.STATUS and result["observed_cases"]==4 and result["observed_outputs"]==32,"chained_cases")
    r=json.loads((private/"receipt.json").read_text())
    need(r["coordinate_control_verified"] is True and r["coordinate_control_pixels"]==n.COUNT and sha(project/"Assets/Editor/Coordinate.compute")==s["coordinate_sha"],"coordinate_control")
    trace=private/"vktrace"
    need(trace.is_dir() and not trace.is_symlink() and {p.name for p in trace.iterdir()}=={f"{label}.{ext}" for label in labels(size) for ext in ("spv","meta")},"trace_population")
    control=captured(trace,"control",size)
    modules=[dict(slot=slot,variant=v,capture=captured(trace,f"{v}-{slot}",size)) for slot in slots for v in ("indexed","standalone")]
    exact=sum(o["vs_cpu"]==n.CounterZero() for case in result["rows"] for o in case["outputs"].values())
    within=sum(o["vs_cpu"]["class_mismatch"]==o["vs_cpu"]["finite_over_tolerance"]==0 for case in result["rows"] for o in case["outputs"].values())
    comparisons=all(c[k]==n.CounterZero() for c in result["rows"] for k in ("stage1_indexed_vs_standalone","indexed_chain_vs_own_replay","standalone_chain_vs_own_replay","indexed_vs_standalone_same_cpu_input"))
    gen=sum(m["capture"]["generator"]["tool_id"]==14 for m in modules)
    return dict(status=STATUS,size=size,managed_resolution=size//2,stages=stages,slots=list(slots),registered_kernels=r["registration_count"],
        coordinate_control_pixels=n.COUNT,coordinate_module=control,modules=modules,validated_modules=len(modules),generator_14_modules=gen,
        exact_outputs=exact,within_tolerance_outputs=within,all_pair_replay_comparisons_exact=comparisons,chain=result,
        isolated_shard_numeric_parity=(exact==32 and comparisons and gen==8),
        original_runtime_kernel_mapping_proven=False,original_fft_numeric_parity_verified=False,
        water_rendering_verified=False,android_device=False,production=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage");v=sub.add_parser("verify");layer=sub.add_parser("render-layer")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    for q in (st,v,layer):q.add_argument("--size",type=int,choices=SIZES,required=True)
    for q in (st,v):q.add_argument("--run-id",required=True)
    v.add_argument("--outcome",required=True);layer.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.action=="render-layer":
        a.out.write_text(render_layer(Path("tools/gt_fft_live_module/layer.cpp").read_text(),a.size));return 0
    result=dict(status="INCONCLUSIVE",size=a.size,water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id,a.size)
        else:result=verify(a.project,a.private,json.loads(a.stage.read_text()),a.run_id,a.outcome,a.size)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
        if a.action=="verify":result["editor_progress"]=old.bounded_progress(a.private,a.run_id)
    dump(a.out,result);print("GT_FFT_SIZE_MATRIX_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
