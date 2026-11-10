#!/usr/bin/env python3
"""GFX-MULTI-016: source Shader48 SHDR tokenized program declaration inventory.

Follows Microsoft D3D12TokenizedProgramFormat.hpp opcode and instruction-length
definitions. Only counts are emitted; NO private DXBC, register indices,
shader source, keywords, program-code, GUID/PPtr or names leave the CI runner.
Source CB/material semantics not proven by presence of declarations.
"""
from __future__ import annotations
import argparse,json,struct
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref

# Microsoft D3D10_SB_OPCODE_TYPE enum indexes (0-index, no explicit assignments
# before these opcodes), documented in DirectX-Headers TokenizedProgramFormat.
RESOURCE=88
CONSTBUFFER=89
SAMPLER=90
CUSTOMDATA=53
RAWRESOURCE=161
STRUCTUREDRESOURCE=162
COUNTS={RESOURCE:"dcl_resource",CONSTBUFFER:"dcl_constant_buffer",
        SAMPLER:"dcl_sampler",RAWRESOURCE:"dcl_resource_raw",
        STRUCTUREDRESOURCE:"dcl_resource_structured"}

def source_shader_chunk(dx):
    if not isinstance(dx,bytes) or len(dx)<36 or dx[:4]!=b"DXBC":
        raise ValueError("INVALID_ORIGINAL_DXBC_CONTAINER")
    total=struct.unpack_from("<I",dx,24)[0]
    count=struct.unpack_from("<I",dx,28)[0]
    if total!=len(dx) or count<1 or count>64 or 32+4*count>len(dx):
        raise ValueError("BAD_DXBC_CONTAINER_TABLE")
    stages=[]
    for i in range(count):
        offset=struct.unpack_from("<I",dx,32+4*i)[0]
        if offset+8>total:raise ValueError("DXBC_CHUNK_OFFSET_INVALID")
        size=struct.unpack_from("<I",dx,offset+4)[0]
        if offset+8+size>total:raise ValueError("DXBC_CHUNK_LENGTH_INVALID")
        tag=dx[offset:offset+4]
        if tag in (b"SHDR",b"SHEX"):stages.append(dx[offset+8:offset+8+size])
    if len(stages)!=1:raise ValueError("MISSING_OR_AMBIGUOUS_SHADER_STAGE_CHUNK")
    return stages[0]

def declaration_counts(blob):
    if not isinstance(blob,bytes) or len(blob)<12 or len(blob)%4:
        raise ValueError("BAD_SHDR_TOKENIZED_LENGTH")
    words=struct.unpack("<%dI"%(len(blob)//4),blob)
    declared=words[1]
    if declared!=len(words):raise ValueError("SHDR_DECLARED_PROGRAM_LENGTH_MISMATCH")
    cursor=2; counts=Counter()
    steps=0
    while cursor<len(words):
        token=words[cursor]
        opcode=token&0x7ff
        if opcode==CUSTOMDATA:
            if cursor+1>=len(words):raise ValueError("SHDR_CUSTOM_DATA_LENGTH_MISSING")
            length=words[cursor+1]
            if length<2:raise ValueError("SHDR_CUSTOM_DATA_INVALID_LENGTH")
            counts["custom_data_blocks"]+=1
        else:
            length=(token>>24)&0x7f
            if length<1:raise ValueError("SHDR_ZERO_INSTRUCTION_LENGTH")
        if cursor+length>len(words):
            raise ValueError("SHDR_INSTRUCTION_EXTENDS_PAST_SOURCE")
        if opcode in COUNTS:counts[COUNTS[opcode]]+=1
        cursor+=length
        steps+=1
        if steps>250000:raise ValueError("SHDR_UNREASONABLE_INSTRUCTION_COUNT")
    if cursor!=len(words):raise ValueError("SHDR_PROGRAM_NOT_EXHAUSTED")
    counts["total_instruction_tokens"]=steps
    counts["shader_token_dwords"]=len(words)
    return {k:int(counts[k]) for k in (*COUNTS.values(),"custom_data_blocks",
                                    "total_instruction_tokens","shader_token_dwords")}

def audit(stage):
    table,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("SHADER48_ORIGINAL_PASS_DRIFT")
    rows=[]
    for p in passes:
        if not p["pairs"]:raise ValueError("PASS_MISSING_EXACT_ORIGINAL_PAIR")
        vs,fs=p["pairs"][0]
        result={}
        for stage_name,meta,expected in (("vertex",vs,"Vertex"),("fragment",fs,"Pixel")):
            original=code_from_ref(meta,table,expected)
            result[stage_name]=declaration_counts(source_shader_chunk(original))
        rows.append({"subshader":p["subshader"],"pass":p["pass"],"source_declaration_counts":result,
                     "source_register_indexes_verified":False})
    alltotal=Counter()
    for row in rows:
        for c in row["source_declaration_counts"].values():
            for name,value in c.items():alltotal[name]+=value
    return {"experiment":"GFX-MULTI-016","source_sha":ZIP2_SHA,
        "source_shader_passes":7,"source_stages_examined":14,
        "source_declaration_totals":dict(alltotal),
        "per_pass":rows,
        "register_numbers_extracted":False,
        "source_material_to_shader_resource_parity":False,
        "source_cb_register_to_spirv_binding_parity":False,
        "original_shader_runtime_android_verified":False,
        "all_source_variants_examined":False,
        "proprietary_shader_bytes_exported":False,
        "stage_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI016_SAFE_SHDR_DECLARATION_COUNTS "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
