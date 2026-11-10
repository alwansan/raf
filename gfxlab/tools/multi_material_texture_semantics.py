#!/usr/bin/env python3
"""GFX-MULTI-023: original Material/Texture2D semantic and channel census.

All source names, PPtrs, raw pixels and texture bytes remain private in the
ephemeral runner. Only aggregate role/format/settings/channel counts are emitted.
Channel patterns are diagnostic clues, not proof of DXT5nm or shader semantics.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import (
    model_plan, fill_sparse_authenticated_streams, all_model_entries,
)
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_texture_readiness import (
    select_exact_renderer, classify_standard, pairs,
)
from gfxlab.tools.shears_provenance_probe import resolve_pptr

ROLES=("basecolor","normal","metallic")
MAX_PIXELS=33_554_432


def named_entries(raw):
    """Read Unity serialized name/value pairs without exporting their names."""
    if raw is None:
        return []
    if not isinstance(raw,list):
        raise ValueError("ORIGINAL_MATERIAL_PROPERTY_CONTAINER_NOT_ARRAY")
    result=[]
    seen=set()
    for entry in raw:
        if isinstance(entry,(list,tuple)) and len(entry)==2:
            name,value=entry
        elif isinstance(entry,dict) and set(entry)=={"m_First","m_Second"}:
            name,value=entry["m_First"],entry["m_Second"]
        elif isinstance(entry,dict) and len(entry)==1:
            name,value=next(iter(entry.items()))
        else:
            raise ValueError("ORIGINAL_MATERIAL_PROPERTY_PAIR_SHAPE_INVALID")
        if not isinstance(name,str) or not name or name in seen:
            raise ValueError("ORIGINAL_MATERIAL_PROPERTY_NAME_INVALID_OR_DUPLICATE")
        seen.add(name)
        result.append((name,value))
    return result


def safe_enum_code(value):
    if type(value) is int and -10000 <= value <= 10000:
        return str(value)
    return "unknown"


def uv_is_identity(scale,offset):
    if not isinstance(scale,(list,tuple)) or len(scale)!=2:
        raise ValueError("ORIGINAL_UV_SCALE_SHAPE_INVALID")
    if not isinstance(offset,(list,tuple)) or len(offset)!=2:
        raise ValueError("ORIGINAL_UV_OFFSET_SHAPE_INVALID")
    vals=list(scale)+list(offset)
    if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1000 for x in vals):
        raise ValueError("ORIGINAL_UV_TRANSFORM_VALUE_INVALID")
    return (all(abs(float(x)-1.0)<1e-6 for x in scale)
            and all(abs(float(x))<1e-6 for x in offset))


def channel_variability(image):
    rgba=image.convert("RGBA")
    channels=rgba.split()
    if len(channels)!=4:
        raise ValueError("DECODED_TEXTURE_NOT_RGBA")
    result={}
    for name,channel in zip(("R","G","B","A"),channels):
        lo,hi=channel.getextrema()
        if type(lo) is not int or type(hi) is not int or not (0<=lo<=hi<=255):
            raise ValueError("DECODED_TEXTURE_CHANNEL_RANGE_INVALID")
        result[name]=(lo<hi)
    result["alpha_fully_opaque"]=(channels[3].getextrema()==(255,255))
    return result


def _material_keys(source,typed):
    private,_=selected_five(source)
    keys=[(m["owner"],m["material_pid"])
          for entry in private["selected"] for m in entry["materials"]]
    envs,_,owner,renderer=select_exact_renderer(source)
    refs=renderer.get("m_Materials")
    if not isinstance(refs,list) or len(refs)!=1:
        raise ValueError("ORIGINAL_SHEARS_MATERIAL_SLOT_DRIFT")
    externals=[x.path for x in envs[owner].file.externals]
    _,shears_key=resolve_pptr(refs[0],owner,externals)
    if shears_key is None:
        raise ValueError("ORIGINAL_SHEARS_MATERIAL_POINTER_UNRESOLVED")
    keys.insert(0,shears_key)
    if len(keys)!=7:
        raise ValueError("ORIGINAL_SEVEN_MATERIAL_KEYS_DRIFT")
    for key in keys:
        obj=typed[key[0]].get(key[1])
        if obj is None or obj.type.name!="Material":
            raise ValueError("ORIGINAL_MATERIAL21_MISSING")
    return keys,envs


def _material_slot_census(source,typed):
    keys,envs=_material_keys(source,typed)
    totals=Counter()
    roles=Counter()
    tint=Counter()
    for owner,pid in keys:
        obj=typed[owner].get(pid)
        tree=obj.read_typetree(check_read=False)
        saved=tree.get("m_SavedProperties")
        if not isinstance(saved,dict):
            raise ValueError("ORIGINAL_MATERIAL_SAVED_PROPERTIES_MISSING")
        colors=named_entries(saved.get("m_Colors",[]))
        floats=named_entries(saved.get("m_Floats",[]))
        ints=named_entries(saved.get("m_Ints",[]))
        texenvs=named_entries(saved.get("m_TexEnvs",[]))
        totals["material_slots"]+=1
        totals["color_slots"]+=len(colors)
        totals["float_slots"]+=len(floats)
        totals["int_slots"]+=len(ints)
        totals["texenv_slots"]+=len(texenvs)
        for name,value in colors:
            if not isinstance(value,dict) or not all(k in value for k in ("r","g","b","a")):
                raise ValueError("ORIGINAL_COLOR_SLOT_SHAPE_INVALID")
            vals=[value[k] for k in ("r","g","b","a")]
            if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>64 for x in vals):
                raise ValueError("ORIGINAL_COLOR_SLOT_VALUE_INVALID")
            if name in ("_Color","_BaseColor"):
                tint["authored_tint_slots"]+=1
                tint["identity_white_tints"]+=int(all(abs(float(x)-1.0)<1e-6 for x in vals))
                tint["nonwhite_tints"]+=int(not all(abs(float(x)-1.0)<1e-6 for x in vals))
        for _,value in floats:
            if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>10000:
                raise ValueError("ORIGINAL_FLOAT_SLOT_VALUE_INVALID")
        for _,value in ints:
            if type(value) is not int or abs(value)>1000000:
                raise ValueError("ORIGINAL_INT_SLOT_VALUE_INVALID")
        material_externals=[x.path for x in envs[owner].file.externals]
        for name,value in texenvs:
            if not isinstance(value,dict) or not isinstance(value.get("m_Texture"),dict):
                raise ValueError("ORIGINAL_TEXENV_SLOT_SHAPE_INVALID")
            kind,key=resolve_pptr(value["m_Texture"],owner,material_externals)
            if kind=="null":
                totals["null_texenv_slots"]+=1
                continue
            if key is None:
                raise ValueError("ORIGINAL_TEXENV_POINTER_UNRESOLVED")
            role=classify_standard(name)
            if role not in ROLES:
                totals["bound_nonstandard_texenv_slots"]+=1
            else:
                roles[role]+=1
                totals["bound_texenv_slots"]+=1
    if totals["material_slots"]!=7 or totals["texenv_slots"]!=63:
        raise ValueError("ORIGINAL_MATERIAL_TEXENV_TOTAL_DRIFT")
    if totals["bound_texenv_slots"]!=21 or totals["null_texenv_slots"]!=42:
        raise ValueError("ORIGINAL_MATERIAL_TEXENV_POINTER_TOTAL_DRIFT")
    if any(roles[r]!=7 for r in ROLES):
        raise ValueError("ORIGINAL_TEXTURE_ROLE_DISTRIBUTION_DRIFT")
    return {
        "material_slot_totals":dict(totals),
        "texture_role_counts":dict(roles),
        "tint_slot_summary":dict(tint),
    }


def audit_source(source,plan):
    entries,typed,_=all_model_entries(source)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("ORIGINAL_SIX_MODEL_SELECTION_DRIFT")
    if sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("ORIGINAL_SEVEN_MATERIAL_SLOTS_DRIFT")
    material_census=_material_slot_census(source,typed)

    role_stats={r:Counter() for r in ROLES}
    format_codes={r:Counter() for r in ROLES}
    color_space_codes={r:Counter() for r in ROLES}
    mip_counts={r:Counter() for r in ROLES}
    filter_codes={r:Counter() for r in ROLES}
    wrap_codes={r:Counter() for r in ROLES}
    channel_stats={r:Counter() for r in ROLES}
    uv_stats={r:Counter() for r in ROLES}
    tint_summary=Counter()
    decoded=0
    total_pixels=0
    texture_count=0

    for entry in plan["entries"]:
        for material in entry["materials"]:
            tint=material.get("tint")
            if tint is not None:
                if not isinstance(tint,list) or len(tint)!=4 or any(
                    type(x) not in (int,float) or not math.isfinite(x) or abs(x)>64 for x in tint
                ):
                    raise ValueError("ORIGINAL_MATERIAL_TINT_SHAPE_INVALID")
                tint_summary["present"]+=1
                is_white=all(abs(float(x)-1.0)<1e-6 for x in tint)
                tint_summary["identity_white"]+=int(is_white)
                tint_summary["nonwhite"]+=int(not is_white)
            for role,link in material["textures"].items():
                if role not in ROLES:
                    raise ValueError("ORIGINAL_TEXTURE_ROLE_NOT_ALLOWLISTED")
                texture_count+=1
                uv_stats[role]["total"]+=1
                uv_stats[role]["identity"]+=int(uv_is_identity(link["uv_scale"],link["uv_offset"]))
                uv_stats[role]["nonidentity"]+=int(not uv_is_identity(link["uv_scale"],link["uv_offset"]))
                obj=typed[link["owner"]].get(link["pid"])
                if obj is None or obj.type.name!="Texture2D":
                    raise ValueError("ORIGINAL_TEXTURE2D_POINTER_DRIFT")
                tree=obj.read_typetree(check_read=False)
                width,height=tree.get("m_Width"),tree.get("m_Height")
                if type(width) is not int or type(height) is not int or not (0<width<=8192 and 0<height<=8192):
                    raise ValueError("ORIGINAL_TEXTURE_DIMENSIONS_INVALID")
                if (width,height)!=(link["width"],link["height"]):
                    raise ValueError("ORIGINAL_TEXTURE_DIMENSIONS_CHANGED_AFTER_HYDRATION")
                if width*height>MAX_PIXELS:
                    raise ValueError("ORIGINAL_TEXTURE_PIXEL_BUDGET_EXCEEDED")

                fmt=tree.get("m_TextureFormat")
                format_codes[role][safe_enum_code(fmt)]+=1
                color_space=tree.get("m_ColorSpace")
                color_space_codes[role][safe_enum_code(color_space)]+=1
                mip=tree.get("m_MipCount")
                mip_counts[role][safe_enum_code(mip)]+=1
                role_stats[role]["textures"]+=1
                role_stats[role]["pixels"]+=width*height
                role_stats[role]["dimensions_verified"]+=1
                role_stats[role]["format_field_present"]+=int(type(fmt) is int)
                role_stats[role]["color_space_field_present"]+=int(type(color_space) is int)
                role_stats[role]["mip_count_field_present"]+=int(type(mip) is int)
                role_stats[role]["streamed_source"]+=int(bool(link.get("streamed")))
                settings=tree.get("m_TextureSettings")
                if isinstance(settings,dict):
                    role_stats[role]["texture_settings_present"]+=1
                    filter_codes[role][safe_enum_code(settings.get("m_FilterMode"))]+=1
                    wrap_codes[role][safe_enum_code(settings.get("m_WrapMode"))]+=1
                    role_stats[role]["anisotropy_field_present"]+=int(type(settings.get("m_Aniso")) is int)
                    role_stats[role]["mip_bias_field_present"]+=int(type(settings.get("m_MipBias")) in (int,float))
                else:
                    filter_codes[role]["unknown"]+=1
                    wrap_codes[role]["unknown"]+=1
                alpha_flag=tree.get("m_AlphaIsTransparency")
                role_stats[role]["alpha_transparency_true"]+=int(alpha_flag is True)
                role_stats[role]["alpha_transparency_false"]+=int(alpha_flag is False)

                try:
                    image=obj.read().image
                except Exception:
                    raise ValueError("ORIGINAL_TEXTURE2D_DECODE_FAILED") from None
                if image is None or image.size!=(width,height):
                    raise ValueError("ORIGINAL_TEXTURE2D_DECODE_DIMENSION_MISMATCH")
                channels=channel_variability(image)
                decoded+=1
                total_pixels+=width*height
                for channel in ("R","G","B","A"):
                    channel_stats[role][channel+"_variable"]+=int(channels[channel])
                    channel_stats[role][channel+"_constant"]+=int(not channels[channel])
                channel_stats[role]["alpha_fully_opaque"]+=int(channels["alpha_fully_opaque"])
                channel_stats[role]["alpha_not_fully_opaque"]+=int(not channels["alpha_fully_opaque"])
                if role=="normal":
                    channel_stats[role]["ag_candidate"]+=int(
                        channels["A"] and channels["G"] and not channels["R"] and not channels["B"]
                    )
                if role=="metallic":
                    channel_stats[role]["alpha_variable_candidate"]+=int(channels["A"])

    if texture_count!=21 or decoded!=21:
        raise ValueError("ORIGINAL_21_TEXTURE_DECODE_TOTAL_DRIFT")
    if any(role_stats[r]["textures"]!=7 for r in ROLES):
        raise ValueError("ORIGINAL_TEXTURE_ROLE_COUNT_DRIFT")
    return {
        "experiment":"GFX-MULTI-023",
        "source_sha":ZIP2_SHA,
        "model_count":6,
        "material_slot_count":7,
        "source_texture_count":texture_count,
        "decoded_texture_count":decoded,
        "sparse_stream_chunks":plan["safe"]["stream_chunks"],
        "sparse_stream_bytes":plan["safe"]["stream_selected_bytes"],
        "material_census":material_census,
        "material_tint_summary":dict(tint_summary),
        "uv_transform_counts_by_role":{r:dict(uv_stats[r]) for r in ROLES},
        "texture_format_code_counts_by_role":{r:dict(format_codes[r]) for r in ROLES},
        "texture_color_space_code_counts_by_role":{r:dict(color_space_codes[r]) for r in ROLES},
        "texture_mip_count_code_counts_by_role":{r:dict(mip_counts[r]) for r in ROLES},
        "texture_filter_mode_code_counts_by_role":{r:dict(filter_codes[r]) for r in ROLES},
        "texture_wrap_mode_code_counts_by_role":{r:dict(wrap_codes[r]) for r in ROLES},
        "texture_metadata_and_channel_counts_by_role":{
            r:{**dict(role_stats[r]),**dict(channel_stats[r])} for r in ROLES
        },
        "total_decoded_pixels":total_pixels,
        "source_material_names_or_ids_exported":False,
        "source_texture_pixels_or_files_exported":False,
        "source_shader_or_register_data_exported":False,
        "original_shader_restored":False,
        "actual_android_original_shader_pixels_verified":False,
        "phase_closed":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("plan","audit"))
    parser.add_argument("--zip2",type=Path,required=True)
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--private-plan",type=Path,required=True)
    parser.add_argument("--paths",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    source=stage_originals(args.zip2,args.stage)
    if args.command=="plan":
        plan=model_plan(args.zip2,source)
        if len(plan["entries"])!=6 or plan["safe"]["materials"]!=7 or plan["safe"]["textures"]!=21:
            raise ValueError("ORIGINAL_SOURCE_PLAN_COUNTS_DRIFT")
        args.private_plan.parent.mkdir(parents=True,exist_ok=True)
        args.private_plan.write_text(json.dumps(plan,sort_keys=True))
        if args.paths is None:
            raise ValueError("MISSING_SPARSE_PATH_LIST_OUTPUT")
        args.paths.write_text("\n".join("/"+p for p in plan["paths"])+"\n")
        print("GFX_MULTI023_SAFE_PLAN "+json.dumps(plan["safe"],sort_keys=True))
        return
    if args.out is None:
        raise ValueError("MISSING_SAFE_REPORT_OUTPUT")
    plan=json.loads(args.private_plan.read_text())
    if plan.get("source_sha")!=ZIP2_SHA:
        raise ValueError("PRIVATE_SOURCE_PLAN_SHA_MISMATCH")
    fill_sparse_authenticated_streams(args.zip2,source,plan)
    report=audit_source(source,plan)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI023_SAFE_MATERIAL_TEXTURE_SEMANTICS "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
