#!/usr/bin/env python3
"""GFX056: original Shader48 pass-scoped declaration and sample-use classes.

Source remains SHA-pinned and private on CI; no Shader48 bytecode, b/t/s slot,
CB size, property, sample signature, keyword, or program ID is published.
Only 24 first-round, pass-balanced representative pairs are CPU translated.
Neither same declaration/sampling class nor successful SPV validation proves
shader instruction equivalence, original Material binding, or Android pixels.
"""
import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair, code_from_ref, translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs, stage_compare
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_representative_spirv_profiles import filter_nonresource_opnames
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence
from gfxlab.tools.multi_shader_original_cb_byte_addresses import (
    private_authenticated_ubo_layouts, scan_known_dxbc_cb_operands,
    spv_used_literal_byte_addresses, compare_source_vec4_range_load_coverage,
)
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

BUDGET=24

def select_pass_scoped_joint_classes(passes, inspector, budget=BUDGET):
    """Keep representative source pairs privately; report aggregate class counts."""
    if (not isinstance(passes,list) or len(passes)!=7
            or type(budget) is not int or not 1<=budget<=BUDGET):
        raise ValueError("GFX056_PASS_OR_BUDGET_INVALID")
    global_decl=set();scoped_decl=set();global_sample=set()
    scoped_sample=set();scoped_joint=set();ordered=[];safe_pass=[]
    scanned=0
    for row in passes:
        if not isinstance(row,dict):raise ValueError("GFX056_PASS_INVALID")
        sub,pa,pairs=(row.get("subshader"),row.get("pass"),row.get("pairs"))
        if type(sub) is not int or type(pa) is not int or not isinstance(pairs,list) or not 1<=len(pairs)<=2000:
            raise ValueError("GFX056_PASS_PAIR_ROWS_INVALID")
        local_decl=set();local_sample=set();local_joint=set();reps=[]
        for pair in pairs:
            if not isinstance(pair,(tuple,list)) or len(pair)!=2:
                raise ValueError("GFX056_EXACT_SOURCE_PAIR_INVALID")
            v=inspector(pair[0],"Vertex")
            f=inspector(pair[1],"Pixel")
            if (not isinstance(v,dict) or not isinstance(f,dict)
                or any(not isinstance(k.get("decl"),tuple)
                       or not isinstance(k.get("sampling"),tuple)
                       or type(k.get("unresolved")) is not int
                       or k["unresolved"]<0 for k in (v,f))):
                raise ValueError("GFX056_PRIVATE_SOURCE_INSPECTOR_SHAPE_INVALID")
            d=(v["decl"],f["decl"])
            s=(v["sampling"],f["sampling"])
            joint=(sub,pa,d,s)
            global_decl.add(d);global_sample.add(s)
            scoped_decl.add((sub,pa,d));scoped_sample.add((sub,pa,s))
            local_decl.add(d);local_sample.add(s)
            if joint not in scoped_joint:
                scoped_joint.add(joint);local_joint.add(joint)
                reps.append((row,pair[0],pair[1]))
            scanned+=1
        ordered.append(reps)
        safe_pass.append({
          "subshader_public_position":sub,
          "pass_public_position":pa,
          "original_exact_pairs":len(pairs),
          "declaration_classes":len(local_decl),
          "sampling_signature_classes":len(local_sample),
          "joint_declaration_sampling_classes":len(local_joint),
        })
    chosen=[]
    pos=0
    while len(chosen)<budget and any(pos<len(x) for x in ordered):
        for reps in ordered:
            if pos<len(reps) and len(chosen)<budget:chosen.append(reps[pos])
        pos+=1
    pass_counts=Counter((r["subshader"],r["pass"]) for r,_,_ in chosen)
    for r in safe_pass:
        r["first_CPU_batch_representative_pairs"]=pass_counts[(r["subshader_public_position"],r["pass_public_position"])]
    if (sum(x["joint_declaration_sampling_classes"] for x in safe_pass)!=len(scoped_joint)
        or len(chosen)!=min(budget,len(scoped_joint))):
        raise ValueError("GFX056_SELECTION_ACCOUNTING_INVALID")
    result={
      "original_exact_pairs_scanned":scanned,
      "global_declaration_classes_ignoring_pass":len(global_decl),
      "pass_scoped_declaration_classes":len(scoped_decl),
      "global_sample_use_classes_ignoring_pass":len(global_sample),
      "pass_scoped_sample_use_classes":len(scoped_sample),
      "pass_scoped_joint_declaration_and_sample_use_classes":len(scoped_joint),
      "first_CPU_batch_budget":budget,
      "first_CPU_batch_representative_pairs":len(chosen),
      "joint_classes_untranslated_in_first_batch":len(scoped_joint)-len(chosen),
      "untested_classes_CPU_SPIRV_parity_confirmed":False,
      "private_declaration_samples_keywords_or_variant_IDs_exported":False,
    }
    return chosen,result,safe_pass

def audit(stage,budget=BUDGET):
    programs,passes=source_pair(stage)
    if len(programs)!=1656:raise ValueError("GFX056_ORIGINAL_PROGRAM_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        idx=meta.get("m_BlobIndex") if isinstance(meta,dict) else None
        t=meta.get("m_GpuProgramType") if isinstance(meta,dict) else None
        if type(idx) is not int or type(t) is not int or not 0<=idx<len(programs):
            raise ValueError("GFX056_PRIVATE_SOURCE_INDEX_INVALID")
        key=(idx,t,kind)
        if key not in cache:
            if len(cache)>=1656:raise ValueError("GFX056_SOURCE_CACHE_LIMIT")
            raw=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(raw)
            slots,cb=private_source_slots(shdr)
            pair,stat=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={
                "decl":canonical_private_declaration_profile(slots,cb),
                "sampling":private_signature(pair),
                "unresolved":stat["source_original_unresolved_dynamic_t_s"],
            }
        return cache[key]
    selected,selection,rows=select_pass_scoped_joint_classes(passes,inspect,budget)
    if (selection["original_exact_pairs_scanned"]!=524
        or selection["global_declaration_classes_ignoring_pass"]!=110
        or selection["pass_scoped_declaration_classes"]!=132
        or selection["global_sample_use_classes_ignoring_pass"]!=58
        or len(cache)!=936):
        raise ValueError("GFX056_INDEPENDENT_GFX048_055_CLASS_COUNTER_DRIFT")
    counts=Counter({
       "first_batch_pairs_attempted":0,
       "first_batch_pairs_both_stages_Vulkan11_validated":0,
       "first_batch_pairs_with_all_source_SPV_checks_passing":0,
       "first_batch_pairs_with_any_rejection_or_unresolved":0,
       "source_stages_attempted":0,
       "source_stages_spirv_val_pass":0,
       "source_stages_sample_t_s_use_pair_multiset_equal":0,
       "source_stages_sample_comparison_unresolved":0,
       "source_stages_without_CB_declaration":0,
       "source_stages_original_CB_global_and_single_vec4_layout_proven":0,
       "source_stages_CB_symbol_or_layout_unresolved":0,
       "source_stages_CB_supported_opcode_vector_ranges_all_have_spv_loads":0,
       "source_stages_CB_supported_opcode_vector_ranges_unresolved":0,
       "source_CB_supported_opcode_distinct_vec4_range_uses":0,
       "source_CB_supported_opcode_vec4_ranges_with_SPV_loads":0,
       "source_CB_supported_opcode_vec4_ranges_without_SPV_load":0,
       "source_CB_dynamic_operand_occurrences_unresolved":0,
    })
    reasons=Counter()
    for passrow,vm,fm in selected:
        counts["first_batch_pairs_attempted"]+=1
        ok_pair=True
        originals={"vertex":code_from_ref(vm,programs,"Vertex"),
                   "fragment":code_from_ref(fm,programs,"Pixel")}
        with tempfile.TemporaryDirectory(prefix="gfxlab056-private-") as tmp:
            folder=Path(tmp)
            converted=translate_pair(originals["vertex"],originals["fragment"],folder)
            if all(converted[x]["vulkan11_spirv_validation_success"] for x in ("vertex","fragment")):
                counts["first_batch_pairs_both_stages_Vulkan11_validated"]+=1
            for kind in ("vertex","fragment"):
                counts["source_stages_attempted"]+=1
                if not converted[kind]["vulkan11_spirv_validation_success"]:
                    reasons["SPV_conversion_or_validation"]+=1
                    ok_pair=False
                    continue
                counts["source_stages_spirv_val_pass"]+=1
                spv=folder/(kind+".spv")
                good,data=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not good:
                    reasons["SPV_reflection_tool"]+=1;ok_pair=False;continue
                try:ref=json.loads(data.decode("utf-8","strict"))
                except (UnicodeDecodeError,ValueError):
                    ref=None
                if not isinstance(ref,dict):
                    reasons["SPV_reflection_structure"]+=1;ok_pair=False;continue
                good,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not good:
                    reasons["SPV_disassembly_tool"]+=1;ok_pair=False;continue
                try:
                    sample=stage_compare(originals[kind],spv,ref,
                                         filter_nonresource_opnames(dis))
                    sample_equal=sample["same_exact_private_original_DXBC_t_s_pair_multiset_as_translated_SPIRV"]
                except (ValueError,IndexError,KeyError,TypeError):
                    sample_equal=False
                    reasons["sample_pair_parser_rejected"]+=1
                if sample_equal:
                    counts["source_stages_sample_t_s_use_pair_multiset_equal"]+=1
                else:
                    counts["source_stages_sample_comparison_unresolved"]+=1
                    ok_pair=False
                shdr=source_shader_chunk(originals[kind])
                _,source_cb=private_source_slots(shdr)
                if not source_cb:
                    counts["source_stages_without_CB_declaration"]+=1
                    continue
                try:
                    global_names=global_cb_evidence(dis,source_cb,ref.get("ubos",[]))
                    actual,layout=private_authenticated_ubo_layouts(dis,source_cb,ref)
                    all_layout=(global_names["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"]
                      and layout["UBO_globals_strict_single_vec4_array_member_layout"]==len(source_cb)
                      and len(actual)==len(source_cb))
                    if not all_layout:
                        counts["source_stages_CB_symbol_or_layout_unresolved"]+=1
                        reasons["CB_original_global_or_array_layout"]+=1
                        ok_pair=False
                        continue
                    counts["source_stages_original_CB_global_and_single_vec4_layout_proven"]+=1
                    source_vecs,srcstats=scan_known_dxbc_cb_operands(shdr,source_cb)
                    _,ranges,_=spv_used_literal_byte_addresses(dis,actual)
                    cmp=compare_source_vec4_range_load_coverage(source_vecs,ranges)
                    counts["source_CB_dynamic_operand_occurrences_unresolved"]+=srcstats[
                        "source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"]
                    counts["source_CB_supported_opcode_distinct_vec4_range_uses"]+=cmp[
                        "source_DXBC_subset_distinct_CB_vec4_ranges"]
                    counts["source_CB_supported_opcode_vec4_ranges_with_SPV_loads"]+=cmp[
                        "source_DXBC_subset_CB_vec4_ranges_read_in_translated_SPV"]
                    counts["source_CB_supported_opcode_vec4_ranges_without_SPV_load"]+=cmp[
                        "source_DXBC_subset_CB_vec4_ranges_without_observed_SPV_load"]
                    if cmp["source_DXBC_subset_CB_vec4_ranges_without_observed_SPV_load"]==0:
                        counts["source_stages_CB_supported_opcode_vector_ranges_all_have_spv_loads"]+=1
                    else:
                        counts["source_stages_CB_supported_opcode_vector_ranges_unresolved"]+=1
                        reasons["CB_partial_source_vec4_load_range_unresolved"]+=1
                        ok_pair=False
                except (ValueError,IndexError,KeyError,TypeError):
                    reasons["CB_original_operand_or_SPV_use_parser_rejected"]+=1
                    ok_pair=False
        if ok_pair:
            counts["first_batch_pairs_with_all_source_SPV_checks_passing"]+=1
        else:
            counts["first_batch_pairs_with_any_rejection_or_unresolved"]+=1
    if (counts["source_stages_attempted"]!=2*len(selected)
        or counts["first_batch_pairs_with_all_source_SPV_checks_passing"]+
           counts["first_batch_pairs_with_any_rejection_or_unresolved"]!=len(selected)
        or counts["source_CB_supported_opcode_vec4_ranges_with_SPV_loads"]+
           counts["source_CB_supported_opcode_vec4_ranges_without_SPV_load"]!=
           counts["source_CB_supported_opcode_distinct_vec4_range_uses"]):
        raise ValueError("GFX056_SOURCE_SAFE_RESULT_ACCOUNTING_DRIFT")
    return {
       "experiment":"GFX-MULTI-056","original_zip2_sha":ZIP2_SHA,
       "evidence_level":"ORIGINAL_SOURCE_524_JOINT_CLASS_CENSUS_AND_BOUND_24_CPU_SPIRV_STAGE_CHECKS",
       "original_shader48_passes":7,
       "source_original_distinct_compiled_stages_inspected":len(cache),
       "source_joint_class_selection_safe_counts":selection,
       "source_per_pass_anonymous_joint_class_counts_and_pilot":rows,
       "first_24_source_CPU_validation_counts":dict(counts),
       "first_24_fixed_public_failure_categories":dict(reasons),
       "full_joint_class_original_CPU_SPIRV_validation_done":False,
       "all_524_original_pairs_individually_SPIRV_translated":False,
       "same_declaration_and_sampling_class_means_same_shader_semantics":False,
       "original_material_property_to_DXBC_t_s_b_register_binding_proven":False,
       "source_CB_member_byte_offsets_as_Material_properties_proven":False,
       "Shader48_original_android_GPU_execution_proven":False,
       "PC_to_Adreno_original_pixels_equivalent":False,
       "originalShaderRestored":False,"phase_closed":False,
       "private_original_code_CB_lengths_register_slots_sample_tuples_or_keywords_exported":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--budget",type=int,default=BUDGET)
    a=p.parse_args()
    result=audit(stage_originals(a.zip2,a.stage),a.budget)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX056_SAFE_PASS_SCOPED_DECLARATION_SAMPLING_CPU_PILOT "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
