"""Read-only, exact-Git-blob source audit of original Raft scene UI structure.

Native serialized objects, not a reconstructed Settings prefab or runtime UI.
Print only generic numeric summaries and cryptographic fingerprints. No original
object names, script bodies, payloads, raw typetrees, or assets are exported.
"""
import argparse
from collections import Counter
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
INTERESTING = {"GameObject", "RectTransform", "Canvas", "MonoBehaviour"}
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
    named_settings = set()
    rect_records = []
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
        elif kind == "RectTransform":
            anchor_min = vector2(tree.get("m_AnchorMin"))
            anchor_max = vector2(tree.get("m_AnchorMax"))
            size = vector2(tree.get("m_SizeDelta"))
            if anchor_min is not None and anchor_max is not None and size is not None:
                counts["rect_geometry_decoded"] += 1
                if anchor_min == anchor_max:
                    counts["rect_fixed_anchor_geometry"] += 1
                else:
                    counts["rect_stretch_anchor_geometry"] += 1
                if any(abs(v) > 1e-7 for v in size):
                    counts["rect_nonzero_size_delta"] += 1
            else:
                counts["rect_geometry_unknown"] += 1
            rect_records.append(local_pptr(tree.get("m_GameObject")))
        elif kind == "MonoBehaviour":
            # A field shape is an evidence candidate only; absent script metadata
            # must not become a claim of confirmed CanvasScaler class identity.
            if SCALER_FIELDS.issubset(tree):
                counts["canvas_scaler_serialized_field_shape_candidates"] += 1
            else:
                counts["other_mono_shape_or_unknown"] += 1
    counts["rect_linked_to_settings_named_go"] = sum(
        owner in named_settings for owner in rect_records if owner is not None)
    return {
        "counts": dict(sorted(counts.items())),
        "decode_unknowns": dict(sorted(errors.items())),
        "source_gameobject_names_emitted": False,
        "canvas_scaler_script_identity_confirmed": False,
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
