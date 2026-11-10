#!/usr/bin/env python3
"""GFX-MULTI-051: bounded authentic DXBC CB operand use versus SPIR-V UBO access.

All real DXBC, SPIR-V, source b# numbers, vector indices, material names and
member offsets remain in GitHub runner memory. Public output contains counts
and explicit limitations only. For source CB access this decoder covers 9
fixed-arity arithmetic opcodes; other instructions are UNKNOWN, not assumed to
have no CB usage. SPIR-V UBO matches rely ONLY on provisional numeric binding
coordinates. None proves true CB identity, member semantics, or GPU parity.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
import tempfile
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import operand, CUSTOMDATA, MAX_DWORDS, MAX_INST
from gfxlab.tools.multi_shader_original_cb_spv_blocksize import numeric_cb_coordinate_candidate
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

# D3D10 tokenized-format public opcode enum: ADD, DP2/3/4, MAD, MIN,
# MAX, MOV, MUL. Count includes a destination; includes only known formats.
KNOWN_ARITHMETIC_ARITY={0:3,15:3,16:3,17:3,50:4,51:3,52:3,54:2,56:3}
MAX_SPV_TEXT_BYTES=16*1024*1024
MAX_UBO_TYPES=2048
MAX_UBO_MEMBERS=4096
_SPV_ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")
_SPV_DECO=re.compile(r"^\s*OpDecorate\s+(%[0-9]+)\s+(Binding|DescriptorSet)\s+([0-9]+)\s*$")

def scan_known_dxbc_cb_operands(shdr,declared):
    """Partial source CB-use scan. Return private per-b# sets and safe counts."""
    if (not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)>MAX_DWORDS*4
        or len(shdr)%4 or not isinstance(declared,dict)):
        raise ValueError("GFX051_BAD_SOURCE_INPUT")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):
        raise ValueError("GFX051_DXBC_LENGTH_INVALID")
    if any(type(k) is not int or type(n) is not int or not 0<=k<=65535 or
           not 0<n<=65535 for k,n in declared.items()):
        raise ValueError("GFX051_BAD_ORIGINAL_CB_DECLARATION")
    per_cb={k:set() for k in declared}
    counts=Counter({
      "all_source_instructions":0,
      "recognized_fixed_arity_arithmetic_instructions":0,
      "noncovered_source_instructions":0,
      "recognized_arithmetic_parse_rejected":0,
      "source_CB_operands_seen_in_covered_arithmetic":0,
      "source_static_CB_vector_accesses_in_covered_arithmetic":0,
      "source_dynamic_or_extended_CB_accesses_in_covered_arithmetic":0,
      "source_CB_registers_seen_in_covered_arithmetic":0,
      "unique_static_CB_vec4_accesses_in_covered_arithmetic":0,
    })
    pos=2
    while pos<len(words):
        opword=words[pos];op=opword&2047
        if op==CUSTOMDATA:
            if pos+1>=len(words):raise ValueError("GFX051_CUSTOM_LENGTH_MISSING")
            ln=words[pos+1]
            if ln<2:raise ValueError("GFX051_CUSTOM_LENGTH_INVALID")
        else:
            ln=(opword>>24)&127
            if not ln:raise ValueError("GFX051_ZERO_LENGTH_OPCODE")
        end=pos+ln
        if end>len(words):raise ValueError("GFX051_OPCODE_OVERRUN")
        counts["all_source_instructions"]+=1
        if counts["all_source_instructions"]>MAX_INST:
            raise ValueError("GFX051_INSTRUCTION_LIMIT")
        if op in KNOWN_ARITHMETIC_ARITY:
            cursor=pos+1
            ex=bool(opword&0x80000000)
            extensions=0
            while ex:
                if cursor>=end or extensions>=4:
                    raise ValueError("GFX051_OPCODE_EXTENSION_INVALID")
                token=words[cursor];cursor+=1
                if (token&63) not in (0,1,2,3):
                    raise ValueError("GFX051_UNKNOWN_OPCODE_EXTENSION")
                ex=bool(token&0x80000000);extensions+=1
            operands=[]
            try:
                for _ in range(KNOWN_ARITHMETIC_ARITY[op]):
                    parsed,cursor=operand(words,cursor,end)
                    operands.append(parsed)
                if cursor!=end:
                    raise ValueError("GFX051_OPERAND_COUNT_MISMATCH")
            except ValueError:
                counts["recognized_arithmetic_parse_rejected"]+=1
            else:
                counts["recognized_fixed_arity_arithmetic_instructions"]+=1
                # destination may be a temporary or output, not CB. Scan
                # *source* operands only; any CB destination is an error.
                if operands[0]["type"]==8:
                    raise ValueError("GFX051_CB_OPERAND_AS_DESTINATION")
                for item in operands[1:]:
                    if item["type"]!=8:continue
                    counts["source_CB_operands_seen_in_covered_arithmetic"]+=1
                    idx=item["indices"]
                    if (item["dimension"]!=2 or item["dynamic"] or
                        item["extended"] or len(idx)!=2 or
                        type(idx[0]) is not int or type(idx[1]) is not int):
                        counts["source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"]+=1
                        continue
                    b,vec=idx
                    if b not in declared:raise ValueError("GFX051_UNDECLARED_SOURCE_CB_SLOT")
                    if not 0<=vec<declared[b]:
                        raise ValueError("GFX051_ORIGINAL_CB_VEC4_OUT_OF_RANGE")
                    per_cb[b].add(vec)
                    counts["source_static_CB_vector_accesses_in_covered_arithmetic"]+=1
        else:
            counts["noncovered_source_instructions"]+=1
        pos=end
    if pos!=len(words):raise ValueError("GFX051_SOURCE_TERMINATION")
    counts["source_CB_registers_seen_in_covered_arithmetic"]=sum(bool(v) for v in per_cb.values())
    counts["unique_static_CB_vec4_accesses_in_covered_arithmetic"]=sum(len(v) for v in per_cb.values())
    return per_cb,dict(counts)

def reflect_ubo_member_shapes(reflect,source_decls):
    """SPIR-V-Cross UBO *layout annotations*; no original property attribution."""
    if not isinstance(reflect,dict) or not isinstance(source_decls,dict):
        raise ValueError("GFX051_REFLECTION_WRONG_TYPE")
    rows=reflect.get("ubos",[]);types=reflect.get("types",{})
    if (not isinstance(rows,list) or not isinstance(types,dict) or
            len(rows)>MAX_UBO_TYPES or len(types)>MAX_UBO_TYPES):
        raise ValueError("GFX051_REFLECTION_BOUNDS")
    c=Counter({
        "spv_reflected_ubo_blocks":len(rows),
        "spv_ubo_blocks_with_type_metadata":0,
        "spv_reflected_members_with_explicit_offset":0,
        "spv_reflected_members_with_array_stride_16":0,
        "spv_reflected_members_with_non16_array_stride":0,
        "spv_reflected_members_without_offset":0,
        "spv_reflected_member_offsets_outside_block":0,
        "spv_reflected_types_unknown_or_malformed":0,
    })
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("GFX051_BAD_UBO_ROW")
        t=types.get(row.get("type"))
        if not isinstance(t,dict):
            c["spv_reflected_types_unknown_or_malformed"]+=1
            continue
        members=t.get("members")
        if not isinstance(members,list) or len(members)>MAX_UBO_MEMBERS:
            c["spv_reflected_types_unknown_or_malformed"]+=1
            continue
        c["spv_ubo_blocks_with_type_metadata"]+=1
        size=row.get("block_size")
        for member in members:
            if not isinstance(member,dict):
                raise ValueError("GFX051_BAD_MEMBER_LAYOUT_RECORD")
            off=member.get("offset")
            if type(off) is not int or off<0:
                c["spv_reflected_members_without_offset"]+=1
            else:
                c["spv_reflected_members_with_explicit_offset"]+=1
                if type(size) is int and off>=size:
                    c["spv_reflected_member_offsets_outside_block"]+=1
            stride=member.get("array_stride")
            if stride is not None:
                if type(stride) is not int or stride<=0:
                    raise ValueError("GFX051_BAD_SPV_MEMBER_ARRAY_STRIDE")
                c["spv_reflected_members_with_array_stride_16" if stride==16 else "spv_reflected_members_with_non16_array_stride"]+=1
    return {**dict(c),
            "original_CB_member_offset_identity_from_spirv_layout_proven":False,
            "original_CB_private_member_offsets_or_names_exported":False}

def spv_numeric_ubo_accesses(dis,source_decls):
    """Bounded SPIR-V resource-global UBO access chains via numeric candidates.

    Binding/set matching is provisional and cannot independently authenticate
    a source CB. Direct/propagated OpAccessChain and OpLoad use only; compiler
    can lower source access to many SPIR-V operations. Never call count parity.
    """
    if (not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES
         or not isinstance(source_decls,dict)):
        raise ValueError("GFX051_SPIRV_DISASSEMBLY_BAD")
    source=dis.decode("utf-8","strict")
    bindings={};sets={};globals_set=set()
    lines=source.splitlines()
    if len(lines)>300000:raise ValueError("GFX051_SPV_INSTRUCTION_LIMIT")
    for raw in lines:
        clean=raw.split(";",1)[0].strip()
        d=_SPV_DECO.fullmatch(clean)
        if d:
            id,kind,val=d.groups()
            target=bindings if kind=="Binding" else sets
            if id in target:raise ValueError("GFX051_DUPLICATE_SPV_DECORATION")
            target[id]=int(val)
        m=_SPV_ASSIGN.fullmatch(clean)
        if m and m.group(2)=="OpVariable":
            parts=(m.group(3) or "").split()
            if len(parts)>=2 and parts[1]=="Uniform":
                globals_set.add(m.group(1))
    origins={}
    unknown_ubo_global_candidates=0
    for id in globals_set:
        b=bindings.get(id);st=sets.get(id,0)
        if st==0 and type(b) is int and b in source_decls:
            origins[id]=b
        else:unknown_ubo_global_candidates+=1
    constants={}
    for raw in lines:
        m=_SPV_ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        target,op,tail=m.groups()
        parts=(tail or "").split()
        if op=="OpConstant" and len(parts)>=2 and re.fullmatch("[0-9]+",parts[1]):
            constants[target]=int(parts[1])
    counts=Counter({
        "spv_uniform_global_candidates_with_same_source_b_binding":len(origins),
        "spv_uniform_globals_without_candidate_source_b_binding":unknown_ubo_global_candidates,
        "spv_access_chains_from_numeric_ubo_global_candidates":0,
        "spv_access_chains_with_all_literal_indices":0,
        "spv_access_chains_with_nonliteral_indices":0,
        "spv_ubo_candidate_pointer_loads":0,
        "spv_access_chains_with_zero_struct_index_and_literal_vector_candidate":0,
    })
    vector_candidates={b:set() for b in source_decls}
    for raw in lines:
        m=_SPV_ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        target,op,tail=m.groups()
        parts=(tail or "").split()
        if op in ("OpAccessChain","OpInBoundsAccessChain"):
            if len(parts)<3 or parts[1] not in origins:continue
            b=origins[parts[1]]
            origins[target]=b
            counts["spv_access_chains_from_numeric_ubo_global_candidates"]+=1
            inds=[constants.get(x) for x in parts[2:]]
            if all(x is not None for x in inds):
                counts["spv_access_chains_with_all_literal_indices"]+=1
                if len(inds)>=2 and inds[0]==0 and inds[1]<source_decls[b]:
                    vector_candidates[b].add(inds[1])
                    counts["spv_access_chains_with_zero_struct_index_and_literal_vector_candidate"]+=1
            else:
                counts["spv_access_chains_with_nonliteral_indices"]+=1
        elif op=="OpLoad" and len(parts)>=2 and parts[1] in origins:
            counts["spv_ubo_candidate_pointer_loads"]+=1
        elif op=="OpCopyObject" and len(parts)>=2 and parts[1] in origins:
            origins[target]=origins[parts[1]]
    counts["spv_distinct_literal_vector_index_candidates"]=sum(len(v) for v in vector_candidates.values())
    return vector_candidates,{**dict(counts),
        "numeric_ubo_binding_proves_original_CB_identity":False,
        "spv_access_chain_count_equals_DXBC_source_operand_semantics":False,
        "spv_private_ubo_ids_or_vector_indices_exported":False}

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX051_EXACT_ORIGINAL_PASS_DRIFT")
    totals=Counter()
    perpass=[]
    for row in passes:
        vm,fm=row["pairs"][0]
        originals={"vertex":code_from_ref(vm,programs,"Vertex"),
                   "fragment":code_from_ref(fm,programs,"Pixel")}
        summary={}
        with tempfile.TemporaryDirectory(prefix="gfxlab051-private-") as temp:
            folder=Path(temp)
            converted=translate_pair(originals["vertex"],originals["fragment"],folder)
            for stage_name,src in originals.items():
                if not converted[stage_name]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX051_SPV_VALIDATION_FAILED")
                source_shdr=source_shader_chunk(src)
                src_cb=private_source_slots(source_shdr)[1]
                src_vectors,source_c=scan_known_dxbc_cb_operands(source_shdr,src_cb)
                spv=folder/(stage_name+".spv")
                ok,payload=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX051_SPIRV_REFLECTION_TOOL_FAILED")
                try:reflection=json.loads(payload.decode("utf-8","strict"))
                except (UnicodeDecodeError,ValueError):
                    raise ValueError("GFX051_SPIRV_REFLECTION_BAD_JSON") from None
                shape=reflect_ubo_member_shapes(reflection,src_cb)
                numeric=numeric_cb_coordinate_candidate(src_cb,reflection.get("ubos",[]))
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX051_SPIRV_DIS_TOOL_FAILED")
                candidate_vectors,spv_c=spv_numeric_ubo_accesses(dis,src_cb)
                # Never describe this as an identity proof. Only diagnose the
                # overlap between a known source subset and a candidate SPV
                # literal path under numeric b/descriptor alignment.
                same_vec=sum(len(a & candidate_vectors.get(b,set())) for b,a in src_vectors.items())
                source_only=sum(len(a - candidate_vectors.get(b,set())) for b,a in src_vectors.items())
                spv_only=sum(len(a - src_vectors.get(b,set())) for b,a in candidate_vectors.items())
                safe={
                    **source_c,**shape,**spv_c,
                    "numeric_b_binding_ubo_blocksize_candidate_complete":numeric["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"],
                    "source_subset_spirv_literal_vector_index_overlap_candidate_count":same_vec,
                    "source_subset_only_literal_vectors_not_observed_in_spv_candidate":source_only,
                    "spv_candidate_only_literal_vectors_not_observed_in_covered_source_opcodes":spv_only,
                    "all_DXBC_CB_opcodes_covered":False,
                    "original_Material_property_to_CB_member_offset_verified":False,
                    "source_CB_slot_to_SpirV_UBO_identity_independently_authenticated":False,
                }
                summary[stage_name]=safe
                totals["source_stages_compared"]+=1
                for key in ("recognized_fixed_arity_arithmetic_instructions",
                            "recognized_arithmetic_parse_rejected",
                            "source_static_CB_vector_accesses_in_covered_arithmetic",
                            "source_dynamic_or_extended_CB_accesses_in_covered_arithmetic",
                            "unique_static_CB_vec4_accesses_in_covered_arithmetic",
                            "spv_access_chains_from_numeric_ubo_global_candidates",
                            "spv_access_chains_with_zero_struct_index_and_literal_vector_candidate",
                            "spv_ubo_candidate_pointer_loads",
                            "source_subset_spirv_literal_vector_index_overlap_candidate_count",
                            "source_subset_only_literal_vectors_not_observed_in_spv_candidate",
                            "spv_candidate_only_literal_vectors_not_observed_in_covered_source_opcodes",
                            "spv_reflected_members_with_explicit_offset",
                            "spv_reflected_members_with_array_stride_16"):
                    totals[key]+=safe[key]
                totals["stages_numeric_b_and_block_size_candidate_complete"]+=int(safe["numeric_b_binding_ubo_blocksize_candidate_complete"])
        perpass.append({"subshader_public_position":row["subshader"],
                        "pass_public_position":row["pass"],
                        "stage_safe_CB_access_shapes":summary})
    if len(perpass)!=7 or totals["source_stages_compared"]!=14:
        raise ValueError("GFX051_ORIGINAL_STAGE_ACCOUNTING")
    return {
        "experiment":"GFX-MULTI-051",
        "original_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_PARTIAL_DXBC_CB_OPERANDS_AND_SPIRV_UBO_NUMERIC_CANDIDATE_ACCESS_SHAPES_CPU_ONLY",
        "original_shader48_source_passes":7,
        "original_exact_matched_keyword_tier_pairs_selected":7,
        "authentic_stages_compared":14,
        "fixed_arity_source_arithmetic_opcodes_covered":len(KNOWN_ARITHMETIC_ARITY),
        "safe_aggregate":dict(totals),
        "per_pass":perpass,
        "full_original_DXBC_CB_instruction_access_coverage":False,
        "original_CB_member_layout_independently_proven":False,
        "SPIRV_numeric_descriptor_binding_is_independent_original_CB_identity":False,
        "Material_original_property_to_b_register_mapping_proven":False,
        "all_524_original_variants_covered":False,
        "originalShaderRestored":False,
        "real_Shader48_Android_GPU_verified":False,
        "original_PC_to_Adreno_pixel_parity_proven":False,
        "private_shader_bytes_b_registers_vector_indices_UBO_names_or_offsets_exported":False,
        "phase_closed":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX051_SAFE_PARTIAL_CB_ACCESS_AND_SPV_UBO_CANDIDATE_SHAPES "+json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
