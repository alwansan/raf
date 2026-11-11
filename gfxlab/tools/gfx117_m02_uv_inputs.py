"""Stage source-indexed UV0 and exact TexEnv transforms for M02."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.original_model_probe import stage_originals

ROLES = ("basecolor", "normal", "metallic")
VERTICES = 1666
LOD = (0, 4)


def export(stage, assets):
    entries, types, _ = all_model_entries(stage)
    model, = [e for e in entries if e["id"] == "M02"]
    material, = model["materials"]
    textures = material["textures"]
    if set(textures) != set(ROLES):
        raise ValueError("M02 texture roles changed")
    st = []
    for role in ROLES:
        ref = textures[role]
        tex = types[ref["owner"]][ref["pid"]].read_typetree(check_read=False)
        settings = tex["m_TextureSettings"]
        if (settings["m_FilterMode"], settings["m_Aniso"], settings["m_WrapU"],
                settings["m_WrapV"], tex["m_ColorSpace"]) != (1, 1, 0, 0, int(role != "normal")):
            raise ValueError("M02 texture sampler state changed")
        st.extend((*ref["uv_scale"], *ref["uv_offset"]))
    mesh = direct_mesh_handler(types[model["owner"]][model["mesh_pid"]])
    uv = mesh.m_UV0
    if len(uv) != VERTICES or any(len(v) != 2 for v in uv):
        raise ValueError("Expected original two-component UV0 for all M02 vertices")
    values = st + [c for point in uv for c in point]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Invalid source UV")
    raw = struct.pack(f"<{len(values)}f", *values)
    (assets / "uv117.bin").write_bytes(raw)
    return {"experiment":"GFX117","uv_vertices":len(uv),"roles":list(ROLES),
            "uv_sha256":hashlib.sha256(raw).hexdigest(),"sample_mips":list(LOD),
            "texture_filter":"bilinear within explicit mip","wrap":"repeat",
            "original_shader_restored":False,"phase_closed":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2","stage","assets","safe"):
        parser.add_argument("--"+name,type=Path,required=True)
    args = parser.parse_args()
    report = export(stage_originals(args.zip2,args.stage),args.assets)
    args.safe.write_text(json.dumps(report,indent=2)+"\n")
