#!/usr/bin/env python3
"""GFX068 original Shader48 relative CB source temp component nearest-writer probe.

A nearest earlier writer within a *contiguous known nine-ALU-opcode run* is only
a local source syntax candidate. All unknown instructions (including branch,
loop, declaration, and unsupported ALU) CLEAR the candidate writer cache.
Never claim proper CFG dominance, runtime address equality or DXBC→SPIR-V SSA.
All original registers and source bytecode remain SHA-pinned CI-private.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path
from collections import Counter
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import (
    original_sample_pairs,CUSTOMDATA,MAX_DWORDS,MAX_INST,operand
)
from gfxlab.tools.multi_shader_original_cb_access_shapes import KNOWN_ARITHMETIC_ARITY
from gfxlab.tools.multi_shader_original_cb_relative_expression067 import (
    source_relative_CB_index_AST_census,decode_original_operand_tree
)
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes

def temp_component_source_origin(nested):
    """Return a PRIVATE (DXBC temporary register, selected component) candidate.

    Reject all but DXBC source operand type=temporary, dim1, direct literal
    temp index, Select1 component selection with an x/y/z/w component.
    """
    if not isinstance(nested,dict):
        return None
    if (nested["type"]!=0 or nested["dimension"]!=1 or
        nested["selection"]!=2 or len(nested["indices"])!=1 or
        nested["indices"][0][0] not in ("literal32","literal64")):
        return None
    index=nested["indices"][0][1]
    if type(index)!=int or index<0 or index>65535:
        return None
    component=nested["component_token_bits"]&3
    return (index,component)

def supported_temp_dest_written_components(dest):
    """Only a true register destination with explicit nonzero write mask."""
    if not isinstance(dest,dict) or dest["type"]!=0:
        return None
    if (dest["dimension"]!=1 or dest["components"]!=2 or
        dest["selection"]!=0 or len(dest["indices"])!=1 or
        dest["indices"][0][0] not in ("literal32","literal64")):
        return None
    idx=dest["indices"][0][1]
    mask=dest["component_token_bits"]&15
    if type(idx)!=int or not 0<=idx<=65535 or mask==0:
        return None
    return (idx,tuple(i for i in range(4) if mask&(1<<i)))

def original_relative_temp_nearest_writer_census(shdr,declared):
    """Source-private linear syntax study; barriers prohibit false dominance."""
    if (not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)%4 or
        len(shdr)>MAX_DWORDS*4 or not isinstance(declared,dict)):
        raise ValueError("GFX068_SOURCE_INPUT_INVALID")
    w=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if w[1]!=len(w):raise ValueError("GFX068_DXBC_SOURCE_LENGTH_MISMATCH")
    live={} # PRIVATE (temporary register, x/y/z/w)->(source opcode, position)
    c=Counter();p=2;n=0
    while p<len(w):
        head=w[p];op=head&2047
        if op==CUSTOMDATA:
            if p+1>=len(w) or w[p+1]<2:
                raise ValueError("GFX068_CUSTOMDATA_LENGTH_MALFORMED")
            length=w[p+1]
        else:length=(head>>24)&127
        if length<1 or p+length>len(w):
            raise ValueError("GFX068_DXBC_INSTRUCTION_BOUNDARY_INVALID")
        end=p+length;n+=1
        if n>MAX_INST:raise ValueError("GFX068_INSTRUCTION_LIMIT")
        if op not in KNOWN_ARITHMETIC_ARITY:
            live.clear()
            c["unsupported_opcode_barriers_invalidating_all_live_writer_candidates"]+=1
            p=end
            continue
        cursor=p+1;ext=bool(head&0x80000000);n_ext=0
        while ext:
            if cursor>=end or n_ext>=4:
                raise ValueError("GFX068_BAD_OPCODE_EXTENSION")
            value=w[cursor];cursor+=1
            if value&63 not in (0,1,2,3):
                raise ValueError("GFX068_UNKNOWN_OPCODE_EXTENSION")
            ext=bool(value&0x80000000);n_ext+=1
        args=[]
        for _ in range(KNOWN_ARITHMETIC_ARITY[op]):
            first=cursor
            node,cursor=decode_original_operand_tree(w,cursor,end)
            old,legacy_cursor=operand(w,first,end)
            if (cursor!=legacy_cursor or node["type"]!=old["type"] or
                node["dimension"]!=old["dimension"]):
                raise ValueError("GFX068_TWO_ORIGINAL_OPERAND_PARSERS_DISAGREE")
            args.append(node)
        if cursor!=end:raise ValueError("GFX068_OPCODE_ARITY_TRAILING_DATA")
        if args[0]["type"]==8:
            raise ValueError("GFX068_CB_AS_WRITE_DESTINATION")
        c["supported_arithmetic_instruction_occurrences"]+=1
        # SOURCE reads precede destination writes even within a single opcode.
        for tree in args[1:]:
            if tree["type"]!=8:
                continue
            c["original_CB_operand_occurrences_in_supported_opcodes"]+=1
            if tree["dimension"]!=2 or len(tree["indices"])!=2:
                c["original_CB_unsupported_dimensional_operand"]+=1
                continue
            b,vec=tree["indices"]
            if b[0] not in ("literal32","literal64") or b[1] not in declared:
                c["original_CB_register_not_static_or_unmapped"]+=1
                continue
            if vec[0]!="relative":
                c["original_CB_nonrelative_operand_occurrences"]+=1
                continue
            c["original_CB_true_relative_vec_index_occurrences"]+=1
            origin=temp_component_source_origin(vec[3])
            if origin is None:
                c["relative_source_temp_component_not_supported"]+=1
                continue
            c["relative_source_temp_selected_component_syntax_valid"]+=1
            prior=live.get(origin)
            if prior is None:
                c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"]+=1
            else:
                opcode,at=prior
                c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"]+=1
                c["candidate_nearest_writer_original_opcode_%d"%opcode]+=1
                gap=n-at
                bucket="one_instruction" if gap==1 else ("two_to_four" if gap<=4 else "five_or_more")
                c["candidate_nearest_writer_gap_"+bucket]+=1
        dest=args[0]
        if dest["type"]==0:
            x=supported_temp_dest_written_components(dest)
            if x is None:
                live.clear()
                c["unrecognized_temporary_destination_invalidated_all_writer_candidates"]+=1
            else:
                reg,components=x
                for comp in components:
                    live[(reg,comp)]=(op,n)
                    c["supported_original_temp_component_writes"]+=1
        p=end
    if p!=len(w):raise ValueError("GFX068_SOURCE_PROGRAM_DID_NOT_TERMINATE")
    if (c["original_CB_true_relative_vec_index_occurrences"]!=
        c["relative_source_temp_selected_component_syntax_valid"]+
        c["relative_source_temp_component_not_supported"]
        or c["relative_source_temp_selected_component_syntax_valid"]!=
        c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"]+
        c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"]):
        raise ValueError("GFX068_RELATIVE_TEMP_WRITER_CANDIDATE_PARTITION_MISMATCH")
    return dict(c)

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX068_SOURCE_COMPILER_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        if not isinstance(meta,dict):
            raise ValueError("GFX068_SOURCE_STAGE_NOT_DICTIONARY")
        idx=meta.get("m_BlobIndex");typ=meta.get("m_GpuProgramType")
        if type(idx)!=int or type(typ)!=int or not 0<=idx<len(programs):
            raise ValueError("GFX068_SOURCE_PROGRAM_REFERENCE_INVALID")
        key=(idx,typ,kind)
        if key not in cache:
            original=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(original)
            slots,cb=private_source_slots(shdr)
            pairs,stats=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={"decl":canonical_private_declaration_profile(slots,cb),
                        "sampling":private_signature(pairs),
                        "unresolved":stats["source_original_unresolved_dynamic_t_s"],
                        "shdr":shdr,"cb":cb}
        return cache[key]
    chosen=[];seen=set()
    for start in (0,24,48,72,96,120,144):
        subset,safe,_=select_pass_scoped_joint_classes(passes,inspect,start=start,budget=24)
        expected={"original_exact_pairs_scanned":524,
                  "global_declaration_classes_ignoring_pass":110,
                  "pass_scoped_declaration_classes":132,
                  "global_sample_use_classes_ignoring_pass":58,
                  "pass_scoped_sample_use_classes":80,
                  "pass_scoped_joint_declaration_and_sample_use_classes":157}
        if any(safe.get(k)!=v for k,v in expected.items()) or safe["batch_end_index_exclusive"]!=min(start+24,157):
            raise ValueError("GFX068_AUTHENTIC_SOURCE_REPRESENTATIVE_ORDER_DRIFT")
        for row,v,f in subset:
            key=(row["subshader"],row["pass"],v["m_BlobIndex"],f["m_BlobIndex"])
            if key in seen:raise ValueError("GFX068_REPEATED_PRIVATE_SOURCE_PAIR")
            seen.add(key)
        chosen.extend(subset)
    if len(chosen)!=157 or len(seen)!=157 or len(cache)!=936:
        raise ValueError("GFX068_157_SOURCE_CLASS_REPRESENTATIVES_DRIFT")
    total=Counter();scanned=0
    for _,vm,fm in chosen:
        for meta,kind in ((vm,"Vertex"),(fm,"Pixel")):
            private=inspect(meta,kind)
            c=original_relative_temp_nearest_writer_census(private["shdr"],private["cb"])
            independent=source_relative_CB_index_AST_census(private["shdr"],private["cb"])
            if (c.get("original_CB_true_relative_vec_index_occurrences",0)!=independent.get("relative_original_CB_vec4_operand_occurrences",0)
                or c.get("original_CB_operand_occurrences_in_supported_opcodes",0)!=independent.get("covered_CB_operand_occurrences",0)
                or c.get("supported_arithmetic_instruction_occurrences",0)!=independent.get("covered_nine_opcode_instruction_occurrences",0)):
                raise ValueError("GFX068_INDEPENDENT_GFX067_SOURCE_STAGE_COUNT_DISAGREEMENT")
            for k,v in c.items():total[k]+=v
            scanned+=1
    if (scanned!=314 or
        total["original_CB_true_relative_vec_index_occurrences"]!=427 or
        total["original_CB_operand_occurrences_in_supported_opcodes"]!=7990 or
        total["supported_arithmetic_instruction_occurrences"]!=19847 or
        total["relative_source_temp_selected_component_syntax_valid"]!=427):
        raise ValueError("GFX068_ORIGINAL_SOURCE_TEMP_OR_CB_ACCOUNTING_DRIFT")
    return {
        "experiment":"GFX-MULTI-068","source_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_RELATIVE_CB_TEMP_COMPONENT_LOCAL_NEAREST_WRITER_CANDIDATE_ONLY_CPU_NO_CFG_OR_SPV",
        "source_exact_original_VS_FS_pairs_censused":524,
        "source_unique_compiled_stages":len(cache),
        "original_source_pass_joint_representative_pairs":len(chosen),
        "original_stage_instances":scanned,
        "original_relative_CB_source_temporary_candidate_aggregates":dict(total),
        "any_local_writer_candidate_proves_CFG_dominance":False,
        "any_local_writer_candidate_proves_DXBC_to_SPV_SSA_provenance":False,
        "source_relative_CB_operand_to_SPV_index_expression_parity_proven":0,
        "all_427_original_relative_CB_runtime_semantics_proven":False,
        "authentic_Material_to_t_s_b_CB_byte_member_semantics_proven":False,
        "original_Shader48_Android_GPU_pixels_verified":False,
        "originalShaderRestored":False,"phase_closed":False,
        "private_source_temp_registers_or_shader_bytecode_exported":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX068_SAFE_427_ORIGINAL_RELATIVE_CB_TEMP_WRITER_CANDIDATES "+json.dumps(d,sort_keys=True))

if __name__=="__main__": main()
