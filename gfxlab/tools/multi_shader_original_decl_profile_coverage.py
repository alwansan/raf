#!/usr/bin/env python3
"""GFX-MULTI-055: coverage of original Shader48 b/t/s declarations, all 524 exact VS/FS pairs.

The original SHA-pinned Raft ZIP2 is staged privately; parse genuine linked DXBC
SHDR/SHEX declarations, cache stage programs by authenticated BlobIndex/stage,
compare canonical private register/CB-byte-vector profiles across all original
exact keyword/hardware-tier matches. Report only integer class counts and
anonymized per-pass coverage. NEVER serialize private slot indices, CB vector
lengths, signature hashes, original shader bytecode/labels or keyword strings.

This does NOT add an original Material property -> b/t/s binding witness,
a ShaderLab/HLSL source, or actual original Shader48 GPU/device parity.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots

MAX_EXACT_PAIRS=2000
MAX_PROGRAMS=1656
MAX_REGISTERS=1024
EXPECTED_EXACT_PAIRS=524
FIELDS=("constant_buffer","resource","sampler")

def canonical_private_declaration_profile(slots,cb_sizes):
    """Resource identity and CB vec4 dimensions held *only in private memory*."""
    if (not isinstance(slots,dict) or not isinstance(cb_sizes,dict)
        or set(slots)!=set(FIELDS)):
        raise ValueError("GFX055_STAGE_SOURCE_SLOT_FAMILIES_INVALID")
    groups=[]
    for family in FIELDS:
        values=slots[family]
        if not isinstance(values,set) or len(values)>MAX_REGISTERS:
            raise ValueError("GFX055_STAGE_SOURCE_REGISTER_SET_INVALID")
        if any(type(v) is not int or not 0<=v<=65535 for v in values):
            raise ValueError("GFX055_SOURCE_REGISTER_INVALID")
        groups.append(tuple(sorted(values)))
    if set(cb_sizes)!=slots["constant_buffer"]:
        raise ValueError("GFX055_SOURCE_CB_DECLARATION_SET_MISMATCH")
    if (len(cb_sizes)>MAX_REGISTERS
        or any(type(v) is not int or not 0<n<=65535
               for v,n in cb_sizes.items())):
        raise ValueError("GFX055_SOURCE_CB_SIZE_INVALID")
    return tuple(groups),tuple(sorted(cb_sizes.items()))

def _one_profile_stats(profile):
    groups, cb = profile
    return (len(groups[0]),len(groups[1]),len(groups[2]),
            sum(n for _,n in cb))

def safe_one_pass_profile_summary(rows):
    """All register values stay in private hashable signatures, never report."""
    if not isinstance(rows,list) or not 1<=len(rows)<=MAX_EXACT_PAIRS:
        raise ValueError("GFX055_SOURCE_PASS_EXACT_PAIRS_INVALID")
    checked=[]
    for pair in rows:
        if (not isinstance(pair,tuple) or len(pair)!=2 or
            any(not isinstance(x,tuple) or len(x)!=2 for x in pair)):
            raise ValueError("GFX055_PAIR_STAGE_PROFILE_INVALID")
        for stage in pair:
            groups, cb = stage
            if (not isinstance(groups,tuple) or len(groups)!=3
                or any(not isinstance(g,tuple) for g in groups)
                or not isinstance(cb,tuple)):
                raise ValueError("GFX055_PAIR_STAGE_PROFILE_SHAPE_INVALID")
        checked.append(pair)
    first=checked[0]
    count=len(checked)
    family_names=("constant_buffer_registers","texture_resource_registers","sampler_registers")
    out={
      "original_exact_keyword_tier_pairs":count,
      "private_joint_VS_FS_declaration_profile_classes":len(set(checked)),
      "pairs_same_full_structural_profile_as_first_pair":sum(x==first for x in checked),
      "pairs_outside_first_structural_profile":sum(x!=first for x in checked),
      "private_CB_register_values_or_sizes_in_report":False,
      "same_profile_implies_same_shader_instructions_or_pixel_output":False,
    }
    for stage_idx,stage_label in enumerate(("vertex","fragment")):
        stage_rows=[x[stage_idx] for x in checked]
        f=stage_rows[0]
        cb_profiles=[x[1] for x in stage_rows]
        first_cb=cb_profiles[0]
        out[stage_label+"_full_structural_profile_classes"]=len(set(stage_rows))
        out[stage_label+"_pairs_same_first_full_profile"]=sum(x==f for x in stage_rows)
        out[stage_label+"_pairs_outside_first_full_profile"]=sum(x!=f for x in stage_rows)
        out[stage_label+"_CB_slot_and_vec4_length_profile_classes"]=len(set(cb_profiles))
        out[stage_label+"_pairs_outside_first_CB_size_register_profile"]=sum(x!=first_cb for x in cb_profiles)
        out[stage_label+"_zero_original_CB_declaration_pair_references"]=sum(not x[1] for x in stage_rows)
        # Number of resource declarations can be published; not IDs / lengths.
        for fam_i,label in enumerate(family_names):
            family_profiles=[x[0][fam_i] for x in stage_rows]
            out[stage_label+"_"+label+"_identity_profile_classes"]=len(set(family_profiles))
            out[stage_label+"_pairs_outside_first_"+label+"_identity"]=sum(
                x!=family_profiles[0] for x in family_profiles)
            # Count frequency of number-of-declarations ONLY. No values.
            counts=Counter(len(x) for x in family_profiles)
            out[stage_label+"_"+label+"_count_histogram"]={
                str(k):v for k,v in sorted(counts.items())}
    if (out["pairs_same_full_structural_profile_as_first_pair"]+
            out["pairs_outside_first_structural_profile"]!=count):
        raise ValueError("GFX055_FIRST_PROFILE_ACCOUNTING")
    return out

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX055_ORIGINAL_SHADER48_COMPILED_TOPOLOGY_DRIFT")
    cache={}
    def parse_one(meta,expected):
        blob_index=meta.get("m_BlobIndex")
        declared_type=meta.get("m_GpuProgramType")
        if (type(blob_index) is not int or type(declared_type) is not int
            or not 0<=blob_index<len(programs)):
            raise ValueError("GFX055_ORIGINAL_SOURCE_SUBPROGRAM_INDEX_INVALID")
        cache_key=(blob_index,expected,declared_type)
        if cache_key not in cache:
            if len(cache)>=MAX_PROGRAMS:
                raise ValueError("GFX055_SOURCE_CACHE_UNBOUNDED")
            # Identity checks include authentic DX11 family, stage and type.
            real=code_from_ref(meta,programs,expected)
            slots,cb_sizes=private_source_slots(source_shader_chunk(real))
            cache[cache_key]=canonical_private_declaration_profile(slots,cb_sizes)
        return cache[cache_key]
    totals=Counter({
      "original_exact_keyword_tier_pairs_scanned":0,
      "authentic_DXBC_stage_reference_uses_scanned":0,
      "source_stages_without_declared_CB":0,
      "source_stages_without_declared_texture_resource":0,
      "source_stages_without_declared_sampler":0,
      "pairs_matching_first_structural_profile_in_their_pass":0,
      "pairs_outside_first_structural_profile_in_their_pass":0,
      "pairs_with_vertex_CB_declaration_change_vs_first":0,
      "pairs_with_fragment_CB_declaration_change_vs_first":0,
    })
    per_pass=[]
    all_classes=set()
    for entry in passes:
        pair_meta=entry["pairs"]
        if not isinstance(pair_meta,list) or not 1<=len(pair_meta)<=MAX_EXACT_PAIRS:
            raise ValueError("GFX055_ORIGINAL_PASS_EXACT_VARIANTS_UNEXPECTED")
        rows=[]
        for v,f in pair_meta:
            pv=parse_one(v,"Vertex")
            pf=parse_one(f,"Pixel")
            rows.append((pv,pf))
            all_classes.add((pv,pf))
            totals["original_exact_keyword_tier_pairs_scanned"]+=1
            totals["authentic_DXBC_stage_reference_uses_scanned"]+=2
            totals["source_stages_without_declared_CB"]+=int(not pv[1])+int(not pf[1])
            totals["source_stages_without_declared_texture_resource"]+=int(not pv[0][1])+int(not pf[0][1])
            totals["source_stages_without_declared_sampler"]+=int(not pv[0][2])+int(not pf[0][2])
        safe=safe_one_pass_profile_summary(rows)
        totals["pairs_matching_first_structural_profile_in_their_pass"]+=safe["pairs_same_full_structural_profile_as_first_pair"]
        totals["pairs_outside_first_structural_profile_in_their_pass"]+=safe["pairs_outside_first_structural_profile"]
        totals["pairs_with_vertex_CB_declaration_change_vs_first"]+=safe["vertex_pairs_outside_first_CB_size_register_profile"]
        totals["pairs_with_fragment_CB_declaration_change_vs_first"]+=safe["fragment_pairs_outside_first_CB_size_register_profile"]
        per_pass.append({
           "subshader_public_position":entry["subshader"],
           "pass_public_position":entry["pass"],
           **safe,
        })
    if (totals["original_exact_keyword_tier_pairs_scanned"]!=EXPECTED_EXACT_PAIRS
        or totals["authentic_DXBC_stage_reference_uses_scanned"]!=2*EXPECTED_EXACT_PAIRS
        or len(per_pass)!=7
        or sum(p["original_exact_keyword_tier_pairs"] for p in per_pass)!=EXPECTED_EXACT_PAIRS):
        raise ValueError("GFX055_SOURCE_524_EXACT_PAIR_ACCOUNTING_DRIFT")
    return {
        "experiment":"GFX-MULTI-055",
        "original_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_ALL_524_EXACT_PAIR_DECLARATION_PROFILE_COVERAGE_CPU_ONLY",
        "original_Shader48_subshaders":2,
        "original_Shader48_passes":7,
        "original_exact_keyword_tier_VS_FS_pairs":EXPECTED_EXACT_PAIRS,
        "original_exact_pair_stage_reference_instances":2*EXPECTED_EXACT_PAIRS,
        "original_unique_stage_programs_cached_for_these_pairs":len(cache),
        "total_private_joint_VS_FS_b_t_s_CB_layout_profile_classes":len(all_classes),
        "safe_counts":dict(totals),
        "per_pass":per_pass,
        "all_524_original_exact_pairs_declaration_profiles_parsed":True,
        "all_524_original_exact_pairs_translated_to_SPIRV":False,
        "all_524_original_source_CB_load_addresses_compared":False,
        "original_Material_property_to_DXBC_t_s_b_register_or_member_semantics_proven":False,
        "original_Shader48_Android_GPU_execution_proven":False,
        "original_PC_vs_Adreno_pixel_parity_proven":False,
        "originalShaderRestored":False,
        "private_shader_code_register_indices_CB_vec4_lengths_profile_signatures_or_keywords_exported":False,
        "phase_closed":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX055_SAFE_ALL_524_ORIGINAL_B_T_S_CB_PROFILE_SCOPE_COUNTS "+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
