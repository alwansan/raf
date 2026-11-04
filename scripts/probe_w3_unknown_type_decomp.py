#!/usr/bin/env python3
"""W3 — raw type-id decomposition of the 'unknown' property bucket (step 9 follow-up).

For each of the 65 unnamed targets with committed schemas (step-9 artifact),
record the *raw numeric* ``m_PropInfo.m_Type`` id histogram of every property
in that shader's serialized property sheet. Cross-check (fail-closed): the
per-target property total implied by the raw histogram must equal the total
implied by the committed step-9 ``property_type_histogram``.

Publication: raw ids only — no name mapping is asserted for ids outside the
previously published set (0=Color, 2=Float, 3=Range, 4=Texture). The public
Unity docs page for ``ShaderPropertyType`` documents the enum's field names but
does not print numeric values; numeric-name assignment beyond the published
four is deliberately NOT asserted here. Keys are ``owner:path_id`` (public).
No shader/asset names, no decompiled content, no values (W2 lanes).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from probe_w3_per_material_keywords import PINNED_OWNERS, sha256_file  # noqa: E402

STEP9_ARTIFACT = "docs/W3_UNNAMED_TARGET_SCHEMAS_2026-11-04.json"
PUBLISHED_TYPES = {0, 2, 3, 4}


def run(game_data_dir: str, repo: Path) -> dict:
    import UnityPy

    step9 = json.load(open(repo / STEP9_ARTIFACT, encoding="utf-8"))
    targets: dict[str, list[dict]] = {}
    for rec in step9["unnamed_target_schemas"]:
        targets.setdefault(rec["owner"], []).append(rec)

    root = Path(game_data_dir)
    owner_names = sorted([p.name for p in root.iterdir() if p.is_file() and p.suffix == ".assets"]
                         + [p.name for p in root.iterdir()
                            if p.is_file() and p.suffix == "" and p.name.startswith("level")])
    if len(owner_names) != 82:
        raise SystemExit(f"expected 82 owners, got {len(owner_names)}")
    per_file = {}
    for name in owner_names:
        size, digest = sha256_file(str(root / name))
        per_file[name] = {"bytes": size, "sha256": digest, "pinned": name in PINNED_OWNERS}
    for pname, exp in PINNED_OWNERS.items():
        if (per_file[pname]["bytes"], per_file[pname]["sha256"]) != exp:
            raise SystemExit(f"pin failed for {pname}")
        per_file[pname]["pin_verified"] = True

    needed = {t["owner"] for t in step9["unnamed_target_schemas"]}
    per_target: dict[str, dict] = {}
    total_hist: Counter = Counter()
    prop_total: int = 0
    for owner in sorted(needed):
        path = str(root / owner)
        env = UnityPy.load(path)
        sf = list(env.files.values())[0]
        want = {(owner, t["path_id"]) for t in targets[owner]}
        for path_id, ob in sf.objects.items():
            key = (owner, path_id)
            if key not in want or ob.type.name != "Shader":
                continue
            d = ob.read_typetree()
            props = (d.get("m_ParsedForm") or {}).get("m_PropInfo") or {}
            props = props.get("m_Props") or []
            raw_hist: dict[str, int] = {}
            published_count = 0
            for p in props:
                t = p.get("m_Type")
                if not isinstance(t, int):
                    raise SystemExit(f"non-int property type at {owner}:{path_id}")
                raw_hist[str(t)] = raw_hist.get(str(t), 0) + 1
                total_hist[str(t)] += 1
                prop_total += 1
                if t in PUBLISHED_TYPES:
                    published_count += 1
            s9 = next(x for x in step9["unnamed_target_schemas"]
                      if x["owner"] == owner and x["path_id"] == path_id)
            s9_total = sum(s9["property_type_histogram"].values())
            raw_total = sum(raw_hist.values())
            if raw_total != s9_total:
                raise SystemExit(
                    f"cross-check failed {owner}:{path_id}: raw {raw_total} vs step9 {s9_total}")
            per_target[f"{owner}:{path_id}"] = {
                "property_count": raw_total,
                "raw_type_histogram": dict(sorted(raw_hist.items(), key=lambda kv: int(kv[0]))),
                "published_type_occurrences": published_count,
                "outside_published_occurrences": raw_total - published_count,
            }
        del env
    if per_target and len(per_target) != len(step9["unnamed_target_schemas"]):
        raise SystemExit("target coverage mismatch vs step-9 artifact")
    outside_total = sum(v["outside_published_occurrences"] for v in per_target.values())
    unknown_step9 = sum(v for t in step9["unnamed_target_schemas"]
                        for k, v in t["property_type_histogram"].items() if k == "unknown")
    if outside_total != unknown_step9:
        raise SystemExit(f"aggregate mismatch: outside {outside_total} vs step9 unknown {unknown_step9}")

    return {
        "probe": "w3-unknown-type-decomp",
        "schema_version": 1,
        "totals": {
            "targets": len(per_target),
            "properties": prop_total,
            "aggregate_raw_type_histogram": {k: total_hist[k] for k in sorted(total_hist, key=int)},
            "outside_published_total": outside_total,
            "step9_unknown_bucket": unknown_step9,
        },
        "per_target": per_target,
        "negative_controls": {
            "per_target_total_matches_step9": True,
            "aggregate_outside_equals_step9_unknown": True,
            "no_name_assertion_beyond_published_four": True,
            "no_values_read": True,
            "empty_histograms_never_asserted": True,
        },
        "tool_versions": {"unitypy": getattr(UnityPy, "__version__", "unknown"),
                          "python": platform.python_version()},
    }


def main() -> int:
    import os
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--repo", default=str(Path.cwd()))
    ap.add_argument("--aggregate-json", required=True)
    args = ap.parse_args()
    report = run(args.game_data, Path(args.repo))
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    with open(args.aggregate_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
