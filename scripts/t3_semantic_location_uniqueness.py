"""Source-free conservative uniqueness gate for shader varying candidate mapping.

Does not derive authored DXBC semantics or identify real Android shader bindings.
A mapping is usable only when exactly one full bijection satisfies supplied
compatibility edges. Duplicate typed varyings without further proof fail closed.
"""
from __future__ import annotations


def unique_bijection(edges: dict[int, set[int]]) -> dict[int, int] | None:
    """Return unique complete left-to-right mapping; None if none or ambiguous.

    Inputs are bounded and must be exact integer locations (not booleans).
    Edges must name exactly the same number of distinct right-side locations
    as left-side locations. More than one valid matching is never guessed.
    """
    if type(edges) is not dict or not 1 <= len(edges) <= 12:
        raise ValueError('invalid_location_scope')
    left = set(edges)
    if any(type(k) is not int or not 0 <= k < 65536 for k in left):
        raise ValueError('invalid_left_location')
    right: set[int] = set()
    for values in edges.values():
        if type(values) is not set or not values:
            raise ValueError('invalid_candidate_set')
        if any(type(v) is not int or not 0 <= v < 65536 for v in values):
            raise ValueError('invalid_right_location')
        right.update(values)
    if len(right) != len(left):
        return None
    ordered = sorted(left, key=lambda k: (len(edges[k]), k))
    found: list[dict[int, int]] = []

    def visit(i: int, used: set[int], mapping: dict[int, int]) -> None:
        if len(found) >= 2:
            return
        if i == len(ordered):
            found.append(mapping.copy())
            return
        key = ordered[i]
        for value in sorted(edges[key] - used):
            mapping[key] = value
            visit(i + 1, used | {value}, mapping)
            del mapping[key]
            if len(found) >= 2:
                return

    visit(0, set(), {})
    return found[0] if len(found) == 1 else None
