#!/usr/bin/env python3
"""GFX-MULTI-035: original unlinked GLES/GLCore code byte markers, source-private.

Inspect bounded source payload bytes in runner only; emit anonymous counts.
Markers and property-name appearances in binary data are not GLSL correctness,
uniform binding, source-pass/keyword link, Adreno pixels or shader restoration.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs
from gfxlab.tools.multi_shader_unreferenced_reflection import collect_linked_indices,EXPECTED_REFERENCED
from gfxlab.tools.multi_shader_unused_program_families import program_family
from gfxlab.tools.multi_shader_material_texenv_bridge import original_material_texenv_sets

MAX_CODE=16*1024*1024
VERSION=re.compile(rb"#[ \t]*version[ \t]+[0-9]{2,4}\b")
MAIN=re.compile(rb"\bvoid[ \t\r\n]+main[ \t]*\(")
UNIFORM=re.compile(rb"\buniform\b")
SAMPLER=re.compile(rb"\bsampler(?:2D|3D|Cube|2DArray|CubeArray)\b")
PRINTABLE=re.compile(rb"[\t\n\r\x20-\x7e]{16,}")
UNIFORM_LINE=re.compile(rb"\buniform\b[^\r\n;]{0,400};")


def boundary_mentions(code,names):
    if not isinstance(code,bytes) or not isinstance(names,set):
        raise ValueError("SOURCE_BINARY_PROPERTY_INPUT_MALFORMED")
    out=set()
    for name in names:
        if (not isinstance(name,str) or len(name)>128 or
                not re.fullmatch(r"[_A-Za-z][_A-Za-z0-9]*",name)):
            raise ValueError("ORIGINAL_PROPERTY_IDENTIFIER_INVALID")
        label=name.encode("ascii")
        if re.search(rb"(?<![_A-Za-z0-9])"+re.escape(label)+rb"(?![_A-Za-z0-9])",code):
            out.add(name)
    return out


def marker_offset_bin(code,match):
    if match is None:return "absent"
    pos=match.start()
    if pos<64:return "first_64_bytes"
    if pos<4096:return "first_4096_bytes"
    return "later_than_4096_bytes"


def scan_binary(code,props,tex_props,bound):
    if not isinstance(code,bytes) or not 0<len(code)<=MAX_CODE:
        raise ValueError("SOURCE_PROGRAM_BINARY_SIZE_INVALID")
    text_spans=[len(m.group(0)) for m in PRINTABLE.finditer(code)]
    ver=VERSION.search(code)
    uniform=UNIFORM.search(code)
    main=MAIN.search(code)
    sampler=SAMPLER.search(code)
    allprops=boundary_mentions(code,props)
    texture=boundary_mentions(code,tex_props)
    bound_names=boundary_mentions(code,bound)
    uniform_source=b"\n".join(m.group(0) for m in UNIFORM_LINE.finditer(code))
    bound_decl=boundary_mentions(uniform_source,bound)
    return {
        "embedded_nul":b"\x00" in code,
        "glsl_version_marker_anywhere":ver is not None,
        "glsl_version_offset_bin":marker_offset_bin(code,ver),
        "main_function_marker_anywhere":main is not None,
        "uniform_token_anywhere":uniform is not None,
        "sampler_token_anywhere":sampler is not None,
        "printable_ascii_window_32_or_more":any(x>=32 for x in text_spans),
        "printable_ascii_window_128_or_more":any(x>=128 for x in text_spans),
        "printable_ascii_window_512_or_more":any(x>=512 for x in text_spans),
        "printable_ascii_window_4096_or_more":any(x>=4096 for x in text_spans),
        "original_property_tokens":allprops,
        "original_texture_property_tokens":texture,
        "original_bound_property_tokens":bound_names,
        "uniform_line_bound_property_tokens":bound_decl,
    }


def inspect(programs,linked,props,tex_props,bound):
    if len(programs)!=1656 or len(linked)!=EXPECTED_REFERENCED:
        raise ValueError("SOURCE_COMPILED_LINK_SHAPE_DRIFT")
    if not bound.issubset(tex_props) or not tex_props.issubset(props):
        raise ValueError("SOURCE_SHADER_PROPERTY_SETS_INVALID")
    group={}
    for f in ("GLES","GLCORE"):
        group[f]=Counter({
            "source_programs":0,
            "embedded_nul":0,
            "glsl_version_marker_anywhere":0,
            "main_function_marker_anywhere":0,
            "uniform_token_anywhere":0,
            "sampler_token_anywhere":0,
            "printable_ascii_window_32_or_more":0,
            "printable_ascii_window_128_or_more":0,
            "printable_ascii_window_512_or_more":0,
            "printable_ascii_window_4096_or_more":0,
            "programs_with_authored_property_tokens":0,
            "programs_with_bound_property_tokens":0,
            "programs_with_bound_uniform_line_tokens":0,
        })
    union={f:{k:set() for k in (
        "original_property_tokens","original_texture_property_tokens",
        "original_bound_property_tokens","uniform_line_bound_property_tokens")}
        for f in group}
    offsets={f:Counter({k:0 for k in (
        "absent","first_64_bytes","first_4096_bytes","later_than_4096_bytes")})
        for f in group}
    for idx,prog in enumerate(programs):
        if idx in linked:continue
        family=program_family(prog.m_ProgramType.name)
        if family not in group or not prog.m_ProgramCode:continue
        row=scan_binary(bytes(prog.m_ProgramCode),props,tex_props,bound)
        c=group[family]
        c["source_programs"]+=1
        for key in (
            "embedded_nul","glsl_version_marker_anywhere",
            "main_function_marker_anywhere","uniform_token_anywhere",
            "sampler_token_anywhere","printable_ascii_window_32_or_more",
            "printable_ascii_window_128_or_more",
            "printable_ascii_window_512_or_more","printable_ascii_window_4096_or_more"):
            c[key]+=int(row[key])
        offsets[family][row["glsl_version_offset_bin"]]+=1
        for key in union[family]:union[family][key].update(row[key])
        c["programs_with_authored_property_tokens"]+=int(bool(row["original_property_tokens"]))
        c["programs_with_bound_property_tokens"]+=int(bool(row["original_bound_property_tokens"]))
        c["programs_with_bound_uniform_line_tokens"]+=int(bool(row["uniform_line_bound_property_tokens"]))
    if group["GLES"]["source_programs"]!=139 or group["GLCORE"]["source_programs"]!=120:
        raise ValueError("SOURCE_GL_TYPED_COUNT_DRIFT")
    return {
        family:{
            **dict(counter),
            "glsl_version_offset_buckets":dict(offsets[family]),
            "unique_original_property_tokens":len(union[family]["original_property_tokens"]),
            "unique_original_texture_property_tokens":len(union[family]["original_texture_property_tokens"]),
            "unique_original_bound_property_tokens":len(union[family]["original_bound_property_tokens"]),
            "unique_bound_uniform_line_property_tokens":len(union[family]["uniform_line_bound_property_tokens"]),
        } for family,counter in group.items()
    }


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    obj=_locate_shader(entries,typed)
    parsed=obj.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(parsed,dict):raise ValueError("SOURCE_SHADER_PARSED_FORM_MISSING")
    records=parsed.get("m_PropInfo",{}).get("m_Props",[])
    if len(records)!=27:raise ValueError("SOURCE_SHADER_PROPERTY_COUNT_CHANGED")
    props=set()
    tex=set()
    for p in records:
        if not isinstance(p,dict) or not isinstance(p.get("m_Name"),str):
            raise ValueError("SOURCE_SHADER_PROPERTY_INVALID")
        props.add(p["m_Name"])
        if p.get("m_Type")==4:tex.add(p["m_Name"])
    if len(props)!=27 or len(tex)!=9:raise ValueError("SOURCE_PROPERTY_IDENTITY_DRIFT")
    _,original_bound=original_material_texenv_sets(stage,typed)
    if len(original_bound)!=7 or sum(map(len,original_bound))!=21:
        raise ValueError("SOURCE_MATERIAL_BOUND_TEXENV_DRIFT")
    bound=set().union(*original_bound)
    program=compiled_programs(obj)
    linked=collect_linked_indices(parsed.get("m_SubShaders"),program)
    return {
        "experiment":"GFX-MULTI-035","original_zip2_sha":ZIP2_SHA,
        "original_shader48_property_names_count":len(props),
        "original_texture_properties_count":len(tex),
        "original_bound_material_property_names_count":len(bound),
        "candidate_source_binary_marker_census":inspect(program,linked,props,tex,bound),
        "program_to_exact_original_pass_variant_verified":False,
        "material_property_to_actual_program_uniform_binding_verified":False,
        "original_shader48_android_gpu_compilation_verified":False,
        "original_shader48_restored":False,
        "pc_device_pixel_parity_verified":False,
        "raw_shaders_property_names_source_values_or_bytes_exported":False,
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
    print("GFX_MULTI035_SAFE_BYTE_MARKER_CENSUS "+json.dumps(d,sort_keys=True))


if __name__=="__main__":main()
