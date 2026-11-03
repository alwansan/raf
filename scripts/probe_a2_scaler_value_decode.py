"""Strict source-locked CanvasScaler value decoder for original Raft scene MonoBehaviours.

Needs exact SHA-matched original UnityEngine.UI.dll decompilation field ordering,
exact 80-byte records, and verified typed Unity MonoBehaviour *base* header
before interpreting any custom bytes. Never recovers or publishes game assets,
original C# bodies, object labels or Unity prefabs. Source-only, NOT an aspect fix.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import struct

from scripts.probe_a2_scaler_raw_shapes import (
    FIELD_TYPES, managed_fields, managed_sha, MAX_SCALER_BYTES,
)
from scripts.probe_a2_scene_ui_layout import SCENE_BLOBS, verified_scene, local_pptr
from scripts.probe_a2_canvas_scaler_monoscript import (
    ORIGINAL_SCRIPTS_BLOB, SCRIPT_SOURCE, script_registry, resolve_script,
)

CUSTOM = struct.Struct("<iffffififff")
BASE_BYTES = 36
RECORD_BYTES = BASE_BYTES + CUSTOM.size
EXPECTED_ORDER = tuple(FIELD_TYPES)
MAX_BEHAVIOURS = 25_000


def verified_field_order(meta):
    if meta.get("fields_matched") != list(EXPECTED_ORDER) or (
            not meta.get("field_types_match_expected")):
        raise ValueError("Original CanvasScaler private serialized field metadata drift")
    # Source metadata order is a prerequisite only. Alignment/offsets additionally
    # require exact comparison to the built-in MonoBehaviour base tree.
    return True


def decode_record(raw, tree):
    if not isinstance(raw, bytes) or len(raw) != RECORD_BYTES:
        raise ValueError("Original CanvasScaler record length differs from pinned layout")
    if not isinstance(tree, dict):
        raise ValueError("Original typed MonoBehaviour base fields unavailable")
    go, script = tree.get("m_GameObject"), tree.get("m_Script")
    if not isinstance(go, dict) or not isinstance(script, dict):
        raise ValueError("Cannot verify original base PPtr fields")
    def pptr(offset, expected, role):
        if type(expected.get("m_FileID")) is not int or type(expected.get("m_PathID")) is not int:
            raise ValueError("Original base PPtr field type unknown")
        parsed = struct.unpack_from("<iq", raw, offset)
        if parsed != (expected["m_FileID"], expected["m_PathID"]):
            candidates64 = [n for n in range(0, 45)
                            if struct.unpack_from("<iq", raw, n)
                            == (expected["m_FileID"], expected["m_PathID"])]
            candidates32 = [n for n in range(0, 45)
                            if (-(2**31) <= expected["m_PathID"] < 2**31
                                and struct.unpack_from("<ii", raw, n)
                                == (expected["m_FileID"], expected["m_PathID"]))]
            raise ValueError(
                "Original base PPtr byte layout disagrees with native TypeTree"
                + " role=" + role
                + " candidate_offsets_i32i64=" + repr(candidates64)
                + " candidate_offsets_i32i32=" + repr(candidates32))
    pptr(0, go, "gameobject")
    pptr(16, script, "script")
    enabled = tree.get("m_Enabled")
    flags = tree.get("m_EditorHideFlags", 0)
    name = tree.get("m_Name")
    identifier = tree.get("m_EditorClassIdentifier", "")
    if type(enabled) not in (int, bool) or int(enabled) not in (0, 1):
        raise ValueError("Original enabled field unknown")
    if raw[12] != int(enabled) or raw[14:16] != b"\x00\x00":
        raise ValueError("Original enabled/alignment bytes mismatch")
    # Native Unity MonoBehaviour uses one byte for EditorHideFlags in this
    # authenticated source, followed by two pad bytes before m_Script PPtr.
    if type(flags) not in (int, bool) or not 0 <= int(flags) <= 255 or raw[13] != int(flags):
        raise ValueError("Original editor flags byte layout mismatch")
    if not isinstance(name, str) or name:
        raise ValueError("Original MonoBehaviour name is non-empty or unresolved")
    if not isinstance(identifier, str) or identifier:
        raise ValueError("Original MonoBehaviour editor identifier unexpected")
    if struct.unpack_from("<i", raw, 28)[0] != 0 or struct.unpack_from("<i", raw, 32)[0] != 0:
        raise ValueError("Original MonoBehaviour base name/editor string lengths mismatch" +
                         " int28=" + str(struct.unpack_from("<i", raw, 28)[0]) +
                         " int32=" + str(struct.unpack_from("<i", raw, 32)[0]) +
                         " typed_editor_class_identifier_present=" + str("m_EditorClassIdentifier" in tree) +
                         " typed_editor_flags_present=" + str("m_EditorHideFlags" in tree))
    (ui_mode, ref_ppu, scale_factor, width, height, match_mode,
     match_width, physical_unit, fallback_dpi, default_sprite_dpi, dynamic_ppu) = CUSTOM.unpack_from(raw, BASE_BYTES)
    numeric = (ref_ppu, scale_factor, width, height, match_width,
               fallback_dpi, default_sprite_dpi, dynamic_ppu)
    if not all(math.isfinite(v) for v in numeric):
        raise ValueError("Original CanvasScaler has non-finite numeric custom field")
    if not (0 <= ui_mode <= 2 and 0 <= match_mode <= 2 and 0 <= physical_unit <= 4):
        raise ValueError("Original CanvasScaler enum out of valid range")
    if not (0 < ref_ppu <= 2000 and 0 < scale_factor <= 100 and
            0 < width <= 65536 and 0 < height <= 65536 and
            0 <= match_width <= 1 and 0 < fallback_dpi <= 2000 and
            0 < default_sprite_dpi <= 2000 and 0 < dynamic_ppu <= 2000):
        raise ValueError("Original CanvasScaler float outside bounded UI contract")
    # Return only aggregate presentation categories, not raw bytes or any name.
    return {
        "ui_scale_mode": ui_mode,
        "reference_resolution": [width, height],
        "screen_match_mode": match_mode,
        "match_width_or_height": match_width,
        "reference_pixels_per_unit": ref_ppu,
        "scale_factor": scale_factor,
        "physical_unit": physical_unit,
        "fallback_screen_dpi": fallback_dpi,
        "default_sprite_dpi": default_sprite_dpi,
        "dynamic_pixels_per_unit": dynamic_ppu,
    }


def audit(root, managed, ilspy, loader=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original scene root")
    verified_scene(root / SCRIPT_SOURCE, ORIGINAL_SCRIPTS_BLOB)
    for name in ("level0", "level1"):
        verified_scene(root / name, SCENE_BLOBS[name])
    managed_hash = managed_sha(managed)
    if ilspy.is_symlink() or not ilspy.is_file() or ilspy.stat().st_size > 400000:
        raise ValueError("Unsafe private metadata input")
    meta = managed_fields(ilspy.read_text(encoding="utf-8-sig"))
    verified_field_order(meta)
    if loader is None:
        import UnityPy
        loader = lambda p: UnityPy.load(str(p))
    globals_file = loader(root / SCRIPT_SOURCE).file
    global_scripts, _ = script_registry(globals_file.objects.values())
    results = {}
    for name in ("level0", "level1"):
        owner = loader(root / name).file
        local_scripts, _ = script_registry(owner.objects.values())
        externals = [x.path for x in owner.externals]
        canvas_owner = set()
        for obj in owner.objects.values():
            if str(obj.type.name) == "Canvas":
                parent = local_pptr(obj.read_typetree(check_read=False).get("m_GameObject"))
                if parent:
                    canvas_owner.add(parent)
        profile_counts = Counter()
        hit = 0
        for obj in owner.objects.values():
            if str(obj.type.name) != "MonoBehaviour":
                continue
            base = obj.read_typetree(check_read=False)
            if resolve_script(base.get("m_Script"), externals, local_scripts,
                              global_scripts) != "verified_unity_ui_canvas_scaler":
                continue
            if hit >= MAX_BEHAVIOURS:
                raise ValueError("Unbounded source CanvasScaler enumeration")
            if local_pptr(base.get("m_GameObject")) not in canvas_owner:
                raise ValueError("Original scaler owner not attached to native Canvas")
            fields = decode_record(obj.get_raw_data(), base)
            profile_counts[json.dumps(fields, sort_keys=True)] += 1
            hit += 1
        if hit != (4 if name == "level0" else 13):
            raise ValueError("Original source CanvasScaler inventory unexpectedly changed")
        results[name] = {
            "scalers_decoded": hit,
            "profiles": [{"config": json.loads(p), "count": count}
                         for p, count in sorted(profile_counts.items())],
        }
    return {
        "original_managed_ui_sha256": managed_hash,
        "original_decompiled_canvas_scaler_sha256": meta["original_ilspy_class_sha256"],
        "base_header_bytes_independently_matched_to_typed_original": BASE_BYTES,
        "custom_fields_bytes": CUSTOM.size,
        "original_serialized_field_order_correlated_with_metadata_and_bytes": True,
        "authentic_original_scaler_custom_values_structurally_decoded": True,
        "scenes": results,
        "android_settings_page_link_proven": False,
        "android_aspect_regression_cause_proven": False,
        "original_assets_modified": False,
        "lfs_downloaded": False,
        "unity_or_android_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--managed", required=True, type=Path)
    p.add_argument("--ilspy", required=True, type=Path)
    a = p.parse_args()
    print("RAFT_A2_SCALER_VALUES " + json.dumps(audit(a.source, a.managed, a.ilspy), sort_keys=True))


if __name__ == "__main__":
    main()
