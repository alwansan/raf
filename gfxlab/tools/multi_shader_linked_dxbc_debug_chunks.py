#!/usr/bin/env python3
"""GFX-MULTI-037: original Shader48 linked DXBC alternative debug/reflection census.

Inspect every real source-linked DX11 stage DXBC container from fixed ZIP2.
The public-safe output contains only counts of public DXBC FourCC categories.
No proprietary shader bytecode, debug symbols/property names, PPtrs, register
numbers or HLSL fragments ever appear in logs or committed artifacts.
Debug/resource chunk presence does NOT prove original Material/CB semantics.
"""
from __future__ import annotations

import argparse,json,struct,re
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import (
    _locate_shader,collect_stage_variant_rows,
)
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs,code_from_ref,exact_pairs
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary
from gfxlab.tools.multi_shader_gl_program_envelope import public_shader_compiler_platform

# Public, generic DirectX container FourCCs (Microsoft DXBC BlobContainer.h,
# RenderDoc DXBC container parser). Never emit an unknown original FourCC.
PUBLIC_TAGS={
    b"RDEF":"RDEF", b"SDBG":"SDBG", b"SPDB":"SPDB", b"ILDB":"ILDB",
    b"RDAT":"RDAT", b"SRCI":"SRCI", b"ISGN":"ISGN", b"ISG1":"ISG1",
    b"OSGN":"OSGN", b"OSG1":"OSG1", b"OSG5":"OSG5",
    b"PCSG":"PCSG", b"PSG1":"PSG1",
    b"SHDR":"SHDR", b"SHEX":"SHEX", b"STAT":"STAT",
    b"SFI0":"SFI0", b"DXIL":"DXIL", b"RTS0":"RTS0", b"PSV0":"PSV0",
    b"HASH":"HASH", b"PRIV":"PRIV", b"ILDN":"ILDN", b"PDBI":"PDBI",
}
ALTERNATE_REFLECTION=("SDBG","SPDB","ILDB","RDAT","SRCI","PRIV","PDBI")
EXPECTED_LINK_ROWS=1435
EXPECTED_PAIR_ROWS=524
EXPECTED_UNIQUE_PROGRAMS=1275
MAX_DXBC_BYTES=8*1024*1024
MAX_CHUNKS=64


def safe_container_chunks(container):
    """Structural validation of DXBC chunk table, never semantic binding inference."""
    if not isinstance(container,bytes) or not 36<=len(container)<=MAX_DXBC_BYTES:
        raise ValueError("ORIGINAL_DXBC_SIZE_INVALID")
    if container[:4]!=b"DXBC":
        raise ValueError("ORIGINAL_DXBC_MAGIC_INVALID")
    declared=struct.unpack_from("<I",container,24)[0]
    n=struct.unpack_from("<I",container,28)[0]
    if declared!=len(container) or not 1<=n<=MAX_CHUNKS or 32+4*n>len(container):
        raise ValueError("ORIGINAL_DXBC_CHUNK_HEADER_INVALID")
    table_end=32+4*n
    spans=[]
    chunks=[]
    for j in range(n):
        off=struct.unpack_from("<I",container,32+4*j)[0]
        if off<table_end or off+8>len(container):
            raise ValueError("ORIGINAL_DXBC_CHUNK_OFFSET_INVALID")
        size=struct.unpack_from("<I",container,off+4)[0]
        end=off+8+size
        if end>len(container):
            raise ValueError("ORIGINAL_DXBC_CHUNK_TRUNCATED")
        tag=container[off:off+4]
        label=PUBLIC_TAGS.get(tag,"OTHER_PUBLIC_TAG_UNRECOGNIZED")
        chunks.append((label,container[off+8:end]))
        spans.append((off,end))
    spans.sort()
    for i in range(1,len(spans)):
        if spans[i][0]<spans[i-1][1]:
            raise ValueError("ORIGINAL_DXBC_CHUNK_OVERLAP")
    if not any(k in ("SHDR","SHEX") for k,_ in chunks):
        raise ValueError("ORIGINAL_DXBC_STAGE_CODE_MISSING")
    return chunks


def authentic_source_property_tokens(data,names):
    """Internal bounded name membership, never publish matched names."""
    if not isinstance(data,bytes) or not isinstance(names,set):
        raise ValueError("ORIGINAL_SOURCE_DEBUG_TOKEN_INPUT_INVALID")
    found=set()
    for name in names:
        if not isinstance(name,str) or not re.fullmatch(r"[_A-Za-z][_A-Za-z0-9]{0,127}",name):
            raise ValueError("ORIGINAL_SOURCE_PROPERTY_NAME_UNEXPECTED")
        label=re.escape(name.encode("ascii"))
        if re.search(rb"(?<![_A-Za-z0-9])"+label+rb"(?![_A-Za-z0-9])",data):
            found.add(name)
    return found


def inspect_one_dxbc(container,names):
    chunks=safe_container_chunks(container)
    categories=Counter(k for k,_ in chunks)
    has_alternative=any(k in ALTERNATE_REFLECTION for k in categories)
    found=set()
    for name,payload in chunks:
        if name in ALTERNATE_REFLECTION:
            found.update(authentic_source_property_tokens(payload,names))
    reflection=rdef_summary(container)
    if bool(categories["RDEF"]) == bool(reflection.get("rdef_missing_in_source",False)):
        raise ValueError("ORIGINAL_DXBC_RDEF_REFLECTION_INCONSISTENT")
    return {
        "tag_counts":dict(categories),
        "alternative_reflection_or_debug_chunk_present":has_alternative,
        "original_property_name_in_alternative_chunk_present":bool(found),
        "distinct_original_property_name_hits_in_debug_chunks":len(found),
        "rdef_chunk_present":bool(categories["RDEF"]),
        "raw_debug_or_reflection_bytes_exported":False,
        "material_property_register_offset_proven":False,
    }


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    shader=_locate_shader(entries,typed)
    platform=public_shader_compiler_platform(shader.read().platforms)
    if platform!="kShaderCompPlatformD3D11":
        raise ValueError("ORIGINAL_SHADER48_COMPILED_PLATFORM_DRIFT")
    tree=shader.read_typetree(check_read=False)
    parsed=tree.get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("ORIGINAL_SHADER48_PARSED_FORM_MISSING")
    subs=parsed.get("m_SubShaders")
    if not isinstance(subs,list) or [len(x.get("m_Passes",[])) for x in subs]!=[4,3]:
        raise ValueError("ORIGINAL_SHADER48_PASS_TOPOLOGY_DRIFT")
    props=parsed.get("m_PropInfo",{}).get("m_Props")
    if not isinstance(props,list) or len(props)!=27:
        raise ValueError("ORIGINAL_SHADER48_PROPERTY_COUNT_DRIFT")
    names=set()
    for entry in props:
        if not isinstance(entry,dict) or not isinstance(entry.get("m_Name"),str):
            raise ValueError("ORIGINAL_SHADER48_PROPERTY_SHAPE_INVALID")
        names.add(entry["m_Name"])
    if len(names)!=27:
        raise ValueError("ORIGINAL_SHADER48_PROPERTY_DUPLICATES")
    programs=compiled_programs(shader)
    if len(programs)!=1656:
        raise ValueError("ORIGINAL_COMPILED_PROGRAM_TABLE_DRIFT")
    seen=set()
    tags=Counter({name:0 for name in {*PUBLIC_TAGS.values(),"OTHER_PUBLIC_TAG_UNRECOGNIZED"}})
    stats=Counter({
        "stage_link_rows":0,
        "exact_matched_vs_fs_variant_pairs":0,
        "unique_dx11_stage_programs":0,
        "vertex_unique_programs":0,
        "fragment_unique_programs":0,
        "programs_with_rdef_chunk":0,
        "programs_with_alternate_debug_or_reflection_chunk":0,
        "programs_with_original_property_tokens_in_alternate_chunk":0,
        "programs_with_unrecognized_public_tag":0,
    })
    aggregate_distinct_names=set()
    for sub in subs:
        for source_pass in sub["m_Passes"]:
            stats["exact_matched_vs_fs_variant_pairs"]+=len(exact_pairs(source_pass))
            for stage_field,stage_label in (("progVertex","Vertex"),
                                            ("progFragment","Pixel")):
                for row in collect_stage_variant_rows(source_pass.get(stage_field)):
                    idx=row.get("m_BlobIndex")
                    typ=row.get("m_GpuProgramType")
                    if type(idx) is not int or not 0<=idx<len(programs):
                        raise ValueError("ORIGINAL_SHADER48_LINK_INDEX_INVALID")
                    source=programs[idx]
                    if type(typ) is not int or int(source.m_ProgramType)!=typ:
                        raise ValueError("ORIGINAL_SHADER48_LINK_PROGRAM_TYPE_INVALID")
                    if "DX11" not in source.m_ProgramType.name or stage_label not in source.m_ProgramType.name:
                        raise ValueError("ORIGINAL_SOURCE_LINK_NOT_DX11_STAGE")
                    stats["stage_link_rows"]+=1
                    if idx in seen:continue
                    seen.add(idx)
                    dxbc=code_from_ref(row,programs,stage_label)
                    result=inspect_one_dxbc(dxbc,names)
                    stats["unique_dx11_stage_programs"]+=1
                    stats["vertex_unique_programs" if stage_label=="Vertex"
                          else "fragment_unique_programs"]+=1
                    stats["programs_with_rdef_chunk"]+=int(result["rdef_chunk_present"])
                    stats["programs_with_alternate_debug_or_reflection_chunk"]+=int(
                        result["alternative_reflection_or_debug_chunk_present"])
                    stats["programs_with_original_property_tokens_in_alternate_chunk"]+=int(
                        result["original_property_name_in_alternative_chunk_present"])
                    stats["programs_with_unrecognized_public_tag"]+=int(
                        bool(result["tag_counts"].get("OTHER_PUBLIC_TAG_UNRECOGNIZED",0)))
                    for name,c in result["tag_counts"].items():tags[name]+=c
    if (stats["stage_link_rows"]!=EXPECTED_LINK_ROWS or
            stats["exact_matched_vs_fs_variant_pairs"]!=EXPECTED_PAIR_ROWS or
            stats["unique_dx11_stage_programs"]!=EXPECTED_UNIQUE_PROGRAMS):
        raise ValueError("ORIGINAL_DXBC_LINKED_STAGE_TOTAL_DRIFT")
    return {
        "experiment":"GFX-MULTI-037",
        "original_zip2_sha":ZIP2_SHA,
        "original_shader_compiled_platform":"kShaderCompPlatformD3D11",
        "source_shader48_subshaders":2,
        "source_shader48_passes":7,
        "original_shader48_declared_property_count":len(names),
        "source_linked_program_counts":dict(stats),
        "public_safe_dxbc_chunk_type_counts":dict(tags),
        "debug_chunk_property_name_to_original_gpu_resource_register_mapping_verified":False,
        "source_original_material_t_s_cb_register_offsets_verified":False,
        "actual_android_original_shader48_compilation_verified":False,
        "original_shader48_restored":False,
        "pc_and_android_pixel_parity_verified":False,
        "source_private_DXBC_hlsl_property_names_identifiers_or_chunk_bytes_exported":False,
        "phase_closed":False,
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
    print("GFX_MULTI037_SAFE_LINKED_DXBC_PUBLIC_CHUNK_CENSUS "+json.dumps(d,sort_keys=True))


if __name__=="__main__":main()
