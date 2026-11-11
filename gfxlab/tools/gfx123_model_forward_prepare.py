"""Prepare the private M00 and M03 controlled Forward fixtures."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
from gfxlab.tools.gfx116_bc3_sampling_pack import decode_mip
from gfxlab.tools.gfx116_m02_bc3_source import git, mip_layout, read_span
from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.gfx119_prepare_draw import fixture_consumer
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.original_model_probe import ZIP2_SHA, read_manifest
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.shears_texture_readiness import select_exact_renderer


def source_keys(stage, selection):
    envs, _, owner, renderer = select_exact_renderer(stage)
    externals = [x.path for x in envs[owner].file.externals]
    simple = resolve_pptr(renderer["m_Materials"][0], owner, externals)[1]
    multi = selection["selected"][2]
    return {"M00": [simple], "M03": [(m["owner"], m["material_pid"]) for m in multi["materials"]]}


def prepare_texture(repo, ref, types, manifest, cache, out):
    tex = types[ref["owner"]][ref["pid"]].read_typetree(check_read=False)
    fourcc, block_bytes = {10: (b"DXT1", 8), 12: (b"DXT5", 16)}[tex["m_TextureFormat"]]
    width, height, count = tex["m_Width"], tex["m_Height"], tex["m_MipCount"]
    if not 1 <= min(width, height) <= max(width, height) <= 2048:
        raise ValueError("Unsupported source texture dimensions")
    stream = tex["m_StreamData"]
    name = PurePosixPath(stream["path"].replace("\\", "/")).name
    mips = mip_layout(width, height, count, block_bytes=block_bytes)
    if stream["size"] != sum(row[4] for row in mips):
        raise ValueError("Original stream size does not match compressed mip layout")
    data = read_span(repo, name, stream["offset"], stream["size"], manifest, cache)
    with out.open("wb") as image:
        for _, w, h, start, size in mips:
            image.write(decode_mip(data[start:start+size], w, h, fourcc=fourcc))
    return {"width": width, "height": height, "levels": count,
            "source_color_space": tex["m_ColorSpace"], "source_format": fourcc.decode(),
            "source_sha256": hashlib.sha256(data).hexdigest()}


def prepare(repo, stage, out):
    if git(repo, "rev-parse", "HEAD").decode().strip() != ZIP2_SHA:
        raise ValueError("Wrong ZIP2 source revision")
    entries, types, _ = all_model_entries(stage)
    selection, _ = selected_five(stage)
    keys = source_keys(stage, selection)
    manifest, cache = read_manifest(repo), {}
    shader = load_original_shader_private(stage)
    rows = []
    for entry in entries:
        label = entry["id"]
        if label not in keys:
            continue
        mesh = direct_mesh_handler(types[entry["owner"]][entry["mesh_pid"]])
        packed = b"".join(struct.pack("<12f", *position, *normal, *tangent, *uv)
                          for position, normal, tangent, uv in zip(
                              mesh.m_Vertices, mesh.m_Normals, mesh.m_Tangents, mesh.m_UV0, strict=True))
        if mesh.m_UV1:
            raise ValueError("Fixture would discard an original UV1 stream")
        for slot, (submesh, triangles, material, key) in enumerate(zip(
                mesh.src.m_SubMeshes, mesh.get_triangles(), entry["materials"], keys[label], strict=True)):
            folder = out / f"{label}-{slot}"
            source = types[key[0]][key[1]]
            refs = material["textures"]
            expected = {role: (ref["owner"], ref["pid"]) for role, ref in refs.items()}
            source_data = (source.read_typetree(check_read=False), key[0],
                           [external.path for external in source.assets_file.externals], expected)
            report = audit(stage, True, fixture_consumer(folder), model=label,
                           material_source=source_data, shader_source=shader)
            (folder / "mesh.bin").write_bytes(packed)
            indices = [i + (submesh.baseVertex or 0) for face in triangles for i in face]
            if len(indices) != submesh.indexCount or not 0 <= min(indices) <= max(indices) < len(packed)//48:
                raise ValueError("Invalid original triangle submesh")
            (folder / "indices.bin").write_bytes(struct.pack(f"<{len(indices)}H", *indices))
            textures = {role: prepare_texture(repo, ref, types, manifest, cache, folder / f"{role}.rgba")
                        for role, ref in refs.items()}
            (folder / "textures.json").write_text(json.dumps(textures, indent=2))
            rows.append({"model": label, "slot": slot, "triangles": len(triangles),
                         "vertices": len(packed)//48, "gles_offline_link_passed": report["gles_offline_link_passed"],
                         "textures": textures, "stages": report["stages"]})
    return {"experiment": "GFX123", "source_sha": ZIP2_SHA, "slots": rows, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2", "stage", "private", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.zip2, args.stage, args.private)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
