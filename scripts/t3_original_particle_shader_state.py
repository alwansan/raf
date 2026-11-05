#!/usr/bin/env python3
"""T3: SHA-original 108-use ParticleSystemRenderer Shader48 one-Pass state.

Authenticates six original scenes and four original Shader/Material owners,
selects the unique source ParticleSystemRenderer rank via PRIVATE owner/PathID
mapping, and inspects only its own original parsed Shader Pass m_State.
No raw shader source, owner, names, PathIDs, GUIDs or material identities leave
this process. Blend categories are serialized SOURCE ONLY, never device pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as original
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_depth_shaderlab import BLEND, BLENDOP, property_name, val, render_state, color_mask

EXPECTED_RANKS = [108, 34, 34, 20, 16, 3]
STATUS = "SHA_ORIGINAL_PARTICLE_108_PASS_RENDER_STATE_CLASSIFIED"
ALPHA_FACTORS = frozenset((5, 7, 8, 9, 10))


def field(record, allowed):
    """Return explicit numeric enum or property-driven unknown, no source name."""
    if not isinstance(record, dict):
        raise ValueError("invalid_original_particle_Shader_state_field")
    if property_name(record) is not None:
        return None
    raw = val(record)
    if (type(raw) not in (int, float) or not raw == raw
            or not float(raw).is_integer() or int(raw) not in allowed):
        raise ValueError("unsupported_original_particle_Shader_state_enum")
    return int(raw)


def blend_family(src, dst):
    if src is None or dst is None:
        return "PROPERTY_DRIVEN_UNRESOLVED"
    if src == 1 and dst == 0:
        return "REPLACE"
    if src in ALPHA_FACTORS or dst in ALPHA_FACTORS:
        return "ALPHA_DEPENDENT"
    if src == 1 and dst == 1:
        return "ADDITIVE_NO_ALPHA_FACTOR"
    return "OTHER_NUMERIC_BLEND"


def classify_state(state):
    """Public-safe ShaderLab source-state classification, fail closed.

    Do not infer alpha clipping or authored fragment alpha handling from
    fixed function Blend alone. Shader source and runtime selection unknown.
    """
    if type(state) is not dict or type(state.get("rtSeparateBlend")) is not bool:
        raise ValueError("missing_or_invalid_original_particle_render_state")
    blend = state.get("rtBlend0")
    if not isinstance(blend, dict):
        raise ValueError("missing_original_particle_rtBlend0")
    src=field(blend.get("srcBlend"),BLEND)
    dst=field(blend.get("destBlend"),BLEND)
    src_a=field(blend.get("srcBlendAlpha"),BLEND)
    dst_a=field(blend.get("destBlendAlpha"),BLEND)
    op=field(blend.get("blendOp"),BLENDOP)
    op_a=field(blend.get("blendOpAlpha"),BLENDOP)
    mask=field(blend.get("colMask"),frozenset(range(16)))
    zwrite=field(state.get("zWrite"),frozenset((0,1)))
    ztest=field(state.get("zTest"),frozenset(range(9)))
    atoc=field(state.get("alphaToMask"),frozenset((0,1)))
    cull=field(state.get("culling"),frozenset((0,1,2)))
    if state["rtSeparateBlend"]:
        # Another seven RT outputs may carry different factors. Do not
        # assert one target's blend describes the entire Shader.
        color_category="MULTI_RENDER_TARGET_UNRESOLVED"
        alpha_category="MULTI_RENDER_TARGET_UNRESOLVED"
    else:
        color_category=blend_family(src,dst)
        alpha_category=blend_family(src_a,dst_a)
    # Preserve the old W1/default behavior and prove whether the source is
    # independently supported by the opt-in Unity 2021.3 ColorWriteMask path.
    # Keep ShaderLab source text PRIVATE; export only public-safe categories.
    try:
        render_state(state)
    except (ValueError,KeyError,TypeError):
        translator=False
    else:
        translator=True
    try:
        render_state(state,allow_selective_color_mask=True)
    except (ValueError,KeyError,TypeError):
        selective_translator=False
    else:
        selective_translator=True
    channel_subset=(color_mask({"name":"<noninit>","val":mask})
                    if mask is not None else "PROPERTY_DRIVEN_UNRESOLVED")
    return {
        "original_pass_rt_separate_blend":state["rtSeparateBlend"],
        "original_pass_color_blend_category":color_category,
        "original_pass_alpha_channel_blend_category":alpha_category,
        "original_pass_blend_operation_known":op is not None and op_a is not None,
        "original_pass_color_mask_category":(
            "PROPERTY_DRIVEN_UNRESOLVED" if mask is None else
            "RGBA" if mask==15 else "NONE" if mask==0 else "PARTIAL"),
        "original_pass_color_mask_shaderlab_channels":channel_subset,
        "original_pass_depth_write_category":(
            "PROPERTY_DRIVEN_UNRESOLVED" if zwrite is None else
            "ON" if zwrite==1 else "OFF"),
        "original_pass_depth_test_category":(
            "PROPERTY_DRIVEN_UNRESOLVED" if ztest is None else
            "OFF" if ztest==0 else "ENABLED_NUMERIC"),
        "original_pass_alpha_to_coverage_category":(
            "PROPERTY_DRIVEN_UNRESOLVED" if atoc is None else
            "ON" if atoc==1 else "OFF"),
        "original_pass_culling_category":(
            "PROPERTY_DRIVEN_UNRESOLVED" if cull is None else
            ("OFF" if cull==0 else "ON")),
        "original_pass_fixed_function_state_translator_accepted":translator,
        "original_pass_opt_in_selective_colormask_translator_accepted":selective_translator,
        "serialized_Unity2021_ColorWriteMask_ABGR_bits_not_reversed":True,
        "original_pass_source_fixed_function_only":True,
        "original_fragment_alpha_output_or_discard_not_verified":True,
        "native_ShaderLab_or_Android_pixels_not_verified":True,
    }


def inspect_parsed(parsed):
    if not isinstance(parsed,dict):
        raise ValueError("missing_original_particle_parsed_Shader")
    subs=parsed.get("m_SubShaders")
    if type(subs) is not list or len(subs)!=1:
        raise ValueError("unexpected_particle_source_SubShader_count")
    passes=subs[0].get("m_Passes") if isinstance(subs[0],dict) else None
    if type(passes) is not list or len(passes)!=1:
        raise ValueError("unexpected_particle_source_Pass_count")
    p=passes[0]
    if not isinstance(p,dict) or type(p.get("m_Type")) is not int:
        raise ValueError("invalid_particle_source_Pass_record")
    if p["m_Type"]!=0:
        raise ValueError("non_normal_particle_source_Pass_unclassified")
    result=classify_state(p.get("m_State"))
    return {"source_108_particle_shader_original_SubShader_count":1,
            "source_108_particle_shader_original_Pass_count":1,
            "source_108_particle_shader_original_normal_Pass":True,**result}


def probe(source:Path, manifest:Path):
    private={}
    report=original.load_original(source,manifest,
        private_particle_slot_counts=private)
    if (report.get("status")!=original.STATUS
        or report.get("six_original_scenes_sha_verified") is not True
        or report.get("original_particle_Shader48_ranked_material_slot_use_no_identity")!=EXPECTED_RANKS
        or report.get("original_particle_highest_Shader48_unique") is not True
        or report.get("original_particle_highest_Shader48_original_pass_count")!=1
        or report.get("original_particle_highest_Shader48_nonparticle_renderer_slots")!=0
        or sorted(private.values(),reverse=True)!=EXPECTED_RANKS):
        raise ValueError("unauthenticated_original_particle_source_scope")
    top=[k for k,v in private.items() if v==EXPECTED_RANKS[0]]
    if len(top)!=1:
        raise ValueError("ambiguous_original_particle_Shader48_identity")
    owner,pid=top[0]
    if (owner not in original.SHADER_OWNERS_SELECTED
        or type(pid) is not int or pid<=0):
        raise ValueError("invalid_private_original_particle_source_object")
    path=source/"Raft_Data"/owner
    if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("changed_original_particle_Shader_owner_SHA")
    import UnityPy
    matches=[o for o in UnityPy.load(str(path)).file.objects.values()
             if o.path_id==pid]
    if len(matches)!=1 or matches[0].type.name!="Shader":
        raise ValueError("original_particle_selected_object_not_Shader48")
    out=inspect_parsed(matches[0].read_typetree().get("m_ParsedForm"))
    return {"schema_version":1,"status":STATUS,
            "source_6_original_scenes_SHA_verified":True,
            "source_4_original_shader_owners_SHA_verified":True,
            "source_particles_true_Shader48_material_slots":215,
            "source_particle_shader_slots_ranked_no_identity":EXPECTED_RANKS,
            "source_highest_particle_Shader48_slots":108,
            "source_highest_particle_Shader48_distinct_renderer_objects":54,
            "source_shader_names_ids_guids_hashes_published":False,
            "original_source_ShaderLab_or_device_modified":False,
            **out}


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        a.add_argument("--"+key,required=True,type=Path)
    args=a.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_particle_state_public_report")
    try:
        result=probe(args.original,args.manifest)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "source_shader_names_ids_guids_hashes_published":False,
                "native_ShaderLab_or_Android_pixels_not_verified":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE_RENDER_STATE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
