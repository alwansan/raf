"""Stage the exact M02 directional ForwardAdd pair for a controlled depth/blend test."""
import argparse
import json
from pathlib import Path
import shutil

from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.gfx119_prepare_draw import fixture_consumer
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.multi_sevenpass_state_enum_semantics import STATE_FIELDS, classify_state_value


def prepare(stage, base, out, *, direct3d=False):
    shader = load_original_shader_private(stage)
    passes = shader[0]["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"]
    state, = [p["m_State"] for p in passes if p["m_State"]["m_Name"] == "FORWARD_DELTA"]
    report = audit(stage, not direct3d, fixture_consumer(out, direct3d=direct3d), shader_source=shader, pass_name="FORWARD_DELTA")
    for name in ("mesh.bin", "indices.bin"):
        shutil.copyfile(base / name, out / name)
    if direct3d:
        from gfxlab.tools.gfx121_prepare_warp import finalize_draw
        finalize_draw(out, additive=True)
    return {"experiment": "GFX127", "source_sha": report["source_sha"], "stages": report["stages"],
            "gles_offline_link_passed": report["gles_offline_link_passed"],
            "source_state_categories": {key: classify_state_value(state.get(key), enums)
                                        for key, enums in STATE_FIELDS.items()},
            "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("stage", "base", "private", "safe"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--direct3d", action="store_true")
    args = parser.parse_args()
    result = prepare(args.stage, args.base, args.private, direct3d=args.direct3d)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
