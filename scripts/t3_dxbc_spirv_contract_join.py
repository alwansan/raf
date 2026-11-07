#!/usr/bin/env python3
"""Synthetic DXBC-to-SPIR-V resource contract join. No private shader inputs.

Explicit provenance is mandatory: identical register/binding numbers are not
evidence of correspondence. This checks declared mappings, not pixel parity.
"""
from collections import Counter

FAMILIES = {"cbuffer", "texture", "sampler", "uav"}
STAGES = {"vertex", "fragment", "compute"}

def _key(item):
    return (item["stage"], item["family"], item["register"])

def _nonnegative_int(value):
    """Resource coordinates are integer indices, never booleans or floats."""
    return type(value) is int and value >= 0


def check_contract(dx_resources, spv_resources, provenance):
    """Return sorted diagnostic codes; empty means declared contract is consistent.

    DX: stage/family/register/count. SPV: stage/family/set/binding/count.
    Provenance: stage/family/register/set/binding/count; one explicit row
    per DX resource. Count models array span, not just descriptor base.
    """
    # Fail closed on incomplete reflection records instead of throwing KeyError.
    schemas = (
        (dx_resources, {"stage", "family", "register", "count"}),
        (spv_resources, {"stage", "family", "set", "binding", "count"}),
        (provenance, {"stage", "family", "register", "set", "binding", "count"}),
    )
    if any(not isinstance(group, (list, tuple)) or any(
        not isinstance(item, dict) or not required.issubset(item)
        for item in group) for group, required in schemas):
        return ["invalid_schema"]
    # A row must belong to exactly one coordinate namespace. Extra keys from
    # the other namespace can otherwise reach missing-field indexing paths.
    for group, forbidden in ((dx_resources, {"set", "binding"}),
                             (spv_resources, {"register"}),
                             (provenance, set())):
        if any(forbidden.intersection(item) for item in group):
            return ["invalid_schema"]
    # Reflection JSON may contain arrays/objects instead of scalar stage/family.
    # Validate before constructing hash keys or Counter dictionaries.
    if any(type(item["stage"]) is not str or type(item["family"]) is not str
           for group in (dx_resources, spv_resources, provenance) for item in group):
        return ["invalid_schema"]
    # Validate coordinates before constructing hash-based keys. Reflection input
    # may contain arrays/objects in numeric fields; fail closed without TypeError.
    for group in (dx_resources, spv_resources, provenance):
        for item in group:
            if type(item["count"]) is not int or item["count"] <= 0:
                return ["invalid_count"]
            coordinates = ("register",) if "register" in item else ("set", "binding")
            if "set" in item and "register" in item:
                coordinates = ("register", "set", "binding")
            if any(not _nonnegative_int(item[field]) for field in coordinates):
                return ["invalid_coordinate"]
    errors = []
    dx_keys = [_key(x) for x in dx_resources]
    spv_keys = [(x["stage"], x["family"], x["set"], x["binding"]) for x in spv_resources]
    map_keys = [_key(x) for x in provenance]
    targets = [(x["stage"], x["family"], x["set"], x["binding"]) for x in provenance]
    for label, keys in (("dx", dx_keys), ("spv", spv_keys),
                        ("provenance", map_keys), ("target", targets)):
        if any(n > 1 for n in Counter(keys).values()):
            errors.append("duplicate_" + label)
    for group in (dx_resources, spv_resources, provenance):
        for item in group:
            if item["stage"] not in STAGES or item["family"] not in FAMILIES:
                errors.append("unknown_stage_or_family")
            if type(item["count"]) is not int or item["count"] <= 0:
                errors.append("invalid_count")
            coordinates = ("register",) if "register" in item else ("set", "binding")
            if "set" in item and "register" in item:
                coordinates = ("register", "set", "binding")
            if any(not _nonnegative_int(item[field]) for field in coordinates):
                errors.append("invalid_coordinate")
    dx = {_key(x): x for x in dx_resources}
    spv = {(x["stage"], x["family"], x["set"], x["binding"]): x for x in spv_resources}
    mapping = {_key(x): x for x in provenance}
    if set(dx) != set(mapping):
        errors.append("missing_or_extra_provenance")
    if set(spv) != set(targets):
        errors.append("unmapped_or_extra_descriptor")
    for key in set(dx) & set(mapping):
        m = mapping[key]
        target = (m["stage"], m["family"], m["set"], m["binding"])
        if target not in spv:
            errors.append("target_missing")
            continue
        if dx[key]["count"] != m["count"] or spv[target]["count"] != m["count"]:
            errors.append("array_span_mismatch")
    return sorted(set(errors))
