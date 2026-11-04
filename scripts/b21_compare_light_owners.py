#!/usr/bin/env python3
"""B21 real original Light108 -> GameObject1 same-export ownership proof.

Never infer exported owner from a name or numeric pathID. The only identity
bridge is the exact SHA-locked B21 private same-process AssetRipper class1/108
trace; actual Unity YAML contains the native Light.m_GameObject local PPtr.
Reports only numerical aggregates and no original/game object identifiers.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re

from scripts.b21_scene_lightmap_links import PIN, verify_source
from scripts.b21_compare_export_lights import (
    ParityError, DOC, META_GUID, MAX_YAML, safe_root, yaml_pointer,
    exported_lights, original_lights, trace_key, trace_pointer, compare,
)

OWNER_FIELD = re.compile(r"(?m)^  m_GameObject:[ \t]*(\{[^}\r\n]+\})[ \t]*\r?$")


def source_owner_edges(root: Path) -> dict:
    import UnityPy
    root = safe_root(root)
    # Verify every selected owner; do not rely on a previous process' claims.
    for scene, expected in PIN.items():
        try:
            verify_source(root / scene, expected)
        except Exception as exc:
            raise ParityError("original_light_owner_sha_pin_failed") from exc
    result = {}
    for scene in ("level0", "level1"):
        objects = list(UnityPy.load(str(root / scene)).file.objects.values())
        gameobjects = {obj.path_id for obj in objects if obj.type.name == "GameObject"}
        if not gameobjects:
            raise ParityError("original_gameobject_table_missing")
        for obj in objects:
            if obj.type.name != "Light":
                continue
            tree = obj.read_typetree(check_read=False)
            owner = tree.get("m_GameObject")
            if not isinstance(owner, dict) or type(owner.get("m_FileID")) is not int or type(owner.get("m_PathID")) is not int:
                raise ParityError("invalid_original_light_gameobject_pptr")
            if owner["m_FileID"] != 0 or owner["m_PathID"] not in gameobjects:
                raise ParityError("original_light_owner_not_authentic_gameobject")
            key = (scene, obj.path_id)
            if key in result:
                raise ParityError("duplicate_original_light_owner_relation")
            result[key] = (scene, owner["m_PathID"])
    if len(result) != 2 or {k[0] for k in result} != {"level0", "level1"}:
        raise ParityError("unverified_original_light_owner_population")
    return result


def actual_owner_edges(project: Path) -> dict:
    root = safe_root(project)
    assets = safe_root(root / "Assets")
    rows = sorted(assets.rglob("*"))
    if any(p.is_symlink() for p in rows):
        raise ParityError("unsafe_exported_scene_link")
    result = {}
    scene_guids = set()
    for path in rows:
        if not path.is_file() or path.suffix not in {".unity", ".prefab", ".asset"}:
            continue
        if path.stat().st_size > MAX_YAML:
            raise ParityError("oversized_actual_light_owner_scene")
        with path.open("rb") as stream:
            if not stream.read(10).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
                continue
        text = path.read_text(encoding="utf-8-sig")
        headers = list(DOC.finditer(text))
        if not any(h[1] == "108" for h in headers):
            continue
        meta = Path(str(path) + ".meta")
        if meta.is_symlink() or not meta.is_file() or meta.stat().st_size > 65536:
            raise ParityError("actual_light_owner_scene_meta_missing")
        guids = META_GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if len(guids) != 1 or guids[0].lower() == "0" * 32:
            raise ParityError("actual_light_owner_scene_guid_invalid")
        guid = guids[0].lower()
        if guid in scene_guids:
            raise ParityError("actual_light_owner_scene_guid_duplicate")
        scene_guids.add(guid)
        anchors = [int(h[2]) for h in headers]
        if len(anchors) != len(set(anchors)) or any(x <= 0 for x in anchors):
            raise ParityError("actual_scene_anchor_invalid")
        gos = {int(h[2]) for h in headers if h[1] == "1"}
        for index, header in enumerate(headers):
            if header[1] != "108":
                continue
            end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
            body = text[header.end():end]
            matches = OWNER_FIELD.findall(body)
            if len(matches) != 1:
                raise ParityError("actual_light_owner_pointer_missing_or_duplicated")
            owner_id = yaml_pointer(matches[0])
            if owner_id not in gos:
                raise ParityError("actual_light_owner_target_is_not_gameobject")
            pointer = (guid, int(header[2]))
            if pointer in result:
                raise ParityError("duplicate_actual_light_owner_relation")
            result[pointer] = (guid, owner_id)
    return result


def check_owners(source_edges: dict, exported_edges: dict,
                 light_trace: dict, value_result: dict) -> dict:
    if not value_result.get("same_export_light_value_parity") or not value_result.get("private_same_instance_w1_trace_matched"):
        raise ParityError("original_light_values_or_export_instance_unproven")
    if not isinstance(light_trace, dict) or not isinstance(light_trace.get("objects"), list):
        raise ParityError("missing_same_instance_native_scene_trace")
    lights, gameobjects = {}, {}
    for row in light_trace["objects"]:
        if not isinstance(row, dict) or row.get("class_id") not in (1, 108):
            raise ParityError("unexpected_class_in_private_scene_trace")
        key = trace_key(row.get("source"))
        if key is None:
            continue
        if row["class_id"] == 108 and key in source_edges:
            if key in lights:
                raise ParityError("duplicate_traced_source_light")
            lights[key] = trace_pointer(row.get("export"))
        elif row["class_id"] == 1 and key in set(source_edges.values()):
            if key in gameobjects:
                raise ParityError("duplicate_traced_source_gameobject")
            gameobjects[key] = trace_pointer(row.get("export"))
    if set(lights) != set(source_edges) or set(gameobjects) != set(source_edges.values()):
        raise ParityError("missing_original_source_light_or_owner_in_export_trace")
    if len(set(gameobjects.values())) != len(gameobjects):
        raise ParityError("two_original_gameobjects_collapsed_to_same_export")
    missing, drift = 0, 0
    for light_source, owner_source in source_edges.items():
        actual = exported_edges.get(lights[light_source])
        if actual is None:
            missing += 1
        elif actual != gameobjects[owner_source]:
            drift += 1
    return {
        "original_light_owner_relations_authenticated": len(source_edges),
        "gameobject1_source_export_lineages_matched": len(gameobjects),
        "actual_unresolved_light_owner_relations": missing,
        "actual_misattached_original_lights": drift,
        "exact_same_export_light_gameobject_owner_parity": missing == 0 and drift == 0,
        "source_to_export_owner_link_proven": missing == 0 and drift == 0,
        "full_scene_hierarchy_or_prefab_runtime_verified": False,
        "shader_lighting_pixels_verified": False,
        "unity_or_android_runtime_executed": False,
        "source_or_export_mutated": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--light-trace", type=Path, required=True)
    p.add_argument("--w1-trace", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    for path in (args.light_trace, args.w1_trace):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
            raise ParityError("untrusted_private_light_trace")
    original = original_lights(args.original)
    actual = exported_lights(args.project)
    l = json.loads(args.light_trace.read_text())
    w = json.loads(args.w1_trace.read_text())
    values = compare(original, actual, l, w)
    source = source_owner_edges(args.original)
    target = actual_owner_edges(args.project)
    result = {"light_values": values, "light_owner": check_owners(source, target, l, values)}
    if args.report is not None:
        dest = Path(os.path.abspath(args.report))
        if dest.is_relative_to(safe_root(args.original)) or dest.is_relative_to(safe_root(args.project)) or dest.is_symlink() or dest in (args.light_trace, args.w1_trace):
            raise ParityError("unsafe_aggregate_owner_result")
        dest.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    print("RAFT_B21_REAL_SAME_EXPORT_LIGHT_OWNER " + json.dumps(result, sort_keys=True))
    return 0 if values["same_export_light_value_parity"] and result["light_owner"]["exact_same_export_light_gameobject_owner_parity"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
