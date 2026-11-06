#!/usr/bin/env python3
"""SHA-authentic private four-pair Particle108 glslang HLSL stage IO-map options.

Generated shaders, original DXBC, original semantic names, private SPIR-V
and per-pair locations never leave the ephemeral CI runner. Successful
Vulkan stage linking is NOT numerical or Unity Android visual parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from scripts import t3_original_particle108_spirv_translation as base
from scripts.t3_particle108_roundtrip_interface_diagnostic import _stage, _join, PAIRS
from scripts.w1_recover_depth_passes import reflection
from scripts.w1_recover_graphics_programs import translate

STATUS="T3_SHA_ORIGINAL_PARTICLE108_GLSLANG_HLSL_STAGE_IO_MAP_CANDIDATES"
CONFIGS={
    "baseline":(),
    "iomap":("--hlsl-iomap",),
    "aml":("--auto-map-locations",),
    "iomap_aml":("--hlsl-iomap","--auto-map-locations"),
}
COUNT_FIELDS=(
    "source_pairs_linked",
    *[key+"_"+suffix for key in CONFIGS for suffix in (
      "stage_compiles_valid","pairs_compared","pairs_linked",
      "fragment_missing_vertex_location","fragment_same_location_type_mismatch")],
)

def compile_alternative(hlsl,spv,stage,flags):
    if (type(stage) is not int or stage not in (0,1) or
        not isinstance(hlsl,Path) or not hlsl.is_file() or hlsl.is_symlink() or
        not 0<hlsl.stat().st_size<=1024*1024 or
        not isinstance(spv,Path) or spv.exists() or spv.is_symlink() or
        type(flags) is not tuple or not all(type(x) is str and x in
            ("--hlsl-iomap","--auto-map-locations") for x in flags)):
        raise ValueError("unsafe_private_hlsl_alternative_compiler_scope")
    suffix={0:"frag",1:"vert"}[stage]
    command=["glslangValidator","-V","-D","-S",suffix,"-e","main",
             *flags,"-o",str(spv),str(hlsl)]
    try:
        process=subprocess.run(command,capture_output=True,timeout=90,check=False)
        if process.returncode or not spv.is_file() or not 0<spv.stat().st_size<=8*1024*1024:
            return False
        validated=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(spv)],
                                 capture_output=True,timeout=45,check=False)
        return validated.returncode==0
    except (subprocess.TimeoutExpired,OSError):
        return False

def compare_pair(stages):
    """Count only full stage link; never publish per-output locations or types."""
    if type(stages) is not dict or set(stages)!={0,1}:
        raise ValueError("invalid_private_stage_pair_map")
    v=_stage(stages[1])
    f=_stage(stages[0])
    missing,different=_join(v,f)
    return {"linked":int(missing==0 and different==0),
            "missing":missing,"type_mismatch":different}

def evaluate(pairs,private,*,translator=translate,reflector=reflection,
             compiler=compile_alternative):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(code) is not bytes or not 0<len(code)<=4*1024*1024
                for code in pair) for pair in pairs) or
        not isinstance(private,Path) or not private.is_dir() or private.is_symlink()):
        raise ValueError("unverified_original_private_four_pairs")
    counts=Counter()
    for index,(vertex,fragment) in enumerate(pairs):
        all_stages={key:{} for key in CONFIGS}
        originals={}
        for kind,code in ((1,vertex),(0,fragment)):
            folder=private/f"pair-{index}-stage-{kind}"
            folder.mkdir(exist_ok=False)
            result=translator(code,kind,folder)
            if (type(result) is not dict or
                any(result.get(key) is not True for key in
                    ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"))):
                raise ValueError("original_private_HLSL_source_translation_failed")
            originals[kind]=_stage(reflector(folder/"original.spv"))
            all_stages["baseline"][kind]=_stage(reflector(folder/"roundtrip.spv"))
            counts["baseline_stage_compiles_valid"]+=1
            for key,flags in CONFIGS.items():
                if key=="baseline":
                    continue
                private_spv=folder/(key+".spv")
                if compiler(folder/"private.hlsl",private_spv,kind,flags):
                    all_stages[key][kind]=_stage(reflector(private_spv))
                    counts[key+"_stage_compiles_valid"]+=1
        counts["source_pairs_linked"]+=compare_pair(originals)["linked"]
        for key,stages in all_stages.items():
            if len(stages)!=2:
                continue
            row=compare_pair(stages)
            counts[key+"_pairs_compared"]+=1
            counts[key+"_pairs_linked"]+=row["linked"]
            counts[key+"_fragment_missing_vertex_location"]+=row["missing"]
            counts[key+"_fragment_same_location_type_mismatch"]+=row["type_mismatch"]
    if (counts["source_pairs_linked"]!=PAIRS or
        counts["baseline_stage_compiles_valid"]!=PAIRS*2 or
        counts["baseline_pairs_compared"]!=PAIRS):
        raise ValueError("original_SHA_authentic_baseline_identity_drift")
    return {
        "schema_version":1,"status":STATUS,"original_keyword_pairs":PAIRS,
        "counts":{key:int(counts[key]) for key in COUNT_FIELDS},
        "input_compilers_glslang_flags_tested":list(CONFIGS),
        "original_DXBC_semantic_to_recompiled_SPIRV_location_proven":False,
        "Android_Unity_asset_modified":False,
        "numeric_pixels_or_Adreno_acceptance_verified":False,
        "private_HLSL_original_bytecode_program_names_or_locations_published":False,
    }

def probe(original,manifest):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    for tool in base.TOOLS:
        if shutil.which(tool) is None:
            raise ValueError("missing_compiler_dependency")
    selection={}
    source_report=base.source.source.load_original(
        original,manifest,private_particle_slot_counts=selection)
    owner,pid=base.source.select(selection,source_report)
    path=original/"Raft_Data"/owner
    if any(p.is_symlink() for p in (path,*path.parents)) or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("invalid_original_particle_owner_SHA")
    matched=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(matched)!=1 or matched[0].type.name!="Shader":
        raise ValueError("ambiguous_original_private_particle_Shader")
    parsed=matched[0].read_typetree()
    tables=[records(segments) for platform,segments in decoded_platforms(parsed) if platform==4]
    if len(tables)!=1:
        raise ValueError("ambiguous_original_particle_D3D11_stage_table")
    baseline=base.source.inspect(parsed["m_ParsedForm"],tables[0])
    if (baseline.get("status")!=base.source.STATUS or
        baseline.get("original_D3D11_program_table_records")!=16 or
        baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS):
        raise ValueError("invalid_original_Particle108_stage_pair_baseline")
    pairs=base.exact_four_pairs(parsed["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-particle108-glslang-iomap-") as directory:
        report=evaluate(pairs,Path(directory))
    report["source_original_four_Shader_Material_owner_SHA_verified"]=True
    report["source_original_six_scenes_SHA_verified"]=True
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original","manifest","out"):
        parser.add_argument("--"+field,type=Path,required=True)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_private_candidate_output")
    try:
        report=probe(args.original,args.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "private_HLSL_original_bytecode_program_names_or_locations_published":False,
                "numeric_pixels_or_Adreno_acceptance_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_GLSLANG_IO_OPTIONS_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
