"""Private Unity reference inputs using original GFX111 packed curves."""
import argparse
import json
from pathlib import Path

from gfxlab.tools.gfx109_gpu_skin_payload import write_case
from gfxlab.tools.gfx111_m02_clip_pose import run
from gfxlab.tools.original_model_probe import stage_originals


def main():
    parser = argparse.ArgumentParser()
    for key in ("zip2", "stage", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
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

    run(stage_originals(args.zip2, args.stage), pose, clip)
    (args.output / "clips.json").write_text(json.dumps({"clips": cases}, allow_nan=False))


if __name__ == "__main__":
    main()
