#!/usr/bin/env python3
"""Aggregate-only, fail-closed RGB drift classifier for authenticated original/export pairs.

Private input: {"pairs":[{"identity_ok":true,"dimensions_ok":true,
"rgb_equal":false,"alpha_equal":true,"format":"DXT5",
"source_srgb":null,"importer_srgb":true}]}
Never print filenames, hashes, pathIDs, or pixel arrays. Unknown metadata remains UNKNOWN.
"""
import argparse
from collections import Counter, defaultdict
import json

EXPECTED_TOTAL = 106
EXPECTED_DRIFT = 30


def classify(doc, strict_baseline=True):
    pairs = doc.get("pairs") if isinstance(doc, dict) else None
    if not isinstance(pairs, list):
        raise ValueError("pairs must be an array")
    groups = defaultdict(Counter)
    counts = Counter()
    for row in pairs:
        if not isinstance(row, dict):
            raise ValueError("pair must be an object")
        for key in ("identity_ok", "dimensions_ok", "rgb_equal", "alpha_equal"):
            if type(row.get(key)) is not bool:
                raise ValueError("missing/invalid required boolean: " + key)
        if not row["identity_ok"] or not row["dimensions_ok"] or not row["alpha_equal"]:
            raise ValueError("unverified identity/dimensions/alpha parity")
        label = "exact" if row["rgb_equal"] else "rgb_drift"
        counts[label] += 1
        for key in ("format", "source_srgb", "importer_srgb"):
            value = row.get(key)
            if key.endswith("srgb"):
                if value is not None and type(value) is not bool:
                    raise ValueError("invalid srgb flag")
                bucket = "UNKNOWN" if value is None else str(value).lower()
            else:
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    raise ValueError("invalid format")
                bucket = value if value is not None else "UNKNOWN"
                if len(bucket) > 64 or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_+-." for c in bucket):
                    raise ValueError("unsafe format category")
            groups[(key, bucket)][label] += 1
    if strict_baseline and (len(pairs) != EXPECTED_TOTAL or counts["rgb_drift"] != EXPECTED_DRIFT):
        raise ValueError("baseline count mismatch; verify input provenance")
    return {"total": len(pairs), "exact": counts["exact"], "rgb_drift": counts["rgb_drift"],
            "strata": {key: {bucket: {"exact": groups[(key, bucket)]["exact"],
                                      "rgb_drift": groups[(key, bucket)]["rgb_drift"]}
                             for k, bucket in sorted(groups) if k == key}
                       for key in ("format", "source_srgb", "importer_srgb")}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("private_manifest")
    args = parser.parse_args()
    with open(args.private_manifest, encoding="utf-8") as stream:
        doc = json.load(stream)
    print(json.dumps(classify(doc), sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
