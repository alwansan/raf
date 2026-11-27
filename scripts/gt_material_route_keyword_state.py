"""Same-instance serialized Material keyword/pass state, not active variants.

Do not union valid and invalid keywords, silently accept legacy keyword
strings, or infer Shader keyword scope from Material serialized state.
The strict bounded candidate accepts modern explicit arrays only.
"""
from scripts.b43_material_keyword_fidelity import FIELDS, NAME
from scripts.gt_runtime_keyword_contract import keyword_set


class Unproven(ValueError):
    pass


class Mismatch(ValueError):
    pass


KINDS=("valid_keyword","invalid_keyword","disabled_pass")


def normalize(tree):
    if type(tree) is not dict or any(field not in tree for field in FIELDS):
        raise Unproven("missing_material_keyword_pass_container")
    # Legacy nonempty strings have no proved mapping to valid/invalid lanes.
    if "m_ShaderKeywords" in tree and tree["m_ShaderKeywords"] != "":
        raise Unproven("unsupported_legacy_material_keyword_state")
    valid,invalid,passes=(tree[k] for k in FIELDS)
    if any(type(x) is not list for x in (valid,invalid,passes)):
        raise Unproven("invalid_material_keyword_pass_container")
    try:
        v,i=keyword_set(valid),keyword_set(invalid)
    except ValueError:
        raise Unproven("invalid_material_keyword_set") from None
    if v&i:
        raise Unproven("overlapping_material_keyword_buckets")
    if (any(type(p) is not str or not NAME.fullmatch(p) for p in passes)
            or len(set(passes))!=len(passes)):
        raise Unproven("invalid_material_disabled_pass_set")
    return v,i,frozenset(passes)


def compare(source, actual):
    before,after=normalize(source),normalize(actual)
    # Explicit bucket differences; a shared union cannot prove equality.
    if before[:2]!=after[:2] and before[0]|before[1]==after[0]|after[1]:
        raise Mismatch("material_keyword_bucket_drift")
    counts={}
    for kind,b,a in zip(KINDS,before,after,strict=True):
        if b-a:
            raise Mismatch("missing_material_"+kind)
        if a-b:
            raise Mismatch("unexpected_material_"+kind)
        counts[kind]=len(b)
    return counts
