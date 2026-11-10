#!/usr/bin/env python3
"""GFX-MULTI-026S: source-only seven-pass state metadata and Material flags census.

No proprietary original state values, Shader48 code, keyword strings,
serialized names, GUIDs or PPtrs in the report. Presence != effective GPU state.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_texture_semantics import _material_keys

STATE_FIELDS=(
 "rtBlend","rtSeparateBlend","alphaToMask","zClip","zTest","zWrite",
 "culling","conservative","offsetFactor","offsetUnits",
 "stencilOp","stencilOpFront","stencilOpBack","stencilReadMask","stencilWriteMask",
 "stencilRef","fogStart","fogEnd","fogDensity","fogColor","colorMask"
)
MATERIAL_KEYS=("m_CustomRenderQueue","m_ShaderKeywords",
               "m_EnableInstancingVariants","m_DoubleSidedGI")

def presence_count(states,keys):
    if not isinstance(states,list) or not states:
        raise ValueError("MISSING_SOURCE_STATE_LIST")
    out=Counter()
    for d in states:
        if d is None:
            out["missing_state_block"]+=1
            continue
        if not isinstance(d,dict):
            raise ValueError("SOURCE_STATE_OBJECT_NOT_DICTIONARY")
        out["present_state_block"]+=1
        for key in keys:
            if key in d:
                out["field_present_"+key]+=1
                out["field_nonnull_"+key]+=int(d[key] is not None)
            else:
                out["field_absent_"+key]+=1
    return dict(out)

def bucket_queue(value):
    if type(value) is not int:
        return "unknown"
    if value == -1:return "shader_default_queue_minus_one"
    if value < 0:return "other_negative_queue"
    return "explicit_nonnegative_queue"

def bucket_keywords(value):
    if value is None:return "absent"
    if isinstance(value,str):
        return "nonempty" if value.strip() else "empty"
    if isinstance(value,list):
        if any(not isinstance(x,str) for x in value):
            raise ValueError("ORIGINAL_MATERIAL_KEYWORD_LIST_INVALID")
        return "nonempty" if value else "empty"
    raise ValueError("ORIGINAL_MATERIAL_KEYWORD_TYPE_INVALID")

def audit(source):
    entries,typed,_=all_model_entries(source)
    if len(entries)!=6 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("SOURCE_MODEL_MATERIAL_CHAIN_DRIFT")
    shaders={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(shaders)!=1:raise ValueError("SOURCE_MIXED_SHADERS_NOT_SUPPORTED")
    owner,pid=next(iter(shaders))
    obj=typed[owner].get(pid)
    if obj is None or obj.type.name!="Shader":
        raise ValueError("SOURCE_SHADER48_IDENTITY_MISSING")
    shader=obj.read_typetree(check_read=False)
    subs=shader.get("m_ParsedForm",{}).get("m_SubShaders")
    if not isinstance(subs,list) or [len(x.get("m_Passes",[])) for x in subs]!=[4,3]:
        raise ValueError("ORIGINAL_TWO_SUBSHADER_SEVEN_PASS_DRIFT")
    states=[]
    info=Counter()
    for sub in subs:
        for pp in sub["m_Passes"]:
            if not isinstance(pp,dict):
                raise ValueError("ORIGINAL_SHADER48_PASS_SHAPE_DRIFT")
            info["passes"]+=1
            info["passes_with_state_key"]+=int("m_State" in pp)
            states.append(pp.get("m_State"))
            info["passes_with_tags_key"]+=int("m_Tags" in pp)
            info["passes_with_name_indices_key"]+=int("m_NameIndices" in pp)
            info["passes_with_programs_key"]+=int("m_Programs" in pp)
    flags=Counter()
    keys,_=_material_keys(source,typed)
    if len(keys)!=7:raise ValueError("ORIGINAL_MATERIAL_SLOT_DRIFT")
    for owner,pid in keys:
        material=typed[owner].get(pid)
        if material is None or material.type.name!="Material":
            raise ValueError("ORIGINAL_SOURCE_MATERIAL_MISSING")
        tree=material.read_typetree(check_read=False)
        flags["material_slots"]+=1
        for key in MATERIAL_KEYS:
            flags[key+"_present"]+=int(key in tree)
            flags[key+"_absent"]+=int(key not in tree)
        flags["render_queue_"+bucket_queue(tree.get("m_CustomRenderQueue"))]+=1
        flags["shader_keywords_"+bucket_keywords(tree.get("m_ShaderKeywords"))]+=1
        if "m_EnableInstancingVariants" in tree:
            v=tree["m_EnableInstancingVariants"]
            flags["instancing_true"]+=int(v in (1,True))
            flags["instancing_false"]+=int(v in (0,False))
            flags["instancing_unexpected"]+=int(v not in (0,1,True,False))
    result={
      "experiment":"GFX-MULTI-026S",
      "source_sha":ZIP2_SHA,
      "source_models":6,
      "shader_identities":len(shaders),
      "original_subshaders":len(subs),
      "original_pass_count":info["passes"],
      "pass_presence_counts":dict(info),
      "pass_state_field_presence":presence_count(states,STATE_FIELDS),
      "original_material_state_presence":dict(flags),
      "render_state_numeric_values_exported":False,
      "material_keywords_or_property_names_exported":False,
      "original_shader48_source_code_exported":False,
      "source_material_to_register_mapping_verified":False,
      "original_android_shader_restored":False,
      "android_gpu_pixels_verified":False,
      "phase_closed":False
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI026S_SAFE_SEVEN_PASS_STATE_PRESENCE "+json.dumps(r,sort_keys=True))
if __name__=="__main__":
    main()
