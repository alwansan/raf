"""Read-only, exact-Git-blob source audit of original Raft scene UI structure.

Native serialized objects, not a reconstructed Settings prefab or runtime UI.
Print only generic numeric summaries and cryptographic fingerprints. No original
object names, script bodies, payloads, raw typetrees, or assets are exported.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

SCENE_BLOBS = {
    "level0": "2aec4377058baf72656a2ba0daea9aefc67fcb7e",
    "level1": "1944f11673108f8db2084906ff5899003c97fc4a",
    "level2": "a45e7c562ea249a08980198c8afca850f7b09778",
    "level3": "f394bff39030688193ba62c11acc819ad459a821",
    "level4": "03bcf6426b1152f0c4de0ecc16a90d4ae766cf1a",
    "level5": "99582def7e1cdc101504d2dbd2c687c6b9c327eb",
}
MAX_SCENE_BYTES = 12_000_000
MAX_OWNER_OBJECTS = 100_000
INTERESTING = {"GameObject", "Transform", "RectTransform", "Canvas", "MonoBehaviour"}
SCALER_FIELDS = frozenset({
    "m_UiScaleMode", "m_ReferenceResolution",
    "m_ScreenMatchMode", "m_MatchWidthOrHeight",
})


def git_blob_sha(raw):
    header = b"blob " + str(len(raw)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + raw).hexdigest()


def verified_scene(path, expected_git_sha):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe original scene input")
    size = path.stat().st_size
    if not 100 <= size <= MAX_SCENE_BYTES:
        raise ValueError("Original scene size outside budget")
    raw = path.read_bytes()
    if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("Original scene is an unresolved LFS pointer")
    if git_blob_sha(raw) != expected_git_sha:
        raise ValueError("Original scene Git blob fingerprint mismatch")
    return {"git_blob_sha1": expected_git_sha, "sha256": hashlib.sha256(raw).hexdigest(),
            "source_bytes": len(raw)}


def local_pptr(value):
    if not isinstance(value, dict):
        return None
    fid, pid = value.get("m_FileID"), value.get("m_PathID")
    if type(fid) is int and fid == 0 and type(pid) is int and pid > 0:
        return pid
    return None


def vector2(value):
    if not isinstance(value, dict):
        return None
    x, y = value.get("x"), value.get("y")
    if type(x) not in (float, int) or type(y) not in (float, int):
        return None
    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    return float(x), float(y)


def scan_objects(objects):
    objects = list(objects)
    if len(objects) > MAX_OWNER_OBJECTS:
        raise ValueError("Unbounded original scene object inventory")
    counts, errors = Counter(), Counter()
    named_settings, canvas_owners, rect_owner_gos = set(), set(), set()
    owner_to_transforms, transform_owners, transform_parents = defaultdict(list), {}, {}
    mono_base_fields = {
        "m_GameObject", "m_Enabled", "m_EditorHideFlags", "m_Script", "m_Name",
        "m_ObjectHideFlags", "m_CorrespondingSourceObject", "m_PrefabInstance",
        "m_PrefabAsset", "m_EditorClassIdentifier",
    }
    for obj in objects:
        kind = str(obj.type.name)
        counts["owner_objects"] += 1
        if kind not in INTERESTING:
            continue
        counts[kind + "_objects"] += 1
        try:
            tree = obj.read_typetree(check_read=False)
            if not isinstance(tree, dict):
                raise ValueError("Not a typed Unity tree")
        except Exception:
            errors[kind + "_typetree_unknown"] += 1
            continue
        counts[kind + "_typetree_decoded"] += 1
        if kind == "GameObject":
            name = tree.get("m_Name")
            if isinstance(name, str) and "settings" in name.casefold():
                counts["settings_name_gameobjects"] += 1
                named_settings.add(int(obj.path_id))
        elif kind == "Canvas":
            owner = local_pptr(tree.get("m_GameObject"))
            if owner is None:
                counts["canvas_owner_unknown"] += 1
            else:
                canvas_owners.add(owner)
        elif kind in {"Transform", "RectTransform"}:
            ident = int(obj.path_id)
            owner = local_pptr(tree.get("m_GameObject"))
            if owner is not None:
                owner_to_transforms[owner].append(ident)
                transform_owners[ident] = owner
            parent = tree.get("m_Father")
            if (isinstance(parent, dict) and type(parent.get("m_FileID")) is int
                    and type(parent.get("m_PathID")) is int
                    and parent["m_FileID"] == 0 and parent["m_PathID"] == 0):
                transform_parents[ident] = None
            else:
                transform_parents[ident] = local_pptr(parent) or "unknown"
            if kind == "RectTransform":
                if owner is not None:
                    rect_owner_gos.add(owner)
                amin = vector2(tree.get("m_AnchorMin"))
                amax = vector2(tree.get("m_AnchorMax"))
                size = vector2(tree.get("m_SizeDelta"))
                if amin is not None and amax is not None and size is not None:
                    counts["rect_geometry_decoded"] += 1
                    counts["rect_fixed_anchor_geometry" if amin == amax
                           else "rect_stretch_anchor_geometry"] += 1
                    if any(abs(v) > 1e-7 for v in size):
                        counts["rect_nonzero_size_delta"] += 1
                else:
                    counts["rect_geometry_unknown"] += 1
        elif kind == "MonoBehaviour":
            # UnityPy often decodes *only the MonoBehaviour base fields* when
            # original MonoScript field schema is unavailable. Never claim
            # CanvasScaler absent because that generic tree has no custom fields.
            if SCALER_FIELDS.issubset(tree):
                counts["canvas_scaler_serialized_field_shape_candidates"] += 1
            elif set(tree).issubset(mono_base_fields):
                counts["mono_base_fields_only_no_custom_schema"] += 1
            else:
                counts["mono_custom_fields_without_scaler_shape"] += 1
    counts["rect_linked_to_settings_named_go"] = sum(
        len(owner_to_transforms.get(go, [])) == 1
        and owner_to_transforms[go][0] in transform_parents
        and go in rect_owner_gos
        for go in named_settings)
    for go in named_settings:
        roots = owner_to_transforms.get(go, [])
        if len(roots) != 1:
            counts["settings_canvas_ancestry_unknown"] += 1
            continue
        seen, current, in_canvas = set(), roots[0], False
        ancestry_unknown = False
        for _ in range(256):
            if current in seen or current not in transform_parents:
                ancestry_unknown = True
                break
            seen.add(current)
            owner = transform_owners.get(current)
            if owner is None:
                ancestry_unknown = True
                break
            if owner in canvas_owners:
                in_canvas = True
                break
            parent = transform_parents[current]
            if parent is None:
                break
            if parent == "unknown":
                ancestry_unknown = True
                break
            current = parent
        else:
            ancestry_unknown = True
        counts["settings_named_go_under_native_canvas" if in_canvas else
               "settings_canvas_ancestry_unknown" if ancestry_unknown else
               "settings_named_go_without_native_canvas_ancestor_in_this_scene"] += 1
    return {
        "counts": dict(sorted(counts.items())),
        "decode_unknowns": dict(sorted(errors.items())),
        "source_gameobject_names_emitted": False,
        "canvas_scaler_script_identity_confirmed": False,
        "monobehaviour_base_typetree_is_not_custom_schema": True,
        "nondecoded_mono_does_not_prove_absence": True,
        "settings_prefab_completeness_confirmed": False,
        "settings_stretch_cause_proven": False,
        "unity_or_android_executed": False,
    }


def audit(root, expected=SCENE_BLOBS, loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original scene directory")
    if len(expected) != 6 or set(expected) != set(SCENE_BLOBS):
        raise ValueError("Original six-scene boundary changed")
    validated = {}
    for name, oid in sorted(expected.items()):
        if name not in SCENE_BLOBS or len(oid) != 40:
            raise ValueError("Invalid scene pin")
        validated[name] = verified_scene(root / name, oid)
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    scenes = {}
    for name in sorted(validated):
        environment = loader(root / name)
        owned = list(environment.file.objects.values())
        parsed = scan_objects(owned)
        scenes[name] = {**validated[name], **parsed}
        del owned, environment
    return {
        "scenes": scenes,
        "selected_scene_count": len(scenes),
        "original_git_blobs_verified": True,
        "original_lfs_downloaded": False,
        "scope": "level0..level5 only: no LFS, no serialized prefab dependency closure",
        "scene_to_settings_ui_reachability_proven": False,
        "settings_stretch_cause_proven": False,
        "gameplay_or_original_assets_modified": False,
        "unity_or_android_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    args = p.parse_args()
    print("RAFT_A2_SCENE_UI_LAYOUT " + json.dumps(audit(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
