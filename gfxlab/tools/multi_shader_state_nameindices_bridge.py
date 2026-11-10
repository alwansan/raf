#!/usr/bin/env python3
"""GFX-MULTI-030S: exact original Shader48 Pass named states vs NameIndices.

Only safe counts leave runner: never publish Shader48 names/IDs, shader code,
textures, source float values, GPU register ids, or material keyword strings.
Name membership does NOT prove effective render state nor material->CB binding.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_state_material_float_link import (
    normalize_private_state_name,private_float_maps
)
from gfxlab.tools.multi_material_texture_semantics import _material_keys
from gfxlab.tools.multi_sevenpass_state_enum_semantics import STATE_FIELDS

MAX_NODES=50000
MAX_DEPTH=14

def bounded_private_text_atoms(value):
    """Collect exact string atoms privately; counts only in public report."""
    atoms=set()
    nodes=0
    nontext=0
    def visit(v,depth):
        nonlocal nodes,nontext
        nodes+=1
        if nodes>MAX_NODES or depth>MAX_DEPTH:
            raise ValueError("NAMEINDICES_METADATA_UNBOUNDED")
        if isinstance(v,str):
            if 0<len(v)<=512:atoms.add(v)
            else:nontext+=1
        elif isinstance(v,dict):
            for k,val in v.items():
                visit(k,depth+1)
                visit(val,depth+1)
        elif isinstance(v,(list,tuple)):
            for item in v:visit(item,depth+1)
        elif v is None or type(v) in (int,float,bool):
            nontext+=1
        else:
            raise ValueError("NAMEINDICES_UNSUPPORTED_SOURCE_METADATA_TYPE")
    visit(value,0)
    return atoms,dict(nodes=nodes,text_atoms=len(atoms),other_scalar_fields=nontext)

def compare_state_sources(named_state,perpass_atoms,shader_props,source_float_maps,valid_keywords):
    if type(shader_props) is not set or type(perpass_atoms) is not set or type(valid_keywords) is not set:
        raise ValueError("SOURCE_STATE_BRIDGE_SETS_INVALID")
    name,bracketed=normalize_private_state_name(named_state)
    if name is None:
        return dict(parseable=False,match_pass_nameindices=False,match_shader_property=False,
            match_original_material_float_slots=0,match_source_valid_keyword=False,
            direct_field_name_metadata_only=True,effective_gpu_state_verified=False)
    return dict(parseable=True,bracketed=bracketed,
        match_pass_nameindices=name in perpass_atoms,
        match_shader_property=name in shader_props,
        match_original_material_float_slots=sum(name in row for row in source_float_maps),
        match_source_valid_keyword=name in valid_keywords,
        direct_field_name_metadata_only=True,effective_gpu_state_verified=False)

def audit(stage):
    entries,typed,_=all_model_entries(stage)
    if len(entries)!=6 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("SOURCE_SHADER48_MODEL_MATERIAL_COUNT_DRIFT")
    shader_refs={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(shader_refs)!=1:raise ValueError("MIXED_SOURCE_SHADER48_IDENTITY")
    owner,pid=next(iter(shader_refs))
    shader=typed[owner].get(pid)
    if shader is None or shader.type.name!="Shader":
        raise ValueError("SOURCE_SHADER48_TYPED_OBJECT_MISSING")
    parsed=shader.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(parsed,dict):raise ValueError("ORIGINAL_SHADER48_PARSED_FORM_MISSING")
    subshaders=parsed.get("m_SubShaders")
    if not isinstance(subshaders,list) or [len(s.get("m_Passes",[])) for s in subshaders]!=[4,3]:
        raise ValueError("ORIGINAL_SHADER48_7_PASS_TOPOLOGY_DRIFT")
    props=parsed.get("m_PropInfo",{}).get("m_Props")
    if not isinstance(props,list) or len(props)!=27:raise ValueError("ORIGINAL_SHADER48_PROPERTY_COUNT_DRIFT")
    prop_names={p["m_Name"] for p in props if isinstance(p,dict) and isinstance(p.get("m_Name"),str)}
    if len(prop_names)!=27:raise ValueError("ORIGINAL_SHADER48_PROPERTY_LABEL_DRIFT")
    floats=private_float_maps(stage,typed)
    if len(floats)!=7:raise ValueError("ORIGINAL_MATERIAL_SLOT_FLOAT_DRIFT")
    keys,_=_material_keys(stage,typed)
    keywords=set()
    for owner,pid in keys:
        tree=typed[owner][pid].read_typetree(check_read=False)
        atoms,_=bounded_private_text_atoms(tree.get("m_ValidKeywords"))
        keywords.update(atoms)
    counts=Counter()
    per_field={field:Counter() for field in STATE_FIELDS}
    for s in subshaders:
        for pp in s["m_Passes"]:
            counts["source_passes"]+=1
            if not isinstance(pp,dict):raise ValueError("ORIGINAL_SHADER48_PASS_NOT_OBJECT")
            indexes=pp.get("m_NameIndices")
            counts["pass_nameindices_field_present"]+=int("m_NameIndices" in pp)
            if indexes is None:
                atoms=set()
                counts["pass_nameindices_missing"]+=1
            else:
                atoms,_=bounded_private_text_atoms(indexes)
                counts["pass_nameindices_with_text_atoms"]+=int(bool(atoms))
            st=pp.get("m_State")
            if not isinstance(st,dict):raise ValueError("SOURCE_PASS_STATE_MISSING")
            for field in STATE_FIELDS:
                v=st.get(field)
                name=v.get("name") if isinstance(v,dict) else None
                result=compare_state_sources(name,atoms,prop_names,floats,keywords)
                c=per_field[field]
                c["source_passes"]+=1
                c["name_parseable"]+=int(result["parseable"])
                c["matched_exact_nameindices"]+=int(result["match_pass_nameindices"])
                c["matched_original_shader_property"]+=int(result["match_shader_property"])
                c["matched_original_material_float_slots"]+=result["match_original_material_float_slots"]
                c["matched_original_material_valid_keyword"]+=int(result["match_source_valid_keyword"])
                c["unmatched_all_sources"]+=int(
                    result["parseable"] and not (
                        result["match_pass_nameindices"] or result["match_shader_property"] or
                        result["match_original_material_float_slots"] or result["match_source_valid_keyword"]))
    if counts["source_passes"]!=7 or any(c["source_passes"]!=7 for c in per_field.values()):
        raise ValueError("SOURCE_SHADER48_NOT_ALL_SEVEN_PASSES_AUDITED")
    return {
      "experiment":"GFX-MULTI-030S",
      "source_sha":ZIP2_SHA,
      "original_shader48_model_count":6,
      "original_material_renderer_slots":7,
      "original_shader48_subshaders":2,
      "original_shader48_passes":counts["source_passes"],
      "source_nameindices_metadata_presence":dict(counts),
      "named_state_exact_source_matches":{
          f:dict(sorted(c.items())) for f,c in per_field.items()},
      "source_shader_property_names_or_original_metadata_published":False,
      "source_original_keyword_or_material_float_values_published":False,
      "source_binary_or_register_ids_published":False,
      "numeric_hash_name_guessing_used":False,
      "original_shaderlab_gles3_shader_compiled":False,
      "original_shader48_material_to_register_bridge_complete":False,
      "original_shader48_runtime_render_state_proven":False,
      "original_shader48_android_gpu_pixels_verified":False,
      "phase_closed":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI030S_EXACT_NAMEINDICES_SOURCE_MATCH_COUNTS "+json.dumps(report,sort_keys=True))
if __name__=="__main__":
    main()
