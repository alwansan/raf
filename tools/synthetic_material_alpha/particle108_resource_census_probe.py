"""Authored Particle108 binding regression, actual SPIR-V compiler controls.
No original DXBC, RDEF, asset or renderer evidence is claimed.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.gt_particle108_unity_bindings import rebind_stage, BridgeError


def run(*args):
    result=subprocess.run(list(map(str,args)),capture_output=True,timeout=60)
    if result.returncode:
        raise RuntimeError("public_tool_failed:"+str(args[0])+":"+
                           (result.stdout+result.stderr).decode(errors="replace")[-1600:])
    return result.stdout


def require(ok,reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return sha256(data).hexdigest()


def verify():
    shader="""Texture2D<float4> texture_t0 : register(t0);
SamplerState sampler_s0 : register(s0);
Texture2D<float4> texture_t1 : register(t1);
SamplerState sampler_s1 : register(s1);
float4 main(float2 uv : TEXCOORD0) : SV_Target {
    return texture_t0.Sample(sampler_s0,uv)*0.25 + texture_t1.Sample(sampler_s1,uv)*0.75;
}
"""
    names=[("_AuthoredA",0),("_AuthoredB",1)]
    metadata={"m_CommonParameters":{"m_TextureParams":[
        {"m_Index":0,"m_NameIndex":0,"m_SamplerIndex":0},
        {"m_Index":1,"m_NameIndex":1,"m_SamplerIndex":1}]}}
    comment="// Texture2D<float4> ghost : register(t9, space8); sampler_s0\n"
    positives=[]
    negatives=[]
    with tempfile.TemporaryDirectory(prefix="gt-particle-binding-") as tmp:
        root=Path(tmp)
        def compile(text,tag):
            source=root/(tag+".hlsl"); source.write_text(text)
            spv=root/(tag+".spv"); stripped=root/(tag+".stripped.spv")
            run("glslangValidator","-D","-V","--target-env","vulkan1.1","-S","frag","-e","main",source,"-o",spv)
            run("spirv-val","--target-env","vulkan1.1",spv)
            run("spirv-opt","--strip-debug",spv,"-o",stripped)
            return stripped.read_bytes()
        for mode,text in (("bare",shader),
                          ("space0",shader.replace("register(t0)","register ( t0 , space0 )").replace("register(s1)","register(s1, space0)")),
                          ("comment",comment+shader)):
            rebound,report=rebind_stage(text,metadata,names,0)
            require(report["original_texture_registers_mapped"]==2 and report["original_sampler_registers_mapped"]==2,
                    "incomplete_authored_resource_mapping")
            require("_AuthoredA.Sample(sampler_AuthoredA" in rebound and "_AuthoredB.Sample(sampler_AuthoredB" in rebound,
                    "wrong_authored_binding_names")
            if mode=="comment":require(rebound.startswith(comment),"comment_changed")
            a=compile(text,mode+"-input")
            b=compile(rebound,mode+"-output")
            require(a==b,"rebind_changed_stripped_SPIRV:"+mode)
            positives.append({"mode":mode,"stripped_spirv_sha256":digest(a),"bytes":len(a),
                              "binding_report":report})
        # Distinct valid program is not equivalence: sampling a different
        # texture/sampler pair must alter stripped SPIR-V.
        rebound,_=rebind_stage(shader,metadata,names,0)
        baseline=compile(rebound,"pair-baseline")
        swapped=rebound.replace("_AuthoredA.Sample(sampler_AuthoredA","_AuthoredB.Sample(sampler_AuthoredB")
        wrong=compile(swapped,"wrong-pair")
        require(baseline!=wrong,"wrong_resource_pair_not_distinguished")
        negatives.append({"case":"wrong_valid_resource_pair","rejected":True,
                          "baseline_sha256":digest(baseline),"mutated_sha256":digest(wrong)})
        changes=(
            ("nonzero_texture_space","register(t0)","register(t0, space1)"),
            ("unregistered_texture","texture_t0 : register(t0);","texture_t0;"),
            ("descriptor_array","texture_t0 : register(t0);","texture_t0[2] : register(t0);"),
            ("texture_wrong_register_class","register(t0)","register(s7)"),
            ("duplicate_translated_slot","register(t1)","register(t0)"),
        )
        for label,old,new in changes:
            try:
                rebind_stage(shader.replace(old,new),metadata,names,0)
            except BridgeError as exc:
                expected="TRANSLATOR_RESOURCE_COLLISION" if label=="duplicate_translated_slot" else "TRANSLATOR_RESOURCE_REGISTER_UNPROVEN"
                require(str(exc)==expected,"unexpected_rejection:"+label+":"+str(exc))
                negatives.append({"case":label,"rejected":True,"reason":str(exc)})
            else:
                raise ValueError("unsupported_texture_accepted:"+label)
    return {"status":"PASS_AUTHORED_PARTICLE108_RESOURCE_CENSUS_AND_SPIRV_PARITY",
            "positive_cases":positives,"negative_controls":negatives,
            "actual_glslang_compilations":8,"actual_spirv_validations":8,
            "actual_spirv_normalizations":8,"actual_original_DXBC_or_RDEF_used":False,
            "original_assets_read":False,"original_fire_or_white_mesh_repaired":False,
            "Unity_or_Android_pixels_verified":False,"XAPK_requested":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"fresh_output_required")
    result=verify()
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
