"""Strict source-safe summary of pre-extracted DXBC signature register contracts.

Does not infer semantic correspondence to SPIR-V.
"""
from collections import Counter

VALID_KINDS = {"input", "output"}


def summarize_signature(records):
    """Validate register component ownership and return aggregates only."""
    if not isinstance(records, list) or len(records) > 256:
        raise ValueError("invalid signature length")
    by_kind = {"input": [], "output": []}
    occupied = {"input": set(), "output": set()}
    for r in records:
        if not isinstance(r, dict) or set(r) != {"kind", "register", "mask", "system_value"}:
            raise ValueError("invalid record schema")
        kind, reg, mask, sys = (r[k] for k in ("kind", "register", "mask", "system_value"))
        if kind not in VALID_KINDS or type(reg) is not int or not 0 <= reg <= 4095 or type(mask) is not int or not 1 <= mask <= 15 or type(sys) is not bool:
            raise ValueError("invalid signature field")
        for channel in range(4):
            if mask & (1 << channel):
                key = (reg, channel)
                if key in occupied[kind]:
                    raise ValueError("overlapping register components")
                occupied[kind].add(key)
        by_kind[kind].append((reg, mask, sys))
    return {
        kind: {
            "records": len(by_kind[kind]),
            "registers": len({x[0] for x in by_kind[kind]}),
            "components": len(occupied[kind]),
            "system_value_records": sum(x[2] for x in by_kind[kind]),
            "mask_histogram": dict(sorted(Counter(x[1].bit_count() for x in by_kind[kind]).items())),
        }
        for kind in VALID_KINDS
    }
