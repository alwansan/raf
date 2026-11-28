"""Original managed integer butterfly body + four source target formats, private editor.
Both source bank candidates are tested; no inferred game selection or water proof.
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
from scripts import verify_original_butterfly_numeric as numeric
from scripts import probe_original_fft_target_formats as formats
from scripts import probe_original_fft_inherited_seed as selector
from scripts import probe_original_water_compute as managed
from scripts.instrument_android_runtime_operations import body_bounds
from tools.gt_fft_indexed_pair import audit as old
N=256
SIZE=512
STAGES=8
FORMATS=("RGHalf","RGFloat","ARGBHalf","ARGBFloat")
STATUS="OBSERVED_SOURCE_TABLE_FFT_FORMAT_MATRIX"
def need(ok,reason):old.need(ok,reason)
def sha(p):return old.sha(p)
def dump(p,o):old.dump(p,o)
def source(root,name,pin):
    p=list(root.rglob(name+".cs"))
    need(len(p)==1 and p[0].is_file() and not p[0].is_symlink() and p[0].stat().st_size<200000,"managed_source_population")
    value=p[0].read_text(encoding="utf-8-sig").replace("\r\n","\n")
    need(hashlib.sha256(value.encode()).hexdigest()==pin,"managed_source_sha")
    return value
ENCODER=r'''using UnityEngine;
class ActualDxEncoder {
 int _Resolution,_NumButterflies;
 public ActualDxEncoder(int n,int stages) {_Resolution=n;_NumButterflies=stages;}
 public void Fill(Texture2D butterfly,int[][] indices,Vector2[][] weights) {__BODY__}
}
'''
PROGRAM=r'''using System;
using System.IO;
using UnityEngine;
using UltimateWater;
class Table {
 static void Main(string[] args) {
   const int n=256,stages=8;
   ButterflyFFTUtility.ComputeButterfly(n,stages,out int[][] indices,out Vector2[][] weights);
   for(int half=0;half<2;half++){
     var tex=new Texture2D(2*n,stages,half==1);
     new ActualDxEncoder(n,stages).Fill(tex,indices,weights);
     using(var w=new BinaryWriter(File.Create(Path.Combine(args[0],half==1?"table-half.f32":"table-float.f32"))))
       for(int y=0;y<stages;y++)for(int x=0;x<2*n;x++){
         Color c=tex.pixels[x,y];w.Write(c.r);w.Write(c.g);w.Write(c.b);w.Write(c.a);
       }
   }
 }
}
'''
def table_check(full,half):
    need(len(full)==len(half)==SIZE*STAGES*16,"table_extent")
    a=list(struct.iter_unpack("<4f",full));b=list(struct.iter_unpack("<4f",half))
    for p,q in zip(a,b):
        need(all(math.isfinite(x) for x in p+q),"table_nonfinite")
        need(all(0<=x<SIZE and int(x)==x for x in p[:2]) and p[:2]==q[:2],"dx11_integer_address")
        need(all(abs(x)<=1.001 for x in p[2:]+q[2:]),"table_weight_extent")
        need(all(struct.unpack("<e",struct.pack("<e",x))[0]==y for x,y in zip(p,q)),"table_half_quantization")
    need(len(set(p[:2] for p in a))>N,"table_address_variation")
    return dict(table_texels=len(a),integer_address_lanes=len(a)*2,half_exact_address_lanes=len(a)*2,
                half_quantized_components=len(a)*4,table_float_sha256=hashlib.sha256(full).hexdigest(),
                table_half_sha256=hashlib.sha256(half).hexdigest())
def stage(src,managed_root,project,private,run_id):
    dx=source(managed_root,"Dx11FFT",managed.ORIGINAL_SOURCE_SHA256["Dx11FFT"])
    gpu=source(managed_root,"GpuFFT",numeric.PINS["GpuFFT"])
    util=source(managed_root,"ButterflyFFTUtility",numeric.PINS["ButterflyFFTUtility"])
    formula=selector.prove(dx,gpu,managed.ORIGINAL_SOURCE_SHA256["Dx11FFT"],numeric.PINS["GpuFFT"])
    c=formats.analyze(gpu)
    examples=[x for x in formula["algebraic_examples_only"] if x["r"]==N]
    need(len(examples)==1 and examples[0]["bank0"]==[6,7] and examples[0]["bank1"]==[16,17] and
         c["temporary_cache_width_multiplier"]==c["temporary_cache_height_multiplier"]==2 and
         set(x["render_texture_format"] for x in c["formats"])==set(FORMATS),"source_selector_or_format_contract")
    pattern=r"protected\s+override\s+void\s+FillButterflyTexture\s*\(\s*Texture2D\s+butterfly\s*,\s*int\[\]\[\]\s+indices\s*,\s*Vector2\[\]\[\]\s+weights\s*\)"
    matches=list(re.finditer(pattern,dx))
    need(len(matches)==1,"derived_table_body_anchor")
    a,b=body_bounds(dx,matches[0].group(0))
    out=old.stage(src,project,private,run_id)
    with tempfile.TemporaryDirectory(prefix="gt-dx11-table-",dir=private.parent) as tmp:
        root=Path(tmp)
        (root/"OriginalUtilityPrivate.cs").write_text(util)
        (root/"ActualDxEncoder.cs").write_text(ENCODER.replace("__BODY__",dx[a:b]))
        doubles=numeric.DOUBLES.replace("public struct Color { public float r,g,b,a; }","public struct Color { public float r,g,b,a; public Color(float r,float g,float b,float a){this.r=r;this.g=g;this.b=b;this.a=a;} }")
        (root/"UnityDoubles.cs").write_text(doubles)
        (root/"Program.cs").write_text(PROGRAM)
        (root/"Table.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion></PropertyGroup></Project>')
        with (root/"dotnet-private.log").open("wb") as log:
            rc=subprocess.run(["dotnet","run","--project",str(root/"Table.csproj"),"--configuration","Release","--",str(private.resolve())],stdout=log,stderr=subprocess.STDOUT,timeout=180).returncode
        need(rc==0,"derived_table_body_execution")
    t=table_check((private/"table-float.f32").read_bytes(),(private/"table-half.f32").read_bytes())
    cfg=private/"config.json";m=json.loads(cfg.read_text());m.update(table_float_sha=t["table_float_sha256"],table_half_sha=t["table_half_sha256"]);dump(cfg,m)
    shutil.copyfile(Path(__file__).with_name("IndexedPair.cs"),project/"Assets/Editor/IndexedPair.cs")
    out.update(status="STAGED_SOURCE_DX11_TABLE_FORMAT_MATRIX",private_config_sha256=sha(cfg),
               source_resolution=N,source_cache_extent=[SIZE,SIZE],source_stages=STAGES,
               source_format_modes=list(FORMATS),source_selector_formula_authenticated=True,
               exact_derived_table_body_executed=True,source_table=t,game_runtime_bank_mapping_verified=False)
    return out
def verify(r,s,run_id,outcome,progress):
    need(outcome=="success" and r["status"]=="PASS" and r["run_id"]==run_id and r["config_sha256"]==s["private_config_sha256"] and
         r["private_guard"] is True and r["vulkan"] is True and r["registration_count"]==20 and r["private_source_hashes_match"] is True and
         progress["editor_native_exit"]==0 and progress["last_managed_checkpoint"]["phase"]=="complete","editor_identity_or_backend")
    cases=r["cases"]
    need(len(cases)==8 and [(x["first_slot"],x["format"]) for x in cases]==[(i,f) for i in (6,16) for f in FORMATS],"case_population")
    observed=0;full=0;matching=0
    for c in cases:
        need(c["outcome"] in ("OBSERVED","UNSUPPORTED","MANAGED_FAILURE"),"case_status")
        if c["outcome"]!="OBSERVED":continue
        need(c["target_format_exact"] is True and c["table_gpu_exact"] is True and c["dispatches"]==4 and c["bindings"]==12 and
             c["sentinel_checks"]==4 and all(type(x) is int and 0<=x<=SIZE*SIZE for x in c["indexed_written"]+c["reference_written"]),"case_comparison")
        observed+=1
        full+=int(c["indexed_written"]==c["reference_written"]==[SIZE*SIZE,SIZE*SIZE])
        matching+=int(c["nonfinite_components"]==0 and c["coverage_mismatch"]==[0,0] and c["different_over_tolerance"]==[0,0] and all(x>0 for x in c["indexed_written"]))
    need(observed>0,"no_format_case_observed")
    return dict(status=STATUS,cases=cases,observed_cases=observed,full_coverage_cases=full,matching_cases=matching,
                all_eight_full_coverage_matching=observed==full==matching==8,registered_slots=20,
                original_game_inputs_verified=False,original_fft_numeric_parity_verified=False,
                original_runtime_kernel_mapping_proven=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False,editor_progress=progress)
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True);st=sub.add_parser("stage")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    st.add_argument("--run-id",required=True);v=sub.add_parser("verify")
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--run-id",required=True);v.add_argument("--outcome",required=True)
    a=p.parse_args();result=dict(status="INCONCLUSIVE",water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id)
        else:
            s=json.loads(a.stage.read_text());cfg=a.private/"config.json";progress=old.bounded_progress(a.private,a.run_id);result["editor_progress"]=progress
            need(sha(cfg)==s["private_config_sha256"] and progress.get("private_launch_marker_matches") is True and progress["private_files_present"]["editor.log"] and progress["private_files_present"]["receipt.json"],"private_editor_commitment")
            r=json.loads((a.private/"receipt.json").read_text());result["editor_receipt"]=r;m=json.loads(cfg.read_text())
            for name,digest in [("indexed.compute",m["indexed_sha"])]+[(x["file"],x["sha256"]) for x in m["rows"]]:
                need(sha(a.private/name)==sha(a.project/"Assets/Private"/name)==digest,"editor_program_bytes_changed")
            for name,digest in [("table-float.f32",m["table_float_sha"]),("table-half.f32",m["table_half_sha"])]:
                need(sha(a.private/name)==digest,"table_bytes_changed")
            result=verify(r,s,a.run_id,a.outcome,progress)
    except Exception as exc:
        result["failure_type"]=type(exc).__name__
        if isinstance(exc,ValueError) and re.fullmatch(r"[a-z_]+",str(exc)):result["failure_reason"]=str(exc)
    dump(a.out,result);print("GT_FFT_SOURCE_FORMAT_PAIR_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("STAGED_SOURCE_DX11_TABLE_FORMAT_MATRIX",STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
