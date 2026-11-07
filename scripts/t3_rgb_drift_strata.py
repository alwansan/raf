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


def classify(doc, strict_baseline=True, require_metadata=False, require_drift_metadata=False):
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
                # The literal sentinel is not authenticated format metadata.
                # Do not count it as known in the drift-coverage gate.
                if bucket.upper() == "UNKNOWN":
                    bucket = "UNKNOWN"
            groups[(key, bucket)][label] += 1
    coverage = {key: sum(1 for (k, bucket), values in groups.items()
                         if k == key and bucket != "UNKNOWN"
                         for _ in range(values["exact"] + values["rgb_drift"]))
                for key in ("format", "source_srgb", "importer_srgb")}
    drift_coverage = {key: sum(values["rgb_drift"] for (k, bucket), values in groups.items()
                               if k == key and bucket != "UNKNOWN")
                      for key in ("format", "source_srgb", "importer_srgb")}
    if require_drift_metadata and any(drift_coverage[key] != counts["rgb_drift"] for key in drift_coverage):
        raise ValueError("missing metadata for RGB-drift pairs; cannot infer drift strata")
    if require_metadata and any(coverage[key] == 0 for key in coverage):
        raise ValueError("missing per-pair metadata coverage; aggregate-only or unknown manifest")
    if strict_baseline and (len(pairs) != EXPECTED_TOTAL or counts["rgb_drift"] != EXPECTED_DRIFT):
        raise ValueError("baseline count mismatch; verify input provenance")
    return {"total": len(pairs), "exact": counts["exact"], "rgb_drift": counts["rgb_drift"],
            "metadata_coverage": coverage, "rgb_drift_metadata_coverage": drift_coverage, "strata": {key: {bucket: {"exact": groups[(key, bucket)]["exact"],
                                      "rgb_drift": groups[(key, bucket)]["rgb_drift"]}
                             for k, bucket in sorted(groups) if k == key}
                       for key in ("format", "source_srgb", "importer_srgb")}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("private_manifest")
    parser.add_argument("--require-metadata", action="store_true", help="reject missing whole-field metadata")
    parser.add_argument("--require-drift-metadata", action="store_true",
                        help="reject unknown metadata for any RGB-drift pair")
    args = parser.parse_args()
    with open(args.private_manifest, encoding="utf-8") as stream:
        doc = json.load(stream)
    print(json.dumps(classify(doc, require_metadata=args.require_metadata,
                              require_drift_metadata=args.require_drift_metadata), sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
