"""Find exact original pairs for specific phase-one rendering contexts."""
import argparse
from collections import Counter
import json
from pathlib import Path

from gfxlab.tools.gfx118_m02_original_forward import keywords
from gfxlab.tools.multi_shader_material_cb_payload095 import original_materials_private, saved_values_private
from gfxlab.tools.multi_shader_one_pass_spirv import exact_pairs
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.multi_sevenpass_state_enum_semantics import STATE_FIELDS, classify_state_value
from gfxlab.tools.multi_shader_state_material_float_link import normalize_private_state_name
from gfxlab.tools.original_model_probe import ZIP2_SHA

CONTEXTS = {
    "FORWARD": (("directional", {"DIRECTIONAL"}), ("directional_screen_shadow", {"DIRECTIONAL", "SHADOWS_SCREEN"})),
    "FORWARD_DELTA": (("directional", {"DIRECTIONAL"}), ("point", {"POINT"})),
    "ShadowCaster": (("depth", {"SHADOWS_DEPTH"}), ("cube", {"SHADOWS_CUBE"})),
    "DEFERRED": (("unlit_gbuffer", set()),),
}


def inventory(stage):
    tree, _, programs = load_original_shader_private(stage)
    parsed = tree["m_ParsedForm"]
    declared = {row["m_Name"] for row in parsed["m_PropInfo"]["m_Props"]}
    materials = original_materials_private(stage)
    material_keywords = [set(material["m_ValidKeywords"]) for material in materials]
    if len(materials) != 7 or any(material.get("m_InvalidKeywords") for material in materials):
        raise ValueError("Unexpected original material keywords")
    source_values = [saved_values_private(material) for material in materials]
    rows = []
    for sub_index, sub in enumerate(parsed["m_SubShaders"]):
        for pass_index, shader_pass in enumerate(sub["m_Passes"]):
            state = shader_pass["m_State"]
            name = state["m_Name"]
            pairs = list(exact_pairs(shader_pass))
            tags = Counter()
            for vertex, fragment in pairs:
                chosen = frozenset(keywords(programs, vertex))
                if chosen != frozenset(keywords(programs, fragment)):
                    raise ValueError("Original stage keyword mismatch")
                tags[chosen] += 1
            pass_keywords = set().union(*tags)
            contexts = {}
            for label, engine_keywords in CONTEXTS[name]:
                slots = [tags[frozenset(keys | engine_keywords)] for keys in material_keywords]
                projected = [tags[frozenset((keys & pass_keywords) | engine_keywords)]
                             for keys in material_keywords]
                contexts[label] = {"exact_single_slots": slots.count(1),
                                   "no_exact_pair_slots": slots.count(0),
                                   "multiple_pair_slots": sum(value > 1 for value in slots),
                                   "candidate_single_slots_after_filtering_pass_absent_keywords": projected.count(1)}
            states = {}
            for field, enums in STATE_FIELDS.items():
                raw = state.get(field)
                kind = classify_state_value(raw, enums)
                row = {"serialized_kind": kind}
                if kind == "named_dynamic_override":
                    key, _ = normalize_private_state_name(raw["name"])
                    row["declared_property"] = key in declared
                    row["matching_saved_float_slots"] = sum(key in values and values[key][0] == "float" for values in source_values)
                states[field] = row
            rows.append({"subshader": sub_index, "pass": pass_index, "name": name,
                         "exact_linkable_pairs": len(pairs), "contexts": contexts, "states": states})
    if len(rows) != 7 or sum(row["exact_linkable_pairs"] for row in rows) != 524:
        raise ValueError("Original pass topology changed")
    return {"experiment": "GFX126", "source_sha": ZIP2_SHA, "passes": rows,
            "filtered_matches_are_candidates_until_unity_runtime_selection_verified": True,
            "runtime_state_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    args.safe.write_text(json.dumps(inventory(args.stage), indent=2) + "\n")
