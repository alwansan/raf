#!/usr/bin/env python3
"""T3 bounded SHA-original Particle108 SHDR/SHEX declaration-opcode census.

RDEF is absent in all eight selected original DXBC stage containers (proven by
CI 42258686807). D3D10/11 tokenized program declaration opcodes may still
provide evidence of SRV, sampler and constant-buffer roles. Never publish
program bytes, opcode operands, register numbers, GUIDs or private identities.
Opcode numbers, opcode-length fields and shader version follow the public
D3D10/D3D11 tokenized program specification (Microsoft DirectX-Headers).
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

from scripts import t3_particle108_original_dxbc_rdef as native

STATUS="T3_SHA_ORIGINAL_PARTICLE108_EIGHT_STAGE_DXBC_DECLARATIONS"
MAX_BYTES=4*1024*1024
MAX_CHUNKS=64
MAX_WORDS=MAX_BYTES//4
DECLARATION_FAMILIES={
    88:"srv", 89:"cbuffer", 90:"sampler",
    156:"uav",157:"uav",158:"uav",
    161:"srv",162:"srv",
}
CUSTOMDATA=53
SAFE_REASONS={
    "DXBC_DECL_CONTAINER":"SOURCE_CONTAINER",
    "DXBC_DECL_CHUNK_TABLE":"CHUNK_TABLE",
    "DXBC_DECL_CHUNK_OFFSET":"CHUNK_OFFSET",
    "DXBC_DECL_CHUNK_SIZE":"CHUNK_SIZE",
    "DXBC_DECL_CHUNK_OVERLAP":"CHUNK_OVERLAP",
    "DXBC_DECL_CODE_CHUNK_CARDINALITY":"SHDR_SHEX_CARDINALITY",
    "DXBC_DECL_PROGRAM_WORD_ALIGNMENT":"TOKEN_ALIGNMENT",
    "DXBC_DECL_PROGRAM_LENGTH":"TOKEN_LENGTH",
    "DXBC_DECL_PROGRAM_STAGE":"TOKEN_STAGE",
    "DXBC_DECL_OPCODE_LENGTH":"OPCODE_LENGTH",
    "DXBC_DECL_OPCODE_OVERRUN":"OPCODE_OVERRUN",
    "DXBC_DECL_CUSTOMDATA_LENGTH":"CUSTOMDATA_LENGTH",
    "original_authored_Shader48_props_changed":"SOURCE_SHADER_SCOPE",
    "original_paired_DXBC_shader_structure_changed":"SOURCE_PAIR_SCOPE",
}

def _word(b,off):
    if off<0 or off+4>len(b):
        raise ValueError("DXBC_DECL_CONTAINER")
    return struct.unpack_from("<I",b,off)[0]

def shader_chunk(dx):
    """Return ephemeral tokenized source program chunk from exactly one DXBC chunk."""
    if (type(dx) is not bytes or not 36<=len(dx)<=MAX_BYTES or
        dx[:4]!=b"DXBC" or _word(dx,24)!=len(dx)):
        raise ValueError("DXBC_DECL_CONTAINER")
    count=_word(dx,28)
    table_end=32+4*count
    if not 1<=count<=MAX_CHUNKS or table_end>len(dx):
        raise ValueError("DXBC_DECL_CHUNK_TABLE")
    spans=[]
    code=[]
    for i in range(count):
        off=_word(dx,32+4*i)
        if off<table_end or off+8>len(dx):
            raise ValueError("DXBC_DECL_CHUNK_OFFSET")
        size=_word(dx,off+4)
        end=off+8+size
        if size>MAX_BYTES or end>len(dx):
            raise ValueError("DXBC_DECL_CHUNK_SIZE")
        if any(off<previous_end and previous_start<end
               for previous_start,previous_end in spans):
            raise ValueError("DXBC_DECL_CHUNK_OVERLAP")
        spans.append((off,end))
        if dx[off:off+4] in (b"SHDR",b"SHEX"):
            code.append(dx[off+8:end])
    if len(code)!=1:
        raise ValueError("DXBC_DECL_CODE_CHUNK_CARDINALITY")
    return code[0]

def stage_declaration_counts(dx,expected_shader_stage):
    """Strict instruction scan; return only source-public aggregate categories.

    expected_shader_stage: 0 pixel, 1 vertex (D3D10_SB_TOKENIZED_PROGRAM_TYPE).
    This counts declarations, not unique bound registers, array ranges, or
    translated Vulkan/Android descriptors.
    """
    code=shader_chunk(dx)
    if len(code)<8 or len(code)%4:
        raise ValueError("DXBC_DECL_PROGRAM_WORD_ALIGNMENT")
    words=struct.unpack("<"+"I"*(len(code)//4),code)
    if len(words)>MAX_WORDS or words[1]!=len(words):
        raise ValueError("DXBC_DECL_PROGRAM_LENGTH")
    stage=(words[0]>>16)&0xffff
    if type(expected_shader_stage) is not int or stage!=expected_shader_stage:
        raise ValueError("DXBC_DECL_PROGRAM_STAGE")
    tally=Counter()
    i=2
    while i<len(words):
        token=words[i]
        opcode=token&0x7ff
        if opcode==CUSTOMDATA:
            if i+1>=len(words):
                raise ValueError("DXBC_DECL_CUSTOMDATA_LENGTH")
            length=words[i+1]
            if length<2:
                raise ValueError("DXBC_DECL_CUSTOMDATA_LENGTH")
            tally["original_customdata_blocks"]+=1
        else:
            length=(token>>24)&0x7f
            if length==0:
                raise ValueError("DXBC_DECL_OPCODE_LENGTH")
        if length>len(words)-i:
            raise ValueError("DXBC_DECL_OPCODE_OVERRUN")
        tally["original_tokenized_instructions"]+=1
        if opcode in DECLARATION_FAMILIES:
            tally["original_dcl_"+DECLARATION_FAMILIES[opcode]+"_instructions"]+=1
        i+=length
    tally["original_tokenized_shader_stages"]+=1
    return tally

def classify_original_pairs(pairs):
    if (type(pairs) is not list or len(pairs)!=4 or
        any(type(pair) is not tuple or len(pair)!=2 for pair in pairs)):
        raise ValueError("ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED")
    tally=Counter()
    for vertex,fragment in pairs:
        tally.update(stage_declaration_counts(vertex,1))
        tally.update(stage_declaration_counts(fragment,0))
        tally["original_source_vertex_fragment_keyword_pairs"]+=1
    if tally["original_tokenized_shader_stages"]!=8:
        raise ValueError("DXBC_DECL_PROGRAM_LENGTH")
    for family in set(DECLARATION_FAMILIES.values()):
        tally.setdefault("original_dcl_"+family+"_instructions",0)
    return {"schema_version":1,"status":STATUS,"counts":dict(sorted(tally.items())),
        "declaration_count_is_not_register_binding_layout":True,
        "original_binding_register_numbers_names_shader_bytes_or_GUIDs_published":False,
        "original_shader_program_Android_pixels_or_Unity_shader_compilation_proven":False,
        "original_vulkan_descriptor_equivalence_proven":False}

def probe(root,manifest):
    import UnityPy
    source_slots={}
    source_result=native.identity.source.load_original(
        root,manifest,private_particle_slot_counts=source_slots)
    owner,pid=native.identity.select(source_slots,source_result)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or native.fingerprint(path)!=native.SHADER_OWNERS[owner]:
        raise ValueError("SOURCE_PARTICLE_OWNER_SHA")
    objs=[o for o in UnityPy.load(str(path)).file.objects.values()
          if o.path_id==pid]
    if len(objs)!=1 or objs[0].type.name!="Shader":
        raise ValueError("SOURCE_SHADER_OBJECT_IDENTITY")
    tree=objs[0].read_typetree()
    props,shape=native.serialize_properties(tree["m_ParsedForm"])
    if shape["original_authored_property_count"]!=13 or shape["original_authored_texture_property_count"]!=2:
        raise ValueError("original_authored_Shader48_props_changed")
    players=[native.records(s) for platform,s in native.decoded_platforms(tree)
             if platform==4]
    if len(players)!=1:
        raise ValueError("SOURCE_D3D11_PROGRAM_TABLE")
    baseline=native.identity.inspect(tree["m_ParsedForm"],players[0])
    if (baseline.get("status")!=native.identity.STATUS or
        baseline.get("matched_vertex_fragment_permutation_pairs")!=4 or
        baseline.get("original_D3D11_program_table_records")!=16):
        raise ValueError("original_paired_DXBC_shader_structure_changed")
    pairs=native.stage.exact_four_pairs(tree["m_ParsedForm"],players[0])
    report=classify_original_pairs(pairs)
    report["source_original_six_scenes_SHA_authenticated"]=True
    report["source_original_four_owner_SHA_authenticated"]=True
    report["source_particle_renderer_material_slots"]=108
    report["source_original_keyword_pairs"]=4
    return report

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_private_token_report_location")
    try:
        report=probe(args.original,args.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
            "failure_type":type(exc).__name__,
            "safe_original_DXBC_declaration_failure_reason":SAFE_REASONS.get(
                str(exc),"UNCLASSIFIED_SOURCE"),
            "original_binding_register_numbers_names_shader_bytes_or_GUIDs_published":False,
            "original_shader_program_Android_pixels_or_Unity_shader_compilation_proven":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_DXBC_DECLARATIONS_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
