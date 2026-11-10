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
    changed = sorted(k for k in FIELDS if original[k] != exported[k])
    unknown = sorted(k for k in FIELDS if original[k] is None or exported[k] is None)
    return {"status": "INCONCLUSIVE" if unknown else ("MISMATCH" if changed else "MATCH"),
            "changed_fields": changed, "unknown_fields": unknown,
            "compared_fields": len(FIELDS) - len(unknown),
            "device_fix_proven": False, "source_authenticated_here": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("original", type=Path)
    p.add_argument("exported", type=Path)
    args = p.parse_args()
    result = compare(json.loads(args.original.read_text()), json.loads(args.exported.read_text()))
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
