#!/usr/bin/env python3
"""GT Particle108: original DXBC dcl_sampler register census without RDEF.

This is source-private, fail-closed instrumentation. It records counts only.
It does NOT equate Shader serialized indices, DXBC sampler declarations and
SPIRV-Cross HLSL register() annotations; equality needs independent evidence.
No original shader bytes, resource names, register indices or GUIDs in reports.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct

from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as original_id
from scripts import t3_original_particle108_spirv_translation as translation
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.t3_particle108_original_dxbc_rdef import source_rdef
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms,records

# D3D10/11 tokenized program format (Microsoft DirectX-Headers):
# opcode bits 0..10, dcl_sampler=90; instruction DWORD count bits 24..30;
# operand type bits 12..19 (sampler=6); index dim bits 20..21 (1D=1);
# 1st index mode bits 22..24 (immediate32=0); mode bits 11..14.
DCL_SAMPLER=90
CUSTOMDATA=53
MAX_BYTES=8*1024*1024
MAX_CHUNKS=64
MAX_SAMPLERS=128
SAMPLER_DECL=re.compile(
    r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*'
    r'\s*:\s*register\(\s*s(\d+)\s*(?:,\s*space0\s*)?\)\s*;'
)
SAMPLER_TYPE=re.compile(r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*\b')
STATUS="GT_ORIGINAL_PARTICLE108_EIGHT_SOURCE_DXBC_SAMPLER_DECL_CENSUS"
SAFE_FAILURE=frozenset((
    "DXBC_SOURCE_CONTAINER_INVALID","DXBC_SOURCE_CHUNKS_INVALID",
    "DXBC_SOURCE_PROGRAM_MISSING","DXBC_SOURCE_PROGRAM_DUPLICATED",
    "DXBC_SOURCE_OPCODE_UNSUPPORTED","DXBC_SOURCE_SAMPLER_DECL_UNSUPPORTED",
    "DXBC_SOURCE_SAMPLER_DUPLICATED","SOURCE_SHA_ORIGINAL_MISMATCH",
    "SOURCE_ORIGINAL_STAGE_METADATA_INVALID","TRANSLATOR_SAMPLER_STAGE_INVALID",
    "SOURCE_ORIGINAL_RDEF_NOT_ABSENT",
))

class SourceError(ValueError):
    def __init__(self, reason):
        if reason not in SAFE_FAILURE:
            raise ValueError("unexpected_private_source_failure")
        self.reason=reason
        super().__init__(reason)

def _u32(blob,offset):
    if offset<0 or offset+4>len(blob):
        raise SourceError("DXBC_SOURCE_CONTAINER_INVALID")
    return struct.unpack_from("<I",blob,offset)[0]

def dxbc_sampler_declarations(data:bytes):
    """Return private tuples (slot, sampler_mode); no RDEF required."""
    if (type(data) is not bytes or not 36<=len(data)<=MAX_BYTES
        or data[:4]!=b"DXBC" or _u32(data,24)!=len(data)):
        raise SourceError("DXBC_SOURCE_CONTAINER_INVALID")
    count=_u32(data,28)
    if not 1<=count<=MAX_CHUNKS or 32+4*count>len(data):
        raise SourceError("DXBC_SOURCE_CHUNKS_INVALID")
    programs=[]
    occupied=[]
    for n in range(count):
        off=_u32(data,32+4*n)
        if off<32+4*count or off+8>len(data):
            raise SourceError("DXBC_SOURCE_CHUNKS_INVALID")
        end=off+8+_u32(data,off+4)
        if end>len(data) or any(off<right and left<end for left,right in occupied):
            raise SourceError("DXBC_SOURCE_CHUNKS_INVALID")
        occupied.append((off,end))
        if data[off:off+4] in (b"SHDR",b"SHEX"):
            programs.append(data[off+8:end])
    if not programs:
        raise SourceError("DXBC_SOURCE_PROGRAM_MISSING")
    if len(programs)!=1:
        raise SourceError("DXBC_SOURCE_PROGRAM_DUPLICATED")
    body=programs[0]
    if len(body)%4 or len(body)<8:
        raise SourceError("DXBC_SOURCE_PROGRAM_MISSING")
    words=struct.unpack("<"+"I"*(len(body)//4),body)
    if words[1]!=len(words):
        raise SourceError("DXBC_SOURCE_PROGRAM_MISSING")
    seen=set()
    values=[]
    i=2
    while i<len(words):
        opcode_token=words[i]
        opcode=opcode_token&0x7ff
        n=(opcode_token>>24)&0x7f
        if n==0 and opcode==CUSTOMDATA and i+1<len(words):
            n=words[i+1]
        if n<1 or i+n>len(words):
            raise SourceError("DXBC_SOURCE_OPCODE_UNSUPPORTED")
        if opcode==DCL_SAMPLER:
            if n!=3 or (opcode_token>>31)!=0:
                raise SourceError("DXBC_SOURCE_SAMPLER_DECL_UNSUPPORTED")
            mode=(opcode_token>>11)&0xf
            operand=words[i+1]
            # Only a direct sampler sN declaration is accepted. Do NOT
            # reinterpret a relative/64-bit/extended operand as a register.
            if (mode not in (0,1,2) or (operand>>31)!=0
                or ((operand>>12)&0xff)!=6 or
                ((operand>>20)&3)!=1 or ((operand>>22)&7)!=0):
                raise SourceError("DXBC_SOURCE_SAMPLER_DECL_UNSUPPORTED")
            slot=words[i+2]
            if slot>4095 or slot in seen or len(values)>=MAX_SAMPLERS:
                raise SourceError("DXBC_SOURCE_SAMPLER_DUPLICATED")
            seen.add(slot)
            values.append((slot,mode))
        i+=n
    if i!=len(words):
        raise SourceError("DXBC_SOURCE_OPCODE_UNSUPPORTED")
    return tuple(values)

def _original_serialized_sampler_set(program):
    if not isinstance(program,dict):
        raise SourceError("SOURCE_ORIGINAL_STAGE_METADATA_INVALID")
    rows=program.get("m_CommonParameters",{}).get("m_TextureParams")
    if not isinstance(rows,list):
        raise SourceError("SOURCE_ORIGINAL_STAGE_METADATA_INVALID")
    result=set()
    for row in rows:
        if not isinstance(row,dict):
            raise SourceError("SOURCE_ORIGINAL_STAGE_METADATA_INVALID")
        idx=row.get("m_SamplerIndex")
        if type(idx) is not int:
            raise SourceError("SOURCE_ORIGINAL_STAGE_METADATA_INVALID")
        if 0<=idx<65535:
            result.add(idx)
    return result

def _hlsl_sampler_set(hlsl):
    if type(hlsl) is not str or not 0<len(hlsl.encode())<=1024*1024:
        raise SourceError("TRANSLATOR_SAMPLER_STAGE_INVALID")
    reg=[int(m.group(1)) for m in SAMPLER_DECL.finditer(hlsl)]
    if len(reg)!=len(SAMPLER_TYPE.findall(hlsl)) or len(reg)!=len(set(reg)):
        raise SourceError("TRANSLATOR_SAMPLER_STAGE_INVALID")
    return set(reg)

def probe(original:Path,manifest:Path,private_source:Path):
    if (not original.is_dir() or original.is_symlink()
        or not manifest.is_file() or manifest.is_symlink()
        or not private_source.is_dir() or private_source.is_symlink()):
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    selected={}
    census=impact.load_original(original,manifest,private_particle_slot_counts=selected)
    owner,pid=original_id.select(selected,census)
    source=original/"Raft_Data"/owner
    if source.is_symlink() or fingerprint(source)!=SHADER_OWNERS[owner]:
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    import UnityPy
    objs=[o for o in UnityPy.load(str(source)).file.objects.values()
          if o.type.name=="Shader" and o.path_id==pid]
    if len(objs)!=1:
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    tree=objs[0].read_typetree()
    parsed=tree.get("m_ParsedForm",{})
    passes=parsed.get("m_SubShaders",[])
    if not isinstance(passes,list) or len(passes)!=1 or len(passes[0].get("m_Passes",[]))!=1:
        raise SourceError("SOURCE_ORIGINAL_STAGE_METADATA_INVALID")
    p=passes[0]["m_Passes"][0]
    tables=[records(x) for platform,x in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    pairs=translation.exact_four_pairs(parsed,tables[0])
    if len(pairs)!=4:
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    counts=Counter()
    for variant,(vs,fs) in enumerate(pairs):
        for stage_id,data in ((1,vs),(0,fs)):
            try:
                source_rdef(data)
            except ValueError as exc:
                if str(exc)!="DXBC_ORIGINAL_RDEF_ABSENT":
                    raise SourceError("SOURCE_ORIGINAL_RDEF_NOT_ABSENT") from None
            else:
                raise SourceError("SOURCE_ORIGINAL_RDEF_NOT_ABSENT")
            decl=dxbc_sampler_declarations(data)
            original_set={slot for slot,_ in decl}
            serialized=_original_serialized_sampler_set(
                p["progVertex" if stage_id==1 else "progFragment"])
            path=private_source/("keyword-%d-stage-%d/private.hlsl"%(variant,stage_id))
            if path.is_symlink() or not path.is_file():
                raise SourceError("TRANSLATOR_SAMPLER_STAGE_INVALID")
            translated=_hlsl_sampler_set(path.read_text(encoding="utf-8"))
            counts["source_original_DXBC_stages_examined"]+=1
            counts["source_original_DXBC_sampler_declarations"]+=len(decl)
            counts["source_original_serialized_sampler_slots"]+=len(serialized)
            counts["translated_HLSL_sampler_register_declarations"]+=len(translated)
            counts["source_original_declared_sampler_slots_matching_serialized"]+=len(original_set&serialized)
            counts["source_original_declared_sampler_slots_NOT_in_serialized"]+=len(original_set-serialized)
            counts["source_serialized_sampler_slots_NOT_in_DXBC_declarations"]+=len(serialized-original_set)
            counts["translated_register_slots_matching_DXBC_samplers_not_proven_identity"]+=len(translated&original_set)
            counts["source_original_comparison_sampler_declarations"]+=sum(mode==1 for _,mode in decl)
            counts["source_original_mono_sampler_declarations"]+=sum(mode==2 for _,mode in decl)
    if counts["source_original_DXBC_stages_examined"]!=8:
        raise SourceError("SOURCE_SHA_ORIGINAL_MISMATCH")
    return {
        "schema":1,"status":STATUS,"counts":dict(sorted(counts.items())),
        "source_original_four_VSFS_keyword_pairs_SHA_authenticated":True,
        "source_original_RDEF_absent_stages":8,
        "original_DXBC_resource_names_register_numbers_shader_values_or_GUIDs_published":False,
        "original_shader_Unity_import_or_Android_pixels_proven":False,
        "sampler_to_original_Material_texture_binding_proven":False,
        "SPIRV_Cross_descriptor_register_equivalence_proven":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","private-source","out"):
        ap.add_argument("--"+key,type=Path,required=True)
    args=ap.parse_args()
    if (args.out.exists() or args.out.is_symlink()
        or not args.out.parent.is_dir()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or args.out.resolve().is_relative_to(args.private_source.resolve())):
        raise SystemExit("unsafe_original_sampler_private_report")
    try:
        result=probe(args.original,args.manifest,args.private_source)
    except Exception as exc:
        reason=exc.reason if isinstance(exc,SourceError) else "UNCLASSIFIED_PRIVATE_SOURCE"
        result={"schema":1,"status":"INCONCLUSIVE","failure_code":reason,
                "original_DXBC_resource_names_register_numbers_shader_values_or_GUIDs_published":False,
                "original_shader_Unity_import_or_Android_pixels_proven":False,
                "sampler_to_original_Material_texture_binding_proven":False}
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_ORIGINAL_DXBC_SAMPLER_DECL_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
