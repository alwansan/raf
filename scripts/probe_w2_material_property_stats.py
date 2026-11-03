"""Aggregate original Material serialized render/keyword property statistics
across the two SHA-pinned original payload owners.

Purpose: complete the pale-surface color-loss chain with material-level
serialization aggregates that constrain any Android port's render setup:
custom render-queue overrides, lightmap flags, instancing/double-sided-GI
toggles, and keyword / disabled-pass / saved-property entry counts.

CPU-only, read-only; the two owners are exactly those pinned by
``scripts.verify_targeted_lfs_compute_sources`` (full SHA256 verified before
parsing). Output is aggregate-only: integer/sub-aggregate distributions with
counts. Material names, shader PPtrs/path IDs, keyword strings, property
names, colors and any payload data are never emitted (forbidden-key check).
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


def _distribution(counter: collections.Counter, limit: int = 12) -> list:
    return [
        {"value": value, "count": count}
        for value, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
    ]


def parse_owner(path: Path) -> dict:
    """Aggregate one owner's Materials (never any per-object data)."""
    import UnityPy

    env = UnityPy.load(str(path))
    material_count = 0
    custom_render_queue = collections.Counter()
    lightmap_flags = collections.Counter()
    instancing_true = 0
    double_sided_gi_true_count = 0
    valid_keywords_count = collections.Counter()
    disabled_passes_count = collections.Counter()
    saved_colors_count = collections.Counter()
    saved_floats_count = collections.Counter()
    saved_ints_count = collections.Counter()
    saved_texenvs_count = collections.Counter()

    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        tree = obj.read_typetree()
        material_count += 1
        queue = tree.get("m_CustomRenderQueue")
        if not isinstance(queue, int):
            raise ValueError(f"m_CustomRenderQueue not an int: {queue!r}")
        custom_render_queue[int(queue)] += 1
        flags = tree.get("m_LightmapFlags")
        if not isinstance(flags, int):
            raise ValueError(f"m_LightmapFlags not an int: {flags!r}")
        lightmap_flags[int(flags)] += 1
        if bool(tree.get("m_EnableInstancingVariants")):
            instancing_true += 1
        if bool(tree.get("m_DoubleSidedGI")):
            double_sided_gi_true_count += 1
        valid_keywords = tree.get("m_ValidKeywords") or []
        if not isinstance(valid_keywords, list):
            raise ValueError("m_ValidKeywords is not a list")
        valid_keywords_count[len(valid_keywords)] += 1
        disabled = tree.get("disabledShaderPasses") or []
        if not isinstance(disabled, list):
            raise ValueError("disabledShaderPasses is not a list")
        disabled_passes_count[len(disabled)] += 1
        saved = tree.get("m_SavedProperties")
        if not isinstance(saved, dict):
            raise ValueError("m_SavedProperties missing/not a dict")
        for field, counter, label in (
            ("m_TexEnvs", saved_texenvs_count, "m_TexEnvs"),
            ("m_Floats", saved_floats_count, "m_Floats"),
            ("m_Ints", saved_ints_count, "m_Ints"),
            ("m_Colors", saved_colors_count, "m_Colors"),
        ):
            entries = saved.get(field)
            if entries is None or not isinstance(entries, list):
                raise ValueError(f"{label} missing/not a list")
            counter[len(entries)] += 1

    return {
        "material_count": material_count,
        "custom_render_queue_distribution": _distribution(custom_render_queue),
        "distinct_custom_render_queue_values": len(custom_render_queue),
        "lightmap_flags_distribution": _distribution(lightmap_flags),
        "instancing_enabled_materials": instancing_true,
        "double_sided_gi_materials": double_sided_gi_true_count,
        "valid_keywords_materials_distribution": _distribution(valid_keywords_count),
        "disabled_passes_materials_distribution": _distribution(disabled_passes_count),
        "saved_colors_entry_distribution": _distribution(saved_colors_count),
        "saved_floats_entry_distribution": _distribution(saved_floats_count),
        "saved_ints_entry_distribution": _distribution(saved_ints_count),
        "saved_texenvs_entry_distribution": _distribution(saved_texenvs_count),
    }


def probe(root: Path) -> dict:
    verify_sources(root, expected={n: EXPECTED[n] for n in OWNERS})
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owners": {name: parse_owner(root / name) for name in OWNERS},
    }
    blob = json.dumps(result)
    for forbidden in ("m_Name", "m_Shader", "m_PathID", "m_ValidKeywords", "stringTagMap"):
        if forbidden in blob:
            raise ValueError(f"aggregate output contains forbidden field key: {forbidden}")
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
