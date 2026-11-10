#!/usr/bin/env python3
"""GFX067: source-private original Shader48 CB relative-index AST grammar.

This records the original nested DXBC operand/address expression rather than
discarding the relative index in a category-only taxonomy. Original b/vec4
indices, source operands, variant identities, and DXBC stay exclusively in CI.
This is NOT original DXBC instruction-SSA to SPIR-V expression equivalence.
"""
from __future__ import annotations
import argparse,json,struct
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import (
    original_sample_pairs,operand,CUSTOMDATA,MAX_DWORDS,MAX_INST,MAX_OPERAND_DEPTH
)
from gfxlab.tools.multi_shader_original_cb_access_shapes import (
    scan_known_dxbc_cb_operands,KNOWN_ARITHMETIC_ARITY
)
from gfxlab.tools.multi_shader_original_dynamic_cb_taxonomy import (
    original_cb_source_dynamic_taxonomy,
)
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes

MAX_EXTENSION=4

def signed32(n):
    if type(n) is not int or not 0<=n<2**32:
        raise ValueError("GFX067_BAD_PRIVATE_U32")
    return n if n<2**31 else n-2**32

def signed64(lo,hi):
    v=(hi<<32)|lo
    return v if v<2**63 else v-2**64

def decode_original_operand_tree(words, pos, end, depth=0):
    """Bounded authentic DXBC operand grammar. ALL returned indices are private.

    A relative address represents nested operand + optional signed literal.
    The source register/component is still a syntactic origin only, not SPV SSA.
    """
    if (not isinstance(words,(list,tuple)) or type(pos)!=int or type(end)!=int
        or pos<0 or end>len(words) or pos>=end or depth>MAX_OPERAND_DEPTH):
        raise ValueError("GFX067_RELATIVE_OPERAND_TREE_BOUNDS")
    first=pos
    token=words[pos];pos+=1
    if type(token)!=int or not 0<=token<2**32:
        raise ValueError("GFX067_OPERAND_WORD_NOT_U32")
    typ=(token>>12)&255
    dim=(token>>20)&3
    components=token&3
    if components==3:
        raise ValueError("GFX067_UNSUPPORTED_N_COMPONENTS")
    selection=(token>>2)&3
    extensions=0
    ext=bool(token&0x80000000)
    while ext:
        if pos>=end or extensions>=MAX_EXTENSION:
            raise ValueError("GFX067_OPERAND_EXTENSION_BOUNDS")
        t=words[pos];pos+=1
        if t&63 not in (0,1,2,3):
            raise ValueError("GFX067_UNKNOWN_OPERAND_EXTENSION")
        ext=bool(t&0x80000000)
        extensions+=1
    indices=[]
    for d in range(dim):
        rep=(token>>(22+3*d))&7
        if rep==0:
            if pos>=end:raise ValueError("GFX067_IMMEDIATE32_TRUNCATED")
            indices.append(("literal32",words[pos]));pos+=1
        elif rep==1:
            if pos+2>end:raise ValueError("GFX067_IMMEDIATE64_TRUNCATED")
            indices.append(("literal64",(words[pos]<<32)|words[pos+1]));pos+=2
        elif rep in (2,3,4):
            base=0
            if rep==3:
                if pos>=end:raise ValueError("GFX067_RELATIVE_IMMEDIATE32_TRUNCATED")
                base=signed32(words[pos]);pos+=1
            elif rep==4:
                if pos+2>end:raise ValueError("GFX067_RELATIVE_IMMEDIATE64_TRUNCATED")
                # Original DXBC signed 64-bit base is kept source-private.
                base=signed64(words[pos],words[pos+1]);pos+=2
            child,pos=decode_original_operand_tree(words,pos,end,depth+1)
            indices.append(("relative",rep,base,child))
        else:
            raise ValueError("GFX067_INVALID_OPERAND_INDEX_REP")
    if typ in (4,5):
        if components not in (1,2):
            raise ValueError("GFX067_IMMEDIATE_VALUE_COMPONENTS")
        count=(1 if components==1 else 4)*(1 if typ==4 else 2)
        if pos+count>end:raise ValueError("GFX067_IMMEDIATE_VALUE_TRUNCATED")
        pos+=count
    return {
        "type":typ, "dimension":dim,"components":components,
        "selection":selection,"component_token_bits":(token>>4)&255,
        "indices":tuple(indices),"extensions":extensions,"depth":depth,
        "private_start":first
    },pos

def _private_tree_signature(tree):
    """Private equality key; never exported. Includes source registers and offsets."""
    return (tree["type"],tree["components"],tree["selection"],
            tree["component_token_bits"],
            tuple((item[0],item[1]) if item[0]!="relative" else
                  ("relative",item[1],item[2],_private_tree_signature(item[3]))
                  for item in tree["indices"]))

def _relative_shape(tree):
    """Return only safe semantic *categories*, no original source identity."""
    nested=tree["indices"][1][3]
    rep=tree["indices"][1][1]
    base=tree["indices"][1][2]
    # DXBC operand type integers are private implementation metadata, not Unity roles.
    typ=nested["type"]
    # The nested type is only a syntactic source category.
    category="temporary" if typ==0 else ("input" if typ==1 else "other_register_or_expression")
    return {
      "representation":rep,
      "base_sign":"negative" if base<0 else ("positive" if base>0 else "zero"),
      "nested_type_category":category,
      "nested_dimension":nested["dimension"],
      "nested_component_count_code":nested["components"],
      "nested_selection_mode":nested["selection"],
      "nested_has_relative_index":any(x[0]=="relative" for x in nested["indices"]),
      "nested_modifier_present":nested["extensions"]>0,
    }

def source_relative_CB_index_AST_census(shdr,declared):
    """Independent nested parse of all CB sources within 9 supported DXBC opcodes.

    Preserve exact private address expressions; publish only safe counts.
    Unknown register/component role is not guessed to be a valid SSA origin.
    """
    if (not isinstance(shdr,bytes) or not 12<=len(shdr)<=MAX_DWORDS*4 or len(shdr)%4
        or not isinstance(declared,dict) or
        any(type(b)!=int or type(n)!=int or not 0<=b<=65535 or not 0<n<=65535
            for b,n in declared.items())):
        raise ValueError("GFX067_ORIGINAL_SOURCE_INPUT_INVALID")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):raise ValueError("GFX067_DXBC_LENGTH_MISMATCH")
    stats=Counter()
    unique_private=set()
    p=2;count=0
    while p<len(words):
        raw=words[p];opcode=raw&2047
        if opcode==CUSTOMDATA:
            if p+1>=len(words) or words[p+1]<2:
                raise ValueError("GFX067_DXBC_CUSTOMDATA_BROKEN")
            size=words[p+1]
        else:size=(raw>>24)&127
        if size<1 or p+size>len(words):
            raise ValueError("GFX067_DXBC_INSTRUCTION_BOUNDS")
        end=p+size;count+=1
        if count>MAX_INST:raise ValueError("GFX067_DXBC_INSTRUCTION_LIMIT")
        if opcode not in KNOWN_ARITHMETIC_ARITY:
            stats["outside_nine_supported_arithmetic_opcodes"]+=1
            p=end;continue
        cursor=p+1
        extension=bool(raw&0x80000000);extensions=0
        while extension:
            if cursor>=end or extensions>=MAX_EXTENSION:
                raise ValueError("GFX067_DXBC_OPCODE_EXTENSIONS_INVALID")
            w=words[cursor];cursor+=1
            if w&63 not in (0,1,2,3):
                raise ValueError("GFX067_DXBC_OPCODE_EXTENSION_TYPE")
            extension=bool(w&0x80000000);extensions+=1
        operands=[]
        for i in range(KNOWN_ARITHMETIC_ARITY[opcode]):
            first=cursor
            independent,cursor=decode_original_operand_tree(words,cursor,end)
            established,legacy_end=operand(words,first,end)
            if cursor!=legacy_end or independent["type"]!=established["type"] or independent["dimension"]!=established["dimension"]:
                raise ValueError("GFX067_INDEPENDENT_DXBC_OPERAND_BOUNDARY_DRIFT")
            operands.append(independent)
        if cursor!=end:raise ValueError("GFX067_SOURCE_INSTRUCTION_TRAILING_TOKENS")
        if operands[0]["type"]==8:raise ValueError("GFX067_SOURCE_CB_DESTINATION_DISALLOWED")
        stats["covered_nine_opcode_instruction_occurrences"]+=1
        for tree in operands[1:]:
            if tree["type"]!=8:continue
            stats["covered_CB_operand_occurrences"]+=1
            if tree["dimension"]!=2 or len(tree["indices"])!=2:
                stats["unsupported_CB_operand_shape"]+=1
                continue
            b,vec=tree["indices"]
            if b[0]=="relative":
                stats["dynamic_original_b_register_index_unresolved"]+=1
                continue
            if b[0] not in ("literal32","literal64") or type(b[1])!=int or b[1] not in declared:
                raise ValueError("GFX067_ORIGINAL_CB_REGISTER_NOT_DECLARED")
            if vec[0]=="relative":
                rep=vec[1]
                if rep not in (2,3,4):
                    raise ValueError("GFX067_SOURCE_RELATIVE_ENCODING_UNKNOWN")
                stats["relative_original_CB_vec4_operand_occurrences"]+=1
                shape=_relative_shape(tree)
                stats["relative_representation_%d"%rep]+=1
                stats["relative_base_"+shape["base_sign"]]+=1
                stats["relative_nested_"+shape["nested_type_category"]]+=1
                stats["relative_nested_selection_mode_%d"%shape["nested_selection_mode"]]+=1
                stats["relative_nested_dimension_%d"%shape["nested_dimension"]]+=1
                stats["relative_nested_components_code_%d"%shape["nested_component_count_code"]]+=1
                stats["relative_nested_modifier_occurrences"]+=int(shape["nested_modifier_present"])
                stats["relative_nested_has_more_relative_index_occurrences"]+=int(shape["nested_has_relative_index"])
                # This is private, not an exported identity, name, or D3D address.
                unique_private.add((b[1],_private_tree_signature(tree)))
            elif vec[0] in ("literal32","literal64"):
                if not 0<=vec[1]<declared[b[1]]:
                    raise ValueError("GFX067_STATIC_VEC4_OUTSIDE_ORIGINAL_CB")
                stats["static_CB_operand_occurrences"]+=1
            else:
                stats["unsupported_CB_operand_shape"]+=1
        p=end
    if p!=len(words):raise ValueError("GFX067_SOURCE_PROGRAM_TERMINATION")
    stats["relative_private_distinct_expression_keys_within_this_stage"]=len(unique_private)
    if stats["relative_original_CB_vec4_operand_occurrences"] != sum(
        stats["relative_representation_%d"%i] for i in (2,3,4)):
        raise ValueError("GFX067_SOURCE_RELATIVE_REPRESENTATION_ACCOUNTING")
    if stats["covered_CB_operand_occurrences"] != (
        stats["relative_original_CB_vec4_operand_occurrences"]+
        stats["static_CB_operand_occurrences"]+
        stats["dynamic_original_b_register_index_unresolved"]+
        stats["unsupported_CB_operand_shape"]):
        raise ValueError("GFX067_ORIGINAL_CB_OPERAND_ACCOUNTING")
    return dict(stats)

def source_to_spv_relative_expression_acceptance(source_operand,spv_index,independent_origin_proof=None):
    """Explicitly BLOCK numeric/SSA parity absent independently validated root.

    Equal offsets/counts are not an identity proof. Real DXBC register-def-use
    and generated SPV SSA-root provenance must be supplied by a future checker.
    GFX067 supplies none; there is deliberately no inferred success path.
    """
    if independent_origin_proof is None:
        return {"verdict":"BLOCKED_NO_INDEPENDENT_DXBC_TO_SPV_SSA_ROOT",
                "per_source_operand_expression_parity_proven":False,
                "source_relative_index_runtime_bounds_proven":False}
    raise ValueError("GFX067_NO_AUTHENTICATED_SSA_IDENTITY_PROOF_IMPLEMENTED")

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX067_SOURCE_PROGRAM_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        if not isinstance(meta,dict):raise ValueError("GFX067_STAGE_META_NOT_OBJECT")
        idx=meta.get("m_BlobIndex");typ=meta.get("m_GpuProgramType")
        if type(idx)!=int or type(typ)!=int or not 0<=idx<len(programs):
            raise ValueError("GFX067_SOURCE_STAGE_REFERENCE_INVALID")
        k=(idx,typ,kind)
        if k not in cache:
            raw=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(raw)
            slots,declared=private_source_slots(shdr)
            pairs,sample_stats=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[k]={"decl":canonical_private_declaration_profile(slots,declared),
                      "sampling":private_signature(pairs),
                      "unresolved":sample_stats["source_original_unresolved_dynamic_t_s"],
                      "shdr":shdr,"cb":declared}
        return cache[k]
    chosen=[];seen=set()
    for start in (0,24,48,72,96,120,144):
        subset,selection,_=select_pass_scoped_joint_classes(passes,inspect,start=start,budget=24)
        required={"original_exact_pairs_scanned":524,
                  "global_declaration_classes_ignoring_pass":110,
                  "pass_scoped_declaration_classes":132,
                  "global_sample_use_classes_ignoring_pass":58,
                  "pass_scoped_sample_use_classes":80,
                  "pass_scoped_joint_declaration_and_sample_use_classes":157}
        if any(selection.get(k)!=v for k,v in required.items()):
            raise ValueError("GFX067_SOURCE_PRIVATE_JOINT_CLASS_CENSUS_DRIFT")
        if selection["batch_end_index_exclusive"]!=min(start+24,157):
            raise ValueError("GFX067_PRIVATE_SOURCE_CLASS_ORDER_DRIFT")
        for row,v,f in subset:
            secret=(row["subshader"],row["pass"],v["m_BlobIndex"],f["m_BlobIndex"])
            if secret in seen:raise ValueError("GFX067_REPEATED_ORIGINAL_REPRESENTATIVE")
            seen.add(secret)
        chosen.extend(subset)
    if len(cache)!=936 or len(chosen)!=157 or len(seen)!=157:
        raise ValueError("GFX067_ORIGINAL_SOURCE_CLASS_ACCOUNTING")
    total=Counter();stage_count=0
    for row,v,f in chosen:
        for meta,kind in ((v,"Vertex"),(f,"Pixel")):
            original=inspect(meta,kind)
            ast=source_relative_CB_index_AST_census(original["shdr"],original["cb"])
            legacy=original_cb_source_dynamic_taxonomy(original["shdr"],original["cb"])
            _,other=scan_known_dxbc_cb_operands(original["shdr"],original["cb"])
            if (ast["relative_original_CB_vec4_operand_occurrences"] !=
                    legacy["dynamic_vec_relative"]+
                    legacy["dynamic_vec_immediate32_plus_relative"]+
                    legacy["dynamic_vec_immediate64_plus_relative"]
                or ast["static_CB_operand_occurrences"]!=
                    legacy["extended_modifier_but_literal_indices"]+
                    legacy["source_CB_static_unmodified_operand_occurrences"]
                or ast["covered_CB_operand_occurrences"]!=other["source_CB_source_operand_occurrences_in_covered_arithmetic"]
                    if "source_CB_source_operand_occurrences_in_covered_arithmetic" in other else False):
                raise ValueError("GFX067_INDEPENDENT_SOURCE_CB_AST_TAXONOMY_DISAGREEMENT")
            for key,val in ast.items():total[key]+=val
            stage_count+=1
    if (stage_count!=314 or
        total["relative_original_CB_vec4_operand_occurrences"]!=427 or
        total["relative_representation_2"]!=77 or
        total["relative_representation_3"]!=350 or
        total["relative_representation_4"]!=0 or
        total["covered_CB_operand_occurrences"]!=7990 or
        total["static_CB_operand_occurrences"]!=7563 or
        total["outside_nine_supported_arithmetic_opcodes"]!=11297):
        raise ValueError("GFX067_ORIGINAL_427_RELATIVE_AST_SOURCE_COUNT_DRIFT")
    verdict=source_to_spv_relative_expression_acceptance(None,None)
    return {
      "experiment":"GFX-MULTI-067",
      "original_zip2_sha":ZIP2_SHA,
      "evidence_level":"ORIGINAL_SOURCE_427_TRUE_RELATIVE_CB_SOURCE_OPERAND_NESTED_AST_GRAMMAR_CPU_ONLY",
      "original_exact_VS_FS_source_pairs_censused":524,
      "original_unique_compiled_source_stage_programs":len(cache),
      "original_Pass_joint_representative_classes":len(chosen),
      "original_stage_instances_grammar_scanned":stage_count,
      "source_relative_expression_safe_aggregate":dict(total),
      "source_to_SPV_SSA_provenance":verdict,
      "original_relative_CB_operand_to_SPV_index_expression_parity_count_proven":0,
      "original_427_relative_CB_operand_numeric_runtime_semantics_proven":False,
      "original_extended_literal_CB_range_656_of_656_previous_cpu_verified":True,
      "all_524_original_shader_program_instructions_semantically_equivalent":False,
      "source_cb_arithmetic_opcode_subset_completeness_proven":False,
      "authentic_Material_property_to_b_t_s_CB_member_byte_mapping_proven":False,
      "original_Android_GPU_Shader48_pixels_verified":False,
      "originalShaderRestored":False,"phase_closed":False,
      "source_private_DXBC_SPV_registers_nested_operands_exported":False
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
    print("GFX067_SAFE_427_ORIGINAL_RELATIVE_CB_EXPRESSION_GRAMMAR "+json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
