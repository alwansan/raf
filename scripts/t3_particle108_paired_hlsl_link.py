#!/usr/bin/env python3
"""Test genuine SHA-pinned Particle108 generated HLSL VS/FS jointly linked by glslang.

Only aggregate success/failure + SPIR-V entrypoint stage counts may leave runner.
Original programs, recovered HLSL, source paths, SHA values, private identifiers,
per-variant Locations, SPIR-V and compiler stdout/stderr remain ephemeral.
A successful linked SPIR-V module is NOT an Android Unity shader repair.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from scripts import t3_original_particle108_spirv_translation as base
from scripts.t3_particle108_glslang_io_map_experiment import compare_pair
from scripts.t3_particle108_roundtrip_interface_diagnostic import PAIRS, _stage
from scripts.w1_recover_depth_passes import reflection
from scripts.w1_recover_graphics_programs import translate

STATUS="T3_SHA_ORIGINAL_PARTICLE108_GLSLANG_LINKED_HLSL_PAIR_CLASSIFIED"
OPTIONS={
    "linked":(),
    "linked_iomap":("--hlsl-iomap",),
    "linked_aml":("--auto-map-locations",),
    "linked_iomap_aml":("--hlsl-iomap","--auto-map-locations"),
}
STAGE_VERTEX=0
STAGE_FRAGMENT=4
MAX_SPIRV=8*1024*1024
MAX_HLSL=1024*1024
PER_OPTION=(
    "attempts","command_success","vulkan11_valid",
    "modules_with_vertex_entry","modules_with_fragment_entry",
    "modules_with_both_vertex_fragment_entries",
    "modules_with_only_one_graphics_entry",
    "modules_with_other_execution_model",
    "modules_missing_spirv_binary",
)
COUNT_KEYS=(
    "source_pairs_linked","separate_roundtrip_pairs_linked",
    *[opt+"_"+key for opt in OPTIONS for key in PER_OPTION],
)

def entrypoint_execution_models(data):
    """Return numeric execution models from a structurally bounded SPIR-V binary."""
    if type(data) is not bytes or not 20<=len(data)<=MAX_SPIRV or len(data)%4:
        raise ValueError("invalid_private_spirv_binary_size")
    words=struct.unpack("<"+"I"*(len(data)//4),data)
    if words[0]!=0x07230203 or words[3]==0:
        raise ValueError("invalid_private_spirv_header")
    models=[]
    offset=5
    while offset<len(words):
        instruction=words[offset]
        count=instruction>>16
        opcode=instruction&0xffff
        if count==0 or count>len(words)-offset:
            raise ValueError("invalid_private_spirv_instruction")
        if opcode==15: # OpEntryPoint <ExecutionModel> <id> <name> [interface IDs]
            if count<4:
                raise ValueError("truncated_private_spirv_entrypoint")
            model=words[offset+1]
            # The name must contain a null terminator in at least the fourth word.
            # Do not decode or publish the private entrypoint name.
            name_words=words[offset+3:offset+count]
            if not any(0 in struct.pack("<I",word) for word in name_words):
                raise ValueError("unterminated_private_spirv_entrypoint_name")
            models.append(model)
        offset+=count
    return models

def stage_result(models):
    """Count-only stage coverage; multiple entrypoints do not imply Vulkan linking."""
    if type(models) not in (tuple,list) or any(type(m) is not int or m<0 or m>4095 for m in models):
        raise ValueError("invalid_private_spirv_execution_models")
    names=set(models)
    return {
        "vertex":int(STAGE_VERTEX in names),
        "fragment":int(STAGE_FRAGMENT in names),
        "both":int(STAGE_VERTEX in names and STAGE_FRAGMENT in names),
        "only_one":int(len(models)==1 and len(names & {STAGE_VERTEX,STAGE_FRAGMENT})==1),
        "other":int(bool(names-{STAGE_VERTEX,STAGE_FRAGMENT})),
    }

def joint_compile(vertex_hlsl,fragment_hlsl,output,flags):
    """Use ONLY allowlisted glslang flags; return no private stdout or code."""
    if (not isinstance(vertex_hlsl,Path) or not isinstance(fragment_hlsl,Path)
        or not isinstance(output,Path) or type(flags) is not tuple
        or flags not in OPTIONS.values() or
        output.exists() or output.is_symlink() or
        vertex_hlsl==fragment_hlsl or
        any(p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=MAX_HLSL
            for p in (vertex_hlsl,fragment_hlsl))):
        raise ValueError("unsafe_private_paired_hlsl_compilation")
    root=output.parent
    if not root.is_dir() or root.is_symlink():
        raise ValueError("unsafe_private_output_folder")
    # glslang identifies stages by these extensions, which are not present
    # on SPIRV-Cross default private.hlsl outputs. Copies are runner-private.
    vertex=root/(output.stem+".vert.hlsl")
    fragment=root/(output.stem+".frag.hlsl")
    for src,dst in ((vertex_hlsl,vertex),(fragment_hlsl,fragment)):
        if dst.exists() or dst.is_symlink() or dst==src:
            raise ValueError("private_staging_collision")
        dst.write_bytes(src.read_bytes())
    command=["glslangValidator","-V","-D","-l","-e","main",
             *flags,"-o",str(output),str(vertex),str(fragment)]
    try:
        compiled=subprocess.run(command,capture_output=True,timeout=90,check=False)
        valid_file=output.is_file() and 20<=output.stat().st_size<=MAX_SPIRV
        result={
            "command_success":int(compiled.returncode==0),
            "vulkan11_valid":0,"missing_spirv_binary":int(not valid_file),
            "models":[],
        }
        if not valid_file:
            return result
        checked=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(output)],
                               capture_output=True,timeout=45,check=False)
        result["vulkan11_valid"]=int(checked.returncode==0)
        if result["vulkan11_valid"]:
            result["models"]=entrypoint_execution_models(output.read_bytes())
        return result
    except (OSError,subprocess.TimeoutExpired):
        return {"command_success":0,"vulkan11_valid":0,
                "missing_spirv_binary":int(not output.exists()),"models":[]}

def classify_joint_result(raw):
    if (type(raw) is not dict or set(raw)!={"command_success","vulkan11_valid",
           "missing_spirv_binary","models"} or
        any(type(raw[k]) is not int or raw[k] not in (0,1) for k in
            ("command_success","vulkan11_valid","missing_spirv_binary"))):
        raise ValueError("invalid_private_linker_result")
    # If command success is false but a usable module exists, still track both,
    # avoiding incorrectly claiming a successful compiler/linker.
    stage=stage_result(raw["models"])
    return {
        "attempts":1,
        "command_success":raw["command_success"],
        "vulkan11_valid":raw["vulkan11_valid"],
        "modules_with_vertex_entry":int(raw["vulkan11_valid"] and stage["vertex"]),
        "modules_with_fragment_entry":int(raw["vulkan11_valid"] and stage["fragment"]),
        "modules_with_both_vertex_fragment_entries":int(raw["vulkan11_valid"] and stage["both"]),
        "modules_with_only_one_graphics_entry":int(raw["vulkan11_valid"] and stage["only_one"]),
        "modules_with_other_execution_model":int(raw["vulkan11_valid"] and stage["other"]),
        "modules_missing_spirv_binary":raw["missing_spirv_binary"],
    }

def evaluate(pairs,workspace,*,translator=translate,reflector=reflection,
             linker=joint_compile):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(code) is not bytes or not 0<len(code)<=4*1024*1024
                for code in pair) for pair in pairs) or
        not isinstance(workspace,Path) or not workspace.is_dir() or workspace.is_symlink()):
        raise ValueError("invalid_authentic_fourpair_private_scope")
    totals=Counter()
    for idx,(vs_code,fs_code) in enumerate(pairs):
        source={}
        roundtrip={}
        filenames={}
        for stage,code in ((1,vs_code),(0,fs_code)):
            folder=workspace/f"pair-{idx}-stage-{stage}"
            folder.mkdir(exist_ok=False)
            report=translator(code,stage,folder)
            if (type(report) is not dict or any(report.get(k) is not True for k in
                ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"))):
                raise ValueError("authentic_private_translation_incomplete")
            source[stage]=_stage(reflector(folder/"original.spv"))
            roundtrip[stage]=_stage(reflector(folder/"roundtrip.spv"))
            filenames[stage]=folder/"private.hlsl"
        totals["source_pairs_linked"]+=compare_pair(source)["linked"]
        totals["separate_roundtrip_pairs_linked"]+=compare_pair(roundtrip)["linked"]
        for key,flags in OPTIONS.items():
            directory=workspace/f"pair-{idx}-paired-{key}"
            directory.mkdir(exist_ok=False)
            raw=linker(filenames[1],filenames[0],directory/"linked.spv",flags)
            row=classify_joint_result(raw)
            for suffix,value in row.items():
                totals[key+"_"+suffix]+=value
    if totals["source_pairs_linked"]!=PAIRS:
        raise ValueError("authentic_source_SPIRV_pair_drift")
    return {
        "schema_version":1,"status":STATUS,"original_keyword_pairs":PAIRS,
        "counts":{k:int(totals[k]) for k in COUNT_KEYS},
        "single_linked_module_not_proof_of_two_stage_pipeline":True,
        "original_DXBC_semantic_to_SPIRV_location_proven":False,
        "original_Unity_Android_game_assets_modified":False,
        "native_Adreno_pixels_verified":False,
        "private_HLSL_SPIRV_original_programs_and_semantics_published":False,
    }

def probe(original,manifest):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    for name in base.TOOLS:
        if shutil.which(name) is None:
            raise ValueError("missing_private_compiler_dependency")
    selection={}
    baseline=base.source.source.load_original(original,manifest,
                                               private_particle_slot_counts=selection)
    owner,pid=base.source.select(selection,baseline)
    path=original/"Raft_Data"/owner
    if any(p.is_symlink() for p in (path,*path.parents)) or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("invalid_original_particle_owner_SHA")
    matched=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(matched)!=1 or matched[0].type.name!="Shader":
        raise ValueError("ambiguous_original_particle_Shader")
    parsed=matched[0].read_typetree()
    tables=[records(segments) for platform,segments in decoded_platforms(parsed) if platform==4]
    if len(tables)!=1:
        raise ValueError("ambiguous_original_D3D11_program_table")
    original=base.source.inspect(parsed["m_ParsedForm"],tables[0])
    if (original.get("status")!=base.source.STATUS or
        original.get("original_D3D11_program_table_records")!=16 or
        original.get("matched_vertex_fragment_permutation_pairs")!=PAIRS):
        raise ValueError("original_Particle108_pair_selection_drift")
    pairs=base.exact_four_pairs(parsed["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-paired-glslang-") as d:
        report=evaluate(pairs,Path(d))
    report["source_original_four_Shader_Material_owner_SHA_verified"]=True
    report["source_original_six_scenes_SHA_verified"]=True
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for arg in ("original","manifest","out"):
        parser.add_argument("--"+arg,type=Path,required=True)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_private_paired_glslang_report_path")
    try:
        report=probe(args.original,args.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "private_HLSL_SPIRV_original_programs_and_semantics_published":False,
                "native_Adreno_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_PAIRED_GLSLANG_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
