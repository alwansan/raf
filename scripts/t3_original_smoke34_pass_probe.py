#!/usr/bin/env python3
"""SHA-original smoke-like 34-slot Shader48 Pass-state probe (NO APK).

Private original GameObject names, owner/path IDs, Material and Shader source
identities remain in runner memory. Only fixed generic state classifications
are returned. Name hints are not visual/phone emitter proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath

from scripts import t3_original_renderer_shader_impact as original
from scripts.t3_original_particle_emitter_semantics import (
    EXPECTED_RANKS, hint_categories, local_gameobject_name,
)
from scripts.t3_original_particle_shader_state import classify_state
from scripts.b03_original_renderer_materials import pointer_shape
from scripts.b21_scene_lightmap_links import verify_source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint

STATUS = "SHA_ORIGINAL_SMOKE34_PASS_STATE_CLASSIFIED"


def choose_smoke_shader(rows: list, private_ranks: dict):
    """Return PRIVATE shader key from 17 actual smoke-hint renderers / 34 slots.

    rows are (private_renderer_key, private_shader_key, slots) records, after
    original PPtrs were resolved. Rank is checked by identity, never by equal
    anonymous count alone; neither private key is serialized.
    """
    if (type(rows) is not list or len(rows) != 17
        or type(private_ranks) is not dict
        or sorted(private_ranks.values(), reverse=True) != EXPECTED_RANKS):
        raise ValueError("untrusted_smoke34_rank_or_renderer_scope")
    counts = Counter()
    renderers = set()
    for row in rows:
        if (type(row) is not tuple or len(row) != 3
            or type(row[0]) is not tuple or len(row[0]) != 2
            or type(row[1]) is not tuple or len(row[1]) != 2
            or type(row[2]) is not int or row[2] != 2):
            raise ValueError("invalid_original_smoke_renderer_slot_record")
        renderer, shader, slots = row
        if renderer in renderers or shader not in private_ranks:
            raise ValueError("duplicate_renderer_or_unverified_private_Shader48")
        renderers.add(renderer)
        counts[shader] += slots
    if len(renderers) != 17 or len(counts) != 1:
        raise ValueError("ambiguous_original_smoke_shader_source")
    target, slots = next(iter(counts.items()))
    if slots != 34 or private_ranks[target] != 34:
        raise ValueError("smoke_shader_not_unique_34_slot_source")
    return target


def inspect_smoke_parsed(parsed: dict, classifier=classify_state):
    """Examine ALL actual normal Pass states without emitting names/programs."""
    if not isinstance(parsed, dict):
        raise ValueError("missing_original_smoke_Shader48_parsed_form")
    subs = parsed.get("m_SubShaders")
    if type(subs) is not list or not 1 <= len(subs) <= 8:
        raise ValueError("invalid_original_smoke_SubShader_count")
    out = []
    for si, sub in enumerate(subs):
        passes = sub.get("m_Passes") if isinstance(sub, dict) else None
        if type(passes) is not list or len(passes) > 32:
            raise ValueError("invalid_original_smoke_Pass_list")
        for pi, rec in enumerate(passes):
            if not isinstance(rec, dict) or type(rec.get("m_Type")) is not int:
                raise ValueError("invalid_original_smoke_Pass_record")
            if rec["m_Type"] != 0:
                raise ValueError("unsupported_original_smoke_non_normal_Pass_type")
            state = classifier(rec.get("m_State"))
            if not isinstance(state, dict) or any(
                type(k) is not str or not k.startswith(
                    ("original_", "serialized_", "native_")
                ) for k in state
            ):
                raise ValueError("unsafe_original_smoke_classification")
            out.append({"subshader_index": si, "pass_index": pi,
                        "original_normal_Pass": True, **state})
    if not out or len(out) > 64:
        raise ValueError("empty_or_unbounded_original_smoke_Pass_records")
    return out


def probe(original_root: Path, manifest: Path):
    import UnityPy

    ranks = {}
    materials = {}
    auth = original.load_original(
        original_root, manifest,
        private_particle_slot_counts=ranks,
        private_particle_materials=materials,
    )
    if (auth.get("status") != original.STATUS
        or auth.get("six_original_scenes_sha_verified") is not True
        or auth.get("original_particle_Shader48_ranked_material_slot_use_no_identity") != EXPECTED_RANKS
        or auth.get("original_particle_highest_Shader48_unique") is not True
        or auth.get("original_particle_highest_Shader48_nonparticle_renderer_slots") != 0
        or sorted(ranks.values(), reverse=True) != EXPECTED_RANKS
        or set(materials) != set(ranks)):
        raise ValueError("unauthenticated_original_six_scene_particle_graph")
    material_to_shader = {}
    for shader, matset in materials.items():
        if type(matset) is not set:
            raise ValueError("untrusted_original_Shader_Material_set")
        for material in matset:
            if material in material_to_shader:
                raise ValueError("original_Material_duplicate_Shader_binding")
            material_to_shader[material] = shader

    rows = []
    named = 0
    for scene, pin in original.SCENE_PINS.items():
        path = original_root / "Raft_Data" / scene
        if path.is_symlink():
            raise ValueError("unsafe_original_scene_symlink")
        verify_source(path, pin)
        file = UnityPy.load(str(path)).file
        by_id = {obj.path_id: obj for obj in file.objects.values()}
        types = {key: obj.type.name for key, obj in by_id.items()}
        external = [e.path for e in file.externals]
        for obj in file.objects.values():
            if obj.type.name != "ParticleSystemRenderer":
                continue
            tree = obj.read_typetree(check_read=False)
            if not isinstance(tree, dict):
                raise ValueError("unreadable_original_particle_tree")
            if "smoke_like" not in hint_categories(
                local_gameobject_name(tree, by_id)
            ):
                continue
            named += 1
            pointers = tree.get("m_Materials")
            if type(pointers) is not list:
                raise ValueError("unreadable_original_smoke_material_slots")
            shaders = Counter()
            for ptr in pointers:
                state, fid, pid = pointer_shape(ptr, types, len(external))
                if state == "null_material_slot":
                    continue
                if state != "external_target_unverified":
                    raise ValueError("unresolved_original_smoke_material_PPtr")
                owner = PurePosixPath(external[fid-1].replace("\\", "/")).name
                key = (owner, pid)
                target = material_to_shader.get(key)
                if target is None:
                    raise ValueError("unresolved_original_smoke_Material_to_Shader48")
                shaders[target] += 1
            if len(shaders) != 1:
                raise ValueError("original_smoke_renderer_multiple_Shader48")
            shader, slots = next(iter(shaders.items()))
            rows.append(((scene, obj.path_id), shader, slots))
    if named != 17:
        raise ValueError("original_smoke_name_hint_population_drift")
    target = choose_smoke_shader(rows, ranks)
    owner, pid = target
    if (owner not in original.SHADER_OWNERS_SELECTED
        or type(pid) is not int or pid <= 0):
        raise ValueError("invalid_private_original_smoke_shader_target")
    path = original_root / "Raft_Data" / owner
    if path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("original_smoke_Shader48_owner_SHA_drift")
    file = UnityPy.load(str(path)).file
    found = [obj for obj in file.objects.values() if obj.path_id == pid]
    if len(found) != 1 or found[0].type.name != "Shader":
        raise ValueError("original_smoke_target_not_unique_Shader48")
    passes = inspect_smoke_parsed(found[0].read_typetree().get("m_ParsedForm"))
    return {
        "schema_version": 1, "status": STATUS,
        "original_zip2_provider_commit_verified": True,
        "original_six_scene_SHA_verified": True,
        "original_four_shader_Material_owner_SHA_verified": True,
        "original_smoke_like_renderer_objects": 17,
        "original_smoke_like_material_slots": 34,
        "original_smoke_Shader48_private_identity_uniquely_linked": True,
        "original_shader34_equal_rank_other_shader_not_merged": True,
        "original_subshader_count": len({row["subshader_index"] for row in passes}),
        "original_normal_pass_count": len(passes),
        "original_normal_pass_state_categories": passes,
        "shader_source_names_guids_PathIDs_bytecode_published": False,
        "postvendor_same_instance_export_state_verified": False,
        "original_program_variant_or_texture_alpha_verified": False,
        "Android_phone_smoke_pixels_or_game_fix_verified": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original", "manifest", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_private_original_output_path")
    try:
        result = probe(a.original, a.manifest)
    except Exception as exc:
        # Never log the exception text: it can contain private asset identifiers.
        result = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_type": type(exc).__name__,
                  "shader_source_names_guids_PathIDs_bytecode_published": False,
                  "Android_phone_smoke_pixels_or_game_fix_verified": False}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                     encoding="utf-8")
    print("T3_SHA_ORIGINAL_SMOKE34_STATE " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
