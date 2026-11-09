"""Fail-closed synthetic semantic-to-SPIR-V location provenance validator.

No automatic semantic reconstruction: explicit authenticated mapping required.
Never publish private semantic names, compiled programs or resource identifiers.
"""
from collections import Counter


def validate(original, reflected, mapping):
    """Return safe aggregate result; malformed/unproven inputs are INCONCLUSIVE.\n\n    Used DXBC lanes may be a strict subset of declared SPIR-V lanes;\n    unmatched declared lanes are not automatically evidence of data loss.

    original: iterable of (opaque_semantic_id, component) used original lanes
    reflected: iterable of (location, component) reflected SPIR-V lanes
    mapping: iterable of (opaque_semantic_id, original_component, location, spv_component)
    Opaque IDs must be authenticated by an upstream original-source extractor.
    """
    result = {"status": "INCONCLUSIVE", "original_lanes": 0,
              "reflected_lanes": 0, "mapped_lanes": 0, "reason": "invalid_input"}
    try:
        if not all(isinstance(x, (list, tuple)) for x in (original, reflected, mapping)):
            return result
        if any(not isinstance(x, (list, tuple)) or len(x) != 2 for x in original):
            return result
        if any(not isinstance(x, (list, tuple)) or len(x) != 2 for x in reflected):
            return result
        if any(not isinstance(x, (list, tuple)) or len(x) != 4 for x in mapping):
            return result
        o = [tuple(x) for x in original]
        r = [tuple(x) for x in reflected]
        m = [tuple(x) for x in mapping]
        if any(not isinstance(s, str) or not s or not isinstance(c, int) or isinstance(c, bool) or c not in range(4) for s,c in o):
            return result
        if any(not isinstance(l, int) or isinstance(l, bool) or l < 0 or not isinstance(c, int) or isinstance(c, bool) or c not in range(4) for l,c in r):
            return result
        if any(not isinstance(s, str) or not s or not isinstance(c, int) or isinstance(c, bool) or c not in range(4) or not isinstance(l, int) or isinstance(l, bool) or l < 0 or not isinstance(d, int) or isinstance(d, bool) or d not in range(4) for s,c,l,d in m):
            return result
        result.update(original_lanes=len(o), reflected_lanes=len(r), mapped_lanes=len(m))
        if not o or not r or not m:
            result["reason"] = "missing_provenance"
        elif any(v != 1 for v in Counter(o).values()) or any(v != 1 for v in Counter(r).values()):
            result["reason"] = "duplicate_source_lane"
        elif len(m) != len(o) or len(m) > len(r):
            result["reason"] = "incomplete_coverage"
        elif Counter((s,c) for s,c,_,_ in m) != Counter(o):
            result["reason"] = "source_mismatch_or_ambiguous"
        elif any(count > Counter(r)[key] for key, count in Counter((l,d) for _,_,l,d in m).items()):
            result["reason"] = "location_mismatch_or_ambiguous"
        else:
            result.update(status="STRUCTURAL_INJECTION_ONLY", reason="requires_authentic_provenance_and_unused_lane_audit", unused_reflected_lanes=len(r)-len(m))
        return result
    except (TypeError, ValueError):
        return result
