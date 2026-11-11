"""Prepare the M02 depth ShadowCaster candidate and inventory inputs for a draw."""
import argparse
import json
from pathlib import Path
import shutil

from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.gfx119_prepare_draw import fixture_consumer
from gfxlab.tools.gfx121_forward_fixture_values import engine_values, pack_buffer
from gfxlab.tools.multi_sevenpass_state_enum_semantics import STATE_FIELDS, classify_state_value
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private


def fit_shadow_world_to_object(out):
    """The source b4 has seven vec4s, with only three WorldToObject rows."""
    path = out / "vertex.json"
    contract = json.loads(path.read_text())
    group, = [g for g in contract["groups"] if g["name"] == "UnityPerDraw"]
    binding, = [b for b in contract["bindings"] if b["name"] == "UnityPerDraw" and b["type"] == 1]
    field, = [f for f in group["parameters"].values() if f["name"] == "unity_WorldToObject"]
    if (contract["sizes"][str(binding["index"])], field["index"], field["rows"], field["columns"]) != (7, 64, 4, 4):
        raise ValueError("ShadowCaster WorldToObject layout changed")
    field["rows"] = 3
    path.write_text(json.dumps(contract))


def prepare(stage, mesh, out, *, direct3d=False):
    shader = load_original_shader_private(stage)
    row, = [p for p in shader[0]["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"]
            if p["m_State"]["m_Name"] == "ShadowCaster"]
    report = audit(stage, not direct3d, fixture_consumer(out, direct3d=direct3d), shader_source=shader,
                   pass_name="ShadowCaster", engine_keywords=("SHADOWS_DEPTH",), filter_absent_keys=True)
    fit_shadow_world_to_object(out)
    engine = engine_values(mesh.read_bytes(), direct3d=direct3d)
    shutil.copyfile(mesh, out / "mesh.bin")
    shutil.copyfile(mesh.with_name("indices.bin"), out / "indices.bin")
    missing = {}
    for name in ("vertex", "fragment"):
        contract = json.loads((out / (name + ".json")).read_text())
        slots = {binding["name"]: binding["index"] for binding in contract["bindings"] if binding["type"] == 1}
        for group in contract["groups"]:
            slot = slots[group["name"]]
            mask = (out / f"{name}-{slot}.mask").read_bytes()
            for field in group["parameters"].values():
                start = field["index"]
                size = 4 * field["columns"] * field["rows"]
                if not all(mask[start:start + size]) and field["name"] not in engine:
                    missing.setdefault(field["name"], set()).add(name)
    if direct3d:
        if set(missing) != {"unity_LightShadowBias"}:
            raise ValueError("Unexpected source shadow semantics")
        engine["unity_LightShadowBias"] = (0, 0, 0, 0)
        engine["unity_WorldToObject"] = engine["unity_WorldToObject"][:12]
        for name, count in (("vertex", 5), ("fragment", 1)):
            contract = json.loads((out / (name + ".json")).read_text())
            groups = {g["name"]: g for g in contract["groups"]}
            slots = {b["index"]: b["name"] for b in contract["bindings"] if b["type"] == 1}
            textures = [(b["name"], b["index"], b["extra"]) for b in contract["bindings"] if b["type"] == 0]
            if set(slots) != set(range(count)) or textures != (
                [("_MainTex", 0, 0)] if name == "fragment" else []
            ):
                raise ValueError("Unexpected ShadowCaster slots")
            for slot, group in slots.items():
                data, _ = pack_buffer((out / f"{name}-{slot}.bin").read_bytes(),
                                      (out / f"{name}-{slot}.mask").read_bytes(),
                                      groups[group], engine, True)
                (out / f"{name}-light-{slot}.bin").write_bytes(data)
    return {"experiment": "GFX131", "source_sha": report["source_sha"],
            "source_pair_count": report["exact_source_pair_count"],
            "world_to_object_rows_in_source_buffer": 3,
            "filtered_material_keywords": report["pass_absent_material_keywords_filtered"],
            "stages": report["stages"], "gles_offline_link_passed": report["gles_offline_link_passed"],
            "additional_uniform_semantic_count": len(missing),
            "additional_uniform_semantic_stage_counts": {
                stage_name: sum(stage_name in names for names in missing.values())
                for stage_name in ("vertex", "fragment")},
            "serialized_state_categories": {field: classify_state_value(row["m_State"].get(field), enum)
                                            for field, enum in STATE_FIELDS.items()},
            "unity_variant_selection_verified": False, "draw_completed": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "mesh", "private", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--direct3d", action="store_true")
    args = parser.parse_args()
    report = prepare(args.stage, args.mesh, args.private, direct3d=args.direct3d)
    args.safe.write_text(json.dumps(report, indent=2) + "\n")
