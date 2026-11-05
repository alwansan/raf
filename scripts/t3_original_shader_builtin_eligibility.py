#!/usr/bin/env python3
"""T3: original six-scene Renderer Shader48 source-name eligibility for exact Unity builtins.

This is a read-only, SHAs-verified *source* question. It never publishes original
Shader names/PathIDs or code. A source name in official Unity 2021.3.45f2's
archive makes only a *candidate* for future exact source/export builtin restore,
not a guarantee that the actual dummy ShaderLab gets replaced or renders.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as original
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.restore_builtin_shaders import archive_sources, download
from scripts.w1_stage_zip2_owners import fingerprint

STATUS = "AUTHENTIC_SCENE_SHADER48_OFFICIAL_BUILTIN_NAME_CANDIDACY_ONLY"
EXPECTED_SOURCE_TARGETS = 21
EXPECTED_SOURCE_SLOTS = 1633
EXPECTED_TOP_SLOTS = 921
EXPECTED_OFFICIAL_NAMES = 198


def compare(source_use: dict, source_names: dict, official_names, source_report: dict,
            *, target_count: int = EXPECTED_SOURCE_TARGETS,
            slot_count: int = EXPECTED_SOURCE_SLOTS,
            top_use: int = EXPECTED_TOP_SLOTS) -> dict:
    """Private exact-key comparison, only aggregate numbers/one boolean leave.

    source_use: (actual original provider, original Shader48 path_id)->Renderer
    material slot count, gathered from authenticated source original loader.
    source_names: same private keys -> (parsed m_Name, optional m_Name).
    """
    if (type(target_count) is not int or target_count <= 0 or
        type(slot_count) is not int or slot_count <= 0 or
        type(top_use) is not int or top_use <= 0 or
        not isinstance(source_use, dict) or not isinstance(source_names, dict) or
        len(source_use) != target_count or set(source_use) != set(source_names) or
        type(source_report) is not dict or
        source_report.get("status") != original.STATUS or
        source_report.get("six_original_scenes_sha_verified") is not True or
        source_report.get("original_selected_shader_owners_sha_verified") != 4 or
        source_report.get("original_material_target_owners_sha_verified") != 3 or
        source_report.get("original_distinct_typed_Shader48_targets") != target_count or
        source_report.get("counts", {}).get("original_slots_to_verified_Shader48") != slot_count or
        type(source_report.get("top_ten_typed_Shader48_slot_counts_no_identity")) is not list or
        source_report["top_ten_typed_Shader48_slot_counts_no_identity"][0] != top_use):
        raise ValueError("untrusted_source_Shader48_scene_population")
    if (type(official_names) not in (set, frozenset) or not official_names or
        not all(type(name) is str and name for name in official_names)):
        raise ValueError("bad_authentic_official_shader_name_set")
    if (sum(n for n in source_use.values() if type(n) is int) != slot_count or
        any(type(n) is not int or n <= 0 or n > slot_count for n in source_use.values()) or
        max(source_use.values()) != top_use or
        sum(n == top_use for n in source_use.values()) != 1):
        raise ValueError("invalid_original_Shader48_slot_weights")
    validated = {}
    seen_names = set()
    for key, names in source_names.items():
        if (type(key) is not tuple or len(key) != 2 or
            key[0] not in original.SHADER_OWNERS_SELECTED or
            type(key[1]) is not int or key[1] <= 0 or
            type(names) is not tuple or len(names) != 2):
            raise ValueError("invalid_source_Shader48_identity_shape")
        parsed, raw = names
        if ((parsed is not None and (type(parsed) is not str or not parsed)) or
            (raw is not None and (type(raw) is not str or not raw))):
            raise ValueError("invalid_original_Shader_name")
        if parsed and raw and parsed != raw:
            raise ValueError("conflicting_original_Shader_names")
        name = parsed or raw
        if not name or name in seen_names:
            raise ValueError("missing_or_ambiguous_original_Shader_name")
        seen_names.add(name)
        validated[key] = name
    highest = next(key for key, n in source_use.items() if n == top_use)
    candidate = {key for key, name in validated.items() if name in official_names}
    candidate_slots = sum(source_use[key] for key in candidate)
    return {
        "schema_version": 1,
        "status": STATUS,
        "scope": "authenticated_original_six_scene_source_only_not_actual_export",
        "source_Shaders_checked": len(validated),
        "source_Shader48_renderer_Material_slots": slot_count,
        "original_top_Shader_renderer_Material_slot_weight": top_use,
        "top_921_source_Shader_name_exactly_in_2021_builtin_list": highest in candidate,
        "source_Shader48_objects_with_exact_official_builtin_names": len(candidate),
        "original_renderer_slots_using_exact_official_builtin_name_candidates": candidate_slots,
        "source_Shader48_objects_not_in_exact_builtin_list": len(validated) - len(candidate),
        "original_renderer_slots_with_nonbuiltin_name_candidates": slot_count - candidate_slots,
        "all_original_shaders_had_valid_unique_serialized_names": True,
        "original_name_intersection_only_not_real_builtin_program_restored": True,
        "original_to_export_Shader_GUID_program_or_compiled_variant_verified": False,
        "full_Unity_native_restorer_or_Adreno_gpu_pixels_verified": False,
        "source_shader_names_ids_guids_per_identity_hashes_disclosed": False,
        "source_or_export_assets_modified": False,
    }


def probe(source: Path, manifest: Path, *, official_names=None, reader=None):
    private = {}
    source_report = original.load_original(source, manifest, private_slot_counts=private)
    selected = {key: n for key, n in private.items()
                if key[0] in original.SHADER_OWNERS_SELECTED}
    if len(selected) != EXPECTED_SOURCE_TARGETS or sum(selected.values()) != EXPECTED_SOURCE_SLOTS:
        raise ValueError("original_scene_Shader48_selected_scope_mismatch")
    if reader is None:
        import UnityPy
        reader = lambda path: UnityPy.load(str(path))
    names = {}
    by_owner = {}
    for owner, obj_id in selected:
        by_owner.setdefault(owner, set()).add(obj_id)
    for owner, ids in by_owner.items():
        path = source / "Raft_Data" / owner
        if path.is_symlink() or not path.is_file() or fingerprint(path) != SHADER_OWNERS[owner]:
            raise ValueError("original_Shader48_owner_fingerprint_mismatch")
        file = reader(path).file
        for obj in file.objects.values():
            if obj.path_id not in ids:
                continue
            if obj.type.name != "Shader" or (owner, obj.path_id) in names:
                raise ValueError("original_selected_Shader48_wrong_class_or_duplicate")
            tree = obj.read_typetree()
            if type(tree) is not dict or type(tree.get("m_ParsedForm")) is not dict:
                raise ValueError("original_Shader48_unexpected_name_tree")
            names[(owner, obj.path_id)] = (
                tree["m_ParsedForm"].get("m_Name"),
                tree.get("m_Name"),
            )
    if set(names) != set(selected):
        raise ValueError("incomplete_original_selected_Shader48_name_records")
    verified_official_archive = official_names is None
    if verified_official_archive:
        archive, _, _ = archive_sources(download())
        if len(archive) != EXPECTED_OFFICIAL_NAMES:
            raise ValueError("official_Unity_2021_shader_archive_count_drift")
        official_names = set(archive)
    report = compare(selected, names, official_names, source_report)
    report["official_Unity_2021_3_45f2_builtins_archive_SHA256_verified"] = (
        verified_official_archive
    )
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_public_source_Shader_name_report")
    try:
        report = probe(args.original, args.manifest)
    except Exception as error:
        report = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "exception_type": type(error).__name__,
            "original_to_export_Shader_GUID_program_or_compiled_variant_verified": False,
            "full_Unity_native_restorer_or_Adreno_gpu_pixels_verified": False,
            "source_shader_names_ids_guids_per_identity_hashes_disclosed": False,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("T3_ORIGINAL_921_SHADER_BUILTIN_ELIGIBILITY " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
