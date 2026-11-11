"""Fail-closed join of two independently sanitized original Foam Blit role reports.

This is static IL provenance only, not evidence of rendered water.
"""
import json
import math
import sys
from decimal import Decimal


def finite_float(value):
    """Reject JSON exponent overflow before aggregate schema validation."""
    parsed = float(value)
    if not math.isfinite(parsed) or (parsed == 0.0 and not Decimal(value).is_zero()):
        raise ValueError("nonfinite_json")
    return parsed
from scripts.t2_foam_pass_role_gate import validate as validate_roles, unique_keys
from scripts.t2_foam_pass_aggregate_consistency import check_counts
from scripts.t2_foam_shaderfind_return_report import validate as validate_original


def reconcile(original_aggregate, per_pass_roles):
    """Return only the intersection of independently checked pass classifications."""
    validate_original(original_aggregate)
    aggregate = check_counts(original_aggregate)
    roles = validate_roles(per_pass_roles)
    for number in (0, 1):
        observed = aggregate["pass" + str(number)]
        if (observed["source"], observed["destination"]) != roles[number]:
            raise ValueError("independent_pass_role_disagreement")
    return {
        "classification_only": True,
        "pass0": aggregate["pass0"],
        "pass1": aggregate["pass1"],
        "independent_summaries_agree": True,
        # Static type parity does not establish a shared runtime texture object.
        "crosspass_rendertexture_instance_identity": "UNKNOWN",
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m scripts.t2_foam_pass_crosscheck original_safe.json per_pass_safe.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        original = json.load(f, object_pairs_hook=unique_keys, parse_float=finite_float,
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite_json")))
    with open(sys.argv[2], encoding="utf-8") as f:
        roles = json.load(f, object_pairs_hook=unique_keys, parse_float=finite_float,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite_json")))
    print(json.dumps(reconcile(original, roles), sort_keys=True))


if __name__ == "__main__":
    main()
