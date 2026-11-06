#!/usr/bin/env python3
"""Compare sanitized FFT probe coordinates; reports first differing key, not raw assets."""
import json
import math
from pathlib import Path

def read_samples(path):
    def no_duplicates(pairs):
        d = {}
        for key, value in pairs:
            if key in d:
                raise ValueError("duplicate JSON key")
            d[key] = value
        return d
    doc = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicates,
                     parse_constant=lambda s: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    if not isinstance(doc, dict) or set(doc) != {"samples"} or not isinstance(doc["samples"], list):
        raise ValueError("expected samples array")
    result = {}
    for item in doc["samples"]:
        if not isinstance(item, dict) or set(item) != {"pass", "x", "y", "channel", "value"}:
            raise ValueError("invalid fields")
        if any(type(item[k]) is not int or item[k] < 0 for k in ("pass", "x", "y")):
            raise ValueError("invalid coordinate")
        if not isinstance(item["channel"], str) or not item["channel"]:
            raise ValueError("invalid channel")
        if type(item["value"]) not in (int, float) or not math.isfinite(item["value"]):
            raise ValueError("invalid value")
        key = (item["pass"], item["x"], item["y"], item["channel"])
        if key in result:
            raise ValueError("duplicate sample")
        result[key] = float(item["value"])
    return result

def first_difference(vulkan, unity, atol=1e-6, rtol=1e-5):
    if not all(math.isfinite(v) and v >= 0 for v in (atol, rtol)):
        raise ValueError("invalid tolerance")
    for key in sorted(set(vulkan) | set(unity)):
        label = dict(zip(("pass", "x", "y", "channel"), key))
        if key not in vulkan or key not in unity:
            return dict(label, status="missing", missing_from="vulkan" if key not in vulkan else "unity")
        if not math.isclose(vulkan[key], unity[key], abs_tol=atol, rel_tol=rtol):
            return dict(label, status="different", absolute_delta=abs(vulkan[key] - unity[key]))
    return {"status": "match", "count": len(vulkan)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("vulkan")
    parser.add_argument("unity")
    args = parser.parse_args()
    print(json.dumps(first_difference(read_samples(args.vulkan), read_samples(args.unity)), sort_keys=True))
