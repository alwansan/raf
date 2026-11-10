#!/usr/bin/env python3
"""GFX-MULTI-025: authentic source Color semantics / Material and Texture alias census.

Never publish source GUID/PPtr/object keys, names, numeric authored color values,
textures, original Shader48 code, or identity assignments. Anonymous counts
only; source evidence does NOT imply Android ShaderLab or GPU pixel fidelity.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

from gfxlab.tools.original_model_probe import ZIP2_SHA,stage_originals
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_float_wrap import _collect_shader_names
from gfxlab.tools.multi_material_texture_semantics import named_entries,_material_keys

COLOR_ROLES={
    "_Color":"base_tint_named",
    "_BaseColor":"base_tint_named",
    "_EmissionColor":"emission_named_candidate",
    "_SpecColor":"specular_named_candidate",
    "_RimColor":"rim_named_candidate",
    "_TintColor":"tint_named_candidate",
    "_ReflectColor":"reflection_named_candidate",
    "_OutlineColor":"outline_named_candidate",
}

def safe_color_role(name):
    if not isinstance(name,str) or not name:
        raise ValueError("INVALID_ORIGINAL_COLOR_PROPERTY_LABEL")
    return COLOR_ROLES.get(name,"other_original_color_property")

def vector_shape(value):
    if not isinstance(value,dict) or not all(k in value for k in ("r","g","b","a")):
        raise ValueError("MALFORMED_ORIGINAL_COLOR_VECTOR")
    vals=[value[k] for k in ("r","g","b","a")]
    if any(type(v) not in (float,int) or not math.isfinite(v) or abs(v)>64 for v in vals):
        raise ValueError("NONFINITE_OR_HUGE_ORIGINAL_COLOR")
    rgb=vals[:3]
    alpha=vals[3]
    return {
        "rgb_black":all(abs(float(v))<1e-6 for v in rgb),
        "rgb_white":all(abs(float(v)-1.0)<1e-6 for v in rgb),
        "rgb_has_nonzero":any(abs(float(v))>=1e-6 for v in rgb),
        "alpha_zero":abs(float(alpha))<1e-6,
        "alpha_one":abs(float(alpha)-1.0)<1e-6,
        "rgba_white":all(abs(float(v)-1.0)<1e-6 for v in vals),
    }

def alias_group_stats(rows):
    """Count group cardinality only, never emit private keys or model memberships."""
    if not isinstance(rows,list) or not rows:
        raise ValueError("ORIGINAL_ALIAS_INPUT_NOT_LIST")
    c=Counter()
    seen_per_key=defaultdict(set)
    roles_per_key=defaultdict(set)
    for row in rows:
        if not isinstance(row,tuple) or len(row)!=3:
            raise ValueError("ORIGINAL_ALIAS_ROW_SHAPE")
        key,model_index,role=row
        if not isinstance(key,tuple) or len(key)!=2:
            raise ValueError("ORIGINAL_ALIAS_IDENTITY_SHAPE")
        if type(model_index) is not int or model_index<0 or model_index>5:
            raise ValueError("ORIGINAL_ALIAS_MODEL_INDEX_INVALID")
        if not isinstance(role,str) or not role:
            raise ValueError("ORIGINAL_ALIAS_ROLE_INVALID")
        c[key]+=1
        seen_per_key[key].add(model_index)
        roles_per_key[key].add(role)
    hist=Counter(c.values())
    return {
        "slots":len(rows),
        "unique_original_objects":len(c),
        "aliased_references":len(rows)-len(c),
        "alias_group_size_histogram":{str(size):n for size,n in sorted(hist.items())},
        "groups_shared_across_models":sum(len(v)>1 for v in seen_per_key.values()),
        "groups_shared_across_roles":sum(len(v)>1 for v in roles_per_key.values()),
        "max_slots_per_original":max(c.values()),
    }

def audit(stage):
    entries,typed,_=all_model_entries(stage)
    if [x["id"] for x in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("ORIGINAL_SIX_MODEL_SELECTION_DRIFT")
    material_keys,_=_material_keys(stage,typed)
    if len(material_keys)!=7:
        raise ValueError("ORIGINAL_SEVEN_MATERIAL_SLOT_DRIFT")
    shader_names=_collect_shader_names(entries,typed)
    material_rows=[]
    texture_rows=[]
    color_by_role=Counter()
    color_by_signature=Counter()
    color_nonwhite_role=Counter()
    color_nonzero_rgb_role=Counter()
    matches=0
    color_slots=0
    slot_idx=0
    for mi,e in enumerate(entries):
        for material in e["materials"]:
            owner,pid=material_keys[slot_idx]
            slot_idx+=1
            material_rows.append(((owner,pid),mi,"Material21"))
            obj=typed[owner].get(pid)
            if obj is None or obj.type.name!="Material":
                raise ValueError("ORIGINAL_MATERIAL21_SOURCE_MISSING")
            saved=obj.read_typetree(check_read=False).get("m_SavedProperties")
            if not isinstance(saved,dict):
                raise ValueError("ORIGINAL_MATERIAL_SAVED_PROPERTIES_MISSING")
            colors=named_entries(saved.get("m_Colors",[]))
            color_slots+=len(colors)
            for name,value in colors:
                matches+=int(name in shader_names)
                role=safe_color_role(name)
                sig=vector_shape(value)
                color_by_role[role]+=1
                color_by_signature["rgba_white"]+=int(sig["rgba_white"])
                color_by_signature["rgba_nonwhite"]+=int(not sig["rgba_white"])
                color_by_signature["rgb_black"]+=int(sig["rgb_black"])
                color_by_signature["rgb_white"]+=int(sig["rgb_white"])
                color_by_signature["rgb_nonzero"]+=int(sig["rgb_has_nonzero"])
                color_by_signature["alpha_zero"]+=int(sig["alpha_zero"])
                color_by_signature["alpha_one"]+=int(sig["alpha_one"])
                color_by_signature["alpha_other"]+=int(not sig["alpha_zero"] and not sig["alpha_one"])
                color_nonwhite_role[role]+=int(not sig["rgba_white"])
                color_nonzero_rgb_role[role]+=int(sig["rgb_has_nonzero"])
            for role,link in material["textures"].items():
                if role not in ("basecolor","normal","metallic"):
                    raise ValueError("ORIGINAL_TEXTURE_ROLE_DRIFT")
                key=(link["owner"],link["pid"])
                target=typed[link["owner"]].get(link["pid"])
                if target is None or target.type.name!="Texture2D":
                    raise ValueError("ORIGINAL_TEXTURE2D_REFERENCE_DRIFT")
                texture_rows.append((key,mi,role))
    materials=alias_group_stats(material_rows)
    textures=alias_group_stats(texture_rows)
    if materials["slots"]!=7 or materials["unique_original_objects"]!=6:
        raise ValueError("ORIGINAL_MATERIAL_SLOT_IDENTITY_TOTAL_DRIFT")
    if textures["slots"]!=21 or textures["unique_original_objects"]!=18:
        raise ValueError("ORIGINAL_TEXTURE_LINK_IDENTITY_TOTAL_DRIFT")
    if color_slots!=14 or matches!=14:
        raise ValueError("ORIGINAL_SHADER48_COLOR_NAME_LINK_DRIFT")
    if color_by_signature["rgba_white"]!=7 or color_by_signature["rgba_nonwhite"]!=7:
        raise ValueError("ORIGINAL_COLOR_VALUE_SIGNATURE_DRIFT")
    return {
        "experiment":"GFX-MULTI-025",
        "source_sha":ZIP2_SHA,
        "models":6,
        "source_shader48_property_names":len(shader_names),
        "material_alias_census":materials,
        "texture_alias_census":textures,
        "saved_color_slots":color_slots,
        "colors_with_name_in_original_shader48":matches,
        "color_name_semantic_candidate_counts":dict(color_by_role),
        "nonwhite_color_role_candidates":dict(color_nonwhite_role),
        "nonzero_rgb_color_role_candidates":dict(color_nonzero_rgb_role),
        "color_value_shape_counts":dict(color_by_signature),
        "color_names_or_values_published":False,
        "source_material_or_texture_identities_published":False,
        "original_shader_pass_bindings_recovered":False,
        "android_original_shader_restored":False,
        "android_gpu_pixels_verified":False,
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
    print("GFX_MULTI025_SAFE_COLOR_AND_ALIAS_CENSUS "+json.dumps(d,sort_keys=True))

if __name__=="__main__":
    main()
