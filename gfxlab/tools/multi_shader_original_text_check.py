#!/usr/bin/env python3
"""GFX-MULTI-021: inspect safe original shader text evidence and Material property parity.

All content is inspected privately in runner. No source text/asset/property
name/GUID/register id exported; only booleans and counts. This cannot establish
original ShaderLab or DX11 source material->register semantic mapping.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_material_texenv_bridge import original_material_texenv_sets
from gfxlab.tools.shears_texture_readiness import classify_standard

_REGISTER_PATTERN=re.compile(rb"\bregister\s*\(\s*[tsbu]\s*[0-9]+\s*\)",re.I)
_SCRIPT_TOKENS=(b"CGPROGRAM",b"HLSLPROGRAM",b"CGINCLUDE",b"HLSLINCLUDE")

def safe_embedded_script_evidence(raw):
    if raw is None:
        return dict(original_embedded_script_field_present=False,embedded_script_bytes=0,
            hlsl_or_cg_program_markers_found=False,register_syntax_marker_found=False,
            original_material_name_to_DX11_register_authoritatively_verified=False)
    if isinstance(raw,str):
        data=raw.encode("utf8",errors="ignore")
    elif isinstance(raw,(bytes,bytearray,memoryview)):
        data=bytes(raw)
    elif isinstance(raw,list) and all(type(x)==int and 0<=x<=255 for x in raw):
        data=bytes(raw)
    else:raise ValueError("UNEXPECTED_TYPED_SOURCE_SHADER_SCRIPT_DATA")
    if len(data)>20*1024*1024:raise ValueError("ORIGINAL_SCRIPT_TOO_LARGE_FOR_SAFE_TEXT_PROBE")
    upper=data.upper()
    markers=any(marker in upper for marker in _SCRIPT_TOKENS)
    registers=bool(_REGISTER_PATTERN.search(data))
    return dict(original_embedded_script_field_present=True,
        embedded_script_bytes=len(data),
        hlsl_or_cg_program_markers_found=markers,
        register_syntax_marker_found=registers,
        original_material_name_to_DX11_register_authoritatively_verified=False)

def bound_material_property_check(shader_properties,material_sets,bound_sets):
    if not isinstance(shader_properties,set) or len(material_sets)!=len(bound_sets):
        raise ValueError("UNSAFE_ORIGINAL_MATERIAL_PROPERTY_SHAPE")
    c=Counter()
    for names,bound in zip(material_sets,bound_sets):
        if not isinstance(names,set) or not isinstance(bound,set) or not bound.issubset(names):
            raise ValueError("ORIGINAL_BOUND_TEXENV_OUTSIDE_MATERIAL_SET")
        for name in names:
            if not isinstance(name,str):raise ValueError("UNEXPECTED_ORIGINAL_PROPERTY_NAME")
            c["stored_texenv_slots"]+=1
            c["stored_texenv_names_declared_in_shader"]+=int(name in shader_properties)
        for name in bound:
            c["bound_texenv_slots"]+=1
            c["bound_texenv_names_declared_in_shader"]+=int(name in shader_properties)
            role=classify_standard(name)
            c["bound_role_"+role if role in ("basecolor","normal","metallic") else "bound_role_other"]+=1
    return dict(c)

def audit(stage):
    entries,typed,_=all_model_entries(stage)
    if len(entries)!=6 or sum(len(x["materials"]) for x in entries)!=7:
        raise ValueError("SOURCE_MODEL_MATERIAL_CHAIN_DRIFT")
    keys={(m["shader_owner"],m["shader_pid"]) for x in entries for m in x["materials"]}
    if len(keys)!=1:raise ValueError("MIXED_ORIGINAL_SHADER_IDENTITY")
    owner,pid=next(iter(keys))
    obj=typed[owner].get(pid)
    if obj is None or obj.type.name!="Shader":raise ValueError("SOURCE_SHADER48_MISSING")
    typed_sh=obj.read_typetree(check_read=False)
    parsed=typed_sh.get("m_ParsedForm")
    if not isinstance(parsed,dict):raise ValueError("SOURCE_SHADER_PARSED_FORM_MISSING")
    props=parsed.get("m_PropInfo",{}).get("m_Props",[])
    if not isinstance(props,list):raise ValueError("SOURCE_PROPERTIES_MISSING")
    propnames=set()
    tex_propnames=set()
    for rec in props:
        if not isinstance(rec,dict) or not isinstance(rec.get("m_Name"),str):
            raise ValueError("MALFORMED_SOURCE_SHADER_PROPERTY")
        name=rec["m_Name"]
        propnames.add(name)
        if rec.get("m_Type")==4:tex_propnames.add(name)
    material_sets,bound_sets=original_material_texenv_sets(stage,typed)
    if len(material_sets)!=7:raise ValueError("SOURCE_MATERIAL_COUNT_DRIFT")
    materials=bound_material_property_check(propnames,material_sets,bound_sets)
    embedded=typed_sh.get("m_Script")
    if embedded is None:
        embedded=getattr(obj.read(),"m_Script",None)
    script=safe_embedded_script_evidence(embedded)
    pass_rows=parsed.get("m_SubShaders",[])
    if not isinstance(pass_rows,list) or len(pass_rows)!=2:
        raise ValueError("ORIGINAL_SUBSHADER_DRIFT")
    pcount=sum(len(x.get("m_Passes",[])) for x in pass_rows if isinstance(x,dict))
    if pcount!=7:raise ValueError("ORIGINAL_PASS_DRIFT")
    return dict(experiment="GFX-MULTI-021",source_sha=ZIP2_SHA,
        original_shader48_typed_source_verified=True,
        source_model_count=6,material_slots=7,shader_subshaders=2,shader_passes=7,
        original_shader_serialized_property_count=len(propnames),
        original_shader_texture_property_count=len(tex_propnames),
        original_material_shader_property_name_parity=materials,
        original_shader_text_evidence=script,
        independently_verified_original_property_name_to_DX11_t_s_register_map=False,
        original_shader_parameter_tables_missing_from_gfx020=True,
        original_CB_memory_offsets_verified=False,
        actual_android_original_shader_pixels_verified=False,
        proprietary_source_names_or_shader_code_exported=False,
        phase_closed=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI021_SAFE_SOURCE_PROPERTY_ORIGINAL_TEXT_EVIDENCE "+json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
