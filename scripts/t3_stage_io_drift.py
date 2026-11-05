"""Privacy-safe aggregate classification of SPIR-V stage IO reflection drift.

Inputs are previously sanitized reflection dictionaries. No source identifiers,
private type strings, program records or hashes are returned.
"""
from collections import Counter


def _interface(rows):
    if type(rows) is not list or len(rows) > 256:
        raise ValueError("untrusted_stage_interface")
    seen = set()
    result = {}
    for row in rows:
        if type(row) is not dict or set(row) != {"location", "type"}:
            raise ValueError("untrusted_stage_interface_entry")
        loc, kind = row["location"], row["type"]
        if (type(loc) is not int or not 0 <= loc <= 65535 or
                type(kind) is not str or not kind or len(kind) > 64):
            raise ValueError("untrusted_stage_interface_value")
        if loc in seen:
            raise ValueError("duplicate_stage_location")
        seen.add(loc)
        result[loc] = kind
    return result


def classify_stage_io(original, roundtrip):
    """Aggregate location/type drift without returning raw interface details."""
    if type(original) is not dict or type(roundtrip) is not dict:
        raise ValueError("untrusted_stage_reflection")
    out = Counter()
    for side in ("inputs", "outputs"):
        a, b = _interface(original.get(side)), _interface(roundtrip.get(side))
        prefix = side + "_"
        out[prefix + "identical"] = int(a == b)
        out[prefix + "original_slots"] = len(a)
        out[prefix + "roundtrip_slots"] = len(b)
        out[prefix + "removed_locations"] = len(a.keys() - b.keys())
        out[prefix + "added_locations"] = len(b.keys() - a.keys())
        out[prefix + "same_location_type_changes"] = sum(a[k] != b[k] for k in a.keys() & b.keys())
        out[prefix + "type_multiset_equal"] = int(sorted(a.values()) == sorted(b.values()))
        out[prefix + "location_only_remap_candidate"] = int(
            a != b and sorted(a.values()) == sorted(b.values()))
    return dict(out)
