#!/usr/bin/env python3
"""Privacy-safe decoded texture drift diagnostics for SHA-authenticated pairs.

Never export pixels, GUIDs, filenames, hashes of images, or per-object rows.
This is a *diagnostic* of decoder/export differences, not a color correction.
"""
from __future__ import annotations

from collections import Counter
from PIL import Image, ImageChops

def classify(original: Image.Image, exported: Image.Image, *, texture_format: str = "UNKNOWN",
             srgb: str = "UNKNOWN") -> dict[str, str]:
    if original.mode != "RGBA" or exported.mode != "RGBA" or original.size != exported.size:
        raise ValueError("invalid authenticated RGBA pair")
    if not original.width or not original.height or original.width * original.height > 16384**2:
        raise ValueError("invalid image dimensions")
    extrema = [ImageChops.difference(a, b).getextrema()[1]
              for a, b in zip(original.split(), exported.split())]
    max_rgb = max(extrema[:3])
    max_alpha = extrema[3]
    alpha = original.getchannel("A")
    low, high = alpha.getextrema()
    occupancy = "OPAQUE" if low == 255 else ("TRANSPARENT" if high == 0 else "MIXED")
    magnitude = ("EXACT" if not max_rgb and not max_alpha else
                 "ALPHA_ONLY" if not max_rgb else
                 "RGB_1" if max_rgb <= 1 else
                 "RGB_2_4" if max_rgb <= 4 else
                 "RGB_5_16" if max_rgb <= 16 else
                 "RGB_17_64" if max_rgb <= 64 else "RGB_65_255")
    # Deliberately keep format and sRGB to bounded, non-identifying classes.
    fmt = str(texture_format).upper()
    if fmt not in {"DXT1", "DXT5", "BC7", "RGBA32", "RGB24", "ETC2_RGBA8", "ASTC_RGBA_4X4"}:
        fmt = "OTHER_OR_UNKNOWN"
    cs = str(srgb).lower()
    color_space = "SRGB" if cs in ("true", "1", "srgb") else ("LINEAR" if cs in ("false", "0", "linear") else "UNKNOWN")
    return {"format": fmt, "color_space": color_space, "alpha_occupancy": occupancy,
            "max_rgb_delta_bin": magnitude, "alpha_delta": "NONE" if not max_alpha else "NONZERO"}

def aggregate(rows: list[dict[str, str]], *, expected: int) -> dict:
    if len(rows) != expected or expected <= 0:
        raise ValueError("incomplete authenticated scope")
    fields = ("format", "color_space", "alpha_occupancy", "max_rgb_delta_bin", "alpha_delta")
    allowed = {
        "format": {"DXT1", "DXT5", "BC7", "RGBA32", "RGB24", "ETC2_RGBA8", "ASTC_RGBA_4X4", "OTHER_OR_UNKNOWN"},
        "color_space": {"SRGB", "LINEAR", "UNKNOWN"},
        "alpha_occupancy": {"OPAQUE", "TRANSPARENT", "MIXED"},
        "max_rgb_delta_bin": {"EXACT", "ALPHA_ONLY", "RGB_1", "RGB_2_4", "RGB_5_16", "RGB_17_64", "RGB_65_255"},
        "alpha_delta": {"NONE", "NONZERO"},
    }
    if any(set(r) != set(fields) or any(r[f] not in allowed[f] for f in fields) for r in rows):
        raise ValueError("invalid diagnostic category")
    # Marginal aggregates only: avoid leaking identifiable joint metadata.
    return {"schema_version": 1, "scope": expected,
            "diagnostics": {f: dict(sorted(Counter(r[f] for r in rows).items())) for f in fields},
            "original_pixels_published": False, "device_validated": False}
