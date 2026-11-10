#!/usr/bin/env python3
"""GFX074 original Shader48 per-stage original source b-register + literal relative vec4 offsets vs loaded translated SPV UBO pointers private multiset evidence.

A nearest earlier writer within a *contiguous trusted writer-opcode run* is only
a local source syntax candidate. All unknown instructions (including branch,
loop, declaration, and unsupported ALU) CLEAR the candidate writer cache.
Never claim proper CFG dominance, runtime address equality or DXBC→SPIR-V SSA.
All original registers and source bytecode remain SHA-pinned CI-private.
"""
from __future__ import annotations
import argparse,json,struct,tempfile
from pathlib import Path
from collections import Counter
from gfxlab.tools.multi_shader_spv_cb_index_add_shape072 import shifted_source_spv_dynamic_UBO_reads,compare_private_stage_relative_source_to_spv_index_shapes
from gfxlab.tools.multi_shader_spv_index_memory_writer074 import spv_index_local_store_candidates
from gfxlab.tools.multi_shader_spv_index_pointer_origin075 import authenticated_spv_CB_index_pointer_origins
from gfxlab.tools.multi_shader_spv_index_address_path_store076 import authenticated_spv_CB_index_address_path_stores
from gfxlab.tools.multi_shader_spv_index_local_store_value077 import authenticated_spv_CB_index_local_store_value_producers
from gfxlab.tools.multi_shader_spv_unknown_cfg078 import authenticated_spv_CB_index_local_store_unknowns_and_cfg078
from gfxlab.tools.multi_shader_spv_unknown_family079 import authenticated_spv_CB_index_unknown_terminal_families079
from gfxlab.tools.multi_shader_spv_integer_terminal_shapes080 import authenticated_spv_CB_index_unknown_integer_opcode_shapes080
from gfxlab.tools.multi_shader_spv_imul_dynamic_operand081 import authenticated_spv_CB_index_imul_dynamic_operand081
from gfxlab.tools.multi_shader_spv_imul_input_load_writes082 import authenticated_spv_CB_index_imul_input_load_writes082
from gfxlab.tools.multi_shader_spv_imul_input_writer_value083 import authenticated_spv_CB_index_imul_input_writer_value083
from gfxlab.tools.multi_shader_spv_imul_input_writer_inner084 import authenticated_spv_CB_index_imul_input_writer_underlying084
from gfxlab.tools.multi_shader_spv_imul_writer_iadd_operands085 import authenticated_spv_CB_index_imul_input_writer_iadd_operands085
from gfxlab.tools.multi_shader_spv_iadd_operand_load_storage086 import authenticated_spv_CB_index_imul_iadd_input_load_storage086
from gfxlab.tools.multi_shader_spv_iadd_input_uniform_iface087 import authenticated_spv_CB_index_iadd_load_interfaces087
from gfxlab.tools.multi_shader_spv_dxbc_input_ubo_overlap088 import authenticated_spv_CB_index_iadd_source_provenance088
from gfxlab.tools.multi_shader_spv_dxbc_input_signature089 import input_interface_source_semantic089
from gfxlab.tools.multi_shader_spv_actual_iadd_source_signature090 import authenticated_spv_CB_index_source_input_signature090
from gfxlab.tools.multi_shader_spv_actual_input_mask_width091 import authenticated_spv_CB_index_actual_input_component_width091
from gfxlab.tools.multi_shader_original_cb_index_b_offset073 import (original_source_private_b_relative_offset_multiset,translated_spv_private_authenticated_b_relative_offset_multiset,compare_private_b_and_relative_literal_multisets)
from gfxlab.tools.multi_shader_original_dynamic_cb_taxonomy import spv_authenticated_dynamic_cb_pointer_loads
from gfxlab.tools.multi_shader_original_cb_byte_addresses import private_authenticated_ubo_layouts
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
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

# Public opcode IDs from Microsoft DirectX-Headers
# D3D12TokenizedProgramFormat.hpp (main blob b95145430ffca8aed30fe57fc9d27ae70908ee05).
# Only standard opcodes with exactly one destination and documented operand arity.
# All others remain HARD source provenance barriers (including control flow).
EXTRA_TRUSTED_WRITER_OPCODE_ARITY={
  1:3,   # AND dst, src0, src1
  27:2,  # FTOI dst, src
  28:2,  # FTOU dst, src
  30:3,  # IADD dst, src0, src1
  35:4,  # IMAD dst, src0, src1, src2
  41:3,  # ISHL dst, src0, src1
  42:3,  # ISHR dst, src0, src1
  43:2,  # ITOF dst, src
  55:4,  # MOVC dst, condition, true, false
  59:2,  # NOT dst, src
  60:3,  # OR dst, src0, src1
  85:3,  # USHR dst, src0, src1
  86:2,  # UTOF dst, src
  87:3,  # XOR dst, src0, src1
}
assert set(EXTRA_TRUSTED_WRITER_OPCODE_ARITY).isdisjoint(KNOWN_ARITHMETIC_ARITY)
TRUSTED_TEMP_WRITER_ARITY={**KNOWN_ARITHMETIC_ARITY,**EXTRA_TRUSTED_WRITER_OPCODE_ARITY}

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
        raise ValueError("GFX074_SOURCE_INPUT_INVALID")
    w=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if w[1]!=len(w):raise ValueError("GFX074_DXBC_SOURCE_LENGTH_MISMATCH")
    live={} # PRIVATE (temporary register, x/y/z/w)->(source opcode, position)
    c=Counter();p=2;n=0
    while p<len(w):
        head=w[p];op=head&2047
        if op==CUSTOMDATA:
            if p+1>=len(w) or w[p+1]<2:
                raise ValueError("GFX074_CUSTOMDATA_LENGTH_MALFORMED")
            length=w[p+1]
        else:length=(head>>24)&127
        if length<1 or p+length>len(w):
            raise ValueError("GFX074_DXBC_INSTRUCTION_BOUNDARY_INVALID")
        end=p+length;n+=1
        if n>MAX_INST:raise ValueError("GFX074_INSTRUCTION_LIMIT")
        if op not in TRUSTED_TEMP_WRITER_ARITY:
            live.clear()
            c["unsupported_opcode_barriers_invalidating_all_live_writer_candidates"]+=1
            p=end
            continue
        cursor=p+1;ext=bool(head&0x80000000);n_ext=0
        while ext:
            if cursor>=end or n_ext>=4:
                raise ValueError("GFX074_BAD_OPCODE_EXTENSION")
            value=w[cursor];cursor+=1
            if value&63 not in (0,1,2,3):
                raise ValueError("GFX074_UNKNOWN_OPCODE_EXTENSION")
            ext=bool(value&0x80000000);n_ext+=1
        args=[]
        for _ in range(TRUSTED_TEMP_WRITER_ARITY[op]):
            first=cursor
            node,cursor=decode_original_operand_tree(w,cursor,end)
            old,legacy_cursor=operand(w,first,end)
            if (cursor!=legacy_cursor or node["type"]!=old["type"] or
                node["dimension"]!=old["dimension"]):
                raise ValueError("GFX074_TWO_ORIGINAL_OPERAND_PARSERS_DISAGREE")
            args.append(node)
        if cursor!=end:raise ValueError("GFX074_OPCODE_ARITY_TRAILING_DATA")
        if args[0]["type"]==8:
            raise ValueError("GFX074_CB_AS_WRITE_DESTINATION")
        if op in KNOWN_ARITHMETIC_ARITY:
            c["supported_arithmetic_instruction_occurrences"]+=1
        else:
            c["extra_trusted_writer_opcode_instances"]+=1
        # SOURCE reads precede destination writes even within a single opcode.
        for tree in args[1:]:
            if op not in KNOWN_ARITHMETIC_ARITY:continue
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
    if p!=len(w):raise ValueError("GFX074_SOURCE_PROGRAM_DID_NOT_TERMINATE")
    if (c["original_CB_true_relative_vec_index_occurrences"]!=
        c["relative_source_temp_selected_component_syntax_valid"]+
        c["relative_source_temp_component_not_supported"]
        or c["relative_source_temp_selected_component_syntax_valid"]!=
        c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"]+
        c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"]):
        raise ValueError("GFX074_RELATIVE_TEMP_WRITER_CANDIDATE_PARTITION_MISMATCH")
    return dict(c)

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX074_SOURCE_COMPILER_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        if not isinstance(meta,dict):
            raise ValueError("GFX074_SOURCE_STAGE_NOT_DICTIONARY")
        idx=meta.get("m_BlobIndex");typ=meta.get("m_GpuProgramType")
        if type(idx)!=int or type(typ)!=int or not 0<=idx<len(programs):
            raise ValueError("GFX074_SOURCE_PROGRAM_REFERENCE_INVALID")
        key=(idx,typ,kind)
        if key not in cache:
            original=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(original)
            slots,cb=private_source_slots(shdr)
            pairs,stats=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={"decl":canonical_private_declaration_profile(slots,cb),
                        "sampling":private_signature(pairs),
                        "unresolved":stats["source_original_unresolved_dynamic_t_s"],
                        "shdr":shdr,"dxbc":original,"cb":cb}
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
            raise ValueError("GFX074_AUTHENTIC_SOURCE_REPRESENTATIVE_ORDER_DRIFT")
        for row,v,f in subset:
            key=(row["subshader"],row["pass"],v["m_BlobIndex"],f["m_BlobIndex"])
            if key in seen:raise ValueError("GFX074_REPEATED_PRIVATE_SOURCE_PAIR")
            seen.add(key)
        chosen.extend(subset)
    if len(chosen)!=157 or len(seen)!=157 or len(cache)!=936:
        raise ValueError("GFX074_157_SOURCE_CLASS_REPRESENTATIVES_DRIFT")
    total=Counter();spv_total=Counter();scanned=0
    for _,vm,fm in chosen:
        vs=inspect(vm,"Vertex")
        fs=inspect(fm,"Pixel")
        with tempfile.TemporaryDirectory(prefix="gfxlab070-original-private-") as tmp:
            folder=Path(tmp)
            translated=translate_pair(vs["dxbc"],fs["dxbc"],folder)
            spv_total["source_exact_VS_FS_pairs_translated"]+=1
            for kind,private in (("vertex",vs),("fragment",fs)):
                c=original_relative_temp_nearest_writer_census(private["shdr"],private["cb"])
                independent=source_relative_CB_index_AST_census(private["shdr"],private["cb"])
                if (c.get("original_CB_true_relative_vec_index_occurrences",0)!=
                    independent.get("relative_original_CB_vec4_operand_occurrences",0)
                    or c.get("original_CB_operand_occurrences_in_supported_opcodes",0)!=
                    independent.get("covered_CB_operand_occurrences",0)
                    or c.get("supported_arithmetic_instruction_occurrences",0)!=
                    independent.get("covered_nine_opcode_instruction_occurrences",0)):
                    raise ValueError("GFX074_INDEPENDENT_GFX067_SOURCE_STAGE_COUNT_DISAGREEMENT")
                for k,v in c.items():total[k]+=v
                scanned+=1
                if not translated[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX074_AUTHENTIC_ORIGINAL_SOURCE_STAGE_VULKAN11_SPV_VALIDATION_FAILED")
                spv_total["source_original_stages_Vulkan11_SPV_validated"]+=1
                if not private["cb"]:
                    if c.get("original_CB_true_relative_vec_index_occurrences",0):
                        raise ValueError("GFX074_CB_FREE_STAGE_WITH_RELATIVE_ORIGINAL_SOURCE_CB")
                    spv_total["source_original_CB_free_stages"]+=1
                    continue
                spv=folder/(kind+".spv")
                ok,raw=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX074_PRIVATE_SPV_REFLECTION_FAILED")
                reflection=json.loads(raw.decode("utf8","strict"))
                if not isinstance(reflection,dict):
                    raise ValueError("GFX074_PRIVATE_SPV_REFLECTION_NOT_OBJECT")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX074_PRIVATE_SPV_DISASSEMBLY_FAILED")
                auth,layout=private_authenticated_ubo_layouts(dis,private["cb"],reflection)
                regs=global_cb_evidence(dis,private["cb"],reflection.get("ubos",[]))
                if (len(auth)!=len(private["cb"]) or
                    layout["UBO_globals_strict_single_vec4_array_member_layout"]!=len(private["cb"]) or
                    not regs["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"]):
                    raise ValueError("GFX074_ORIGINAL_CB_B_REAL_UNIFORM_GLOBAL_AND_VEC4_LAYOUT_FAILED")
                spv_total["authenticated_original_CB_source_stage_instances"]+=1
                outcome=shifted_source_spv_dynamic_UBO_reads(dis,auth)
                writer074=spv_index_local_store_candidates(dis,auth)
                shape075=authenticated_spv_CB_index_pointer_origins(dis,auth)
                path076=authenticated_spv_CB_index_address_path_stores(dis,auth)
                values077=authenticated_spv_CB_index_local_store_value_producers(dis,auth)
                audit078=authenticated_spv_CB_index_local_store_unknowns_and_cfg078(dis,auth)
                family079=authenticated_spv_CB_index_unknown_terminal_families079(dis,auth)
                int080=authenticated_spv_CB_index_unknown_integer_opcode_shapes080(dis,auth)
                in081=authenticated_spv_CB_index_imul_dynamic_operand081(dis,auth)
                writes082=authenticated_spv_CB_index_imul_input_load_writes082(dis,auth)
                producer083=authenticated_spv_CB_index_imul_input_writer_value083(dis,auth)
                inner084=authenticated_spv_CB_index_imul_input_writer_underlying084(dis,auth)
                ops085=authenticated_spv_CB_index_imul_input_writer_iadd_operands085(dis,auth)
                memory086=authenticated_spv_CB_index_imul_iadd_input_load_storage086(dis,auth)
                interface087=authenticated_spv_CB_index_iadd_load_interfaces087(dis,auth)
                provenance088=authenticated_spv_CB_index_iadd_source_provenance088(
                    dis,auth,private["shdr"],private["cb"])
                signature089=input_interface_source_semantic089(
                    dis,auth,private["shdr"],private["cb"],private["dxbc"],kind)
                actual090=authenticated_spv_CB_index_source_input_signature090(
                    dis,auth,private["shdr"],private["cb"],private["dxbc"],kind)
                mask091=authenticated_spv_CB_index_actual_input_component_width091(
                    dis,auth,private["shdr"],private["cb"],private["dxbc"],kind)
                if mask091.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=outcome.get(
                    "SPV_authenticated_dynamic_vec_OpLoad_occurrences",0):
                    raise ValueError("GFX091_AUTHENTIC_SPV_UBO_INDEX_READ_COUNT_DRIFT")
                for key,val in mask091.items():
                    if type(val) is int:
                        spv_total["GFX091_"+key]+=val

                if actual090.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=outcome.get(
                    "SPV_authenticated_dynamic_vec_OpLoad_occurrences",0):
                    raise ValueError("GFX090_ACTUAL_OPIADD_INPUT_AUTHENTIC_SPV_READ_COUNT_DRIFT")
                for key,val in actual090.items():
                    if type(val) is int:
                        spv_total["GFX090_"+key]+=val

                if (signature089.get("GFX089_previous_427_authenticated_source_CB_reads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX089_ORIGINAL_CB_AUTHENTICATED_SPV_READ_COUNT_DRIFT")
                for key,val in signature089.items():
                    if type(val) is int:
                        spv_total["GFX089_"+key]+=val

                if (provenance088.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX088_SOURCE_PRIVATE_SPV_INDEX_READ_COUNT_DRIFT")
                for key,val in provenance088.items():
                    if type(val) is int:
                        spv_total["GFX088_"+key]+=val

                if (interface087.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX087_AUTHENTIC_B_SPV_CB_READ_COUNT_DRIFT")
                for key,val in interface087.items():
                    if type(val) is int:
                        spv_total["GFX087_"+key]+=val

                if (memory086.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX086_AUTHENTIC_ORIGINAL_B_SPV_CB_INDEX_COUNT_DRIFT")
                for key,val in memory086.items():
                    if type(val) is int:
                        spv_total["GFX086_"+key]+=val

                if (ops085.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX085_ORIGINAL_B_SPV_INDEX_LOAD_ACCOUNTING_DRIFT")
                for key,val in ops085.items():
                    if type(val) is int:
                        spv_total["GFX085_"+key]+=val

                if (inner084.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX084_REAL_ORIGINAL_B_SPV_DYNAMIC_CB_COUNT_DRIFT")
                for key,val in inner084.items():
                    if type(val) is int:
                        spv_total["GFX084_"+key]+=val

                if (producer083.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX083_ORIGINAL_B_CB_SPV_LOADED_INDEX_COUNT_DRIFT")
                for key,val in producer083.items():
                    if type(val) is int:
                        spv_total["GFX083_"+key]+=val

                if (writes082.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX082_SPV_SOURCE_AUTHENTIC_CB_INDEX_COUNT_DRIFT")
                for key,val in writes082.items():
                    if type(val) is int:
                        spv_total["GFX082_"+key]+=val

                if (in081.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX081_AUTHENTIC_SPV_INDEX_CB_LOADS_DRIFT")
                for key,val in in081.items():
                    if type(val) is int:
                        spv_total["GFX081_"+key]+=val

                if (int080.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX080_REAL_CB_INDEX_OPLOAD_COUNT_DRIFT")
                for key,val in int080.items():
                    if type(val) is int:
                        spv_total["GFX080_"+key]+=val

                if (family079.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX079_PRIVATE_SPV_INDEX_LOAD_COUNT_DRIFT")
                for key,val in family079.items():
                    if type(val) is int:
                        spv_total["GFX079_"+key]+=val

                if (audit078.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX078_AUTHENTIC_CB_LOAD_COUNT_INCONSISTENT")
                for key,val in audit078.items():
                    if type(val) is int:
                        spv_total["GFX078_"+key]+=val

                if (values077.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX077_SPV_STORED_VALUE_REAL_INDEX_CB_LOAD_COUNT_DRIFT")
                for key,val in values077.items():
                    if type(val) is int:
                        spv_total["GFX077_"+key]+=val

                if (path076.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX076_ORIGINAL_B_SPV_NORMALIZED_ADDRESS_PATH_LOAD_COUNT_DRIFT")
                for key,val in path076.items():
                    if type(val) is int:
                        spv_total["GFX076_"+key]+=val

                if (shape075.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX075_PRIVATE_SPV_POINTER_ORIGIN_VS_REAL_LOADED_CB_COUNT_DRIFT")
                for key,val in shape075.items():
                    if type(val) is int:
                        spv_total["GFX075_"+key]+=val

                if writer074.get("SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences",0)!=outcome.get(
                    "SPV_authenticated_dynamic_vec_OpLoad_occurrences",0):
                    raise ValueError("GFX074_INDEPENDENT_AUTHENTIC_CB_DYNAMIC_LOAD_COUNT_DRIFT")
                for key,val in writer074.items():
                    if type(val) is int:
                        spv_total["GFX074_"+key]+=val

                # GFX074 precise private key: original b-register identity and
                # literal vec4 displacement, compared to actual loaded SPV
                # authenticated original b Uniform global, not to numeric b
                # guessed from SPIR-V descriptor binding alone.
                source_keys,source_key_stats=original_source_private_b_relative_offset_multiset(
                    private["shdr"],private["cb"])
                spv_keys,spv_key_stats=translated_spv_private_authenticated_b_relative_offset_multiset(
                    dis,auth)
                private_compare=compare_private_b_and_relative_literal_multisets(
                    source_keys,spv_keys)
                if (source_key_stats.get("source_relative_CB_index_keys_classified",0)!=
                    independent.get("relative_original_CB_vec4_operand_occurrences",0)
                    or spv_key_stats.get("SPV_authenticated_source_b_real_dynamic_UBO_vector_Load_occurrences",0)!=
                    outcome.get("SPV_authenticated_dynamic_vec_OpLoad_occurrences",0)):
                    raise ValueError("GFX074_SOURCE_OR_SPV_PRIVATE_DYNAMIC_INDEX_MULTIPLICITY_DRIFT")
                for k,v in private_compare.items():
                    if type(v) is int:
                        spv_total[k]+=v
                spv_total["source_stages_with_exact_private_original_b_and_literal_relative_offset_multiset_match"]+=int(
                    private_compare["private_stage_b_offset_shape_multiset_equal"])
                spv_total["source_stages_with_private_original_b_or_literal_relative_offset_multiset_mismatch"]+=int(
                    not private_compare["private_stage_b_offset_shape_multiset_equal"])
                spv_total["SPV_original_source_b_dynamic_index_loads_unclassified"]+=spv_key_stats.get(
                    "SPV_dynamic_UBO_index_shape_unclassified",0)
                # Per authentic original stage category count matching is stronger
                # than merely 350+77 overall, but NOT per-b/per-instruction parity.
                cmp=compare_private_stage_relative_source_to_spv_index_shapes(
                    independent.get("relative_representation_2",0),
                    independent.get("relative_representation_3",0),
                    outcome)
                for key,val in cmp.items():
                    if type(val) is bool and key.startswith("per_stage_"):
                        spv_total[key+"_success"]+=int(val)
                        spv_total[key+"_mismatch"]+=int(not val)
                old_spv=spv_authenticated_dynamic_cb_pointer_loads(dis,auth)
                for k,v in outcome.items():
                    if type(v) is int:
                        spv_total[k]+=v
                spv_total["GFX063_independent_SPV_authentic_UBO_dynamic_Load_occurrences"]+=old_spv[
                    "spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"]
                local=c.get("candidate_nearest_writer_original_opcode_41",0)
                if local:
                    spv_total["source_stage_instances_with_original_local_ISHL_writer_candidates"]+=1
                    spv_total["original_local_ISHL_writer_candidate_occurrences_in_checked_stages"]+=local
                    any_shift=(outcome["SPV_dynamic_vec_OpLoad_index_direct_shift"]+
                        outcome["SPV_dynamic_vec_OpLoad_index_via_shift_ancestor"]>0)
                    spv_total["original_local_ISHL_candidate_stages_with_independent_SPV_shifted_CB_loads"]+=int(any_shift)
                    spv_total["original_local_ISHL_candidate_stages_without_observed_SPV_shifted_CB_loads"]+=int(not any_shift)
    if (scanned!=314 or len(chosen)!=157 or
        total["original_CB_true_relative_vec_index_occurrences"]!=427 or
        total["original_CB_operand_occurrences_in_supported_opcodes"]!=7990 or
        total["supported_arithmetic_instruction_occurrences"]!=19847 or
        total["relative_source_temp_selected_component_syntax_valid"]!=427 or
        total["candidate_nearest_writer_original_opcode_41"]!=68 or
        total["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"]!=359 or
        spv_total["source_exact_VS_FS_pairs_translated"]!=157 or
        spv_total["source_original_stages_Vulkan11_SPV_validated"]!=314 or
        spv_total["source_original_CB_free_stages"]!=3 or
        spv_total["authenticated_original_CB_source_stage_instances"]!=311 or
        spv_total["original_local_ISHL_writer_candidate_occurrences_in_checked_stages"]!=68 or
        spv_total["GFX074_SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences"]!=427 or
        spv_total["GFX074_SPV_index_root_is_actual_OpLoad"]!=427 or
        spv_total["GFX075_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX075_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX076_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX076_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX077_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX077_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX077_SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"]!=128 or
        spv_total["GFX078_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX078_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX078_SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"]!=128 or
        spv_total["GFX078_SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"]!=47 or
        spv_total["GFX078_SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_unknown"]!=12 or
        spv_total["GFX079_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX079_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX079_SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_unknown"]!=12 or
        spv_total["GFX079_SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"]!=47 or
        spv_total["GFX080_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX080_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX080_SPV_sameblock_store_unknown_ancestry_terminal_integer_math"]!=12 or
        spv_total["GFX080_SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"]!=47 or
        spv_total["GFX081_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX081_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX081_SPV_unknown_integer_terminal_OpIMul_literal_shape_nonpower_of_two_literal"]!=12 or
        spv_total["GFX082_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX082_SPV_index_OpLoad_pointer_root_classified"]!=427 or
        spv_total["GFX082_SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"]!=12 or
        spv_total["GFX083_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX083_SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"]!=12 or
        spv_total["GFX083_SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_same_block_store_syntax"]!=12 or
        spv_total["GFX084_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX084_SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"]!=12 or
        spv_total["GFX084_SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_same_block_store_syntax"]!=12 or
        spv_total["GFX085_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX085_SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"]!=12 or
        spv_total["GFX086_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX086_SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"]!=12 or
        spv_total["GFX087_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX087_SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"]!=12 or
        spv_total["GFX088_SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]!=427 or
        spv_total["GFX088_SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"]!=12):
        raise ValueError("GFX075_SOURCE_AND_SPV_POINTER_ROOT_CENSUS_ACCOUNTING_DRIFT")
    if (spv_total["original_local_ISHL_candidate_stages_with_independent_SPV_shifted_CB_loads"]+
        spv_total["original_local_ISHL_candidate_stages_without_observed_SPV_shifted_CB_loads"]!=
        spv_total["source_stage_instances_with_original_local_ISHL_writer_candidates"]):
        raise ValueError("GFX074_SOURCE_STAGE_LEVEL_COEXISTENCE_PARTITION_DRIFT")
    return {
      "experiment":"GFX-MULTI-091","source_zip2_sha":ZIP2_SHA,
      "evidence_level":"ORIGINAL_SOURCE_TEMP_LOCAL_ISHL_PLUS_INDEPENDENT_SPV_DYNAMIC_CB_INDEX_ROOT_PRODUCER_OPCODE_TAXONOMY_NO_CROSS_LANGUAGE_SEMANTIC_EQUIVALENCE",
      "source_exact_original_VS_FS_pairs_censused":524,
      "source_unique_compiled_stages":len(cache),
      "original_source_pass_joint_representative_pairs":len(chosen),
      "original_source_stage_instances":scanned,
      "source_CB_relative_temp_local_candidates_safe_counts":dict(total),
      "independent_translated_SPV_authentic_UBO_shifted_dynamic_loads_safe_counts":dict(spv_total),
      "SPV_local_store_candidate_does_not_prove_source_DXBC_temp_or_CFG_dominance":True,
      "SPV_local_store_to_original_temp_SSA_value_proven":False,
      "GFX074_source_to_translated_same_instruction_and_index_value_proven":False,
      "source_stage_relative_index_root_shape_count_equality_means_same_individual_DXBC_operand":False,
      "private_source_b_and_literal_offset_multiset_count_equality_proves_temp_SSA_values":False,
      "private_source_b_and_literal_offset_multiset_equality_proves_instruction_bijection":False,
      "source_local_ISHL_stage_and_SPV_shifted_read_coexistence_establishes_same_operand_mapping":False,
      "source_original_ISHL_to_SPV_OpShiftLeftLogical_SSA_roots_proven":0,
      "original_427_relative_CB_source_uses_numeric_runtime_index_parity_proven":False,
      "all_524_original_variant_programs_semantically_equivalent":False,
      "original_Material_property_to_b_t_s_and_CB_member_byte_bridge_proven":False,
      "original_Shader48_Android_Adreno_GPU_pixels_verified":False,
      "originalShaderRestored":False,"phase_closed":False,
      "original_shader_temp_ID_DXBC_SPV_or_PPtr_exported":False
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
    print("GFX091_SAFE_ACTUAL_12_ISGN_MASK_COMPONENT_VS_SPV_INPUT_WIDTH_CLASSES "+json.dumps(d,sort_keys=True))

if __name__=="__main__": main()
