"""Inventory exact directional Forward choices for the seven source renderer slots."""
import argparse
import json
from pathlib import Path

from gfxlab.tools.gfx118_m02_original_forward import keywords
from gfxlab.tools.multi_shader_material_cb_payload095 import original_materials_private
from gfxlab.tools.multi_shader_one_pass_spirv import exact_pairs
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.original_model_probe import ZIP2_SHA


def audit(stage):
    materials = original_materials_private(stage)
    labels = ("M00/0","M01/0","M02/0","M03/0","M03/1","M04/0","M05/0")
    if len(materials) != len(labels):
        raise ValueError("Source renderer slots changed")
    tree, _, programs = load_original_shader_private(stage)
    forward = tree["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"][0]
    if forward["m_State"]["m_Name"] != "FORWARD":
        raise ValueError("Source Forward pass changed")
    pairs = [(keywords(programs,v),keywords(programs,f),v,f) for v,f in exact_pairs(forward)]
    resolved = set()
    rows = []
    for label, material in zip(labels,materials,strict=True):
        source = set(material["m_ValidKeywords"])
        if material.get("m_InvalidKeywords"):
            raise ValueError("Unexpected invalid material keywords")
        expected = source | {"DIRECTIONAL"}
        choices = [(v["m_BlobIndex"],f["m_BlobIndex"]) for vk,fk,v,f in pairs if vk == fk == expected]
        if len(choices) == 1:
            resolved.add(choices[0])
        rows.append({"renderer_slot":label,"material_keyword_count":len(source),
                     "exact_directional_forward_pairs":len(choices),
                     "requires_explicit_variant_resolution":len(choices)!=1})
    return {"experiment":"GFX122","source_sha":ZIP2_SHA,"directional_forward_slots":rows,
            "unique_selected_pairs":len(resolved),
            "device_draw_slots_already_verified":1,"phase_closed":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--safe",type=Path,required=True)
    a=parser.parse_args()
    d=audit(a.stage)
    a.safe.write_text(json.dumps(d,indent=2)+"\n")
