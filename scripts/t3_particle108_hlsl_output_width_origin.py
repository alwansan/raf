#!/usr/bin/env python3
"""Private source-authentic Particle108 SPIR-V -> generated HLSL -> roundtrip SPIR-V width-shape origin.

Only aggregate counters leave the CI process. Generated HLSL, original
semantics, per-stage reflection names, source bytes and Location values
remain ephemeral. An equal type multiset is NEVER semantic/field identity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from scripts import t3_original_particle108_spirv_translation as base
from scripts.t3_particle108_roundtrip_interface_diagnostic import PAIRS, _stage
from scripts.w1_recover_depth_passes import reflection, interfaces_match
from scripts.w1_recover_graphics_programs import translate

STATUS="T3_ORIGINAL_PARTICLE108_PRIVATE_HLSL_VERTEX_OUTPUT_TYPE_ORIGIN"
MAX_HLSL=1024*1024
IDENT=r"[A-Za-z_][A-Za-z_0-9]*"
OUTPUT_STRUCT=re.compile(r"\bstruct\s+SPIRV_Cross_Output\s*\{([^{}]*)\}\s*;",re.S)
OUTPUT_FIELD=re.compile(
    rf"^\s*(?:(?:nointerpolation|linear|centroid|sample|noperspective)\s+)*"
    rf"({IDENT})\s+({IDENT})\s*:\s*({IDENT})\s*$")
VECTOR_TYPE=re.compile(r"^(float|int|uint)([1-4]?)$")
SPIRV_VECTOR_TYPE=re.compile(r"^(vec|ivec|uvec)([2-4])$")
COUNTERS=(
    "vertex_variants_checked","source_vertex_output_records","roundtrip_vertex_output_records",
    "generated_hlsl_output_struct_found","generated_hlsl_output_struct_not_found",
    "generated_hlsl_output_user_fields","generated_hlsl_output_builtin_fields",
    "generated_hlsl_output_unparsed_fields","generated_hlsl_output_unsupported_user_types",
    "generated_hlsl_output_user_field_total_equals_source",
    "hlsl_user_output_type_multiset_equals_source",
    "hlsl_user_output_type_multiset_equals_roundtrip",
    "source_output_type_multiset_equals_roundtrip",
    "hlsl_user_output_type_multiset_differs_source",
    "hlsl_user_output_type_multiset_differs_roundtrip",
    "source_named_output_records","source_output_names_unique",
    "hlsl_user_output_field_names_unique",
    "source_to_hlsl_exact_name_matches",
    "source_to_hlsl_exact_name_type_equal",
    "source_to_hlsl_exact_name_type_narrowing",
    "source_to_hlsl_exact_name_type_widening",
    "source_to_hlsl_exact_name_type_other",
    "original_vs_fs_pairs_linked","roundtrip_vs_fs_pairs_linked",
)
def _normalized_spirv(kind):
    if type(kind) is not str or len(kind)>90:
        return None
    if kind in ("float","int","uint"):
        return (kind,1)
    m=SPIRV_VECTOR_TYPE.fullmatch(kind)
    return (({"vec":"float","ivec":"int","uvec":"uint"}[m.group(1)],int(m.group(2)))
            if m else None)

def _normalized_hlsl(kind):
    if type(kind) is not str or len(kind)>90:
        return None
    m=VECTOR_TYPE.fullmatch(kind)
    return (m.group(1),int(m.group(2) or "1")) if m else None

def extract_output_struct(hlsl):
    """Private strict structural extractor. Names and semantics MUST NOT be returned in public report."""
    if type(hlsl) is not str or not 0<len(hlsl.encode("utf-8"))<=MAX_HLSL:
        raise ValueError("invalid_private_generated_hlsl_scope")
    blocks=OUTPUT_STRUCT.findall(hlsl)
    if len(blocks)!=1:
        return None
    fields=[]
    for raw in blocks[0].split(";"):
        if not raw.strip():
            continue
        m=OUTPUT_FIELD.fullmatch(raw)
        if not m:
            fields.append({"name":None,"semantic":None,"type":None})
            continue
        hlsl_type,name,semantic=m.groups()
        fields.append({"name":name,"semantic":semantic,"type":_normalized_hlsl(hlsl_type)})
    if len(fields)>256:
        raise ValueError("unbounded_generated_output_fields")
    return fields

def classify(source,roundtrip,raw_source,fields):
    """Accept only in-process private data, return only allow-listed counts."""
    original=_stage(source)
    rebuilt=_stage(roundtrip)
    if type(raw_source) is not dict or type(raw_source.get("outputs")) is not list:
        raise ValueError("invalid_private_named_source_reflection")
    original_map={x["location"]:x["type"] for x in original["outputs"]}
    round_map={x["location"]:x["type"] for x in rebuilt["outputs"]}
    orig_shapes=Counter(_normalized_spirv(t) for t in original_map.values())
    rt_shapes=Counter(_normalized_spirv(t) for t in round_map.values())
    if None in orig_shapes or None in rt_shapes:
        raise ValueError("unsupported_original_or_roundtrip_SPIRV_output_type")
    counts=Counter({
        "vertex_variants_checked":1,
        "source_vertex_output_records":len(original_map),
        "roundtrip_vertex_output_records":len(round_map),
        "source_output_type_multiset_equals_roundtrip":int(orig_shapes==rt_shapes),
    })
    raw_names={}
    for row in raw_source["outputs"]:
        if (type(row) is not dict or type(row.get("location")) is not int or
            type(row.get("type")) is not str):
            raise ValueError("invalid_private_reflected_output_row")
        loc=row["location"]
        if loc not in original_map or original_map[loc]!=row["type"]:
            raise ValueError("unverified_named_source_location_type")
        name=row.get("name")
        if type(name) is str and name:
            if len(name)>256:
                raise ValueError("unbounded_private_reflected_name")
            counts["source_named_output_records"]+=1
            if name in raw_names:
                raise ValueError("duplicate_original_output_reflection_name")
            raw_names[name]=_normalized_spirv(row["type"])
    counts["source_output_names_unique"]=int(len(raw_names)==len(original_map))
    if fields is None:
        counts["generated_hlsl_output_struct_not_found"]+=1
        return {k:int(counts[k]) for k in COUNTERS}
    counts["generated_hlsl_output_struct_found"]+=1
    hlsl_names={}
    kinds=[]
    for field in fields:
        if type(field) is not dict or set(field)!={"name","semantic","type"}:
            raise ValueError("untrusted_private_hlsl_field_shape")
        name,semantic,kind=field["name"],field["semantic"],field["type"]
        if name is None or semantic is None:
            counts["generated_hlsl_output_unparsed_fields"]+=1
            continue
        if type(name) is not str or type(semantic) is not str or len(name)>256 or len(semantic)>256:
            raise ValueError("unbounded_private_hlsl_field_identity")
        # SPIR-V reflection excludes built-in outputs. HLSL SV_* and PSIZE are not
        # original user varyings; retain only counts.
        if semantic.upper().startswith("SV_") or semantic.upper()=="PSIZE":
            counts["generated_hlsl_output_builtin_fields"]+=1
            continue
        if name in hlsl_names:
            raise ValueError("duplicate_private_HLSL_output_field")
        hlsl_names[name]=kind
        counts["generated_hlsl_output_user_fields"]+=1
        if kind is None:
            counts["generated_hlsl_output_unsupported_user_types"]+=1
        else:
            kinds.append(kind)
    counts["hlsl_user_output_field_names_unique"]=1
    counts["generated_hlsl_output_user_field_total_equals_source"]=int(
        len(hlsl_names)==len(original_map))
    if not counts["generated_hlsl_output_unparsed_fields"] and not counts["generated_hlsl_output_unsupported_user_types"]:
        hm=Counter(kinds)
        counts["hlsl_user_output_type_multiset_equals_source"]=int(hm==orig_shapes)
        counts["hlsl_user_output_type_multiset_equals_roundtrip"]=int(hm==rt_shapes)
        counts["hlsl_user_output_type_multiset_differs_source"]=int(hm!=orig_shapes)
        counts["hlsl_user_output_type_multiset_differs_roundtrip"]=int(hm!=rt_shapes)
    for name,shape in hlsl_names.items():
        if name not in raw_names:
            continue
        counts["source_to_hlsl_exact_name_matches"]+=1
        original_shape=raw_names[name]
        if shape is None or original_shape is None:
            counts["source_to_hlsl_exact_name_type_other"]+=1
        elif original_shape==shape:
            counts["source_to_hlsl_exact_name_type_equal"]+=1
        elif original_shape[0]==shape[0] and original_shape[1]>shape[1]:
            counts["source_to_hlsl_exact_name_type_narrowing"]+=1
        elif original_shape[0]==shape[0] and original_shape[1]<shape[1]:
            counts["source_to_hlsl_exact_name_type_widening"]+=1
        else:
            counts["source_to_hlsl_exact_name_type_other"]+=1
    return {k:int(counts[k]) for k in COUNTERS}

def raw_reflection_private(path):
    proc=subprocess.run(["spirv-cross",str(path),"--reflect"],capture_output=True,timeout=30)
    if proc.returncode or len(proc.stdout)>MAX_HLSL:
        raise ValueError("private_named_source_SPIRV_reflection_failed")
    return json.loads(proc.stdout)

def evaluate(pairs,workspace,*,translator=translate,reflector=reflection,
             raw_reader=raw_reflection_private):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(code) is not bytes or not 0<len(code)<=4*1024*1024
                for code in pair) for pair in pairs) or
        not isinstance(workspace,Path) or not workspace.is_dir() or workspace.is_symlink()):
        raise ValueError("invalid_original_fourpairs_for_hlsl_width_probe")
    totals=Counter()
    for index,pair in enumerate(pairs):
        stages={}
        for stage,code in ((1,pair[0]),(0,pair[1])):
            folder=workspace/f"variant-{index}-stage-{stage}"
            folder.mkdir(exist_ok=False)
            flags=translator(code,stage,folder)
            if type(flags) is not dict or any(flags.get(k) is not True for k in
                ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")):
                raise ValueError("private_translation_stage_incomplete")
            original=_stage(reflector(folder/"original.spv"))
            roundtrip=_stage(reflector(folder/"roundtrip.spv"))
            stages[stage]=(original,roundtrip)
            if stage==1:
                hlsl_file=folder/"private.hlsl"
                if (hlsl_file.is_symlink() or not hlsl_file.is_file() or
                    not 0<hlsl_file.stat().st_size<=MAX_HLSL):
                    raise ValueError("missing_or_oversized_private_hlsl")
                fields=extract_output_struct(hlsl_file.read_text())
                row=classify(original,roundtrip,raw_reader(folder/"original.spv"),fields)
                for k in COUNTERS: totals[k]+=row[k]
        totals["original_vs_fs_pairs_linked"]+=int(interfaces_match(stages[1][0],stages[0][0]))
        totals["roundtrip_vs_fs_pairs_linked"]+=int(interfaces_match(stages[1][1],stages[0][1]))
    if totals["vertex_variants_checked"]!=PAIRS or totals["original_vs_fs_pairs_linked"]!=PAIRS:
        raise ValueError("authentic_private_stage_link_baseline_drift")
    return {
        "schema_version":1,"status":STATUS,"original_keyword_pairs":PAIRS,
        "counts":{k:int(totals[k]) for k in COUNTERS},
        "source_original_game_assets_modified":False,
        "source_semantic_to_HLSL_field_identity_proven":False,
        "HLSL_type_multiset_equivalence_proves_field_identity":False,
        "native_Android_Adreno_pixels_verified":False,
        "private_names_HLSL_and_programs_published":False,
    }

def probe(original,manifest):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    from scripts import t3_particle108_roundtrip_interface_diagnostic as prior
    for tool in base.TOOLS:
        if shutil.which(tool) is None:
            raise ValueError("required_translation_tool_missing")
    selection={}
    source_report=base.source.source.load_original(original,manifest,private_particle_slot_counts=selection)
    owner,pid=base.source.select(selection,source_report)
    path=original/"Raft_Data"/owner
    if any(p.is_symlink() for p in (path,*path.parents)) or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("original_private_particle_owner_SHA_mismatch")
    matched=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(matched)!=1 or matched[0].type.name!="Shader":
        raise ValueError("original_private_shader_id_ambiguous")
    parsed=matched[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(parsed) if platform==4]
    if len(tables)!=1:
        raise ValueError("original_private_D3D11_program_table_ambiguous")
    baseline=base.source.inspect(parsed["m_ParsedForm"],tables[0])
    if baseline.get("status")!=base.source.STATUS or baseline.get("original_D3D11_program_table_records")!=16 or baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS:
        raise ValueError("original_four_Particle_pairs_identity_drift")
    pairs=base.exact_four_pairs(parsed["m_ParsedForm"],tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-particle108-private-hlsl-width-origin-") as temporary:
        report=evaluate(pairs,Path(temporary))
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
        raise ValueError("unsafe_private_hlsl_report_output_path")
    try:
        report=probe(args.original,args.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "private_names_HLSL_and_programs_published":False,
                "native_Android_Adreno_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_HLSL_TYPE_ORIGIN_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report.get("status")==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
