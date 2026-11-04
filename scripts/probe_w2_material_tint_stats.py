"""Aggregate original Material color-tint usage across the two SHA-pinned
original payload owners.

Purpose: the pale-surface color-loss chain's final material-level ring. For
every serialized material color property (``m_SavedProperties.m_Colors``),
emit aggregate-only counters that constrain a faithful port: whether the
property is used at all, how many materials keep it at the identity tint
``(1,1,1,1)``, how many deviate, have alpha below 1 (blended tint) or any
component outside [0,1] (HDR/negative). If a port loses these tints (e.g.
renders every material at the identity tint), colors wash out even when the
global color space and texture flags are correct.

CPU-only, read-only; owners exactly ``resources.assets`` and
``sharedassets0.assets`` pinned via ``scripts.verify_targeted_lfs_compute_sources``
(full SHA256 verified before parsing). Output publishes:
- per material: only integer counters;
- per property name: only counter tables (property names are engine packaging
  metadata; W3's precedent publishes comparable name keys);
- never any color float values, property lists, object names, path IDs or
  payload bytes.

Fail-closed: entry shape deviations (not a 2-tuple, second not an rgba dict)
hard-fail; the output blob rejects forbidden keys (m_Name, m_PathID,
m_Shader, m_ValidKeywords) and rejects any float-like color value that could
leak payloads (best-effort literal scan).
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
import re
import sys

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

SCHEMA_VERSION = 1

OWNERS = ("resources.assets", "sharedassets0.assets")

IDENTITY = (1.0, 1.0, 1.0, 1.0)
EPS = 1e-6

VALUE_SCANNER = re.compile(r'-?\d+\.\d+')


def _color_vector(entry) -> tuple:
    second = entry[1]
    vec = (second["r"], second["g"], second["b"], second["a"])
    for component in vec:
        if not isinstance(component, (int, float)) or isinstance(component, bool):
            raise ValueError(f"non-numeric color component: {component!r}")
        if isinstance(component, float) and math.isnan(component):
            raise ValueError("NaN color component must fail closed")
    return tuple(float(c) for c in vec)


def parse_owner(path: Path) -> dict:
    """Aggregate one owner's material color tints (no per-object data)."""
    import UnityPy

    env = UnityPy.load(str(path))
    material_count = 0
    per_name = collections.defaultdict(
        lambda: {
            "materials_using": 0,
            "identity_tint": 0,
            "non_identity_tint": 0,
            "alpha_below_1": 0,
            "component_outside_unit": 0,
            "non_finite_component": 0,
        }
    )
    materials_with_non_default_tint = 0
    materials_only_identity = 0
    materials_without_colors = 0

    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        tree = obj.read_typetree()
        saved = tree.get("m_SavedProperties")
        if not isinstance(saved, dict):
            raise ValueError("m_SavedProperties missing/not a dict")
        colors = saved.get("m_Colors")
        if colors is None or not isinstance(colors, list):
            raise ValueError("m_SavedProperties.m_Colors missing/not a list")
        material_count += 1
        any_non_default = False
        used_any = False
        for entry in colors:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                raise ValueError(f"unexpected m_Colors entry shape: {type(entry).__name__}")
            name, second = entry[0], entry[1]
            if not isinstance(name, str) or not isinstance(second, dict) or set(second) != {"r", "g", "b", "a"}:
                raise ValueError(f"unexpected m_Colors entry content: keys={sorted(second) if isinstance(second, dict) else type(second).__name__}")
            used_any = True
            vec = _color_vector(entry)
            stats = per_name[name]
            stats["materials_using"] += 1
            is_identity = all(abs(vec[i] - IDENTITY[i]) <= EPS for i in range(4))
            if is_identity:
                stats["identity_tint"] += 1
            else:
                stats["non_identity_tint"] += 1
                any_non_default = True
            if vec[3] < 1.0 - EPS:
                stats["alpha_below_1"] += 1
                any_non_default = True
            if any(math.isinf(c) for c in vec):
                stats["non_finite_component"] += 1
            if any(c < -EPS or c > 1.0 + EPS for c in vec):
                stats["component_outside_unit"] += 1
        if not used_any:
            materials_without_colors += 1
        elif any_non_default:
            materials_with_non_default_tint += 1
        else:
            materials_only_identity += 1

    return {
        "material_count": material_count,
        "materials_with_non_default_tint": materials_with_non_default_tint,
        "materials_only_identity_tint": materials_only_identity,
        "materials_without_colors": materials_without_colors,
        "per_property_name": {name: dict(stats) for name, stats in sorted(per_name.items())},
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
    for forbidden in ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords", "stringTagMap"):
        if forbidden in blob:
            raise ValueError(f"aggregate output contains forbidden field key: {forbidden}")
    # best-effort guard: no long float chains that could carry color payloads
    for match in VALUE_SCANNER.findall(blob):
        if float(match) not in (0.0, 1.0):
            raise ValueError(f"non-trivial float literal leaked into aggregate: {match}")
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
