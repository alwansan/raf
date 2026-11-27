"""Actual producer/consumer, one shared fragment and two parameter blobs.

Uses freshly compiled authored DXBC only, real legacy translation, parameter
producer, compose and compiler. No mock transforms or Unity/game resources.
"""
import argparse
import base64
import copy
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import shutil

from tools.gt_next23b_bound_stage_identity.audit import verify_slots,sha,canonical
from tools.gt_next23b_translation_replay.audit import snapshot,replay,TOOLS
from scripts.w1_recover_graphics_programs import translate,records
from scripts.gt_original_921_all_variants import stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes
from scripts.gt_original_921_shaderlab import compose,verify_entrypoints

KEY="GT_AUTHORED_ALT"
def require(ok,msg):
    if not ok:raise AssertionError(msg)
def reject(fn,reason):
    try:fn()
    except ValueError as exc:
        require(str(exc).endswith(reason),"wrong rejection: "+str(exc));return reason
    raise AssertionError("accepted mutation "+reason)
def ints(*v):return struct.pack("<"+"i"*len(v),*v)
def string(s):
    b=s.encode("ascii");return ints(len(b))+b+bytes((-len(b))%4)
def param(label=None):
    if label is None:return ints(202012090,0,0)
    cb="GT_CBuffer"+label; tint="GT_Tint"+label; tex="_GT_Tex"+label
    return (ints(202012090,2)+string("$Globals")+ints(0,0,0)
        +string(cb)+ints(16,1)+string(tint)+ints(0,1,4,0,0,0)+ints(0)
        +ints(2)+string(tex)+ints(0,0,0,4)+string(cb)+ints(1,0,0))
def segments_for(entries):
    offset=0;table=[]
    for raw in entries:
        table.append(struct.pack("<III",offset,len(raw),1));offset+=len(raw)
    return (ints(len(entries))+b"".join(table),b"".join(entries))
def fixture(programs):
    vs,fs=[],[]
    common={"m_TextureParams":[],"m_ConstantBufferBindings":[],"m_ConstantBuffers":[]}
    pairs=[];slots=[]
    # Deliberately reverse the FS table: paired order != FS ordinal.
    for i in range(2):
        pair={"subshader":0,"pass":0}
        for stage,lane,ordinal,target,ref in ((1,"vs",i,vs,"program-000"),
                                             (0,"fs",1-i,fs,"program-001")):
            md={"m_BlobIndex":0 if stage else 1,"m_ShaderHardwareTier":0,
                "m_KeywordIndices":[0] if i else [],"m_GlobalKeywordIndices":[],"m_LocalKeywordIndices":[]}
            target.append(md)
            pair[lane]={"player_bucket":0,"bucket_ordinal":ordinal,"program_ref":ref,
                        "original_variant_metadata":md}
            slots.append({"subshader":0,"pass":0,"stage":stage,"player_bucket":0,"bucket_ordinal":ordinal,
                 "program_ref":ref,"metadata_sha256":sha(canonical(md)),"blob_index":md["m_BlobIndex"],
                 "keyword_indices":md["m_KeywordIndices"],"dxbc_sha256":sha(programs[ref]["source.dxbc"])})
        pairs.append(pair)
    fs.reverse()
    vprog={"m_PlayerSubPrograms":[vs],"m_SubPrograms":[],"m_CommonParameters":common,
           "m_ParameterBlobIndices":[[2,2]]}
    fprog={"m_PlayerSubPrograms":[fs],"m_SubPrograms":[],"m_CommonParameters":common,
           "m_ParameterBlobIndices":[[4,3]]}
    state={"m_Tags":{"tags":[["LightMode","Always"]]}}
    names=[["GT_AuthoredRegistry",0]]
    actual={"m_Type":0,"m_State":state,"m_NameIndices":names,"progVertex":vprog,"progFragment":fprog}
    parsed={"m_KeywordNames":[KEY],"m_KeywordFlags":[0],"m_SubShaders":[{"m_Passes":[actual]}]}
    passes=[{"subshader":0,"pass":0,"original_state":state,"original_name_indices":names,
             "original_vertex_program":vprog,"original_fragment_program":fprog,
             "matched_pairs":2,"unmatched_vertex":0,"unmatched_fragment":0}]
    manifest={"original_shader_ParsedForm_full_private":parsed,"paired":pairs,"unpaired":[],
              "original_passes":passes}
    witness={"parsed_form_sha256":sha(canonical(parsed)),"slots":slots}
    entries=[programs["program-000"]["source.dxbc"],programs["program-001"]["source.dxbc"],
             param(),param("A"),param("B")]
    return manifest,parsed,witness,segments_for(entries)
def save(root,name,data):(root/name).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
def reflect_route(shader,root,key,name):
    import re
    block=re.findall(r"(?ms)^HLSLPROGRAM\n(.*?)^ENDHLSL$",shader)[0]
    code=re.sub(r"(?m)^#pragma [^\n]*\n","",block)
    src=root/(name+".hlsl");src.write_text(code,encoding="utf-8")
    binary=root/(name+".spv")
    args=["glslangValidator","-V","-D","--target-env","vulkan1.1","-S","frag","-e","gt_fs_main",
          "-DSHADER_STAGE_FRAGMENT=1"]
    if key:args+=["-D"+KEY+"=1"]
    subprocess.run([*args,"-o",str(binary),str(src)],capture_output=True,check=True)
    subprocess.run(["spirv-val","--target-env","vulkan1.1",str(binary)],capture_output=True,check=True)
    reflection=json.loads(subprocess.check_output(["spirv-cross",str(binary),"--reflect"]))
    save(root,name+"-reflection.json",reflection)
    # Reflect actual compiled resources/CB member names, not text markers.
    tex=[v["name"] for v in reflection.get("separate_images",[])]
    samp=[v["name"] for v in reflection.get("separate_samplers",[])]
    ubos=reflection.get("ubos",[])
    require(len(tex)==len(samp)==len(ubos)==1,"unexpected actual reflected resource counts")
    members=reflection["types"][ubos[0]["type"]]["members"]
    require(len(members)==1 and members[0]["offset"]==0,"unexpected CB member geometry")
    return {"texture":tex[0],"sampler":samp[0],"cb":ubos[0]["name"],"member":members[0]["name"]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--fixture",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    a.out.mkdir(exist_ok=True)
    meta=json.loads((a.fixture/"fixture.json").read_text())
    pins={n:{"path":str(Path(shutil.which(n)).resolve()),"sha256":sha(Path(shutil.which(n)).read_bytes())} for n in TOOLS}
    with tempfile.TemporaryDirectory(prefix="gt-authored-bound-") as tmp:
        root=Path(tmp);programs={};proof={}
        for ref,name,stage in (("program-000","vertex",1),("program-001","shared_fragment",0)):
            code=(a.fixture/(name+".dxbc")).read_bytes()
            expected=meta["programs"][name]["dxbc_sha256"]
            require(sha(code)==expected,"authored source digest")
            folder=root/ref;folder.mkdir()
            result=translate(code,stage,folder)
            require(all(result[k] is True for k in ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),"actual translation")
            snap=snapshot(folder);proof[ref]=replay(stage,expected,snap,pins)
            programs[ref]={k:snap[k] for k in ("source.dxbc","private.hlsl")}
            dest=a.out/ref;dest.mkdir()
            for k,v in snap.items():(dest/k).write_bytes(v)
        manifest,parsed,source_witness,segments=fixture(programs)
        packet,counts=keyword_routes(parsed,manifest["paired"],[],manifest["original_passes"])
        produced=stage_parameter_records(manifest["paired"],[],manifest["original_passes"],
              records(segments),root,{ref:ref for ref in programs})
        require(produced["original_variant_stages_with_parameter_records"]==4,"producer count")
        require(produced["named_constant_buffer_reflected_offsets_verified"]==2,"actual named CB offsets")
        paramfile="original-private-parameter-records.json"
        params=json.loads((root/paramfile).read_text())
        save(root,"original-private-variant-manifest.json",manifest)
        save(root,"original-private-keyword-routes.json",packet)
        (root/"original-private-layout.txt").write_text('Shader "GT/AuthoredBound" {\nSubShader { Pass {\n// Original stage programs attach here\n} } }\n')
        def snaps():
            return {i:{n:(root/f"bound-stage-{i:03d}"/n).read_bytes() for n in ("resource-bound.hlsl","named-constant-buffers.hlsl")} for i in range(4)}
        bound=snaps()
        def check(**overrides):
            data=dict(manifest=manifest,parsed=parsed,segments=segments,source_witness=source_witness,
                 translation_proof=proof,programs=programs,parameter_packet=params,bound_files=bound,
                 route_packet=packet,expected_counts=(2,))
            data.update(overrides)
            return verify_slots(**data)
        private,report=check()
        require(report["stage_slots"]==4 and report["programs"]==2,"join counts")
        def compile_case(name):
            shader=compose(root,engine_keywords=True)
            verify_entrypoints(shader,root,routes=[[[],[KEY]]])
            (a.out/(name+".shader")).write_text(shader)
            return [reflect_route(shader,a.out,k,name+("-alt" if k else "-empty")) for k in (False,True)]
        before=compile_case("baseline")
        want=lambda label:{"texture":"_GT_Tex"+label,"sampler":"sampler_GT_Tex"+label,
                           "cb":"GT_CBuffer"+label,"member":"GT_Tint"+label}
        require(before==[want("A"),want("B")],"baseline actual reflected names: "+str(before))
        mutated=copy.deepcopy(params)
        mutated["stage_records"][1],mutated["stage_records"][3]=mutated["stage_records"][3],mutated["stage_records"][1]
        save(root,paramfile,mutated)
        # Reorder the two actual same-program FS records and their bound files.
        # The untouched composer still compiles and validates each exact route.
        for pos,other in ((1,3),(3,1)):
            for n,b in bound[other].items():(root/f"bound-stage-{pos:03d}"/n).write_bytes(b)
        after=compile_case("swapped")
        require(after==[want("B"),want("A")],"legacy wrong route names not reproduced: "+str(after))
        controls={"paired_record_and_folder_swap":reject(lambda:check(parameter_packet=mutated,bound_files=snaps()),
                    "parameter_record_slot_or_payload_mismatch")}
        controls["bound_only_swap"]=reject(lambda:check(bound_files=snaps()),"resource_bound_bytes_mismatch")
        forged=copy.deepcopy(mutated)
        # Even restoring coordinate labels/index cannot launder the wrong names.
        for pos in (1,3):
            for field in ("subshader","pass","stage","player_bucket","ordinal","original_parameter_blob_index"):
                forged["stage_records"][pos][field]=params["stage_records"][pos][field]
        controls["forged_coordinates"]=reject(lambda:check(parameter_packet=forged,bound_files=snaps()),
                    "parameter_record_slot_or_payload_mismatch")
        drift=copy.deepcopy(params);drift["blobs_base64"]["3"]=drift["blobs_base64"]["4"]
        controls["parameter_bytes"]=reject(lambda:check(parameter_packet=drift),"parameter_blob_bytes_drift")
        drift=copy.deepcopy(packet);drift[0]["routes"].reverse()
        controls["route_packet"]=reject(lambda:check(route_packet=drift),"route_packet_identity")
        save(a.out,"source-fixture.json",manifest);save(a.out,"actual-parameter-records.json",params)
        save(a.out,"source-slot-witness.json",source_witness);save(a.out,"translation-proof.json",proof)
        save(a.out,"binding-witness.json",private);save(a.out,"tool-pins.json",pins)
        for i,files in bound.items():
            folder=a.out/f"bound-stage-{i:03d}";folder.mkdir()
            for n,b in files.items():(folder/n).write_bytes(b)
        (a.out/"parameter-table-segment.bin").write_bytes(segments[0])
        (a.out/"parameter-payload-segment.bin").write_bytes(segments[1])
        summary={"status":"PASS_ACTUAL_AUTHORED_SHARED_PROGRAM_SLOT_BINDING",
          "actual_programs":2,"same_fragment_dxbc_for_both_routes":True,
          "source_routes":2,"bound_stage_slots":4,"distinct_parameter_blobs":3,
          "legacy_producer_actual_report":produced,"old_composer_and_compiler_accepted_swap":True,
          "reflected_baseline":before,"reflected_swapped":after,"negative_controls":controls,
          "original_assets_read":False,"original_2312_slots_verified":False,
          "semantic_equivalence_verified":False,"unity_bundle_or_gpu_proven":False,"production_install_allowed":False}
        save(a.out,"report.json",summary)
        print("GT_ACTUAL_BOUND_STAGE_IDENTITY "+json.dumps(summary,sort_keys=True))
if __name__=="__main__":main()
