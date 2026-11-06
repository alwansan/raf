#!/usr/bin/env python3
"""T3: source-authentic Particle108 original DXBC authored signature coverage.

Original D3D11 ISGN/ISG1 and OSGN/OSG1/OSG5 input/output signatures from
four exact source VS/FS keyword pairs, strict masks/types/register records.
Private signature semantic names, DXBC, PathIDs, GUIDs never leave runner.
This does NOT identify compiler-generated SPIR-V names or original-to-HLSL
Location correspondence and cannot prove Vulkan or Android visual parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_particle108_spirv_translation as tr
from scripts.t3_original_921_dxbc_semantic_join import (
    COUNTER_FIELDS, read_original_dxbc_signatures, compare_original_vf
)
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS="SOURCE_SHA_ORIGINAL_PARTICLE108_FOUR_DXBC_SEMANTIC_MASK_LINKS_CLASSIFIED"
PAIRS=4
SAFE_PAIR_FIELDS=(
    "original_unmatched_fragment_semantic_records",
    "original_unmatched_fragment_component_lanes",
    "original_matched_semantic_missing_output_component_lanes",
    "original_matched_semantic_type_mismatches",
)


def classify_pairs(pairs:list,*,reader=read_original_dxbc_signatures,
                   join=compare_original_vf):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 or
            any(type(buf) is not bytes or not 0<len(buf)<=4*1024*1024
                for buf in pair) for pair in pairs)):
        raise ValueError("invalid_authenticated_four_original_DXBC_pair_scope")
    totals=Counter()
    for pair in pairs:
        # ALL original authored semantic values stay private. Do not
        # stringify raw signature rows, even on validation failure.
        vertex=reader(pair[0])
        fragment=reader(pair[1])
        if type(vertex) is not dict or type(fragment) is not dict:
            raise ValueError("untrusted_private_original_DXBC_signature_data")
        comparison=join(vertex,fragment)
        if type(comparison) is not dict or set(comparison)!=set(COUNTER_FIELDS):
            raise ValueError("untrusted_private_original_semantic_join_aggregate")
        for key in COUNTER_FIELDS:
            value=comparison[key]
            if type(value) is not int or not 0<=value<=4096:
                raise ValueError("invalid_private_original_semantic_counter")
            totals[key]+=value
        totals["source_exact_keyword_pairs_classified"]+=1
        totals["source_pairs_with_complete_user_VSFS_semantic_mask_type_link"]+=(
            all(comparison[k]==0 for k in SAFE_PAIR_FIELDS))
        totals["source_pairs_with_unmatched_fragment_semantics"]+=(
            comparison["original_unmatched_fragment_semantic_records"]>0)
        totals["source_pairs_with_component_mask_shortfalls"]+=(
            comparison["original_matched_semantic_missing_output_component_lanes"]>0)
        totals["source_pairs_with_component_type_mismatch"]+=(
            comparison["original_matched_semantic_type_mismatches"]>0)
    if (totals["source_exact_keyword_pairs_classified"]!=PAIRS or
        totals["original_programs_read"]!=8):
        raise ValueError("original_Particle108_fourpair_semantic_link_incomplete")
    keys=tuple(COUNTER_FIELDS)+(
        "source_exact_keyword_pairs_classified",
        "source_pairs_with_complete_user_VSFS_semantic_mask_type_link",
        "source_pairs_with_unmatched_fragment_semantics",
        "source_pairs_with_component_mask_shortfalls",
        "source_pairs_with_component_type_mismatch"
    )
    return {
        "schema_version":1,"status":STATUS,
        "original_source_particle108_material_slots":108,
        "original_source_particle_renderer_count":54,
        "original_source_shader48_normal_Passes":1,
        "original_exact_VSFS_keyword_pairs":PAIRS,
        "original_D3D11_table_entry_count":16,
        "counts":{key:int(totals[key]) for key in keys},
        "original_compiled_DXBC_authored_semantic_signatures_read":True,
        "original_semantic_to_SPIRV_Location_or_HLSL_mapping_verified":False,
        "original_source_private_semantic_names_masks_registers_or_bytes_published":False,
        "original_source_ShaderLab_or_Android_pixels_modified":False,
        "native_Unity_Android_Adreno_pixels_verified":False,
    }


def probe(original:Path,manifest:Path):
    import UnityPy
    sourcegraph={}
    report=tr.source.source.load_original(original,manifest,
                                          private_particle_slot_counts=sourcegraph)
    owner,pid=tr.source.select(sourcegraph,report)
    path=original/"Raft_Data"/owner
    if (any(part.is_symlink() for part in (path,*path.parents))
        or fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("authentic_original_particle108_Shader_owner_SHA_drift")
    selected=[o for o in UnityPy.load(str(path)).file.objects.values()
              if o.path_id==pid]
    if len(selected)!=1 or selected[0].type.name!="Shader":
        raise ValueError("original_particle108_Shader48_identity_drift")
    parsed=selected[0].read_typetree()
    tables=[records(segments) for p,segments in decoded_platforms(parsed)
            if p==4]
    if len(tables)!=1:
        raise ValueError("original_particle108_D3D11_table_ambiguous")
    base=tr.source.inspect(parsed["m_ParsedForm"],tables[0])
    if (base.get("status")!=tr.source.STATUS or
        base.get("original_D3D11_program_table_records")!=16 or
        base.get("genuine_D3D11_vertex_stage_variant_records")!=4 or
        base.get("genuine_D3D11_fragment_stage_variant_records")!=4 or
        base.get("matched_vertex_fragment_permutation_pairs")!=4 or
        base.get("unmatched_vertex_permutations")!=0 or
        base.get("unmatched_fragment_permutations")!=0):
        raise ValueError("original_particle108_semantic_probe_stage_baseline_drift")
    paired=tr.exact_four_pairs(parsed["m_ParsedForm"],tables[0])
    out=classify_pairs(paired)
    out["six_original_scenes_SHA_authenticated"]=True
    out["four_original_shader_owners_SHA_authenticated"]=True
    return out


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        a.add_argument("--"+key,required=True,type=Path)
    args=a.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_private_original_DXBC_semantics_report_path")
    try:
        out=probe(args.original,args.manifest)
    except Exception as exc:
        out={"schema_version":1,"status":"INCONCLUSIVE",
             "failure_type":type(exc).__name__,
             "original_source_private_semantic_names_masks_registers_or_bytes_published":False,
             "native_Unity_Android_Adreno_pixels_verified":False,
             "original_source_ShaderLab_or_Android_pixels_modified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_AUTHENTIC_DXBC_SIGNATURE "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
