#!/usr/bin/env python3
"""T3: compare allowlisted render-state summaries without disclosing game assets.

Input is a pair of *already authenticated*, private normalized JSON summaries.
This does not authenticate the source, match renderers or prove a device fix.
"""
import argparse
import json
from pathlib import Path

FIELDS = ("blend_src", "blend_dst", "blend_op", "zwrite", "ztest",
          "cull", "color_mask", "alpha_clip", "render_queue")
ALLOWED = {k: (str, int, bool, type(None)) for k in FIELDS}

def compare(original, exported):
    if not isinstance(original, dict) or not isinstance(exported, dict):
        raise ValueError("expected_object")
    if set(original) != set(FIELDS) or set(exported) != set(FIELDS):
        raise ValueError("missing_or_unexpected_state_field")
    for record in (original, exported):
        for key, value in record.items():
            if type(value) not in ALLOWED[key]:
                raise ValueError("invalid_state_type")
            if isinstance(value, str) and (not value or len(value) > 64):
                raise ValueError("invalid_state_value")
    unknown = sorted(k for k in FIELDS if original[k] is None or exported[k] is None)
    # A definite difference is actionable even when another field is unknown.
    # Never report an unknown-versus-known value as a proven mismatch.
    changed = sorted(k for k in FIELDS
                     if k not in unknown and (type(original[k]) is not type(exported[k])
                                              or original[k] != exported[k]))
    status = "MISMATCH" if changed else ("INCONCLUSIVE" if unknown else "MATCH")
    return {"status": status,
            "changed_fields": changed, "unknown_fields": unknown,
            "compared_fields": len(FIELDS) - len(unknown),
            "device_fix_proven": False, "source_authenticated_here": False}

def _unique_object_pairs(pairs):
    """Reject ambiguous JSON members rather than silently taking the last value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_field")
        result[key] = value
    return result


def load_summary(path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_object_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite_json_value")))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("original", type=Path)
    p.add_argument("exported", type=Path)
    args = p.parse_args()
    result = compare(load_summary(args.original), load_summary(args.exported))
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
