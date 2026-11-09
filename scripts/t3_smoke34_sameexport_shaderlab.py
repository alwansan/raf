#!/usr/bin/env python3
"""T3 SHA-original smoke-name Shader48 → SAME AssetRipper instance ShaderLab.

Original names, IDs, GUIDs and exported ShaderLab never leave the private runner.
The original 17-renderer/34-slot identity is re-resolved, not inferred by rank.
This is not original GPU bytecode equivalence or phone smoke verification.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re

from scripts import t3_original_renderer_shader_impact as source
from scripts.t3_original_particle_emitter_semantics import (
    EXPECTED_RANKS, hint_categories, local_gameobject_name,
)
from scripts.t3_original_smoke34_pass_probe import (
    choose_smoke_shader, inspect_smoke_parsed,
)
from scripts.b03_original_renderer_materials import pointer_shape
from scripts.b21_scene_lightmap_links import verify_source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.t3_same_export_material_texenv import combine_same_export
from scripts.b05_verify_material_texenv_bindings import _trace_source, _trace_export
from scripts.probe_a13_exported_material_shader_guids import GUID, BUILTIN
from scripts.b49_shaderlab_pass_contract import pass_coverage, remove_comments

STATUS = "T3_SHA_SMOKE34_SAME_INSTANCE_SHADERLAB_CLASSIFIED"
MAX_ITEMS = 150000
MAX_SHADER_BYTES = 8000000


def original_private_smoke_target(root: Path, manifest: Path):
    """Rebuild private original 17→34 linkage, return selected target and state."""
    import UnityPy
    ranks, materials = {}, {}
    auth = source.load_original(root, manifest,
        private_particle_slot_counts=ranks, private_particle_materials=materials)
    if (auth.get("status") != source.STATUS
        or auth.get("six_original_scenes_sha_verified") is not True
        or auth.get("original_particle_Shader48_ranked_material_slot_use_no_identity") != EXPECTED_RANKS
        or auth.get("original_particle_highest_Shader48_unique") is not True
        or auth.get("original_particle_highest_Shader48_nonparticle_renderer_slots") != 0
        or sorted(ranks.values(), reverse=True) != EXPECTED_RANKS
        or set(materials) != set(ranks)):
        raise ValueError("unauthenticated_original_smoke34_particle_scope")
    material_to_shader = {}
    for shader, matset in materials.items():
        if type(matset) is not set:
            raise ValueError("invalid_private_original_smoke_material_set")
        for material in matset:
            if material in material_to_shader:
                raise ValueError("ambiguous_source_Material_to_Shader")
            material_to_shader[material] = shader
    rows = []
    smoke_names = 0
    for scene, pin in source.SCENE_PINS.items():
        path = root / "Raft_Data" / scene
        if path.is_symlink():
            raise ValueError("unsafe_original_scene_symlink")
        verify_source(path, pin)
        file = UnityPy.load(str(path)).file
        by_id = {o.path_id: o for o in file.objects.values()}
        types = {pid: o.type.name for pid, o in by_id.items()}
        external = [x.path for x in file.externals]
        for obj in file.objects.values():
            if obj.type.name != "ParticleSystemRenderer":
                continue
            tree = obj.read_typetree(check_read=False)
            if not isinstance(tree, dict):
                raise ValueError("bad_original_renderer_tree")
            if "smoke_like" not in hint_categories(
                local_gameobject_name(tree, by_id)):
                continue
            smoke_names += 1
            ptrs = tree.get("m_Materials")
            if type(ptrs) is not list:
                raise ValueError("missing_original_smoke_renderer_materials")
            found = Counter()
            for ptr in ptrs:
                state, fid, pid = pointer_shape(ptr, types, len(external))
                if state == "null_material_slot":
                    continue
                if state != "external_target_unverified":
                    raise ValueError("untrusted_original_smoke_material_pointer")
                owner = PurePosixPath(external[fid - 1].replace("\\", "/")).name
                target = material_to_shader.get((owner, pid))
                if target is None:
                    raise ValueError("unresolved_original_smoke_shader_pointer")
                found[target] += 1
            if len(found) != 1:
                raise ValueError("ambiguous_original_smoke_renderer_shader")
            shader, slots = next(iter(found.items()))
            rows.append(((scene, obj.path_id), shader, slots))
    if smoke_names != 17:
        raise ValueError("changed_original_smoke_name_population")
    key = choose_smoke_shader(rows, ranks)
    owner, pid = key
    if (owner not in source.SHADER_OWNERS_SELECTED
        or type(pid) is not int or pid <= 0):
        raise ValueError("invalid_private_original_Shader48_key")
    path = root / "Raft_Data" / owner
    if path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("changed_original_smoke_Shader48_owner_SHA")
    file = UnityPy.load(str(path)).file
    objects = [o for o in file.objects.values() if o.path_id == pid]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("unresolved_typed_original_smoke_Shader48")
    passes = inspect_smoke_parsed(
        objects[0].read_typetree().get("m_ParsedForm"))
    if (len(passes) != 1
        or passes[0].get("original_pass_color_blend_category") != "ALPHA_DEPENDENT"
        or passes[0].get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT"
        or passes[0].get("original_pass_color_mask_shaderlab_channels") != "RGB"
        or passes[0].get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("original_smoke34_pass_baseline_changed")
    return key, passes[0]


def lexical_colormask_scope(shaderlab: str):
    """Only describe exact token presence; never assert bound active Pass."""
    if type(shaderlab) is not str or len(shaderlab) > MAX_SHADER_BYTES:
        raise ValueError("invalid_exported_shaderlab_text_scope")
    clean = remove_comments(shaderlab)
    tokens = re.findall(r"(?im)(?:^|\\{)[ \\t]*ColorMask[ \\t]+(RGB|RGBA|0|[RGBA]{1,4})(?=[ \\t]*(?:$|\\}))", clean)
    # Mask directives inside HLSL or alternate SubShaders remain ambiguous.
    upper = [v.upper() for v in tokens]
    return {
        "lexical_shaderlab_colormask_RGB_seen": "RGB" in upper,
        "lexical_shaderlab_colormask_RGBA_seen": "RGBA" in upper,
        "lexical_shaderlab_colormask_directive_count": len(upper),
        "lexical_colormask_active_pass_or_runtime_proven": False,
    }


def compare_same_export(shader_key: tuple, w1: dict, b02: dict, assets: Path):
    """Select exact .shader via same-instance Class48 trace and its private GUID."""
    if (type(shader_key) is not tuple or len(shader_key) != 2
        or shader_key[0] not in source.SHADER_OWNERS_SELECTED
        or type(shader_key[1]) is not int or shader_key[1] <= 0
        or not assets.is_dir() or assets.is_symlink()
        or any(p.is_symlink() for p in assets.parents)):
        raise ValueError("unsafe_original_private_shader_or_export_Assets")
    combine_same_export(w1, b02)
    candidates = [row for row in w1["objects"]
                  if row.get("class_id") == 48 and _trace_source(row) == shader_key]
    if len(candidates) != 1:
        raise ValueError("missing_or_duplicate_exact_same_instance_Shader48_trace")
    ptr = _trace_export(candidates[0])
    if ptr[0] <= 0:
        raise ValueError("null_real_Shader48_export_pointer")
    result = {
        "schema_version": 1, "status": STATUS,
        "same_instance_w1_b02_trace_verified": True,
        "original_smoke_renderers": 17, "original_smoke_material_slots": 34,
        "original_distinct_equal_rank_fire_Shader48_not_confused": True,
        "original_pass_count": 1, "original_color_blend": "ALPHA_DEPENDENT",
        "original_alpha_blend": "ALPHA_DEPENDENT",
        "original_color_mask": "RGB", "original_zwrite": "OFF",
        "original_shader_program_same_export_equivalence_proven": False,
        "exported_active_pass_equivalence_proven": False,
        "original_private_shader_name_ID_guid_programs_published": False,
        "android_game_device_smoke_pixels_verified": False,
        "actual_exported_custom_shader": False,
        "actual_exported_builtin_reference": False,
        "selected_shaderlab_dummy_exporter_marker": False,
        "selected_shaderlab_no_subprogram_marker": False,
        "selected_shaderlab_pass_count": 0,
        "selected_shaderlab_complete_program_pass_count": 0,
        "selected_shaderlab_braces_balanced": False,
        "lexical_shaderlab_colormask_RGB_seen": False,
        "lexical_shaderlab_colormask_RGBA_seen": False,
        "lexical_shaderlab_colormask_directive_count": 0,
        "lexical_colormask_active_pass_or_runtime_proven": False,
    }
    if ptr[1] in BUILTIN:
        if ptr[2] != 0:
            raise ValueError("wrong_original_builtin_shader_pointer_kind")
        result["actual_exported_builtin_reference"] = True
        result["export_shader_status"] = "UNITY_BUILTIN_REFERENCE_NO_CUSTOM_SHADERLAB"
        return result
    if ptr[2] not in (2, 3):
        raise ValueError("invalid_original_custom_Shader48_export_kind")
    result["actual_exported_custom_shader"] = True
    paths = list(assets.rglob("*"))
    if len(paths) > MAX_ITEMS or any(p.is_symlink() for p in paths):
        raise ValueError("unsafe_or_oversized_exported_Assets_inventory")
    selected = []
    for meta in paths:
        if not meta.is_file() or not meta.name.endswith(".shader.meta"):
            continue
        if meta.stat().st_size > 256000:
            raise ValueError("oversized_exported_shader_meta")
        matches = GUID.findall(meta.read_text("utf-8-sig"))
        if len(matches) != 1:
            raise ValueError("invalid_exported_shader_meta_guid")
        if matches[0].lower() == ptr[1]:
            selected.append(meta)
    if len(selected) > 1:
        raise ValueError("duplicate_exported_shader_meta_same_GUID")
    if not selected:
        result["export_shader_status"] = "CUSTOM_SHADER_META_MISSING"
        return result
    sibling = Path(str(selected[0])[:-5])
    if not sibling.is_file() or sibling.is_symlink():
        result["export_shader_status"] = "CUSTOM_SHADER_TEXT_MISSING"
        return result
    if sibling.stat().st_size > MAX_SHADER_BYTES:
        raise ValueError("oversized_selected_exported_ShaderLab")
    shaderlab = sibling.read_text("utf-8-sig")
    coverage = pass_coverage(shaderlab)
    if (type(coverage.get("pass_count")) is not int
        or type(coverage.get("passes_with_complete_program")) is not int
        or type(coverage.get("pass_braces_balanced")) is not bool):
        raise ValueError("unsafe_export_ShaderLab_coverage_schema")
    result["selected_shaderlab_dummy_exporter_marker"] = (
        "//DummyShaderTextExporter" in shaderlab)
    result["selected_shaderlab_no_subprogram_marker"] = (
        "// No subprograms found" in shaderlab)
    result["selected_shaderlab_pass_count"] = coverage["pass_count"]
    result["selected_shaderlab_complete_program_pass_count"] = coverage[
        "passes_with_complete_program"]
    result["selected_shaderlab_braces_balanced"] = coverage[
        "pass_braces_balanced"]
    result.update(lexical_colormask_scope(shaderlab))
    if result["selected_shaderlab_dummy_exporter_marker"]:
        result["export_shader_status"] = "ACTUAL_DUMMY_SHADER_TEXT_EXPORTER"
    elif result["selected_shaderlab_no_subprogram_marker"]:
        result["export_shader_status"] = "NO_PROGRAM_SUBPROGRAMS_EXPORTED"
    elif (not coverage["pass_braces_balanced"] or
          coverage["pass_count"] == 0 or
          coverage["passes_with_complete_program"] == 0):
        result["export_shader_status"] = "INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER"
    else:
        result["export_shader_status"] = (
            "PROGRAMMED_STRUCTURAL_PASS_NOT_AUTHENTICITY")
    return result


def run(original: Path, manifest: Path, project: Path, w1path: Path, b02path: Path):
    key, state = original_private_smoke_target(original, manifest)
    if state.get("native_ShaderLab_or_Android_pixels_not_verified") is not True:
        raise ValueError("untrusted_original_smoke_state_evidence")
    w1 = json.loads(w1path.read_text("utf-8"))
    b02 = json.loads(b02path.read_text("utf-8"))
    safe = compare_same_export(key, w1, b02, project / "Assets")
    safe["original_six_scene_SHA_verified"] = True
    safe["original_four_owner_SHA_verified"] = True
    return safe


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original", "manifest", "project", "w1-trace", "b02-trace", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("unsafe_private_smoke_export_report_destination")
    try:
        safe = run(a.original, a.manifest, a.project, a.w1_trace, a.b02_trace)
    except Exception as ex:
        # Never expose original errors: raw exception messages may name files/IDs.
        safe = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "failure_type": type(ex).__name__,
            "android_game_device_smoke_pixels_verified": False,
            "original_private_shader_name_ID_guid_programs_published": False,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print("T3_SMOKE34_ACTUAL_SAME_EXPORT " + json.dumps(safe, sort_keys=True))
    return 0 if safe["status"] == STATUS else 2

if __name__ == "__main__":
    raise SystemExit(main())
