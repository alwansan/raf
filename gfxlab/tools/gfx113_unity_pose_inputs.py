"""Private Unity reference inputs using original GFX111 packed curves."""
import argparse
import json
import struct
from pathlib import Path

from gfxlab.tools.gfx109_gpu_skin_payload import write_case
from gfxlab.tools.gfx111_m02_clip_pose import run
from gfxlab.tools.original_model_probe import stage_originals


def main():
    parser = argparse.ArgumentParser()
    for key in ("zip2", "stage", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--native-bake", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cases = []

    def pose(clip, sample, time, positions, weights, world, bindposes, reference):
        write_case(args.output / f"C{clip}P{sample}.bin", positions, weights, world, bindposes, reference)
        if sample == 0:
            cases[clip]["bindposes"] = [{"values": p} for p in bindposes]

    def clip(index, graph, bones, parent_of, curves, constants, bindings, start, stop):
        nodes = {}

        def visit(key):
            if key is None:
                return -1
            if key not in nodes:
                data = graph.data(key)
                parent = visit(parent_of(key, data))
                nodes[key] = (len(nodes), {"parent": parent,
                    "position": data["m_LocalPosition"], "rotation": data["m_LocalRotation"],
                    "scale": data["m_LocalScale"]})
            return nodes[key][0]

        bone_indices = [visit(key) for key in bones]
        field_ids = {"m_LocalPosition": 0, "m_LocalRotation": 1, "m_LocalScale": 2}
        binding_rows = [{"node": visit(node), "field": field_ids[field], "width": len(axes)}
                        for node, field, axes in bindings]
        cases.append({"start": start, "stop": stop, "nodes": [row for _, row in nodes.values()],
                      "bones": bone_indices, "bindings": binding_rows, "constants": constants,
                      "curves": [{"keys": [{"time": t, "coeff": c} for t, c in curve]}
                                 for curve in curves]})

    stage = stage_originals(args.zip2, args.stage)
    run(stage, pose, clip)
    if args.native_bake:
        from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
        from gfxlab.tools.multi_model_transport import all_model_entries

        entries, types, _ = all_model_entries(stage)
        model, = [entry for entry in entries if entry["id"] == "M02"]
        mesh = direct_mesh_handler(types[model["owner"]][model["mesh_pid"]])
        indices = [i + getattr(submesh, "baseVertex", 0)
                   for submesh, triangles in zip(mesh.src.m_SubMeshes, mesh.get_triangles(), strict=True)
                   for triangle in triangles for i in triangle]
        if len(indices) != 2388 * 3 or min(indices) < 0 or max(indices) >= 1666:
            raise ValueError("Unexpected M02 index range")
        (args.output / "indices.bin").write_bytes(struct.pack(f"<{len(indices)}H", *indices))
    (args.output / "clips.json").write_text(json.dumps({"clips": cases}, allow_nan=False))


if __name__ == "__main__":
    main()
