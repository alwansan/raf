"""Follow typed source references from selected skinned renderers to animation clips."""
import argparse
import json
import zlib
from collections import Counter, defaultdict
from pathlib import Path

from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.original_model_probe import ZIP2_SHA, ptr, stage_originals
from gfxlab.tools.shears_provenance_probe import resolve_pptr


class SourceGraph:
    def __init__(self, types):
        self.types = types
        self.externals = {}
        self.transforms = defaultdict(list)
        self.animators = defaultdict(list)
        self.renderers = defaultdict(list)
        self.cache = {}
        for owner, objects in types.items():
            if objects:
                first = next(iter(objects.values()))
                self.externals[owner] = [x.path for x in first.assets_file.externals]
            for path_id, obj in objects.items():
                kind = obj.type.name
                if kind not in {"Transform", "RectTransform", "Animator", "SkinnedMeshRenderer"}:
                    continue
                key = owner, path_id
                data = self.data(key)
                if kind == "SkinnedMeshRenderer":
                    mesh = self.target(data.get("m_Mesh"), owner, {"Mesh"})
                    if mesh:
                        self.renderers[mesh].append(key)
                    continue
                go = self.target(data.get("m_GameObject"), owner, {"GameObject"})
                if go:
                    mapping = self.animators if kind == "Animator" else self.transforms
                    mapping[go].append(key)

    def target(self, pointer, owner, kinds):
        _, key = resolve_pptr(pointer, owner, self.externals.get(owner, []))
        if key:
            obj = self.types.get(key[0], {}).get(key[1])
            if obj is not None and obj.type.name in kinds:
                return key
        return None

    def data(self, key):
        if key not in self.cache:
            self.cache[key] = self.types[key[0]][key[1]].read_typetree(check_read=False)
        return self.cache[key]

    def ancestry(self, node):
        visited = set()
        while node is not None:
            if node in visited or len(visited) >= 512:
                raise ValueError("Invalid source transform ancestry")
            visited.add(node)
            yield node
            data = self.data(node)
            father = data.get("m_Father")
            if ptr(father) == (0, 0):
                return
            node = self.target(father, node[0], {"Transform", "RectTransform"})
            if node is None:
                raise ValueError("Source parent Transform is unresolved")

    def nearest_animators(self, node):
        for key in self.ancestry(node):
            go = self.target(self.data(key).get("m_GameObject"), key[0], {"GameObject"})
            if self.animators.get(go):
                return self.animators[go]
        return []

    def relative_path(self, node, root):
        parts = []
        for key in self.ancestry(node):
            if key == root:
                return "/".join(reversed(parts))
            go = self.target(self.data(key).get("m_GameObject"), key[0], {"GameObject"})
            if go is None:
                return None
            parts.append(self.data(go)["m_Name"])
        return None

    def controller_report(self, animator, bone_nodes):
        a = self.data(animator)
        avatar = self.target(a.get("m_Avatar"), animator[0], {"Avatar"})
        controller = self.target(a.get("m_Controller"), animator[0], {"AnimatorController"})
        result = {
            "animator_enabled": bool(a.get("m_Enabled")),
            "avatar_resolved": avatar is not None,
            "controller_resolved": controller is not None,
        }
        if controller is None:
            return result
        refs = self.data(controller)["m_AnimationClips"]
        unique = set()
        unresolved = 0
        for ref in refs:
            clip = self.target(ref, controller[0], {"AnimationClip"})
            if clip is None:
                unresolved += 1
            else:
                unique.add(clip)
        counts = Counter()
        go = self.target(a.get("m_GameObject"), animator[0], {"GameObject"})
        roots = self.transforms[go]
        if len(roots) != 1:
            raise ValueError("Animator root Transform is ambiguous")
        # Match paths using the original Avatar hash table. The CRC check is an
        # additional consistency check, never used alone to infer a binding.
        names_by_hash = defaultdict(set)
        if avatar:
            for raw_id, path in self.data(avatar)["m_TOS"]:
                names_by_hash[raw_id & 0xFFFFFFFF].add(path)
        path_ids = defaultdict(set)
        for node in bone_nodes:
            path = self.relative_path(node, roots[0])
            if path is None:
                continue
            path_id = zlib.crc32(path.encode("utf-8"))
            if names_by_hash[path_id] == {path}:
                path_ids[path_id].add(node)
        all_bound = set()
        for clip in unique:
            data = self.data(clip)
            muscle = data.get("m_MuscleClip", {})
            if data.get("m_MuscleClipSize", 0) and muscle.get("m_Clip"):
                counts["clips_with_packed_muscle_data"] += 1
            bindings = data.get("m_ClipBindingConstant", {}).get("genericBindings", [])
            transforms = [b for b in bindings if b.get("typeID") == 4 and not b.get("isPPtrCurve")]
            if transforms:
                counts["clips_with_transform_bindings"] += 1
            bound = set()
            for binding in transforms:
                matches = path_ids.get(binding["path"] & 0xFFFFFFFF, set())
                if len(matches) == 1:
                    bound.update(matches)
                    counts["matched_bone_binding_occurrences"] += 1
            if bound:
                counts["clips_with_verified_bone_bindings"] += 1
                all_bound.update(bound)
        counts["bones_with_verified_avatar_path"] = sum(len(nodes) == 1 for nodes in path_ids.values())
        counts["bones_bound_across_clips"] = len(all_bound)
        return {**result, "controller_clip_refs": len(refs),
                "distinct_typed_clips": len(unique), "unresolved_clip_refs": unresolved, **counts}


def audit(stage):
    entries, types, _ = all_model_entries(stage)
    selection, _ = selected_five(stage)
    if len(selection["selected"]) != 5:
        raise ValueError("Source selection count changed")
    graph = SourceGraph(types)
    result = []
    for i, e in enumerate(entries):
        if not e["source_bones"]:
            continue
        mesh = e["owner"], e["mesh_pid"]
        renderers = graph.renderers[mesh]
        if i:
            row = selection["selected"][i - 1]
            if (row["owner"], row["mesh_pid"]) != mesh:
                raise ValueError("Source renderer selection changed")
            renderers = [r for r in renderers if graph.target(
                graph.data(r).get("m_GameObject"), r[0], {"GameObject"}
            ) == (row["owner"], row["game_object_pid"])]
        if len(renderers) != 1:
            raise ValueError("Exact source renderer is ambiguous")
        renderer = renderers[0]
        data = graph.data(renderer)
        go = graph.target(data.get("m_GameObject"), renderer[0], {"GameObject"})
        nodes = graph.transforms[go]
        if len(nodes) != 1:
            raise ValueError("Source renderer Transform is ambiguous")
        renderer_animators = graph.nearest_animators(nodes[0])
        bones = data["m_Bones"]
        if len(bones) != e["source_bones"]:
            raise ValueError("Source bone count changed")
        counts = Counter()
        without_animator = 0
        bone_nodes = []
        for ref in bones:
            node = graph.target(ref, renderer[0], {"Transform", "RectTransform"})
            if node is None:
                raise ValueError("Source bone Transform is unresolved")
            bone_nodes.append(node)
            animators = graph.nearest_animators(node)
            counts.update(animators)
            without_animator += not animators
        keys = sorted(set(renderer_animators) | counts.keys())
        result.append({"model": e["id"], "source_bones": len(bones),
                       "bones_without_animator_ancestor": without_animator,
                       "animator_candidates": [
                           {"renderer_nearest": key in renderer_animators,
                            "bones_nearest": counts[key], **graph.controller_report(key, bone_nodes)}
                           for key in keys
                       ]})
    return {"experiment": "GFX110", "source_sha": ZIP2_SHA, "cases": result,
            "animation_sampled": False, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2", "stage", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = audit(stage_originals(args.zip2, args.stage))
    args.safe.write_text(json.dumps(report, indent=2) + "\n")
