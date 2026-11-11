"""Private exact M02 texture mip transport from the pinned ZIP2 Git tree."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from gfxlab.tools.multi_model_transport import STREAMS, all_model_entries
from gfxlab.tools.original_model_probe import ZIP2_SHA, read_manifest, stage_originals


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def read_span(repo, name, offset, size, manifest, cached):
    if name not in STREAMS or type(offset) is not int or offset < 0:
        raise ValueError("Unexpected source texture stream")
    row = manifest["Raft_Data/" + name]
    total = int(row["bytes"])
    if row["kind"] != "split" or not 0 < size <= 8 * 1024 * 1024 or offset + size > total:
        raise ValueError("Invalid stream range")
    prefix = f"Raft/Raft_Data/{name}"
    readme = git(repo, "show", f"{ZIP2_SHA}:{prefix}/README.txt").decode()
    match = re.search(r"^Chunk size: at most 45 MiB \(47,185,920 bytes\)$", readme, re.M)
    if not match or row["sha256"] not in readme or f"Original size (bytes): {total}" not in readme:
        raise ValueError("Source split layout changed")
    width = 45 * 1024 * 1024
    paths = git(repo, "ls-tree", "-r", "--name-only", ZIP2_SHA, "--", prefix).decode().splitlines()
    expected = [f"{prefix}/part-{i:05d}" for i in range((total + width - 1) // width)]
    if sorted(paths) != sorted([f"{prefix}/README.txt", *expected]):
        raise ValueError("Source chunks do not match split layout")
    result = bytearray()
    for i in range(offset // width, (offset + size - 1) // width + 1):
        path = expected[i]
        if path not in cached:
            oid = git(repo, "rev-parse", f"{ZIP2_SHA}:{path}").decode().strip()
            data = git(repo, "cat-file", "blob", oid)
            actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
            if actual != oid or len(data) != min(width, total - i * width):
                raise ValueError("Source Git blob identity mismatch")
            cached[path] = data
        data = cached[path]
        result.extend(data[max(0, offset - i * width):min(len(data), offset + size - i * width)])
    if len(result) != size:
        raise ValueError("Truncated source texture")
    return bytes(result)


def mip_layout(width, height, count, *, block_bytes=16):
    start = 0
    rows = []
    if width <= 0 or height <= 0 or count != max(width,height).bit_length():
        raise ValueError("Expected a complete mip chain")
    for level in range(count):
        w, h = max(1,width>>level), max(1,height>>level)
        size = ((w+3)//4)*((h+3)//4)*block_bytes
        rows.append((level,w,h,start,size))
        start += size
    return rows


def export(repo, stage, out):
    if git(repo,"rev-parse","HEAD").decode().strip() != ZIP2_SHA:
        raise ValueError("Source checkout SHA mismatch")
    manifest = read_manifest(repo)
    entries, types, _ = all_model_entries(stage)
    model, = [e for e in entries if e["id"] == "M02"]
    material, = model["materials"]
    if set(material["textures"]) != {"basecolor","normal","metallic"}:
        raise ValueError("Source M02 material texture roles changed")
    out.mkdir(parents=True, exist_ok=False)
    report = {}
    cached = {}
    for role, ref in sorted(material["textures"].items()):
        tex = types[ref["owner"]][ref["pid"]].read_typetree(check_read=False)
        if tex["m_TextureFormat"] != 12 or tex["m_Width"] != 1024 or tex["m_Height"] != 1024:
            raise ValueError("Expected pinned DXT5 M02 texture")
        stream = tex["m_StreamData"]
        name = PurePosixPath(stream["path"].replace("\\","/")).name
        levels = mip_layout(tex["m_Width"],tex["m_Height"],tex["m_MipCount"])
        if stream["size"] != sum(row[4] for row in levels):
            raise ValueError("Source stream span does not match BC3 block layout")
        data = read_span(repo,name,stream["offset"],stream["size"],manifest,cached)
        (out/(role+".bc3")).write_bytes(data)
        report[role] = {
            "format":"BC3", "compressed_bytes":len(data), "source_color_space_code":tex["m_ColorSpace"],
            "mips":[{"level":i,"width":w,"height":h,"bytes":size,
                     "sha256":hashlib.sha256(data[start:start+size]).hexdigest()}
                    for i,w,h,start,size in levels],
        }
    return {"experiment":"GFX116","source_sha":ZIP2_SHA,"model":"M02","textures":report,
            "verified_source_chunks":len(cached),"android_texture_sampling_verified":False,
            "phase_closed":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2","stage","private","safe"):
        parser.add_argument("--"+name,type=Path,required=True)
    args = parser.parse_args()
    report = export(args.zip2,stage_originals(args.zip2,args.stage),args.private)
    args.safe.write_text(json.dumps(report,indent=2)+"\n")
