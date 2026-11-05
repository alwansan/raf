"""Conservative source-free VS output -> FS input SPIR-V component coverage.

Consumes *sanitized* SPIRV-Cross reflection records only. This does not parse
original DXBC signatures or establish DXBC semantic/interpolation compatibility.
Never return source-provided locations, names, types, paths, bytecode, or hashes.
"""
from __future__ import annotations

import re

MAX_RECORDS = 256
MAX_LOCATION = 65535
_TYPE_RE = re.compile(r"(float|int|uint|bool|[iub]?vec[234])\Z")
_BUILTINS = frozenset({
    "Position", "PointSize", "ClipDistance", "CullDistance", "PrimitiveId",
    "Layer", "ViewportIndex", "FragCoord", "FrontFacing", "SampleId",
    "SampleMask", "FragDepth", "VertexId", "InstanceId",
})


def _type_components(value):
    """Return (family, count) or None; unknown widths are not guessed."""
    if type(value) is not str or len(value) > 16:
        raise ValueError("invalid sanitized SPIR-V type")
    if not _TYPE_RE.fullmatch(value):
        return None
    if value in ("float", "int", "uint", "bool"):
        return (value, 1)
    prefix = value[:-4] if value.endswith("vec2") or value.endswith("vec3") or value.endswith("vec4") else ""
    family = {"": "float", "i": "int", "u": "uint", "b": "bool"}.get(prefix)
    if family is None:
        raise ValueError("unhandled SPIR-V vector type")
    return (family, int(value[-1]))


def _collect(rows):
    if type(rows) is not list or len(rows) > MAX_RECORDS:
        raise ValueError("invalid bounded interface list")
    occupied = {}
    unsupported = builtins = 0
    for row in rows:
        if type(row) is not dict:
            raise ValueError("invalid interface record")
        fields = set(row)
        if "builtin" in fields:
            if not (fields == {"builtin"} or fields == {"builtin", "type"}):
                raise ValueError("ambiguous builtin record")
            if type(row["builtin"]) is not str or row["builtin"] not in _BUILTINS:
                raise ValueError("unapproved builtin identifier")
            if "type" in row and (type(row["type"]) is not str or len(row["type"]) > 16):
                raise ValueError("invalid builtin type")
            builtins += 1
            continue
        if fields not in ({"location", "type"}, {"location", "component", "type"}):
            raise ValueError("unsanitized or incomplete interface record")
        location = row["location"]
        component = row.get("component", 0)
        if (type(location) is not int or not 0 <= location <= MAX_LOCATION or
            type(component) is not int or not 0 <= component <= 3):
            raise ValueError("invalid Location or Component decoration")
        typed = _type_components(row["type"])
        if typed is None:
            unsupported += 1
            continue
        family, width = typed
        if component + width > 4:
            raise ValueError("cross-location or packed wide vector not supported")
        for lane in range(component, component + width):
            key = (location, lane)
            if key in occupied:
                raise ValueError("duplicate occupied interface component")
            occupied[key] = family
    return occupied, unsupported, builtins, len(rows)


def classify_vf_components(vertex_outputs, fragment_inputs):
    """Aggregate structural coverage; *never* semantic or visual proof.

    A candidate means only matching scalar-family slots at identical SPIR-V
    Location+Component. Interpolation modes, decorations, DXBC semantic
    registers, arrays/matrices/64-bit and cross-stage relinking are excluded.
    """
    vs, v_unknown, v_builtin, v_count = _collect(vertex_outputs)
    fs, f_unknown, f_builtin, f_count = _collect(fragment_inputs)
    missing = sum(slot not in vs for slot in fs)
    mismatched = sum(slot in vs and vs[slot] != family for slot, family in fs.items())
    extra = sum(slot not in fs for slot in vs)
    unknown = v_unknown + f_unknown
    if unknown:
        status = "INCONCLUSIVE_UNSUPPORTED_TYPE"
    elif not fs:
        status = "NO_USER_VARYINGS"
    elif missing or mismatched:
        status = "STRUCTURAL_DEFICIT"
    else:
        status = "STRUCTURAL_CANDIDATE_ONLY"
    return {
        "status": status,
        "vertex_output_records": v_count,
        "fragment_input_records": f_count,
        "vertex_output_components": len(vs),
        "fragment_input_components": len(fs),
        "missing_fragment_components": missing,
        "typed_mismatch_components": mismatched,
        "extra_vertex_components": extra,
        "unsupported_type_records": unknown,
        "excluded_builtin_records": v_builtin + f_builtin,
        "original_dxbc_semantics_verified": False,
        "interpolation_verified": False,
        "pixel_fidelity_verified": False,
    }
