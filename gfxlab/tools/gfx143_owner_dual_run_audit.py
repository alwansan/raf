"""GFX143: source-safe two-run audit of original GFX124 Adreno readbacks.

This module never embeds original Raft fixtures or owner captures in GitHub.
All user ZIPs and source-original APKs are local inputs; public output contains
only aggregate image difference statistics, not pixel values.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from gfxlab.tools.gfx124_batch_zip_audit import audit
from gfxlab.tools.gfx124_batch_pack import (
    CONTROLS, SLOTS, POSES, SHADOW_CONTROLS, DEFERRED_CAPTURES, REFERENCE_SIZE
)

CAPTURES = 51
CASES = 9


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _raw_png(data: bytes) -> bytes:
    with Image.open(io.BytesIO(data)) as image:
        if image.format != "PNG" or image.size != (256, 256):
            raise ValueError("Unexpected capture PNG dimensions")
        return image.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()


def _reference_path(test: dict, control: str) -> str:
    folder, mode = test["primary"], control
    if "secondary" in test:
        folder, mode = test["primary"], "combined"
    elif "forward_add" in test:
        folder = test["forward_add"] if control == "lit" else folder
        mode = "combined" if control == "lit" else "light"
    elif "animation" in test:
        folder = test["animation"]
    elif "shadow" in test:
        folder = test["shadow"]
    elif "deferred" in test:
        folder = test["deferred"]
    return f"assets/{folder}/{mode}.rgba"


def _controls(test: dict) -> tuple[str, ...]:
    if "deferred" in test:
        return tuple(DEFERRED_CAPTURES)
    if "shadow" in test:
        return tuple(SHADOW_CONTROLS)
    if "animation" in test:
        return tuple(POSES)
    if "forward_add" in test:
        return ("lit", "off", "reject")
    if "secondary" in test:
        return ("combined",)
    return tuple(CONTROLS)


def pixel_statistics(actual: bytes, reference: bytes, *, threshold: int = 30,
                     covered_mask: bytes | None = None) -> dict:
    """RGB outliers and alpha channel drift. Mask is independent RT0 for MRTs."""
    if len(actual) != REFERENCE_SIZE or len(reference) != REFERENCE_SIZE:
        raise ValueError("RGBA8 capture length changed")
    if covered_mask is not None and len(covered_mask) != REFERENCE_SIZE // 4:
        raise ValueError("Invalid independent render-target coverage mask")
    total = covered = max_rgb = above10 = above30 = alpha_diff = max_alpha = 0
    coord = []
    for i in range(0, REFERENCE_SIZE, 4):
        pixel = i // 4
        dr = [abs(actual[i+k] - reference[i+k]) for k in range(3)]
        da = abs(actual[i+3] - reference[i+3])
        if da:
            alpha_diff += 1
            max_alpha = max(max_alpha, da)
        valid = (covered_mask[pixel] == 255 if covered_mask is not None
                 else actual[i+3] == reference[i+3] == 255)
        if valid:
            covered += 1
            m = max(dr)
            max_rgb = max(max_rgb, m)
            total += sum(dr)
            above10 += m > 10
            if m > threshold:
                above30 += 1
                coord.append((pixel % 256, pixel // 256))
    return {
        "covered_pixels": covered,
        "covered_rgb_mae_0_to_255": round(total / (covered * 3), 6) if covered else 0.0,
        "max_rgb_channel_error": max_rgb,
        "rgb_outlier_pixels_gt10": above10,
        "rgb_outlier_pixels_gt30": above30,
        "outlier_bbox_xyxy": [
            min(p[0] for p in coord), min(p[1] for p in coord),
            max(p[0] for p in coord), max(p[1] for p in coord),
        ] if coord else None,
        "alpha_byte_differing_pixels": alpha_diff,
        "max_alpha_byte_error": max_alpha,
    }


def analyze(first, second, signed_apk: Path, expected_apk_sha256: str) -> dict:
    """Run the *production* owner ZIP auditor before any hotspot comparisons."""
    if digest(signed_apk.read_bytes()) != expected_apk_sha256:
        raise ValueError("Wrong signed original reference APK")
    checked_first = audit(first, signed_apk)
    checked_second = audit(second, signed_apk)
    for checked in (checked_first, checked_second):
        if checked["completed_tests"] != CASES or len(checked["tests"]) != CASES:
            raise ValueError("Not all nine phone tests completed and validated")
        if any(not case["draw_completed"] for case in checked["tests"]):
            raise ValueError("Android owner batch contains failed draw cases")
    with ZipFile(first) as a, ZipFile(second) as b, ZipFile(signed_apk) as apk:
        names = set(a.namelist())
        if names != set(b.namelist()) or len(names) != CAPTURES + 1:
            raise ValueError("Owner replays have incomplete or inconsistent ZIP names")
        identical = all(a.read(name) == b.read(name) for name in sorted(names))
        report = json.loads(a.read("summary.json"))
        plan = json.loads(apk.read("assets/batch.json"))["tests"]
        if [x["id"] for x in plan] != [x["id"] for x in report["tests"]]:
            raise ValueError("Original owner plan changed")
        snapshots = []
        for test in plan:
            tid = test["id"]
            rows = next(x["captures"] for x in report["tests"] if x["id"] == tid)
            is_deferred = "deferred" in test
            mask = (apk.read(_reference_path(test, "native-rt0"))[3::4]
                    if is_deferred else None)
            for control, row in zip(_controls(test), rows, strict=True):
                name = tid if "secondary" in test else f"{tid}-{control}"
                file = name + (".rgba" if is_deferred else ".png")
                raw = a.read(file) if is_deferred else _raw_png(a.read(file))
                ref = apk.read(_reference_path(test, control))
                stats = pixel_statistics(raw, ref, covered_mask=mask)
                if ref[3::4] != raw[3::4] and not is_deferred:
                    raise ValueError("Forward PNG alpha changed against reference")
                snapshots.append({"name": name, **stats})
        if len(snapshots) != CAPTURES:
            raise ValueError("Unexpected number of verified captures")
    hotspot = [
        {key: value for key, value in row.items() if key in (
            "name", "rgb_outlier_pixels_gt30", "max_rgb_channel_error",
            "covered_rgb_mae_0_to_255", "outlier_bbox_xyxy"
        )}
        for row in snapshots if row["rgb_outlier_pixels_gt30"]
    ]
    drift = [
        {key: row[key] for key in ("name", "alpha_byte_differing_pixels", "max_alpha_byte_error")}
        for row in snapshots if row["alpha_byte_differing_pixels"]
    ]
    return {
        "experiment": "GFX143", "source_original_signed_apk_sha256": expected_apk_sha256,
        "production_gfx124_zip_audit_passed_twice": True,
        "renderer": checked_first["renderer"], "gles": checked_first["gles"],
        "planned_cases": CASES, "validated_cases": checked_first["completed_tests"],
        "validated_captures": len(snapshots),
        "owner_zip_contents_byte_identical": identical,
        "all_coverage_masks_match_reference": True,
        "capture_count_with_exact_rgba": sum(row["max_rgb_channel_error"] == 0
                                            and row["alpha_byte_differing_pixels"] == 0
                                            for row in snapshots),
        "hotspots_rgb_channel_error_above30": hotspot,
        "deferred_alpha_channel_numerical_drift": drift,
        "forward_add_preserves_base_when_off_and_depth_rejected": all(
            checked_first["tests"][5]["controls_preserved_forward"].values()
        ),
        "original_animator_runtime_verified": False,
        "unity_original_pass_selection_verified": False,
        "original_game_pc_android_pixel_parity": False,
        "phase_closed": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run1", type=Path)
    p.add_argument("run2", type=Path)
    p.add_argument("original_signed_apk", type=Path)
    p.add_argument("--expected-apk-sha256", required=True)
    p.add_argument("--safe", type=Path, required=True)
    args = p.parse_args()
    report = analyze(args.run1, args.run2, args.original_signed_apk,
                     args.expected_apk_sha256)
    args.safe.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
