#!/usr/bin/env python3
"""Source-only Particle108 genuine four-keyword-pair reflected-name bridge.

Classify whether compiler-reflected SPIR-V location/name/type identities
survive DXBC -> SPIR-V -> HLSL -> SPIR-V for all four authentic source pairs.
Never assume compiler names == original DXBC semantics; never auto-patch.
No private names, source IDs, shader bytes, GUIDs or per-pair data leave runner.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from scripts import t3_original_particle108_spirv_translation as tr
from scripts.t3_spirv_interface_name_drift import (
    FIELDS, BOOLEAN_FIELDS, classify_reflected_names, read_reflection
)
from scripts.w1_recover_depth_passes import reflection, interfaces_match
from scripts.w1_recover_graphics_programs import translate

STATUS="T3_SOURCE_PARTICLE108_FOUR_PAIR_REFLECTED_NAME_LOCATION_BRIDGE_CLASSIFIED"
MAX_PRIVATE_REFLECTION_NAMES=256
EXPECTED={s+"_"+k for s in ("inputs","outputs") for k in FIELDS}


def _valid_public_name_counts(row):
    if type(row) is not dict or set(row)!=EXPECTED:
        raise ValueError("private_name_classifier_schema_mismatch")
    safe={}
    for key,value in row.items():
        suffix=key.split("_",1)[1]
        max_value=1 if suffix in BOOLEAN_FIELDS else MAX_PRIVATE_REFLECTION_NAMES
        if type(value) is not int or value<0 or value>max_value:
            raise ValueError("private_name_classifier_invalid_numeric_value")
        safe[key]=value
    return safe


def evaluate(private_pairs:list, workspace:Path, *,
             translator=translate, safe_reflector=reflection,
             raw_reflector=read_reflection,
             name_classifier=classify_reflected_names,
             pair_checker=interfaces_match):
    if (type(private_pairs) is not list or len(private_pairs)!=tr.PAIRS
        or not isinstance(workspace,Path) or not workspace.is_dir()
        or workspace.is_symlink()):
        raise ValueError("untrusted_particle108_name_bridge_scope")
    summary=Counter()
    for index,pair in enumerate(private_pairs):
        if (type(pair) is not tuple or len(pair)!=2
            or any(type(code) is not bytes or not 0<len(code)<=tr.MAX_PRIVATE_STAGE_BYTES
                   for code in pair)):
            raise ValueError("untrusted_real_original_DXBC_stage_pair")
        stages={}
        for stage,code in ((1,pair[0]),(0,pair[1])):
            stage_dir=workspace/f"variant-{index}-stage-{stage}"
            stage_dir.mkdir(exist_ok=False)
            # The translation result contains original stage hashes: NEVER
            # aggregate or display it, including unexpected failure text.
            report=translator(code,stage,stage_dir)
            if (type(report) is not dict or
                any(type(report.get(key)) is not bool for key in
                    ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")) or
                ("stage" in report and report["stage"]!=stage) or
                (report["hlsl_recovered"] and not report["vulkan11_valid"]) or
                (report["roundtrip_vulkan11_valid"] and not report["hlsl_recovered"])):
                raise ValueError("invalid_private_particle_name_bridge_translation_result")
            summary["stage_translation_attempts"]+=1
            summary["source_vulkan11_valid"]+=report["vulkan11_valid"]
            summary["hlsl_recovered"]+=report["hlsl_recovered"]
            summary["roundtrip_vulkan11_valid"]+=report["roundtrip_vulkan11_valid"]
            st={"safe":{},"names_complete":False,"unlocated":False}
            for state,enabled,filename in (
                    ("source",report["vulkan11_valid"],"original.spv"),
                    ("roundtrip",report["roundtrip_vulkan11_valid"],"roundtrip.spv")):
                if not enabled:
                    continue
                try:
                    f=stage_dir/filename
                    safe=tr._validate_reflection(safe_reflector(f))
                    raw=raw_reflector(f)
                    if type(raw) is not dict:
                        raise ValueError("untrusted_private_SPIRV_name_reflection")
                    st["safe"][state]=safe
                    st.setdefault("raw",{})[state]=raw
                    summary[state+"_reflection_available"]+=1
                except (ValueError,TypeError,KeyError,OSError,RuntimeError):
                    summary[state+"_reflection_unavailable"]+=1
            if len(st["safe"])==2:
                data=_valid_public_name_counts(name_classifier(
                    st["raw"]["source"],st["raw"]["roundtrip"],
                    st["safe"]["source"],st["safe"]["roundtrip"]))
                summary["source_vs_roundtrip_stage_names_classified"]+=1
                for key,value in data.items():
                    summary["name_"+key]+=value
                st["names_complete"]=all(
                    data[side+"_name_type_complete_preservation"]==1
                    for side in ("inputs","outputs"))
                st["unlocated"]=any(
                    data[side+"_"+state+"_unlocated_entries"]>0
                    for side in ("inputs","outputs")
                    for state in ("source","roundtrip"))
                summary["stages_full_located_name_type_preservation"]+=st["names_complete"]
                summary["stages_with_unlocated_builtin_or_other_rows"]+=st["unlocated"]
                summary["stages_full_located_name_type_no_unlocated_rows"]+=(
                    st["names_complete"] and not st["unlocated"])
                summary["stages_with_located_name_type_relocation_candidate"]+=(
                    st["names_complete"] and
                    any(data[side+"_name_type_relocation_only_candidate"]
                        for side in ("inputs","outputs")))
            # Keep source and roundtrip raw named interfaces in process-only
            # state so *none* appear in the returned aggregate report.
            stages[stage]=st
        vertex,fragment=stages[1],stages[0]
        for state in ("source","roundtrip"):
            if state in vertex["safe"] and state in fragment["safe"]:
                compatible=bool(pair_checker(vertex["safe"][state],
                                             fragment["safe"][state]))
                summary[state+"_stage_pair_interfaces_compared"]+=1
                summary[state+"_stage_pair_interfaces_compatible"]+=compatible
        if "source" in vertex["safe"] and "source" in fragment["safe"] and (
            "roundtrip" in vertex["safe"] and "roundtrip" in fragment["safe"]):
            original_ok=bool(pair_checker(vertex["safe"]["source"],
                                          fragment["safe"]["source"]))
            roundtrip_ok=bool(pair_checker(vertex["safe"]["roundtrip"],
                                           fragment["safe"]["roundtrip"]))
            summary["source_compatible_roundtrip_incompatible_pairs"]+=(
                original_ok and not roundtrip_ok)
            summary["incompatible_pairs_with_both_stages_name_type_complete"]+=(
                original_ok and not roundtrip_ok
                and vertex["names_complete"] and fragment["names_complete"])
            summary["incompatible_pairs_with_all_located_name_and_no_unlocated_rows"]+=(
                original_ok and not roundtrip_ok
                and vertex["names_complete"] and fragment["names_complete"]
                and not vertex["unlocated"] and not fragment["unlocated"])
    if summary["stage_translation_attempts"]!=tr.PAIRS*tr.STAGES:
        raise ValueError("incomplete_original_particle108_named_stage_scope")
    keys=(
        "stage_translation_attempts","source_vulkan11_valid",
        "hlsl_recovered","roundtrip_vulkan11_valid",
        "source_reflection_available","roundtrip_reflection_available",
        "source_reflection_unavailable","roundtrip_reflection_unavailable",
        "source_vs_roundtrip_stage_names_classified",
        "stages_full_located_name_type_preservation",
        "stages_with_unlocated_builtin_or_other_rows",
        "stages_full_located_name_type_no_unlocated_rows",
        "stages_with_located_name_type_relocation_candidate",
        "source_stage_pair_interfaces_compared",
        "source_stage_pair_interfaces_compatible",
        "roundtrip_stage_pair_interfaces_compared",
        "roundtrip_stage_pair_interfaces_compatible",
        "source_compatible_roundtrip_incompatible_pairs",
        "incompatible_pairs_with_both_stages_name_type_complete",
        "incompatible_pairs_with_all_located_name_and_no_unlocated_rows",
    )
    keys+=tuple("name_"+side+"_"+field for side in ("inputs","outputs")
                for field in FIELDS)
    out={"schema_version":1,"status":STATUS,
         "original_source_particle108_use_slots":108,
         "original_source_particle_renderer_objects":54,
         "source_original_keyword_variant_pairs":4,
         "source_original_shader_Pass_count":1,
         "counts":{key:int(summary[key]) for key in keys},
         "compiler_reflected_names_are_original_DXBC_semantics_verified":False,
         "compiler_reflected_names_sufficient_for_automatic_location_patch_verified":False,
         "source_shader_bytecode_names_hashes_guids_and_paths_published":False,
         "native_Unity_Android_Adreno_pixels_verified":False,
         "original_shader_is_actual_phone_fire_smoke_emitter_verified":False,
         "game_shader_assets_changed":False}
    return out


def probe(original:Path,manifest:Path):
    import shutil
    for tool in tr.TOOLS:
        if shutil.which(tool) is None:
            raise ValueError("required_original_private_translation_tool_missing")
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    private={}
    report=tr.source.source.load_original(original,manifest,
                                    private_particle_slot_counts=private)
    owner,pid=tr.source.select(private,report)
    path=original/"Raft_Data"/owner
    if (any(p.is_symlink() for p in (path,*path.parents))
        or fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("selected_original_particle108_shader_owner_SHA_drift")
    obj=[o for o in UnityPy.load(str(path)).file.objects.values()
         if o.path_id==pid]
    if len(obj)!=1 or obj[0].type.name!="Shader":
        raise ValueError("selected_original_particle108_Shader48_identity_drift")
    tree=obj[0].read_typetree()
    tables=[records(segments) for platform,segments in decoded_platforms(tree)
            if platform==4]
    if len(tables)!=1:
        raise ValueError("unique_original_D3D11_platform_required")
    baseline=tr.source.inspect(tree.get("m_ParsedForm"),tables[0])
    if (baseline.get("status")!=tr.source.STATUS
        or baseline.get("original_D3D11_program_table_records")!=16
        or baseline.get("matched_vertex_fragment_permutation_pairs")!=4
        or baseline.get("unmatched_vertex_permutations")!=0
        or baseline.get("unmatched_fragment_permutations")!=0):
        raise ValueError("original_particle108_stage_baseline_drift")
    pairs=tr.exact_four_pairs(tree["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-original-particle108-names-private-") as temp:
        result=evaluate(pairs,Path(temp))
    result["six_source_original_scenes_SHA_verified"]=True
    result["four_source_original_shader_owners_SHA_verified"]=True
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_particle108_name_bridge_output")
    try:
        result=probe(args.original,args.manifest)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "source_shader_bytecode_names_hashes_guids_and_paths_published":False,
                "native_Unity_Android_Adreno_pixels_verified":False,
                "game_shader_assets_changed":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_SOURCE_PARTICLE108_REFLECTED_NAME_BRIDGE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
