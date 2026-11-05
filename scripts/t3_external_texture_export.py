#!/usr/bin/env python3
"""T3 authentic cross-owner Texture2D source→same-AssetRipper-export fidelity.

Requires 3 exact SHA-authenticated ZIP2 original owners, original one-based
external dependency table, W1 Material21 trace and B02 Texture2D28 trace
from ONE exporter invocation, and actual exported Unity Material YAML.
Never compare naked m_PathID, property name alone, guessed GUID, or unverified
archive wrapper. No private object identities / values enter public outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath

from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_external_texture_lineage as previous
from scripts import t3_same_export_material_texenv as common
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
from scripts.w1_stage_zip2_owners import fingerprint

OWNER = previous.SOURCE_OWNER
TARGETS = {"sharedassets0.assets":22, "sharedassets1.assets":3}
TOTAL = sum(TARGETS.values())
SOURCE_SHA = common.SOURCE_SHA


def owner_name(path):
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("invalid_original_or_exported_source_owner")
    name = PurePosixPath(path.replace("\\", "/")).name
    if not name or name in (".", ".."):
        raise ValueError("unsafe_original_owner_basename")
    return name


def verify_and_index_original_targets(root: Path):
    """Classify exact source object PathIDs after SHA validating both providers."""
    import UnityPy
    root = root / "Raft_Data"
    types = {}
    for name in TARGETS:
        source = root / name
        if (source.is_symlink() or not source.is_file()
                or fingerprint(source) != SHADER_OWNERS[name]):
            raise ValueError("unverified_external_original_owner_bytes")
        env = UnityPy.load(str(source))
        objtypes = {}
        for obj in env.file.objects.values():
            pid = obj.path_id
            if type(pid) is not int or pid <= 0 or pid in objtypes:
                raise ValueError("duplicate_original_external_target_identity")
            objtypes[pid] = obj.type.name
        types[name] = objtypes
    return types


def compare_external(original, paths, original_types, w1, b02, exported):
    """Private exact comparison, only safe aggregate returns."""
    for name in TARGETS:
        if not isinstance(original_types.get(name), dict):
            raise ValueError("external_original_owner_not_authenticated")
    if len(original) != 41 or sum(len(v) for v in original.values()) != 227:
        raise ValueError("unexpected_selected_original_material_scope")
    # This controls both trace instance correspondence AND typed object classes
    # rather than accepting two unrelated exports with identical filenames.
    common.combine_same_export(w1, b02)
    material_rows = {}
    for row in w1["objects"]:
        if row.get("class_id") != 21:
            continue
        src = row.get("source")
        if not isinstance(src, dict) or set(src) != {"owner","path_id"}:
            raise ValueError("malformed_same_export_material_identity")
        if owner_name(src["owner"]) != OWNER:
            continue
        key = (OWNER, src["path_id"])
        if key in material_rows or key not in original:
            raise ValueError("duplicate_or_untrusted_exported_material_identity")
        ptr = b05._trace_export(row)
        if ptr[0] <= 0 or ptr[2] not in (2,3):
            raise ValueError("invalid_same_export_material_pointer")
        material_rows[key] = ptr[:2]
    if set(material_rows) != set(original) or not set(material_rows.values()).issubset(exported):
        raise ValueError("selected_materials_not_in_exact_export")
    if len(set(material_rows.values())) != len(material_rows):
        raise ValueError("same_export_material_pointer_collision")

    texture_rows = {}
    for row in b02["objects"]:
        if row.get("class_id") != 28:
            raise ValueError("non_Texture2D_in_export_trace")
        src = row.get("source")
        if not isinstance(src, dict) or set(src) != {"owner","path_id"}:
            raise ValueError("malformed_original_exported_texture_identity")
        key = (owner_name(src["owner"]),src["path_id"])
        if key in texture_rows:
            raise ValueError("duplicate_original_texture_export_identity")
        ptr = b05._trace_export(row)
        if ptr[0] <= 0 or ptr[2] not in (2,3):
            raise ValueError("invalid_Texture2D_export_pointer")
        texture_rows[key] = ptr

    if not isinstance(paths, list):
        raise ValueError("invalid_original_external_table")
    outcome = Counter()
    per_owner = Counter()
    for material, slots in original.items():
        actual = exported[material_rows[material]]
        for slotname, val in slots.items():
            original_ptr, _uv = b05._slot(val)
            file_id, path_id = original_ptr
            if file_id == 0 or path_id == 0:
                continue
            if file_id > len(paths):
                raise ValueError("external_original_fileid_out_of_bounds")
            name = owner_name(paths[file_id-1])
            if name not in TARGETS:
                raise ValueError("unexpected_external_provider_after_SHA_pin")
            per_owner[name] += 1
            outcome["external_original_slots"] += 1
            actual_slot = actual.get(slotname)
            if actual_slot is None:
                outcome["missing_export_material_texture_slots"] += 1
                continue
            actual_ptr,_ = b05._slot(actual_slot)
            if actual_ptr[0] == 0:
                outcome["original_external_became_null"] += 1
                continue
            kind = original_types[name].get(path_id)
            if kind is None:
                outcome["source_external_target_absent"] += 1
                continue
            if kind != "Texture2D":
                outcome["source_external_target_not_Texture2D"] += 1
                continue
            outcome["verified_original_Texture2D_class"] += 1
            expected = texture_rows.get((name,path_id))
            if expected is None:
                outcome["source_Texture2D_not_in_same_export_trace"] += 1
                continue
            outcome["external_target_same_export_trace_present"] += 1
            if expected == actual_ptr:
                outcome["external_exact_export_pointer_matches"] += 1
            else:
                outcome["external_wrong_export_pointer_targets"] += 1
    if outcome["external_original_slots"] != TOTAL or per_owner != Counter(TARGETS):
        raise ValueError("original_provider_external_slot_distribution_changed")
    errors = sum(outcome[k] for k in (
        "missing_export_material_texture_slots",
        "original_external_became_null",
        "source_external_target_absent",
        "source_external_target_not_Texture2D",
        "source_Texture2D_not_in_same_export_trace",
        "external_wrong_export_pointer_targets",
    ))
    result = {
        "schema_version":1,
        "experiment":"T3-25-external-Texture2D-same-export",
        "source_original_materials":len(original),
        "original_external_provider_count":len(TARGETS),
        "original_external_texture_slot_count":TOTAL,
        "authentic_external_source_owner_counts":dict(sorted(per_owner.items())),
        "same_instance_export_trace_checked":True,
        "source_target_Texture2D_verified":outcome["verified_original_Texture2D_class"],
        "exact_external_texture_targets_matched":outcome["external_exact_export_pointer_matches"],
        "unresolved_source_or_export_targets":errors,
        "wrong_external_texture_pointer_targets":outcome["external_wrong_export_pointer_targets"],
        "missing_target_trace_records":outcome["source_Texture2D_not_in_same_export_trace"],
        "missing_export_material_slots":outcome["missing_export_material_texture_slots"],
        "exported_external_slots_became_null":outcome["original_external_became_null"],
        "original_external_wrong_class_or_missing":outcome["source_external_target_absent"]+outcome["source_external_target_not_Texture2D"],
        "original_objects_private":True,
        "full_game_or_android_gpu_pixels_verified":False,
    }
    result["status"] = (
        "SCOPED_25_EXTERNAL_TEXTURE_MATCH"
        if not errors and outcome["external_exact_export_pointer_matches"]==TOTAL
        else "SCOPED_EXTERNAL_TEXTURE_MISMATCH_OR_INCOMPLETE")
    return result


def run(root: Path, project: Path, manifest: Path, w1path: Path, b02path: Path):
    import UnityPy
    if any(p.is_symlink() for p in (root, project, manifest, w1path, b02path)):
        raise ValueError("symlinked_original_or_export_trace")
    original = b05.original_texenvs(root, owner_names={OWNER})
    env = UnityPy.load(str(root/"Raft_Data"/OWNER))
    external = [x.path for x in env.file.externals]
    names = manifest_provider_basename_counts(manifest)
    inventory = previous.dependencies(original,external,names)
    if inventory["required_sha_pinned_public_provider_names"] != TARGETS:
        raise ValueError("external_owner_names_do_not_match_prior_real_source")
    target_types = verify_and_index_original_targets(root)
    w1 = json.loads(w1path.read_text(encoding="utf8"))
    b02 = json.loads(b02path.read_text(encoding="utf8"))
    exported = b05.exported_texenvs(project)
    return compare_external(original,external,target_types,w1,b02,exported)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","project","manifest","w1-trace","b02-trace","out"):
        ap.add_argument("--"+flag,required=True,type=Path)
    args=ap.parse_args(argv)
    if args.out.exists() or args.out.is_symlink() or args.out.resolve().is_relative_to(args.original.resolve()) or args.out.resolve().is_relative_to(args.project.resolve()):
        raise ValueError("unsafe_real_external_verification_report_location")
    stage="source_and_original_dependency"
    try:
        stage="real_original_source_and_same_export_comparison"
        report=run(args.original,args.project,args.manifest,args.w1_trace,args.b02_trace)
    except Exception as ex:
        # Source names/PathIDs, proprietary values and source paths from other
        # libraries must never be printed even during an unsuccessful run.
        report={"schema_version":1,"experiment":"T3-25-external-Texture2D-same-export",
                "status":"INCONCLUSIVE","phase":stage,"exception_type":type(ex).__name__,
                "external_texture_identity_verified":False,
                "full_game_or_android_gpu_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_EXTERNAL_TEXTURE_SOURCE_EXPORT "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SCOPED_25_EXTERNAL_TEXTURE_MATCH" else 2


if __name__=="__main__":
    raise SystemExit(main())
