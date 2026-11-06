#!/usr/bin/env python3
"""T3 private four-pair original DXBC-register vs source SPIR-V Location test.

A numerical register/Location match is NEVER proof of semantic identity or
pixel parity. Original bytes, names, identifiers, locations and reflections
remain private; only allow-listed aggregate counts leave the runner.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import tempfile

PAIRS=4
STATUS="ORIGINAL_PARTICLE108_DXBC_REGISTER_VS_SOURCE_SPIRV_NUMERIC_LOCATION_CLASSIFIED"
KEYS=("original_user_records","original_unique_registers",
      "original_records_sharing_register","spirv_located_rows",
      "spirv_unlocated_rows","numerically_matching_register_records",
      "missing_numeric_register_locations","type_class_matches",
      "type_class_mismatches","unsupported_spirv_type_class",
      "component_width_shortfalls","extra_spirv_locations",
      "unique_numeric_type_width_candidates",
      "all_user_records_unique_numeric_candidates")

def _type(value):
    if type(value) is not str or len(value)>24:
        raise ValueError("invalid_private_SPIRV_type")
    m=re.fullmatch(r"(?:(?P<prefix>[iu])?vec(?P<width>[234])|(?P<scalar>float|int|uint))",value)
    if not m: return None
    if m["scalar"]:
        return {"float":(3,1),"int":(2,1),"uint":(1,1)}[m["scalar"]]
    return ({None:3,"i":2,"u":1}[m["prefix"]],int(m["width"]))

def classify_stage(original,reflected):
    """Inspect private rows, but return ONLY non-identifying aggregate integers."""
    if type(original) is not dict or type(reflected) is not dict:
        raise ValueError("invalid_original_or_reflection_root")
    out=Counter()
    for side,spvside in (("input","inputs"),("output","outputs")):
        rows,spv=original.get(side),reflected.get(spvside,[])
        if (type(rows) is not list or type(spv) is not list or
            len(rows)>256 or len(spv)>256):
            raise ValueError("unbounded_private_stage_rows")
        users=[]
        for row in rows:
            if (type(row) is not dict or any(type(row.get(k)) is not int
                for k in ("register","mask","type","system_value")) or
                not (0<=row["register"]<=4095 or
                     (row["system_value"]!=0 and row["register"]==0xffffffff)) or
                not 1<=row["mask"]<=15 or row["type"] not in (1,2,3) or
                not 0<=row["system_value"]<=64):
                raise ValueError("untrusted_private_original_DXBC_record")
            if row["system_value"]==0: users.append(row)
        locations={}; unlocated=0
        for row in spv:
            if type(row) is not dict:
                raise ValueError("untrusted_private_SPIRV_row")
            if "location" not in row:
                unlocated+=1;continue
            loc=row["location"]
            if (type(loc) is not int or not 0<=loc<=65535 or
                loc in locations or type(row.get("type")) is not str):
                raise ValueError("invalid_or_duplicate_SPIRV_location")
            locations[loc]=_type(row["type"])
        registers=Counter(r["register"] for r in users)
        out["original_user_records"]+=len(users)
        out["original_unique_registers"]+=len(registers)
        out["original_records_sharing_register"]+=sum(n for n in registers.values() if n>1)
        out["spirv_located_rows"]+=len(locations)
        out["spirv_unlocated_rows"]+=unlocated
        out["extra_spirv_locations"]+=len(set(locations)-set(registers))
        for row in users:
            reg=row["register"]
            if reg not in locations:
                out["missing_numeric_register_locations"]+=1
                continue
            out["numerically_matching_register_records"]+=1
            got=locations[reg]
            if got is None:
                out["unsupported_spirv_type_class"]+=1
                continue
            kind,width=got
            if kind!=row["type"]:
                out["type_class_mismatches"]+=1
                continue
            out["type_class_matches"]+=1
            # A lane count match is not proof of original xyzw component mapping.
            if row["mask"].bit_count()>width:
                out["component_width_shortfalls"]+=1
                continue
            if registers[reg]==1:
                out["unique_numeric_type_width_candidates"]+=1
    out["all_user_records_unique_numeric_candidates"]=int(
        out["original_user_records"]>0 and
        out["unique_numeric_type_width_candidates"]==out["original_user_records"])
    return {key:int(out[key]) for key in KEYS}

def classify_stage_roles(original,reflected):
    """Four-variant aggregate caller; never return original semantic/location IDs."""
    if type(original) is not dict or type(reflected) is not dict:
        raise ValueError("invalid_private_stage_role_scope")
    result={}
    for name,plural,other,other_plural in (
        ("inputs","inputs","output","outputs"),
        ("outputs","outputs","input","inputs")):
        sig={"input":[],"output":[]}
        raw={"inputs":[],"outputs":[]}
        sig["input" if name=="inputs" else "output"]=original.get(
            "input" if name=="inputs" else "output")
        raw[plural]=reflected.get(plural,[])
        result[name]=classify_stage(sig,raw)
    return result

def classify_missing_fragment_usedmask(vertex,fragment,raw_fragment_spirv):
    """Classify absent *numeric* Fragment input Locations by private DXBC used_mask.

    Read masks are compiled signature metadata, not pixel/semantic proof.
    Return only bounded class counts, NEVER individual names, IDs or Locations.
    """
    if (type(vertex) is not dict or type(fragment) is not dict or
        type(raw_fragment_spirv) is not dict or
        type(vertex.get("output")) is not list or
        type(fragment.get("input")) is not list or
        type(raw_fragment_spirv.get("inputs",[])) is not list or
        max(len(vertex["output"]),len(fragment["input"]),
            len(raw_fragment_spirv.get("inputs",[])))>256):
        raise ValueError("untrusted_fragment_missing_usedmask_scope")
    located=set()
    for row in raw_fragment_spirv.get("inputs",[]):
        if type(row) is not dict:
            raise ValueError("untrusted_private_fragment_reflection")
        if "location" in row:
            loc=row["location"]
            if type(loc) is not int or not 0<=loc<=65535 or loc in located:
                raise ValueError("untrusted_or_duplicate_fragment_SPIRV_location")
            located.add(loc)
    upstream={}
    for row in vertex["output"]:
        if type(row) is not dict:
            raise ValueError("invalid_private_vertex_semantic")
        if row.get("system_value")==0:
            key=(row.get("semantic"),row.get("index"))
            if (type(key[0]) is not str or type(key[1]) is not int or
                key in upstream):
                raise ValueError("invalid_or_duplicate_private_vertex_semantic")
            upstream[key]=row
    out=Counter()
    for row in fragment["input"]:
        if type(row) is not dict:
            raise ValueError("invalid_private_fragment_signature")
        if row.get("system_value")!=0:
            continue
        reg,mask,read_mask=row.get("register"),row.get("mask"),row.get("used_mask")
        if (type(reg) is not int or not 0<=reg<=4095 or
            type(mask) is not int or not 1<=mask<=15 or
            type(read_mask) is not int or not 0<=read_mask<=15 or
            type(row.get("semantic")) is not str or
            type(row.get("index")) is not int):
            raise ValueError("invalid_original_fragment_DXBC_used_mask")
        if reg in located:
            continue
        out["missing_fragment_numeric_location_records"]+=1
        if read_mask==0:
            out["missing_fragment_original_used_mask_zero"]+=1
        else:
            out["missing_fragment_original_used_mask_nonzero"]+=1
            out["missing_fragment_original_used_mask_lanes"]+=read_mask.bit_count()
        out["missing_fragment_used_mask_outside_declared_mask"]+=int(
            bool(read_mask & ~mask))
        src=upstream.get((row["semantic"],row["index"]))
        compatible=(src is not None and src.get("system_value")==0 and
                    type(src.get("mask")) is int and
                    type(src.get("type")) is int and
                    src["type"]==row.get("type") and
                    (mask & ~src["mask"])==0)
        out["missing_fragment_original_vertex_semantic_mask_type_join"]+=int(compatible)
    return {key:int(out[key]) for key in (
        "missing_fragment_numeric_location_records",
        "missing_fragment_original_used_mask_zero",
        "missing_fragment_original_used_mask_nonzero",
        "missing_fragment_original_used_mask_lanes",
        "missing_fragment_used_mask_outside_declared_mask",
        "missing_fragment_original_vertex_semantic_mask_type_join")}

def evaluate(pairs,workspace,*,translator=None,dxbc_reader=None,
             spirv_reader=None,safe_spirv_reader=None,reflection_validator=None):
    from scripts import t3_original_particle108_spirv_translation as tr
    from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures
    from scripts.t3_spirv_interface_name_drift import read_reflection
    from scripts.w1_recover_graphics_programs import translate
    from scripts.w1_recover_depth_passes import reflection
    translator=translator or translate
    dxbc_reader=dxbc_reader or read_original_dxbc_signatures
    spirv_reader=spirv_reader or read_reflection
    safe_spirv_reader=safe_spirv_reader or reflection
    reflection_validator=reflection_validator or tr._validate_reflection
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(code) is not bytes or not 0<len(code)<=4*1024*1024
                for code in pair) for pair in pairs) or
        not isinstance(workspace,Path) or not workspace.is_dir()
        or workspace.is_symlink()):
        raise ValueError("untrusted_original_fourpair_private_scope")
    total=Counter(); complete=0
    role_counts={k:Counter() for k in ('vertex_inputs','vertex_outputs','fragment_inputs','fragment_outputs')}
    fragment_used_mask_totals=Counter()
    for i,pair in enumerate(pairs):
        source_by_stage={1:dxbc_reader(pair[0]),0:dxbc_reader(pair[1])}
        stage_ok=0
        for stage,code in ((1,pair[0]),(0,pair[1])):
            folder=workspace/f"pair-{i}-stage-{stage}"
            folder.mkdir(exist_ok=False)
            report=translator(code,stage,folder)
            if type(report) is not dict or report.get("vulkan11_valid") is not True:
                raise ValueError("source_original_SPIRV_translation_failed")
            file=folder/"original.spv"
            safe=reflection_validator(safe_spirv_reader(file))
            raw=spirv_reader(file)
            if type(raw) is not dict: raise ValueError("invalid_private_SPIRV_reflection")
            for side in ("inputs","outputs"):
                entries=raw.get(side,[])
                if type(entries) is not list or len(entries)>256 or any(
                    type(e) is not dict for e in entries):
                    raise ValueError("untrusted_private_reflection_entries")
                projected=sorted(({"location":r["location"],"type":r["type"]}
                                  for r in entries if "location" in r),
                                 key=lambda x:x["location"])
                if projected!=safe[side]:
                    raise ValueError("original_private_SPIRV_safe_reflection_disagrees")
            source_signature=source_by_stage[stage]
            if stage==0:
                missing=classify_missing_fragment_usedmask(
                    source_by_stage[1],source_by_stage[0],raw)
                for k,v in missing.items():
                    fragment_used_mask_totals[k]+=v
            row=classify_stage(source_signature,raw)
            scoped=classify_stage_roles(source_signature,raw)
            phase='vertex' if stage==1 else 'fragment'
            for side,values in scoped.items():
                slot=role_counts[phase+'_'+side]
                for key in ('original_user_records','spirv_located_rows',
                            'missing_numeric_register_locations',
                            'numerically_matching_register_records',
                            'type_class_mismatches',
                            'component_width_shortfalls',
                            'extra_spirv_locations'):
                    slot[key]+=values[key]
            for key in KEYS: total[key]+=row[key]
            total["original_DXBC_to_SPIRV_stages"]+=1
            stage_ok+=int(row["all_user_records_unique_numeric_candidates"]==1)
        complete+=int(stage_ok==2)
    total["original_four_VSFS_keyword_pairs"]=PAIRS
    total["four_pairs_with_numerical_unique_register_location_candidates"]=complete
    return {"schema_version":1,"status":STATUS,
            "counts":{k:int(total[k]) for k in (*KEYS,
                "original_DXBC_to_SPIRV_stages",
                "original_four_VSFS_keyword_pairs",
                "four_pairs_with_numerical_unique_register_location_candidates")},
            "missing_fragment_usedmask_aggregate":{
                k:int(fragment_used_mask_totals[k]) for k in (
                    "missing_fragment_numeric_location_records",
                    "missing_fragment_original_used_mask_zero",
                    "missing_fragment_original_used_mask_nonzero",
                    "missing_fragment_original_used_mask_lanes",
                    "missing_fragment_used_mask_outside_declared_mask",
                    "missing_fragment_original_vertex_semantic_mask_type_join")},
            "stage_role_aggregate_counts":{
                role:{key:int(values[key]) for key in (
                    'original_user_records','spirv_located_rows',
                    'missing_numeric_register_locations',
                    'numerically_matching_register_records',
                    'type_class_mismatches','component_width_shortfalls',
                    'extra_spirv_locations')}
                for role,values in sorted(role_counts.items())},
            "source_SPIRV_Location_equals_DXBC_register_semantic_identity_proven":False,
            "authored_semantic_to_HLSL_variable_mapping_proven":False,
            "auto_location_patch_authorized":False,
            "private_original_names_IDs_bytes_hashes_or_varying_Locations_published":False,
            "Android_Adreno_pixels_verified":False}

def probe(original,manifest):
    from scripts import t3_original_particle108_spirv_translation as tr
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    from scripts.w1_stage_zip2_owners import fingerprint
    import UnityPy
    scope={}
    report=tr.source.source.load_original(
        original,manifest,private_particle_slot_counts=scope)
    owner,pid=tr.source.select(scope,report)
    path=original/"Raft_Data"/owner
    if (any(p.is_symlink() for p in (path,*path.parents)) or
        fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("original_Shader_owner_sha_drift")
    objs=[o for o in UnityPy.load(str(path)).file.objects.values()
          if o.path_id==pid]
    if len(objs)!=1 or objs[0].type.name!="Shader":
        raise ValueError("original_Shader_identity_drift")
    tree=objs[0].read_typetree()
    tables=[records(segments) for p,segments in decoded_platforms(tree) if p==4]
    if len(tables)!=1: raise ValueError("original_D3D11_platform_ambiguous")
    baseline=tr.source.inspect(tree["m_ParsedForm"],tables[0])
    if (baseline.get("status")!=tr.source.STATUS or
        baseline.get("original_D3D11_program_table_records")!=16 or
        baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS):
        raise ValueError("source_four_stage_pair_baseline_drift")
    pairs=tr.exact_four_pairs(tree["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-dxbc-location-") as d:
        result=evaluate(pairs,Path(d))
    result["original_six_scene_SHA_verified"]=True
    result["original_four_owner_SHA_verified"]=True
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("original","manifest","out"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_location_report_path")
    try: result=probe(a.original,a.manifest)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "private_original_names_IDs_bytes_hashes_or_varying_Locations_published":False,
                "Android_Adreno_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_PRIVATE_LOCATION_NUMERIC_HYPOTHESIS "+
          json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
