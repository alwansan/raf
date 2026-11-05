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
from scripts.t3_pixel_drift_diagnostics import classify as diagnose_pair, aggregate as aggregate_diagnostics

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
        try:
            texture = obj.read()
            decoded = texture.image
            if decoded is None:
                category = "UNSUPPORTED_MODE"
            else:
                with Image.open(pngs[guid]) as image:
                    exported_image = image.copy()
                    category = compare_pair(decoded, exported_image, original_id=guid,
                                            exported_id=guid, authenticated=True)
                    if category in ('EXACT', 'RGB_DRIFT', 'ALPHA_ONLY_DRIFT'):
                        raw_format = getattr(texture, 'm_TextureFormat', 'UNKNOWN')
                        fmt = getattr(raw_format, 'name', str(raw_format))
                        raw_srgb = getattr(texture, 'm_IsSRGB', None)
                        diagnostic_rows.append(diagnose_pair(decoded, exported_image,
                            texture_format=fmt, srgb=str(raw_srgb) if raw_srgb is not None else 'UNKNOWN'))
        except (NotImplementedError, ValueError, TypeError, OSError):
            category = "UNSUPPORTED_MODE"
        categories.append(category)
    report = aggregate(categories, expected=EXPECTED)
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
    args = ap.parse_args(argv)
    if args.out.exists() or args.out.is_symlink() or args.out.resolve().is_relative_to(args.original.resolve()) or args.out.resolve().is_relative_to(args.project.resolve()):
        raise ValueError("unsafe_report_destination")
    try:
        report = run(args.original, args.manifest, args.project, args.w1_trace, args.b02_trace)
        status = 0 if report["decoded_pixel_exact"] else 2
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
