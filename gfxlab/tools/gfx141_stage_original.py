"""GFX141: stage pinned original Shader48 and private Mesa reference fixtures.

Intentionally generates only files under --private on the CI runner.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.gfx119_prepare_draw import prepare as prepare_m02
from gfxlab.tools.gfx123_model_forward_prepare import prepare as prepare_models
from gfxlab.tools.gfx116_m02_bc3_source import export as extract_mips
from gfxlab.tools.gfx116_bc3_sampling_pack import pack as pack_mips
from gfxlab.tools.gfx127_prepare_forward_add import prepare as prepare_add
from gfxlab.tools.gfx129_stage_animated_forward import prepare as prepare_animation
from gfxlab.tools.gfx131_prepare_shadow import prepare as prepare_shadow
from gfxlab.tools.gfx134_prepare_deferred import prepare as prepare_deferred


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def stage(zip2, work):
    actual = subprocess.check_output(["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True).strip()
    if actual != ZIP2_SHA:
        raise ValueError("ZIP2 source revision changed")
    work.mkdir(parents=True, exist_ok=False)
    stage_originals(zip2, work / "source")
    source = work / "source/Raft_Data"
    forward = work / "m02-source"
    prepare_m02(source, forward)
    models = prepare_models(zip2, source, work / "model-source")
    mips = extract_mips(zip2, source, work / "bc3")
    write(work / "mip-stage.json", mips)
    write(work / "model-stage.json", models)
    pack_mips(work / "bc3", work / "mip-stage.json", work / "textures")
    prepare_add(source, forward, work / "add-source")
    animations = prepare_animation(source, forward / "mesh.bin", work / "animation-source")
    write(work / "animation-stage.json", animations)
    prepare_shadow(source, forward / "mesh.bin", work / "shadow-source")
    prepare_deferred(source, forward, work / "deferred-source")
    script = [os.environ.get("PYTHON", "python3"), "-m", "gfxlab.tools.gfx119_mesa_forward_draw"]

    def mesa(*args):
        subprocess.run(script + [str(arg) for arg in args], check=True)

    mesa("--private", forward, "--textures", work / "textures",
         "--safe", work / "m02-mesa.json", "--portable", work / "M02-0",
         "--forward-add", work / "add-source",
         "--forward-add-portable", work / "M02-0-add",
         "--animation", work / "animation-source",
         "--animation-portable", work / "M02-0-anim",
         "--shadow", work / "shadow-source",
         "--shadow-portable", work / "M02-0-shadow",
         "--deferred", work / "deferred-source",
         "--deferred-portable", work / "M02-0-deferred")

    for slot in ("M00-0", "M03-0", "M03-1"):
        args = ["--private", work / "model-source" / slot,
                "--textures", work / "model-source" / slot,
                "--safe", work / (slot + "-mesa.json"),
                "--portable", work / "models" / slot]
        if slot == "M03-0":
            args.extend(["--second-slot", work / "model-source/M03-1"])
        mesa(*args)
    print("GFX141: all source-original Mesa fixtures staged in private runner temp")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip2", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    stage(args.zip2, args.private)
