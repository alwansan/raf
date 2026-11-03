"""Inspect SHA-pinned original Raft CanvasScaler raw *shape*, no invented values.

Extracts serializable UnityEngine.UI class field-order evidence from a privately
decompiled original managed DLL (ILSpy temporary output), and compares scene
MonoBehaviour record byte lengths without publishing original binary or code.
No raw-value decoder is asserted until the schema and base layout are proved.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_a2_scene_ui_layout import verified_scene, git_blob_sha, SCENE_BLOBS, local_pptr
from scripts.probe_a2_canvas_scaler_monoscript import (
    ORIGINAL_SCRIPTS_BLOB, SCRIPT_SOURCE, script_registry, resolve_script,
)
from scripts.probe_original_android_display_paths import mask_csharp_noncode

MANAGED_UI_GIT_BLOB = "7c31ff89d8525add38b34f218666f6c9d8db0a58"
MANAGED_UI = "UnityEngine.UI.dll"
MAX_MANAGED_BYTES = 2_000_000
MAX_SCALER_BYTES = 1024
FIELD_TYPES = {
    "m_UiScaleMode": "ScaleMode",
    "m_ReferencePixelsPerUnit": "float",
    "m_ScaleFactor": "float",
    "m_ReferenceResolution": "Vector2",
    "m_ScreenMatchMode": "ScreenMatchMode",
    "m_MatchWidthOrHeight": "float",
    "m_PhysicalUnit": "Unit",
    "m_FallbackScreenDPI": "float",
    "m_DefaultSpriteDPI": "float",
    "m_DynamicPixelsPerUnit": "float",
}

ALL_INSTANCE_M_FIELDS = re.compile(
    r"\b(?:private|public|protected|internal)\s+"
    r"(?:(?:readonly)\s+)*"
    r"(?P<type>[A-Za-z_]\w*)\s+(?P<field>m_[A-Za-z_]\w*)\s*(?=[;=])"
)
DECL = re.compile(
    r"\b(?:private|public|protected|internal)\s+"
    r"(?:(?:static|readonly)\s+)*"
    r"(?P<type>[A-Za-z_]\w*)\s+(?P<field>m_[A-Za-z_]\w*)\s*(?=[;=])"
)


def managed_sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe original managed UI source")
    if not 10000 <= path.stat().st_size <= MAX_MANAGED_BYTES:
        raise ValueError("Original managed UI size outside safety boundary")
    data = path.read_bytes()
    if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("Original managed UI is unresolved LFS")
    if git_blob_sha(data) != MANAGED_UI_GIT_BLOB:
        raise ValueError("Original UnityEngine.UI.dll Git object drift")
    return hashlib.sha256(data).hexdigest()


def managed_fields(text):
    if not isinstance(text, str) or len(text) > 400000:
        raise ValueError("Unexpected original CanvasScaler decompilation size")
    code = mask_csharp_noncode(text)
    collected = []
    for match in DECL.finditer(code):
        field = match.group("field")
        if field not in FIELD_TYPES:
            continue
        collected.append((field, match.group("type")))
    extras = [(m.group("field"), m.group("type"), m.start()) for m in ALL_INSTANCE_M_FIELDS.finditer(code)
              if m.group("field") not in FIELD_TYPES]
    # The UI library's editor-only preset flag may explain a four-byte tail,
    # but it is not a confirmed serialized field unless source attributes and
    # actual byte layout also corroborate it.
    preset = [(typ, pos) for name, typ, pos in extras if name == "m_PresetInfoIsWorld"]
    known_preset = len(preset) == 1 and preset[0][0] == "bool"
    def marker_before(pos):
        before = code[max(0, pos - 250):pos]
        last_boundary = max(before.rfind(";"), before.rfind("}"))
        return bool(re.search(r"\bSerializeField\b", before[last_boundary + 1:]))
    preset_serializefield_attribute_near = (known_preset and marker_before(preset[0][1]))
    other_extra_serialized_markers = sum(marker_before(pos) for n, _, pos in extras
                                         if n != "m_PresetInfoIsWorld")
    last_matched_pos = max((m.start() for m in DECL.finditer(code)
                            if m.group("field") in FIELD_TYPES), default=-1)
    preset_after_all_ten_known_fields = known_preset and preset[0][1] > last_matched_pos
    names = [a for a, _ in collected]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate original CanvasScaler serialized fields")
    types_mismatch = [name for name, typ in collected
                      if FIELD_TYPES.get(name) != typ]
    # Metadata is a *source field-order hint*, not an authenticated Unity
    # serialized TypeTree. Report unknown rather than promising byte offsets.
    return {
        "fields_matched": names,
        "additional_instance_m_field_declarations": len(extras),
        "additional_instance_m_field_name_sha256": sorted(hashlib.sha256(n.encode()).hexdigest() for n, _, _ in extras),
        "extra_preset_info_is_world_bool_declared": known_preset,
        "extra_preset_info_is_world_has_serializefield_near": preset_serializefield_attribute_near,
        "extra_preset_info_is_world_is_last": bool(preset_after_all_ten_known_fields),
        "other_extra_serializefield_markers": other_extra_serialized_markers,
        "field_count": len(names),
        "field_types_match_expected": not types_mismatch,
        "original_ilspy_class_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_order_is_verified_serialization_order": False,
        "original_unity_ui_serialized_typetree_verified": False,
        "serialized_base_header_length_verified": False,
    }


def inspect(root: Path, managed: Path, ilspy: Path, loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe scene directory")
    verified_scene(root / SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB)
    for name in ("level0", "level1"):
        verified_scene(root / name, SCENE_BLOBS[name])
    ui_sha256 = managed_sha(managed)
    if ilspy.is_symlink() or not ilspy.is_file() or ilspy.stat().st_size > 400000:
        raise ValueError("Missing or unsafe private ILSpy class source")
    fields = managed_fields(ilspy.read_text(encoding="utf-8-sig"))
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    global_file = loader(root / SCRIPT_SOURCE).file
    global_scripts, _ = script_registry(global_file.objects.values())
    scenes = {}
    for scene in ("level0", "level1"):
        sf = loader(root / scene).file
        local_scripts, _ = script_registry(sf.objects.values())
        externals = [x.path for x in sf.externals]
        canvas_owners = set()
        for obj in sf.objects.values():
            if str(obj.type.name) == "Canvas":
                tree = obj.read_typetree(check_read=False)
                owner = local_pptr(tree.get("m_GameObject"))
                if owner is not None:
                    canvas_owners.add(owner)
        sizes, read_errors = Counter(), Counter()
        total, verified_canvas_owner = 0, 0
        hashes = []
        for obj in sf.objects.values():
            if str(obj.type.name) != "MonoBehaviour":
                continue
            tree = obj.read_typetree(check_read=False)
            category = resolve_script(tree.get("m_Script"), externals,
                                      local_scripts, global_scripts)
            if category != "verified_unity_ui_canvas_scaler":
                continue
            raw = obj.get_raw_data()
            if len(raw) > MAX_SCALER_BYTES or len(raw) < 32:
                raise ValueError("Original CanvasScaler object length unsafe or anomalous")
            total += 1
            sizes[len(raw)] += 1
            hashes.append(hashlib.sha256(raw).hexdigest())
            if local_pptr(tree.get("m_GameObject")) in canvas_owners:
                verified_canvas_owner += 1
            if set(tree).intersection(FIELD_TYPES):
                read_errors["custom_fields_present_in_generic_typetree"] += 1
        if total == 0:
            raise ValueError("No authentic original CanvasScaler data in selected scene")
        if total != verified_canvas_owner:
            raise ValueError("Original CanvasScaler owner is not native Canvas")
        scenes[scene] = {
            "verified_scaler_monoscript_objects": total,
            "verified_native_canvas_owners": verified_canvas_owner,
            "serialized_record_size_histogram": dict(sorted(sizes.items())),
            "distinct_record_sha256_count": len(set(hashes)),
            "generic_tree_custom_field_presence": dict(sorted(read_errors.items())),
            "raw_source_value_excerpts_emitted": False,
        }
    return {
        "unity_ui_managed_sha256": ui_sha256,
        "source_ui_git_blob_sha1": MANAGED_UI_GIT_BLOB,
        "field_metadata": fields,
        "scenes": scenes,
        "authentic_values_decoded": False,
        "source_unity_serialized_typetree_verified": False,
        "android_settings_regression_root_cause_proven": False,
        "lfs_downloaded": False,
        "unity_or_android_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--managed", required=True, type=Path)
    p.add_argument("--ilspy", required=True, type=Path)
    a = p.parse_args()
    print("RAFT_A2_SCALER_RAW_SCHEMA " + json.dumps(
        inspect(a.source, a.managed, a.ilspy), sort_keys=True))


if __name__ == "__main__":
    main()
