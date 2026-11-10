#!/usr/bin/env python3
"""GFX-MULTI-039: complete original Shader48 DX11 SHDR interpolation census.

Read tokenized programs from the SHA-pinned original D3D11 compiled source.
D3D10_OPCODE_DCL_INPUT_PS and _SIV modes are bits [14:11] of opcode token;
DCL_INPUT_PS_SGV has no interpolation mode. Public enum labels only.
No private shader program code, byte offsets, registers or material identities
leave the source runner. Original Material→t/s/CB binding remains UNPROVEN.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader,collect_stage_variant_rows
from gfxlab.tools.multi_shader_gl_program_envelope import public_shader_compiler_platform
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs,code_from_ref,exact_pairs
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk,declaration_counts

# Public D3D12TokenizedProgramFormat.hpp D3D10_SB_OPCODE_TYPE enum.
DCL_INPUT_PS=98
DCL_INPUT_PS_SGV=99
DCL_INPUT_PS_SIV=100
CUSTOMDATA=53
MODES={
 0:"undefined",
 1:"constant",
 2:"linear",
 3:"linear_centroid",
 4:"linear_noperspective",
 5:"linear_noperspective_centroid",
 6:"linear_sample",
 7:"linear_noperspective_sample",
}
RESOURCE_FIELDS=(
 "dcl_resource","dcl_constant_buffer","dcl_sampler",
 "dcl_resource_raw","dcl_resource_structured")
EXPECTED_LINKS=1435
EXPECTED_PAIRS=524
EXPECTED_VS_UNIQUE=620
EXPECTED_PS_UNIQUE=655
MAX_DWORDS=2000000


def inspect_interpolation(blob,kind):
    """Scan entire bounded SHDR instruction tokens. No register index is read."""
    if kind not in ("Vertex","Pixel"):
        raise ValueError("ORIGINAL_DXBC_STAGE_TYPE_INVALID")
    if not isinstance(blob,bytes) or len(blob)<12 or len(blob)%4:
        raise ValueError("ORIGINAL_SHADER_SHDR_BAD_TOKEN_SIZE")
    words=struct.unpack("<%dI"%(len(blob)//4),blob)
    if len(words)>MAX_DWORDS or words[1]!=len(words):
        raise ValueError("ORIGINAL_SHADER_SHDR_BAD_DECLARED_LENGTH")
    out=Counter({x:0 for x in (
        "ordinary_input_ps_declarations",
        "system_value_input_ps_interpolated_declarations",
        "system_generated_input_ps_declarations",
        "pixel_interpolation_declaration_total",
        "all_instruction_tokens")})
    for name in MODES.values():out["interpolation_"+name]=0
    pos=2
    while pos<len(words):
        token=words[pos]
        opcode=token&0x7ff
        if opcode==CUSTOMDATA:
            if pos+1>=len(words):
                raise ValueError("ORIGINAL_SHDR_CUSTOMDATA_TRUNCATED")
            n=words[pos+1]
            if n<2:
                raise ValueError("ORIGINAL_SHDR_CUSTOMDATA_LENGTH_INVALID")
        else:
            n=(token>>24)&0x7f
            if n<1:
                raise ValueError("ORIGINAL_SHDR_ZERO_LENGTH_OPCODE")
        if pos+n>len(words):
            raise ValueError("ORIGINAL_SHDR_OPCODE_OUT_OF_BOUNDS")
        out["all_instruction_tokens"]+=1
        if opcode in (DCL_INPUT_PS,DCL_INPUT_PS_SIV,DCL_INPUT_PS_SGV):
            if n<(2 if opcode==DCL_INPUT_PS else 3):
                raise ValueError("ORIGINAL_PIXEL_INPUT_DECLARATION_TOO_SHORT")
            if kind!="Pixel":
                raise ValueError("ORIGINAL_VERTEX_CONTAINS_PIXEL_INPUT_DECLARATION")
            if opcode==DCL_INPUT_PS_SGV:
                out["system_generated_input_ps_declarations"]+=1
            else:
                mode=(token>>11)&0xf
                if mode not in MODES:
                    raise ValueError("ORIGINAL_PIXEL_INTERPOLATION_MODE_UNDOCUMENTED")
                out["ordinary_input_ps_declarations" if opcode==DCL_INPUT_PS
                    else "system_value_input_ps_interpolated_declarations"]+=1
                out["interpolation_"+MODES[mode]]+=1
                out["pixel_interpolation_declaration_total"]+=1
        pos+=n
    if pos!=len(words):
        raise ValueError("ORIGINAL_SHADER_SHDR_OPCODE_STREAM_INCOMPLETE")
    return dict(out)


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    shader=_locate_shader(entries,typed)
    if public_shader_compiler_platform(shader.read().platforms)!="kShaderCompPlatformD3D11":
        raise ValueError("ORIGINAL_SHADER_COMPILER_PLATFORM_DRIFT")
    parsed=shader.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("ORIGINAL_SHADER48_PARSED_FORM_MISSING")
    subs=parsed.get("m_SubShaders")
    if not isinstance(subs,list) or [len(s.get("m_Passes",[])) for s in subs]!=[4,3]:
        raise ValueError("ORIGINAL_SEVEN_PASS_TOPOLOGY_DRIFT")
    programs=compiled_programs(shader)
    seen=set()
    totals=Counter({
        "original_stage_link_rows":0,"exact_variant_stage_pairs":0,
        "unique_vertex_programs":0,"unique_fragment_programs":0,
        "unique_original_stage_programs":0,
    })
    instruction_by_stage={"Vertex":Counter(),"Pixel":Counter()}
    interpolation_by_stage={"Vertex":Counter(),"Pixel":Counter()}
    per_pass=[]
    for sub in subs:
        for p in sub["m_Passes"]:
            stage_link_counts=Counter({"vertex_links":0,"pixel_links":0})
            pairs=exact_pairs(p)
            if not pairs:
                raise ValueError("ORIGINAL_SOURCE_PASS_HAS_NO_MATCHED_PAIRS")
            totals["exact_variant_stage_pairs"]+=len(pairs)
            for field,kind in (("progVertex","Vertex"),("progFragment","Pixel")):
                for row in collect_stage_variant_rows(p.get(field)):
                    idx=row.get("m_BlobIndex")
                    typ=row.get("m_GpuProgramType")
                    if type(idx) is not int or not 0<=idx<len(programs):
                        raise ValueError("ORIGINAL_SHDR_LINKED_INDEX_INVALID")
                    source=programs[idx]
                    if (type(typ) is not int or int(source.m_ProgramType)!=typ
                            or "DX11" not in source.m_ProgramType.name
                            or kind not in source.m_ProgramType.name):
                        raise ValueError("ORIGINAL_SHDR_LINKED_GPU_TYPE_MISMATCH")
                    totals["original_stage_link_rows"]+=1
                    stage_link_counts["vertex_links" if kind=="Vertex" else "pixel_links"]+=1
                    if idx in seen:
                        continue
                    seen.add(idx)
                    original=code_from_ref(row,programs,kind)
                    blob=source_shader_chunk(original)
                    d=declaration_counts(blob)
                    i=inspect_interpolation(blob,kind)
                    for k,v in d.items():instruction_by_stage[kind][k]+=v
                    for k,v in i.items():interpolation_by_stage[kind][k]+=v
                    totals["unique_vertex_programs" if kind=="Vertex" else
                           "unique_fragment_programs"]+=1
                    totals["unique_original_stage_programs"]+=1
            per_pass.append({
                "exact_original_keyword_tier_pairs":len(pairs),
                "original_stage_link_rows":sum(stage_link_counts.values()),
            })
    if len(per_pass)!=7 or totals["original_stage_link_rows"]!=EXPECTED_LINKS or (
         totals["exact_variant_stage_pairs"]!=EXPECTED_PAIRS or
         totals["unique_vertex_programs"]!=EXPECTED_VS_UNIQUE or
         totals["unique_fragment_programs"]!=EXPECTED_PS_UNIQUE or
         totals["unique_original_stage_programs"]!=EXPECTED_VS_UNIQUE+EXPECTED_PS_UNIQUE):
        raise ValueError("ORIGINAL_SHDR_ALL_LINKED_PROGRAM_COUNTS_DRIFT")
    return {
        "experiment":"GFX-MULTI-039",
        "original_zip2_sha":ZIP2_SHA,
        "original_shader_compiler_platform":"kShaderCompPlatformD3D11",
        "original_program_accounting":dict(totals),
        "original_pass_link_counts":per_pass,
        "all_original_linked_program_declaration_totals":{
            kind:{k:int(instruction_by_stage[kind][k]) for k in (
                *RESOURCE_FIELDS,"total_instruction_tokens","shader_token_dwords")}
            for kind in ("Vertex","Pixel")},
        "all_linked_pixel_input_interpolation_mode_totals":
            dict(interpolation_by_stage["Pixel"]),
        "vertex_shdr_pixel_interpolation_declarations":
            sum(interpolation_by_stage["Vertex"][x] for x in (
                "ordinary_input_ps_declarations",
                "system_value_input_ps_interpolated_declarations",
                "system_generated_input_ps_declarations")),
        "original_stage_interpolation_categories_parsed_from_D3D10_opcode_token":True,
        "interpolation_runtime_and_GLES_reproduction_verified":False,
        "source_original_material_to_GPU_register_cb_binding_verified":False,
        "android_original_shader48_execution_verified":False,
        "original_shader48_restored":False,
        "pc_to_adreno_pixel_parity_verified":False,
        "private_original_DXBC_instruction_operands_keyword_names_and_registers_exported":False,
        "phase_closed":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip2",type=Path,required=True)
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI039_SAFE_LINKED_SHDR_INTERPOLATION_CENSUS "+json.dumps(d,sort_keys=True))


if __name__=="__main__":main()
