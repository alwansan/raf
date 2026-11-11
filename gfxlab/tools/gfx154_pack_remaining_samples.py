"""Package only the three additional Forward samples into the GFX154 test APK."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from gfxlab.tools.gfx124_batch_pack import files_for_slot

MODELS = ("M01-0", "M04-0", "M05-0")


def pack(shell, assets, evidence, out):
    data = json.loads(evidence.read_text())
    expected = {f'{row["source"]["model"]}-{row["source"]["slot"]}': row["gpu"]["rgba_sha256"]
                for row in data["slots"]}
    tests = [{"id": model, "primary": model} for model in MODELS]
    with ZipFile(shell) as archive:
        names = archive.namelist()
        required = {"AndroidManifest.xml", "classes.dex"}
        if len(names) != len(set(names)) or not required <= set(names) <= required | {"resources.arsc"} or archive.testzip():
            raise ValueError("Unexpected source-free shell")
    files = {}
    for model in MODELS:
        folder = assets / model
        scene = json.loads((folder / "scene.json").read_text())
        if scene.get("source_uv1") is not True:
            raise ValueError(f"Source UV1 missing for {model}")
        if hashlib.sha256((folder / "light.rgba").read_bytes()).hexdigest() != expected[model]:
            raise ValueError(f"GPU reference changed for {model}")
        files.update({f"assets/{model}/{path.name}": path for path in files_for_slot(folder, combined=False)})
    with out.open("xb") as target, shell.open("rb") as source:
        shutil.copyfileobj(source, target)
    with ZipFile(out, "a", ZIP_DEFLATED) as archive:
        archive.writestr("assets/batch.json", json.dumps({"tests": tests}))
        for name, path in files.items():
            archive.write(path, name)
        if archive.testzip():
            raise ValueError("Invalid unsigned package")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("shell", "assets", "evidence", "out"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    pack(args.shell, args.assets, args.evidence, args.out)
