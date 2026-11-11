"""Source-free metrics for controlled original Shader48 OpenGL Cull Off/Back/Front renders.

Inputs remain private RGBA8 images; only safe aggregate counts leave CI.
"""
from __future__ import annotations

import hashlib
import numpy as np

SIDE = 256


def _validate(name: str, image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.shape != (SIDE, SIDE, 4) or image.dtype != np.uint8:
        raise ValueError(f"Invalid source {name} RGBA8 readback shape or dtype")
    if not np.isin(image[:, :, 3], (0, 255)).all():
        raise ValueError(f"Nonbinary source {name} geometric alpha")
    return image


def _compare(off: np.ndarray, other: np.ndarray, region: np.ndarray) -> dict:
    mask = (off[:, :, 3] == 255) & (other[:, :, 3] == 255)
    delta = np.abs(off[:, :, :3].astype(np.int16) - other[:, :, :3].astype(np.int16))
    pixmax = np.max(delta, axis=2)
    changed = mask & (pixmax > 0)
    hot = mask & (pixmax > 10)
    changed_pos = np.argwhere(changed)
    return {
        "coverage_pixels": int((other[:, :, 3] == 255).sum()),
        "coverage_mask_exact": bool(np.array_equal(off[:, :, 3], other[:, :, 3])),
        "rgba_exact": bool(np.array_equal(off, other)),
        "covered_rgb_changed_pixels": int(changed.sum()),
        "covered_rgb_mean_absolute_error": round(float(delta[mask].mean()), 6) if mask.any() else None,
        "covered_rgb_max_channel_difference": int(np.max(delta[mask])) if mask.any() else None,
        "covered_rgb_difference_gt10_pixels": int(hot.sum()),
        "covered_rgb_difference_gt10_in_previous_Adreno_hotspot_bbox": int((hot & region).sum()),
        "covered_rgb_difference_gt10_outside_previous_hotspot_bbox": int((hot & ~region).sum()),
        "covered_rgb_changed_bbox_xyxy": [int(changed_pos[:, 1].min()), int(changed_pos[:, 0].min()),
                                         int(changed_pos[:, 1].max()), int(changed_pos[:, 0].max())]
            if len(changed_pos) else None,
        "original_color_sha256": hashlib.sha256(other.tobytes()).hexdigest(),
    }


def summarize(off: np.ndarray, back: np.ndarray, front: np.ndarray,
              off_repeat: np.ndarray, back_repeat: np.ndarray, *,
              expected_source_coverage: int = 3301) -> dict:
    for name, image in (("off", off), ("back", back), ("front", front),
                        ("off-repeat", off_repeat), ("back-repeat", back_repeat)):
        _validate(name, image)
    if not np.array_equal(off, off_repeat):
        raise ValueError("Cull Off baseline not restored byte-for-byte")
    if not np.array_equal(back, back_repeat):
        raise ValueError("Cull Back original draw not deterministic")
    covered = int(np.count_nonzero(off[:, :, 3]))
    if covered != expected_source_coverage:
        raise ValueError("Source original M03-1 coverage changed from pinned owner fixture")
    region = np.zeros((SIDE, SIDE), dtype=bool)
    # Prior GFX143 high-error bounding rectangle from source-safe owner report;
    # GLES readback coordinates have the bottom-left origin.
    region[128:140, 61:118] = True
    return {
        "experiment": "GFX147",
        "original_source_M03_1_coverage": covered,
        "controlled_gl_front_face": "CCW",
        "depth_func": "LESS",
        "off_repeat_exact": True,
        "back_repeat_exact": True,
        "back_vs_off": _compare(off, back, region),
        "front_vs_off": _compare(off, front, region),
        "source_M03_1_previous_Adreno_gt10_hot_pixels": 58,
        "original_Unity_effective_Cull_runtime_verified": False,
        "actual_Adreno_CullBack_pixel_parity_verified": False,
        "original_game_PC_Android_scene_parity_verified": False,
        "phase_closed": False,
    }
