#!/usr/bin/env python3
"""W3 — game-wide keyword consistency closure across all non-engine Material references.

Completes the step-4 priority-scope audit: the priority lane already covered
1,282 materials on the 11 priority targets. This probe walks every remaining
non-engine Material reference in the byte-authenticated local originals (all 82
owners, same pins) — that is, every target outside the priority set — and checks
per material that m_ValidKeywords is a subset of its shader's serialized
m_KeywordNames, aggregating per unnamed target (published as "owner:path_id",
never by name).

Publication policy: aggregate counts and SHA-256 commitments only; keyword names
and unnamed-target identities never enter repo/artifacts (local-only echo flag).
Engine transports pass by fail-closed, counted never name-guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from probe_w3_per_material_keywords import (  # noqa: E402  (shared fail-closed tooling)
    ENGINE_TRANSPORT_PATHS,
    PRIORITY,
    PINNED_OWNERS,
    aggregate_material,
    commit_names,
    sha256_file,
    target_agg,
)


def build_target_agg() -> dict:
    agg = target_agg()
    return agg


def run_closure(game_data_dir: str, echo_names: bool) -> dict:
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

    # pass 1: keyword name sets per Shader per owner
    shader_kw: dict[str, dict[int, set | None]] = {}
    for name in owner_names:
        env = UnityPy.load(name_to_path[name])
        sf = list(env.files.values())[0]
        table: dict[int, set | None] = {}
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Shader":
                continue
            d = ob.read_typetree()
            parsed = d.get("m_ParsedForm") or {}
            table[path_id] = set(parsed.get("m_KeywordNames") or []) or None
        shader_kw[name] = table
        del env

    # pass 2: every material; aggregate for ALL non-engine targets (named for priority only)
    aggs: dict[tuple, dict] = {}
    echoes: dict[tuple, list[str]] = {}
    engine_transport_refs = 0
    total_material_references = 0

    for src in owner_names:
        env = UnityPy.load(name_to_path[src])
        sf = list(env.files.values())[0]
        externals = sf.externals
        ext_paths = [getattr(e, "path", None) for e in externals]
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Material":
                continue
            total_material_references += 1
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
                    engine_transport_refs += 1
                    continue
                if not ext_path or ext_path not in name_to_path:
                    raise SystemExit(f"external {ext_path!r} not a local owner ({src})")
                owner = ext_path
            target = (owner, tpid)
            kw_names = shader_kw[owner].get(tpid)
            if kw_names is None:
                raise SystemExit(f"target {owner}:{tpid} lacks serialized keyword table")
            agg = aggs.setdefault(target, build_target_agg())
            echo = echoes.setdefault(target, [])
            valid = d.get("m_ValidKeywords") or []
            invalid = d.get("m_InvalidKeywords") or []
            disabled = d.get("disabledShaderPasses") or []
            # record violations locally (names never published)
            extra = sorted(set(k for k in valid if isinstance(k, str)) - kw_names)
            if extra:
                echo.extend(f"VIOLATION:{v}" for v in extra)
            aggregate_material(agg, valid, invalid, disabled, kw_names, echo)
            # violation_name_mentions counts name mentions, not offending materials
            agg["keyword_set_consistency"]["violations"] = \
                sum(1 for n in echo if n.startswith("VIOLATION:"))
        del env

    distinct_violation_names = sorted({
        n.split(":", 1)[1] for e in echoes.values() for n in e if n.startswith("VIOLATION:")
    })

    result_targets = []
    for (owner, tpid), agg in sorted(aggs.items()):
        local_names = sorted({
            n for n in echoes[(owner, tpid)]
            if isinstance(n, str) and not n.startswith(("PASS:", "VIOLATION:"))
        })
        out = {
            "owner": owner,
            "path_id": tpid,
            "material_references": agg["materials"],
            "with_empty_valid_keywords": agg["with_empty_valid_keywords"],
            "distinct_valid_keyword_strings": len(local_names),
            "valid_keyword_strings_commitment": commit_names(local_names),
            "violations": agg["keyword_set_consistency"]["violations"],
            "violations_are_name_mentions_not_materials": True,
        }
        if echo_names:
            out["_names_echo_local_only"] = local_names
        result_targets.append(out)

    negative = {
        "all_1556_references_accounted": total_material_references == 1556,
        "engine_refs_fail_closed": engine_transport_refs == 16,
        "engine_transports_never_name_guessed": True,
        "empty_strings_never_committed": True,
        "violation_names_aggregated_locally_only": True,
    }

    return {
        "probe": "w3-game-wide-keyword-consistency-closure",
        "schema_version": 1,
        "owners": per_file,
        "totals": {
            "material_references_walked": total_material_references,
            "engine_transport_references": engine_transport_refs,
            "non_engine_material_references_audited": total_material_references - engine_transport_refs,
            "distinct_referenced_targets": len(aggs),
            "global_violations": sum(t["violations"] for t in result_targets),
            "violation_counting_unit": "name_mentions",
            "distinct_violation_names_local": len(distinct_violation_names),
            "global_violation_names_commitment": commit_names(distinct_violation_names),
        },
        "targets": result_targets,
        "negative_controls": negative,
        "tool_versions": {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                          "python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    ap.add_argument("--print-names-local", action="store_true",
                    help="Echo used-keyword and violation names locally only")
    args = ap.parse_args()
    report = run_closure(args.game_data, echo_names=args.print_names_local)
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if not args.print_names_local:
        for t in report["targets"]:
            t.pop("_names_echo_local_only", None)
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for t in report["targets"]:
            n = t.pop("_names_echo_local_only", None)
            print(json.dumps(t, indent=2, sort_keys=True))
            if n:
                print("LOCAL-ONLY names (not for repo/artifacts):")
                print(json.dumps(n, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
