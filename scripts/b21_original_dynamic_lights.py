#!/usr/bin/env python3
"""B21 read-only typed Unity Light-component provenance on six SHA-pinned originals.

Light is native class ID 108; original values are not emitted to logs/artifacts.
Without a same-instance export mapping this identifies source lighting facts only,
not whether Android retained or rendered those lights.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from scripts.b21_scene_lightmap_links import PIN, SourceError, verify_source

MAX_OBJECTS = 100_000
MAX_LIGHTS = 20_000
MAX_LIGHT_COMPONENT_FIELDS = 200


def finite_number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def classification(value: object, *, allow_negative: bool = False) -> str:
    if not finite_number(value):
        return "unknown_or_nonfinite"
    if not allow_negative and value < 0:
        return "negative_unverified"
    if value == 0:
        return "zero"
    return "positive" if value > 0 else "negative"


def color_classification(value: object) -> str:
    if not isinstance(value, dict) or not all(key in value for key in ("r", "g", "b", "a")):
        return "unknown_color_schema"
    components = [value[key] for key in ("r", "g", "b", "a")]
    if not all(finite_number(x) for x in components):
        return "nonfinite_color"
    if any(x < 0 for x in components):
        return "negative_components_unverified"
    if all(x == 0 for x in components[:3]):
        return "black_rgb"
    if all(x == 1 for x in components[:3]):
        return "unit_white_rgb"
    return "finite_other_rgb"


def local_owner_status(value: object, local_ids: set[int]) -> str:
    if not isinstance(value, dict):
        return "owner_schema_unknown"
    fid, pid = value.get("m_FileID"), value.get("m_PathID")
    if type(fid) is not int or type(pid) is not int or pid <= 0 or fid < 0:
        return "owner_pointer_unknown"
    if fid != 0:
        return "external_owner_not_verified"
    return "local_owner_present" if pid in local_ids else "local_owner_missing"


def audit_lights(objects: list) -> dict:
    if len(objects) > MAX_OBJECTS:
        raise SourceError("lighting_scene_objects_over_budget")
    ids = []
    for obj in objects:
        path_id = getattr(obj, "path_id", None)
        if type(path_id) is not int or path_id <= 0:
            raise SourceError("lighting_invalid_object_id")
        ids.append(path_id)
    if len(ids) != len(set(ids)):
        raise SourceError("lighting_duplicate_object_id")
    local_ids = set(ids)
    count = Counter()
    light_count = 0
    for obj in objects:
        if str(obj.type.name) != "Light":
            continue
        light_count += 1
        if light_count > MAX_LIGHTS:
            raise SourceError("light_components_over_budget")
        count["original_light_component_objects"] += 1
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            count["original_light_typetree_unknown"] += 1
            continue
        if not isinstance(tree, dict) or len(tree) > MAX_LIGHT_COMPONENT_FIELDS:
            count["original_light_typetree_unknown"] += 1
            continue
        count["original_light_typetree_decoded"] += 1
        count["original_light_" + local_owner_status(tree.get("m_GameObject"), local_ids)] += 1
        enabled = tree.get("m_Enabled")
        count["original_light_enabled_" + ("yes" if enabled == 1 and type(enabled) is int
                else "no" if enabled == 0 and type(enabled) is int else "unknown")] += 1
        count["original_light_color_" + color_classification(tree.get("m_Color"))] += 1
        count["original_light_intensity_" + classification(tree.get("m_Intensity"))] += 1
        count["original_light_range_" + classification(tree.get("m_Range"))] += 1
        light_type = tree.get("m_Type")
        if type(light_type) is int and 0 <= light_type <= 16:
            count["original_light_type_serialized_numeric"] += 1
        else:
            count["original_light_type_unknown"] += 1
    return {
        "counts": dict(sorted(count.items())),
        "native_light_component_semantics_read_only": True,
        "source_light_values_emitted": False,
        "same_instance_export_mapping_verified": False,
        "lighting_pixel_equivalence_proven": False,
        "scene_or_shader_mutated": False,
        "android_or_unity_render_executed": False,
    }


def run(root: Path, loader=None) -> dict:
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise SourceError("unsafe_lighting_source_root")
    for scene, expected in PIN.items():
        try:
            verify_source(root / scene, expected)
        except SourceError as exc:
            raise SourceError(f"{scene}: {exc}") from exc
    if loader is None:
        import UnityPy
        loader = lambda path: UnityPy.load(str(path))
    scenes = {}
    for scene in PIN:
        env = loader(root / scene)
        objects = list(env.file.objects.values())
        scenes[scene] = audit_lights(objects)
        scenes[scene]["source_bytes"] = PIN[scene][0]
        scenes[scene]["original_sha256"] = PIN[scene][1]
        del env, objects
    return {
        "original_pin": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        "six_original_scenes_sha256_verified": True,
        "real_scene_count": len(scenes),
        "all_40_scenes_examined": False,
        "scenes": scenes,
        "actual_export_checked": False,
        "gameplay_modified": False,
        "phone_graphics_verified": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    result = run(args.source)
    rendered = json.dumps(result, sort_keys=True)
    print("RAFT_B21_ORIGINAL_DYNAMIC_LIGHTS " + rendered)
    if args.report is not None:
        target = args.report.absolute()
        if target.is_relative_to(args.source.absolute()):
            raise SourceError("report_inside_original_source_refused")
        target.write_text(rendered + "\n", encoding="utf8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
