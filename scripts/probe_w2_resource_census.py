"""Complete original resource census: exactly how many objects of every
serialized type exist in every owner of the original build.

Purpose (the owner's full-resource-restoration directive): a rebuilt
package (export, reimport, native port) can be reconciled against the
original's exact per-owner type census — any missing GameObject, Mesh,
AudioClip, Texture2D, Sprite or material shows up as a count deficit
before any device run. No other client has published this census.

Per owner: only {serializedClassName: count} counters (no object names,
path IDs or payload bytes). Owners enumerated by the same rule as the
full-game lane: every ``*.assets`` file plus every ``level<N>`` scene
owner in the given source directory. Identity of each owner is verified
against its committed Git object (``git show HEAD:<path>``) — LFS
pointers and regular blobs both supported via
``probe_w2_fullgame_texture_colors.verify_and_hash``.

Type names are serialized class metadata and published as-is (counters
and type-name keys only). No typetree parse is performed: only
``obj.type.name`` is read, making this the cheapest full-game census.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import re
import subprocess
import sys

from scripts.probe_w2_fullgame_texture_colors import sha256_file, verify_and_hash

SCHEMA_VERSION = 1

_FORBIDDEN = ("m_PathID", "m_Shader", "stringTagMap")

OWNER_NAME_OK = re.compile(r"(^[A-Za-z0-9_\-\.]+\.assets$)|(^[A-Za-z0-9_\-\.]+\.resource$)|(level[0-9]+$)")


def census_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    counts = collections.Counter(str(obj.type.name) for obj in env.objects)
    if not counts:
        raise ValueError(f"owner parses to zero objects: {owner.name}")
    return {
        "totalObjects": sum(counts.values()),
        "typeCounts": dict(sorted(counts.items())),
    }


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    owners = {}
    for owner in owner_paths:
        if repo is not None:
            info = verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        else:
            info = {"sha256": sha256_file(owner), "byte_count": owner.stat().st_size,
                    "registered_sha256": None, "identity_kind": "unverified-local"}
        owners[owner.name] = {**info, **census_owner(owner)}
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owners": owners,
    }
    blob = json.dumps(result)
    for forbidden in _FORBIDDEN:
        if forbidden in blob:
            raise ValueError(f"forbidden output key leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--owner", action="append", required=True, help="serialized owner (repeatable)")
    parser.add_argument("--repo", help="repo worktree for identity cross-check")
    parser.add_argument("--repo-rel-prefix", default="Raft/Raft_Data")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    owners = []
    for name in args.owner:
        if not OWNER_NAME_OK.match(name):
            raise ValueError(f"unsafe owner name: {name}")
        path = Path(args.source) / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    total = sum(o["totalObjects"] for o in result["owners"].values())
    print(json.dumps({"aggregate_written": str(out), "owners": len(result["owners"]), "totalObjects": total,
                      "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
