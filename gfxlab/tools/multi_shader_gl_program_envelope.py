#!/usr/bin/env python3
"""GFX-MULTI-036: source-private Shader48 compiler platform/opaque GL payload audit.

This is a *bounded evidence census*, not a GL binary resource parser. Even
matching a self-length header or a keyword signature cannot establish that an
unlinked GLES/GLCore entry belongs to any original Shader48 Pass/Material.
Never publish raw source shader code, original property names, keyword values,
object pointers, raw signature digests or original numeric shader registers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter,defaultdict
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED,EXPECTED_REFERENCED,EXPECTED_UNUSED,collect_linked_indices,
)
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs
from gfxlab.tools.multi_shader_unused_program_families import program_family

MAX_CODE=16*1024*1024
ASCII_BYTES=set(range(32,127)) | {9,10,13}
FAMILIES=("GLES","GLCORE")
SIZE_BUCKETS=("1_to_31","32_to_127","128_to_511","512_to_4095",
              "4096_to_65535","65536_and_more")
ASCII_BUCKETS=("0_to_24_percent","25_to_49_percent",
               "50_to_74_percent","75_to_100_percent")
COMPILER_PLATFORMS={"GLES":{"kShaderCompPlatformGLES20","kShaderCompPlatformGLES3Plus"},
                    "GLCORE":{"kShaderCompPlatformOpenGLCore"}}


def public_shader_compiler_platform(platforms):
    """Enum is from public UnityPy ShaderCompilerPlatform, not a guessed code."""
    from UnityPy.enums.ShaderCompilerPlatform import ShaderCompilerPlatform
    if not isinstance(platforms,(tuple,list)) or len(platforms)!=1:
        raise ValueError("ORIGINAL_COMPILER_PLATFORM_COUNT_NOT_ONE")
    raw=platforms[0]
    try:
        label=ShaderCompilerPlatform(int(raw)).name
    except (ValueError,TypeError,AttributeError) as ex:
        raise ValueError("ORIGINAL_COMPILER_PLATFORM_NOT_IN_PUBLIC_ENUM") from ex
    return label


def safe_keywords(program):
    """Keyword names are held only in ephemeral runner-private tuples."""
    raw=getattr(program,"m_Keywords",None)
    if not isinstance(raw,list) or len(raw)>1024:
        raise ValueError("ORIGINAL_PROGRAM_KEYWORD_TABLE_INVALID")
    if any(not isinstance(x,str) or not 1<=len(x)<=256 for x in raw):
        raise ValueError("ORIGINAL_PROGRAM_KEYWORD_INVALID")
    if len(raw)!=len(set(raw)):
        raise ValueError("ORIGINAL_PROGRAM_DUPLICATE_KEYWORDS")
    return tuple(sorted(raw))


def length_bucket(n):
    if type(n) is not int or n<=0 or n>MAX_CODE:
        raise ValueError("ORIGINAL_CODE_SIZE_OUT_OF_BOUNDS")
    if n<32:return "1_to_31"
    if n<128:return "32_to_127"
    if n<512:return "128_to_511"
    if n<4096:return "512_to_4095"
    if n<65536:return "4096_to_65535"
    return "65536_and_more"


def ascii_bucket(data):
    if not isinstance(data,bytes) or not data or len(data)>MAX_CODE:
        raise ValueError("ORIGINAL_CODE_BYTES_INVALID")
    printable=sum(b in ASCII_BYTES for b in data)
    percent=100*printable//len(data)
    if percent<25:return "0_to_24_percent"
    if percent<50:return "25_to_49_percent"
    if percent<75:return "50_to_74_percent"
    return "75_to_100_percent"


def bounded_envelope_flags(code):
    """Only syntactic headers/length equality. Not proven Unity binary formats."""
    if not isinstance(code,bytes) or not 0<len(code)<=MAX_CODE:
        raise ValueError("ORIGINAL_ENVELOPE_CODE_OUT_OF_BOUNDS")
    flags={
        "u32le_first_word_equals_total_bytes":False,
        "u32le_first_word_equals_trailing_bytes":False,
        "u32le_second_word_equals_trailing_bytes":False,
        "known_leading_gzip_magic":code.startswith(b"\x1f\x8b"),
        "known_leading_zlib_header":len(code)>=2 and code[:2] in (
            b"\x78\x01",b"\x78\x9c",b"\x78\xda"),
        "known_leading_lz4_frame_magic":code.startswith(b"\x04\x22\x4d\x18"),
        "known_leading_spirv_magic":code.startswith(b"\x03\x02\x23\x07"),
        "known_leading_dxbc_magic":code.startswith(b"DXBC"),
    }
    if len(code)>=4:
        head=struct.unpack_from("<I",code,0)[0]
        flags["u32le_first_word_equals_total_bytes"]=head==len(code)
        flags["u32le_first_word_equals_trailing_bytes"]=head==len(code)-4
    if len(code)>=8:
        head=struct.unpack_from("<I",code,4)[0]
        flags["u32le_second_word_equals_trailing_bytes"]=head==len(code)-8
    return flags


def version_bucket(value):
    if type(value) is not int:
        raise ValueError("ORIGINAL_SUBPROGRAM_VERSION_INVALID")
    if 202012090<=value<204000000:return "2021_2_or_newer"
    if 201806140<=value<202012090:return "2019_to_2021_1"
    if 201509030<=value<201806140:return "2015_to_2018"
    return "unknown"


def inspect_candidates(programs,linked,shader_compiler_platform):
    if len(programs)!=EXPECTED_COMPILED or len(linked)!=EXPECTED_REFERENCED:
        raise ValueError("ORIGINAL_SHADER48_PROGRAM_LINK_TABLE_DRIFT")
    if any(type(idx) is not int or not 0<=idx<len(programs) for idx in linked):
        raise ValueError("ORIGINAL_SHADER48_LINK_INDICES_INVALID")
    exact_linked_keywords=Counter(safe_keywords(programs[idx]) for idx in linked)
    totals={}
    for f in FAMILIES:
        totals[f]=Counter({
            "candidate_entries":0,
            "nonempty_keyword_signature_entries":0,
            "nonempty_keyword_signature_matches_linked_dx11":0,
            "nonempty_keyword_signature_unique_linked_match":0,
            "platform_family_matches_original_compiler_platform":0,
        })
    sizes={f:Counter({key:0 for key in SIZE_BUCKETS}) for f in FAMILIES}
    ratios={f:Counter({key:0 for key in ASCII_BUCKETS}) for f in FAMILIES}
    versions={f:Counter({key:0 for key in (
        "2015_to_2018","2019_to_2021_1","2021_2_or_newer","unknown")}) for f in FAMILIES}
    envelopes={f:Counter() for f in FAMILIES}
    digest_sets={f:set() for f in FAMILIES}
    keyword_sets={f:set() for f in FAMILIES}
    keyword_nonempty_sets={f:set() for f in FAMILIES}
    for index,p in enumerate(programs):
        if index in linked:continue
        family=program_family(p.m_ProgramType.name)
        if family not in FAMILIES:continue
        code=bytes(p.m_ProgramCode)
        if not code:continue
        if len(code)>MAX_CODE:raise ValueError("ORIGINAL_GL_CODE_TOO_LARGE")
        totals[family]["candidate_entries"]+=1
        sizes[family][length_bucket(len(code))]+=1
        ratios[family][ascii_bucket(code)]+=1
        versions[family][version_bucket(p.m_Version)]+=1
        for key,yes in bounded_envelope_flags(code).items():
            envelopes[family][key]+=int(yes)
        digest_sets[family].add(hashlib.sha256(code).digest())
        signature=safe_keywords(p)
        keyword_sets[family].add(signature)
        if signature:
            keyword_nonempty_sets[family].add(signature)
            totals[family]["nonempty_keyword_signature_entries"]+=1
            if signature in exact_linked_keywords:
                totals[family]["nonempty_keyword_signature_matches_linked_dx11"]+=1
                if exact_linked_keywords[signature]==1:
                    totals[family]["nonempty_keyword_signature_unique_linked_match"]+=1
        totals[family]["platform_family_matches_original_compiler_platform"]+=int(
            shader_compiler_platform in COMPILER_PLATFORMS[family])
    if totals["GLES"]["candidate_entries"]!=139 or totals["GLCORE"]["candidate_entries"]!=120:
        raise ValueError("SOURCE_GLES_GLCORE_TABLE_CHANGED")
    output={}
    for family in FAMILIES:
        total=totals[family]["candidate_entries"]
        if not all(sum(x.values())==total for x in (
            sizes[family],ratios[family],versions[family])):
            raise ValueError("SOURCE_GL_PROGRAM_SHAPE_ACCOUNTING_FAILED")
        output[family]={
            **dict(totals[family]),
            "source_code_byte_size_buckets":dict(sizes[family]),
            "source_code_printable_byte_ratio_buckets":dict(ratios[family]),
            "public_subprogram_version_era_buckets":dict(versions[family]),
            "syntactic_only_envelope_candidate_counts":dict(envelopes[family]),
            "distinct_private_code_payload_count":len(digest_sets[family]),
            "distinct_private_keyword_signature_count":len(keyword_sets[family]),
            "distinct_nonempty_keyword_signature_count":len(keyword_nonempty_sets[family]),
            "keyword_match_proves_original_pass_or_material_binding":False,
            "raw_keyword_names_or_digest_bytes_exported":False,
        }
    return output


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    obj=_locate_shader(entries,typed)
    source=obj.read()
    platform=public_shader_compiler_platform(source.platforms)
    typed_tree=obj.read_typetree(check_read=False)
    subs=typed_tree.get("m_ParsedForm",{}).get("m_SubShaders")
    programs=compiled_programs(obj)
    linked=collect_linked_indices(subs,programs)
    report=inspect_candidates(programs,linked,platform)
    return {
        "experiment":"GFX-MULTI-036",
        "original_zip2_sha":ZIP2_SHA,
        "original_shader48_compiled_blob_platform_name_public_enum":platform,
        "original_compiled_blob_has_exactly_one_platform":True,
        "original_compiled_table_entries":len(programs),
        "original_exact_linked_dx11_indices":len(linked),
        "unreferenced_original_gl_typed_programs":report,
        "original_compiled_platform_proves_unlinked_GL_programs_usable_on_Android":False,
        "syntactic_length_magic_or_keyword_matches_are_resource_reflection":False,
        "authentic_original_gl_stage_to_pass_variant_link_verified":False,
        "material_to_original_t_s_cb_register_offsets_verified":False,
        "actual_android_original_shader48_compilation_verified":False,
        "original_shader48_restored":False,
        "pc_vs_android_original_shader_pixel_parity_verified":False,
        "raw_private_shader_bytes_names_digests_ids_or_offsets_exported":False,
        "phase_closed":False,
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
    print("GFX_MULTI036_SAFE_ORIGINAL_GL_PLATFORM_AND_ENVELOPE "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
