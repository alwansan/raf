"""GT Particle108 three linked Texture2D export-alpha diagnostic (NO APK).

Original SHA-authenticated six-scene five-Material graph and Texture2D owners
identify the three targets. A same-instance AssetRipper trace selects exported
TextureImporter GUIDs. This classifies actual exported image alpha and importer
metadata without changing assets or publishing names, IDs, GUIDs, or pixels.

An opaque input does NOT prove the shader is wrong: shader alpha may be derived
from RGB or uniforms. Exported alpha is NOT Android Vulkan blending parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import t3_original_particle_material_texenv as material_source
from scripts import t3_original_particle_texture_targets as texture_source
from scripts.verify_export_lineage import identity, pointer
from scripts.verify_exported_material_texture_links import GUID, IMAGES

MAX_IMAGE_BYTES = 256 * 1024 * 1024
MAX_PIXELS = 64 * 1024 * 1024
MAX_META = 256 * 1024
EXPECTED_TARGETS = 3
STATUS = "GT_PARTICLE108_THREE_SAME_EXPORT_TEXTURE_ALPHA_CLASSIFIED"
META_FIELDS = ("alphaSource", "alphaIsTransparency", "sRGBTexture", "mipmapEnabled")


def alpha_profile(image):
    """Private pixel analysis: return only aggregate alpha coverage."""
    if not 0 < image.width * image.height <= MAX_PIXELS:
        raise ValueError("unsupported_or_oversize_particle_texture_dimensions")
    has_alpha = "A" in image.getbands() or "transparency" in image.info
    rgba = image.convert("RGBA")
    bins = rgba.getchannel("A").histogram()
    if len(bins) != 256 or sum(bins) != image.width * image.height:
        raise ValueError("invalid_decoded_alpha_histogram")
    return {
        "has_explicit_alpha": bool(has_alpha),
        "all_opaque": bins[255] == image.width * image.height,
        "has_transparent_pixels": sum(bins[:255]) > 0,
        "has_partially_transparent_pixels": sum(bins[1:255]) > 0,
        "fully_transparent_pixel_present": bins[0] > 0,
    }


def source_texture_export_map(trace, originals, *, metrics=None):
    """One original Texture2D28 => one exported pointer; only numeric telemetry."""
    if (type(trace) is not dict or trace.get("schema_version") != 1
            or not re.fullmatch("[a-fA-F0-9]{32}", str(trace.get("export_instance", "")))
            or not isinstance(trace.get("objects"), list)
            or len(originals) != EXPECTED_TARGETS):
        raise ValueError("untrusted_particle_source_export_linkage")
    if metrics is not None:
        if type(metrics) is not dict or metrics:
            raise ValueError("invalid_export_trace_numeric_diagnostic")
        metrics.update({
            "original_selected_Texture2D28":EXPECTED_TARGETS,
            "all_export_trace_Texture2D28_rows":0,
            "rows_matching_original_selected_Texture2D28":0,
            "duplicate_original_selected_texture_rows":0,
            "matched_original_selected_unique_targets":0,
            "distinct_exported_GUIDs_for_matched_original":0,
        })
    result = {}
    for row in trace["objects"]:
        if not isinstance(row, dict) or row.get("class_id") != 28:
            continue
        if metrics is not None:
            metrics["all_export_trace_Texture2D28_rows"] += 1
        key = identity(row["source"])
        if key not in originals:
            continue
        if metrics is not None:
            metrics["rows_matching_original_selected_Texture2D28"] += 1
        if key in result:
            if metrics is not None:
                metrics["duplicate_original_selected_texture_rows"] += 1
            raise ValueError("duplicated_original_particle_Texture2D_export")
        fid, guid, kind = pointer(row["export"])
        if fid <= 0 or kind not in ("2", "3"):
            raise ValueError("invalid_same_export_Texture2D_pointer")
        result[key] = guid
        if metrics is not None:
            metrics["matched_original_selected_unique_targets"] = len(result)
            metrics["distinct_exported_GUIDs_for_matched_original"] = len(set(result.values()))
    if set(result) != set(originals) or len(set(result.values())) != EXPECTED_TARGETS:
        raise ValueError("original_particle_Texture2D_Guid_not_unique")
    return result


def image_meta_index(assets, wanted):
    """Use exactly the previously traced GUIDs; never infer assets by names."""
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_exported_Unity_Assets")
    indexed = {}
    files = sorted(assets.rglob("*"))
    if len(files) > 150000 or any(path.is_symlink() for path in files):
        raise ValueError("unsafe_exported_asset_inventory")
    for meta in files:
        if not meta.is_file() or not meta.name.endswith(".meta"):
            continue
        if meta.stat().st_size > MAX_META:
            continue
        text = meta.read_text(encoding="utf-8-sig")
        found = GUID.findall(text)
        if len(found) != 1 or found[0].lower() not in wanted:
            continue
        guid = found[0].lower()
        image = meta.with_suffix("")
        if guid in indexed:
            raise ValueError("duplicate_particle_exported_Texture2D_GUID")
        if (not image.is_file() or image.is_symlink()
                or image.suffix.lower() not in IMAGES):
            raise ValueError("selected_particle_Texture2D_not_exported_as_image")
        fields = {}
        for name in META_FIELDS:
            matches = re.findall(r"(?m)^\s+" + name + r":\s*(-?\d+)\s*$", text)
            fields[name] = int(matches[0]) if len(matches) == 1 else None
        indexed[guid] = (image, fields, "TextureImporter:" in text)
    if set(indexed) != set(wanted):
        raise ValueError("selected_particle_texture_image_importer_missing")
    return indexed


def analyze_exported_images(index):
    from PIL import Image
    total = Counter()
    importer_values = {k: Counter() for k in META_FIELDS}
    for path, fields, is_importer in index.values():
        if not is_importer or not 0 < path.stat().st_size <= MAX_IMAGE_BYTES:
            raise ValueError("particle_image_or_importer_unusable")
        with Image.open(path) as image:
            profile = alpha_profile(image)
        total["linked_exported_images_decoded"] += 1
        for key, truth in profile.items():
            total[key] += int(truth)
        for key, value in fields.items():
            importer_values[key]["missing" if value is None else str(value)] += 1
    if total["linked_exported_images_decoded"] != EXPECTED_TARGETS:
        raise ValueError("missing_exported_particle_alpha_classification")
    return total, {key: dict(sorted(value.items())) for key, value in importer_values.items()}


def audit(original, manifest, project, trace_path, *, checkpoint=None, trace_metrics=None):
    def mark(step):
        if checkpoint is not None:
            checkpoint(step)
    original = original.absolute()
    project = project.absolute()
    trace_path = trace_path.absolute()
    if (not original.is_dir() or original.is_symlink()
            or project.is_symlink() or trace_path.is_symlink()
            or not trace_path.is_file()
            or trace_path.is_relative_to(project)
            or any(path.is_symlink() for path in (original, project, trace_path))):
        raise ValueError("unsafe_original_or_exported_particle_data")
    mark("original_material_shader_Texture2D_PPtrs")
    original_targets = {}
    materials = material_source.run(
        original, manifest, private_local_texture_targets=original_targets)
    mark("original_Texture2D28_manifest_and_stream")
    source = texture_source.run(original, manifest)
    if (materials["status"] != material_source.STATUS
            or source["status"] != texture_source.STATUS
            or source["original_selected_typed_Texture2D28_targets"] != EXPECTED_TARGETS
            or sum(original_targets.values()) != 10):
        raise ValueError("unverified_particle_original_Texture2D_scope")
    if trace_path.stat().st_size > 40 * 1024 * 1024:
        raise ValueError("oversize_private_export_trace")
    mark("read_private_export_trace")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    mark("join_same_export_Texture2D28_GUID")
    mapping = source_texture_export_map(trace, original_targets, metrics=trace_metrics)
    mark("locate_exported_TextureImporter_image")
    exported = image_meta_index(project / "Assets", set(mapping.values()))
    mark("decode_exported_image_alpha")
    counts, importers = analyze_exported_images(exported)
    mark("completed")
    return {
        "schema_version": 1,
        "status": STATUS,
        "source_original_texture2d_sha_verified": True,
        "source_particle_material_to_texture_references": 10,
        "source_original_texture2d_objects": EXPECTED_TARGETS,
        "same_export_source_texture_guids_joined": len(mapping),
        "actual_exported_alpha_image_counts": dict(sorted(counts.items())),
        "exported_importer_metadata_numeric_counts": importers,
        "original_source_texture_pixels_compared": False,
        "texture_alpha_loss_from_original_proven": False,
        "correct_runtime_particle_shader_blend_proven": False,
        "android_device_fire_pixels_verified": False,
        "original_source_or_exported_assets_modified": False,
        "private_ids_guids_paths_or_pixels_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "manifest", "project", "trace", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    if (a.out.is_symlink() or a.out.exists() or
            a.out.resolve().is_relative_to(a.project.resolve()) or
            a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_particle_alpha_report_destination")
    progress = {"stage": "input_paths_and_layout"}
    numeric_trace_metrics = {}
    stages = {
        "input_paths_and_layout",
        "original_material_shader_Texture2D_PPtrs",
        "original_Texture2D28_manifest_and_stream",
        "read_private_export_trace",
        "join_same_export_Texture2D28_GUID",
        "locate_exported_TextureImporter_image",
        "decode_exported_image_alpha",
        "completed",
    }
    def mark(stage):
        if stage not in stages:
            raise ValueError("invalid_private_diagnostic_stage")
        progress["stage"] = stage
    try:
        report = audit(a.original, a.manifest, a.project, a.trace, checkpoint=mark,
                       trace_metrics=numeric_trace_metrics)
    except Exception as error:
        report = {
            "schema_version": 1,
            "status": "INCONCLUSIVE",
            "error_type": type(error).__name__,
            "failure_code": (str(error) if str(error) in ["untrusted_particle_source_export_linkage","duplicated_original_particle_Texture2D_export","invalid_same_export_Texture2D_pointer","original_particle_Texture2D_Guid_not_unique"]
                             else "UNCLASSIFIED_SAFE_ERROR"),
            "failure_stage": progress["stage"],
            "trace_source_export_match_counts": numeric_trace_metrics,
            "android_device_fire_pixels_verified": False,
            "private_ids_guids_paths_or_pixels_published": False,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("GT_PARTICLE108_EXPORTED_TEXTURE_ALPHA " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
