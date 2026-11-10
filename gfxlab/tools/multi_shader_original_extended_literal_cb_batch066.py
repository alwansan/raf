#!/usr/bin/env python3
"""GFX066: independent first 24 Shader48 Pass-scoped class representative source range audit.

Reclassifies only nine known source DXBC fixed-arity ALU opcode families.
A CB operand can have an extended modifier while retaining two *literal*
b-register and vec4 addresses. Actual SPV OpLoad at the same authenticated
b/vec4 range is structural, NOT original operand-by-operand proof: other
source operations may read the same range, and modifier value semantics remain
unknown. All source identifiers, original DXBC/SPV stay private on CI.
"""
from __future__ import annotations
import argparse,json,struct,tempfile
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs,operand,CUSTOMDATA,MAX_DWORDS,MAX_INST
from gfxlab.tools.multi_shader_original_cb_access_shapes import KNOWN_ARITHMETIC_ARITY,scan_known_dxbc_cb_operands
from gfxlab.tools.multi_shader_original_dynamic_cb_taxonomy import original_cb_source_dynamic_taxonomy
from gfxlab.tools.multi_shader_original_cb_byte_addresses import (
    private_authenticated_ubo_layouts,spv_used_literal_byte_addresses,
    compare_source_vec4_range_load_coverage,
)
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

def source_extended_literal_CB_ranges(shdr,declared):
    """Return private (source b -> set(vec4 index)) and safe occurrence counters.

    Extended operand presence does not by itself alter index representation.
    Reject unrecognized/malformed extensions via the independently reused
    operand() decoder; never assume modifier has no effect on loaded value.
    """
    if (not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)%4
            or len(shdr)>MAX_DWORDS*4 or not isinstance(declared,dict)
            or any(type(b)!=int or type(n)!=int or not 0<=b<=65535
                   or not 0<n<=65535 for b,n in declared.items())):
        raise ValueError("GFX066_SOURCE_OR_CB_DECL_INVALID")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):raise ValueError("GFX066_DXBC_LENGTH_MISMATCH")
    by_b={b:set() for b in declared}
    c=Counter({
      "original_covered_fixed_arity_instructions":0,
      "original_noncovered_instructions":0,
      "original_CB_source_operands_in_covered_opcodes":0,
      "original_CB_extended_literal_index_operand_occurrences":0,
      "original_CB_true_dynamic_index_operand_occurrences":0,
      "original_CB_nonextended_literal_operand_occurrences":0,
      "original_extended_literal_CB_distinct_b_vec4_ranges":0,
      "original_CB_extended_modifier_token_type_0_occurrences":0,
      "original_CB_extended_modifier_token_type_1_occurrences":0,
      "original_CB_extended_modifier_token_type_2_occurrences":0,
      "original_CB_extended_modifier_token_type_3_occurrences":0,
      "original_CB_extended_modifier_chained_operand_occurrences":0,
    })
    pos=2
    n=0
    while pos<len(words):
        instr=words[pos];op=instr&2047
        if op==CUSTOMDATA:
            if pos+1>=len(words):raise ValueError("GFX066_CUSTOMDATA_LENGTH_TRUNCATED")
            length=words[pos+1]
            if length<2:raise ValueError("GFX066_BAD_CUSTOMDATA_LENGTH")
        else:
            length=(instr>>24)&127
            if length<1:raise ValueError("GFX066_EMPTY_OPCODE")
        end=pos+length
        if end>len(words):raise ValueError("GFX066_OPCODE_OVERRUN")
        n+=1
        if n>MAX_INST:raise ValueError("GFX066_ORIGINAL_OPCODE_LIMIT")
        if op not in KNOWN_ARITHMETIC_ARITY:
            c["original_noncovered_instructions"]+=1
            pos=end;continue
        cursor=pos+1
        ext=bool(instr&0x80000000)
        ext_count=0
        while ext:
            if cursor>=end or ext_count>=4:
                raise ValueError("GFX066_BAD_OPCODE_EXTENSION")
            val=words[cursor];cursor+=1
            if val&63 not in (0,1,2,3):
                raise ValueError("GFX066_UNKNOWN_OPCODE_EXTENSION")
            ext=bool(val&0x80000000)
            ext_count+=1
        parsed=[]
        try:
            for _ in range(KNOWN_ARITHMETIC_ARITY[op]):
                first=cursor
                d,cursor=operand(words,cursor,end)
                parsed.append((first,d))
            if cursor!=end:
                raise ValueError("GFX066_MISMATCHED_INSTRUCTION_ARITY")
        except (ValueError,IndexError):
            raise ValueError("GFX066_SOURCE_OPERAND_PARSER_REJECTED") from None
        if parsed[0][1]["type"]==8:raise ValueError("GFX066_CB_DESTINATION_NOT_ALLOWED")
        c["original_covered_fixed_arity_instructions"]+=1
        for offset,item in parsed[1:]:
            if item["type"]!=8:continue
            c["original_CB_source_operands_in_covered_opcodes"]+=1
            token=words[offset]
            representation=[(token>>(22+3*k))&7 for k in range(item["dimension"])]
            indices=item["indices"]
            if (item["dimension"]!=2 or len(indices)!=2
                    or len(representation)!=2
                    or any(r not in (0,1) for r in representation)
                    or item["dynamic"]):
                c["original_CB_true_dynamic_index_operand_occurrences"]+=1
                continue
            b,vec=indices
            if type(b)!=int or type(vec)!=int:
                c["original_CB_true_dynamic_index_operand_occurrences"]+=1
                continue
            if b not in declared:raise ValueError("GFX066_UNDECLARED_ORIGINAL_CB_B_REGISTER")
            if not 0<=vec<declared[b]:
                raise ValueError("GFX066_ORIGINAL_CB_VEC4_OUTSIDE_DECLARED_ARRAY")
            if not item["extended"]:
                c["original_CB_nonextended_literal_operand_occurrences"]+=1
                continue
            c["original_CB_extended_literal_index_operand_occurrences"]+=1
            by_b[b].add(vec)
            # A source operand's extended tokens precede immediate indices.
            ep=offset+1
            ext=bool(token&0x80000000)
            count=0
            while ext:
                if ep>=end or count>=4:raise ValueError("GFX066_BAD_OPERAND_MODIFIER_CHAIN")
                extra=words[ep]
                kind=extra&63
                if kind not in (0,1,2,3):raise ValueError("GFX066_UNKNOWN_OPERAND_MODIFIER")
                c["original_CB_extended_modifier_token_type_%d_occurrences"%kind]+=1
                ext=bool(extra&0x80000000)
                count+=1;ep+=1
            if count!=1:c["original_CB_extended_modifier_chained_operand_occurrences"]+=1
        pos=end
    if pos!=len(words):raise ValueError("GFX066_SOURCE_PROGRAM_TERMINATION")
    c["original_extended_literal_CB_distinct_b_vec4_ranges"]=sum(len(v) for v in by_b.values())
    if c["original_CB_source_operands_in_covered_opcodes"]!=sum(
          c[k] for k in ("original_CB_extended_literal_index_operand_occurrences",
             "original_CB_true_dynamic_index_operand_occurrences",
             "original_CB_nonextended_literal_operand_occurrences")):
        raise ValueError("GFX066_CB_OPERAND_PARTITION_INVALID")
    return by_b,dict(c)

def compare_private_source_extended_ranges_to_SPV(extended,loaded):
    """Set range overlap is *not* occurrence-level or modifier-value parity."""
    d=compare_source_vec4_range_load_coverage(extended,loaded)
    return {
      "extended_literal_source_distinct_CB_vec4_ranges":d[
          "source_DXBC_subset_distinct_CB_vec4_ranges"],
      "extended_literal_source_distinct_ranges_with_SPV_OpLoad":d[
          "source_DXBC_subset_CB_vec4_ranges_read_in_translated_SPV"],
      "extended_literal_source_distinct_ranges_without_SPV_OpLoad":d[
          "source_DXBC_subset_CB_vec4_ranges_without_observed_SPV_load"],
      "extended_literal_range_presence_proves_source_modifier_value_semantics":False,
      "extended_literal_range_presence_proves_per_source_operand_read_equivalence":False,
      "literal_index_source_b_to_original_Material_property_proven":False,
      "private_source_b_register_or_vec4_indices_exported":False,
    }

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX066_ORIGINAL_SOURCE_PASS_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        idx=meta.get("m_BlobIndex") if isinstance(meta,dict) else None
        typ=meta.get("m_GpuProgramType") if isinstance(meta,dict) else None
        if type(idx)!=int or type(typ)!=int or not 0<=idx<len(programs):
            raise ValueError("GFX066_SOURCE_PROGRAM_REFERENCE_INVALID")
        key=(idx,typ,kind)
        if key not in cache:
            raw=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(raw)
            slots,declared=private_source_slots(shdr)
            pairs,stats=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={
                "decl":canonical_private_declaration_profile(slots,declared),
                "sampling":private_signature(pairs),
                "unresolved":stats["source_original_unresolved_dynamic_t_s"],
                "shdr":shdr,"dxbc":raw,"cb":declared,
            }
        return cache[key]
    chosen=[];seen=set()
    for start in (0,24,48,72,96,120,144):
        subset,counts,_=select_pass_scoped_joint_classes(passes,inspect,start=start,budget=24)
        expected={
           "original_exact_pairs_scanned":524,
           "global_declaration_classes_ignoring_pass":110,
           "pass_scoped_declaration_classes":132,
           "global_sample_use_classes_ignoring_pass":58,
           "pass_scoped_sample_use_classes":80,
           "pass_scoped_joint_declaration_and_sample_use_classes":157,
        }
        if any(counts.get(k)!=v for k,v in expected.items()):
            raise ValueError("GFX066_ORIGINAL_CLASS_CENSUS_DRIFT")
        if counts["batch_end_index_exclusive"]!=min(start+24,157):
            raise ValueError("GFX066_PRIVATE_CLASS_ORDER_DRIFT")
        for row,v,f in subset:
            private_id=(row["subshader"],row["pass"],v["m_BlobIndex"],f["m_BlobIndex"])
            if private_id in seen:raise ValueError("GFX066_PRIVATE_CLASS_REPRESENTATIVE_DUPLICATE")
            seen.add(private_id)
        chosen.extend(subset)
    if len(cache)!=936 or len(chosen)!=157 or len(seen)!=157:
        raise ValueError("GFX066_ORIGINAL_SOURCE_REPRESENTATIVE_COUNT_DRIFT")
    total=Counter()
    best={}
    stage_instances=0
    for row,v,f in chosen:
        private_score=0
        stage_instances+=2
        for meta,kind in ((v,"Vertex"),(f,"Pixel")):
            private=inspect(meta,kind)
            by_b,s=source_extended_literal_CB_ranges(private["shdr"],private["cb"])
            tax=original_cb_source_dynamic_taxonomy(private["shdr"],private["cb"])
            legacy_,legacy=scan_known_dxbc_cb_operands(private["shdr"],private["cb"])
            relative=sum(tax.get(k,0) for k in (
              "dynamic_b_and_vec","dynamic_b_only","dynamic_vec_relative",
              "dynamic_vec_immediate32_plus_relative",
              "dynamic_vec_immediate64_plus_relative","unsupported_CB_index_shape"))
            if (s["original_CB_extended_literal_index_operand_occurrences"]!=
                    tax["extended_modifier_but_literal_indices"]
                or s["original_CB_true_dynamic_index_operand_occurrences"]!=relative
                or s["original_CB_nonextended_literal_operand_occurrences"]!=
                    legacy["source_static_CB_vector_accesses_in_covered_arithmetic"]
                or s["original_CB_extended_literal_index_operand_occurrences"]+
                   s["original_CB_true_dynamic_index_operand_occurrences"]!=
                   legacy["source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"]):
                raise ValueError("GFX066_INDEPENDENT_ORIGINAL_SOURCE_PARSER_DISAGREEMENT")
            private_score+=s["original_CB_extended_literal_index_operand_occurrences"]
            for key,value in s.items():total[key]+=value
        pa=(row["subshader"],row["pass"])
        if pa not in best or private_score>best[pa][0]:
            best[pa]=(private_score,v,f)
    if stage_instances!=314 or len(best)!=7:
        raise ValueError("GFX066_ORIGINAL_314_STAGES_OR_SEVEN_PASSES_DRIFT")
    if (total["original_CB_extended_literal_index_operand_occurrences"]!=763
        or total["original_CB_true_dynamic_index_operand_occurrences"]!=427
        or total["original_CB_nonextended_literal_operand_occurrences"]!=6800):
        raise ValueError("GFX066_GFX063_ORIGINAL_763_427_SOURCE_COUNT_DRIFT")
    pilot=Counter()
    pilot["source_class_slice_start"]=24
    pilot["source_class_slice_end_exclusive"]=157
    for row,vs,fs in chosen[24:]:
        score=0
        for meta,kind in ((vs,"Vertex"),(fs,"Pixel")):
            original=inspect(meta,kind)
            _,stats=source_extended_literal_CB_ranges(original["shdr"],original["cb"])
            score+=stats["original_CB_extended_literal_index_operand_occurrences"]
        origv=inspect(vs,"Vertex");origf=inspect(fs,"Pixel")
        pilot["selected_original_Pass_pair_instances"]+=1
        if score>0:pilot["selected_Pass_pairs_with_extended_literal_CB_operand"]+=1
        with tempfile.TemporaryDirectory(prefix="gfxlab064-private-") as temp:
            folder=Path(temp)
            trans=translate_pair(origv["dxbc"],origf["dxbc"],folder)
            for kind,original in (("vertex",origv),("fragment",origf)):
                if not trans[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX066_ORIGINAL_SOURCE_SPV_VALIDATOR_FAIL")
                pilot["original_source_stage_instances_Vulkan11_SPV_valid"]+=1
                by_b,cs=source_extended_literal_CB_ranges(original["shdr"],original["cb"])
                pilot["original_modifier_literal_operand_occurrences_in_pilot"]+=cs[
                    "original_CB_extended_literal_index_operand_occurrences"]
                if not original["cb"]:
                    if any(by_b.values()):
                        raise ValueError("GFX066_CB_FREE_STAGE_HAS_SOURCE_CB_RANGES")
                    pilot["original_stage_instances_without_CB"]+=1
                    continue
                spv=folder/(kind+".spv")
                ok,data=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX066_SPV_REFLECTION_FAILED")
                reflection=json.loads(data.decode("utf8","strict"))
                if not isinstance(reflection,dict):raise ValueError("GFX066_SPV_REFLECTION_OBJECT_INVALID")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX066_SPV_DISASSEMBLY_FAILED")
                authenticated,layout=private_authenticated_ubo_layouts(dis,original["cb"],reflection)
                global_CB=global_cb_evidence(dis,original["cb"],reflection.get("ubos",[]))
                if (len(authenticated)!=len(original["cb"])
                    or layout["UBO_globals_strict_single_vec4_array_member_layout"]!=len(original["cb"])
                    or not global_CB["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"]):
                    raise ValueError("GFX066_ORIGINAL_CB_REAL_GLOBAL_LAYOUT_NOT_VERIFIED")
                pilot["original_source_stage_instances_authenticated_b_and_UBO_layout"]+=1
                _,loads,stats=spv_used_literal_byte_addresses(dis,authenticated)
                cmp=compare_private_source_extended_ranges_to_SPV(by_b,loads)
                for key in ("extended_literal_source_distinct_CB_vec4_ranges",
                            "extended_literal_source_distinct_ranges_with_SPV_OpLoad",
                            "extended_literal_source_distinct_ranges_without_SPV_OpLoad"):
                    pilot[key]+=cmp[key]
                pilot["SPV_actual_literal_pointer_load_occurrences"]+=stats[
                    "SPV_pointer_loads_from_supported_access_chains"]
                pilot["original_source_stage_instances_with_modifier_literal_ranges"]+=int(bool(
                    cmp["extended_literal_source_distinct_CB_vec4_ranges"]))
                if cmp["extended_literal_source_distinct_ranges_without_SPV_OpLoad"]==0:
                    pilot["original_source_stage_instances_with_all_modified_literal_ranges_observed"]+=1
    if pilot["selected_original_Pass_pair_instances"]!=133 or pilot[
          "original_source_stage_instances_Vulkan11_SPV_valid"]!=266 or (
          pilot["original_source_stage_instances_authenticated_b_and_UBO_layout"]+
          pilot["original_stage_instances_without_CB"])!=266:
        raise ValueError("GFX066_SPV_PILOT_STAGE_ACCOUNTING")
    if (pilot["extended_literal_source_distinct_ranges_with_SPV_OpLoad"]+
        pilot["extended_literal_source_distinct_ranges_without_SPV_OpLoad"] !=
        pilot["extended_literal_source_distinct_CB_vec4_ranges"]):
        raise ValueError("GFX066_SPV_PRIVATE_RANGE_ACCOUNTING")
    return {
      "experiment":"GFX-MULTI-066",
      "original_zip2_sha":ZIP2_SHA,
      "evidence_level":"SOURCE_PRIVATE_ORIGINAL_SHADER48_EXTENDED_LITERAL_CB_B_VEC4_RANGE_TO_TRANSLATED_SPV_OPLOAD_PILOT_CPU_ONLY",
      "original_exact_VS_FS_source_pairs_censused":524,
      "original_unique_compiled_source_stage_programs":len(cache),
      "original_Pass_joint_source_classes":157,
      "original_source_class_representatives_scanned":len(chosen),
      "original_source_representative_stage_instances_scanned":stage_instances,
      "source_nine_supported_arithmetic_opcode_CB_safe_counts":dict(total),
      "original_remaining133_Pass_joint_extended_literal_pair_batch":dict(pilot),
      "all_763_extended_literal_source_operand_occurrences_individually_SPV_read_proven":False,
      "pilot_range_overlap_proves_individual_source_operand_to_SPV_instruction_mapping":False,
      "remaining133_all_source_extended_literal_distinct_ranges_matched":pilot["extended_literal_source_distinct_ranges_without_SPV_OpLoad"]==0,
      "pilot_range_overlap_proves_extended_operand_value_modifier_semantics":False,
      "original_427_relative_CB_vector_indices_expression_parity_proven":False,
      "all_524_shader_variants_program_semantics_proven":False,
      "Material_property_to_source_t_s_b_and_CB_member_semantic_bridge_proven":False,
      "original_Adreno_GPU_pixel_parity_proven":False,
      "originalShaderRestored":False,"phase_closed":False,
      "private_original_shader_bytes_CB_register_indices_CB_lengths_SpV_or_shader_program_IDs_exported":False,
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
    print("GFX066_SAFE_REMAINING133_EXTENDED_LITERAL_CB_SOURCE_RANGE_SPV_OPLOAD "+json.dumps(result,sort_keys=True))
    if not result["remaining133_all_source_extended_literal_distinct_ranges_matched"]:
        raise SystemExit("GFX066_REMAINING133_ORIGINAL_SOURCE_TO_SPV_OPLOAD_RANGE_MISMATCH")
if __name__=="__main__":main()
