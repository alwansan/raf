"""SHA-locked read-only bridge: original CanvasScaler MonoScript identity in UI scenes.

Only original Git objects, script PPtr metadata and native owner links are
inspected. It does NOT decode CanvasScaler custom serialized fields, instantiate
Unity UI, determine an Android aspect fault or publish game-owned class names.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.probe_a2_scene_ui_layout import (
    git_blob_sha, local_pptr, verified_scene, SCENE_BLOBS,
)

ORIGINAL_SCRIPTS_BLOB = "4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9"
SCRIPT_SOURCE = "globalgamemanagers.assets"
MAX_SCRIPTS = 10_000
MAX_BEHAVIOURS = 25_000
TARGET_CLASSES = {"CanvasScaler", "Settings", "GraphicsSettingsBox", "ControlsSettingsBox"}


def script_category(tree):
    if not isinstance(tree, dict):
        return "unknown"
    name = tree.get("m_ClassName")
    namespace = tree.get("m_Namespace")
    assembly = tree.get("m_AssemblyName")
    if not isinstance(name, str) or not isinstance(namespace, str) or not isinstance(assembly, str):
        return "unknown"
    if name == "CanvasScaler" and namespace == "UnityEngine.UI" and (
            assembly == "UnityEngine.UI" or assembly == "UnityEngine.UI.dll"):
        return "verified_unity_ui_canvas_scaler"
    if name == "CanvasScaler":
        return "canvas_scaler_name_only_not_verified"
    if name in TARGET_CLASSES:
        return "matching_original_game_class_unverified_" + name
    return "unrelated"


def script_registry(objects):
    registry, counts = {}, Counter()
    count = 0
    for obj in objects:
        if str(obj.type.name) != "MonoScript":
            continue
        count += 1
        if count > MAX_SCRIPTS:
            raise ValueError("Unbounded MonoScript inventory")
        try:
            tree = obj.read_typetree(check_read=False)
            category = script_category(tree)
        except Exception:
            category = "unknown"
        registry[int(obj.path_id)] = category
        counts[category] += 1
    counts["monoscript_objects"] = count
    return registry, dict(sorted(counts.items()))


def resolve_script(script_pptr, external_paths, local_registry, global_registry):
    if not isinstance(script_pptr, dict):
        return "unresolved_pointer"
    fid, pid = script_pptr.get("m_FileID"), script_pptr.get("m_PathID")
    if type(fid) is not int or type(pid) is not int or pid <= 0:
        return "unresolved_pointer"
    if fid == 0:
        return local_registry.get(pid, "unresolved_local_script")
    if fid < 1 or fid > len(external_paths):
        return "unresolved_external_script"
    path = external_paths[fid - 1]
    if not isinstance(path, str):
        return "unresolved_external_script"
    basename = path.replace("\\", "/").rsplit("/", 1)[-1]
    if basename != SCRIPT_SOURCE:
        return "unresolved_other_original_owner"
    return global_registry.get(pid, "unresolved_global_script")


def inspect_scene_file(owner_file, global_registry):
    externals = [x.path for x in owner_file.externals]
    local_registry, local_counts = script_registry(owner_file.objects.values())
    counters = Counter()
    canvas_owners, named_settings, behaviours = set(), set(), []
    for obj in owner_file.objects.values():
        kind = str(obj.type.name)
        if kind not in {"GameObject", "Canvas", "MonoBehaviour"}:
            continue
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            counters[kind + "_base_typetree_unavailable"] += 1
            continue
        if not isinstance(tree, dict):
            counters[kind + "_base_typetree_unavailable"] += 1
            continue
        if kind == "GameObject":
            name = tree.get("m_Name")
            if isinstance(name, str) and "settings" in name.casefold():
                named_settings.add(int(obj.path_id))
        elif kind == "Canvas":
            owner = local_pptr(tree.get("m_GameObject"))
            if owner:
                canvas_owners.add(owner)
        else:
            if len(behaviours) >= MAX_BEHAVIOURS:
                raise ValueError("Unbounded original scene MonoBehaviour inventory")
            behaviours.append((tree.get("m_Script"), local_pptr(tree.get("m_GameObject"))))
    for ptr, owner in behaviours:
        category = resolve_script(ptr, externals, local_registry, global_registry)
        counters[category] += 1
        if category == "verified_unity_ui_canvas_scaler":
            if owner in canvas_owners:
                counters["canvas_scaler_owner_is_native_canvas_owner"] += 1
            if owner in named_settings:
                counters["canvas_scaler_owner_named_settings"] += 1
        elif category == "matching_original_game_class_unverified_Settings" and owner in named_settings:
            counters["settings_class_script_owner_named_settings"] += 1
    return {
        "counts": dict(sorted(counters.items())),
        "original_script_owner_gitmismatch": False,
        "global_monoscript_identity_read": True,
        "settings_named_object_count": len(named_settings),
        "native_canvas_owner_count": len(canvas_owners),
        "monobehaviours_inspected": len(behaviours),
        "mono_script_externals_used": len(externals),
        "canvas_scaler_custom_fields_decoded": False,
        "original_settings_prefab_dependency_closure": False,
        "ui_aspect_cause_proven": False,
        "unity_or_android_executed": False,
    }


def audit(root, unity_loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original asset directory")
    verified_scene(root / SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB)
    for scene in ("level0", "level1"):
        verified_scene(root / scene, SCENE_BLOBS[scene])
    if unity_loader is None:
        import UnityPy
        unity_loader = lambda path: UnityPy.load(str(path))
    global_owner = unity_loader(root / SCRIPT_SOURCE).file
    scripts, script_counts = script_registry(global_owner.objects.values())
    scenes = {}
    for name in ("level0", "level1"):
        owner = unity_loader(root / name).file
        scenes[name] = inspect_scene_file(owner, scripts)
    return {
        "global_script_source_git_blob_sha1": ORIGINAL_SCRIPTS_BLOB,
        "original_script_categories": script_counts,
        "scene_results": scenes,
        "source_sha_pins_verified": True,
        "raw_monoscript_names_exported": False,
        "ui_scale_parameters_decoded": False,
        "actual_android_settings_ui_cause_proven": False,
        "original_lfs_hydrated": False,
        "unity_or_android_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    print("RAFT_A2_CANVAS_SCALER_MONOSCRIPT " + json.dumps(audit(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
