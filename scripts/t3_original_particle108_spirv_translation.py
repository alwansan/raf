#!/usr/bin/env python3
"""T3 original Particle108 all FOUR genuine DXBC VS/FS pairs -> Vulkan1.1 SPIR-V.

Use exact SHA-pinned six-scene ParticleSystemRenderer -> Material21 -> Shader48
private source identity. Four identical serialized keyword AND player-bucket
permutations must link to true DXBC stage programs before translation.
All eight original code blobs, translated SPIR-V, HLSL and per-program hashes
remain in a disposable runner-private folder. Reports are aggregate only.
No native Android shader or game asset is changed or inferred to render.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_particle108_dxbc_feasibility as source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import (
    linked_program, stage_variants, variant_key, reflection, interfaces_match,
)
from scripts.t3_stage_io_drift import classify_stage_io

STATUS = "SHA_ORIGINAL_PARTICLE108_FOUR_KEYWORD_PAIRS_VULKAN_SPIRV_CPU_CLASSIFIED"
TOOLS = ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator")
PAIRS = 4
STAGES = 2
SHADER_TABLE_RECORDS = 16
MAX_PRIVATE_STAGE_BYTES = 8 * 1024 * 1024
MAX_STAGE_REFLECTION_SLOTS = 256
IO_KEYS = ("identical","original_slots","roundtrip_slots","removed_locations",
           "added_locations","same_location_type_changes",
           "type_multiset_equal","location_only_remap_candidate")
IO_BOOLEAN = frozenset(("identical","type_multiset_equal","location_only_remap_candidate"))


def exact_four_stage_links(parsed:dict, table:list, *, linker=linked_program):
    """Return paired DXBC and the exact serialized bucket and ordinal of each stage."""
    if (type(parsed) is not dict or
        type(parsed.get("m_SubShaders")) is not list or
        len(parsed["m_SubShaders"])!=1 or
        type(parsed["m_SubShaders"][0]) is not dict or
        type(parsed["m_SubShaders"][0].get("m_Passes")) is not list or
        len(parsed["m_SubShaders"][0]["m_Passes"])!=1):
        raise ValueError("untrusted_original_particle108_one_Pass_graph")
    p=parsed["m_SubShaders"][0]["m_Passes"][0]
    if type(p) is not dict or type(p.get("m_Type")) is not int or p["m_Type"]!=0:
        raise ValueError("non_normal_original_particle108_pass")
    if (type(table) is not list or len(table)!=SHADER_TABLE_RECORDS or
        any(type(e) is not tuple or len(e)!=2 or type(e[0]) is not int
            or type(e[1]) is not bytes or not e[1] for e in table)):
        raise ValueError("untrusted_original_particle108_program_table")
    stages={}
    for field,kind in (("progVertex",1),("progFragment",0)):
        program=p.get(field)
        if type(program) is not dict:
            raise ValueError("missing_original_Particle108_Vertex_or_Fragment")
        rows=stage_variants(program)
        if len(rows)!=PAIRS:
            raise ValueError("not_four_original_particle108_stage_variants")
        indexed={}
        for bucket,ordinal,meta in rows:
            if (type(ordinal) is not int or ordinal<0 or type(meta) is not dict or
                (bucket is not None and (type(bucket) is not int or bucket<0))):
                raise ValueError("invalid_original_shader_stage_variant_metadata")
            key=(bucket,variant_key(meta))
            if key in indexed:
                raise ValueError("duplicate_original_shader_keyword_player_bucket")
            indexed[key]=(ordinal,meta)
        stages[kind]=indexed
    if len(stages[1].keys() & stages[0].keys())!=PAIRS:
        raise ValueError("original_particle108_stage_keyword_bucket_mismatch")
    pairs=[]
    for key,(vert_ordinal,vert_meta) in stages[1].items():
        fragment_ordinal,fragment_meta=stages[0][key]
        vs,_=linker(vert_meta,table,1)
        fs,_=linker(fragment_meta,table,0)
        if (type(vs) is not bytes or type(fs) is not bytes or
            not vs or not fs or max(len(vs),len(fs))>MAX_PRIVATE_STAGE_BYTES):
            raise ValueError("invalid_original_particle108_linked_DXBC_bytes")
        pairs.append(((vs,key[0],vert_ordinal),(fs,key[0],fragment_ordinal)))
    if len(pairs)!=PAIRS:
        raise ValueError("incomplete_original_particle108_compiled_pairs")
    return pairs


def exact_four_pairs(parsed:dict, table:list, *, linker=linked_program):
    """Return ONLY private paired original DXBC buffers; no guessed keywords."""
    return [(vs[0],fs[0]) for vs,fs in exact_four_stage_links(parsed,table,linker=linker)]


def _validate_reflection(data:dict):
    if (type(data) is not dict or
        set(data)!={"inputs","outputs","resource_slots"} or
        type(data["inputs"]) is not list or
        type(data["outputs"]) is not list or
        type(data["resource_slots"]) is not dict):
        raise ValueError("invalid_private_stage_SPIRV_reflection_schema")
    if (len(data["inputs"])>MAX_STAGE_REFLECTION_SLOTS or
        len(data["outputs"])>MAX_STAGE_REFLECTION_SLOTS or
        len(data["resource_slots"])>16):
        raise ValueError("unbounded_private_stage_SPIRV_reflection")
    for side in ("inputs","outputs"):
        for item in data[side]:
            if (type(item) is not dict or set(item)!={"location","type"} or
                type(item["location"]) is not int or item["location"]<0 or
                type(item["type"]) is not str or len(item["type"])>90):
                raise ValueError("invalid_private_stage_SPIRV_IO_record")
        if len({item["location"] for item in data[side]})!=len(data[side]):
            raise ValueError("duplicate_private_SPIRV_IO_location")
    for key,rows in data["resource_slots"].items():
        if (type(key) is not str or key not in
            ("ubos","ssbos","textures","separate_images","separate_samplers","images")
            or type(rows) is not list or len(rows)>MAX_STAGE_REFLECTION_SLOTS or
            any(type(row) is not list or len(row)!=2 for row in rows)):
            raise ValueError("invalid_private_SPIRV_resource_binding_shape")
    return data


def evaluate(pairs:list, temporary:Path, *, translator=translate,
             reflector=reflection, pair_checker=interfaces_match,
             io_classifier=classify_stage_io):
    """Safe aggregate from eight private compilers; failed stage ≠ device fix."""
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        not isinstance(temporary,Path) or not temporary.is_dir() or
        temporary.is_symlink()):
        raise ValueError("invalid_fourpair_private_SPIRV_translation_scope")
    counts=Counter()
    for i,pair in enumerate(pairs):
        if (type(pair) is not tuple or len(pair)!=2 or
            any(type(code) is not bytes or not code or len(code)>MAX_PRIVATE_STAGE_BYTES
                for code in pair)):
            raise ValueError("invalid_private_original_DXBC_pair")
        stages={}
        for stage,code in ((1,pair[0]),(0,pair[1])):
            path=temporary/("variant-"+str(i)+"-stage-"+str(stage))
            path.mkdir(exist_ok=False)
            # Translator returns per-program hashes, which are NEVER passed
            # into the public report or to error logs.
            t=translator(code,stage,path)
            if (type(t) is not dict or
                any(type(t.get(k)) is not bool for k in
                    ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")) or
                ("stage" in t and t["stage"]!=stage) or
                (t["hlsl_recovered"] and not t["vulkan11_valid"]) or
                (t["roundtrip_vulkan11_valid"] and not t["hlsl_recovered"])):
                raise ValueError("invalid_private_DXBC_translator_result")
            counts["stage_translation_attempts"]+=1
            counts["source_stage_spirv_vulkan11_valid"]+=t["vulkan11_valid"]
            counts["stage_hlsl_recovered"]+=t["hlsl_recovered"]
            counts["stage_hlsl_roundtrip_spirv_vulkan11_valid"]+=t["roundtrip_vulkan11_valid"]
            reflections={}
            for field,valid,filename in (
                    ("original",t["vulkan11_valid"],"original.spv"),
                    ("roundtrip",t["roundtrip_vulkan11_valid"],"roundtrip.spv")):
                if valid:
                    try:
                        reflections[field]=_validate_reflection(reflector(path/filename))
                        counts[field+"_stage_reflections"]+=1
                    except (ValueError, OSError, TypeError, RuntimeError, KeyError):
                        counts[field+"_stage_reflection_failures"]+=1
            if "original" in reflections and "roundtrip" in reflections:
                x,y=reflections["original"],reflections["roundtrip"]
                counts["stage_original_roundtrip_reflection_pairs_compared"]+=1
                counts["stage_original_roundtrip_io_equal"]+=(
                    all(sorted(x[side], key=lambda row: row["location"]) ==
                        sorted(y[side], key=lambda row: row["location"])
                        for side in ("inputs", "outputs")))
                counts["stage_original_roundtrip_resource_slot_shapes_equal"]+=(
                    x["resource_slots"]==y["resource_slots"])
                # Use only the previously validated, anonymous stage I/O
                # classifier. No original/translated semantics, names or
                # per-stage private locations leave the temporary runner.
                classified=io_classifier(x,y)
                expected={side+"_"+key for side in ("inputs","outputs")
                          for key in IO_KEYS}
                if type(classified) is not dict or set(classified)!=expected:
                    raise ValueError("untrusted_private_stage_IO_drift_classifier_shape")
                counts["stage_original_roundtrip_io_drift_classified"]+=1
                for field,amount in classified.items():
                    suffix=field.split("_",1)[1]
                    cap=1 if suffix in IO_BOOLEAN else 256
                    if type(amount) is not int or not 0<=amount<=cap:
                        raise ValueError("untrusted_private_stage_IO_drift_numeric_count")
                    counts["io_drift_"+field]+=amount
            stages[stage]={"flags":t,"reflections":reflections}
        v,f=stages[1],stages[0]
        for field,name in (("original","source"),("roundtrip","roundtrip")):
            if field in v["reflections"] and field in f["reflections"]:
                counts[name+"_vs_fs_interfaces_compared"]+=1
                counts[name+"_vs_fs_interfaces_compatible"]+=bool(
                    pair_checker(v["reflections"][field],f["reflections"][field]))
        if v["flags"]["vulkan11_valid"] and f["flags"]["vulkan11_valid"]:
            counts["pairs_with_both_source_stages_spirv_vulkan11_valid"]+=1
        if (v["flags"]["roundtrip_vulkan11_valid"] and
            f["flags"]["roundtrip_vulkan11_valid"]):
            counts["pairs_with_both_roundtrip_stages_spirv_vulkan11_valid"]+=1
    safe_keys=(
        "stage_translation_attempts","source_stage_spirv_vulkan11_valid",
        "stage_hlsl_recovered","stage_hlsl_roundtrip_spirv_vulkan11_valid",
        "original_stage_reflections","original_stage_reflection_failures",
        "roundtrip_stage_reflections","roundtrip_stage_reflection_failures",
        "stage_original_roundtrip_reflection_pairs_compared",
        "stage_original_roundtrip_io_equal",
        "stage_original_roundtrip_io_drift_classified",
        "stage_original_roundtrip_resource_slot_shapes_equal",
        "source_vs_fs_interfaces_compared","source_vs_fs_interfaces_compatible",
        "roundtrip_vs_fs_interfaces_compared","roundtrip_vs_fs_interfaces_compatible",
        "pairs_with_both_source_stages_spirv_vulkan11_valid",
        "pairs_with_both_roundtrip_stages_spirv_vulkan11_valid")
    # Source/roundtrip I/O summaries are public count-only; no reflected
    # per-program interface values are returned.
    safe_keys += tuple("io_drift_"+side+"_"+key for side in ("inputs","outputs")
                       for key in IO_KEYS)
    if counts["stage_translation_attempts"]!=PAIRS*STAGES:
        raise ValueError("incomplete_fourpair_private_translation_attempts")
    return {"schema_version":1,"status":STATUS,
            "source_original_particle108_shader_use_slots":108,
            "source_original_particle_renderers":54,
            "source_original_Shader48_SubShader_count":1,
            "source_original_Shader48_normal_Pass_count":1,
            "original_D3D11_table_records":SHADER_TABLE_RECORDS,
            "original_exact_vertex_fragment_keyword_pairs":PAIRS,
            "original_paired_D3D11_stage_programs":PAIRS*STAGES,
            "counts":{k:int(counts[k]) for k in safe_keys},
            "all_original_four_keyword_pairs_translation_attempted":True,
            "private_game_shader_program_bytes_names_hashes_or_Guids_published":False,
            "source_shader_is_users_phone_fire_smoke_emitter_verified":False,
            "full_Unity_HLSL_ShaderLab_original_semantics_verified":False,
            "native_Unity_Android_Adreno_pixels_verified":False,
            "source_game_assets_modified":False}


def probe(original:Path,manifest:Path,*,translator=translate,
          reflector=reflection,pair_checker=interfaces_match):
    for binary in TOOLS:
        if shutil.which(binary) is None:
            raise ValueError("required_pinned_runner_DXBC_translation_tool_missing")
    private={}
    report=source.source.load_original(original,manifest,
                                       private_particle_slot_counts=private)
    owner,pid=source.select(private,report)
    path=original/"Raft_Data"/owner
    if (any(p.is_symlink() for p in (path,*path.parents))
        or fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("original_particle108_SHA_Shader_owner_drift")
    import UnityPy
    objs=[o for o in UnityPy.load(str(path)).file.objects.values()
          if o.path_id==pid]
    if len(objs)!=1 or objs[0].type.name!="Shader":
        raise ValueError("original_particle108_Shader48_type_or_identity_drift")
    tree=objs[0].read_typetree()
    tables=[records(segments) for platform,segments in decoded_platforms(tree)
            if platform==4]
    if len(tables)!=1:
        raise ValueError("one_real_original_D3D11_platform_required")
    parsed=tree.get("m_ParsedForm")
    baseline=source.inspect(parsed,tables[0])
    if (baseline.get("status")!=source.STATUS or
        baseline.get("original_D3D11_program_table_records")!=SHADER_TABLE_RECORDS or
        baseline.get("genuine_D3D11_vertex_stage_variant_records")!=PAIRS or
        baseline.get("genuine_D3D11_fragment_stage_variant_records")!=PAIRS or
        baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS or
        baseline.get("unmatched_vertex_permutations")!=0 or
        baseline.get("unmatched_fragment_permutations")!=0 or
        baseline.get("original_all_compiled_vertex_fragment_stages_available") is not True):
        raise ValueError("original_particle108_D3D11_fourpair_baseline_changed")
    pairs=exact_four_pairs(parsed,tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-particle108-private-vulkan-") as temp:
        result=evaluate(pairs,Path(temp),translator=translator,
                        reflector=reflector,pair_checker=pair_checker)
    result["six_original_source_scenes_SHA_verified"]=True
    result["four_original_Shader_Material_owners_SHA_verified"]=True
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_public_original_Particle108_SPIRV_report")
    try:
        r=probe(a.original,a.manifest)
    except Exception as error:
        r={"schema_version":1,"status":"INCONCLUSIVE",
           "failure_type":type(error).__name__,
           "private_game_shader_program_bytes_names_hashes_or_Guids_published":False,
           "native_Unity_Android_Adreno_pixels_verified":False,
           "source_game_assets_modified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_ORIGINAL_SPIRV_TRANSLATION "+json.dumps(r,sort_keys=True))
    return 0 if r["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
