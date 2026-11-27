"""Fail-closed source and serialized keyword-set contracts (no Unity execution)."""
import re

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\Z")
_PRIVATE_PREFIX = "GT_ORIGINAL_921_"


def keyword_set(names):
    """Reject duplicates, private selectors and unproved identifier spellings."""
    if (type(names) not in (list, tuple)
            or any(type(name) is not str or not _IDENTIFIER.fullmatch(name)
                   or name.startswith(_PRIVATE_PREFIX) for name in names)
            or len(set(names)) != len(names)):
        raise ValueError("original_runtime_keyword_set_invalid")
    return frozenset(names)


def exact_independent_toggle_plan(keys):
    """Independent multi_compile dimensions must cover their entire powerset.

    Sparse lattices require a separately proved pragma grouping. Never fill
    missing combinations with the first program, even for an import default.
    This proves names/route coverage, not Unity keyword scope or rendering.
    """
    if type(keys) not in (list, tuple) or not keys:
        raise ValueError("original_runtime_routes_missing")
    sets = [keyword_set(key) for key in keys]
    if len(set(sets)) != len(sets):
        raise ValueError("original_runtime_route_collision")
    names = sorted(set().union(*sets))
    if len(sets) != 1 << len(names):
        raise ValueError("original_runtime_sparse_keyword_lattice_unproved")
    return names, sets


def strict_engine_router(keys, programs):
    """Emit exact branches for a proved independent-toggle lattice only."""
    names, sets = exact_independent_toggle_plan(keys)
    if (type(programs) is not dict
            or any(type(index) is not int for index in programs)
            or set(programs) != set(range(len(sets)))
            or any(type(code) is not str or not code.strip()
                   for code in programs.values())):
        raise ValueError("original_runtime_route_program_table_invalid")
    pragmas = ["#pragma multi_compile __ " + name for name in names
               if name != "INSTANCING_ON"]
    if "INSTANCING_ON" in names:
        pragmas.append("#pragma multi_compile_instancing")
    lines = []
    for index, enabled in enumerate(sets):
        condition = " && ".join(("" if name in enabled else "!") +
                                 "defined(" + name + ")" for name in names) or "1"
        lines.extend([("#elif " if index else "#if ") + condition, programs[index]])
    lines.extend(["#else", "#error Unmapped_original_keyword_set", "#endif", ""])
    return pragmas, "\n".join(lines)


def strict_bundle_route_key(keyword_names, row, expected_keys):
    """Match the entire decoded row, never a projection onto expected names.

    Nonempty separate global/local index lanes need their own source-proved
    mapping; until then they cannot participate in a strict receipt.
    """
    keyword_set(keyword_names)
    if any(type(row.get(field, [])) is not list or row.get(field, [])
           for field in ("m_GlobalKeywordIndices", "m_LocalKeywordIndices")):
        raise ValueError("original_runtime_keyword_scope_unproved")
    indices = row.get("m_KeywordIndices")
    if (type(indices) is not list
            or any(type(index) is not int or not 0 <= index < len(keyword_names)
                   for index in indices)
            or len(set(indices)) != len(indices)):
        raise ValueError("original_runtime_bundle_keyword_indices_invalid")
    active = keyword_set([keyword_names[index] for index in indices])
    if active not in expected_keys:
        raise ValueError("original_runtime_bundle_unmapped_exact_keyword_set")
    return active
