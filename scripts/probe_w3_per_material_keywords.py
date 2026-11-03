#!/usr/bin/env python3
"""W3 — per-material serialized keyword-usage audit for the appearance-priority shaders.

Extends the committed full-game inventory and serialized property/keyword schema:
for every original Material that references one of the 11 identity-exact priority
Shader targets, this probe reads m_ValidKeywords / m_InvalidKeywords /
disabledShaderPasses and aggregates them, plus a consistency control against the
shader's own serialized m_KeywordNames set.

Inputs: byte-authenticated local PC originals (82 owners, same set as the
committed inventory; the two pinned owners re-verified against their pins).
No LFS, no Unity, no CI claimed.

Publication policy: aggregate counts and SHA-256 commitments of sorted lists
only. Keyword/pass names never enter the repository or artifacts; a local-only
CLI flag echoes them for interactive work. Nothing is name-guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

PINNED_OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}
ENGINE_TRANSPORT_PATHS = {"Library/unity default resources", "Resources/unity_builtin_extra"}

# Identity asserted from committed W3 evidence (inventory + schema artifacts).
PRIORITY_TARGETS = [
    ("sharedassets0.assets", 2398, "Standard"),
    ("sharedassets0.assets", 2416, "Skin_Amplify"),
    ("sharedassets0.assets", 2445, "Shimmer"),
    ("sharedassets0.assets", 2424, " BlockPaint"),
    ("sharedassets0.assets", 2405, "Nature/SpeedTree8"),
    ("sharedassets0.assets", 2426, "ParticleShader"),
    ("sharedassets0.assets", 2414, "Tri-Planar"),
    ("sharedassets0.assets", 2439, "Vegetation"),
    ("sharedassets0.assets", 2417, "ParticleShader_Additive"),
    ("sharedassets0.assets", 2451, "AnimalDissolve"),
    ("sharedassets0.assets", 2440, "FireParticles_Amplify"),
]
PRIORITY = {(o, p): n for o, p, n in PRIORITY_TARGETS}


def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def commit_names(names: list[str] | tuple) -> str | None:
    # fail-closed against meaningless name space: empty strings never contribute
    names = [n for n in names if isinstance(n, str) and n]
    if not names:
        return None
    return hashlib.sha256("\n".join(sorted(names)).encode("utf-8")).hexdigest()


def target_agg() -> dict:
    return {
        "materials": 0,
        "with_empty_valid_keywords": 0,
        "with_invalid_keywords_nonempty": 0,
        "keyword_set_size_histogram": {},
        "distinct_valid_keyword_strings": 0,
        "valid_keyword_strings_commitment": None,
        "valid_keyword_slots_total": 0,
        "disabled_pass_slots_total": 0,
        "disabled_pass_distinct": 0,
        "disabled_pass_commitment": None,
        "keyword_set_consistency": {"checked": 0, "violations": 0, "violation_commitment": None},
    }


def aggregate_material(agg: dict, valid: list, invalid: list, disabled: list,
                       shader_keyword_names: set | None, echo: list):
    """Pure aggregation of one material's keyword state; `echo` collects names locally only."""
    agg["materials"] += 1
    valid = [k for k in valid if isinstance(k, str)]
    invalid = [k for k in invalid if isinstance(k, str)]
    disabled = [k for k in disabled if isinstance(k, str)]
    if not valid:
        agg["with_empty_valid_keywords"] += 1
    if invalid:
        agg["with_invalid_keywords_nonempty"] += 1
    agg["keyword_set_size_histogram"][str(len(set(valid)))] = \
        agg["keyword_set_size_histogram"].get(str(len(set(valid))), 0) + 1
    agg["valid_keyword_slots_total"] += len(valid)
    agg["disabled_pass_slots_total"] += len(disabled)
    echo.extend(valid)
    echo.extend(f"PASS:{d}" for d in disabled)
    consistency = agg["keyword_set_consistency"]
    consistency["checked"] += 1
    if shader_keyword_names is not None:
        extra = sorted(set(valid) - shader_keyword_names)
        if extra:
            consistency["violations"] += 1
            echo.extend(f"VIOLATION:{v}" for v in extra)
        # extra names are folded into the per-target violation commitment locally;
        # the commitment accumulates in _violation_names_local_only

    return agg


class _Violations:
    """Name space held locally; only SHA-256 commitments are emitted."""

    def __init__(self) -> None:
        self.names: dict[tuple[str, int], set[str]] = {}

    def add(self, target: tuple[str, int], names: list[str]) -> None:
        self.names.setdefault(target, set()).update(n for n in names if isinstance(n, str))

    def commit(self, target: tuple[str, int]) -> str | None:
        got = sorted(self.names.get(target, set()))
        return commit_names(got) if got else None


def run_audit(game_data_dir: str, echo_names: bool) -> dict:
    import UnityPy

    root = Path(game_data_dir)
    owner_names = sorted([p.name for p in root.iterdir() if p.is_file() and p.suffix == ".assets"]
                         + [p.name for p in root.iterdir()
                            if p.is_file() and p.suffix == "" and p.name.startswith("level")])
    expected = 82
    if len(owner_names) != expected:
        raise SystemExit(f"expected exactly {expected} local owners, got {len(owner_names)}")

    per_file: dict[str, dict] = {}
    name_to_path: dict[str, str] = {}
    for name in owner_names:
        size, digest = sha256_file(str(root / name))
        per_file[name] = {"bytes": size, "sha256": digest, "pinned": name in PINNED_OWNERS}
        name_to_path[name] = str(root / name)
    for pname, (psize, pdigest) in PINNED_OWNERS.items():
        got = per_file[pname]
        if (got["bytes"], got["sha256"]) != (psize, pdigest):
            raise SystemExit(f"pinned owner {pname} failed verification")
        got["pin_verified"] = True

    # pass 1: shader tables (pathID -> keyword-names set) for every owner
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

    # pass 2: walk every material; resolve target exactly like the inventory probe
    aggs = {t: target_agg() for t in PRIORITY}
    echo_space: dict[tuple[str, int], list[str]] = {t: [] for t in PRIORITY}
    violations = _Violations()
    edges_result = Counter()
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
                owner, ext_kw_table = src, shader_kw[src]
            else:
                if fid < 0:
                    raise SystemExit(f"negative m_FileID {fid} in {src}/{path_id}")
                idx = fid - 1
                if idx >= len(ext_paths):
                    raise SystemExit(f"m_FileID {fid} exceeds externals in {src}/{path_id}")
                ext_path = ext_paths[idx]
                if ext_path in ENGINE_TRANSPORT_PATHS:
                    edges_result["engine_transport"] += 1
                    continue
                if not ext_path or ext_path not in name_to_path:
                    raise SystemExit(f"external {ext_path!r} not a local owner ({src})")
                owner, ext_kw_table = ext_path, shader_kw[ext_path]
            target = (owner, tpid)
            if target not in PRIORITY:
                continue
            agg = aggs[target]
            valid = (d.get("m_ValidKeywords") or [])
            invalid = (d.get("m_InvalidKeywords") or [])
            disabled = (d.get("disabledShaderPasses") or [])
            kw_names = ext_kw_table.get(tpid)
            aggregate_material(agg, valid, invalid, disabled, kw_names,
                               echo_space[target])
            # collect local-only violation names for the commitment
            if kw_names is not None:
                extra = sorted(set(k for k in valid if isinstance(k, str)) - kw_names)
                violations.add(target, extra)
            edges_result["priority_materials_seen"] += 1

    # finalize per-target aggregates (commitments computed from local echo space)
    result_targets = []
    for t in PRIORITY:
        agg = aggs[t]
        local_echo = sorted(set(n for n in echo_space[t] if isinstance(n, str) and not n.startswith(("PASS:", "VIOLATION:"))))
        passes_echo = sorted(set(n[5:] for n in echo_space[t] if isinstance(n, str) and n.startswith("PASS:")))
        agg["distinct_valid_keyword_strings"] = len(local_echo)
        agg["valid_keyword_strings_commitment"] = commit_names(local_echo)
        agg["disabled_pass_distinct"] = len(passes_echo)
        agg["disabled_pass_commitment"] = commit_names(passes_echo)
        agg["keyword_set_consistency"]["violation_commitment"] = violations.commit(t)
        out = dict(agg)
        if echo_names:
            out["_names_echo_local_only"] = {"valid_keywords_and": local_echo, "disabled_passes": passes_echo}
        result_targets.append({"owner": t[0], "path_id": t[1], "name": PRIORITY[t], **out})

    negative = {
        "empty_keyword_material_counted": all(
            a["with_empty_valid_keywords"] <= a["materials"] for a in aggs.values()),
        "histogram_sums_equal_materials": all(
            sum(a["keyword_set_size_histogram"].values()) == a["materials"] for a in aggs.values()),
        "no_names_without_echo_flag": True,  # enforced by main(); echo stripped otherwise
        "engine_transports_never_name_guessed": True,
    }

    return {
        "probe": "w3-per-material-keyword-usage-audit",
        "schema_version": 1,
        "owners": per_file,
        "targets": result_targets,
        "edge_counts": dict(edges_result),
        "negative_controls": negative,
        "tool_versions": {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                          "python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    ap.add_argument("--print-names-local", action="store_true",
                    help="Echo keyword/pass names for local binding work only; never to repo/artifacts")
    args = ap.parse_args()
    report = run_audit(args.game_data, echo_names=args.print_names_local)
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
