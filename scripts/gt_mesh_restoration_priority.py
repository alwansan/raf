"""Census original Mesh geometry and rig layout for the ZIP2 restoration queue."""
import argparse
from collections import Counter
import gc
import json
from pathlib import Path
import re

from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_stage_serialized_owners import OWNERS, read_expected


# Names are used only to tag likely content categories, never as asset identity.
CATEGORIES = {
    "character_name": re.compile(r"player|character|maya|rouhi|tala|johnny|elaine|shogo|bruno", re.I),
    "wood_name": re.compile(r"wood|plank|log(?:_|$)|timber", re.I),
    "island_name": re.compile(r"island|terrain|caravan|balboa|tangaroa|utopia|varuna|temperance", re.I),
}


def mesh_metrics(tree):
    data = tree["m_VertexData"]
    compressed = tree["m_CompressedMesh"]["m_Vertices"]["m_NumItems"]
    if compressed % 3:
        raise ValueError("invalid_compressed_position_count")
    vertices = compressed // 3 if compressed else data["m_VertexCount"]
    stream = tree.get("m_StreamData") or {}
    stream_size = stream.get("size", 0)
    submeshes = tree["m_SubMeshes"]
    bones = len(tree["m_BindPose"])
    indices = sum(sub["indexCount"] for sub in submeshes)
    if min(vertices, indices, stream_size) < 0:
        raise ValueError("invalid_original_mesh_dimensions")
    name = tree["m_Name"]
    tags = [key for key, pattern in CATEGORIES.items() if pattern.search(name)]
    if vertices >= 10000:
        tags.append("at_least_10000_vertices")
    if bones:
        tags.append("bind_pose_present")
    if stream_size:
        tags.append("streamed")
    if compressed:
        tags.append("compressed_positions")
    if not vertices:
        tags.append("zero_original_vertex_count")
    return vertices, indices, bones, stream_size, tags


def audit(root, manifest, selected, private_queue=None):
    import UnityPy

    known = read_expected(manifest)
    owners = tuple(selected) if selected else OWNERS
    if len(owners) != len(set(owners)) or set(owners) - known.keys():
        raise ValueError("invalid_owner_selection")
    counts, cohorts = Counter(), {name: Counter() for name in CATEGORIES}
    queue = []
    for owner in owners:
        _, size, digest = known[owner]
        source = root / owner
        verify(source, size, digest)
        environment = UnityPy.load(str(source))
        for obj in environment.file.objects.values():
            if obj.type.name != "Mesh":
                continue
            vertices, indices, bones, stream_size, tags = mesh_metrics(obj.read_typetree(check_read=False))
            counts.update({"source_meshes": 1, "source_vertices": vertices, "source_indices": indices})
            counts.update(tags)
            for tag in set(tags) & cohorts.keys():
                cohorts[tag].update({"meshes": 1, "vertices": vertices, "indices": indices,
                                     "streamed": int(stream_size > 0),
                                     "with_bind_pose": int(bones > 0),
                                     "at_least_10000_vertices": int(vertices >= 10000)})
            if tags:
                queue.append({"owner": owner, "path_id": obj.path_id, "tags": tags,
                              "vertices": vertices, "indices": indices, "bind_pose_count": bones})
        del environment
        gc.collect()
    if not counts["source_meshes"]:
        raise ValueError("no_source_meshes")
    if private_queue is not None:
        with private_queue.open("x", encoding="utf-8") as output:
            json.dump(sorted(queue, key=lambda row: (-row["vertices"], row["owner"], row["path_id"])), output)
    return {"schema": "GT_ORIGINAL_MESH_RESTORATION_PRIORITY_V1",
            "source_owner_count": len(owners), "full_owner_scope": set(owners) == set(OWNERS),
            "counts": dict(counts), "name_hint_cohorts": cohorts,
            "name_hint_cohorts_can_overlap": True,
            "project_export_or_rig_parity_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--owner", action="append")
    parser.add_argument("--private-queue", type=Path)
    args = parser.parse_args()
    if any(path.resolve().is_relative_to(args.source.resolve())
           for path in (args.report, args.private_queue) if path is not None):
        raise ValueError("output_inside_source")
    result = audit(args.source, args.manifest, args.owner, args.private_queue)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_MESH_RESTORATION_PRIORITY " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
