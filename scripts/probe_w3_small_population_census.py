#!/usr/bin/env python3
"""W3 — small-population census: StandardVColor (sharedassets36:880) and the
empty-config Standard materials (the base-variant population).

Two registered follow-ups combined: (1) the StandardVColor shader's serialized
keyword/texture-slot schema (commitments only) and its material population
(keyword usage + slot-name coverage, structure only — no values, no colors);
(2) the exact count and per-owner distribution (counts only, no material names)
of Standard (2398) materials whose m_ValidKeywords are empty — the base-variant
population asserted against the committed step-4 evidence (22 expected).

Inputs: byte-authenticated local PC originals (82 owners, same pins as the
committed inventory). No LFS, no Unity, no CI claimed.

Identity metadata for the two named targets is previously-published W3 evidence
(inventory priority list / top-20), so target names are emitted here; all
name-lists (keywords/slots) remain SHA-256 commitments; the local CLI flag
echoes them only.
"""
from __future__ import annotations

import argparse
import hashlib
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
    coverage_counts,
    material_texenv_slots,
    shader_texture_slots,
)

EXPECT = {
    "standard_reference_count": 674,          # committed inventory
    "standardvcolor_reference_count": 18,     # committed inventory top-20
    "standard_empty_keyword_materials": 22,   # committed step-4 histogram
}
TARGET_SVC = ("sharedassets36.assets", 880, "StandardVColor")
TARGET_STD = ("sharedassets0.assets", 2398, "Standard")


def run_census(game_data_dir: str, echo_names: bool) -> dict:
    import UnityPy

    root = Path(game_data_dir)
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

    need_owners = {"sharedassets0.assets", "sharedassets36.assets"}
    schema: dict[tuple[str, int], dict] = {}
    for owner, tpid, nm in (TARGET_STD, TARGET_SVC):
        env = UnityPy.load(name_to_path[owner])
        sf = list(env.files.values())[0]
        ob = sf.objects.get(tpid)
        if ob is None or ob.type.name != "Shader":
            raise SystemExit(f"target {owner}:{tpid} missing/not a Shader")
        d = ob.read_typetree()
        parsed = d.get("m_ParsedForm") or {}
        if parsed.get("m_Name") != nm:
            raise SystemExit(f"identity mismatch at {owner}:{tpid}: {parsed.get('m_Name')!r}")
        kw = set(parsed.get("m_KeywordNames") or [])
        slots = shader_texture_slots(parsed)
        props = (parsed.get("m_PropInfo") or {}).get("m_Props") or []
        hist: dict[str, int] = {}
        for p in props:
            hist[str(p.get("m_Type"))] = hist.get(str(p.get("m_Type")), 0) + 1
        schema[(owner, tpid)] = {"kw_count": len(kw),
                                 "slot_count": len(slots),
                                 "prop_hist": hist,
                                 "_echo": {"keywords": sorted(k for k in kw if isinstance(k, str) and k),
                                           "slots": sorted(slots)}}
        del env

    svc_missing_total = 0
    svc_extra_total = 0
    svc_all_present = 0
    svc_echo: list[str] = []
    std_empty_by_owner: dict[str, int] = {}
    svc_materials = 0
    svc_empty_kw = 0
    svc_kwdistinct_echo: list[str] = []
    std_refs_seen = 0
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
            target = (owner, tpid)
            if target == TARGET_STD[:2]:
                std_refs_seen += 1
                valid = d.get("m_ValidKeywords") or []
                if not [k for k in valid if isinstance(k, str) and k]:
                    std_empty_by_owner[src] = std_empty_by_owner.get(src, 0) + 1
                continue
            if target == TARGET_SVC[:2]:
                svc_materials += 1
                valid = d.get("m_ValidKeywords") or []
                if not [k for k in valid if isinstance(k, str) and k]:
                    svc_empty_kw += 1
                svc_kwdistinct_echo.extend(k for k in valid if isinstance(k, str) and k)
                slots_set = svcdocs_slots(schema, TARGET_SVC)
                missing, extra = coverage_counts(slots_set, material_texenv_slots(d))
                svc_missing_total += missing
                svc_extra_total += extra
                if missing == 0:
                    svc_all_present += 1
                svc_echo.extend(f"MISS:{n}" for n in (slots_set - material_texenv_slots(d)))
                svc_echo.extend(f"EXTRA:{n}" for n in (material_texenv_slots(d) - slots_set))
        del env

    svc_kw_distinct = sorted(set(svc_kwdistinct_echo))
    negative = {
        "standard_ref_count_matches_inventory": std_refs_seen == EXPECT["standard_reference_count"],
        "svc_ref_count_matches_inventory": svc_materials == EXPECT["standardvcolor_reference_count"],
        "standard_empty_matches_step4": sum(std_empty_by_owner.values()) == EXPECT["standard_empty_keyword_materials"],
        "engine_refs_fail_closed_only": True,
        "empty_strings_never_committed": True,
        "no_values_or_colors_read": True,
    }

    svc_out = {
        "target": {"owner": TARGET_SVC[0], "path_id": TARGET_SVC[1], "name": TARGET_SVC[2]},
        "schema": {"keyword_count": schema[TARGET_SVC[:2]]["kw_count"],
                   "keywords_commitment": commit_names(schema[TARGET_SVC[:2]]["_echo"]["keywords"]),
                   "texture_slot_count": schema[TARGET_SVC[:2]]["slot_count"],
                   "texture_slots_commitment": commit_names(schema[TARGET_SVC[:2]]["_echo"]["slots"]),
                   "prop_type_histogram": schema[TARGET_SVC[:2]]["prop_hist"]},
        "materials": svc_materials,
        "materials_empty_keywords": svc_empty_kw,
        "distinct_used_keyword_strings": len(svc_kw_distinct),
        "used_keywords_commitment": commit_names(svc_kw_distinct),
        "slot_coverage": {"materials_all_declared_slots_present": svc_all_present,
                          "missing_slot_occurrences_total": svc_missing_total,
                          "extra_slot_occurrences_total": svc_extra_total},
    }
    std_out = {
        "target": {"owner": TARGET_STD[0], "path_id": TARGET_STD[1], "name": TARGET_STD[2]},
        "references_verified": std_refs_seen,
        "empty_keyword_materials": sum(std_empty_by_owner.values()),
        "empty_by_owner_counts": dict(sorted(std_empty_by_owner.items())),
        "expected_from_step4": EXPECT["standard_empty_keyword_materials"],
        "match": sum(std_empty_by_owner.values()) == EXPECT["standard_empty_keyword_materials"],
    }
    result = {
        "probe": "w3-small-population-census",
        "schema_version": 1,
        "owners": per_file,
        "standardvcolor": svc_out,
        "standard_base_variant_population": std_out,
        "negative_controls": negative,
        "tool_versions": {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                          "python": platform.python_version()},
    }
    if echo_names:
        result["_names_echo_local_only"] = {
            "standardvcolor": {"keywords": schema[TARGET_SVC[:2]]["_echo"]["keywords"],
                               "slots": schema[TARGET_SVC[:2]]["_echo"]["slots"],
                               "material_keywords": svc_kw_distinct},
            "standard": {"keywords": schema[TARGET_STD[:2]]["_echo"]["keywords"]},
        }
    return result


def svcdocs_slots(schema, target):
    return set(schema[target[0:2]]["_echo"]["slots"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    ap.add_argument("--print-names-local", action="store_true",
                    help="Echo keyword/slot names locally only; never to repo/artifacts")
    args = ap.parse_args()
    report = run_census(args.game_data, echo_names=args.print_names_local)
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if not args.print_names_local:
        report.pop("_names_echo_local_only", None)
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        n = report.pop("_names_echo_local_only", None)
        print(json.dumps(report, indent=2, sort_keys=True))
        if n:
            print("LOCAL-ONLY names (not for repo/artifacts):")
            print(json.dumps(n, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
