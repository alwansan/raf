#!/usr/bin/env python3
"""GFX-MULTI-029S — original Shader48 named state parameter -> Material Float evidence.

Only aggregate counts leave private source runner; no original Shader48 name,
keyword string, signed float value, image, register, ID or PPtr is published.
Source metadata equivalence is NOT actual effective Unity/Android GPU render state.
"""
from __future__ import annotations
import argparse,json,math,re
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_texture_semantics import _material_keys,named_entries
from gfxlab.tools.multi_sevenpass_state_enum_semantics import STATE_FIELDS

BRACKETED=re.compile(r"^\[([A-Za-z_][A-Za-z0-9_]*)\]$")
def normalize_private_state_name(value):
    """Only explicitly bracketed ShaderLab property tokens may be unwrapped."""
    if type(value)!=str or not value or len(value)>256:return None,False
    m=BRACKETED.fullmatch(value)
    if m:return m.group(1),True
    return value,False

def compare_named_state(name,shader_properties,source_float_maps,valid_enum):
    """Name/metadata exact set test, with private float data never emitted."""
    if type(shader_properties)!=set or not isinstance(source_float_maps,list):
        raise ValueError("INVALID_PRIVATE_ORIGINAL_PROPERTY_INPUTS")
    prop,bracket=normalize_private_state_name(name)
    if prop is None:
        return dict(name_metadata_parseable=False,source_property_declaration_present=False,
            material_float_matching_slots=0,material_float_valid_enum_slots=0,
            material_float_unrecognized_value_slots=0,bracket_syntax_unwrapped=False,
            effective_shader_gpu_state_verified=False)
    found=valid=unknown=0
    for f in source_float_maps:
        if type(f)!=dict:raise ValueError("PRIVATE_ORIGINAL_MATERIAL_FLOAT_MAP_MALFORMED")
        if prop not in f:continue
        found+=1
        x=f[prop]
        if type(x) not in (float,int) or not math.isfinite(x):
            unknown+=1;continue
        rounded=round(x)
        if abs(x-rounded)<=1e-5 and rounded in valid_enum:
            valid+=1
        else:unknown+=1
    return dict(name_metadata_parseable=True,
        source_property_declaration_present=prop in shader_properties,
        material_float_matching_slots=found,
        material_float_valid_enum_slots=valid,
        material_float_unrecognized_value_slots=unknown,
        bracket_syntax_unwrapped=bracket,
        effective_shader_gpu_state_verified=False)

def private_float_maps(source,types):
    keys,_=_material_keys(source,types)
    if len(keys)!=7:raise ValueError("SOURCE_MATERIAL_SLOT_COUNT_CHANGED")
    seen=[]
    for owner,pid in keys:
        obj=types[owner].get(pid)
        if obj is None or obj.type.name!="Material":
            raise ValueError("ORIGINAL_MATERIAL_TYPE_MISMATCH")
        saved=obj.read_typetree(check_read=False).get("m_SavedProperties")
        if not isinstance(saved,dict):
            raise ValueError("ORIGINAL_MATERIAL_FLOAT_SOURCE_MISSING")
        vals=dict(named_entries(saved.get("m_Floats",[])))
        for v in vals.values():
            if type(v) not in (float,int) or not math.isfinite(v) or abs(v)>10000:
                raise ValueError("ORIGINAL_MATERIAL_FLOAT_VALUE_MALFORMED")
        seen.append(vals)
    return seen

def audit(stage):
    entries,typed,_=all_model_entries(stage)
    if len(entries)!=6 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("SOURCE_MODEL_MATERIAL_GRAPH_DRIFT")
    shaders={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(shaders)!=1:raise ValueError("ORIGINAL_SHADER48_IDENTITY_DRIFT")
    owner,pid=next(iter(shaders))
    obj=typed[owner].get(pid)
    if obj is None or obj.type.name!="Shader":
        raise ValueError("ORIGINAL_SHADER48_UNAVAILABLE")
    tree=obj.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(tree,dict):raise ValueError("SOURCE_PARSED_SHADER_MISSING")
    props=tree.get("m_PropInfo",{}).get("m_Props",[])
    if not isinstance(props,list):raise ValueError("SOURCE_SHADER_PROPERTIES_MISSING")
    names={x["m_Name"] for x in props if isinstance(x,dict) and isinstance(x.get("m_Name"),str)}
    floats=private_float_maps(stage,typed)
    subs=tree.get("m_SubShaders")
    if not isinstance(subs,list) or [len(x.get("m_Passes",[])) for x in subs]!=[4,3]:
        raise ValueError("SOURCE_SHADER48_PASS_TOPOLOGY_DRIFT")
    counters=Counter()
    for s in subs:
        for p in s["m_Passes"]:
            st=p.get("m_State")
            if not isinstance(st,dict):raise ValueError("SOURCE_SHADER_STATE_MISSING")
            counters["source_passes_checked"]+=1
            for field,valid_enum in STATE_FIELDS.items():
                value=st.get(field)
                if not isinstance(value,dict):
                    counters["state_"+field+"_without_named_state_record"]+=1
                    continue
                label=value.get("name")
                result=compare_named_state(label,names,floats,valid_enum)
                prefix="state_"+field+"_"
                counters[prefix+"pass_names_parseable"]+=int(result["name_metadata_parseable"])
                counters[prefix+"shader_property_declarations_matched"]+=int(
                    result["source_property_declaration_present"])
                counters[prefix+"bracket_tokens_normalized"]+=int(result["bracket_syntax_unwrapped"])
                counters[prefix+"material_float_matching_slots"]+=result["material_float_matching_slots"]
                counters[prefix+"material_float_valid_enum_slots"]+=result["material_float_valid_enum_slots"]
                counters[prefix+"material_float_unrecognized_values"]+=result["material_float_unrecognized_value_slots"]
    if counters["source_passes_checked"]!=7:raise ValueError("SOURCE_SHADER_PASS_COVERAGE_INCOMPLETE")
    return dict(experiment="GFX-MULTI-029S",source_sha=ZIP2_SHA,
        original_shader48_source_verified=True,source_models=6,material_slots=7,
        original_shader_passes=7,source_shader_property_count=len(names),
        dynamic_named_state_material_float_match_aggregate=dict(sorted(counters.items())),
        effective_render_state_parity_on_android_verified=False,
        shader_property_to_DX11_register_equivalence_verified=False,
        original_CB_offsets_verified=False,
        original_shader48_restored=False,
        private_names_floats_original_shader_bytes_exported=False,
        phase_closed=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI029S_SAFE_NAMED_STATE_MATERIAL_FLOAT_BRIDGE "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
