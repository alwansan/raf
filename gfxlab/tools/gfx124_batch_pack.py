"""Assemble validated private Forward cases into the GFX124 unsigned shell."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED


CONTROLS = ("light", "dark", "flat", "nonmetal")
ROLES = ("basecolor", "normal", "metallic")
SLOTS = ("M00-0", "M02-0", "M03-0", "M03-1")
REFERENCE_SIZE = 256 * 256 * 4


def check_digest(path, expected):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Reference identity mismatch: {path.parent.name}/{path.name}")


def files_for_slot(folder, *, combined):
    scene = json.loads((folder / "scene.json").read_text())
    files = {"scene.json", "probe.vert", "probe.frag", "mesh.bin", "indices.bin"}
    files.update(f"{name}.rgba" for name in (*ROLES, *CONTROLS))
    for index, row in enumerate(scene["blocks"]):
        for mode in ("light", "dark"):
            name = f"{mode}-{index}.bin"
            if row[mode] != name or (folder / name).stat().st_size != row["bytes"]:
                raise ValueError("Wrong uniform buffer layout")
            files.add(name)
    if len(scene["blocks"]) != 8 or len(scene["samplers"]) != 7:
        raise ValueError("Unexpected source binding count")
    if combined:
        files.add("combined.rgba")
    if {path.name for path in folder.iterdir()} != files:
        raise ValueError("Unexpected private slot payload")
    for name in files:
        path = folder / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Invalid private slot file")
    for role in ROLES:
        layout = scene.get("textures", {}).get(role, {"width": 1024, "height": 1024, "levels": 11})
        w, h, levels = layout["width"], layout["height"], layout["levels"]
        if not 1 <= min(w, h) <= max(w, h) <= 2048 or levels != max(w, h).bit_length():
            raise ValueError("Invalid mip metadata")
        expected = sum(max(1, w >> i) * max(1, h >> i) * 4 for i in range(levels))
        if (folder / f"{role}.rgba").stat().st_size != expected:
            raise ValueError("Invalid mip payload size")
    for ref in (*CONTROLS, *(("combined",) if combined else ())):
        if (folder / f"{ref}.rgba").stat().st_size != REFERENCE_SIZE:
            raise ValueError("Invalid Mesa reference size")
    return [folder / name for name in sorted(files)]


def inject(shell, m02, models, evidence, out):
    report = json.loads(evidence.read_text())
    hashes = {"M02-0": report["m02_regression_rgba_sha256"]}
    for row in report["slots"]:
        hashes[f'{row["model"]}-{row["slot"]}'] = row["mesa_draw"]["rgba_sha256"]
        if row["model"] == "M03" and row["slot"] == 0:
            check_digest(models / "M03-0" / "combined.rgba",
                         row["mesa_draw"]["two_slots_shared_depth_draw"]["rgba_sha256"])
    tests = [{"id": slot, "primary": slot} for slot in SLOTS]
    tests.append({"id": "M03-combined", "primary": "M03-0", "secondary": "M03-1"})
    entries = {}
    for slot in SLOTS:
        folder = m02 if slot == "M02-0" else models / slot
        check_digest(folder / "light.rgba", hashes[slot])
        entries.update({f"assets/{slot}/{path.name}": path
                        for path in files_for_slot(folder, combined=slot == "M03-0")})
    with ZipFile(shell) as archive:
        names = archive.namelist()
        if (archive.testzip() or len(names) != len(set(names)) or
                not {"AndroidManifest.xml", "classes.dex"} <= set(names) or
                any(name.startswith(("assets/", "META-INF/")) for name in names)):
            raise ValueError("Expected unsigned source-free APK shell")
    try:
        with out.open("xb") as target:
            with shell.open("rb") as source:
                shutil.copyfileobj(source, target)
        with ZipFile(out, "a", compression=ZIP_DEFLATED) as archive:
            archive.writestr("assets/batch.json", json.dumps({"tests": tests}))
            for name, path in entries.items():
                archive.write(path, name)
            if archive.testzip():
                raise ValueError("Corrupt private batch APK")
    except FileExistsError:
        raise
    except Exception:
        out.unlink(missing_ok=True)
        raise
    return {"tests": len(tests), "expected_captures": len(SLOTS) * len(CONTROLS) + 1,
            "fixture_entries": len(entries) + 1, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("shell", "m02", "models", "evidence", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inject(args.shell, args.m02, args.models, args.evidence, args.out)))
