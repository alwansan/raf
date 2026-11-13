"""Verify ZIP2 character mesh-to-renderer and renderer-to-bone links."""
import argparse
from collections import Counter
import json
import math
import struct
from pathlib import Path

from scripts.gt_mesh_restoration_priority import CATEGORIES
from scripts.gt_original_mesh_texture_graph import resolve
from scripts.gt_original_material_link_graph import pointer
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_stage_serialized_owners import read_expected


def streamed_frame_counts(words, curve_count):
    """Validate Unity StreamedClip frame boundaries and curve indices."""
    offset = 0
    frames = keys = sentinels = 0
    previous = -math.inf
    while offset < len(words):
        if len(words) - offset < 2:
            raise ValueError("truncated_original_animation_stream_header")
        time = struct.unpack("<f", struct.pack("<I", words[offset] & 0xffffffff))[0]
        count = words[offset + 1]
        end = offset + 2 + 5 * count
        if count < 0 or end > len(words) or math.isnan(time) or time < previous:
            raise ValueError("invalid_original_animation_stream_frame")
        if not math.isfinite(time):
            if not ((time < 0 and offset == 0) or (time > 0 and end == len(words))):
                raise ValueError("invalid_original_animation_stream_sentinel")
            sentinels += 1
        if any(not 0 <= words[index] < curve_count for index in range(offset + 2, end, 5)):
            raise ValueError("original_animation_stream_curve_out_of_range")
        frames += 1
        keys += count
        previous, offset = time, end
    return {"streamed_frames": frames, "streamed_curve_keys": keys,
            "streamed_sentinel_frames": sentinels}


def audit(root, manifest):
    import UnityPy

    known = read_expected(manifest)
    kinds, externals, meshes, renderers, parents = {}, {}, {}, [], {}
    animators = {}
    transforms = {}
    game_objects_by_transform = {}
    animator_assets = {}
    selected_controllers = set()
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
            elif obj.type.name == "Animator":
                tree = obj.read_typetree(check_read=False)
                file_id, path_id = pointer(tree["m_GameObject"])
                if file_id == 0 and path_id:
                    animators.setdefault((owner, path_id), []).append(tree)
            elif obj.type.name in ("Avatar", "AnimatorController", "AnimatorOverrideController", "AnimationClip"):
                animator_assets[owner, obj.path_id] = obj.type.name
            elif obj.type.name == "SkinnedMeshRenderer":
                renderers.append((owner, obj.read_typetree(check_read=False)))

    def target(owner, value):
        file_id, path_id = pointer(value)
        return resolve(owner, file_id, externals)[1], path_id

    counts = Counter()
    used = set()
    # Decode Transform parent pointers only for owners reachable from candidate rigs.
    def parent(identity):
        owner, path_id = identity
        if owner not in parents:
            sf = UnityPy.load(str(root / owner)).file
            records = {
                obj.path_id: obj.read_typetree(check_read=False)
                for obj in sf.objects.values()
                if obj.type.name in ("Transform", "RectTransform")
            }
            parents[owner] = {pid: tree["m_Father"] for pid, tree in records.items()}
            for pid, tree in records.items():
                game_object = target(owner, tree["m_GameObject"])
                if game_object[0] is not None and game_object[1]:
                    transforms[game_object] = (owner, pid)
                    game_objects_by_transform[owner, pid] = game_object
        value = parents[owner].get(path_id)
        return target(owner, value) if value is not None else (None, 0)

    def ancestry(bone, root_bone):
        seen = set()
        while bone[0] is not None and bone[1]:
            if bone == root_bone:
                return "under_root"
            if bone in seen:
                return "parent_cycle"
            seen.add(bone)
            bone = parent(bone)
        return "outside_root"

    def animator_candidates(owner, start):
        parent((owner, 0))  # Populate the GameObject to Transform index for this owner.
        transform = transforms.get(start, (None, 0))
        seen = set()
        while transform[0] is not None and transform[1] and transform not in seen:
            seen.add(transform)
            if start in animators:
                return start[0], animators[start]
            transform = parent(transform)
            if transform[0] is not None and transform[1]:
                parent(transform)
            start = game_objects_by_transform.get(transform, (None, 0))
        return None, []

    for owner, tree in renderers:
        identity = target(owner, tree["m_Mesh"])
        if identity not in meshes:
            continue
        used.add(identity)
        animator_owner, candidates = animator_candidates(owner, target(owner, tree["m_GameObject"]))
        if len(candidates) == 1:
            counts["renderers_with_unique_ancestor_animator"] += 1
            animator = candidates[0]
            for key, allowed in (
                ("m_Avatar", ("Avatar",)),
                ("m_Controller", ("AnimatorController", "AnimatorOverrideController")),
            ):
                asset = target(animator_owner, animator[key])
                result = ("null" if asset[1] == 0 else "verified"
                          if animator_assets.get(asset) in allowed else "unresolved")
                counts["ancestor_animator_" + key[2:].lower() + "_" + result] += 1
                if key == "m_Controller" and result == "verified":
                    selected_controllers.add(asset)
        elif candidates:
            counts["renderers_with_ambiguous_ancestor_animator"] += 1
        else:
            counts["renderers_without_ancestor_animator"] += 1
        bones = tree["m_Bones"]
        counts["character_skinned_renderers"] += 1
        counts["renderer_bone_counts_match_bind_poses"] += len(bones) == meshes[identity]
        root_bone = target(owner, tree["m_RootBone"])
        rig_ancestry = Counter()
        for bone in bones:
            dest, path_id = target(owner, bone)
            counts["renderer_bone_slots"] += 1
            if path_id == 0:
                counts["null_bone_slots"] += 1
            elif kinds.get(dest, {}).get(path_id) in ("Transform", "RectTransform"):
                counts["verified_transform_bone_slots"] += 1
                rig_ancestry[ancestry((dest, path_id), root_bone)] += 1
            else:
                counts["unresolved_bone_slots"] += 1
        counts.update({"bone_slots_" + key: value for key, value in rig_ancestry.items()})
        counts["renderers_with_all_bones_under_root"] += bool(bones) and rig_ancestry["under_root"] == len(bones)
        dest, path_id = root_bone
        if path_id == 0:
            counts["null_root_bones"] += 1
        elif kinds.get(dest, {}).get(path_id) in ("Transform", "RectTransform"):
            counts["verified_root_bone_transforms"] += 1
        else:
            counts["unresolved_root_bones"] += 1
    pending = set(selected_controllers)
    visited, clips = set(), set()
    while pending:
        identity = pending.pop()
        if identity in visited:
            continue
        visited.add(identity)
        owner, path_id = identity
        obj = UnityPy.load(str(root / owner)).file.objects[path_id]
        tree = obj.read_typetree(check_read=False)
        if obj.type.name == "AnimatorController":
            references = tree["m_AnimationClips"]
        else:
            base = target(owner, tree["m_Controller"])
            if animator_assets.get(base) in ("AnimatorController", "AnimatorOverrideController"):
                pending.add(base)
            else:
                counts["override_unresolved_base_controller"] += 1
            references = [value for pair in tree["m_Clips"]
                          for value in (pair["m_OriginalClip"], pair["m_OverrideClip"])]
        for reference in references:
            clip = target(owner, reference)
            counts["controller_clip_slots"] += 1
            if animator_assets.get(clip) == "AnimationClip":
                clips.add(clip)
                counts["controller_clip_slots_verified"] += 1
            elif clip[1] == 0:
                counts["controller_clip_slots_null"] += 1
            else:
                counts["controller_clip_slots_unresolved"] += 1
    counts["unique_selected_controller_assets"] = len(selected_controllers)
    counts["unique_controllers_checked_including_bases"] = len(visited)
    counts["unique_verified_animation_clips"] = len(clips)
    clip_payloads = Counter()
    durations = []
    for owner in sorted({owner for owner, _ in clips}):
        sf = UnityPy.load(str(root / owner)).file
        for clip_owner, pid in sorted(clips):
            if clip_owner != owner:
                continue
            clip = sf.objects[pid].read_typetree(check_read=False)
            muscle = clip["m_MuscleClip"]
            start, stop = muscle["m_StartTime"], muscle["m_StopTime"]
            sample_rate = clip["m_SampleRate"]
            if not all(math.isfinite(v) for v in (start, stop, sample_rate)) or stop < start or sample_rate <= 0:
                raise ValueError("invalid_original_animation_clip_timing")
            durations.append(stop - start)
            data = muscle["m_Clip"]["data"]
            dense = data["m_DenseClip"]
            samples = dense["m_SampleArray"]
            if (dense["m_FrameCount"] < 0 or dense["m_CurveCount"] < 0 or
                    len(samples) != dense["m_FrameCount"] * dense["m_CurveCount"] or
                    not all(math.isfinite(v) for v in samples)):
                raise ValueError("invalid_original_animation_dense_samples")
            constant = data["m_ConstantClip"]["data"]
            if not all(math.isfinite(v) for v in constant):
                raise ValueError("invalid_original_animation_constant_samples")
            stream = data["m_StreamedClip"]
            streamed = stream["data"]
            clip_payloads.update(streamed_frame_counts(streamed, stream["curveCount"]))
            clip_payloads.update({
                "clips_with_valid_timing": 1,
                "looping_clips": int(bool(muscle["m_LoopTime"])),
                "dense_samples": len(samples),
                "streamed_words": len(streamed),
                "constant_samples": len(constant),
                "generic_bindings": len(clip["m_ClipBindingConstant"]["genericBindings"]),
            })
    counts["source_clip_payloads"] = {
        **clip_payloads,
        "minimum_duration_seconds": min(durations, default=None),
        "maximum_duration_seconds": max(durations, default=None),
    }


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
