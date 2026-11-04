#!/usr/bin/env python3
"""B21 original Light108 -> same-instance Unity export value parity (read only).

Requires SHA256-authenticated ZIP2 scenes, TWO private trace files from ONE
AssetRipper invocation (W1 + B21 optional class108), and actual Unity YAML.
Never infer an exported GUID or Light object from a source name/pathID alone.
Report contains only safe counts. It does not establish rendering equivalence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import re

from scripts.b21_scene_lightmap_links import PIN, verify_source

SOURCE_PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
GUID_RE = re.compile(r"^[0-9a-f]{32}$")
META_GUID = re.compile(r"(?m)^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$")
DOC = re.compile(r"(?m)^--- !u!(\d+) &(-?\d+)(?: stripped)?[ \t]*\r?$")
FIELD = re.compile(r"^  (m_GameObject|m_Color|m_Intensity|m_Range|m_Type|m_Enabled):[ \t]*(.*?)\s*$")
FLOAT = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\Z")
MAX_YAML = 128 * 1024 * 1024
MAX_LIGHTS = 20_000
CHANNELS = ("r", "g", "b", "a")


class ParityError(ValueError):
    pass


def safe_root(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_dir():
        raise ParityError("missing_or_symlinked_root")
    return path


def number(raw: object) -> float:
    if isinstance(raw, str):
        if not FLOAT.fullmatch(raw.strip()):
            raise ParityError("invalid_numeric_yaml")
        value = float(raw)
    elif type(raw) in (int, float):
        value = float(raw)
    else:
        raise ParityError("invalid_numeric_source")
    if not math.isfinite(value):
        raise ParityError("nonfinite_light_field")
    return value


def fields_from_tree(tree: object) -> tuple:
    if not isinstance(tree, dict):
        raise ParityError("invalid_original_light_typetree")
    enabled, kind = tree.get("m_Enabled"), tree.get("m_Type")
    if type(enabled) is not int or enabled not in (0, 1) or type(kind) is not int or not 0 <= kind <= 16:
        raise ParityError("invalid_original_light_flags")
    rgba = tree.get("m_Color")
    if not isinstance(rgba, dict) or any(x not in rgba for x in CHANNELS):
        raise ParityError("invalid_original_light_color")
    owner = tree.get("m_GameObject")
    if not isinstance(owner, dict) or type(owner.get("m_FileID")) is not int or type(owner.get("m_PathID")) is not int:
        raise ParityError("invalid_original_light_owner")
    if owner["m_FileID"] != 0 or owner["m_PathID"] <= 0:
        raise ParityError("original_light_owner_not_local")
    return (enabled, kind, tuple(number(rgba[x]) for x in CHANNELS),
            number(tree.get("m_Intensity")), number(tree.get("m_Range")))


def original_lights(source_root: Path) -> dict:
    import UnityPy
    root = safe_root(source_root)
    for name, pin in PIN.items():
        try:
            verify_source(root / name, pin)
        except Exception as exc:
            raise ParityError("original_scene_pin_failed") from exc
    selected = {}
    for scene in PIN:
        env = UnityPy.load(str(root / scene))
        items = list(env.file.objects.values())
        ids = {obj.path_id for obj in items}
        if len(items) != len(ids):
            raise ParityError("duplicate_original_scene_object_id")
        for obj in items:
            if obj.type.name != "Light":
                continue
            key = (scene, obj.path_id)
            if key in selected or len(selected) >= MAX_LIGHTS:
                raise ParityError("duplicate_or_oversize_original_light")
            tree = obj.read_typetree(check_read=False)
            if tree["m_GameObject"]["m_PathID"] not in ids:
                raise ParityError("original_light_owner_absent")
            selected[key] = fields_from_tree(tree)
    # The authenticated six-scene baseline has one Light in level0 and level1.
    if len(selected) != 2 or {key[0] for key in selected} != {"level0", "level1"}:
        raise ParityError("unverified_original_light_population")
    return selected


def yaml_pointer(value: str) -> int:
    match = re.fullmatch(r"\{fileID:[ \t]*(-?\d+)\}", value.strip())
    if not match or int(match[1]) <= 0:
        raise ParityError("missing_or_nonlocal_exported_light_owner")
    return int(match[1])


def yaml_rgba(raw: str) -> tuple:
    if not raw.startswith("{") or not raw.endswith("}"):
        raise ParityError("unexpected_exported_light_color_shape")
    chunks = [x.strip().split(":", 1) for x in raw[1:-1].split(",")]
    if len(chunks) != 4 or any(len(x) != 2 for x in chunks):
        raise ParityError("malformed_exported_light_color")
    fields = {}
    for key, value in chunks:
        if key in fields:
            raise ParityError("duplicate_exported_light_color_channel")
        fields[key] = number(value.strip())
    if set(fields) != set(CHANNELS):
        raise ParityError("exported_light_color_channels_changed")
    return tuple(fields[x] for x in CHANNELS)


def exported_light_body(body: str, local_objects: set[int]) -> tuple:
    if not body.lstrip().startswith("Light:\n"):
        raise ParityError("wrong_exported_native_light_type")
    fields = {}
    for line in body.splitlines():
        match = FIELD.fullmatch(line)
        if not match:
            continue
        name, value = match.groups()
        if name in fields:
            raise ParityError("duplicate_exported_light_field")
        fields[name] = value.strip()
    expected = {"m_GameObject", "m_Enabled", "m_Type", "m_Color", "m_Intensity", "m_Range"}
    if set(fields) != expected:
        raise ParityError("missing_exported_light_fields")
    owner = yaml_pointer(fields["m_GameObject"])
    if owner not in local_objects:
        raise ParityError("exported_light_owner_object_missing")
    if fields["m_Enabled"] not in ("0", "1") or not re.fullmatch(r"\d+", fields["m_Type"]):
        raise ParityError("invalid_exported_light_enum")
    kind = int(fields["m_Type"])
    if kind > 16:
        raise ParityError("unexpected_exported_light_type")
    return (int(fields["m_Enabled"]), kind, yaml_rgba(fields["m_Color"]),
            number(fields["m_Intensity"]), number(fields["m_Range"]))


def exported_lights(project: Path) -> dict:
    root = safe_root(project)
    assets = safe_root(root / "Assets")
    entries = sorted(assets.rglob("*"))
    if any(p.is_symlink() for p in entries):
        raise ParityError("symlink_inside_export")
    lights = {}
    for path in entries:
        if not path.is_file() or path.suffix not in {".unity", ".prefab", ".asset"}:
            continue
        if path.stat().st_size > MAX_YAML:
            raise ParityError("oversize_exported_scene")
        with path.open("rb") as stream:
            if not stream.read(10).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
                continue
        text = path.read_text(encoding="utf-8-sig")
        headers = list(DOC.finditer(text))
        if not any(h[1] == "108" for h in headers):
            continue
        meta = Path(str(path) + ".meta")
        if meta.is_symlink() or not meta.is_file() or meta.stat().st_size > 65536:
            raise ParityError("missing_export_light_owner_meta")
        guids = META_GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if len(guids) != 1 or guids[0].lower() == "0" * 32:
            raise ParityError("invalid_export_light_owner_guid")
        guid = guids[0].lower()
        anchors = [int(h[2]) for h in headers]
        if any(x <= 0 for x in anchors) or len(set(anchors)) != len(anchors):
            raise ParityError("duplicate_or_bad_export_yaml_anchor")
        gameobjects = {int(h[2]) for h in headers if h[1] == "1"}
        for i, header in enumerate(headers):
            if header[1] != "108":
                continue
            key = (guid, int(header[2]))
            if key in lights or len(lights) >= MAX_LIGHTS:
                raise ParityError("duplicate_or_oversize_exported_lights")
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            lights[key] = exported_light_body(text[header.end():end], gameobjects)
    return lights


def trace_key(row: object):
    if not isinstance(row, dict) or set(row) != {"owner", "path_id"}:
        raise ParityError("invalid_private_light_source_identity")
    scene, pid = row["owner"], row["path_id"]
    if not isinstance(scene, str) or type(pid) is not int or pid <= 0:
        raise ParityError("malformed_private_light_source_identity")
    if scene in PIN:
        return scene, pid
    return None  # Another original scene: outside the six-source scope.


def trace_pointer(row: object):
    if not isinstance(row, dict) or set(row) != {"file_id", "guid", "type"}:
        raise ParityError("invalid_private_light_export_pointer")
    fid, guid, kind = row["file_id"], row["guid"], row["type"]
    if type(fid) is not int or fid <= 0 or not isinstance(guid, str) or not GUID_RE.fullmatch(guid.lower()) or type(kind) is not int or kind not in (2, 3):
        raise ParityError("unsupported_export_light_pointer")
    if guid == "0" * 32:
        raise ParityError("export_scene_guid_unavailable")
    return guid.lower(), fid


def compare(original: dict, actual: dict, b21trace: dict, w1trace: dict) -> dict:
    if not isinstance(b21trace, dict) or b21trace.get("schema_version") != 1 or not isinstance(b21trace.get("objects"), list):
        raise ParityError("invalid_private_light_trace")
    instance = b21trace.get("export_instance")
    if not isinstance(instance, str) or not GUID_RE.fullmatch(instance):
        raise ParityError("invalid_private_export_instance")
    if not isinstance(w1trace, dict) or w1trace.get("schema_version") != 1 or w1trace.get("export_instance") != instance:
        raise ParityError("not_same_export_instance_as_w1")
    if not isinstance(w1trace.get("objects"), list) or not any(isinstance(x, dict) and x.get("class_id") in (21, 48) for x in w1trace["objects"]):
        raise ParityError("missing_real_w1_export_evidence")
    expected = {}
    covered = set()
    ignored = 0
    for row in b21trace["objects"]:
        if not isinstance(row, dict) or row.get("class_id") not in (1, 108):
            raise ParityError("unexpected_private_light_trace_class")
        if row["class_id"] == 1:
            # Optional GameObject lineage is checked separately; never count it as a Light.
            continue
        key = trace_key(row.get("source"))
        if key is None:
            ignored += 1
            continue
        if key not in original or key in covered:
            raise ParityError("missing_or_duplicate_original_light_identity")
        covered.add(key)
        target = trace_pointer(row.get("export"))
        if target in expected:
            raise ParityError("distinct_original_lights_collapsed_in_export")
        expected[target] = original[key]
    if covered != set(original):
        raise ParityError("original_lights_absent_from_same_export_trace")
    if not expected or expected.keys() - actual.keys():
        raise ParityError("traced_original_light_not_found_in_actual_export_yaml")
    counts = Counter()
    for pointer, native in expected.items():
        exported = actual[pointer]
        counts["matched_original_export_light_objects"] += 1
        if native[0] != exported[0]:
            counts["changed_enabled_flag"] += 1
        if native[1] != exported[1]:
            counts["changed_light_type"] += 1
        if any(not math.isclose(x, y, rel_tol=2e-6, abs_tol=2e-5) for x, y in zip(native[2], exported[2])):
            counts["changed_color_rgba"] += 1
        if not math.isclose(native[3], exported[3], rel_tol=2e-6, abs_tol=2e-5):
            counts["changed_intensity"] += 1
        if not math.isclose(native[4], exported[4], rel_tol=2e-6, abs_tol=2e-5):
            counts["changed_range"] += 1
    mismatches = {k: v for k, v in counts.items() if k.startswith("changed_") and v}
    return {
        "source_original_light_count": len(original),
        "selected_lights_with_private_export_identity": len(covered),
        "matched_exported_light_values": counts["matched_original_export_light_objects"],
        "other_scene_lights_out_of_scope": ignored,
        "value_mismatches": mismatches,
        "same_export_light_value_parity": not bool(mismatches),
        "source_original_scenes_sha_verified": True,
        "private_same_instance_w1_trace_matched": True,
        "gameobject_identity_across_export_verified": False,
        "original_light_visual_equivalence_proven": False,
        "unity_or_android_rendering_executed": False,
        "assets_changed": 0,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", type=Path, required=True, help="SHA-pinned ZIP2 Raft_Data")
    p.add_argument("--project", type=Path, required=True, help="Actual SAME AssetRipper Unity export")
    p.add_argument("--light-trace", type=Path, required=True, help="PRIVATE B21 trace from same export")
    p.add_argument("--w1-trace", type=Path, required=True, help="PRIVATE W1 trace from same export")
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    root, project = safe_root(args.original), safe_root(args.project)
    for path in (args.light_trace, args.w1_trace):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
            raise ParityError("missing_or_unsafe_private_export_trace")
    original = original_lights(root)
    actual = exported_lights(project)
    with args.light_trace.open(encoding="utf8") as f:
        light_trace = json.load(f)
    with args.w1_trace.open(encoding="utf8") as f:
        w1_trace = json.load(f)
    report = compare(original, actual, light_trace, w1_trace)
    if args.report is not None:
        dest = Path(os.path.abspath(args.report))
        if dest.is_relative_to(root) or dest.is_relative_to(project) or dest in (args.light_trace, args.w1_trace) or dest.is_symlink():
            raise ParityError("unsafe_aggregate_report_destination")
        dest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print("RAFT_B21_SAME_EXPORT_LIGHT_PARITY " + json.dumps(report, sort_keys=True))
    return 0 if report["same_export_light_value_parity"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
