#!/usr/bin/env python3
"""GFX-MULTI-028S source-only Shader48 seven-pass render-state *category* audit.

Authenticated original SHA ZIP2 parsed privately, no raw state numbers,
Shader names, source keywords or original binaries are published.
Official Unity 2021.3 CullMode / CompareFunction enums are classification
references, NOT proof of actual Android GPU render state.
"""
from __future__ import annotations
import argparse,json,math
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_texture_semantics import _material_keys

CULL={0:"off",1:"front",2:"back"}
ZTEST={0:"disabled",1:"never",2:"less",3:"equal",4:"less_equal",
       5:"greater",6:"not_equal",7:"greater_equal",8:"always"}
SWITCH={0:"off",1:"on"}
STATE_FIELDS={"culling":CULL,"zWrite":SWITCH,"zTest":ZTEST,
              "alphaToMask":SWITCH}
KEYWORD_FIELDS=("m_ShaderKeywords","m_ValidKeywords","m_InvalidKeywords")

def classify_state_value(src,known):
    """Keep dynamic named values separate from literal numeric enum values."""
    if src is None:return "missing_or_null"
    if type(src)==dict:
        name=src.get("name")
        if name is not None and type(name)!=str:
            return "unsupported_named_value"
        if name:return "named_dynamic_override"
        src=src.get("val")
    if type(src) not in (int,float) or not math.isfinite(src):
        return "non_numeric_or_nonfinite"
    integral=round(src)
    if abs(src-integral)>0.00001:
        return "non_integral_value"
    return known.get(integral,"out_of_enum_range")

def classify_bool(src):
    if type(src)==bool:return "true" if src else "false"
    if type(src)==int and src in (0,1):return "true" if src else "false"
    return "unknown_boolean_shape"

def classify_material_keyword_field(tree,key):
    if key not in tree:return "field_absent"
    obj=tree[key]
    if obj is None:return "null"
    if type(obj)==str:return "nonempty" if obj else "empty"
    if type(obj) in (list,tuple):return "nonempty" if len(obj)>0 else "empty"
    return "unrecognized_field_shape"

def audit(stage):
    original,types,_=all_model_entries(stage)
    if len(original)!=6 or sum(len(e["materials"]) for e in original)!=7:
        raise ValueError("SOURCE_SIX_MODEL_SEVEN_MATERIAL_DRIFT")
    shaders={(m["shader_owner"],m["shader_pid"])
            for model in original for m in model["materials"]}
    if len(shaders)!=1:raise ValueError("ORIGINAL_SHADER48_IDENTITY_DRIFT")
    o,pid=next(iter(shaders))
    obj=types[o].get(pid)
    if obj is None or obj.type.name!="Shader":
        raise ValueError("EXPECTED_ORIGINAL_SHADER48_TYPED_OBJECT")
    d=obj.read_typetree(check_read=False)
    sub=d.get("m_ParsedForm",{}).get("m_SubShaders")
    if not isinstance(sub,list) or [len(x.get("m_Passes",[])) for x in sub]!=[4,3]:
        raise ValueError("ORIGINAL_PASS_TOPOLOGY_DRIFT")
    totals=Counter()
    for group in sub:
        for p in group["m_Passes"]:
            state=p.get("m_State")
            if not isinstance(state,dict):raise ValueError("ORIGINAL_RENDER_STATE_MISSING")
            totals["shader_passes_examined"]+=1
            for field,enums in STATE_FIELDS.items():
                category=classify_state_value(state.get(field),enums)
                totals["state_"+field+"_"+category]+=1
            if "rtSeparateBlend" in state:
                totals["blend_rtSeparateBlend_"+classify_bool(state["rtSeparateBlend"])]+=1
            else:totals["blend_rtSeparateBlend_absent"]+=1
            totals["direct_rtBlend_field_present"]+=int("rtBlend" in state)
            totals["direct_rtBlend_field_absent"]+=int("rtBlend" not in state)
    keys,_=_material_keys(stage,types)
    if len(keys)!=7:raise ValueError("ORIGINAL_RENDERER_MATERIAL_SLOT_DRIFT")
    for owner,pid in keys:
        m=types[owner].get(pid)
        if m is None or m.type.name!="Material":
            raise ValueError("AUTHENTIC_ORIGINAL_MATERIAL_REQUIRED")
        tree=m.read_typetree(check_read=False)
        totals["material_slots_examined"]+=1
        for field in KEYWORD_FIELDS:
            category=classify_material_keyword_field(tree,field)
            totals["material_"+field+"_"+category]+=1
    if totals["shader_passes_examined"]!=7 or totals["material_slots_examined"]!=7:
        raise ValueError("SOURCE_STATE_AGGREGATE_INCOMPLETE")
    return dict(experiment="GFX-MULTI-028S",source_sha=ZIP2_SHA,
        sample_source_model_count=6,original_shader_identities=1,
        original_shader_subshaders=2,original_shader_passes=7,
        original_material_slots=7,
        anonymized_state_enum_categories=dict(sorted(totals.items())),
        official_unity2021_shader_state_enum_classification_only=True,
        original_compiled_shader_blend_attachment_states_verified=False,
        original_material_to_DX11_binding_proven=False,
        all_source_variants_tested=False,
        original_shader48_compiled_on_android=False,
        android_gpu_pixel_parity_verified=False,
        raw_state_values_or_names_exported=False,stage_closed=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI028S_SAFE_STATE_ENUM_CATEGORIES "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
