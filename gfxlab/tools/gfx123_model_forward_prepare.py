"""Prepare private source-pinned Forward fixtures for the selected models."""
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


MODEL_IDS = tuple(f"M{i:02d}" for i in range(6))


def source_keys(stage, selection):
    envs, _, owner, renderer = select_exact_renderer(stage)
    externals = [x.path for x in envs[owner].file.externals]
    simple = resolve_pptr(renderer["m_Materials"][0], owner, externals)[1]
    models = {label: [(m["owner"], m["material_pid"]) for m in model["materials"]]
              for label, model in zip(MODEL_IDS[1:], selection["selected"], strict=True)}
    return {"M00": [simple], **models}


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


def prepare(repo, stage, out, *, direct3d=False, models=("M00", "M03")):
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
        if label not in models:
            continue
        mesh = direct_mesh_handler(types[entry["owner"]][entry["mesh_pid"]])
        packed = b"".join(struct.pack("<12f", *position, *normal, *tangent, *uv)
                          for position, normal, tangent, uv in zip(
                              mesh.m_Vertices, mesh.m_Normals, mesh.m_Tangents, mesh.m_UV0, strict=True))
        uv1 = mesh.m_UV1
        if uv1 and (len(uv1) != len(mesh.m_Vertices) or any(len(uv) != 2 for uv in uv1)):
            raise ValueError("Unsupported original UV1 stream shape")
        for slot, (submesh, triangles, material, key) in enumerate(zip(
                mesh.src.m_SubMeshes, mesh.get_triangles(), entry["materials"], keys[label], strict=True)):
            folder = out / f"{label}-{slot}"
            source = types[key[0]][key[1]]
            refs = material["textures"]
            expected = {role: (ref["owner"], ref["pid"]) for role, ref in refs.items()}
            source_data = (source.read_typetree(check_read=False), key[0],
                           [external.path for external in source.assets_file.externals], expected)
            report = audit(stage, not direct3d, fixture_consumer(folder, direct3d=direct3d), model=label,
                           material_source=source_data, shader_source=shader)
            (folder / "mesh.bin").write_bytes(packed)
            if uv1:
                (folder / "uv1.bin").write_bytes(b"".join(struct.pack("<2f", *uv) for uv in uv1))
            indices = [i + (submesh.baseVertex or 0) for face in triangles for i in face]
            if len(indices) != submesh.indexCount or not 0 <= min(indices) <= max(indices) < len(packed)//48:
                raise ValueError("Invalid original triangle submesh")
            (folder / "indices.bin").write_bytes(struct.pack(f"<{len(indices)}H", *indices))
            textures = {role: prepare_texture(repo, ref, types, manifest, cache, folder / f"{role}.rgba")
                        for role, ref in refs.items()}
            (folder / "textures.json").write_text(json.dumps(textures, indent=2))
            if direct3d:
                from gfxlab.tools.gfx121_prepare_warp import finalize_draw
                finalize_draw(folder)
                (folder / "textures.bin").write_bytes(b"".join(
                    struct.pack("<4I", row["width"], row["height"], row["levels"], row["source_color_space"])
                    for row in (textures[role] for role in ("basecolor", "metallic", "normal"))))
            rows.append({"model": label, "slot": slot, "triangles": len(triangles),
                         "vertices": len(packed)//48, "source_uv1_vertices": len(uv1 or []), "gles_offline_link_passed": report["gles_offline_link_passed"],
                         "textures": textures, "stages": report["stages"]})
    if {row["model"] for row in rows} != set(models):
        raise ValueError("Requested models are missing from the source batch")
    return {"experiment": "GFX123", "source_sha": ZIP2_SHA, "slots": rows, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2", "stage", "private", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--direct3d", action="store_true")
    parser.add_argument("--models", nargs="+", choices=MODEL_IDS, default=("M00", "M03"))
    args = parser.parse_args()
    result = prepare(args.zip2, args.stage, args.private, direct3d=args.direct3d, models=args.models)
    args.safe.write_text(json.dumps(result, indent=2) + "\n")
