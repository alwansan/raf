"""Compile authored mixed-scope candidate marker programs to actual Vulkan SPIR-V.
No original program, Unity, or shader installation. The marker oracle checks
the exact constant carried by each stage, rather than accepting compilation
alone. Local/global pragma semantics remain unproved without Unity.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts import gt_keyword_candidate_plan as m
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tests"))
from test_gt_keyword_candidate_plan import make,A,B

def run(args,**kw):
    return subprocess.run(args,check=True,text=True,capture_output=True,timeout=30,**kw).stdout
def probe():
    manifest,packet,proof,_=make();plan=m.plan(manifest,packet,proof);row=plan["passes"][0]
    programs={}
    for i in range(4):
        # Unique stage-local integral marker encoded as a float constant.
        programs[i]=f"float4 gt_vs_main(float4 p:POSITION):SV_POSITION {{ return float4(p.x+{i+11}.0,p.y,p.z,p.w); }}\nfloat4 gt_fs_main():SV_Target {{ return float4({i+21}.0,0,0,1); }}"
    pragmas,code=m.emit(row,programs);records=[]
    with tempfile.TemporaryDirectory() as t:
        root=Path(t);src=root/"route.hlsl";spv=root/"route.spv"
        src.write_text(code)
        for i,keys in enumerate(row["engine_keys"]):
            for stage,entry,marker in (("vert","gt_vs_main",i+11),("frag","gt_fs_main",i+21)):
                spv.unlink(missing_ok=True)
                run(["glslangValidator","-V","-D","--target-env","vulkan1.1","-S",stage,"-e",entry,*[f"-D{k}=1" for k in keys],"-o",str(spv),str(src)])
                run(["spirv-val","--target-env","vulkan1.1",str(spv)])
                dis=run(["spirv-dis",str(spv)])
                # The selected stage contains exactly its route-specific constant.
                candidates={int(v) for v in re.findall(r"OpConstant %float (\d+)(?:\s|$)",dis) if 11<=int(v)<=24}
                if candidates!={marker}:raise ValueError("compiled_stage_marker_mismatch")
                model="Vertex" if stage=="vert" else "Fragment"
                if f'OpEntryPoint {model} ' not in dis or f'"{entry}"' not in dis:raise ValueError("compiled_execution_model")
                records.append(dict(route=i,stage=stage,marker=marker,sha256=m.sha(spv.read_bytes())))
        # Actual compiler failure for an unmapped empty route. No fallback.
        src.write_text(code.replace(f"#elif !defined({A}) && !defined({B})\n"+programs[1]+"\n",""))
        bad=subprocess.run(["glslangValidator","-V","-D","--target-env","vulkan1.1","-S","frag","-e","gt_fs_main","-o",str(spv),str(src)],text=True,capture_output=True,timeout=30)
        if bad.returncode==0 or "Unmapped_original_keyword_set" not in bad.stdout+bad.stderr:raise ValueError("unmapped_compiler_control_not_rejected")
    return dict(status="PASS_AUTHORED_CANDIDATE_ROUTER_COMPILER_ONLY",summary=m.safe_summary(plan),actual_compiled_and_validated_stages=len(records),records=records,actual_unmapped_compiler_rejections=1,original_assets_read=False,original_runtime_verified=False,production_activation=False,Unity_executed=False,Android_device=False,XAPK=False)
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError("fresh_output")
    r=probe();a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n");print(json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
