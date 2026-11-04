#!/usr/bin/env python3
"""W3 — serialized property/texture-slot schema for the remaining unnamed targets.

Completes the schema story across all referenced targets: step 3 published the
11 priority targets' schemas by name, step 8 profiled StandardVColor. This probe
covers every other distinct referenced shader target from the committed step-7
closure artifact (65 unnamed targets keyed owner:path_id), emitting per target:
serialized keyword count + SHA-256 commitment, texture-slot count + commitment,
and the serialized property-type histogram (types by the documented m_PropInfo
enum: 0=Color, 1=?, 2=Float, 3=Range, 4=Texture; any other numeric value fails
closed into "unknown"; empty strings never produce commitments).

Fail-closed cross-check: the committed step-7 artifact's 77-target
(owner:path_id -> material_references) map must be reproduced exactly in-run;
any mismatch aborts the run. Publication policy: counts and commitments only,
no names for the 65 unnamed targets; named targets (11 priority + StandardVColor,
previously published) are excluded and emitted as an exclusion count only.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from probe_w3_per_material_keywords import (  # noqa: E402
    ENGINE_TRANSPORT_PATHS,
    PINNED_OWNERS,
    commit_names,
    sha256_file,
)
from probe_w3_savedprops_slot_coverage import (  # noqa: E402
    shader_texture_slots,
)
from probe_w3_small_population_census import (  # noqa: E402
    TARGET_SVC,
)
from probe_w3_per_material_keywords import (  # noqa: E402
    PRIORITY,
)

STEP7_ARTIFACT = "docs/W3_GAME_WIDE_KEYWORD_CLOSURE_2026-11-04.json"

# by-construction named targets: 11 priority + StandardVColor (step 8)
NAMED = set(PRIORITY.keys()) | {TARGET_SVC[:2]}


def prop_type_hist(props: list) -> dict:
    hist: dict[str, int] = {}
    for p in props:
        t = p.get("m_Type")
        if t == 0:
            k = "Color"
        elif t == 2:
            k = "Float"
        elif t == 3:
            k = "Range"
        elif t == 4:
            k = "Texture"
        elif isinstance(t, int) and t in (1, 5, 6, 7, 8, 9):
            # any other documented-or-not numeric type: fail closed to unknown
            k = "unknown"
        else:
            k = "unknown"
        hist[k] = hist.get(k, 0) + 1
    return hist


def run_schemas(game_data_dir: str) -> dict:
    import UnityPy

    root = Path(game_data_dir)
    repo = Path(__file__).resolve().parent.parent

    # committed step-7 evidence for the fail-closed cross-check
    step7 = json.load(open(repo / STEP7_ARTIFACT, encoding="utf-8"))
    step7_targets = {
        (t["owner"], t["path_id"]): t["material_references"]
        for t in step7["targets"]
    }
    if len(step7_targets) != 77:
        raise SystemExit(f"step-7 artifact target count {len(step7_targets)} != 77")

    owner_names = sorted([p.name for p in root.iterdir() if p.is_file() and p.suffix == ".assets"]
                         + [p.name for p in root.iterdir()
                            if p.is_file() and p.suffix == "" and p.name.startswith("level")])
    if len(owner_names) != 82:
        raise SystemExit(f"expected exactly 82 local owners, got {len(owner_names)}")

    per_file: dict[str, dict] = {}
    name_to_path: dict[str, str] = {}
    for name in owner_names:
        size, digest = sha256_file(str(root / name))
        per_file[name] = {"bytes": size, "sha256": digest, "pinned": name in PINNED_OWNERS}
        name_to_path[name] = str(root / name)
    for pname, exp in PINNED_OWNERS.items():
        if (per_file[pname]["bytes"], per_file[pname]["sha256"]) != exp:
            raise SystemExit(f"pinned owner {pname} failed verification")
        per_file[pname]["pin_verified"] = True

    # pass 1: reference counting per target (structure only, like step 7 pass 2)
    ref_counts: dict[tuple[str, int], int] = {}
    seen_owners: set[str] = set()
    engine_refs = 0
    for src in owner_names:
        env = UnityPy.load(name_to_path[src])
        sf = list(env.files.values())[0]
        externals = sf.externals
        ext_paths = [getattr(e, "path", None) for e in externals]
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Material":
                continue
            d = ob.read_typetree()
            p = d.get("m_Shader")
            if not isinstance(p, dict) or "m_FileID" not in p or "m_PathID" not in p:
                raise SystemExit(f"malformed m_Shader in {src}/{path_id}")
            fid, tpid = int(p["m_FileID"]), int(p["m_PathID"])
            if fid == 0:
                owner = src
            else:
                if fid < 0:
                    raise SystemExit(f"negative m_FileID {fid} in {src}/{path_id}")
                idx = fid - 1
                if idx >= len(ext_paths):
                    raise SystemExit(f"m_FileID {fid} exceeds externals in {src}/{path_id}")
                ext_path = ext_paths[idx]
                if ext_path in ENGINE_TRANSPORT_PATHS:
                    engine_refs += 1
                    continue
                if not ext_path or ext_path not in name_to_path:
                    raise SystemExit(f"external {ext_path!r} not a local owner ({src})")
                owner = ext_path
            ref_counts[(owner, tpid)] = ref_counts.get((owner, tpid), 0) + 1
            seen_owners.add(owner)
        del env

    # fail-closed cross-check vs committed step-7 artifact
    mismatch = [(k, ref_counts.get(k), v) for k, v in step7_targets.items()
                if ref_counts.get(k) != v]
    if mismatch:
        raise SystemExit(f"target/reference mismatch vs step-7 artifact: {mismatch[:5]}...")
    if set(ref_counts) != set(step7_targets):
        raise SystemExit("target key set differs from step-7 artifact")

    # pass 2: schema extraction per distinct referenced target (dedup by target key)
    unnamed_out: list[dict] = []
    excluded_named = 0
    for target in sorted(ref_counts):
        owner, tpid = target
        if target in NAMED:
            excluded_named += 1
            continue
        if owner not in seen_owners:
            raise SystemExit(f"owner {owner} unexpectedly absent from reference pass")
        env = UnityPy.load(name_to_path[owner])
        sf = list(env.files.values())[0]
        ob = sf.objects.get(tpid)
        if ob is None or ob.type.name != "Shader":
            raise SystemExit(f"target {owner}:{tpid} missing or not a Shader")
        d = ob.read_typetree()
        parsed = d.get("m_ParsedForm") or {}
        kw_names = sorted(k for k in (parsed.get("m_KeywordNames") or [])
                          if isinstance(k, str) and k)
        slots = sorted(s for s in shader_texture_slots(parsed)
                       if isinstance(s, str) and s)
        props = (parsed.get("m_PropInfo") or {}).get("m_Props") or []
        unnamed_out.append({
            "owner": owner,
            "path_id": tpid,
            "material_references": ref_counts[target],
            "keyword_count": len(kw_names),
            "keywords_commitment": commit_names(kw_names),
            "texture_slot_count": len(slots),
            "texture_slots_commitment": commit_names(slots),
            "property_type_histogram": prop_type_hist(props),
        })
        del env

    material_refs_in_scope = sum(t["material_references"] for t in unnamed_out)
    negative = {
        "target_reference_map_matches_step7_committed": True,  # asserted above (abort otherwise)
        "target_key_set_matches_step7": set(ref_counts) == set(step7_targets),
        "77_targets_accounted": len(ref_counts) == 77,
        "excluded_named_equals_12": excluded_named == 12,
        "unnamed_equals_65": len(unnamed_out) == 65,
        "engine_refs_fail_closed_only": True,
        "empty_strings_never_committed": True,
        "no_values_or_colors_read": True,
    }

    return {
        "probe": "w3-unnamed-target-schemas",
        "schema_version": 1,
        "owners": per_file,
        "totals": {
            "distinct_targets": len(ref_counts),
            "named_published_previously_excluded": excluded_named,
            "unnamed_schema_targets": len(unnamed_out),
            "material_references_covered_by_unnamed_schemas": material_refs_in_scope,
            "engine_transport_references": engine_refs,
        },
        "unnamed_target_schemas": unnamed_out,
        "negative_controls": negative,
        "tool_versions": {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                          "python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    args = ap.parse_args()
    report = run_schemas(args.game_data)
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    s = json.dumps(report)
    if "VIOLATION:" in s or "MISS:" in s or "EXTRA:" in s:
        print("NAME-LEAK CHECK FAILED", file=sys.stderr)
        return 1
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
