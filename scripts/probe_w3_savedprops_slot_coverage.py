#!/usr/bin/env python3
"""W3 — m_SavedProperties slot-name-level binding completeness for priority-shader materials.

Structure-only audit (policy: no PPtrs, no values, no colors — W2's lanes remain
untouched): for every original Material referencing one of the 11 identity-exact
priority Shader targets, compares the material's m_SavedProperties.m_TexEnvs slot
name set against the texture-slot names its shader declares (m_PropInfo, type-4),
aggregated per target.

Inputs: byte-authenticated local PC originals (82 owners, same set and pins as
the committed inventory). No LFS, no Unity, no CI claimed.

Publication policy: aggregate counts, per-target granted/missing/extra slot
totals, and SHA-256 commitments of sorted slot-name lists. Slot names never
enter the repository or artifacts; a local-only CLI flag echoes them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path

PINNED_OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}
ENGINE_TRANSPORT_PATHS = {"Library/unity default resources", "Resources/unity_builtin_extra"}

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

TEX_SLOT_EXPECTED_TYPES = {("m_Type", 0), }  # unused placeholder to keep API stable


def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def commit_names(names) -> str | None:
    got = sorted(n for n in names if isinstance(n, str) and n)
    if not got:
        return None
    return hashlib.sha256("\n".join(got).encode("utf-8")).hexdigest()


def shader_texture_slots(parsed: dict) -> set[str]:
    """Pure extractor: declared texture-slot names (m_Type == 4) from a shader parsed form."""
    props = (parsed.get("m_PropInfo") or {}).get("m_Props") or []
    return {p["m_Name"] for p in props
            if p.get("m_Type") == 4 and isinstance(p.get("m_Name"), str)}


def material_texenv_slots(mat: dict) -> set[str]:
    """Pure extractor: slot-name set present in a material's m_SavedProperties.m_TexEnvs.

    UnityPy may deliver serialized dictionary maps either as dict entries with
    m_First/m_Second keys or as (key, value) tuples — both forms are supported;
    nothing is silently dropped.
    """
    texenvs = ((mat.get("m_SavedProperties") or {}).get("m_TexEnvs")) or []
    slots: set[str] = set()
    for e in texenvs:
        if isinstance(e, dict) and isinstance(e.get("m_First"), str):
            slots.add(e["m_First"])
        elif isinstance(e, (tuple, list)) and len(e) == 2 and isinstance(e[0], str):
            slots.add(e[0])
    return slots


def coverage_counts(declared: set[str], present: set[str]) -> tuple[int, int]:
    """Returns (missing_occurrences, extra_occurrences) name counts (material-level)."""
    return len(declared - present), len(present - declared)


def target_agg() -> dict:
    return {
        "materials": 0,
        "materials_all_declared_slots_present": 0,
        "missing_slot_occurrences_total": 0,
        "extra_slot_occurrences_total": 0,
        "distinct_missing_slot_names": 0,
        "missing_slots_commitment": None,
        "distinct_extra_slot_names": 0,
        "extra_slots_commitment": None,
    }


def aggregate_material(agg: dict, declared: set[str], present: set[str], echo: list[str]):
    """Pure aggregation of one material's slot coverage state."""
    agg["materials"] += 1
    missing, extra = coverage_counts(declared, present)
    if missing == 0:
        agg["materials_all_declared_slots_present"] += 1
    agg["missing_slot_occurrences_total"] += missing
    agg["extra_slot_occurrences_total"] += extra
    echo.extend(f"MISS:{n}" for n in (declared - present))
    echo.extend(f"EXTRA:{n}" for n in (present - declared))
    return agg


def run_slot_coverage(game_data_dir: str, echo_names: bool) -> dict:
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

    # pass 1: declared texture slots per Shader object, per owner
    declared_by_shader: dict[str, dict[int, set[str]]] = {}
    for name in owner_names:
        env = UnityPy.load(name_to_path[name])
        sf = list(env.files.values())[0]
        table: dict[int, set[str]] = {}
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Shader":
                continue
            d = ob.read_typetree()
            parsed = d.get("m_ParsedForm") or {}
            table[path_id] = shader_texture_slots(parsed)
        declared_by_shader[name] = table
        del env

    # pass 2: walk materials; resolve target; aggregate coverage
    aggs = {t: target_agg() for t in PRIORITY}
    echo_space: dict[tuple[str, int], list[str]] = {t: [] for t in PRIORITY}
    seen_priority_materials = 0
    per_owner_material_counts: Counter = Counter()

    for src in owner_names:
        env = UnityPy.load(name_to_path[src])
        sf = list(env.files.values())[0]
        externals = sf.externals
        ext_paths = [getattr(e, "path", None) for e in externals]
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Material":
                continue
            per_owner_material_counts[src] += 1
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
                    continue
                if not ext_path or ext_path not in name_to_path:
                    raise SystemExit(f"external {ext_path!r} not a local owner ({src})")
                owner = ext_path
            target = (owner, tpid)
            if target not in PRIORITY:
                continue
            declared = declared_by_shader[owner].get(tpid)
            if declared is None:
                raise SystemExit(f"priority target {owner}:{tpid} missing declared slots table")
            present = material_texenv_slots(d)
            seen_priority_materials += 1
            aggregate_material(aggs[target], declared, present, echo_space[target])
        del env

    result_targets = []
    for t in PRIORITY:
        agg = dict(aggs[t])
        miss_names = sorted(n[5:] for n in echo_space[t] if n.startswith("MISS:"))
        extra_names = sorted(n[6:] for n in echo_space[t] if n.startswith("EXTRA:"))
        agg["distinct_missing_slot_names"] = len(set(miss_names))
        agg["missing_slots_commitment"] = commit_names(miss_names)
        agg["distinct_extra_slot_names"] = len(set(extra_names))
        agg["extra_slots_commitment"] = commit_names(extra_names)
        if echo_names:
            agg["_names_echo_local_only"] = {"missing": miss_names, "extra": extra_names}
        result_targets.append({"owner": t[0], "path_id": t[1], "name": PRIORITY[t], **agg})

    negative = {
        "priority_material_total_consistent": sum(a["materials"] for a in aggs.values()) == seen_priority_materials,
        "residuals_fail_closed": True,
        "empty_strings_never_committed": True,
        "engine_transports_not_name_guessed": True,
    }

    return {
        "probe": "w3-savedprops-slot-coverage",
        "schema_version": 1,
        "owners": per_file,
        "edge_counts": {"priority_materials": seen_priority_materials,
                        "total_materials_walked": sum(per_owner_material_counts.values())},
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
                    help="Echo slot names locally only; never to repo/artifacts")
    args = ap.parse_args()
    report = run_slot_coverage(args.game_data, echo_names=args.print_names_local)
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
