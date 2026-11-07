#!/usr/bin/env python3
"""Fail-closed count-only Foam pass1 evidence gate. Not a runtime proof."""
import json
import sys
from pathlib import Path
P = "field_api_Graphics_Blit_"

def evaluate(r):
    if not isinstance(r, dict):
        raise ValueError("not_object")
    for p in (0, 1):
        n = r.get(P + f"explicit_sites_pass_literal{p}")
        if type(n) is not int or n < 0:
            raise ValueError("invalid_sites")
        for role, cats in (("source", ("Texture", "RenderTexture", "unknown")),
                           ("destination", ("RenderTexture", "null", "unknown"))):
            counts = [r.get(P + f"pass{p}_{role}_{c}") for c in cats]
            if any(type(v) is not int or v < 0 for v in counts) or sum(counts) != n:
                raise ValueError("invalid_partition")
    if r[P + "explicit_sites_pass_literal1"] != 1:
        raise ValueError("pass1_not_unique")
    if r[P + "pass1_source_unknown"] or r[P + "pass1_destination_unknown"]:
        return "UNRESOLVED"
    return "TYPE_ONLY"

def unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate_key")
        d[k] = v
    return d

def main(args):
    if len(args) != 2:
        return 2
    path = Path(args[1])
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 16384:
            raise ValueError("unsafe_file")
        result = evaluate(json.loads(path.read_text("utf8"), object_pairs_hook=unique))
    except (OSError, UnicodeError, ValueError, TypeError):
        print("FOAM_PASS1_GATE_BLOCKED")
        return 2
    print("FOAM_PASS1_" + result + " runtime_identity_proven=false device_pixels_proven=false")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
