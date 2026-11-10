#!/usr/bin/env python3
"""GFX-OWNER-002: original Material float vs Standard fallback source delta.

Only anonymous aggregate counts are published; no raw source numeric Material
values, source shader code/ids, private property lists or Texture2D pixels.
This does not establish original Shader48's runtime smoothness semantics.
"""
from __future__ import annotations
import argparse,json,math
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_material_texture_semantics import _material_keys,named_entries

FALLBACK_GLOSS=0.45
def near_source_scalar(value,reference):
    if type(value) not in (float,int) or not math.isfinite(value) or abs(value)>10000:
        raise ValueError("ORIGINAL_MATERIAL_FLOAT_SCALAR_INVALID")
    return abs(float(value)-reference)<=1e-6

def audit(source):
    entries,typed,_=all_model_entries(source)
    if len(entries)!=6 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("ORIGINAL_MATERIAL_GRAPH_DRIFT")
    keys,_=_material_keys(source,typed)
    if len(keys)!=7:raise ValueError("ORIGINAL_MATERIAL_SLOT_DRIFT")
    cnt=Counter()
    for owner,pid in keys:
        obj=typed[owner].get(pid)
        if obj is None or obj.type.name!="Material":
            raise ValueError("ORIGINAL_SOURCE_MATERIAL21_UNRESOLVED")
        d=obj.read_typetree(check_read=False)
        saved=d.get("m_SavedProperties")
        if not isinstance(saved,dict):
            raise ValueError("ORIGINAL_MATERIAL_SAVED_PROPERTIES_UNAVAILABLE")
        values=dict(named_entries(saved.get("m_Floats",[])))
        cnt["material_renderer_slots"]+=1
        cnt["source_material_float_slot_count"]+=len(values)
        for v in values.values():
            near_source_scalar(v,0)
        for name,key in (("_Glossiness","glossiness"),
                         ("_GlossMapScale","gloss_map_scale"),
                         ("_Metallic","metallic"),
                         ("_BumpScale","normal_strength")):
            if name not in values:
                cnt[key+"_field_missing"]+=1
            else:
                cnt[key+"_field_present"]+=1
                cnt[key+"_exact_zero"]+=int(near_source_scalar(values[name],0))
                cnt[key+"_exact_one"]+=int(near_source_scalar(values[name],1))
                if key=="glossiness":
                    cnt["original_glossiness_matches_hardcoded_0_45"]+=int(
                        near_source_scalar(values[name],FALLBACK_GLOSS))
                    cnt["original_glossiness_differs_hardcoded_0_45"]+=int(
                        not near_source_scalar(values[name],FALLBACK_GLOSS))
    if cnt["material_renderer_slots"]!=7 or cnt["source_material_float_slot_count"]!=112:
        raise ValueError("ORIGINAL_MATERIAL_FLOAT_COUNT_DRIFT")

    tex=Counter()
    for e in entries:
        for m in e["materials"]:
            for role,link in m["textures"].items():
                if role not in ("basecolor","normal","metallic"):
                    raise ValueError("ORIGINAL_UNEXPECTED_TEXTURE_ROLE")
                obj=typed[link["owner"]].get(link["pid"])
                if obj is None or obj.type.name!="Texture2D":
                    raise ValueError("ORIGINAL_TEXTURE2D_MISSING")
                d=obj.read_typetree(check_read=False)
                color_space=d.get("m_ColorSpace")
                if type(color_space) is not int:
                    raise ValueError("ORIGINAL_TEXTURE_COLORSPACE_MISSING")
                tex[role+"_links"]+=1
                tex[role+"_source_srgb"]+=int(color_space==1)
                tex[role+"_source_linear"]+=int(color_space==0)
                tex[role+"_source_unknown"]+=int(color_space not in (0,1))
                # Existing Unity Standard fallback uses sRGB only for basecolor.
                fallback_srgb=role=="basecolor"
                tex[role+"_source_vs_standard_fallback_gamma_mismatch"]+=int(
                    (color_space==1)!=fallback_srgb if color_space in (0,1) else False)
    if any(tex[role+"_links"]!=7 for role in ("basecolor","normal","metallic")):
        raise ValueError("ORIGINAL_ALL_21_TEXTURE_ROLES_DRIFT")
    if cnt["glossiness_field_present"]+cnt["glossiness_field_missing"]!=7:
        raise ValueError("ORIGINAL_GLOSSINESS_SLOT_ACCOUNTING_ERROR")
    return dict(
        experiment="GFX-OWNER-002",source_sha=ZIP2_SHA,
        source_models=6,source_material_slots=7,source_texture_links=21,
        material_scalar_summary=dict(cnt),
        source_vs_existing_unity_standard_importer_gamma_counts=dict(tex),
        fallback_constant_used_for_comparison="UnityStandard._Glossiness hardcoded 0.45",
        sampler_color_space_code_meanings_from_unity2021_reference=True,
        real_shader48_glossiness_program_semantics_verified=False,
        original_shader48_material_to_register_link_verified=False,
        actual_android_source_material_shader48_pixels_verified=False,
        raw_original_material_float_values_or_source_ids_exported=False,
        raw_texture_or_shader_bytes_exported=False,
        phase_closed=False)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("GFX_OWNER002_SAFE_ORIGINAL_MATERIAL_IMPORT_DELTAS "+json.dumps(r,sort_keys=True))
if __name__=="__main__":
    main()
