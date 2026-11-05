#!/usr/bin/env python3
"""T3 private genuine decoded Texture2D -> exported PNG pixel parity.

Run ONLY after SHA-verified original providers and same-instance W1/B02 traces.
Never publish image bytes, source IDs, GUIDs, filenames or exception messages.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from collections import Counter
from scripts import t3_linked_texture_sampler_export as linked
from scripts import b05_verify_material_texenv_bindings as b05
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
from scripts.t3_decoded_texture_pixel_parity import compare_pair, aggregate
from scripts.t3_pixel_drift_diagnostics import (classify as diagnose_pair, aggregate as aggregate_diagnostics,
    original_texture_categories)
from scripts.t3_normalmap_dxt5_semantic import semantic_rgba_input, NORMALMAP_DXT5NM

GUID = re.compile(r"(?m)^guid: ([0-9a-f]{32})\s*$")
EXPECTED = 106

def _safe_png_index(assets: Path):
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("invalid_export_assets")
    mapping = {}
    count = 0
    for meta in assets.rglob("*.meta"):
        count += 1
        if count > 100000 or meta.is_symlink() or meta.stat().st_size > 1024 * 1024:
            raise ValueError("unsafe_meta_collection")
        image = Path(str(meta)[:-5])
        if image.suffix.lower() != ".png" or not image.is_file() or image.is_symlink():
            continue
        found = GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if len(found) != 1 or found[0] in mapping:
            raise ValueError("ambiguous_export_png_guid")
        mapping[found[0]] = image
    return mapping

def run(original: Path, manifest: Path, project: Path, w1path: Path, b02path: Path):
    import UnityPy
    from PIL import Image
    material = b05.original_texenvs(original, owner_names={linked.OWNER})
    owner_env = UnityPy.load(str(original / "Raft_Data" / linked.OWNER))
    paths = [x.path for x in owner_env.file.externals]
    source_set, counts = linked.source_targets(material, paths, manifest_provider_basename_counts(manifest))
    if len(source_set) != EXPECTED:
        raise ValueError("unexpected_original_texture_population")
    w1 = json.loads(w1path.read_text(encoding="utf8"))
    b02 = json.loads(b02path.read_text(encoding="utf8"))
    selected = linked.subset_same_export(source_set, w1, b02)
    pngs = _safe_png_index(project / "Assets")
    source_by_owner = {}
    categories = []
    semantic_categories = []
    normalmap_usage_seen = 0
    normalmap_exact_after_unwrap = 0
    normalmap_raw_rgb_drift = 0
    diagnostic_rows = []
    for row in selected["objects"]:
        src = row["source"]
        name = src["owner"].removeprefix("Raft_Data/")
        key = (name, src["path_id"])
        if key not in source_set:
            raise ValueError("unverified_source_identity")
        ptr = row["export"]
        guid = ptr["guid"]
        if guid not in pngs:
            raise ValueError("missing_exact_export_png_guid")
        if name not in source_by_owner:
            env = UnityPy.load(str(original / "Raft_Data" / name))
            source_by_owner[name] = {o.path_id: o for o in env.objects if o.type.name == "Texture2D"}
        obj = source_by_owner[name].get(src["path_id"])
        if obj is None:
            raise ValueError("missing_original_Texture2D")
        # Only UnityPy source read/decode failures can mean UNSUPPORTED_MODE.
        # Exported PNG errors and authenticated parity errors are INCONCLUSIVE,
        # not evidence that the original texture codec is unsupported.
        try:
            texture = obj.read()
            decoded = texture.image
        except (NotImplementedError, ValueError, TypeError, OSError):
            decoded = None
        if decoded is None:
            category = "UNSUPPORTED_MODE"
        else:
            with Image.open(pngs[guid]) as image:
                exported_image = image.copy()
            category = compare_pair(decoded, exported_image, original_id=guid,
                                    exported_id=guid, authenticated=True)
        # A diagnostic failure is NOT an unsupported source decoder. Let it
        # propagate to main() as INCONCLUSIVE rather than falsifying parity.
        semantic_category = category
        if category in ('EXACT', 'RGB_DRIFT', 'ALPHA_ONLY_DRIFT'):
            # Typed original source m_TextureFormat/m_ColorSpace and usage=3
            # identify DXT5nm. The SHA-pinned AssetRipper exporter explicitly
            # UnpackNormal()s those pixels. Preserve RAW mismatch evidence,
            # compare a SECOND semantic channel only after exact BGRA mapping.
            source_tree = obj.read_typetree()
            fmt, color_space = original_texture_categories(source_tree)
            mode = source_tree.get("m_LightmapFormat")
            if type(mode) is not int or not 0 <= mode <= 11:
                raise ValueError("unsupported_authenticated_original_normalmap_mode")
            if mode == NORMALMAP_DXT5NM:
                normalmap_usage_seen += 1
                normalmap_raw_rgb_drift += int(category == 'RGB_DRIFT')
                transformed = semantic_rgba_input(
                    decoded, format_code=source_tree['m_TextureFormat'],
                    color_space=source_tree['m_ColorSpace'], lightmap_format=mode)
                semantic_category = compare_pair(transformed, exported_image,
                    original_id=guid, exported_id=guid, authenticated=True)
                normalmap_exact_after_unwrap += int(semantic_category == 'EXACT')
            diagnostic_rows.append(diagnose_pair(decoded, exported_image,
                texture_format=fmt, srgb=color_space))
        categories.append(category)
        semantic_categories.append(semantic_category)
    report = aggregate(categories, expected=EXPECTED)
    semantic = aggregate(semantic_categories, expected=EXPECTED)
    # Exact source cohort of 30 DXT5nm was separately authenticated by
    # CI42013419416, and 106 selected actual PNG GUIDs by this same-run trace.
    # Never turn a partial/invalid converter match into a success flag.
    report['semantic_category_counts'] = semantic['categories']
    report['original_NormalmapDXT5nm_objects'] = normalmap_usage_seen
    report['raw_RGB_drifts_in_NormalmapDXT5nm'] = normalmap_raw_rgb_drift
    report['NormalmapDXT5nm_exact_after_pinned_unpack'] = normalmap_exact_after_unwrap
    report['normalmap_semantic_pixel_content_exact'] = (
        normalmap_usage_seen == 30
        and normalmap_raw_rgb_drift == 30
        and normalmap_exact_after_unwrap == 30
        and semantic['decoded_pixel_exact']
        and report['categories']['EXACT'] == 76)
    report['normalmap_semantic_status'] = (
        'ALL_106_SCOPED_NORMALMAP_SEMANTIC_RGBA_EXACT'
        if report['normalmap_semantic_pixel_content_exact']
        else 'NORMALMAP_SEMANTIC_MISMATCH_OR_INCOMPLETE')
    if len(diagnostic_rows) == EXPECTED:
        report['pixel_drift_diagnostics'] = aggregate_diagnostics(diagnostic_rows, expected=EXPECTED)
    else:
        report['pixel_drift_diagnostics_status'] = 'INCOMPLETE_AUTHENTICATED_RGBA_SCOPE'
    report.update(experiment="T3-authentic-decoded-original-to-export-pixels",
                  original_source_texture_candidates=counts["unique_linked_source_Texture2D_candidates"],
                  actual_export_guid_png_pairs=len(categories),
                  original_bytes_sha_verified_by_parent_workflow=True,
                  android_device_tested=False)
    return report

def main(argv=None):
    ap = argparse.ArgumentParser()
    for key in ("original", "manifest", "project", "w1-trace", "b02-trace", "out"):
        ap.add_argument("--" + key, required=True, type=Path)
    ap.add_argument("--verify-normalmap-semantic", action="store_true",
                    help="Accept only all 106 PNG pixels matching after exact original normal-map unpacking; retain raw drift counts")
    args = ap.parse_args(argv)
    if args.out.exists() or args.out.is_symlink() or args.out.resolve().is_relative_to(args.original.resolve()) or args.out.resolve().is_relative_to(args.project.resolve()):
        raise ValueError("unsafe_report_destination")
    try:
        report = run(args.original, args.manifest, args.project, args.w1_trace, args.b02_trace)
        status = 0 if (report["normalmap_semantic_pixel_content_exact"]
                       if args.verify_normalmap_semantic
                       else report["decoded_pixel_exact"]) else 2
    except Exception as exc:
        report = {"schema_version": 1, "experiment": "T3-authentic-decoded-original-to-export-pixels",
                  "status": "INCONCLUSIVE", "exception_type": type(exc).__name__,
                  "decoded_pixel_exact": False, "android_device_tested": False}
        status = 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("T3_DECODED_PIXEL_PARITY " + json.dumps(report, sort_keys=True))
    return status

if __name__ == "__main__":
    raise SystemExit(main())
