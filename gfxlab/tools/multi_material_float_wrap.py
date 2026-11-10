#!/usr/bin/env python3
"""GFX-MULTI-024: private source Material scalar and texture-settings census.

Original ZIP2 @ pinned SHA only; no assets, names, PPtrs, numeric material
values, image bytes or shader code enter public logs or Git. Public enumeration
labels come exclusively from the Unity 2021.3 C# reference source, not guessed.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import ZIP2_SHA, stage_originals
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_texture_semantics import named_entries

# Unity-Technologies/UnityCsReference branch 2021.3 at
# https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs
UNITY_REF="https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs"
ENUMS={
    "TextureFormat":{10:"DXT1",12:"DXT5"},
    "TextureColorSpace":{0:"Linear",1:"sRGB"},  # NOT PlayerSettings.ColorSpace
    "FilterMode":{0:"Point",1:"Bilinear",2:"Trilinear"},
    "TextureWrapMode":{0:"Repeat",1:"Clamp",2:"Mirror",3:"MirrorOnce"},
}
ROLES=("basecolor","normal","metallic")
# These are only public Unity Standard-style property names; unknowns are not exported.
KNOWN_FLOAT={
    "_Metallic":"metallic_named",
    "_Glossiness":"gloss_named",
    "_Smoothness":"gloss_named",
    "_GlossMapScale":"gloss_named",
    "_BumpScale":"normal_strength_named",
    "_Parallax":"height_named",
    "_Cutoff":"alpha_cutout_named",
    "_OcclusionStrength":"occlusion_named",
    "_EmissionScaleUI":"emission_named",
    "_DetailNormalMapScale":"normal_strength_named",
    "_Mode":"render_mode_named",
    "_SrcBlend":"blend_named",
    "_DstBlend":"blend_named",
    "_ZWrite":"depth_named",
    "_UVSec":"uv_channel_named",
    "_SmoothnessTextureChannel":"gloss_named",
}

def enum_label(group, value):
    if group not in ENUMS:
        raise ValueError("UNSUPPORTED_PUBLIC_UNITY_ENUM_CLASS")
    if type(value) is not int:
        return "missing_or_malformed"
    return ENUMS[group].get(value,"unmapped_source_code")

def scalar_bucket(value):
    if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>10000:
        raise ValueError("MALFORMED_ORIGINAL_FLOAT_VALUE")
    if value<0:
        return "negative"
    if value==0:
        return "zero"
    if value<1:
        return "between_zero_one"
    if value==1:
        return "one"
    return "above_one"

def color_bucket(raw):
    if not isinstance(raw,dict) or not all(k in raw for k in ("r","g","b","a")):
        raise ValueError("ORIGINAL_COLOR_SLOT_SHAPE_INVALID")
    vals=[raw[k] for k in ("r","g","b","a")]
    if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>64 for v in vals):
        raise ValueError("ORIGINAL_COLOR_SLOT_NONFINITE_OR_LARGE")
    if all(abs(v-1)<1e-6 for v in vals):
        return "white_rgba"
    if all(abs(v)<1e-6 for v in vals):
        return "zero_rgba"
    return "non_identity_color"

def _collect_shader_names(entries,typed):
    refs={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(refs)!=1:
        raise ValueError("ORIGINAL_SHADER48_IDENTITY_DRIFT")
    owner,pid=next(iter(refs))
    shader=typed[owner].get(pid)
    if shader is None or shader.type.name!="Shader":
        raise ValueError("ORIGINAL_SHADER48_SOURCE_MISSING")
    tree=shader.read_typetree(check_read=False)
    props=tree.get("m_ParsedForm",{}).get("m_PropInfo",{}).get("m_Props")
    if not isinstance(props,list) or len(props)!=27:
        raise ValueError("ORIGINAL_SHADER48_PROPERTIES_DRIFT")
    names=set()
    for p in props:
        if not isinstance(p,dict) or not isinstance(p.get("m_Name"),str) or not p["m_Name"]:
            raise ValueError("ORIGINAL_SHADER48_PROPERTY_SHAPE_INVALID")
        if p["m_Name"] in names:
            raise ValueError("ORIGINAL_SHADER48_DUPLICATE_PROPERTY")
        names.add(p["m_Name"])
    return names

def _inspect_settings(settings):
    if not isinstance(settings,dict):
        raise ValueError("ORIGINAL_TEXTURE_SETTINGS_MISSING")
    out={}
    for axis in ("U","V","W"):
        key="m_Wrap"+axis
        out[axis]=enum_label("TextureWrapMode",settings.get(key))
    out["filter"]=enum_label("FilterMode",settings.get("m_FilterMode"))
    for key in ("m_Aniso","m_MipBias"):
        v=settings.get(key)
        if type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1000:
            raise ValueError("ORIGINAL_TEXTURE_SETTINGS_SCALAR_INVALID")
    return out

def audit(stage):
    entries,typed,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("ORIGINAL_SIX_MODEL_SELECTION_DRIFT")
    materials=[m for e in entries for m in e["materials"]]
    if len(materials)!=7:
        raise ValueError("ORIGINAL_MATERIAL_COUNT_DRIFT")
    shader_names=_collect_shader_names(entries,typed)
    material_totals=Counter()
    floats_by_bucket=Counter()
    float_name_categories=Counter()
    colors_by_bucket=Counter()
    per_material=[]
    texture_count=0
    unique_mat_keys=set()
    settings_by_role={r:{"format":Counter(),"colorspace":Counter(),"filter":Counter(),
                         "U":Counter(),"V":Counter(),"W":Counter(),"mip_count":Counter(),
                         "aniso_bucket":Counter(),"mip_bias_bucket":Counter()} for r in ROLES}
    texture_keys=set()
    from gfxlab.tools.multi_material_texture_semantics import _material_keys
    keys,_=_material_keys(stage,typed)
    if len(keys)!=7:
        raise ValueError("SOURCE_MATERIAL_POINTER_COUNT_DRIFT")
    for owner,pid in keys:
        # Renderer material slots may legitimately alias the exact same
        # original Material21. Count seven slots and separate unique objects.
        unique_mat_keys.add((owner,pid))
        obj=typed[owner].get(pid)
        if obj is None or obj.type.name!="Material":
            raise ValueError("ORIGINAL_MATERIAL21_SOURCE_MISSING")
        d=obj.read_typetree(check_read=False)
        saved=d.get("m_SavedProperties")
        if not isinstance(saved,dict):
            raise ValueError("ORIGINAL_MATERIAL_SAVED_PROPERTIES_MISSING")
        fl=named_entries(saved.get("m_Floats",[]))
        co=named_entries(saved.get("m_Colors",[]))
        material_totals["material_slots"]+=1
        material_totals["float_slots"]+=len(fl)
        material_totals["color_slots"]+=len(co)
        per_material.append((len(fl),len(co)))
        for name,value in fl:
            material_totals["float_name_in_shader"]+=int(name in shader_names)
            floats_by_bucket[scalar_bucket(value)]+=1
            float_name_categories[KNOWN_FLOAT.get(name,"unknown_property_name")]+=1
        for name,value in co:
            material_totals["color_name_in_shader"]+=int(name in shader_names)
            colors_by_bucket[color_bucket(value)]+=1
    if material_totals["float_slots"]!=112 or material_totals["color_slots"]!=14:
        raise ValueError("ORIGINAL_FLOAT_COLOR_SLOT_DRIFT")
    if sum(map(lambda p:p[0],per_material))!=112 or sum(map(lambda p:p[1],per_material))!=14:
        raise ValueError("ORIGINAL_PER_MATERIAL_ACCOUNTING_DRIFT")

    for e in entries:
        for m in e["materials"]:
            for role,link in m["textures"].items():
                if role not in ROLES:
                    raise ValueError("UNEXPECTED_ORIGINAL_TEXTURE_ROLE")
                texture_count+=1
                key=(link["owner"],link["pid"])
                # Some materials may share a texture: don't infer uniqueness.
                texture_keys.add(key)
                obj=typed[link["owner"]].get(link["pid"])
                if obj is None or obj.type.name!="Texture2D":
                    raise ValueError("ORIGINAL_TEXTURE2D_POINTER_DRIFT")
                d=obj.read_typetree(check_read=False)
                s=_inspect_settings(d.get("m_TextureSettings"))
                cnt=settings_by_role[role]
                cnt["format"][enum_label("TextureFormat",d.get("m_TextureFormat"))]+=1
                cnt["colorspace"][enum_label("TextureColorSpace",d.get("m_ColorSpace"))]+=1
                cnt["filter"][s["filter"]]+=1
                for axis in ("U","V","W"):
                    cnt[axis][s[axis]]+=1
                mip=d.get("m_MipCount")
                if type(mip) is not int or not 1<=mip<=32:
                    raise ValueError("ORIGINAL_TEXTURE_MIP_COUNT_INVALID")
                cnt["mip_count"][str(mip)]+=1
                cnt["aniso_bucket"][scalar_bucket(d["m_TextureSettings"]["m_Aniso"])]+=1
                cnt["mip_bias_bucket"][scalar_bucket(d["m_TextureSettings"]["m_MipBias"])]+=1
    if texture_count!=21 or any(sum(settings_by_role[r]["format"].values())!=7 for r in ROLES):
        raise ValueError("ORIGINAL_TEXTURE_SETTINGS_TOTAL_DRIFT")
    return {
        "experiment":"GFX-MULTI-024",
        "source_sha":ZIP2_SHA,
        "source_models":6,
        "material_slots":material_totals["material_slots"],
        "unique_original_material_objects":len(unique_mat_keys),
        "material_slot_references_reused":7-len(unique_mat_keys),
        "float_slots":material_totals["float_slots"],
        "color_slots":material_totals["color_slots"],
        "shader48_original_property_count":len(shader_names),
        "material_to_shader_property_name_membership":{
            "float_slots_declared":material_totals["float_name_in_shader"],
            "color_slots_declared":material_totals["color_name_in_shader"],
            "missing_float_property_declarations":112-material_totals["float_name_in_shader"],
            "missing_color_property_declarations":14-material_totals["color_name_in_shader"],
        },
        "float_value_buckets":dict(floats_by_bucket),
        "float_known_name_category_counts":dict(float_name_categories),
        "color_value_buckets":dict(colors_by_bucket),
        "material_float_slot_distribution":{"min":min(x[0] for x in per_material),
                                            "max":max(x[0] for x in per_material)},
        "texture_links":texture_count,
        "unique_source_textures":len(texture_keys),
        "source_texture_settings_by_role":{
            r:{name:dict(vals) for name,vals in groups.items()}
            for r,groups in settings_by_role.items()},
        "unity_version_reference":"UnityCsReference/2021.3/GraphicsEnums.cs",
        "texture_color_space_is_internal_texture_enum_not_player_color_space":True,
        "source_names_pointers_and_values_published":False,
        "original_shader_restored":False,
        "original_shader_property_to_register_mapping_verified":False,
        "android_gpu_pixels_verified":False,
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
    print("GFX_MULTI024_SAFE_MATERIAL_SETTINGS "+json.dumps(report,sort_keys=True))
if __name__=="__main__":
    main()
