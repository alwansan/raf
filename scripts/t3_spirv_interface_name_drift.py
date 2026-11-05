"""T3: classify SPIRV-Cross *reflected names*, not true source DXBC semantics.

Original vkd3d SPIR-V and derivative HLSL/roundtrip SPIR-V remain private.
This compares exact type/name/mapped Location without copying names/IDs/hashes
to public reports. A reflected name may be compiler-generated or renamed;
this is *not* a D3D signature semantic, interpolation or pixel parity proof.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess

SIDES = ("inputs", "outputs")
FIELDS = (
    "source_located", "roundtrip_located",
    "source_located_without_name", "roundtrip_located_without_name",
    "source_unlocated_entries", "roundtrip_unlocated_entries",
    "source_named", "roundtrip_named",
    "source_name_type_matches", "source_name_type_same_location",
    "source_name_type_relocated", "same_name_different_type",
    "source_only_names", "roundtrip_only_names",
    "name_type_complete_preservation", "name_type_relocation_only_candidate",
    "name_comparison_incomplete",
)
BOOLEAN_FIELDS = frozenset((
    "name_type_complete_preservation",
    "name_type_relocation_only_candidate",
    "name_comparison_incomplete",
))


def read_reflection(path: Path):
    """Read private full reflection into memory only; omit stdout/stderr on failure."""
    if not isinstance(path, Path) or path.is_symlink() or not path.is_file():
        raise ValueError("missing_or_unsafe_private_spirv_reflection_input")
    if not 0 < path.stat().st_size <= 2 * 1024 * 1024:
        raise ValueError("private_spirv_input_outside_bounded_size")
    out = subprocess.run(["spirv-cross", str(path), "--reflect"],
                         capture_output=True, timeout=30, check=False)
    if out.returncode != 0 or not 0 < len(out.stdout) <= 1024 * 1024:
        raise ValueError("private_spirv_interface_reflection_unavailable")
    try:
        data = json.loads(out.stdout)
    except (ValueError, UnicodeError) as err:
        raise ValueError("private_spirv_interface_reflection_invalid_json") from None
    if type(data) is not dict:
        raise ValueError("untrusted_private_spirv_reflection_root")
    return data


def _collect(raw: dict, sanitized: dict, side: str):
    """Trust each located source row only after matching existing safe parser."""
    if (type(raw) is not dict or type(sanitized) is not dict or
        type(raw.get(side, [])) is not list or
        len(raw.get(side, [])) > 256 or
        type(sanitized.get(side)) is not list or
        len(sanitized[side]) > 256):
        raise ValueError("invalid_source_or_roundtrip_spirv_interface_shape")
    records, unlocated, unnamed = {}, 0, 0
    locations = {}
    for row in raw.get(side, []):
        if type(row) is not dict:
            raise ValueError("invalid_private_spirv_reflection_entry")
        if "location" not in row:
            # Built-ins and other unlocated rows are outside this comparison.
            unlocated += 1
            continue
        loc, typ = row["location"], row.get("type")
        if (type(loc) is not int or not 0 <= loc <= 65535 or
            type(typ) is not str or not 0 < len(typ) <= 128 or loc in locations):
            raise ValueError("invalid_or_duplicate_private_spirv_location_type")
        locations[loc] = typ
        name = row.get("name")
        if name is None or name == "":
            unnamed += 1
            continue
        if (type(name) is not str or not 0 < len(name) <= 256 or
            any(ord(c) < 32 or ord(c) == 127 for c in name) or
            name in records):
            raise ValueError("invalid_or_duplicate_private_spirv_reflection_name")
        records[name] = (typ, loc)
    expected = {}
    for row in sanitized[side]:
        if (type(row) is not dict or set(row) != {"type", "location"} or
            type(row["location"]) is not int or
            type(row["type"]) is not str or
            row["location"] in expected):
            raise ValueError("invalid_legacy_source_spirv_interface_shape")
        expected[row["location"]] = row["type"]
    if locations != expected:
        raise ValueError("private_reflection_name_data_disagrees_with_safe_IO_baseline")
    return records, len(locations), unlocated, unnamed


def classify_reflected_names(src: dict, derived: dict,
                             sanitized_source: dict, sanitized_derived: dict):
    """Counts only: synthetic compiler names needn't equal original DXBC semantics."""
    result = {}
    for side in SIDES:
        a, a_total, a_unlocated, a_unnamed = _collect(src, sanitized_source, side)
        b, b_total, b_unlocated, b_unnamed = _collect(derived, sanitized_derived, side)
        names_a, names_b = set(a), set(b)
        common = names_a & names_b
        paired = {name for name in common if a[name][0] == b[name][0]}
        moved = sum(a[name][1] != b[name][1] for name in paired)
        same_loc = len(paired) - moved
        complete = (a_unnamed == b_unnamed == 0 and
                    names_a == names_b and len(paired) == len(names_a) and
                    a_total == b_total)
        data = {
            "source_located": a_total,
            "roundtrip_located": b_total,
            "source_located_without_name": a_unnamed,
            "roundtrip_located_without_name": b_unnamed,
            "source_unlocated_entries": a_unlocated,
            "roundtrip_unlocated_entries": b_unlocated,
            "source_named": len(a),
            "roundtrip_named": len(b),
            "source_name_type_matches": len(paired),
            "source_name_type_same_location": same_loc,
            "source_name_type_relocated": moved,
            "same_name_different_type": len(common) - len(paired),
            "source_only_names": len(names_a - names_b),
            "roundtrip_only_names": len(names_b - names_a),
            "name_type_complete_preservation": int(complete),
            "name_type_relocation_only_candidate": int(
                complete and moved > 0),
            "name_comparison_incomplete": int(
                a_unnamed > 0 or b_unnamed > 0),
        }
        if set(data) != set(FIELDS):
            raise ValueError("bad_public_reflected_name_comparison_shape")
        result.update({side + "_" + key: val for key, val in data.items()})
    # Never serialize a source/roundtrip name, original bytecode, per-program
    # identifier, path, raw reflection JSON, or even a per-stage report.
    return result
