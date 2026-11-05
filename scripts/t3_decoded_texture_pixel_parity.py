#!/usr/bin/env python3
"""T3: fail-closed decoded RGBA pixel comparison for authenticated texture pairs.

Private caller must authenticate original bytes, exported PNG GUID and .meta,
and pair provenance BEFORE invoking compare_pair. Never log pixel data.
This is NOT a Unity/Adreno or sRGB-equivalence test.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

MAX_PIXELS = 16384 * 16384
CATEGORIES = frozenset({
    "EXACT", "VERTICAL_FLIP", "HORIZONTAL_FLIP", "BOTH_AXES_FLIP",
    "ALPHA_ONLY_DRIFT", "RGB_DRIFT", "DIMENSION_MISMATCH",
    "UNSUPPORTED_MODE", "UNVERIFIED_IDENTITY", "INVALID_INPUT",
})


def compare_pair(original: Any, exported: Any, *, original_id: str,
                 exported_id: str, authenticated: bool = False) -> str:
    """Compare two PIL Image objects; output category only, no pixel details.

    original_id/exported_id are trusted caller-supplied provenance keys, not
    names guessed from filenames. Caller must separately check color-space
    metadata, source decoder format, and export metadata.
    """
    if not authenticated or not original_id or original_id != exported_id:
        return "UNVERIFIED_IDENTITY"
    try:
        from PIL import Image, ImageChops
        if not isinstance(original, Image.Image) or not isinstance(exported, Image.Image):
            return "INVALID_INPUT"
        if original.mode != "RGBA" or exported.mode != "RGBA":
            return "UNSUPPORTED_MODE"
        if original.size != exported.size:
            return "DIMENSION_MISMATCH"
        width, height = original.size
        if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
            return "INVALID_INPUT"
        if ImageChops.difference(original, exported).getbbox() is None:
            return "EXACT"
        # Orientation is diagnostic only: NEVER silently normalize/flip source.
        transpose = Image.Transpose
        for category, op in (
            ("VERTICAL_FLIP", transpose.FLIP_TOP_BOTTOM),
            ("HORIZONTAL_FLIP", transpose.FLIP_LEFT_RIGHT),
            ("BOTH_AXES_FLIP", transpose.ROTATE_180),
        ):
            if ImageChops.difference(original.transpose(op), exported).getbbox() is None:
                return category
        rgb_a = original.getchannel("R"), original.getchannel("G"), original.getchannel("B")
        rgb_b = exported.getchannel("R"), exported.getchannel("G"), exported.getchannel("B")
        if all(ImageChops.difference(a, b).getbbox() is None for a, b in zip(rgb_a, rgb_b)):
            return "ALPHA_ONLY_DRIFT"
        return "RGB_DRIFT"
    except (ValueError, TypeError, OSError, MemoryError):
        return "INVALID_INPUT"


def aggregate(categories: list[str], *, expected: int = 106) -> dict:
    """Safe public aggregate, rejecting incomplete scope or unknown categories."""
    if type(expected) is not int or expected <= 0:
        raise ValueError("Invalid expected scope")
    if len(categories) != expected or any(c not in CATEGORIES for c in categories):
        raise ValueError("Incomplete/invalid authenticated pixel scope")
    counts = Counter(categories)
    return {
        "schema_version": 1,
        "scope": expected,
        "categories": {k: counts[k] for k in sorted(CATEGORIES)},
        "decoded_pixel_exact": counts["EXACT"] == expected,
        "unity_android_pixels_proven": False,
        "srgb_equivalence_proven": False,
        "render_002_closed": False,
    }
