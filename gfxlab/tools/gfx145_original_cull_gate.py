"""GFX145: source-pinned Shader48 Cull metadata fallback and material override gate.

This emits enum names and aggregate counts only; never original ShaderLab
property strings, material values, raw shaders or GPU runtime assertions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from gfxlab.tools.multi_sevenpass_state_enum_semantics import CULL, classify_state_value
from gfxlab.tools.multi_shader_state_material_float_link import normalize_private_state_name
from gfxlab.tools.original_model_probe import ZIP2_SHA, stage_originals


def inspect_cull(raw, properties: set[str], saved_materials: list[dict]) -> dict:
    if not isinstance(properties, set) or not isinstance(saved_materials, list) or not saved_materials:
        raise ValueError("Invalid source material or property inventory")
    if isinstance(raw, dict):
        name = raw.get("name")
        fallback = classify_state_value(raw.get("val"), CULL)
    else:
        name, fallback = None, classify_state_value(raw, CULL)
    if name is not None and not isinstance(name, str):
        raise ValueError("Invalid source Cull dynamic-override name")
    key, bracketed = normalize_private_state_name(name)
    has_override = bool(key)
    values = Counter()
    matching = non_enum = 0
    if has_override:
        for material in saved_materials:
            entry = material.get(key)
            if entry is None:
                continue
            matching += 1
            if not isinstance(entry, tuple) or len(entry)!=2 or entry[0]!="float" or len(entry[1])!=1:
                non_enum += 1
                continue
            category = classify_state_value(entry[1][0], CULL)
            if category in CULL.values():
                values[category] += 1
            else:
                non_enum += 1
    return {
        "fallback_cull_enum":fallback,
        "named_dynamic_override":has_override,
        "name_is_bracketed_ShaderLab_token":bracketed,
        "name_declared_as_ShaderLab_property":key in properties if has_override else False,
        "material_slots_with_matching_saved_float":matching,
        "material_slots_with_unrecognized_enum":non_enum,
        "matching_material_cull_enum_categories":dict(sorted(values.items())),
        "runtime_unity_effective_cull_verified":False,
        "runtime_unity_override_resolution_verified":False,
    }


def inspect_original(stage):
    from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
    from gfxlab.tools.multi_shader_material_cb_payload095 import (
        original_materials_private, saved_values_private
    )
    tree, _, _ = load_original_shader_private(stage)
    parsed = tree["m_ParsedForm"]
    props = {p["m_Name"] for p in parsed["m_PropInfo"]["m_Props"]}
    saved = [saved_values_private(m) for m in original_materials_private(stage)]
    if len(saved)!=7:
        raise ValueError("Original Shader48 seven material slots changed")
    passes=[]
    for si, group in enumerate(parsed["m_SubShaders"]):
        for pi, p in enumerate(group["m_Passes"]):
            raw = p["m_State"]["culling"]
            row = inspect_cull(raw,props,saved)
            row.update(subshader_index=si,pass_index=pi,
                       pass_category=p["m_State"]["m_Name"])
            passes.append(row)
    if len(passes)!=7 or passes[0]["pass_category"]!="FORWARD":
        raise ValueError("Original Shader48 pass graph changed")
    return {
        "experiment":"GFX145", "source_sha":ZIP2_SHA,
        "original_material_slots":7,"original_shader_passes":7,
        "selected_m03_1_source_forward_cull":passes[0],
        "all_passes":passes,
        "source_metadata_only":True,
        "source_Cull_fallback_is_not_proof_of_runtime_effective_state":True,
        "original_unity_Cull_runtime_verified":False,
        "original_game_PC_Android_pixel_parity":False,"phase_closed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--safe",type=Path,required=True)
    args=p.parse_args()
    # stage_originals enforces ZIP2_SHA source identity and reconstructs only
    # private fixture files under runner temp.
    stage=stage_originals(args.zip2,args.stage)
    result=inspect_original(stage)
    args.safe.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
