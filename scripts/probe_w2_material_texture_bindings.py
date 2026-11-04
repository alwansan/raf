"""Aggregates the original Material texture-binding usage across every
serialized owner.

Purpose: ring 8 of the W2 pale-surface chain — after color space, texture
flags, tints and sampler settings, the next way a port loses surfaces is
dropping or corrupting the material→texture bindings (``m_SavedProperties.
m_TexEnvs`` → ``m_Texture`` PPtr). If an export rebuilds material documents
with ``m_FileID=0, m_PathID=0`` everywhere (or re-points them at the wrong
external), surfaces render flat/pale even when everything above is correct.

Per owner, only integer counters are emitted:
- material count;
- per texture-slot name: how many materials bind the slot (``m_FileID != 0
  or m_PathID != 0``) vs leave it null (slot names are engine packaging
  metadata — comparable to keyword names per W3's precedent);
- ``m_FileID`` distribution of bound entries (external-reference shape);
- per named slot: binding count split by fileID.

Fail-closed: entry shapes enforced (2-tuple with a name string and a dict
containing ``m_Texture`` with ``m_FileID``/``m_PathID`` integers ≥ 0);
negative or non-integer path IDs hard-fail. No object names, path IDs,
payload bytes or float values are published, and the committed-object
identity check from ``probe_w2_fullgame_texture_colors`` is reused.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys

from scripts.probe_w2_fullgame_texture_colors import (
    sha256_file,
    validate_owner_names,
    verify_and_hash,
)

SCHEMA_VERSION = 1


def aggregate_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    materials = 0
    bound_by_name = collections.Counter()
    null_by_name = collections.Counter()
    fileid_by_name = collections.defaultdict(collections.Counter)
    fileid_total = collections.Counter()

    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        saved = obj.read_typetree().get("m_SavedProperties")
        if not isinstance(saved, dict):
            raise ValueError(f"m_SavedProperties missing in {owner.name}")
        texenvs = saved.get("m_TexEnvs")
        if not isinstance(texenvs, list):
            raise ValueError(f"m_TexEnvs missing in {owner.name}")
        materials += 1
        for entry in texenvs:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                raise ValueError(f"unexpected m_TexEnvs entry shape in {owner.name}")
            name, prop = entry
            if not isinstance(name, str) or not isinstance(prop, dict):
                raise ValueError(f"unexpected m_TexEnvs entry content in {owner.name}")
            tex = prop.get("m_Texture")
            if not isinstance(tex, dict) or {"m_FileID", "m_PathID"} - set(tex):
                raise ValueError(f"m_Texture PPtr malformed in {owner.name}")
            fileid = tex["m_FileID"]
            pathid = tex["m_PathID"]
            for value in (fileid, pathid):
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"negative/non-int PPtr component in {owner.name}: {value!r}")
            is_bound = fileid != 0 or pathid != 0
            if is_bound:
                bound_by_name[name] += 1
                fileid_by_name[name][fileid] += 1
                fileid_total[fileid] += 1
            else:
                null_by_name[name] += 1

    return {
        "material_count": materials,
        "bound_by_slot": dict(sorted(bound_by_name.items())),
        "null_by_slot": dict(sorted(null_by_name.items())),
        "fileid_by_bound_slot": {name: dict(sorted(c.items())) for name, c in sorted(fileid_by_name.items())},
        "fileid_total": dict(sorted(fileid_total.items())),
    }


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    owners = {}
    manifest = {}
    for owner in owner_paths:
        if repo is not None:
            info = verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        else:
            info = {
                "sha256": sha256_file(owner),
                "byte_count": owner.stat().st_size,
                "registered_sha256": None,
                "identity_kind": "unverified-local",
            }
        manifest[owner.name] = info
        owners[owner.name] = aggregate_owner(owner)
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owner_manifest": manifest,
        "owners": owners,
    }
    blob = json.dumps(result)
    for forbidden in ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords", "stringTagMap", "m_FileID"):
        if forbidden in blob:
            raise ValueError(f"forbidden output field leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--owner", action="append", required=True, help="serialized owner file (repeatable)")
    parser.add_argument("--repo", help="optional repo worktree for identity cross-check")
    parser.add_argument(
        "--repo-rel-prefix",
        default="Raft/Raft_Data",
        help="repo-relative directory prefix of the owners (default Raft/Raft_Data)",
    )
    parser.add_argument("--out", required=True, help="aggregate JSON path")
    args = parser.parse_args(argv)
    source = Path(args.source)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    owners = []
    for name in validate_owner_names(args.owner):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "no_proprietary_payload": True, "owners": len(result["owners"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
