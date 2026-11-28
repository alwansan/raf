"""Execute the unchanged original managed FFT constructor on the same-export imported shader.
No source or DLL is emitted. No original scene, player, or FFT dispatch is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from scripts import probe_original_fft_caller_graph as caller
from scripts import probe_original_fft_index_derivation as index
from scripts import probe_original_fft_inherited_seed as seed
from scripts import probe_original_fft_target_formats as formats
from scripts import probe_original_fft_kernel_callsites as calls
from scripts import probe_original_water_compute as water
from scripts import probe_fft_monoscript_field as mono
from tools.gt_fft_exact_import import audit as previous

need=previous.need
sha=previous.sha
digest=previous.digest
write_json=previous.write_json
DLL_BLOB="fc9d4ba920a178fdb89c970d9d772a01051dadc6"

def unique_ctor(text,name):
    rows=[x["params"] for x in caller.source_declarations(text) if x["name"]==name]
    need(len(rows)==1 and len(rows[0])==4,"ctor_population")
    params=[re.fullmatch(r"([\w.]+)\s+([A-Za-z_]\w*)",p.strip()) for p in rows[0]]
    need(all(params),"ctor_parameter_shape")
    return [(p[1].split(".")[-1],p[2]) for p in params]

def eval_bool(expr,env):
    x=re.sub(r"\s+","",expr)
    if x in ("true","false"):return x=="true"
    if x in env and type(env[x]) is bool:return env[x]
    if x.startswith("!") and x[1:] in env and type(env[x[1:]]) is bool:return not env[x[1:]]
    raise ValueError("unsupported_boolean_forwarding")

def contract(dx,gpu):
    proof=seed.prove(dx,gpu,water.ORIGINAL_SOURCE_SHA256["Dx11FFT"],seed.BASE_SHA256)
    index_report=index.index_source_links(dx,water.ORIGINAL_SOURCE_SHA256["Dx11FFT"])
    formats.analyze(gpu)
    d=unique_ctor(dx,"Dx11FFT");g=unique_ctor(gpu,"GpuFFT")
    need([v[0] for v in d]==["ComputeShader","int","bool","bool"] and g[0][0]=="int" and [v[0] for v in g[1:]]==["bool"]*3,"ctor_type_contract")
    init=list(re.finditer(r":\s*base\s*\(",calls.mask_noncode(dx)))
    need(len(init)==1,"base_init")
    args,_=calls.parse_original_args(dx,init[0].end()-1)
    need(len(args)==4 and args[0].strip()==d[1][1],"base_size_forward")
    def base_position(field):
        found=re.findall(r"\b"+re.escape(field)+r"\s*=\s*([A-Za-z_]\w*)\s*;",calls.mask_noncode(gpu))
        need(len(found)==1 and found[0] in [p[1] for p in g],"base_bool_field")
        return [p[1] for p in g].index(found[0])
    two_pos,high_pos=base_position("_TwoChannels"),base_position("_HighPrecision")
    rows=[]
    for n in range(5,10):
        for third in (False,True):
            for fourth in (False,True):
                env={d[2][1]:third,d[3][1]:fourth}
                two,high=[eval_bool(args[p],env) for p in (two_pos,high_pos)]
                rows.append(dict(resolution=1<<n,third=third,fourth=fourth,seed=n,first=(n-5)*2+(10 if fourth else 0),
                                 two_channels=two,high_precision=high,format=("ARGB" if two else "RG")+("Float" if high else "Half")))
    namespaces=mono.NAMESPACE.findall(dx);base_ns=mono.NAMESPACE.findall(gpu)
    need(len(namespaces)<=1 and len(base_ns)<=1,"namespace_population")
    def qualified(ns,name):return (ns[0]+"." if ns else "")+name
    return dict(type_name=qualified(namespaces,"Dx11FFT"),base_name=qualified(base_ns,"GpuFFT"),
                selector_hash=index_report["first_pass_index_identifier_sha256"],seed_hash=proof["protected_inherited_seed_identifier_sha256"],
                two_hash=digest(b"_TwoChannels"),high_hash=digest(b"_HighPrecision"),cases=rows)

def stage(managed,dll,dest,import_stage,run_id):
    s=json.loads(import_stage.read_text())
    need(s["status"]=="STAGED_EXACT_FFT_IMPORT" and s["run_id"]==run_id,"import_stage")
    dx=caller.read_pin(managed,"Dx11FFT")
    paths=list(managed.rglob("GpuFFT.cs"));need(len(paths)==1 and not paths[0].is_symlink(),"base_source")
    gpu=paths[0].read_text(encoding="utf-8-sig").replace("\r\n","\n")
    p=contract(dx,gpu)
    need(dll.is_file() and not dll.is_symlink() and 0<dll.stat().st_size<32*1024*1024,"dll_extent")
    data=dll.read_bytes()
    need(hashlib.sha1(("blob "+str(len(data))+"\0").encode()+data).hexdigest()==DLL_BLOB,"original_dll_git_blob")
    private=dest/"original-managed-private.dll"
    need(not private.exists(),"private_path")
    private.write_bytes(data)
    p.update(run_id=run_id,assembly_sha=sha(private),compute_sha=s["candidate_sha256"],meta_sha=s["candidate_meta_sha256"])
    expected=dest/"original-constructor-private.json";write_json(expected,p)
    # Avoid a compiled authored assembly with the original game's simple name.
    write_json(dest/"Assets/GTFFTWitness.asmdef",{"name":"GT.FFT.Witness","autoReferenced":False})
    write_json(dest/"Assets/Editor/GTFFTConstructor.asmdef",{"name":"GT.FFT.Constructor.Editor","references":["GT.FFT.Witness"],"includePlatforms":["Editor"],"autoReferenced":False})
    shutil.copyfile(Path(__file__).with_name("GTFFTOriginalConstructor.cs"),dest/"Assets/Editor/GTFFTOriginalConstructor.cs")
    return dict(status="STAGED_ORIGINAL_CONSTRUCTOR",run_id=run_id,assembly_sha256=p["assembly_sha"],expected_sha256=sha(expected),
                candidate_sha256=p["compute_sha"],candidate_meta_sha256=p["meta_sha"],original_source_pins_verified=True,
                original_selector_source_verified=True,source_bool_forwarding_verified=True,case_count=len(p["cases"]),
                original_dll_unmodified=True,original_component_runtime_verified=False,dispatch_executed=False,production=False,android_device=False,XAPK=False)

def verify(dest,s,outcome,run_id):
    result=dict(status="INCONCLUSIVE",run_id=run_id,editor_outcome=outcome,original_component_runtime_verified=False,
                original_water_caller_executed=False,dispatch_executed=False,water_rendering_verified=False,production=False,android_device=False,XAPK=False)
    try:
        need(s["status"]=="STAGED_ORIGINAL_CONSTRUCTOR" and s["run_id"]==run_id,"stage")
        expected=dest/"original-constructor-private.json";need(sha(expected)==s["expected_sha256"],"expected_sha")
        p=json.loads(expected.read_text())
        result["original_dll_bytes_unchanged"]=sha(dest/"original-managed-private.dll")==s["assembly_sha256"]==p["assembly_sha"]
        result["compute_source_unchanged"]=sha(dest/"Assets/Original.compute")==p["compute_sha"]
        result["compute_meta_bytes_unchanged"]=sha(dest/"Assets/Original.compute.meta")==p["meta_sha"]
        native=dest/"editor-exit-code";mark=dest/"editor-run-marker"
        result["native_editor_exit"]=int(native.read_text()) if native.is_file() else None
        result["native_run_marker_matched"]=mark.is_file() and mark.read_text().strip()==run_id
        raw=dest/"constructor-receipt.json"
        need(raw.is_file(),"managed_receipt_missing")
        j=json.loads(raw.read_text());need(j["run_id"]==run_id,"editor_run")
        result["editor_receipt"]=j
        rows=j["cases"];need(len(rows)<=20,"receipt_case_count")
        # No private field names, DLL bytes, type strings or raw exceptions in receipt.
        for got,expected_row in zip(rows,p["cases"]):
            need(all(got[k]==v for k,v in expected_row.items()),"case_source_contract")
            need(got["shader_field_matched"] and got["first_workgroup"]==2*got["resolution"] and got["second_workgroup"]==2*got["resolution"],"original_constructor_workgroups")
        need(j["status"]=="PASS" and len(rows)==20 and j["original_assembly_loaded"] and j["constructor_il_nonempty"] and j["same_export_reference_resolved"] and j["vulkan"],"original_constructor_receipt")
        need(result["original_dll_bytes_unchanged"] and result["compute_source_unchanged"] and result["compute_meta_bytes_unchanged"] and result["native_editor_exit"]==0 and result["native_run_marker_matched"] and outcome=="success","editor_boundary")
        result.update(status="OBSERVED_ORIGINAL_MANAGED_CONSTRUCTOR",original_constructor_cases_verified=20,
                      original_constructor_selector_and_format_flags_verified=True,original_constructor_kernel_pair_registered=True)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("action",choices=("stage","verify"))
    for key in ("managed","dll","dest","import-stage","stage-report","out"):p.add_argument("--"+key,type=Path)
    p.add_argument("--run-id",required=True);p.add_argument("--outcome",default="")
    a=p.parse_args()
    if a.action=="stage":result=stage(a.managed,a.dll,a.dest,a.import_stage,a.run_id)
    else:result=verify(a.dest,json.loads(a.stage_report.read_text()),a.outcome,a.run_id)
    write_json(a.out,result);print("GT_FFT_ORIGINAL_CONSTRUCTOR_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("STAGED_ORIGINAL_CONSTRUCTOR","OBSERVED_ORIGINAL_MANAGED_CONSTRUCTOR") else 2
if __name__=="__main__":raise SystemExit(main())
