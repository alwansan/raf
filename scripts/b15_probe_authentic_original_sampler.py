#!/usr/bin/env python3
"""B15: real SHA-authenticated ZIP2 Texture2D sampler typed-input acceptance.

This checks ORIGINAL source objects only. It does not compare any exported
TextureImporter or recover a shader, texture, color, pixel or Android runtime.
No proprietary names, path IDs, actual float values or asset bytes are emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.b15_texture_sampler_parity import SOURCE_PINS, _authenticate, original_sampler

OWNER = "sharedassets6.assets"
EXPECTED_TEXTURES = 87
PIN = (6_607_272, "0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632")


def inspect_original(path: Path, *, expected_pin=PIN, expected_textures=EXPECTED_TEXTURES) -> dict:
    if (path.name != OWNER or not path.is_file()
            or any(part.is_symlink() for part in (path, *path.parents))):
        raise ValueError("missing or redirected selected original texture owner")
    if SOURCE_PINS.get(OWNER) != PIN:
        raise ValueError("production B15 original owner pin unexpectedly changed")
    _authenticate(path, *expected_pin)

    import UnityPy
    env = UnityPy.load(str(path))
    seen_ids = set()
    filter_histogram = Counter()
    wrap_histogram = Counter()
    mip_bias_nonzero = 0
    count = 0
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        pid = obj.path_id
        if type(pid) is not int or not pid or pid in seen_ids:
            raise ValueError("invalid or duplicated original Texture2D identity")
        seen_ids.add(pid)
        filtering, anisotropy, bias, wrap_u, wrap_v, wrap_w = original_sampler(obj.read_typetree())
        filter_histogram[filtering] += 1
        for value in (wrap_u, wrap_v, wrap_w):
            wrap_histogram[value] += 1
        mip_bias_nonzero += (bias != 0.0)
        count += 1

    if count != expected_textures:
        raise ValueError("SHA-verified original Texture2D count differed from W2 baseline")
    if sum(filter_histogram.values()) != count or sum(wrap_histogram.values()) != count * 3:
        raise AssertionError("original sampler field coverage incomplete")
    # W2 authenticated all 4,050 original textures: zero nonzero mip biases.
    if mip_bias_nonzero:
        raise ValueError("original sampled mip bias disagrees with authenticated W2 baseline")

    return {
        "schema_version": 1,
        "selected_original_owner_sha256_verified": True,
        "selected_original_owner_bytes_verified": True,
        "selected_original_texture_count": count,
        "typed_sampler_settings_decoded": count,
        "filter_enum_slots_checked": sum(filter_histogram.values()),
        "wrap_enum_slots_checked": sum(wrap_histogram.values()),
        "source_mip_bias_nonzero_count": mip_bias_nonzero,
        "source_scope": "one-pinned-zip2-owner",
        "full_original_game_coverage": False,
        "same_export_identity_verified": False,
        "exported_importer_compared": False,
        "unity_or_android_pixels_verified": False,
        "modified_game_assets": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original", type=Path, required=True, help="SHA-verified owner file")
    ap.add_argument("--out", type=Path, required=True, help="aggregate JSON outside original source")
    args = ap.parse_args()
    if (args.out.is_symlink() or args.out.resolve().is_relative_to(args.original.resolve().parent)):
        raise ValueError("aggregate report path must be separate from original")
    result = inspect_original(args.original)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("RAFT_B15_ORIGINAL_SAMPLER_SOURCE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
