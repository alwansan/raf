#!/usr/bin/env python3
"""Read-only Renderer->Material->actual ShaderLab Dummy impact on one Unity export.

The unit of observation is a *serialized exported Renderer material slot*, never
a visible object/draw call. Use after vendor restoration on one authentic bounded
export. Private GUIDs, object IDs, names, paths, source text stay in local RAM.
Only bounded aggregate categories/bands may leave the runner.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import b03_verify_renderer_material_links as b03
from scripts import t3_audit_exported_material_programs as t3

RESULT_STATUS = "EXPORTED_RENDERER_SHADER_DUMMY_IMPACT_SOURCE_ONLY"
MAX_FILES = 150_000
MATERIAL_LINE = re.compile(r"(?m)^  m_Shader:")
BANDS = ("1", "2_to_4", "5_to_16", "17_plus")
RENDERER_CLASS_COUNT = len(b03.RENDERERS)


def _band_counts(frequencies: Counter) -> dict[str, int]:
    return {
        "1": sum(v == 1 for v in frequencies.values()),
        "2_to_4": sum(2 <= v <= 4 for v in frequencies.values()),
        "5_to_16": sum(5 <= v <= 16 for v in frequencies.values()),
        "17_plus": sum(v >= 17 for v in frequencies.values()),
    }


def _status_for_material(body: str, profiles: dict) -> tuple[str, str]:
    """Return class and *private* target guid, never put target in report."""
    fields = t3.SHADER.findall(body)
    if len(fields) != 1 or len(MATERIAL_LINE.findall(body)) != 1:
        raise b03.LinkError("ambiguous_exported_Material_Shader_field")
    try:
        fid, guid, kind = t3.pptr(fields[0])
    except ValueError as error:
        raise b03.LinkError("invalid_exported_Material_Shader_PPtr") from error
    if fid < 0:
        raise b03.LinkError("negative_exported_Material_Shader_file_id")
    if fid == 0:
        if guid not in ("", b03.ZERO) or kind not in (None, "0"):
            raise b03.LinkError("ambiguous_exported_null_Material_Shader")
        return "null_shader", ""
    if guid in t3.ENGINE and kind == "0":
        return "builtin_shader", ""
    if fid == 4800000 and kind == "3" and guid in profiles:
        return ("dummy_shader" if profiles[guid]["dummy"] else "non_dummy_shader"), guid
    return "unresolved_or_unsupported_shader", ""


def _project_objects(project: Path):
    project = Path(project).absolute()
    if any(p.is_symlink() for p in (project, *project.parents)):
        raise b03.LinkError("unsafe_export_project_path")
    assets = project / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise b03.LinkError("missing_or_symlinked_export_Assets")
    entries = sorted(assets.rglob("*"))
    if len(entries) > MAX_FILES or any(p.is_symlink() for p in entries):
        raise b03.LinkError("oversize_or_redirected_export_inventory")
    profiles = t3._shader_profiles(entries)
    if not profiles:
        raise b03.LinkError("no_exported_ShaderLab_sources")
    objects = []
    seen_owners = set()
    for path in entries:
        if path.suffix not in b03.YAML_EXT or not path.is_file():
            continue
        if path.stat().st_size > b03.MAX_YAML:
            raise b03.LinkError("oversize_exported_YAML")
        with path.open("rb") as stream:
            prefix = stream.read(16).lstrip(b"\xef\xbb\xbf")
        if not prefix.startswith(b"%YAML"):
            if path.suffix == ".mat":
                raise b03.LinkError("non_yaml_exported_Material")
            continue
        owner = b03.source_guids(Path(str(path) + ".meta"))
        if owner in seen_owners:
            raise b03.LinkError("duplicate_exported_YAML_meta_guid")
        seen_owners.add(owner)
        docs = b03.documents(path.read_text("utf-8-sig"))
        objects.extend((owner, kind, fid, body) for kind, fid, body in docs)
    return profiles, objects


def audit(project: Path, expected_material_report: dict | None = None) -> dict:
    profiles, objects = _project_objects(project)
    materials = {}
    class_counts = Counter()
    for owner, kind, fid, body in objects:
        if kind != "21":
            continue
        if not body.lstrip().startswith("Material:\n"):
            raise b03.LinkError("unexpected_exported_Material_type_name")
        key = (owner, fid)
        if key in materials:
            raise b03.LinkError("duplicate_exported_Material_identity")
        materials[key] = _status_for_material(body, profiles)
        class_counts[materials[key][0]] += 1
    if not materials:
        raise b03.LinkError("no_exported_Material_YAML_documents")
    if expected_material_report is not None:
        if (type(expected_material_report) is not dict or
            expected_material_report.get("status") != t3.STATUS or
            type(expected_material_report.get("counts")) is not dict):
            raise b03.LinkError("not_a_valid_same_export_Material_audit")
        expected = expected_material_report["counts"]
        pairs = (
            ("material_documents", len(materials)),
            ("material_docs_using_dummy_Shader", class_counts["dummy_shader"]),
            ("material_docs_using_non_dummy_Shader", class_counts["non_dummy_shader"]),
            ("material_docs_using_Unity_builtin_Shader", class_counts["builtin_shader"]),
            ("material_docs_with_null_Shader", class_counts["null_shader"]),
            ("material_docs_with_unknown_or_broken_Shader",
             class_counts["unresolved_or_unsupported_shader"]),
        )
        if any(type(expected.get(name)) is not int or expected[name] != value
               for name, value in pairs):
            raise b03.LinkError("material_quality_report_differs_from_same_export")
    counts = Counter()
    per_dummy_target = Counter()
    encountered_dummy_targets = set()
    for owner, kind, _, body in objects:
        slots = b03.renderer_slots(kind, body)
        if slots is None:
            continue
        counts["renderer_objects"] += 1
        counts["renderer_material_slots"] += len(slots)
        if not slots:
            counts["renderer_empty_material_arrays"] += 1
        saw_dummy = False
        for fid, guid, pointer_type in slots:
            if fid == 0:
                if guid not in ("", b03.ZERO) or pointer_type not in (None, "0"):
                    raise b03.LinkError("ambiguous_null_exported_Renderer_slot")
                counts["renderer_slots_null_material"] += 1
                continue
            if guid in b03.BUILTIN or (guid == b03.ZERO and pointer_type == "0"):
                counts["renderer_slots_builtin_material_unverified"] += 1
                continue
            if pointer_type is not None and pointer_type not in ("2", "3"):
                counts["renderer_slots_unsupported_pointer_type"] += 1
                continue
            status = materials.get((guid or owner, fid))
            if status is None:
                counts["renderer_slots_unresolved_material"] += 1
                continue
            classification, shader = status
            counts["renderer_slots_resolved_material"] += 1
            counts["renderer_slots_" + classification] += 1
            if classification == "dummy_shader":
                saw_dummy = True
                per_dummy_target[shader] += 1
                encountered_dummy_targets.add(shader)
        if saw_dummy:
            counts["renderer_objects_with_at_least_one_dummy_shader_slot"] += 1
    if not counts["renderer_objects"]:
        raise b03.LinkError("no_exported_Renderer_YAML_documents")
    if counts["renderer_material_slots"] != sum(
        counts[key] for key in (
            "renderer_slots_null_material",
            "renderer_slots_builtin_material_unverified",
            "renderer_slots_unsupported_pointer_type",
            "renderer_slots_unresolved_material",
            "renderer_slots_resolved_material",
    )):
        raise b03.LinkError("renderer_slot_accounting_mismatch")
    if counts["renderer_slots_resolved_material"] != sum(
        counts["renderer_slots_" + status] for status in (
            "dummy_shader", "non_dummy_shader", "builtin_shader",
            "null_shader", "unresolved_or_unsupported_shader",
    )):
        raise b03.LinkError("resolved_renderer_material_shader_accounting_mismatch")
    aggregate = {
        "schema_version": 1,
        "status": RESULT_STATUS,
        "scope": "one_exported_Unity_project_after_selected_vendor_restorers",
        "counts": {key: counts[key] for key in (
            "renderer_objects", "renderer_material_slots",
            "renderer_empty_material_arrays",
            "renderer_objects_with_at_least_one_dummy_shader_slot",
            "renderer_slots_resolved_material",
            "renderer_slots_dummy_shader",
            "renderer_slots_non_dummy_shader",
            "renderer_slots_builtin_shader",
            "renderer_slots_null_shader",
            "renderer_slots_unresolved_or_unsupported_shader",
            "renderer_slots_null_material",
            "renderer_slots_builtin_material_unverified",
            "renderer_slots_unresolved_material",
            "renderer_slots_unsupported_pointer_type",
        )},
        "source_material_documents": len(materials),
        "source_material_documents_with_dummy_shader": class_counts["dummy_shader"],
        "source_material_documents_with_non_dummy_shader": class_counts["non_dummy_shader"],
        "distinct_renderer_referenced_dummy_shader_targets": len(encountered_dummy_targets),
        "renderer_slot_dummy_target_frequency_bands": _band_counts(per_dummy_target),
        "target_frequency_unit": "exported_serialized_renderer_material_slots_not_draw_calls",
        "original_to_export_renderer_identity_or_shader48_proven": False,
        "full_native_unity_import_or_android_pixels_verified": False,
        "metadata_or_game_assets_modified": False,
    }
    return aggregate


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--same-export-material-quality", type=Path)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.project.resolve())):
        raise b03.LinkError("unsafe_aggregate_report_destination")
    try:
        expected = None
        if args.same_export_material_quality is not None:
            if args.same_export_material_quality.resolve().is_relative_to(
                    args.project.resolve()):
                raise b03.LinkError("unsafe_expected_report_inside_export")
            expected = json.loads(args.same_export_material_quality.read_text("utf-8"))
        result = audit(args.project, expected)
    except Exception as error:
        # Original object IDs, Unity file paths and GUIDs NEVER appear in reports.
        result = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "exception_type": type(error).__name__,
                  "original_to_export_renderer_identity_or_shader48_proven": False,
                  "full_native_unity_import_or_android_pixels_verified": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("RAFT_T3_RENDERER_MATERIAL_SHADER_IMPACT " +
          json.dumps(result, sort_keys=True))
    return 0 if result["status"] == RESULT_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
