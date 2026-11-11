"""Compare encrypted private source-original Mesa Cull GPU frames to actual owner Adreno captures.

Only numerical, source-free aggregates may be published. Never push private
APK, source meshes/shaders/mip textures or decoded device/Mesa images to GitHub.
The caller must first decrypt AES-256-GCM CMS *locally*, outside public CI.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

from gfxlab.tools.gfx124_batch_zip_audit import audit as audit_owner

APK_SHA = "3a4c7fa7f3593325755b32c0f6c5ad941097936b53808666388a4743b5db3773"
MESA_SHA = {
    "off": "c6d786e908500674d64c3220bf4e26b98253302a88ba390a67b00b570877da78",
    "back": "3664e3146c10a225dafd9bf490454ea29a94d9e3dbe6d7bb9a4171dfe7ccc4e6",
    "front": "d28270e7ae29647374d3e5d52fa9eb0d4a1a3e2e55bad2feaf7d6537907bd0b5",
}
PIXELS = 256 * 256
SIDE = 256


def rgba(data: bytes) -> np.ndarray:
    if len(data) != PIXELS * 4:
        raise ValueError("Unexpected original RGBA8 frame size")
    return np.frombuffer(data, np.uint8).reshape(SIDE, SIDE, 4)


def compare_pixels(device: np.ndarray, reference: np.ndarray, covered: np.ndarray):
    if device.shape != (SIDE, SIDE, 4) or reference.shape != device.shape or covered.shape != (SIDE, SIDE):
        raise ValueError("Wrong original or device readback layout")
    if not covered.any():
        raise ValueError("Missing original geometric coverage")
    differences = np.abs(device[:,:,:3].astype(np.int16) - reference[:,:,:3].astype(np.int16))
    max_rgb = differences.max(axis=2)
    return {
        "pixels_difference_any": int(((max_rgb > 0) & covered).sum()),
        "outlier_pixels_gt10": int(((max_rgb > 10) & covered).sum()),
        "outlier_pixels_gt30": int(((max_rgb > 30) & covered).sum()),
        "max_rgb_channel_error": int(differences[covered].max()),
        "mean_absolute_covered_rgb_error": round(float(differences[covered].mean()), 6),
        "total_covered_rgb_abs_error": int(differences[covered].sum()),
    }, max_rgb


def analyze(private_mesa: Path, signed_apk: Path, owner_zip: Path) -> dict:
    if sha256(signed_apk.read_bytes()).hexdigest() != APK_SHA:
        raise ValueError("Wrong source-original signed Android APK")
    passed = audit_owner(owner_zip, signed_apk)
    if passed["completed_tests"] != 9 or len(passed["tests"]) != 9:
        raise ValueError("Original owner 9-case phone batch not verified")
    with ZipFile(private_mesa) as mesa, ZipFile(signed_apk) as apk, ZipFile(owner_zip) as owner:
        if set(mesa.namelist()) != {f"{name}.rgba" for name in MESA_SHA}:
            raise ValueError("Unexpected private original GPU readback entries")
        frames = {}
        for name, expected in MESA_SHA.items():
            raw = mesa.read(name + ".rgba")
            if sha256(raw).hexdigest() != expected:
                raise ValueError("Private original Mesa Cull framebuffer differs from authenticated CI")
            frames[name] = rgba(raw)
        if apk.read("assets/M03-1/light.rgba") != mesa.read("off.rgba"):
            raise ValueError("Original Mesa Off differs from signed APK reference")
        summary = json.loads(owner.read("summary.json"))
        if summary["renderer"] != "Adreno (TM) 730" or summary["completed_tests"] != 9:
            raise ValueError("Wrong source owner device")
        row = next(case for case in summary["tests"] if case["id"] == "M03-1")
        capture = next(c for c in row["captures"] if c["name"] == "M03-1-light")
        png = owner.read(capture["image"])
        if sha256(png).hexdigest() != capture["image_sha256"]:
            raise ValueError("Owner M03-1 PNG SHA changed")
        with Image.open(io.BytesIO(png)) as image:
            if image.format != "PNG" or image.size != (SIDE, SIDE):
                raise ValueError("Unexpected GLES owner capture shape")
            adreno = np.asarray(image.convert("RGBA"))[::-1].copy()
        if sha256(adreno.tobytes()).hexdigest() != capture["raw_rgba_sha256"]:
            raise ValueError("Owner GL bottom-left RGBA byte order mismatch")
        covered = frames["off"][:, :, 3] == 255
        if int(covered.sum()) != 3301 or any(
            not np.array_equal(adreno[:, :, 3], frames[name][:, :, 3])
            for name in MESA_SHA
        ):
            raise ValueError("Original Adreno/Mesa Cull geometric masks not equal")
    metrics, outliers = {}, {}
    for name, frame in frames.items():
        metrics[name], outliers[name] = compare_pixels(adreno, frame, covered)
    old, new = outliers["off"] > 10, outliers["back"] > 10
    changed = np.any(frames["off"][:, :, :3] != frames["back"][:, :, :3], axis=2) & covered
    rect = np.zeros_like(covered)
    rect[128:140,61:118] = True
    return {
        "experiment": "GFX147.2",
        "source_original_signed_apk_sha256": APK_SHA,
        "owner_device_renderer": passed["renderer"],
        "owner_zip_sha256": sha256(owner_zip.read_bytes()).hexdigest(),
        "original_M03_1_covered_pixels": 3301,
        "private_source_original_Mesa_frame_SHA256_all_verified": True,
        "production_owner_9_case_audit_passed": True,
        "original_device_cull_off_vs_Mesa": metrics,
        "Mesa_CullBack_changed_source_pixels": int(changed.sum()),
        "Adreno_Off_vs_Mesa_Off_gt10": int((old & covered).sum()),
        "Adreno_Off_vs_Mesa_Back_gt10": int((new & covered).sum()),
        "previous_hot_pixels_corrected_by_new_Mesa_Back_reference": int((old & ~new & covered).sum()),
        "new_hot_pixels_introduced_by_new_Mesa_Back_reference": int((~old & new & covered).sum()),
        "remaining_old_hot_pixels_under_new_Mesa_Back_reference": int((old & new & covered).sum()),
        "original_Mesa_CullBack_changes_overlapping_Adreno_Off_hot_pixels": int((old & changed).sum()),
        "source_Mesa_CullBack_changes_in_prior_bbox": int((changed & rect).sum()),
        "actual_Adreno_CullBack_runtime_verified": False,
        "original_Unity_effective_Cull_runtime_verified": False,
        "actual_PC_game_Android_scene_parity_verified": False,
        "phase_closed": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("private_mesa_zip", type=Path)
    p.add_argument("original_signed_apk", type=Path)
    p.add_argument("owner_zip", type=Path)
    p.add_argument("--safe", type=Path, required=True)
    a = p.parse_args()
    result = analyze(a.private_mesa_zip, a.original_signed_apk, a.owner_zip)
    a.safe.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
