#!/usr/bin/env python3
"""GFX-MULTI-033: private source-only unused Shader48 program-platform census.

No private DXBC/GLSL/SPIR-V bytes, shader names, original object IDs,
original property names, linked indices or user data leave the CI runner.
A program type or code signature is not sufficient to prove a material/pass
link or equivalence to original Shader48 on Android.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import (
    _locate_shader, collect_stage_variant_rows,
)
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED, EXPECTED_UNUSED,
    collect_linked_indices,
)

FAMILIES=("D3D9","D3D11","GLES","GLCORE","VULKAN","METAL","CONSOLE","OTHER")
STAGES=("VERTEX","FRAGMENT","COMPUTE","GEOMETRY","HULL","DOMAIN","OTHER")
MAX_CODE_BYTES=16*1024*1024
MAGIC_SPIRV=b"\x03\x02\x23\x07"


def program_family(label):
    """Public generic enum class, never publish the source shader/program name."""
    if not isinstance(label,str) or not label:
        raise ValueError("SOURCE_PROGRAM_TYPE_LABEL_INVALID")
    name=label.upper()
    if "DX11" in name or "D3D11" in name or "DIRECT3D11" in name:
        return "D3D11"
    if "DX9" in name or "D3D9" in name or "DIRECT3D9" in name:
        return "D3D9"
    if "GLES" in name or "OPENGL_ES" in name:
        return "GLES"
    if "GLCORE" in name or "OPENGLCORE" in name or "GLSL" in name:
        return "GLCORE"
    if "VULKAN" in name or "SPIRV" in name:
        return "VULKAN"
    if "METAL" in name:
        return "METAL"
    if any(x in name for x in ("PS4","PS5","XBOX","SWITCH","WII","CONSOLE")):
        return "CONSOLE"
    return "OTHER"


def stage_family(label):
    if not isinstance(label,str) or not label:
        raise ValueError("SOURCE_STAGE_TYPE_LABEL_INVALID")
    name=label.upper()
    if "VERTEX" in name: return "VERTEX"
    if "PIXEL" in name or "FRAGMENT" in name: return "FRAGMENT"
    if "COMPUTE" in name: return "COMPUTE"
    if "GEOMETRY" in name: return "GEOMETRY"
    if "HULL" in name: return "HULL"
    if "DOMAIN" in name: return "DOMAIN"
    return "OTHER"


def recognizable_prefix(code):
    """Strict leading header only; OTHER means unknown/wrapped, not invalid."""
    if code.startswith(MAGIC_SPIRV):
        return "SPIRV_LEADING_MAGIC"
    prefix=code[:64].lstrip(b"\xef\xbb\xbf\r\n\t ")
    if prefix.startswith(b"#version "):
        return "GLSL_LEADING_VERSION"
    if code.startswith(b"DXBC") and len(code)>=36:
        return "DXBC_LEADING_MAGIC_UNVALIDATED"
    return "UNKNOWN_OR_WRAPPED"


def alt_pass_program_links(subshaders,programs,already_linked):
    """Inspect only actual alternative original Pass prog* stage fields.

    A raw reference is counted only if its declared type equals the real
    compiled table program type. No inference by numerical proximity or
    model/material naming is permitted.
    """
    extra_fields=0
    extra_rows=0
    to_unused=set()
    to_existing=set()
    if len(subshaders)!=2 or [len(s.get("m_Passes",[])) for s in subshaders]!=[4,3]:
        raise ValueError("SOURCE_ALTERNATE_PASS_TOPOLOGY_DRIFT")
    for sub in subshaders:
        for original_pass in sub["m_Passes"]:
            for field,stage in original_pass.items():
                if (not isinstance(field,str) or
                        not (field.startswith("prog") and
                             len(field)>4 and field[4].isupper()) or
                        field in ("progVertex","progFragment")):
                    continue
                extra_fields+=1
                if not isinstance(stage,dict):
                    raise ValueError("SOURCE_ALTERNATE_PASS_FIELD_NOT_OBJECT")
                rows=collect_stage_variant_rows(stage)
                for row in rows:
                    index=row.get("m_BlobIndex")
                    typ=row.get("m_GpuProgramType")
                    if type(index) is not int or not 0<=index<len(programs):
                        raise ValueError("SOURCE_ALTERNATE_PASS_INDEX_INVALID")
                    if type(typ) is not int or typ!=int(programs[index].m_ProgramType):
                        raise ValueError("SOURCE_ALTERNATE_PASS_TYPE_MISMATCH")
                    extra_rows+=1
                    if index in already_linked:
                        to_existing.add(index)
                    else:
                        to_unused.add(index)
    return {
        "other_original_pass_program_field_rows":extra_fields,
        "other_original_pass_stage_variant_rows":extra_rows,
        "other_original_pass_unique_existing_indices":len(to_existing),
        "other_original_pass_unique_previously_unused_indices":len(to_unused),
    }


def inspect_unused_platforms(programs,linked):
    if len(programs)!=EXPECTED_COMPILED:
        raise ValueError("SOURCE_COMPILED_PROGRAM_TABLE_CHANGED")
    if len(linked)!=EXPECTED_REFERENCED or any(
            type(idx) is not int or not 0<=idx<len(programs) for idx in linked):
        raise ValueError("SOURCE_LINKED_INDEX_SET_CHANGED")
    fam=Counter({f:0 for f in FAMILIES})
    stage=Counter({f:0 for f in STAGES})
    prefix=Counter({p:0 for p in (
        "SPIRV_LEADING_MAGIC","GLSL_LEADING_VERSION",
        "DXBC_LEADING_MAGIC_UNVALIDATED","UNKNOWN_OR_WRAPPED")})
    empty=0
    unused=0
    for idx,program in enumerate(programs):
        if idx in linked:
            continue
        unused+=1
        if program is None or not hasattr(program,"m_ProgramType"):
            raise ValueError("SOURCE_UNUSED_PROGRAM_MISSING_TYPE")
        label=program.m_ProgramType.name
        kind=program_family(label)
        code=bytes(program.m_ProgramCode)
        if len(code)>MAX_CODE_BYTES:
            raise ValueError("SOURCE_UNUSED_PROGRAM_UNBOUNDED")
        if not code:
            empty+=1
            continue
        if kind=="D3D11":
            raise ValueError("SOURCE_UNEXPECTED_UNREFERENCED_D3D11_PROGRAM")
        fam[kind]+=1
        stage[stage_family(label)]+=1
        prefix[recognizable_prefix(code)]+=1
    if unused!=EXPECTED_UNUSED or empty!=112 or unused-empty!=269:
        raise ValueError("SOURCE_UNUSED_PROGRAM_CENSUS_DRIFT")
    if sum(fam.values())!=269 or sum(stage.values())!=269 or sum(prefix.values())!=269:
        raise ValueError("SOURCE_UNUSED_PROGRAM_BUCKET_TOTAL_INVALID")
    return {
        "unused_total":unused,
        "unused_empty_code":empty,
        "unused_non_d3d11_code":unused-empty,
        "nonempty_platform_type_families":dict(fam),
        "nonempty_shader_stage_type_families":dict(stage),
        "nonempty_strict_leading_payload_signatures":dict(prefix),
        "type_label_gles_or_vulkan_candidate_count":fam["GLES"]+fam["VULKAN"],
        "strict_leading_glsl_or_spirv_magic_count":(
            prefix["GLSL_LEADING_VERSION"]+prefix["SPIRV_LEADING_MAGIC"]),
        "type_or_header_proves_original_android_pass_link":False,
    }


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    shader=_locate_shader(entries,typed)
    tree=shader.read_typetree(check_read=False)
    parsed=tree.get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("SOURCE_PARSED_SHADER48_MISSING")
    subs=parsed.get("m_SubShaders")
    programs=compiled_programs(shader)
    refs=collect_linked_indices(subs,programs)
    unused=inspect_unused_platforms(programs,refs)
    alternate=alt_pass_program_links(subs,programs,refs)
    return {
        "experiment":"GFX-MULTI-033",
        "original_zip2_source_sha":ZIP2_SHA,
        "source_shader_count":1,
        "original_shader48_subshaders":2,
        "original_shader48_passes":7,
        "source_compiled_program_entries":len(programs),
        "unique_original_vs_fs_program_indices":len(refs),
        "unreferenced_programs":unused,
        "alternate_authentic_original_pass_links":alternate,
        "unreferenced_source_program_can_be_assumed_android_gles":False,
        "material_property_to_register_or_cb_byte_offset_verified":False,
        "original_shader48_android_glsl_runtime_verified":False,
        "original_shader48_restored":False,
        "pc_vs_adreno_pixel_parity_verified":False,
        "raw_shaders_values_source_names_or_private_ids_exported":False,
        "phase_closed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI033_SAFE_SOURCE_PROGRAM_FAMILIES "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
