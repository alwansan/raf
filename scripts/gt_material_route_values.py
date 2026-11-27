"""Strict per-route serialized Material values, not shader/GPU semantics.

Reuse the original B22/B44 shape and numeric contracts. Compare finite
RGBA and float values as binary32, and integer values as signed int32.
Never report private property names, values, or identities.
"""
from scripts.b22_verify_material_scalars import normalize as normalize_scalars, _float_bits
from scripts.b44_verify_material_colors import normalize_colors


class Unproven(ValueError):
    pass


class Mismatch(ValueError):
    pass


FIELDS = (("m_Colors","color"),("m_Floats","float"),("m_Ints","int"))


def normalize(tree, *, exported=False):
    saved=tree.get("m_SavedProperties")
    if type(saved) is not dict or not all(k in saved for k,_ in FIELDS):
        raise Unproven("missing_material_value_container")
    # Native exported YAML may use a property-name mapping (including {}),
    # while original source typetrees must be arrays. Duplicate YAML mapping
    # keys are rejected by the route gate before normalization.
    adapted=dict(saved)
    if exported:
        for field in ("m_Floats","m_Ints"):
            if type(adapted[field]) is dict:
                adapted[field]=[{k:v} for k,v in adapted[field].items()]
    try:
        values=normalize_scalars(adapted,exported=exported)
        colors=normalize_colors(saved["m_Colors"],exported=exported)
        values["m_Colors"]={name:tuple(_float_bits(c) for c in rgba)
                             for name,rgba in colors.items()}
    except (KeyError,ValueError,TypeError,OverflowError):
        raise Unproven("invalid_material_serialized_value") from None
    return values


def compare(source, actual):
    before=normalize(source)
    after=normalize(actual,exported=True)
    counts={}
    for field,kind in FIELDS:
        b,a=before[field],after[field]
        if b.keys()-a.keys():
            raise Mismatch("missing_material_"+kind+"_slot")
        if a.keys()-b.keys():
            raise Mismatch("unexpected_material_"+kind+"_slot")
        if b!=a:
            raise Mismatch("material_"+kind+"_value_drift")
        counts[kind]=len(b)
    return counts
