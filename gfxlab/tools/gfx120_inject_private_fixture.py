"""Append authenticated local fixture assets to the source-free GFX120 APK shell."""
import argparse
import hashlib
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def inject(shell, assets, out, mesa_hash):
    expected = {"scene.json","probe.vert","probe.frag","mesh.bin","indices.bin",
                *(role+".rgba" for role in ("basecolor","normal","metallic","light","dark","flat","nonmetal")),
                *(f"{mode}-{i}.bin" for mode in ("light","dark") for i in range(8))}
    files = {p.name:p for p in assets.iterdir()}
    if files.keys() != expected or any(not p.is_file() or p.is_symlink() for p in files.values()):
        raise ValueError("Unexpected private Forward fixture")
    if hashlib.sha256(files["light.rgba"].read_bytes()).hexdigest() != mesa_hash:
        raise ValueError("Mesa reference identity changed")
    with ZipFile(shell) as z:
        names = z.namelist()
        if (z.testzip() is not None or len(names) != len(set(names))
                or not {"AndroidManifest.xml","classes.dex"} <= set(names)
                or any(n.startswith(("assets/","META-INF/")) for n in names)):
            raise ValueError("Expected a source-free unsigned shell")
    with out.open("xb") as target, shell.open("rb") as source:
        shutil.copyfileobj(source,target)
    # Append only. Preserve original entries and their alignment.
    with ZipFile(out,"a",compression=ZIP_DEFLATED) as z:
        for name,p in sorted(files.items()):
            z.write(p,"assets/"+name)
        if z.testzip() is not None:
            raise ValueError("Corrupt unsigned private APK")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    for name in ("shell","assets","out"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--mesa-hash",required=True)
    a=parser.parse_args()
    inject(a.shell,a.assets,a.out,a.mesa_hash)
