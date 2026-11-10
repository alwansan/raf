#!/usr/bin/env python3
"""GFX-MULTI-017: strict original DXBC DCL source operand index shape.

No original shader binary, register slot values, CB sizes, keywords,
material IDs, GUID/PPtrs or source code leave ephemeral runner. Report only
counts, booleans, and errors for resource-operand parsing.

Based on Microsoft D3D12TokenizedProgramFormat.hpp D3D10 SB operand format.
This is source register decoding, NOT register-to-SPIR-V or material mapping.
"""
import argparse,json,struct
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk

# D3D10_SB_OPCODE_DCL_RESOURCE=88, _CONSTANT_BUFFER=89, _SAMPLER=90
# OperandToken0: type bits [19:12], index-dim [21:20], index representation
# for dimension i at [22+3i:24+3i] (0=immediate32).
DECL={88:("resource",7,1),89:("constant_buffer",8,2),90:("sampler",6,1)}

def declaration_operand(opcode,words):
    if opcode not in DECL:raise ValueError("UNKNOWN_DCL_OPCODE")
    family,expected_type,dim=DECL[opcode]
    if len(words)<2:raise ValueError("MISSING_DCL_OPERAND")
    # These source DCL forms have one non-extended operand.
    head=words[1]
    if head&0x80000000:raise ValueError("EXTENDED_OPERAND_UNSUPPORTED")
    got_type=(head>>12)&0xff
    got_dim=(head>>20)&3
    if got_type!=expected_type:raise ValueError("WRONG_DCL_OPERAND_TYPE")
    if got_dim!=dim:raise ValueError("WRONG_DCL_INDEX_DIMENSION")
    if len(words)<2+dim:raise ValueError("TRUNCATED_DCL_IMMEDIATE_INDICES")
    for i in range(dim):
        representation=(head>>(22+3*i))&7
        if representation!=0:raise ValueError("NON_IMMEDIATE_DCL_INDEX_UNVERIFIED")
    indexes=tuple(words[2:2+dim])
    # Values returned only to private local Python, never serialized.
    return family,indexes

def scan_declarations(blob):
    if not isinstance(blob,bytes) or len(blob)<12 or len(blob)%4:raise ValueError("SHDR_BAD_LENGTH")
    words=struct.unpack("<%dI"%(len(blob)//4),blob)
    if words[1]!=len(words):raise ValueError("SHDR_PROGRAM_LENGTH_MISMATCH")
    idx=2
    slots={"constant_buffer":set(),"resource":set(),"sampler":set()}
    decl=Counter();duplicated=Counter();seen_cb_sizes=set()
    while idx<len(words):
        token=words[idx]
        opcode=token&2047
        if opcode==53:
            if idx+1>=len(words):raise ValueError("CUSTOM_LENGTH_MISSING")
            step=words[idx+1]
            if step<2:raise ValueError("BAD_CUSTOM_LENGTH")
        else:
            step=(token>>24)&127
            if not step:raise ValueError("SOURCE_ZERO_INSTRUCTION_LENGTH")
        if idx+step>len(words):raise ValueError("SOURCE_TOKEN_OVERRUN")
        if opcode in DECL:
            family,indexes=declaration_operand(opcode,words[idx:idx+step])
            slot=indexes[0]
            decl[family]+=1
            if slot in slots[family]:duplicated[family]+=1
            slots[family].add(slot)
            if family=="constant_buffer":
                if indexes[1]>0:seen_cb_sizes.add(slot)
        idx+=step
    if idx!=len(words):raise ValueError("SHDR_INSTRUCTION_TERMINATION_MISMATCH")
    result={}
    for fam in ("constant_buffer","resource","sampler"):
        result[fam+"_declarations"]=decl[fam]
        result[fam+"_distinct_register_slots"]=len(slots[fam])
        result[fam+"_duplicate_slot_declarations"]=duplicated[fam]
    result["constant_buffers_with_nonzero_declaration_size"]=len(seen_cb_sizes)
    result["source_register_numbers_exported"]=False
    result["original_register_to_spirv_descriptor_equivalence_verified"]=False
    return result

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("AUTHENTIC_SOURCE_PASS_COUNT_DRIFT")
    rows=[]
    for p in passes:
        if not p["pairs"]:raise ValueError("SOURCE_STAGE_PAIR_MISSING")
        v,f=p["pairs"][0]
        row={}
        for which,meta,kind in (("vertex",v,"Vertex"),("fragment",f,"Pixel")):
            original=code_from_ref(meta,programs,kind)
            row[which]=scan_declarations(source_shader_chunk(original))
        rows.append({"subshader":p["subshader"],"pass":p["pass"],"stages":row})
    total=Counter()
    for p in rows:
        for source in p["stages"].values():
            for k,val in source.items():
                if isinstance(val,int) and not isinstance(val,bool):total[k]+=val
    return {"experiment":"GFX-MULTI-017","source_sha":ZIP2_SHA,
        "source_shader_passes":7,"source_program_stages":14,
        "original_private_register_shape_counts":dict(total),
        "per_pass":rows,
        "original_dxbc_register_indexes_extracted_privately":True,
        "original_register_indexes_or_sizes_published":False,
        "source_material_texture_slot_identity_mapped":False,
        "original_cb_byte_offsets_matched_to_spirv":False,
        "original_sampler_semantics_matched":False,
        "android_original_shader_tested":False,"phase_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI017_SAFE_SOURCE_REGISTER_SHAPE "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
