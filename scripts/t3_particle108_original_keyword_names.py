#!/usr/bin/env python3
"""Private original Shader48 keyword-index -> authored table provenance only.

Unity 2021.2+ SerializedShader has m_KeywordNames/m_KeywordFlags. The PC
game's original Unity serialization might predate those fields. We MUST
distinguish absence from corruption and never manufacture keyword names.
Only aggregate counts/status leave the runner. A mapped table is not
evidence that Unity 2021 Android material/keyword dispatch is correct.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts import t3_particle108_original_keyword_lattice as lattice
from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts import t3_original_particle108_spirv_translation as paired
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import stage_variants

STATUS="T3_SOURCE_ORIGINAL_PARTICLE108_KEYWORD_AUTHOR_TABLE_CLASSIFIED"
MAX_TABLE=4096
IDENT=re.compile(r"[_A-Za-z][_A-Za-z0-9]{0,127}\Z")
FIELD="m_KeywordIndices"


def classify(parsed:dict)->dict:
    """Inspect source-only table shape and exact two anonymous switch indices."""
    if type(parsed) is not dict:
        raise ValueError("invalid_original_parsed_form")
    subs=parsed.get("m_SubShaders")
    if (type(subs) is not list or len(subs)!=1 or type(subs[0]) is not dict
        or type(subs[0].get("m_Passes")) is not list or len(subs[0]["m_Passes"])!=1):
        raise ValueError("invalid_original_pass_shape")
    normal=subs[0]["m_Passes"][0]
    shape=lattice.classify(normal)
    if (shape["source_original_VSFS_serialized_variant_keys_exact"] is not True
        or shape["source_original_two_switch_index_set_shape_regardless_of_tier"] is not True):
        raise ValueError("original_pair_lattice_shape_changed")
    rows=stage_variants(normal["progVertex"])
    if len(rows)!=4:
        raise ValueError("not_four_original_variants")
    sets=[]
    for bucket,ordinal,meta in rows:
        # One family: direct array indices only. No implicit mapping from other
        # index namespaces into m_KeywordNames.
        if any(meta.get(other,[]) for other in lattice.FIELDS if other!=FIELD):
            raise ValueError("unexpected_original_keyword_index_namespace")
        keys=meta.get(FIELD)
        if (type(keys) is not list or len(keys)>128
            or any(type(x) is not int or not 0<=x<=lattice.MAX_INDEX for x in keys)):
            raise ValueError("untrusted_original_keyword_indices")
        sets.append(frozenset(keys))
    common=set.intersection(*(set(row) for row in sets))
    switches=set.union(*(set(row)-common for row in sets))
    if (len(switches)!=2 or
        {frozenset(set(row)-common) for row in sets}
        !={frozenset(),frozenset(switches),
           *(frozenset((item,)) for item in switches)}):
        raise ValueError("original_switch_count_drift")
    exists_names="m_KeywordNames" in parsed
    exists_flags="m_KeywordFlags" in parsed
    report={
        "schema_version":1, "status":STATUS,
        "original_source_four_VSFS_pairs_joined":True,
        "original_source_two_switch_index_lattice":True,
        "original_distinct_switch_indices":2,
        "original_parsed_keyword_names_field_present":exists_names,
        "original_parsed_keyword_flags_field_present":exists_flags,
        "keyword_table_size":0,"keyword_flags_size":0,
        "switch_indices_in_table_bounds":False,
        "switch_names_unique_valid_identifiers":False,
        "name_flag_rows_structurally_valid":False,
        "original_switch_index_to_name_table_mapping_proven":False,
        "original_index_name_to_unity_directive_or_global_scope_proven":False,
        "original_material_keyword_variant_runtime_binding_proven":False,
        "Unity_Editor_compile_or_Android_GPU_pixels_proven":False,
        "source_keyword_names_indices_flags_shader_text_or_paths_published":False,
    }
    if not exists_names and not exists_flags:
        report["table_category"]="BOTH_FIELDS_ABSENT_ORIGINAL_SERIALIZATION"
        return report
    if exists_names!=exists_flags:
        report["table_category"]="PARTIAL_KEYWORD_NAME_FLAG_FIELDS"
        return report
    names=parsed["m_KeywordNames"]
    flags=parsed["m_KeywordFlags"]
    if type(names) is not list or type(flags) not in (list,bytes,bytearray):
        report["table_category"]="INVALID_KEYWORD_NAME_FLAG_FIELD_TYPES"
        return report
    if len(names)>MAX_TABLE or len(flags)>MAX_TABLE:
        report["table_category"]="OVERSIZED_KEYWORD_NAME_FLAG_FIELDS"
        return report
    report["keyword_table_size"]=len(names)
    report["keyword_flags_size"]=len(flags)
    if len(names)!=len(flags) or any(type(flag) is not int or not 0<=flag<=255 for flag in flags):
        report["table_category"]="UNTRUSTED_NAME_FLAG_ROW_PARITY"
        return report
    report["name_flag_rows_structurally_valid"]=True
    if any(idx>=len(names) for idx in switches):
        report["table_category"]="ORIGINAL_SWITCH_INDEX_OUTSIDE_TABLE"
        return report
    report["switch_indices_in_table_bounds"]=True
    if any(type(item) is not str or IDENT.fullmatch(item) is None for item in names):
        report["table_category"]="UNSAFE_OR_NONIDENTIFIER_SOURCE_KEYWORD_NAME"
        return report
    if len(set(names))!=len(names) or len({names[idx] for idx in switches})!=2:
        report["table_category"]="DUPLICATED_OR_AMBIGUOUS_KEYWORD_NAME"
        return report
    report["switch_names_unique_valid_identifiers"]=True
    report["original_switch_index_to_name_table_mapping_proven"]=True
    report["table_category"]="TWO_SWITCH_INDEX_NAMES_FOUND_WITH_FLAGS_UNINTERPRETED"
    return report


def probe(original:Path,manifest:Path)->dict:
    if (not isinstance(original,Path) or not original.is_dir() or original.is_symlink()
        or not isinstance(manifest,Path) or not manifest.is_file() or manifest.is_symlink()):
        raise ValueError("invalid_original_path")
    private={}
    census=impact.load_original(original,manifest,private_particle_slot_counts=private)
    owner,pid=identity.select(private,census)
    p=original/"Raft_Data"/owner
    if p.is_symlink() or fingerprint(p)!=SHADER_OWNERS[owner]:
        raise ValueError("original_owner_sha_drift")
    import UnityPy
    matches=[obj for obj in UnityPy.load(str(p)).file.objects.values()
             if obj.type.name=="Shader" and obj.path_id==pid]
    if len(matches)!=1:
        raise ValueError("original_shader_identity_drift")
    tree=matches[0].read_typetree()
    platforms=[records(parts) for platform,parts in decoded_platforms(tree)
               if platform==4]
    if len(platforms)!=1:
        raise ValueError("original_D3D11_platform_missing")
    parsed=tree.get("m_ParsedForm")
    # Authenticate exact VS/FS bytecodes before trusting any metadata names.
    original_pairs=paired.exact_four_pairs(parsed,platforms[0])
    if len(original_pairs)!=4:
        raise ValueError("original_four_pair_DXBC_mismatch")
    result=classify(parsed)
    result["source_sha_verified_six_scenes"]=True
    result["source_sha_verified_four_shader_owners"]=True
    result["original_four_D3D11_program_pairs_linked"]=4
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve()) or
        not args.out.parent.is_dir() or args.out.parent.is_symlink()):
        raise ValueError("unsafe_private_keyword_summary_destination")
    try:
        report=probe(args.original,args.manifest)
    except Exception:
        report={
            "schema_version":1,"status":"INCONCLUSIVE",
            "failure_category":"PRIVATE_ORIGINAL_UNCLASSIFIED",
            "original_switch_index_to_name_table_mapping_proven":False,
            "original_index_name_to_unity_directive_or_global_scope_proven":False,
            "Unity_Editor_compile_or_Android_GPU_pixels_proven":False,
            "source_keyword_names_indices_flags_shader_text_or_paths_published":False,
        }
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_ORIGINAL_KEYWORD_NAME_TABLE_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
