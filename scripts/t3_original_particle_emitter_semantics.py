#!/usr/bin/env python3
"""T3 source-only emitter-semantic bridge: six SHA-original scenes to Particle108.

This is NOT identification of the on-phone square smoke effect. Private original
GameObject names, scene names, PathIDs and Material PPtrs remain runner-private.
Only bounded counts from a fixed public keyword taxonomy are exported.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re

from scripts import t3_original_renderer_shader_impact as source
from scripts.b03_original_renderer_materials import pointer_shape
from scripts.b21_scene_lightmap_links import verify_source

STATUS = "SHA_ORIGINAL_PARTICLE108_EMITTER_NAME_HINTS_CLASSIFIED"
EXPECTED_RANKS = [108, 34, 34, 20, 16, 3]
# These are predeclared generic semantic hints, never extracted private names.
TOKENS = {
    "smoke_like": frozenset(("smoke", "smoky", "steam", "fume", "fumes", "dust", "ash")),
    "fire_like": frozenset(("fire", "flame", "flames", "ember", "embers", "spark", "sparks")),
    "water_like": frozenset(("water", "foam", "splash", "spray", "bubble", "bubbles")),
}


def hint_categories(name: str | None) -> set[str]:
    if name is None or not isinstance(name, str) or not name or len(name) > 4096:
        return set()
    # Handle CamelCase and common Unity punctuation without emitting strings.
    readable = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    words = set(re.findall(r"[a-z]+", readable.casefold()))
    return {category for category, tokens in TOKENS.items() if words & tokens}


def safe_aggregate(rows: list, *, expected_selected_slots: int = 108,
                   expected_selected_renderers: int = 54) -> dict:
    """Rows are private tuples: (is_selected, slot_matches, GameObject name|None).

    No caller-provided label, hash, renderer/path ID or source owner is returned.
    """
    if (type(rows) is not list
        or type(expected_selected_slots) is not int or expected_selected_slots <= 0
        or type(expected_selected_renderers) is not int or expected_selected_renderers <= 0
        or len(rows) > 100000):
        raise ValueError("untrusted_particle_emitter_aggregate_scope")
    count = Counter()
    selected_slots = 0
    for row in rows:
        if (type(row) is not tuple or len(row) != 3
            or type(row[0]) is not bool or type(row[1]) is not int
            or row[1] < 0 or row[1] > 256
            or (row[0] and row[1] == 0) or (not row[0] and row[1] != 0)
            or (row[2] is not None and type(row[2]) is not str)):
            raise ValueError("invalid_source_particle_renderer_record")
        selected, slots, name = row
        group = "selected" if selected else "other"
        selected_slots += slots
        count[group + "_renderer_objects"] += 1
        if name is None or not name:
            count[group + "_GameObject_name_unresolved"] += 1
        else:
            count[group + "_GameObject_name_resolved"] += 1
            hints = hint_categories(name)
            for tag in TOKENS:
                count[group + "_" + tag + "_GameObject_names"] += int(tag in hints)
            count[group + "_no_semantic_keyword_match"] += int(not hints)
    if (selected_slots != expected_selected_slots
        or count["selected_renderer_objects"] != expected_selected_renderers):
        raise ValueError("source_original_selected_108_particle_scope_changed")
    result = {
        "schema_version": 1, "status": STATUS,
        "source_selected_particle_shader_renderer_objects": count["selected_renderer_objects"],
        "source_selected_particle_shader_material_slot_use": selected_slots,
        "source_other_particle_renderer_objects": count["other_renderer_objects"],
    }
    for group in ("selected", "other"):
        for key in ("GameObject_name_resolved", "GameObject_name_unresolved",
                    "smoke_like_GameObject_names", "fire_like_GameObject_names",
                    "water_like_GameObject_names", "no_semantic_keyword_match"):
            result[group + "_" + key] = count[group + "_" + key]
        if (result[group + "_GameObject_name_resolved"]
              + result[group + "_GameObject_name_unresolved"]
              != count[group + "_renderer_objects"]):
            raise ValueError("source_GameObject_join_accounting_mismatch")
    result.update({
        "original_names_guids_PathIDs_or_private_shader_identifiers_published": False,
        "name_hint_is_not_onscreen_smoke_emitter_identity": True,
        "original_game_device_pixels_verified": False,
        "actual_android_ShaderLab_pass_recovered": False,
    })
    return result



def safe_ranked_semantic_hints(source_shader_ranks: dict, tagged_slots: list) -> dict:
    """Collapse private (Shader owner/ID, scene object ID) into anonymous ranks.

    tagged_slots are (fixed category, private shader key, private renderer key, count).
    Only total SOURCE particle material use rank and semantic matched counts leave.
    """
    if (type(source_shader_ranks) is not dict or not source_shader_ranks
        or type(tagged_slots) is not list or len(tagged_slots) > 100000
        or any(type(n) is not int or n < 1 for n in source_shader_ranks.values())):
        raise ValueError("invalid_original_private_Shader48_rank_scope")
    slots = Counter()
    renderers = {}
    for row in tagged_slots:
        if (type(row) is not tuple or len(row) != 4
            or row[0] not in TOKENS or row[1] not in source_shader_ranks
            or not isinstance(row[2], tuple) or len(row[2]) != 2
            or type(row[3]) is not int or not 0 < row[3] <= 256):
            raise ValueError("invalid_private_original_semantic_Shader48_slot")
        tag, shader, renderer, n = row
        key = (tag, shader)
        slots[key] += n
        renderers.setdefault(key, set()).add(renderer)
        if slots[key] > source_shader_ranks[shader]:
            raise ValueError("semantic_Shader48_slots_exceed_original_source_rank")
    result = {}
    for tag in TOKENS:
        safe = []
        for (label, shader), n in slots.items():
            if label == tag:
                safe.append({
                    "original_source_particle_Shader48_total_material_use_rank": source_shader_ranks[shader],
                    "matched_semantic_material_slots": n,
                    "matched_semantic_renderer_objects": len(renderers[(label, shader)]),
                })
        safe.sort(key=lambda x: (
            -x["matched_semantic_material_slots"],
            -x["original_source_particle_Shader48_total_material_use_rank"],
            -x["matched_semantic_renderer_objects"],
        ))
        result[tag + "_anonymous_source_Shader48_candidates"] = safe
    return result


def local_gameobject_name(renderer_tree: dict, by_id: dict):
    pointer = renderer_tree.get("m_GameObject")
    if (not isinstance(pointer, dict)
        or type(pointer.get("m_FileID")) is not int
        or type(pointer.get("m_PathID")) is not int):
        return None
    file_id, path_id = pointer["m_FileID"], pointer["m_PathID"]
    if file_id != 0 or path_id <= 0:
        return None
    target = by_id.get(path_id)
    if target is None or target.type.name != "GameObject":
        return None
    obj = target.read_typetree(check_read=False)
    if not isinstance(obj, dict):
        return None
    name = obj.get("m_Name")
    return name if isinstance(name, str) and 0 < len(name) <= 4096 else None


def scan_original(original: Path, manifest: Path) -> dict:
    import UnityPy

    private_slot_counts = {}
    private_materials = {}
    original_report = source.load_original(
        original, manifest,
        private_particle_slot_counts=private_slot_counts,
        private_particle_materials=private_materials,
    )
    if (original_report.get("status") != source.STATUS
        or original_report.get("six_original_scenes_sha_verified") is not True
        or original_report.get("original_particle_Shader48_ranked_material_slot_use_no_identity") != EXPECTED_RANKS
        or original_report.get("original_particle_highest_Shader48_unique") is not True
        or original_report.get("original_particle_highest_Shader48_nonparticle_renderer_slots") != 0):
        raise ValueError("untrusted_authenticated_original_particle108_source")
    targets = [k for k, n in private_slot_counts.items() if n == 108]
    if len(targets) != 1 or targets[0] not in private_materials:
        raise ValueError("ambiguous_private_original_particle108_material_targets")
    selected_materials = private_materials[targets[0]]
    if len(selected_materials) != 5:
        raise ValueError("original_particle108_selected_Material21_count_changed")
    material_to_shader = {}
    for shader, material_set in private_materials.items():
        if shader not in private_slot_counts or not isinstance(material_set, set):
            raise ValueError("original_source_particle_Shader48_Material_join_incomplete")
        for material in material_set:
            if material in material_to_shader:
                raise ValueError("original_source_Material_has_multiple_Shader48_targets")
            material_to_shader[material] = shader
    records = []
    tagged_shader_slots = []
    typed_source_slots = 0
    for scene, pin in source.SCENE_PINS.items():
        scene_path = original / "Raft_Data" / scene
        if scene_path.is_symlink():
            raise ValueError("unsafe_original_scene_symlink")
        verify_source(scene_path, pin)
        file = UnityPy.load(str(scene_path)).file
        by_id = {obj.path_id: obj for obj in file.objects.values()}
        external_paths = [row.path for row in file.externals]
        local_types = {key: value.type.name for key, value in by_id.items()}
        for obj in file.objects.values():
            if obj.type.name != "ParticleSystemRenderer":
                continue
            tree = obj.read_typetree(check_read=False)
            if not isinstance(tree, dict) or not isinstance(tree.get("m_Materials"), list):
                raise ValueError("unreadable_original_particle_renderer_materials")
            selected_slots = 0
            name = local_gameobject_name(tree, by_id)
            tags = hint_categories(name)
            for ptr in tree["m_Materials"]:
                state, fid, pid = pointer_shape(
                    ptr, local_types, len(external_paths))
                if state == "null_material_slot":
                    continue
                if state != "external_target_unverified":
                    raise ValueError("unexpected_original_particle_local_material_source")
                material_owner = PurePosixPath(external_paths[fid-1].replace("\\", "/")).name
                material_key = (material_owner, pid)
                selected_slots += int(material_key in selected_materials)
                source_shader = material_to_shader.get(material_key)
                if source_shader is not None:
                    typed_source_slots += 1
                    for tag in tags:
                        tagged_shader_slots.append(
                            (tag, source_shader, (scene, obj.path_id), 1))
            records.append((bool(selected_slots), selected_slots, name))
    if typed_source_slots != original_report["original_particle_typed_Shader48_material_slots"]:
        raise ValueError("original_particle_verified_typed_Shader48_slot_join_incomplete")
    result = safe_aggregate(
        records,
        expected_selected_slots=108,
        expected_selected_renderers=original_report["original_particle_highest_Shader48_distinct_particle_renderers"],
    )
    result.update(safe_ranked_semantic_hints(private_slot_counts, tagged_shader_slots))
    result["source_original_typed_particle_Shader48_slots_rejoined"] = typed_source_slots
    result["original_six_scene_SHA_verified"] = True
    result["original_four_shader_Material_owner_SHA_verified"] = True
    result["original_source_selected_five_Material21_verified"] = True
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original", "manifest", "out"):
        ap.add_argument("--" + key, required=True, type=Path)
    args = ap.parse_args(argv)
    if (args.out.is_symlink() or args.out.exists()
        or args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_emitter_semantic_report_destination")
    try:
        out = scan_original(args.original, args.manifest)
    except Exception as exc:
        # Never format private error strings, original file identities or names.
        out = {"schema_version": 1, "status": "INCONCLUSIVE",
               "failure_type": type(exc).__name__,
               "original_names_guids_PathIDs_or_private_shader_identifiers_published": False,
               "original_game_device_pixels_verified": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("T3_ORIGINAL_PARTICLE_EMITTER_HINTS " + json.dumps(out, sort_keys=True))
    return 0 if out["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
