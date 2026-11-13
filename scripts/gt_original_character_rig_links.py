"""Verify ZIP2 character mesh-to-renderer and renderer-to-bone links."""
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.gt_mesh_restoration_priority import CATEGORIES
from scripts.gt_original_mesh_texture_graph import resolve
from scripts.gt_original_material_link_graph import pointer
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_stage_serialized_owners import read_expected


def audit(root, manifest):
    import UnityPy

    known = read_expected(manifest)
    kinds, externals, meshes, renderers = {}, {}, {}, []
    for owner, (_, size, digest) in known.items():
        source = root / owner
        verify(source, size, digest)
        sf = UnityPy.load(str(source)).file
        externals[owner] = [entry.path for entry in sf.externals]
        kinds[owner] = {obj.path_id: obj.type.name for obj in sf.objects.values()
                        if obj.type.name in ("Transform", "RectTransform")}
        for obj in sf.objects.values():
            if obj.type.name == "Mesh":
                tree = obj.read_typetree(check_read=False)
                if CATEGORIES["character_name"].search(tree["m_Name"]):
                    meshes[owner, obj.path_id] = len(tree["m_BindPose"])
            elif obj.type.name == "SkinnedMeshRenderer":
                renderers.append((owner, obj.read_typetree(check_read=False)))

    def target(owner, value):
        file_id, path_id = pointer(value)
        return resolve(owner, file_id, externals)[1], path_id

    counts = Counter()
    used = set()
    for owner, tree in renderers:
        identity = target(owner, tree["m_Mesh"])
        if identity not in meshes:
            continue
        used.add(identity)
        bones = tree["m_Bones"]
        counts["character_skinned_renderers"] += 1
        counts["renderer_bone_counts_match_bind_poses"] += len(bones) == meshes[identity]
        for bone in bones:
            dest, path_id = target(owner, bone)
            counts["renderer_bone_slots"] += 1
            if path_id == 0:
                counts["null_bone_slots"] += 1
            elif kinds.get(dest, {}).get(path_id) in ("Transform", "RectTransform"):
                counts["verified_transform_bone_slots"] += 1
            else:
                counts["unresolved_bone_slots"] += 1
        dest, path_id = target(owner, tree["m_RootBone"])
        if path_id == 0:
            counts["null_root_bones"] += 1
        elif kinds.get(dest, {}).get(path_id) in ("Transform", "RectTransform"):
            counts["verified_root_bone_transforms"] += 1
        else:
            counts["unresolved_root_bones"] += 1
    return {"verified_source_owners": len(known), "character_mesh_name_matches": len(meshes),
            "character_meshes_with_bind_poses": sum(bool(n) for n in meshes.values()),
            "distinct_character_meshes_linked_by_skinned_renderers": len(used),
            "all_source_skinned_renderers": len(renderers), **counts,
            "export_or_animation_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.source, args.manifest), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
