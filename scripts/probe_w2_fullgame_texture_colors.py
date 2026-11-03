"""Aggregates per-Texture2D color-space/label data for all serialized owners of the original build and extends the two pinged-owner lanes to the full game.

Scope: every serialized owner under ``Raft/Raft_Data`` given explicitly on the command line (``*.assets`` + extension-less original scene owners; ``*.resS`` stream companions and FMOD ``.bank`` files carry no typetrees and are skipped). Per owner, only integer/table aggregates are emitted: texture count, ``m_ColorSpace`` split, distinct-format count, and dominant ``(format, colorspace)`` pairs.

Identity handling (fail-closed):
- Every owner is hashed (SHA256) before parsing; per-owner digest+size go into the manifest section.
- With ``--repo <path>``, each owner's registered Git identity is cross-checked: LFS-tracked files against the parsed pointer OIDs in the repo worktree, regular tracked files against the git blob SHA-256 (SHA-1) computed from the repo objects. A mismatch, or a missing pointer registration, is a hard failure with no statistical innovation.
- Always aggregate-only: no material/object names, no path IDs, no keyword strings, and no image bytes pass into the output.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA_VERSION = 1

VALID_TEXTURE_COLOR_SPACES = {0: "Gamma", 1: "Linear"}

CHUNK = 1024 * 1024 * 4

POINTER_RE = re.compile(r"oid sha256:([0-9a-f]{64})")

LFS_MAGIC = b"version https://git-lfs"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            piece = fh.read(CHUNK)
            if not piece:
                break
            digest.update(piece)
    return digest.hexdigest()


def expected_git_identity(repo: Path, repo_rel: str) -> str | None:
    """Return the owner's registered sha256 identity (LFS pointer oid) if
    tracked; ``None`` if untracked."""
    blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{repo_rel}"],
        capture_output=True,
        check=True,
    ).stdout
    text = blob.decode("ascii", errors="strict")
    match = POINTER_RE.search(text)
    if match is None:
        match = re.search(r"^oid sha256:([0-9a-f]{64})\s", text)
    if match:
        return match.group(1)
    raise ValueError(f"tracked object has neither LFS pointer nor raw SHA identity: {repo_rel}")


def verify_and_hash(owner: Path, repo: Path, repo_rel: str) -> dict:
    digest = sha256_file(owner)
    size = owner.stat().st_size
    registered_path = repo / repo_rel
    registered_bytes = registered_path.read_bytes()
    info = {
        "sha256": digest,
        "byte_count": size,
        "registered_sha256": None,
        "identity_kind": None,
    }
    if registered_bytes.startswith(LFS_MAGIC):
        registered_text = registered_bytes.decode("ascii")
        match = POINTER_RE.search(registered_text)
        if match is None:
            raise ValueError(f"malformed LFS pointer for owner: {repo_rel}")
        info["identity_kind"] = "lfs-pointer-oid"
        info["registered_sha256"] = match.group(1)
    else:
        # regular tracked file: compare against the git-registered blob content
        blob_bytes = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{repo_rel}"],
            capture_output=True,
            check=True,
        ).stdout
        info["identity_kind"] = "tracked-regular-blob"
        info["registered_sha256"] = hashlib.sha256(blob_bytes).hexdigest()
    if info["registered_sha256"] != digest:
        raise ValueError(
            f"owner identity mismatch against registered object: {repo_rel} "
            f"local={digest} registered={info['registered_sha256']}"
        )
    return info


def aggregate_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    textures = 0
    split = collections.Counter()
    pairs = collections.Counter()
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        tree = obj.read_typetree()
        space = tree.get("m_ColorSpace")
        if space not in VALID_TEXTURE_COLOR_SPACES:
            raise ValueError(f"m_ColorSpace outside engine enum in {owner.name}: {space!r}")
        fmt = tree.get("m_TextureFormat")
        if not isinstance(fmt, int):
            raise ValueError(f"m_TextureFormat non-int in {owner.name}: {fmt!r}")
        textures += 1
        split[int(space)] += 1
        pairs[(int(fmt), int(space))] += 1
    return {
        "texture_count": textures,
        "colorspace_split": {VALID_TEXTURE_COLOR_SPACES[key]: val for key, val in sorted(split.items())},
        "distinct_formats": len({fmt for fmt, _ in pairs}),
        "top_pairs": [
            {"format": fmt, "colorspace": VALID_TEXTURE_COLOR_SPACES[space], "count": count}
            for (fmt, space), count in pairs.most_common(4)
        ],
    }


def validate_owner_names(owner_names) -> list[str]:
    clean = []
    for name in owner_names:
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError(f"unsafe owner name: {name}")
        clean.append(name)
    return clean


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    owners = {}
    manifest = {}
    for owner in owner_paths:
        if repo is not None:
            repo_rel = f"{repo_rel_prefix}/{owner.name}"
            info = verify_and_hash(owner, repo, repo_rel)
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
    for forbidden in ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords"):
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
    validate_owner_names(args.owner)
    owners = []
    for name in validate_owner_names(args.owner):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    repo_rel_prefix = args.repo_rel_prefix.strip("/")
    result = probe(owners, repo, repo_rel_prefix)
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "no_proprietary_payload": True, "owners": len(result["owners"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
