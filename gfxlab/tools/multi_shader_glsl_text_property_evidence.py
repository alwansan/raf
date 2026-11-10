#!/usr/bin/env python3
"""GFX-MULTI-034: inspect *unlinked* original GL-family Shader48 bytes privately.

UnityPy's public ShaderSubProgram exporter treats GLES/GLCore m_ProgramCode
as UTF-8 source text, which requires direct source inspection rather than a
leading #version assumption. Publish only counts, never the actual source,
private material names, shader identifiers, registers, original code or PPtrs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED, collect_linked_indices,
)
from gfxlab.tools.multi_shader_unused_program_families import program_family
from gfxlab.tools.multi_shader_material_texenv_bridge import original_material_texenv_sets

MAX_SHADER_TEXT_BYTES=16*1024*1024
UNIFORM_STMT=re.compile(r"\buniform\b[^;\r\n]{0,400};")
MAIN_FN=re.compile(r"\bvoid\s+main\s*\(")
VERSION_DIRECTIVE=re.compile(r"(?m)^[ \t]*#[ \t]*version\b")
GLSL_SAMPLER=re.compile(r"\bsampler(?:2D|3D|Cube|2DArray|CubeArray)\b")
GLSL_RESOURCE_DECL=re.compile(r"\buniform\b")
GLSL_STAGE_DIRECTIVE=re.compile(r"\b(?:VERTEX|FRAGMENT|SHADER_STAGE)\b")


def sanitize_comment_text(source):
    if not isinstance(source,str) or len(source)>MAX_SHADER_TEXT_BYTES:
        raise ValueError("SOURCE_GLSL_TEXT_LENGTH_OR_TYPE_INVALID")
    # Strip comments before comparing authored property labels, to avoid
    # interpreting commented-out properties as live GLSL resource declarations.
    no_block=re.sub(r"/\*.*?\*/", " ",source,flags=re.DOTALL)
    return re.sub(r"//[^\r\n]*", " ",no_block)


def safe_property_token_hits(text, names):
    """Internal exact identifier boundary matching; no names leave function."""
    if not isinstance(text,str) or not isinstance(names,set):
        raise ValueError("SOURCE_TEXT_OR_PROPERTY_SHAPE_INVALID")
    result=set()
    for name in names:
        if (not isinstance(name,str) or not 1<=len(name)<=128
                or not re.fullmatch(r"[_A-Za-z][_A-Za-z0-9]*",name)):
            raise ValueError("SOURCE_PROPERTY_IDENTIFIER_INVALID")
        pattern=r"(?<![_A-Za-z0-9])"+re.escape(name)+r"(?![_A-Za-z0-9])"
        if re.search(pattern,text):
            result.add(name)
    return result


def bounded_glsl_evidence(code,properties,texture_properties,material_bound):
    if not isinstance(code,bytes) or len(code)>MAX_SHADER_TEXT_BYTES:
        raise ValueError("ORIGINAL_GL_PROGRAM_TEXT_TOO_LARGE")
    try:
        text=code.decode("utf-8","strict")
    except UnicodeDecodeError:
        return {
            "strict_utf8":False,
            "embedded_null_byte":b"\x00" in code,
            "glsl_version_directive":False,
            "main_function":False,
            "uniform_statement_present":False,
            "sampler_declaration_present":False,
            "stage_directive_present":False,
            "authored_property_token_matches":set(),
            "original_texture_property_token_matches":set(),
            "bound_material_property_token_matches":set(),
            "authored_property_uniform_matches":set(),
            "bound_material_uniform_matches":set(),
        }
    clean=sanitize_comment_text(text)
    uniform_fragments="\n".join(x.group(0) for x in UNIFORM_STMT.finditer(clean))
    all_props=safe_property_token_hits(clean,properties)
    tex=safe_property_token_hits(clean,texture_properties)
    bound=safe_property_token_hits(clean,material_bound)
    uniform_props=safe_property_token_hits(uniform_fragments,properties)
    uniform_bound=safe_property_token_hits(uniform_fragments,material_bound)
    return {
        "strict_utf8":True,
        "embedded_null_byte":"\x00" in text,
        "glsl_version_directive":bool(VERSION_DIRECTIVE.search(clean)),
        "main_function":bool(MAIN_FN.search(clean)),
        "uniform_statement_present":bool(GLSL_RESOURCE_DECL.search(clean)),
        "sampler_declaration_present":bool(GLSL_SAMPLER.search(clean)),
        "stage_directive_present":bool(GLSL_STAGE_DIRECTIVE.search(clean)),
        "authored_property_token_matches":all_props,
        "original_texture_property_token_matches":tex,
        "bound_material_property_token_matches":bound,
        "authored_property_uniform_matches":uniform_props,
        "bound_material_uniform_matches":uniform_bound,
    }


def analyze_programs(programs,linked,properties,texture_properties,material_bound):
    if len(programs)!=EXPECTED_COMPILED or len(linked)!=EXPECTED_REFERENCED:
        raise ValueError("SOURCE_COMPILED_PROGRAM_TABLE_OR_LINK_COUNT_CHANGED")
    if not texture_properties.issubset(properties) or not material_bound.issubset(texture_properties):
        raise ValueError("SOURCE_MATERIAL_TEXTURE_PROPERTY_SET_MISMATCH")
    aggregates={
        f:Counter({
            "candidate_entries":0,
            "strict_utf8_decoded":0,
            "invalid_utf8_or_binary":0,
            "embedded_nul":0,
            "glsl_version_directive":0,
            "main_function":0,
            "uniform_statement_present":0,
            "sampler_declaration_present":0,
            "stage_directive_present":0,
            "programs_with_authored_property_tokens":0,
            "programs_with_bound_material_tokens":0,
            "programs_with_authored_uniform_tokens":0,
            "programs_with_bound_material_uniform_tokens":0,
        }) for f in ("GLES","GLCORE")
    }
    unique={f:{name:set() for name in (
        "authored_property_token_matches",
        "original_texture_property_token_matches",
        "bound_material_property_token_matches",
        "authored_property_uniform_matches",
        "bound_material_uniform_matches")}
        for f in ("GLES","GLCORE")}
    for idx,program in enumerate(programs):
        if idx in linked:
            continue
        family=program_family(program.m_ProgramType.name)
        if family not in aggregates:
            continue
        code=bytes(program.m_ProgramCode)
        if not code:
            continue
        row=bounded_glsl_evidence(code,properties,texture_properties,material_bound)
        a=aggregates[family]
        a["candidate_entries"]+=1
        a["strict_utf8_decoded"]+=int(row["strict_utf8"])
        a["invalid_utf8_or_binary"]+=int(not row["strict_utf8"])
        a["embedded_nul"]+=int(row["embedded_null_byte"])
        for flag in ("glsl_version_directive","main_function",
                     "uniform_statement_present","sampler_declaration_present",
                     "stage_directive_present"):
            a[flag]+=int(row[flag])
        for propname in unique[family]:
            unique[family][propname].update(row[propname])
        a["programs_with_authored_property_tokens"]+=int(bool(row["authored_property_token_matches"]))
        a["programs_with_bound_material_tokens"]+=int(bool(row["bound_material_property_token_matches"]))
        a["programs_with_authored_uniform_tokens"]+=int(bool(row["authored_property_uniform_matches"]))
        a["programs_with_bound_material_uniform_tokens"]+=int(bool(row["bound_material_uniform_matches"]))
    if aggregates["GLES"]["candidate_entries"]!=139 or aggregates["GLCORE"]["candidate_entries"]!=120:
        raise ValueError("SOURCE_GLES_GLCORE_PROGRAM_COUNT_CHANGED")
    return {
        f:{
            **dict(aggregates[f]),
            "unique_authored_property_tokens":len(unique[f]["authored_property_token_matches"]),
            "unique_texture_property_tokens":len(unique[f]["original_texture_property_token_matches"]),
            "unique_bound_material_property_tokens":len(unique[f]["bound_material_property_token_matches"]),
            "unique_authored_uniform_property_tokens":len(unique[f]["authored_property_uniform_matches"]),
            "unique_bound_material_uniform_property_tokens":len(unique[f]["bound_material_uniform_matches"]),
        } for f in ("GLES","GLCORE")
    }


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    obj=_locate_shader(entries,typed)
    tree=obj.read_typetree(check_read=False)
    parsed=tree.get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("ORIGINAL_SHADER48_PARSED_FORM_MISSING")
    raw_props=parsed.get("m_PropInfo",{}).get("m_Props",[])
    if not isinstance(raw_props,list) or len(raw_props)!=27:
        raise ValueError("ORIGINAL_SHADER48_PROPERTY_COUNT_DRIFT")
    all_names=set()
    tex_names=set()
    for prop in raw_props:
        if not isinstance(prop,dict) or not isinstance(prop.get("m_Name"),str):
            raise ValueError("ORIGINAL_SOURCE_SHADER_PROPERTY_SHAPE_INVALID")
        name=prop["m_Name"]
        if name in all_names:
            raise ValueError("ORIGINAL_SHADER48_PROPERTY_DUPLICATE")
        all_names.add(name)
        if prop.get("m_Type")==4:
            tex_names.add(name)
    if len(tex_names)!=9:
        raise ValueError("ORIGINAL_SHADER48_TEXTURE_PROPERTIES_CHANGED")
    _material,bound=original_material_texenv_sets(stage,typed)
    if len(bound)!=7 or sum(map(len,bound))!=21:
        raise ValueError("SOURCE_MATERIAL_BOUND_TEXTURE_LINK_COUNT_DRIFT")
    bound_names=set().union(*bound)
    if not bound_names.issubset(tex_names):
        raise ValueError("BOUND_MATERIAL_TEXENV_NOT_A_SHADER_TEXTURE")
    programs=__import__(
        "gfxlab.tools.multi_shader_one_pass_spirv",fromlist=["compiled_programs"]).compiled_programs(obj)
    linked=collect_linked_indices(parsed.get("m_SubShaders"),programs)
    counts=analyze_programs(programs,linked,all_names,tex_names,bound_names)
    return {
        "experiment":"GFX-MULTI-034",
        "original_source_sha":ZIP2_SHA,
        "original_shader48_properties":len(all_names),
        "original_shader48_texture_properties":len(tex_names),
        "original_bound_texture_roles":sum(map(len,bound)),
        "distinct_bound_shader_property_labels":len(bound_names),
        "gl_family_private_text_evidence":counts,
        "candidate_text_has_exact_original_pass_variant_mapping":False,
        "candidate_original_glsl_on_adreno_compiled":False,
        "source_glsl_material_semantic_bridge_verified":False,
        "dx11_material_to_t_s_cb_register_bridge_verified":False,
        "original_shader48_restored":False,
        "owner_pc_pixel_parity_verified":False,
        "raw_private_glsl_or_shader_names_exported":False,
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
    print("GFX_MULTI034_SAFE_GLSL_TEXT_EVIDENCE "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
