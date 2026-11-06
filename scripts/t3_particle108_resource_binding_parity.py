#!/usr/bin/env python3
"""T3 SHA-original Particle108 four keyword pairs private SPIR-V resource parity.

Genuine VS/FS DXBC sources are selected by six-scene Material->Shader PPtrs.
Original SPIR-V versus SPIRV-Cross HLSL/glslang roundtrip descriptor classes
are checked anonymously. Never publish original resource names, slot numbers,
HLSL, bytecode, source-path identities or per-stage private manifests.
This is NOT a new shader, Unity compile, or Android GPU pixel proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_particle108_spirv_translation as original
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import reflection, interfaces_match

STATUS="T3_SHA_ORIGINAL_PARTICLE108_FOURPAIR_RESOURCE_SLOT_CLASSIFIED"
PAIR_COUNT=4
CATEGORIES=("ubos","ssbos","textures","separate_images","separate_samplers","images")
MAX_BINDINGS=128
MAX_SLOT_ID=4095
SAFE_FAILURE_CATEGORIES=frozenset((
    "SOURCE_AUTHENTICATION", "ORIGINAL_SHADER_PROPERTY_SCHEMA",
    "ORIGINAL_COMPILED_KEYWORD_PAIRS", "SOURCE_STAGE_TRANSLATION",
    "STAGE_SPIRV_REFLECTION", "DESCRIPTOR_SET_OR_BINDING_UNLOCATED",
    "DESCRIPTOR_ALIAS_OR_DUPLICATE", "RESOURCE_CATEGORY_UNSUPPORTED",
    "STAGE_SPIRV_IO_INCOMPATIBLE", "STAGE_REFLECTION_SCHEMA_REJECTED",
    "STAGE_DESCRIPTOR_SCHEMA_OTHER",
))
class PrivateReasonError(ValueError):
    def __init__(self,reason):
        if reason not in SAFE_FAILURE_CATEGORIES:
            raise ValueError("untrusted_original_descriptor_failure_category")
        self.reason=reason
        super().__init__("original_resource_descriptor_"+reason)


def canonical_resources(reflected):
    """Strongly type check shader descriptor resources, stay source-private."""
    data=original._validate_reflection(reflected)
    resources=data["resource_slots"]
    if any(k not in CATEGORIES for k in resources):
        raise ValueError("unhandled_private_SPIRV_resource_category")
    result={}
    for category in CATEGORIES:
        raw=resources.get(category,[])
        if type(raw) is not list or len(raw)>MAX_BINDINGS:
            raise ValueError("unbounded_private_SPIRV_descriptor_category")
        rows=[]
        for item in raw:
            if (type(item) is not list or len(item)!=2 or
                any(type(x) is not int or not 0<=x<=MAX_SLOT_ID for x in item)):
                raise ValueError("unlocated_or_malformed_private_resource_descriptor")
            rows.append(tuple(item))
        if len(set(rows))!=len(rows):
            raise ValueError("duplicate_private_stage_resource_binding")
        result[category]=frozenset(rows)
    return result


def classify_stages(stages):
    """4 pairs * 2 stages * 2 reflections in; safe aggregate counts out."""
    if (type(stages) is not list or len(stages)!=PAIR_COUNT or
        any(type(pair) is not dict or set(pair)!={0,1} for pair in stages)):
        raise ValueError("invalid_original_particle108_four_pair_scope")
    totals=Counter()
    source_manifest={1:[],0:[]}
    roundtrip_manifest={1:[],0:[]}
    pair_source_shapes=[]
    pair_roundtrip_shapes=[]
    for pair in stages:
        parsed={}
        for stage in (1,0):
            variants=pair[stage]
            if type(variants) is not dict or set(variants)!={"source","roundtrip"}:
                raise ValueError("incomplete_original_and_roundtrip_stage_reflections")
            x=original._validate_reflection(variants["source"])
            y=original._validate_reflection(variants["roundtrip"])
            a,b=canonical_resources(x),canonical_resources(y)
            source_manifest[stage].append(a)
            roundtrip_manifest[stage].append(b)
            totals["source_stage_reflections"]+=1
            totals["roundtrip_stage_reflections"]+=1
            same=(a==b)
            totals["stage_full_resource_slot_parity"]+=int(same)
            totals["stage_descriptor_slot_drift"]+=int(not same)
            for category in CATEGORIES:
                missing=a[category]-b[category]
                added=b[category]-a[category]
                totals["source_"+category+"_entries"]+=len(a[category])
                totals["roundtrip_"+category+"_entries"]+=len(b[category])
                totals["removed_descriptor_entries"]+=len(missing)
                totals["added_descriptor_entries"]+=len(added)
                totals["descriptor_categories_with_count_drift"]+=int(
                    len(a[category])!=len(b[category]))
                totals["descriptor_categories_with_slot_drift"]+=int(
                    a[category]!=b[category])
        vert,frag=pair[1],pair[0]
        if not interfaces_match(vert["source"],frag["source"]):
            raise ValueError("original_source_SPIRV_stage_IO_not_compatible")
        totals["source_VSFS_keyword_pairs_linked"]+=1
        totals["roundtrip_VSFS_keyword_pairs_linked"]+=int(
            interfaces_match(vert["roundtrip"],frag["roundtrip"]))
        pair_source_shapes.append((source_manifest[1][-1],source_manifest[0][-1]))
        pair_roundtrip_shapes.append((roundtrip_manifest[1][-1],roundtrip_manifest[0][-1]))
    for stage in (1,0):
        totals["source_"+("vertex" if stage else "fragment")+
               "_binding_layout_stable_across_four_keywords"]=int(
                   len(set(map(_signature,source_manifest[stage])))==1)
        totals["roundtrip_"+("vertex" if stage else "fragment")+
               "_binding_layout_stable_across_four_keywords"]=int(
                   len(set(map(_signature,roundtrip_manifest[stage])))==1)
    totals["source_full_pair_descriptor_layouts_distinct"]=len(
        set((_signature(v),_signature(f)) for v,f in pair_source_shapes))
    totals["roundtrip_full_pair_descriptor_layouts_distinct"]=len(
        set((_signature(v),_signature(f)) for v,f in pair_roundtrip_shapes))
    if totals["source_VSFS_keyword_pairs_linked"]!=PAIR_COUNT:
        raise ValueError("source_four_keyword_stage_join_missing")
    return {
        "schema_version":1,"status":STATUS,
        "original_exact_keyword_pairs":PAIR_COUNT,
        "original_vertex_fragment_programs":PAIR_COUNT*2,
        "counts":dict(sorted(totals.items())),
        "original_source_descriptor_set_binding_numbers_published":False,
        "original_private_names_HLSL_DXBC_SPIRV_Guids_published":False,
        "roundtrip_layout_parity_is_NOT_program_numeric_equivalence":True,
        "source_shader_replaced_or_Unity_Android_pixels_proven":False,
    }


def _signature(manifest):
    return tuple((key,tuple(sorted(manifest[key]))) for key in CATEGORIES)


def evaluate(pairs,temporary,*,translator=translate,reflector=reflection):
    if (type(pairs) is not list or len(pairs)!=PAIR_COUNT or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(x) is not bytes or not 0<len(x)<=original.MAX_PRIVATE_STAGE_BYTES
                for x in pair) for pair in pairs) or
        not isinstance(temporary,Path) or not temporary.is_dir() or temporary.is_symlink()):
        raise ValueError("invalid_private_real_original_DXBC_fourpair_scope")
    stages=[]
    for i,pair in enumerate(pairs):
        row={}
        for stage,code in ((1,pair[0]),(0,pair[1])):
            folder=temporary/("keyword-%d-stage-%d"%(i,stage))
            folder.mkdir(exist_ok=False)
            try:
                private_report=translator(code,stage,folder)
            except (ValueError,RuntimeError,OSError,TypeError,KeyError):
                raise PrivateReasonError("SOURCE_STAGE_TRANSLATION") from None
            if (type(private_report) is not dict or
                private_report.get("stage")!=stage or
                any(private_report.get(flag) is not True for flag in (
                    "vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"))):
                raise PrivateReasonError("SOURCE_STAGE_TRANSLATION")
            try:
                row[stage]={
                    "source":reflector(folder/"original.spv"),
                    "roundtrip":reflector(folder/"roundtrip.spv"),
                }
            except (ValueError,RuntimeError,OSError,TypeError,KeyError):
                raise PrivateReasonError("STAGE_SPIRV_REFLECTION") from None
        stages.append(row)
    try:
        return classify_stages(stages)
    except (ValueError,RuntimeError,OSError,TypeError,KeyError) as error:
        allowlist={
            "unlocated_or_malformed_private_resource_descriptor":"DESCRIPTOR_SET_OR_BINDING_UNLOCATED",
            "duplicate_private_stage_resource_binding":"DESCRIPTOR_ALIAS_OR_DUPLICATE",
            "unhandled_private_SPIRV_resource_category":"RESOURCE_CATEGORY_UNSUPPORTED",
            "original_source_SPIRV_stage_IO_not_compatible":"STAGE_SPIRV_IO_INCOMPATIBLE",
            "invalid_private_stage_SPIRV_reflection_schema":"STAGE_REFLECTION_SCHEMA_REJECTED",
            "invalid_private_stage_SPIRV_IO_record":"STAGE_REFLECTION_SCHEMA_REJECTED",
            "duplicate_private_SPIRV_IO_location":"STAGE_REFLECTION_SCHEMA_REJECTED",
            "invalid_private_SPIRV_resource_binding_shape":"STAGE_REFLECTION_SCHEMA_REJECTED",
            "unbounded_private_stage_SPIRV_reflection":"STAGE_REFLECTION_SCHEMA_REJECTED",
        }
        raise PrivateReasonError(
            allowlist.get(str(error),"STAGE_DESCRIPTOR_SCHEMA_OTHER")) from None


def probe(original_root,manifest):
    for command in original.TOOLS:
        if shutil.which(command) is None:
            raise ValueError("missing_pinned_source_private_compiler")
    selection={}
    try:
        baseline=identity.source.load_original(
            original_root,manifest,private_particle_slot_counts=selection)
        owner,pid=identity.select(selection,baseline)
    except (ValueError,RuntimeError,OSError,TypeError,KeyError):
        raise PrivateReasonError("SOURCE_AUTHENTICATION") from None
    path=original_root/"Raft_Data"/owner
    if any(p.is_symlink() for p in (path,*path.parents)) or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("original_selected_particle108_Shader48_SHA_drift")
    import UnityPy
    objects=[o for o in UnityPy.load(str(path)).file.objects.values()
             if o.path_id==pid]
    if len(objects)!=1 or objects[0].type.name!="Shader":
        raise ValueError("missing_exact_SHA_original_108_particle_Shader48")
    source_tree=objects[0].read_typetree()
    parsed=source_tree.get("m_ParsedForm")
    try:
        text,shape=serialize_properties(parsed)
    except (ValueError,RuntimeError,OSError,TypeError,KeyError):
        raise PrivateReasonError("ORIGINAL_SHADER_PROPERTY_SCHEMA") from None
    if (shape["original_authored_property_count"]!=13 or
        shape["original_authored_texture_property_count"]!=2 or
        "HLSLPROGRAM" in text):
        raise ValueError("original_particle108_authored_13_property_contract_drift")
    tables=[records(parts) for platform,parts in decoded_platforms(source_tree)
            if platform==4]
    if len(tables)!=1:
        raise ValueError("original_D3D11_player_program_table_ambiguous")
    src=identity.inspect(parsed,tables[0])
    if (src.get("status")!=identity.STATUS or
        src.get("matched_vertex_fragment_permutation_pairs")!=PAIR_COUNT or
        src.get("original_D3D11_program_table_records")!=16):
        raise ValueError("original_keyword_and_DXBC_baseline_drift")
    try:
        pairs=original.exact_four_pairs(parsed,tables[0])
    except (ValueError,RuntimeError,OSError,TypeError,KeyError):
        raise PrivateReasonError("ORIGINAL_COMPILED_KEYWORD_PAIRS") from None
    with tempfile.TemporaryDirectory(prefix="t3-private-particle108-descriptors-") as dirname:
        report=evaluate(pairs,Path(dirname))
    report["source_original_six_scenes_SHA_verified"]=True
    report["source_original_four_Shader_Material_owners_SHA_verified"]=True
    report["source_original_particle_material_use_slots"]=108
    report["source_authored_shader_properties"]=13
    report["source_authored_texture_properties"]=2
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original","manifest","out"):
        p.add_argument("--"+field,type=Path,required=True)
    args=p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_source_private_resource_report")
    try:
        report=probe(args.original,args.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "safe_failure_reason":(exc.reason if isinstance(exc,PrivateReasonError)
                                       else "UNKNOWN_PRIVATE_STAGE"),
                "original_private_names_HLSL_DXBC_SPIRV_Guids_published":False,
                "source_shader_replaced_or_Unity_Android_pixels_proven":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_ORIGINAL_RESOURCE_BINDINGS_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
