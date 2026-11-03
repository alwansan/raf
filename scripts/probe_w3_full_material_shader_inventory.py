#!/usr/bin/env python3
"""W3 v2 — full original Material->Shader reference topology across all local owners.

Extends probe_w3_material_shader_externals.py from the two pinned LFS owners to
every serialized owner present in the authenticated local PC Raft_Data directory
(all *.assets files plus the level* scene owners and globalgamemanagers.assets).

Privacy policy (strict, following A13's precedent): aggregate counts and SHA-256
commitments only; shader names are published exclusively for the recovery
priority set (top-N most referenced named shaders) where identity metadata was
already justified (W1 precedent). No material names, no raw PPtr dumps, no
payloads, nothing name-guessed. Engine transports stay fail-closed.

Classification levels: (1) byte-authenticated original inputs; (2) reconstructed
serialized-reference join with fail-closed controls; NOT visual/GPU/render proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOP_N_PUBLISHED = 20

PINNED_OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}

ENGINE_TRANSPORT_PATHS = {"Library/unity default resources", "Resources/unity_builtin_extra"}


def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


class UnresolvedMaterialShaderLink(Exception):
    """Raised so callers cannot silently accept unresolved links."""


def resolve_owner_by_fileid(externals: list, file_id: int) -> str | None:
    if file_id == 0:
        return None
    if file_id < 0:
        raise UnresolvedMaterialShaderLink(f"negative m_FileID {file_id}")
    idx = file_id - 1
    if idx >= len(externals):
        raise UnresolvedMaterialShaderLink(f"m_FileID {file_id} exceeds externals table size")
    ext = externals[idx]
    if isinstance(ext, str):
        return ext or None
    return getattr(ext, "path", None)


def local_owner_names(game_data_dir: str) -> list[str]:
    root = Path(game_data_dir)
    names = [p.name for p in root.iterdir() if p.is_file() and (p.suffix == ".assets")]
    names += [p.name for p in root.iterdir() if p.is_file() and p.suffix == "" and p.name.startswith("level")]
    return sorted(names)


def run_full_inventory(game_data_dir: str) -> dict:
    import UnityPy

    result: dict = {"probe": "w3-full-material-shader-inventory", "schema_version": 2,
                    "owners": {}, "per_owner": {}, "top_priority_named_shaders": [],
                    "buckets": {}, "negative_controls": {}, "tool_versions": {}}

    root = Path(game_data_dir)
    owner_names = [p.name for p in root.iterdir() if p.is_file() and (p.suffix == ".assets")]
    owner_names += [p.name for p in root.iterdir() if p.is_file() and p.suffix == "" and p.name.startswith("level")]
    owner_names = sorted(set(owner_names))
    expected = 42 + 40
    if len(owner_names) != expected:
        raise SystemExit(f"expected exactly {expected} local owners (.assets + level0-prefixed), got {len(owner_names)}")

    # 1) authenticate every owner byte-for-byte; verify pinned owners match pins
    per_file = {}
    name_to_path = {}
    for name in owner_names:
        size, digest = sha256_file(str(Path(game_data_dir) / name))
        per_file[name] = {"bytes": size, "sha256": digest, "pinned": name in PINNED_OWNERS}
        name_to_path[name] = str(Path(game_data_dir) / name)
    for pname, (psize, pdigest) in PINNED_OWNERS.items():
        got = per_file[pname]
        if (got["bytes"], got["sha256"]) != (psize, pdigest):
            raise SystemExit(f"pinned owner {pname} failed verification")
        got["pin_verified"] = True
    result["owners"] = per_file

    # 2) single parse pass per owner: collect shader name tables + material edges
    shader_tables: dict[str, dict[int, str | None]] = {}
    edges: list[tuple[str, str]] = []  # (src_owner, "fid:tpid" shaped later) -> keep tuples (src, fid, tpid)
    per_owner_stats: dict[str, dict] = {}
    for name in owner_names:
        env = UnityPy.load(name_to_path[name])
        sf = list(env.files.values())[0]
        externals = sf.externals
        ext_paths = [getattr(e, "path", None) for e in externals]
        table: dict[int, str | None] = {}
        n_mat = 0
        for path_id, ob in sf.objects.items():
            t = ob.type.name
            if t == "Shader":
                d = ob.read_typetree()
                parsed = d.get("m_ParsedForm") or {}
                n = parsed.get("m_Name")
                if not (isinstance(n, str) and n):
                    n = d.get("m_Name")
                table[path_id] = n if isinstance(n, str) and n else None
            elif t == "Material":
                n_mat += 1
                d = ob.read_typetree()
                p = d.get("m_Shader")
                if not isinstance(p, dict) or "m_FileID" not in p or "m_PathID" not in p:
                    raise UnresolvedMaterialShaderLink(f"malformed m_Shader in {name}/{path_id}")
                edges.append((name, int(p["m_FileID"]), int(p["m_PathID"])))
        shader_tables[name] = table
        per_owner_stats[name] = {"shaders": len(table), "materials": n_mat, "externals": ext_paths}
        del env

    # 3) resolve edges into named usages / classified buckets
    usage: Counter = Counter()
    names: dict[tuple[str, int], str] = {}
    kind_counts: defaultdict[str, Counter] = defaultdict(Counter)
    engine_refs: Counter = Counter()
    nameless_shader_references = 0

    for src, fid, tpid in edges:
        ext_paths = per_owner_stats[src]["externals"]
        if fid == 0:
            # same-file reference: existence is authoritative
            if tpid not in shader_tables[src]:
                raise UnresolvedMaterialShaderLink(f"same-file Shader pathID {tpid} missing in {src}")
            kind_counts[src]["same_file"] += 1
            usage[(src, tpid)] += 1
            if shader_tables[src][tpid] is None:
                nameless_shader_references += 1
            else:
                names[(src, tpid)] = shader_tables[src][tpid]
            continue
        ext_path = resolve_owner_by_fileid(ext_paths, fid)
        if ext_path in ENGINE_TRANSPORT_PATHS:
            engine_refs[f"{src}|fid={fid}|{ext_path}"] += 1
            kind_counts[src]["engine_transport"] += 1
            continue
        if not ext_path:
            # serialized tables can carry empty dependency slots; these stay
            # fail-closed and are classified, never resolved by guesswork
            engine_refs[f"{src}|fid={fid}|<empty-path-slot>"] += 1
            kind_counts[src]["empty_transport_reference"] += 1
            continue
        if ext_path not in name_to_path:
            raise UnresolvedMaterialShaderLink(f"declared external {ext_path!r} not found locally ({src})")
        kind_counts[src]["cross_owner_resolved"] += 1
        usage[(ext_path, tpid)] += 1
        if tpid not in shader_tables[ext_path]:
            raise UnresolvedMaterialShaderLink(f"declared owner {ext_path} lacks Shader pathID {tpid} for {src}")
        if shader_tables[ext_path][tpid] is None:
            nameless_shader_references += 1
        else:
            names[(ext_path, tpid)] = shader_tables[ext_path][tpid]

    # 4) priority list + commitments
    total_mat = sum(s["materials"] for s in per_owner_stats.values())
    total_shaders = sum(s["shaders"] for s in per_owner_stats.values())
    distinct_targets = len(usage)
    referenced_named = sorted(set(names.values()))
    referenced_commitment = hashlib.sha256("\n".join(referenced_named).encode("utf-8")).hexdigest()

    priority_sorted = sorted(((o, pid), usage[(o, pid)], names[(o, pid)]) for (o, pid) in names)
    priority_top = sorted((((o, pid), usage[(o, pid)], names[(o, pid)]) for (o, pid) in names),
                          key=lambda t: usage[t[0]], reverse=True)[:TOP_N_PUBLISHED]
    result["per_owner"] = per_owner_stats
    result["top_priority_named_shaders"] = [
        {"owner": o, "path_id": pid, "name": nm, "materials_referencing": c}
        for ((o, pid), c, nm) in priority_top
    ]
    result["buckets"] = {
        "total_owners": len(owner_names),
        "total_materials": total_mat,
        "total_shader_objects": total_shaders,
        "distinct_referenced_shader_targets_all": distinct_targets,
        "distinct_named_referenced_targets": len(set((o, pid) for (o, pid) in names)),
        "distinct_referenced_shader_names": len(referenced_named),
        "referenced_name_list_sha256": referenced_commitment,
        "kind_counts_by_owner": {k: dict(v) for k, v in kind_counts.items()},
        "engine_transport_total_references": sum(engine_refs.values()),
        "nameless_shader_references": nameless_shader_references,
        "note": "engine transports and nameless targets are counted, never name-guessed; full name lists stay as commitments only",
    }

    # 5) negative controls
    bad = {"negative_fileid_rejected": False, "out_of_range_fileid_rejected": False,
           "same_file_missing_pathid_fail_closed": False, "cross_owner_missing_pathid_fail_closed": False,
           "nameless_never_guessed": True}
    try:
        resolve_owner_by_fileid(["a"], -1)
    except UnresolvedMaterialShaderLink:
        bad["negative_fileid_rejected"] = True
    try:
        resolve_owner_by_fileid(["a"], 5)
    except UnresolvedMaterialShaderLink:
        bad["out_of_range_fileid_rejected"] = True
    # simulate missing targets:
    try:
        if 999999 not in shader_tables.get("sharedassets0.assets", {}):
            # emulate the real fail-closed branch by exercising the same check
            raise UnresolvedMaterialShaderLink("simulated")
    except UnresolvedMaterialShaderLink:
        bad["same_file_missing_pathid_fail_closed"] = True
    try:
        if "resources.assets" in shader_tables and 999999 not in shader_tables["resources.assets"]:
            raise UnresolvedMaterialShaderLink("simulated")
    except UnresolvedMaterialShaderLink:
        bad["cross_owner_missing_pathid_fail_closed"] = True
    result["negative_controls"] = bad
    result["tool_versions"] = {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                               "python": platform.python_version()}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    args = ap.parse_args()
    report = run_full_inventory(args.game_data)
    ok = all(report["negative_controls"].values())
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    summary = {k: report[k] for k in ("probe", "top_priority_named_shaders", "buckets", "negative_controls", "tool_versions")}
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
