#!/usr/bin/env python3
"""GT source-only: inspect genuine DXBC SAMPLE resource/sampler operand pairs.

This is NOT an original Material sampler binding, filter/wrap parity, shader
restoration, Android render or runtime keyword proof. Only authenticated SHA
original Particle108 stage DXBC is accepted. Reports have counts only: no
source shader bytecode, HLSL, names, register numbers or GUIDs published.

D3D10/11 tokenized program opcode and operand fields are from Microsoft's
D3D12TokenizedProgramFormat.hpp: SAMPLE family=69..74, sampler=6, resource=7.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import struct

from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts import t3_original_particle108_spirv_translation as translation
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.gt_particle108_original_dxbc_sampler_decl import (
    SourceError as OriginalDXBCError,
    dxbc_sampler_declarations,
)

SAMPLE_ARITY={69:4,70:5,71:5,72:5,73:6,74:5}
CUSTOMDATA=53
MAX_DWORDS=2_000_000
MAX_RECURSION=5
FAILURES=frozenset((
    "SHA_ORIGINAL_MISMATCH", "SOURCE_DXBC_MALFORMED",
    "SOURCE_SAMPLE_OPCODE_LENGTH_INVALID", "SOURCE_SAMPLE_OPERAND_UNSUPPORTED",
    "SOURCE_SAMPLE_REGISTER_INDIRECT", "SOURCE_SAMPLE_RESOURCE_SAMPLER_MISSING",
    "SOURCE_ORIGINAL_TEXTURE_TABLE_MISSING", "SOURCE_ORIGINAL_TEXTURE_TABLE_AMBIGUOUS",
))
class SampleProofError(ValueError):
    def __init__(self,reason):
        if reason not in FAILURES:
            raise ValueError("unsupported_original_sampling_failure_reason")
        super().__init__(reason)
        self.reason=reason


def _words_from_original_dxbc(blob):
    """Container/chunk table and single SHDR/SHEX program, bounded and exact."""
    # Existing source parser checks length, offsets and instruction bounds.
    # Keep one public, privacy-safe fail-closed exception family.
    try:
        dxbc_sampler_declarations(blob)
    except OriginalDXBCError:
        raise SampleProofError("SOURCE_DXBC_MALFORMED") from None
    if type(blob) is not bytes or len(blob)<36 or blob[:4]!=b"DXBC":
        raise SampleProofError("SOURCE_DXBC_MALFORMED")
    chunks=struct.unpack_from("<I",blob,28)[0]
    result=[]
    for k in range(chunks):
        start=struct.unpack_from("<I",blob,32+4*k)[0]
        if blob[start:start+4] in (b"SHDR",b"SHEX"):
            size=struct.unpack_from("<I",blob,start+4)[0]
            b=blob[start+8:start+8+size]
            if len(b)%4 or not 8<=len(b)<=MAX_DWORDS*4:
                raise SampleProofError("SOURCE_DXBC_MALFORMED")
            result=struct.unpack("<"+"I"*(len(b)//4),b)
    if not result or result[1]!=len(result):
        raise SampleProofError("SOURCE_DXBC_MALFORMED")
    return result


def _operand(words, at, end, depth=0):
    """Read a tokenized operand; return (next position, type, direct 1D slot).

    Direct register index is only considered established for immediate32 1D
    addressing. Relative, multidimensional and anonymous resource/sampler
    addressing are never mapped by guesswork.
    """
    if depth>MAX_RECURSION or at>=end:
        raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
    token=words[at]
    at+=1
    if token>>31:
        while True:
            if at>=end:
                raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
            ext=words[at]
            at+=1
            if not (ext>>31):
                break
            if at>=end or at>len(words):
                raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
    kind=(token>>12)&255
    ndim=(token>>20)&3
    direct=None
    indices=[]
    for k in range(ndim):
        mode=(token>>(22+3*k))&7
        if mode in (0,1):
            consumed=1 if mode==0 else 2
            if at+consumed>end:
                raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
            indices.append(words[at] if mode==0 else None)
            at+=consumed
        elif mode in (2,3,4):
            if mode in (3,4):
                consumed=1 if mode==3 else 2
                if at+consumed>end:
                    raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
                at+=consumed
            at,_,_=_operand(words,at,end,depth+1)
            indices.append(None)
        else:
            raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
    if ndim==1 and ((token>>22)&7)==0:
        direct=indices[0]
    if kind in (4,5):  # literal immediate32 / immediate64 source operands
        comps={1:1,2:4}.get(token&3)
        if comps is None:
            raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
        size=comps*(1 if kind==4 else 2)
        if at+size>end:
            raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
        at+=size
    if at>end:
        raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
    return at,kind,direct


def sample_operand_pairs(blob):
    """Return private tuples (original source resource t, sampler s, opcode)."""
    words=_words_from_original_dxbc(blob)
    pos=2
    pairs=[]
    while pos<len(words):
        tok=words[pos]
        code=tok&0x7ff
        length=(tok>>24)&0x7f
        if code==CUSTOMDATA and length==0:
            if pos+1>=len(words):
                raise SampleProofError("SOURCE_SAMPLE_OPCODE_LENGTH_INVALID")
            length=words[pos+1]
        if length<1 or pos+length>len(words):
            raise SampleProofError("SOURCE_SAMPLE_OPCODE_LENGTH_INVALID")
        if code in SAMPLE_ARITY:
            end=pos+length
            at=pos+1
            if tok>>31:
                # Extended opcode tokens are explicitly skipped, not confused
                # with operand descriptors; reject long malformed chains.
                for _ in range(8):
                    if at>=end:
                        raise SampleProofError("SOURCE_SAMPLE_OPCODE_LENGTH_INVALID")
                    extra=words[at]
                    at+=1
                    if not extra>>31:
                        break
                else:
                    raise SampleProofError("SOURCE_SAMPLE_OPERAND_UNSUPPORTED")
            decoded=[]
            for _ in range(SAMPLE_ARITY[code]):
                at,typ,idx=_operand(words,at,end)
                decoded.append((typ,idx))
            if at!=end:
                raise SampleProofError("SOURCE_SAMPLE_OPCODE_LENGTH_INVALID")
            # Every SAMPLE variant: dest, coordinates, resource, sampler,
            # followed by optional compare/LOD/bias/derivatives.
            rt,tx=decoded[2]
            st,sm=decoded[3]
            if rt!=7 or st!=6:
                raise SampleProofError("SOURCE_SAMPLE_RESOURCE_SAMPLER_MISSING")
            if tx is None or sm is None:
                raise SampleProofError("SOURCE_SAMPLE_REGISTER_INDIRECT")
            if tx>4095 or sm>4095:
                raise SampleProofError("SOURCE_SAMPLE_RESOURCE_SAMPLER_MISSING")
            pairs.append((tx,sm,code))
        pos+=length
    if pos!=len(words):
        raise SampleProofError("SOURCE_SAMPLE_OPCODE_LENGTH_INVALID")
    return tuple(pairs)


def source_texture_slots(program):
    common=program.get("m_CommonParameters") if isinstance(program,dict) else None
    rows=common.get("m_TextureParams") if isinstance(common,dict) else None
    if not isinstance(rows,list):
        raise SampleProofError("SOURCE_ORIGINAL_TEXTURE_TABLE_MISSING")
    out=set()
    for row in rows:
        if not isinstance(row,dict) or type(row.get("m_Index")) is not int:
            raise SampleProofError("SOURCE_ORIGINAL_TEXTURE_TABLE_MISSING")
        slot=row["m_Index"]
        if not 0<=slot<=4095 or slot in out:
            raise SampleProofError("SOURCE_ORIGINAL_TEXTURE_TABLE_AMBIGUOUS")
        out.add(slot)
    return out


def probe(root:Path,manifest:Path):
    if (not root.is_dir() or root.is_symlink() or
        not manifest.is_file() or manifest.is_symlink()):
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    selected={}
    result=impact.load_original(root,manifest,private_particle_slot_counts=selected)
    owner,pid=identity.select(selected,result)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    import UnityPy
    obj=[o for o in UnityPy.load(str(path)).file.objects.values()
         if o.type.name=="Shader" and o.path_id==pid]
    if len(obj)!=1:
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    tree=obj[0].read_typetree()
    sub=tree["m_ParsedForm"]["m_SubShaders"]
    if len(sub)!=1 or len(sub[0]["m_Passes"])!=1:
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    prog=sub[0]["m_Passes"][0]
    table=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(table)!=1:
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    pairs=translation.exact_four_pairs(tree["m_ParsedForm"],table[0])
    if len(pairs)!=4:
        raise SampleProofError("SHA_ORIGINAL_MISMATCH")
    totals=Counter()
    for vs,fs in pairs:
        for stage,code in ((1,vs),(0,fs)):
            direct=sample_operand_pairs(code)
            declared=dict(dxbc_sampler_declarations(code))
            original_textures=source_texture_slots(
                prog["progVertex" if stage==1 else "progFragment"])
            by_sampler=defaultdict(set)
            for tex,sampler,_ in direct:
                by_sampler[sampler].add(tex)
            counts=Counter()
            counts["DXBC_stages_examined"]+=1
            counts["original_sample_family_instructions"]+=len(direct)
            counts["unique_original_sample_sampler_slots"]+=len(by_sampler)
            counts["sampler_slots_with_exactly_one_sampled_texture"]+=sum(
                len(v)==1 for v in by_sampler.values())
            counts["sampler_slots_with_multiple_sampled_textures"]+=sum(
                len(v)>1 for v in by_sampler.values())
            counts["sample_instructions_with_dcl_sampler_slot"]+=sum(
                s in declared for _,s,_ in direct)
            counts["sample_instructions_without_dcl_sampler_slot"]+=sum(
                s not in declared for _,s,_ in direct)
            counts["sample_instructions_with_original_serialized_texture_slot"]+=sum(
                t in original_textures for t,_,_ in direct)
            counts["sample_instructions_without_original_serialized_texture_slot"]+=sum(
                t not in original_textures for t,_,_ in direct)
            totals.update(counts)
    return {"schema":1,
        "status":"SOURCE_ORIGINAL_PARTICLE108_DXBC_SAMPLE_PAIRS_CLASSIFIED",
        "counts":dict(sorted(totals.items())),
        "source_original_shaders_SHA_authenticated":True,
        "original_sampled_texture_to_sampler_pair_material_state_equivalence_proven":False,
        "original_filter_wrap_or_Adreno_pixels_proven":False,
        "original_names_register_numbers_HLSL_DXBC_Guids_published":False}


def main():
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        ap.add_argument("--"+key,type=Path,required=True)
    a=ap.parse_args()
    if (a.out.exists() or a.out.is_symlink() or
        not a.out.parent.is_dir() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise SystemExit("unsafe_private_sampling_report")
    try:
        result=probe(a.original,a.manifest)
    except Exception as exc:
        reason=exc.reason if isinstance(exc,SampleProofError) else "UNCLASSIFIED_SOURCE"
        result={"schema":1,"status":"INCONCLUSIVE","failure_code":reason,
            "source_original_shaders_SHA_authenticated":False,
            "original_sampled_texture_to_sampler_pair_material_state_equivalence_proven":False,
            "original_filter_wrap_or_Adreno_pixels_proven":False,
            "original_names_register_numbers_HLSL_DXBC_Guids_published":False}
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_ORIGINAL_PARTICLE108_SAMPLE_PAIR_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="SOURCE_ORIGINAL_PARTICLE108_DXBC_SAMPLE_PAIRS_CLASSIFIED" else 2


if __name__=="__main__":
    raise SystemExit(main())
