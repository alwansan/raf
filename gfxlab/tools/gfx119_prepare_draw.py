"""Prepare private inputs for the M02 controlled Forward draw."""
import argparse
import json
from pathlib import Path
import shutil
import struct

from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
from gfxlab.tools.gfx118_m02_original_forward import audit
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_dxbc_signature_pairs import signature_from_container


def fixture_consumer(out, *, direct3d=False):
    out.mkdir(parents=True, exist_ok=True)

    def consume(folder, stages):
        if folder is not None:
            for name in ("probe.vert", "probe.frag"):
                shutil.copyfile(folder / name, out / name)
        for name, (dxbc, sizes, payloads, merged) in stages.items():
            if direct3d:
                (out / f"{name}.dxbc").write_bytes(dxbc)
            for slot, (data, mask) in payloads.items():
                (out / f"{name}-{slot}.bin").write_bytes(data)
                (out / f"{name}-{slot}.mask").write_bytes(mask)
            contract = dict(sizes=sizes, bindings=merged["bindings"], groups=merged["groups"])
            if name == "vertex":
                contract["inputs"] = signature_from_container(dxbc, "ISGN")
            (out / f"{name}.json").write_text(json.dumps(contract, default=list))

    return consume


def prepare(stage, out, *, direct3d=False):
    audit(stage, not direct3d, fixture_consumer(out, direct3d=direct3d))
    entries, types, _ = all_model_entries(stage)
    model, = [entry for entry in entries if entry["id"] == "M02"]
    mesh = direct_mesh_handler(types[model["owner"]][model["mesh_pid"]])
    with (out / "mesh.bin").open("wb") as target:
        for position, normal, tangent, uv in zip(
            mesh.m_Vertices, mesh.m_Normals, mesh.m_Tangents, mesh.m_UV0, strict=True
        ):
            target.write(struct.pack("<12f", *position, *normal, *tangent, *uv))
    indices = [index + getattr(submesh, "baseVertex", 0)
               for submesh, triangles in zip(mesh.src.m_SubMeshes, mesh.get_triangles(), strict=True)
               for triangle in triangles for index in triangle]
    if len(indices) != 2388 * 3 or min(indices) < 0 or max(indices) >= 1666:
        raise ValueError("Unexpected original M02 indices")
    (out / "indices.bin").write_bytes(struct.pack(f"<{len(indices)}H", *indices))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--private", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.stage, args.private)
