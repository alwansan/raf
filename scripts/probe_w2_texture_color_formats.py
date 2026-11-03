"""Aggregate the original Texture2D ``(m_TextureFormat, m_ColorSpace)`` pairs
across the two SHA-pinned original payload owners.

Purpose: the original project builds in **Linear** color space (see
``probe_w2_color_space_settings``). Texture-level color-space labels then show
whether the original stored albedo textures with sRGB color-space evaluation
(``m_ColorSpace == 0``, ``ColorSpace.Gamma``) and data textures (normal maps,
masks) linear (``m_ColorSpace == 1``), which is the pipeline the Android port
must reproduce to avoid washed-out, pale surfaces.

CPU-only, read-only; the two payload owners are exactly those pinned by
``scripts.verify_targeted_lfs_compute_sources`` (full SHA256 verified before
parsing). Output is aggregate-only: integer format/color-space pairs with
counts. Object names, path IDs and image payload bytes are never emitted.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

SCHEMA_VERSION = 1

OWNERS = ("resources.assets", "sharedassets0.assets")

VALID_TEXTURE_COLOR_SPACES = {0: "Gamma", 1: "Linear"}


def parse_owner(path: Path) -> dict:
    """Return aggregate counts for one owner (never any per-object data)."""
    import UnityPy

    env = UnityPy.load(str(path))
    pairs = collections.Counter()
    dims = collections.Counter()
    format_values = collections.Counter()
    texture_count = 0
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        texture_count += 1
        tree = obj.read_typetree()
        cs = tree.get("m_ColorSpace")
        if cs not in VALID_TEXTURE_COLOR_SPACES:
            raise ValueError(
                f"Texture2D m_ColorSpace outside engine enum: {cs!r}"
            )
        fmt = tree.get("m_TextureFormat")
        if not isinstance(fmt, int):
            raise ValueError(f"Texture2D m_TextureFormat not an int: {fmt!r}")
        pairs[(int(fmt), int(cs))] += 1
        format_values[int(fmt)] += 1
        dims[int(tree.get("m_Width")), int(tree.get("m_Height"))] += 1
    return {
        "texture_count": texture_count,
        "format_colorspace_pairs": [
            {"format": f, "colorspace": c, "colorspace_label": VALID_TEXTURE_COLOR_SPACES[c], "count": n}
            for (f, c), n in sorted(pairs.items())
        ],
        "distinct_formats": len(format_values),
        "largest_repeated_resolutions": [
            {"width": w, "height": h, "count": n}
            for (w, h), n in dims.most_common(5)
        ],
    }


def probe(root: Path) -> dict:
    verify_sources(root, expected={n: EXPECTED[n] for n in OWNERS})
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owners": {},
    }
    for name in OWNERS:
        result["owners"][name] = parse_owner(root / name)
    blob = json.dumps(result, sort_keys=True)
    forbidden = (b"m_Name", b"m_PathID", b"m_Script")
    low = blob.encode().lower().decode()
    for key in (b"m_name", b"m_pathid", b"m_script"):
        if key.decode() in low:
            raise ValueError("aggregate output contains a forbidden field key")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="Original Raft_Data root directory")
    parser.add_argument("--out", required=True, help="Aggregate JSON output path")
    args = parser.parse_args(argv)
    result = probe(Path(args.source))
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(f"{{\"aggregate_written\": {json.dumps(args.out)}, \"no_proprietary_payload\": true}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
