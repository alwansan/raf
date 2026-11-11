"""Assemble and audit the private targeted M03-1 Cull diagnostic."""
import argparse
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from gfxlab.tools.gfx120_owner_zip_audit import audit_capture, sha

SOURCE_APK = "3a4c7fa7f3593325755b32c0f6c5ad941097936b53808666388a4743b5db3773"
SLOT = "assets/M03-1/"
HASHES = {
    "off": "c6d786e908500674d64c3220bf4e26b98253302a88ba390a67b00b570877da78",
    "back": "3664e3146c10a225dafd9bf490454ea29a94d9e3dbe6d7bb9a4171dfe7ccc4e6",
    "front": "d28270e7ae29647374d3e5d52fa9eb0d4a1a3e2e55bad2feaf7d6537907bd0b5",
}
BATCH = {"tests": [{"id": "M03-1", "primary": "M03-1"}]}


def pack(shell, source, references, output):
    if sha(source.read_bytes()) != SOURCE_APK:
        raise ValueError("Original diagnostic APK identity differs")
    with ZipFile(source) as apk, ZipFile(shell) as base:
        required = {"AndroidManifest.xml", "classes.dex"}
        names = set(base.namelist())
        if not required <= names <= required | {"resources.arsc"} or len(names) != len(base.namelist()) or base.testzip():
            raise ValueError("Unexpected source-free APK shell")
        scene = json.loads(apk.read(SLOT + "scene.json"))
        names = ["scene.json", "mesh.bin", "indices.bin", "probe.vert", "probe.frag",
                 "basecolor.rgba", "normal.rgba", "metallic.rgba"]
        names += [row[key] for row in scene["blocks"] for key in ("light", "dark")]
        entries = {SLOT + name: apk.read(SLOT + name) for name in names}
        if len(entries) != 24:
            raise ValueError("Unexpected source slot assets")
        for mode, digest in HASHES.items():
            raw = (references / (mode + ".rgba")).read_bytes()
            if sha(raw) != digest:
                raise ValueError("Mesa reference identity changed")
            entries[SLOT + "cull-" + mode + ".rgba"] = raw
        if entries[SLOT + "cull-off.rgba"] != apk.read(SLOT + "light.rgba"):
            raise ValueError("Off reference differs from prior batch")
    with output.open("xb") as target, shell.open("rb") as base:
        shutil.copyfileobj(base, target)
    with ZipFile(output, "a", ZIP_DEFLATED) as target:
        target.writestr("assets/batch.json", json.dumps(BATCH))
        for name, raw in entries.items():
            target.writestr(name, raw)
        if target.testzip():
            raise ValueError("Corrupt assembled APK")


def audit(log_path, apk_path):
    with ZipFile(log_path) as logs, ZipFile(apk_path) as apk:
        files = logs.infolist()
        names = {entry.filename for entry in files}
        if len(files) != len(names) or any(entry.file_size > 512*1024 for entry in files):
            raise ValueError("Unexpected Cull ZIP")
        summary = json.loads(logs.read("summary.json"))
        if summary.get("experiment") != "GFX148":
            raise ValueError("Wrong Cull experiment")
        test, = summary["tests"]
        if test["id"] != "M03-1" or not test["draw_completed"]:
            raise ValueError(f"Cull test did not complete: {test.get('error')}")
        if [capture["cull_mode"] for capture in test["captures"]] != list(HASHES):
            raise ValueError("Missing or reordered Cull modes")
        if names != {"summary.json", *(f"M03-1-{mode}.png" for mode in HASHES)}:
            raise ValueError("Unexpected Cull capture entries")
        results = {}
        for row in test["captures"]:
            mode = row["cull_mode"]
            name = f"M03-1-{mode}.png"
            reference = apk.read(SLOT + "cull-" + mode + ".rgba")
            if sha(reference) != HASHES[mode] or row["name"] != name.removesuffix(".png"):
                raise ValueError("Wrong same-mode Mesa reference or capture")
            rgba, safe = audit_capture(row, name, logs.read(name), reference)
            safe["rgb_error_above10_pixels"] = sum(
                max(abs(a-b) for a,b in zip(rgba[i:i+3], reference[i:i+3])) > 10
                for i in range(0, len(rgba), 4) if rgba[i+3] == reference[i+3] == 255)
            results[mode] = safe
    return {"experiment": "GFX148", "renderer": summary["renderer"], "gles": summary["gles"],
            "matching_cull_modes": results, "unity_effective_cull_verified": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("pack")
    for field in ("shell", "source", "references", "output"):
        build.add_argument(field, type=Path)
    check = commands.add_parser("audit")
    for field in ("logs", "apk"):
        check.add_argument(field, type=Path)
    args = parser.parse_args()
    if args.command == "pack":
        pack(args.shell, args.source, args.references, args.output)
    else:
        print(json.dumps(audit(args.logs, args.apk), indent=2))
