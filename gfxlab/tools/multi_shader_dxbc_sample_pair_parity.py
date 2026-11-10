#!/usr/bin/env python3
"""GFX-MULTI-047: independent authentic DXBC sampling opcode resource/sampler use.

Decodes bounded Microsoft D3D10/11 tokenized SHDR operands directly. Compares
private t/s pair multisets with independently disassembled vkd3d-lowered SPIR-V
from exactly matched Shader48 keyword/tier pairs. No proprietary source,
register slots, pair tuples, code, identifiers or shaders are exported.
Source-stage/tier, original Material property mapping, CB byte layout, and
Windows-vs-Adreno runtime pixels are separate open gates.
"""
from __future__ import annotations
import argparse
import json
import struct
import tempfile
import re
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair, code_from_ref, translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_spirv_sample_use import (
    resource_variable_ids, spv_sample_use, ASSIGN, SAMPLE_PREFIX, GATHER
)
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

# Microsoft D3D12TokenizedProgramFormat.hpp / Wine vkd3d tpf.c opcode table.
# Value: (resource source-operand index, sampler source-operand index,
#         total source operand count), excluding exactly one destination.
SAMPLE_LAYOUTS={
    0x45:(1,2,3),  # sample
    0x46:(1,2,4),  # sample_c
    0x47:(1,2,4),  # sample_c_lz
    0x48:(1,2,4),  # sample_l
    0x49:(1,2,5),  # sample_d
    0x4a:(1,2,4),  # sample_b
    0x6d:(1,2,3),  # gather4
    0x7e:(1,2,4),  # gather4_c
    0x7f:(2,3,4),  # gather4_po: coords, offset, tex, sampler
    0x80:(2,3,5),  # gather4_po_c
}
CUSTOMDATA=53
MAX_DWORDS=2_000_000
MAX_INST=300_000
MAX_OPERAND_DEPTH=4
MAX_EXTENDED_TOKENS=4
MAX_SOURCE_OPERANDS=12

def operand(words,pos,end,depth=0):
    """Read one entire D3D10 operand including chained modifiers and indices."""
    if pos>=end or depth>MAX_OPERAND_DEPTH:
        raise ValueError("GFX047_OPERAND_TRUNCATED_OR_NESTING")
    token=words[pos];pos+=1
    typ=(token>>12)&0xff
    dim=(token>>20)&3
    components=token&3
    if components==3:
        raise ValueError("GFX047_UNSUPPORTED_N_COMPONENT_OPERAND")
    extended=bool(token&0x80000000)
    extensions=0
    while extended:
        if pos>=end or extensions>=MAX_EXTENDED_TOKENS:
            raise ValueError("GFX047_OPERAND_EXTENSION_BAD")
        extra=words[pos];pos+=1
        # Extended source modifiers and min precision are structurally bounded.
        if (extra&63) not in (0,1,2,3):
            raise ValueError("GFX047_OPERAND_EXTENSION_TYPE_UNKNOWN")
        extended=bool(extra&0x80000000)
        extensions+=1
    indices=[]
    dynamic=False
    for dimension in range(dim):
        kind=(token>>(22+3*dimension))&7
        if kind==0:
            if pos>=end:raise ValueError("GFX047_IMMEDIATE32_INDEX_TRUNCATED")
            indices.append(words[pos]);pos+=1
        elif kind==1:
            if pos+2>end:raise ValueError("GFX047_IMMEDIATE64_INDEX_TRUNCATED")
            indices.append((words[pos]<<32)|words[pos+1]);pos+=2
        elif kind in (2,3,4):
            dynamic=True
            if kind in (3,4):
                size=1 if kind==3 else 2
                if pos+size>end:raise ValueError("GFX047_RELATIVE_BASE_TRUNCATED")
                pos+=size
            _,pos=operand(words,pos,end,depth+1)
            indices.append(None)
        else:
            raise ValueError("GFX047_OPERAND_INDEX_REP_UNSUPPORTED")
    if typ in (4,5):
        if components not in (1,2):
            raise ValueError("GFX047_IMMEDIATE_OPERAND_COMPONENTS_UNSUPPORTED")
        size=(1 if components==1 else 4)*(1 if typ==4 else 2)
        if pos+size>end:raise ValueError("GFX047_IMMEDIATE_VALUE_TRUNCATED")
        pos+=size
    return {"type":typ,"dimension":dim,"indices":tuple(indices),
            "dynamic":dynamic,"extended":extensions>0},pos

def _slot(op,want):
    if op["type"]!=want:
        raise ValueError("GFX047_SAMPLE_RESOURCE_OR_SAMPLER_WRONG_TYPE")
    if op["dynamic"] or op["extended"] or op["dimension"]!=1 or len(op["indices"])!=1:
        return None
    x=op["indices"][0]
    if type(x) is not int or not 0<=x<=65535:
        return None
    return x

def original_sample_pairs(shdr,original_resource,original_samplers):
    """Return private pair multiset and counts; caller must never serialize pairs."""
    if not isinstance(shdr,bytes) or not 12<=len(shdr)<=MAX_DWORDS*4 or len(shdr)%4:
        raise ValueError("GFX047_SHDR_INVALID_BYTES")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):
        raise ValueError("GFX047_SHDR_DECLARED_LENGTH_INVALID")
    cursor=2;steps=0; pairs=[];unresolved=0; sample_count=0
    per_kind=Counter()
    while cursor<len(words):
        tok=words[cursor];opcode=tok&0x7ff
        if opcode==CUSTOMDATA:
            if cursor+1>=len(words):raise ValueError("GFX047_CUSTOMDATA_LENGTH_ABSENT")
            length=words[cursor+1]
            if length<2:raise ValueError("GFX047_CUSTOMDATA_SHORT")
        else:
            length=(tok>>24)&127
            if length<1:raise ValueError("GFX047_INSTRUCTION_ZERO_LENGTH")
        end=cursor+length
        if end>len(words):raise ValueError("GFX047_INSTRUCTION_OVERRUN")
        if opcode in SAMPLE_LAYOUTS:
            ri,si,nsrc=SAMPLE_LAYOUTS[opcode]
            pos=cursor+1
            ext=bool(tok&0x80000000)
            extra_count=0
            while ext:
                if pos>=end or extra_count>=MAX_EXTENDED_TOKENS:
                    raise ValueError("GFX047_EXTENDED_OPCODE_INVALID")
                nxt=words[pos];pos+=1
                if (nxt&63) not in (0,1,2,3):
                    raise ValueError("GFX047_EXTENDED_OPCODE_TYPE_UNKNOWN")
                ext=bool(nxt&0x80000000)
                extra_count+=1
            dest,pos=operand(words,pos,end)
            if nsrc>MAX_SOURCE_OPERANDS:
                raise ValueError("GFX047_SAMPLE_SOURCE_ARITY_UNSAFE")
            src=[]
            for _ in range(nsrc):
                o,pos=operand(words,pos,end);src.append(o)
            if pos!=end:
                raise ValueError("GFX047_SAMPLE_OPERAND_TERMINATION_MISMATCH")
            # Sample opcodes have an actual destination. Its type is output/temp/null.
            if dest["type"] in (6,7):
                raise ValueError("GFX047_SAMPLE_DEST_RESOURCE_TYPE")
            t=_slot(src[ri],7)
            s=_slot(src[si],6)
            if t is not None and t not in original_resource:
                raise ValueError("GFX047_UNDECLARED_TEXTURE_SOURCE_REGISTER")
            if s is not None and s not in original_samplers:
                raise ValueError("GFX047_UNDECLARED_SAMPLER_SOURCE_REGISTER")
            sample_count+=1
            per_kind["gather" if opcode in (0x6d,0x7e,0x7f,0x80) else "sample"]+=1
            if t is None or s is None:
                unresolved+=1
            else:pairs.append((t,s))
        cursor=end;steps+=1
        if steps>MAX_INST:raise ValueError("GFX047_ORIGINAL_INSTRUCTIONS_UNBOUNDED")
    if cursor!=len(words) or len(pairs)+unresolved!=sample_count:
        raise ValueError("GFX047_SOURCE_SAMPLING_ACCOUNTING")
    return pairs,{"source_sample_or_gather_operations":sample_count,
                  "source_original_immediate_t_s_pairs":len(pairs),
                  "source_original_unresolved_dynamic_t_s":unresolved,
                  "source_distinct_pairs_within_stage":len(set(pairs)),
                  "original_sample_ops":per_kind["sample"],
                  "original_gather_ops":per_kind["gather"],
                  "source_instruction_count":steps}

def private_spirv_sample_pairs(dis,resources,samplers):
    """Private exact SPIR-V direct-use sample pairs (never exported)."""
    if not isinstance(dis,bytes) or len(dis)>16*1024*1024:
        raise ValueError("GFX047_SPIRV_DISASSEMBLY_BOUNDS")
    text=dis.decode("utf-8","strict")
    names={**resources,**samplers}
    loaded={};sampled={};seen=set();pairs=[];unresolved=0
    for raw in text.splitlines():
        m=ASSIGN.match(raw.split(";",1)[0].strip())
        if not m:continue
        dst,op,rest=m.groups()
        if dst in seen:raise ValueError("GFX047_SPIRV_DUPLICATE_RESULT_ID")
        seen.add(dst)
        args=(rest or "").split()
        if op=="OpLoad" and len(args)>=2 and args[1] in names:
            loaded[dst]=names[args[1]]
        elif op=="OpCopyObject" and len(args)>=2:
            if args[1] in loaded:loaded[dst]=loaded[args[1]]
            if args[1] in sampled:sampled[dst]=sampled[args[1]]
        elif op=="OpSampledImage" and len(args)>=3:
            image=loaded.get(args[1]);sampler=loaded.get(args[2])
            if image and sampler and image[0]=="resource" and sampler[0]=="sampler":
                sampled[dst]=(image[1],sampler[1])
        if op.startswith(SAMPLE_PREFIX) or op in GATHER:
            if len(args)>=2 and args[1] in sampled:pairs.append(sampled[args[1]])
            else:unresolved+=1
    return pairs,unresolved

def stage_compare(source_bytes,spv,reflect,dis):
    source_blob=source_shader_chunk(source_bytes)
    source_slots,_=private_source_slots(source_blob)
    res=resource_variable_ids(source_slots["resource"],reflect.get("separate_images",[]),"resource",dis)
    samp=resource_variable_ids(source_slots["sampler"],reflect.get("separate_samplers",[]),"sampler",dis)
    source_pairs,src_counts=original_sample_pairs(
        source_blob,source_slots["resource"],source_slots["sampler"])
    trans_pairs,trans_unresolved=private_spirv_sample_pairs(dis,res,samp)
    translated=spv_sample_use(dis,res,samp)
    if (len(trans_pairs)!=translated["sample_or_gather_with_strict_t_s_pair"]
            or trans_unresolved!=translated["sample_or_gather_unresolved"]):
        raise ValueError("GFX047_TRANSLATED_COUNTER_RECONCILIATION_FAILED")
    match=Counter(source_pairs)==Counter(trans_pairs)
    return {
      **src_counts,
      "translated_sample_or_gather_operations":translated["sample_or_gather_operations"],
      "translated_sample_or_gather_strict_pairs":len(trans_pairs),
      "translated_unresolved_dynamic_pairs":trans_unresolved,
      "same_exact_private_original_DXBC_t_s_pair_multiset_as_translated_SPIRV":match and src_counts["source_original_unresolved_dynamic_t_s"]==0 and trans_unresolved==0,
      "original_to_translated_pair_count_delta":abs(len(source_pairs)-len(trans_pairs)),
      "private_source_t_s_pair_edges_or_register_ids_exported":False,
      "original_Material_TexEnv_property_register_binding_verified":False,
      "original_constant_buffer_offsets_verified":False,
      "original_shader48_Android_execution_verified":False,
    }

def audit(stage):
    table,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX047_EXACT_SEVEN_PASS_LINK_MISSING")
    rows=[];totals=Counter()
    for passrow in passes:
        vs,fs=passrow["pairs"][0]
        originals={"vertex":code_from_ref(vs,table,"Vertex"),
                   "fragment":code_from_ref(fs,table,"Pixel")}
        with tempfile.TemporaryDirectory(prefix="gfxlab-047-private-dxbc-pairs-") as tmp:
            folder=Path(tmp)
            converted=translate_pair(originals["vertex"],originals["fragment"],folder)
            row={"subshader_public_position":passrow["subshader"],
                 "pass_public_position":passrow["pass"],"stages":{}}
            for kind in ("vertex","fragment"):
                if not converted[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX047_TRANSLATED_SPIRV_VALIDATION_FAILED")
                spv=folder/(kind+".spv")
                ok,b=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX047_REFLECTION_FAILED")
                try:ref=json.loads(b.decode("utf8"))
                except (ValueError,UnicodeDecodeError):
                    raise ValueError("GFX047_REFLECTION_INVALID") from None
                if not isinstance(ref,dict):
                    raise ValueError("GFX047_REFLECTION_NOT_OBJECT")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX047_SPIRV_DISASSEMBLE_FAILED")
                stat=stage_compare(originals[kind],spv,ref,dis)
                row["stages"][kind]=stat
                totals["stages_compared"]+=1
                totals["source_sample_ops"]+=stat["source_original_immediate_t_s_pairs"]
                totals["source_unresolved"]+=stat["source_original_unresolved_dynamic_t_s"]
                totals["translated_sample_ops"]+=stat["translated_sample_or_gather_strict_pairs"]
                totals["translated_unresolved"]+=stat["translated_unresolved_dynamic_pairs"]
                totals["stages_matching_exact_private_pair_multiset"]+=int(
                    stat["same_exact_private_original_DXBC_t_s_pair_multiset_as_translated_SPIRV"])
            rows.append(row)
    if len(rows)!=7 or totals["stages_compared"]!=14:
        raise ValueError("GFX047_STAGE_ACCOUNTING_INVALID")
    return {
      "experiment":"GFX-MULTI-047",
      "source_zip2_sha":ZIP2_SHA,
      "source_independent_original_DXBC_instruction_operand_parser":True,
      "exact_matched_original_keyword_hardware_tier_pairs":7,
      "original_shader48_passes":7,
      "source_stages_compared":14,
      "pass_and_stage_aggregate_only":rows,
      "comparison_counts":dict(totals),
      "all_14_stages_exact_private_pair_multiset_equivalent":totals["stages_matching_exact_private_pair_multiset"]==14 and totals["source_unresolved"]==0 and totals["translated_unresolved"]==0,
      "all_524_variants_checked":False,
      "original_Material_property_to_DX11_resource_register_bridge_proven":False,
      "original_constant_buffer_byte_offsets_proven":False,
      "original_Android_shader48_GPU_runtime_proven":False,
      "PC_to_Adreno_original_pixel_equivalence_proven":False,
      "originalShaderRestored":False,
      "phase_closed":False,
      "private_source_names_registers_SPIRV_ids_code_or_sample_pairs_published":False,
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
    print("GFX047_SAFE_ORIGINAL_DXBC_SAMPLE_PAIR_PARITY "+json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
