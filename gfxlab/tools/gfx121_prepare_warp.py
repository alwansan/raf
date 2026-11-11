"""Prepare the private Windows fixture from the same source and material as GFX120."""
import argparse
import json
from pathlib import Path

from gfxlab.tools.gfx119_prepare_draw import prepare
from gfxlab.tools.gfx121_forward_fixture_values import engine_values, pack_buffer
from gfxlab.tools.original_model_probe import stage_originals


def stage_draw(source, draw):
    prepare(source,draw,direct3d=True)
    return finalize_draw(draw)


def finalize_draw(draw, *, additive=False, camera_mesh=None, deferred=False):
    mesh = (draw/"mesh.bin").read_bytes() if camera_mesh is None else camera_mesh
    engine = engine_values(mesh,direct3d=True)
    verified_textures = {"_MainTex":0,"_MetallicGlossMap":1,"_BumpMap":2,"_OcclusionMap":3,
                         "unity_SpecCube0":4,"unity_SpecCube1":5,"unity_ProbeVolumeSH":6}
    if additive:
        verified_textures = {"_MainTex":0,"_MetallicGlossMap":1,"_BumpMap":2,"unity_ProbeVolumeSH":3}
    if deferred:
        verified_textures = {"_MainTex":0,"_MetallicGlossMap":1,"_BumpMap":2,"_OcclusionMap":3}
    for stage in ("vertex","fragment"):
        contract = json.loads((draw/(stage+".json")).read_text())
        groups = {g["name"]:g for g in contract["groups"]}
        textures = {r["name"]:r["index"] for r in contract["bindings"] if r["type"]==0}
        if textures != (verified_textures if stage=="fragment" else {}):
            raise ValueError("Original texture register layout changed")
        slots = {r["index"]:r["name"] for r in contract["bindings"] if r["type"]==1}
        if (additive or deferred) and stage == "fragment":
            samplers = {r["name"]:r["extra"] for r in contract["bindings"] if r["type"]==0}
            expected_samplers = ({"_MainTex":0,"_MetallicGlossMap":2,"_BumpMap":1,"_OcclusionMap":3}
                                 if deferred else {"_MainTex":1,"_MetallicGlossMap":3,"_BumpMap":2,"unity_ProbeVolumeSH":0})
            if samplers != expected_samplers:
                raise ValueError("Original sampler slots changed")
        slot_count = (5 if stage == "vertex" else 3) if additive else 4
        if deferred and stage == "fragment":
            slot_count = 1
        if set(slots) != set(range(slot_count)):
            raise ValueError("Original buffer slots changed")
        for slot, group in slots.items():
            source = (draw/f"{stage}-{slot}.bin").read_bytes()
            mask = (draw/f"{stage}-{slot}.mask").read_bytes()
            for mode in ("light","dark"):
                data,_ = pack_buffer(source,mask,groups[group],engine,mode=="light")
                if len(data) != contract["sizes"][str(slot)]*16:
                    raise ValueError("Original buffer layout changed")
                (draw/f"{stage}-{mode}-{slot}.bin").write_bytes(data)
    return draw


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for name in ("zip2","stage","draw"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args()
    stage_draw(stage_originals(args.zip2,args.stage),args.draw)
