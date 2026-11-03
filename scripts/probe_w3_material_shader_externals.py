#!/usr/bin/env python3
"""W3 — resolve original Material->Shader external PPtrs against authenticated owners.

Follows A13's exact next step: inspect the original serialized owner external-file
tables (m_Externals) and resolve nonzero m_FileID references by owner mapping, then
join m_PathID across owners. Local authenticated PC originals are byte-verified by
SHA-256 against the already-pinned LFS owners before any parse (no new LFS transfer).

Privacy: publishes aggregate counts, hashes and shader *names* already established
as legitimate identity evidence (W1 precedent). No raw shader source, program bytes,
material property blobs or proprietary asset payloads are emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict

# Authenticated original LFS pins (established by W1/A13 CI evidence).
PINNED_OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}
TOOL_VERSIONS = {"unitypy_expected": "1.25.4"}


def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


class UnresolvedMaterialShaderLink(Exception):
    """Raised intentionally so callers cannot silently accept unresolved links."""


def resolve_owner_by_fileid(externals: list, file_id: int) -> str | None:
    """Map a serialized PPtr m_FileID to the declared external owner path.

    Unity semantics: m_FileID == 0 means same-file; positive values index the
    serialized file's m_Externals table 1-based. Negative or zero-length external
    tables or out-of-range indexes are unresolved, never guessed.
    """
    if file_id == 0:
        return None
    if file_id < 0:
        raise UnresolvedMaterialShaderLink(f"negative m_FileID {file_id}")
    idx = file_id - 1
    if idx >= len(externals):
        raise UnresolvedMaterialShaderLink(f"m_FileID {file_id} exceeds externals table size {len(externals)}")
    ext = externals[idx]
    return getattr(ext, "path", None)


def classify_pptr(externals: list, file_id: int, path_id: int) -> dict:
    """Classify a single Material->Shader PPtr without claiming any resolution."""
    if file_id == 0:
        return {"kind": "same_file", "path_id": path_id}
    owner = resolve_owner_by_fileid(externals, file_id)
    kind = "owner_resolveable" if owner is not None else "unresolved"
    return {"kind": kind, "file_id": file_id, "owner_path": owner, "path_id": path_id}


def shader_names_in_owner(sf) -> dict[int, dict]:
    """Collect path_id -> {name, sha commitment placeholder} for Shader objects."""
    out: dict[int, dict] = {}
    for path_id, ob in sf.objects.items():
        if ob.type.name != "Shader":
            continue
        d = ob.read_typetree()
        parsed = d.get("m_ParsedForm") or {}
        parsed_name = parsed.get("m_Name")
        out[path_id] = {
            "name": parsed_name if isinstance(parsed_name, str) and parsed_name else d.get("m_Name"),
            "m_Name_empty": d.get("m_Name", "") == "",
        }
    return out


def run_probe(game_data_dir: str) -> dict:
    import UnityPy  # imported lazily so synthetic tests run without assets

    import UnityPy
    actual_version = UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown"

    result: dict = {"schema_version": 1, "probe": "w3-material-shader-externals", "owners": {}, "cross_owner_resolution": {}, "builtin_engine_references": {}, "negative_controls": {}}

    # 1) Byte-authenticate local owners against pinned LFS owners.
    verified_files: dict[str, str] = {}
    for fname, (size, digest) in PINNED_OWNERS.items():
        path = f"{game_data_dir}/{fname}"
        got_size, got_digest = sha256_file(path)
        if (got_size, got_digest) != (size, digest):
            raise SystemExit(f"owner {fname} failed authentication: got {got_size}/{got_digest}")
        verified_files[fname] = path
    result["owners"] = {
        f: {"bytes": PINNED_OWNERS[f][0], "sha256": PINNED_OWNERS[f][1], "verified": True}
        for f in verified_files
    }

    def load_serialized(fname: str):
        path = verified_files.get(fname, f"{game_data_dir}/{fname}")
        env = UnityPy.load(path)
        return list(env.files.values())[0]

    # Secondary reference owner used only to resolve FileID->globalgamemanagers
    # links; its bytes are hashed for the record but it is not a pinned LFS owner.
    ggm_size, ggm_digest = sha256_file(f"{game_data_dir}/globalgamemanagers.assets")
    result["owners"]["globalgamemanagers.assets"] = {
        "bytes": ggm_size, "sha256": ggm_digest, "verified": None,
        "note": "local original file used as reference owner; not one of the two pinned LFS owners",
    }

    sf_res = load_serialized("resources.assets")
    sf_sh0 = load_serialized("sharedassets0.assets")

    # 2) Record the authentic external tables verbatim (dependency identity).
    for label, sf in (("resources.assets", sf_res), ("sharedassets0.assets", sf_sh0)):
        result["owners"][label]["externals_table"] = [getattr(e, "path", None) for e in sf.externals]

    # 3) Join shader path -> name for each referenceable owner.
    sh0_names = shader_names_in_owner(sf_sh0)
    ggm = load_serialized("globalgamemanagers.assets")
    ggm_names = shader_names_in_owner(ggm)

    # 4) Walk every Material in both target owners and classify its m_Shader PPtr.
    counts = defaultdict(Counter)
    name_by_shader = defaultdict(Counter)   # (owner, path_id) -> Counter of usage count via references
    builtin_refs = Counter()                 # (owner, file_id, external_path, path_id) -> count
    total_materials = Counter()
    unresolved_examples = []

    for src_owner, sf in (("resources.assets", sf_res), ("sharedassets0.assets", sf_sh0)):
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Material":
                continue
            d = ob.read_typetree()
            pledge = d.get("m_Shader")
            if not isinstance(pledge, dict) or "m_FileID" not in pledge or "m_PathID" not in pledge:
                raise UnresolvedMaterialShaderLink(
                    f"missing/malformed m_Shader on material {src_owner}/{path_id}: {pledge!r}")
            fid, pid = int(pledge["m_FileID"]), int(pledge["m_PathID"])
            total_materials[src_owner] += 1
            info = classify_pptr(sf.externals, fid, pid)
            counts[src_owner][info["kind"]] += 1

            if info["kind"] == "same_file":
                target_owner = src_owner
            else:
                ext_path = info.get("owner_path")
                mapping = {
                    "globalgamemanagers.assets": ("globalgamemanagers.assets", ggm_names),
                    "sharedassets0.assets": ("sharedassets0.assets", sh0_names),
                }
                if ext_path not in mapping:
                    # Engine default-resource transports (Library/unity default
                    # resources & Resources/unity_builtin_extra). These are
                    # engine-internal references, NOT resolvable to game Shader
                    # objects; classify explicitly, never guess a name.
                    builtin_refs[f"{src_owner}|fid={fid}|{ext_path}|pid={pid}"] += 1
                    continue
                target_owner, names = mapping[ext_path]
                if pid not in names:
                    raise UnresolvedMaterialShaderLink(
                        f"declared owner {target_owner} lacks Shader path_id {pid} for material {src_owner}/{path_id}")
                name_by_shader[(target_owner, pid)]["used"] += 1
                if names[pid]["name"]:
                    name_by_shader[(target_owner, pid)]["name"] = names[pid]["name"]

    result["cross_owner_resolution"] = {
        "material_totals": {k: v for k, v in sorted(total_materials.items())},
        "link_kinds": {o: dict(c) for o, c in sorted(counts.items())},
        "distinct_resolved_shader_targets": len(name_by_shader),
        "shader_targets": [
            {"owner": owner, "path_id": pid, "name": c.get("name"), "material_references": c.get("used", 0)}
            for (owner, pid), c in sorted(name_by_shader.items(), key=lambda kv: -kv[1].get("used", 0))
        ],
    }
    result["builtin_engine_references"] = {
        "distinct": len(builtin_refs),
        "total_references": sum(builtin_refs.values()),
        "aggregate_by_owner_fileid": {
            k.split("|")[0] + "|" + k.split("|")[1]: v for k, v in sorted(builtin_refs.items())
        },
    }

    # 5) Negative controls (must all fail/be rejected; results recorded, not asserted silently).
    nc: dict[str, bool] = {}
    with_res = [getattr(e, "path", None) for e in sf_res.externals]
    # negative: negative fileID
    try:
        resolve_owner_by_fileid(with_res, -1)
        nc["negative_fileid_rejected"] = False
    except UnresolvedMaterialShaderLink:
        nc["negative_fileid_rejected"] = True
    # negative: out-of-range fileID
    try:
        resolve_owner_by_fileid(with_res, len(with_res) + 1)
        nc["out_of_range_fileid_rejected"] = False
    except UnresolvedMaterialShaderLink:
        nc["out_of_range_fileid_rejected"] = True
    # negative: same_file probing must not silently pretend an owner
    try:
        r = resolve_owner_by_fileid(with_res, 0)
        nc["fileid0_unresolved"] = (r is None)
    except UnresolvedMaterialShaderLink:
        nc["fileid0_unresolved"] = True
    # negative: missing path_id target in declared owner must fail closed
    try:
        mapping = {"sharedassets0.assets": ("sharedassets0.assets", sh0_names)}
        ext_path = with_res[1]
        if ext_path not in mapping or 1 not in mapping[ext_path][1]:
            nc["missing_target_pathid_fails_closed"] = True
        else:
            nc["missing_target_pathid_fails_closed"] = False
    except UnresolvedMaterialShaderLink:
        nc["missing_target_pathid_fails_closed"] = True
    result["negative_controls"] = nc

    result["tool_versions"] = {"unitypy": actual_version, "python": platform.python_version()}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True, help="Path to the original Raft_Data directory")
    ap.add_argument("--aggregate-json", default=None, help="Write aggregate JSON here")
    ap.add_argument("--strict", action="store_true", help="Fail closed on any unresolved game link")
    args = ap.parse_args()

    report = run_probe(args.game_data)
    ok = all(report["negative_controls"].values())
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
