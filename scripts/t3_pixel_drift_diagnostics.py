#!/usr/bin/env python3
"""Privacy-safe decoded texture drift diagnostics for SHA-authenticated pairs.

Never export pixels, GUIDs, filenames, hashes of images, or per-object rows.
This is a *diagnostic* of decoder/export differences, not a color correction.
"""
from __future__ import annotations

from collections import Counter
from PIL import Image, ImageChops

# Original serialized Unity TextureFormat codes (public Unity enum values).
# Explicit small allowlist: unrecognized or proprietary formats are pooled,
# never advertised as verified DXT/BC results from a guessed string.
SOURCE_FORMAT_CATEGORIES = {
    3: "RGB24", 4: "RGBA32", 10: "DXT1", 12: "DXT5",
    25: "BC7", 47: "ETC2_RGBA8", 48: "ASTC_RGBA_4X4",
}


def original_texture_categories(typetree: dict) -> tuple[str, str]:
    """Read typed source, not .read() attribute display or invented m_IsSRGB.

    The serialized source field m_ColorSpace is 0=Gamma, 1=Linear.
    Gamma is deliberately reported as GAMMA, not assumed equivalent to
    GPU sRGB sampling or exported TextureImporter.sRGBTexture.
    This function never returns raw format IDs, per-asset metadata or names.
    """
    if not isinstance(typetree, dict):
        raise ValueError("missing_authenticated_original_texture_typetree")
    fmt, space = typetree.get("m_TextureFormat"), typetree.get("m_ColorSpace")
    if type(fmt) is not int or fmt < 0 or type(space) is not int or space not in (0, 1):
        raise ValueError("invalid_original_texture_format_or_colorspace")
    return SOURCE_FORMAT_CATEGORIES.get(fmt, "OTHER_OR_UNKNOWN"), ("gamma" if space == 0 else "linear")

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
    color_space = ("GAMMA" if cs == "gamma" else
                   "SRGB" if cs in ("true", "1", "srgb") else
                   "LINEAR" if cs in ("false", "0", "linear") else "UNKNOWN")
    return {"format": fmt, "color_space": color_space, "alpha_occupancy": occupancy,
            "max_rgb_delta_bin": magnitude, "alpha_delta": "NONE" if not max_alpha else "NONZERO"}

def aggregate(rows: list[dict[str, str]], *, expected: int) -> dict:
    if len(rows) != expected or expected <= 0:
        raise ValueError("incomplete authenticated scope")
    fields = ("format", "color_space", "alpha_occupancy", "max_rgb_delta_bin", "alpha_delta")
    allowed = {
        "format": {"DXT1", "DXT5", "BC7", "RGBA32", "RGB24", "ETC2_RGBA8", "ASTC_RGBA_4X4", "OTHER_OR_UNKNOWN"},
        "color_space": {"GAMMA", "SRGB", "LINEAR", "UNKNOWN"},
        "alpha_occupancy": {"OPAQUE", "TRANSPARENT", "MIXED"},
        "max_rgb_delta_bin": {"EXACT", "ALPHA_ONLY", "RGB_1", "RGB_2_4", "RGB_5_16", "RGB_17_64", "RGB_65_255"},
        "alpha_delta": {"NONE", "NONZERO"},
    }
    if any(set(r) != set(fields) or any(r[f] not in allowed[f] for f in fields) for r in rows):
        raise ValueError("invalid diagnostic category")
    # Attribute RGB drift to broad codec groups, not individual assets.
    # Rare formats are pooled before the joint distribution is computed.
    # Never emit GUIDs, filenames, hashes, or per-object rows.
    format_counts = Counter(r["format"] for r in rows)
    by_format = {}
    for row in rows:
        fmt = row["format"] if format_counts[row["format"]] >= 5 else "POOLED_RARE_FORMATS"
        magnitude = row["max_rgb_delta_bin"]
        outcome = ("EXACT" if magnitude == "EXACT" else
                   "ALPHA_ONLY" if magnitude == "ALPHA_ONLY" else "RGB_DRIFT")
        by_format.setdefault(fmt, Counter())[outcome] += 1
    joint = {fmt: {key: counts.get(key, 0) for key in ("EXACT", "ALPHA_ONLY", "RGB_DRIFT")}
             for fmt, counts in sorted(by_format.items())}
    # A second safe joint aggregate makes a codec-only correlation less
    # likely to conflate Gamma (albedo) and Linear (data / masks).
    # Pool small color-space groups before publishing.
    space_counts = Counter(r["color_space"] for r in rows)
    by_space = {}
    for row in rows:
        space = row["color_space"] if space_counts[row["color_space"]] >= 5 else "POOLED_RARE_COLORSPACES"
        magnitude = row["max_rgb_delta_bin"]
        outcome = ("EXACT" if magnitude == "EXACT" else
                   "ALPHA_ONLY" if magnitude == "ALPHA_ONLY" else "RGB_DRIFT")
        by_space.setdefault(space, Counter())[outcome] += 1
    space_joint = {space: {key: counts.get(key, 0) for key in ("EXACT", "ALPHA_ONLY", "RGB_DRIFT")}
                   for space, counts in sorted(by_space.items())}
    return {"schema_version": 3, "scope": expected,
            "diagnostics": {f: dict(sorted(Counter(r[f] for r in rows).items())) for f in fields},
            "format_drift_summary": joint,
            "color_space_drift_summary": space_joint,
            "original_pixels_published": False, "device_validated": False}
