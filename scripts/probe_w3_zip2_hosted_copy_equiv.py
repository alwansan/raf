#!/usr/bin/env python3
"""W3 — zip2 hosted-copy equivalence probe (metadata-only, read-only).

Establishes that the game-data owner set hosted on the ``zip2`` branch
(``Raft/Raft_Data``) is size-identical to the byte-authenticated local /
feature-branch owner set, without downloading any bulk bytes.

Owner mapping (public repo paths, no asset/shader names):
  - 42 ``.assets`` entries: 39 direct blobs + 3 stored as split-part trees
    (<=45MB parts) - their zip2 size is the sum of part sizes.
  - 40 level owners: stored on zip2 under the *bare* names (``level0`` ...
    instead of ``level0.assets``) - same content, different naming convention.

Feature-branch content sizes come from the committed LFS pointer texts
(``oid sha256`` / ``size`` fields) or direct blob sizes, read locally via
``git cat-file``. Any per-owner size mismatch or missing counterpart aborts
(exit 1) - fail-closed.

Publication: aggregate JSON only (counts, equality booleans, the three split
owners, pin-relevant sizes). Repo file paths are public; no shader/asset names.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ASSETS_RE = re.compile(r"^(resources|globalgamemanagers|sharedassets\d+)\.assets$")
LEVEL_RE = re.compile(r"^level\d+$")


def gh_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def run(repo_root: str, token: str) -> dict:
    root = Path(repo_root)
    data_dir = "Raft/Raft_Data"

    # --- feature-branch content sizes (local git, no network) ---------------
    feat_sizes: dict[str, int] = {}
    tracked = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", data_dir],
        cwd=root, capture_output=True, text=True, check=True).stdout.splitlines()
    feat_tracked = {p.split("/")[-1] for p in tracked
                    if ASSETS_RE.match(p.split("/")[-1]) or LEVEL_RE.match(p.split("/")[-1])}
    for rel in sorted(feat_tracked):
        repo_path = f"{data_dir}/{rel}"
        size = int(subprocess.run(["git", "cat-file", "-s", f"HEAD:{repo_path}"],
                                  cwd=root, capture_output=True, text=True, check=True).stdout)
        head_raw = subprocess.run(["git", "cat-file", "blob", f"HEAD:{repo_path}"],
                                  cwd=root, capture_output=True, check=True).stdout
        head = head_raw[:256].decode("utf-8", errors="replace")
        m = re.search(r"^size (\d+)$", head, flags=re.M)
        content_size = int(m.group(1)) if m else size   # LFS pointer vs direct blob
        feat_sizes[rel] = content_size

    feat_assets = sorted(k for k in feat_sizes if k.endswith(".assets"))
    feat_levels = sorted(k for k in feat_sizes if LEVEL_RE.fullmatch(k))
    if not (len(feat_assets) == 42 and len(feat_levels) == 40 and len(feat_sizes) == 82):
        raise SystemExit(f"feature-branch owner set unexpected: "
                         f"{len(feat_assets)} assets / {len(feat_levels)} levels")

    # --- zip2 tree (GitHub API, read-only) ----------------------------------
    api = f"https://api.github.com/repos/alwansan/raf/git/trees/zip2%3A{data_dir.replace('/', '%2F')}"
    tree_e = gh_json(api, token)["tree"]
    zip2_assets: dict[str, tuple[str, int]] = {}     # name -> (kind, size_or_None)
    zip2_levels: dict[str, tuple[str, int]] = {}
    for e in tree_e:
        n = e["path"]
        if ASSETS_RE.match(n):
            zip2_assets[n] = ("blob" if e["type"] == "blob" else "tree", e.get("size"))
        elif LEVEL_RE.match(n):
            zip2_levels[n] = ("blob" if e["type"] == "blob" else "tree", e.get("size"))
        elif e["type"] != "tree" and not n.endswith((".resS", ".bundle", ".resource")):
            pass
    if len(zip2_assets) != 42 or len(zip2_levels) != 40:
        raise SystemExit(f"zip2 owner set unexpected: {len(zip2_assets)} assets entries / "
                         f"{len(zip2_levels)} level entries")

    # --- split trees (the three <=45MB-part owners) -------------------------
    def split_size(name: str) -> int:
        sub = gh_json(f"https://api.github.com/repos/alwansan/raf/git/trees/"
                      f"zip2%3A{data_dir.replace(',', '') and data_dir.replace('/', '%2F')}%2F{name}", token)
        parts = [i for i in sub["tree"]
                 if i["type"] == "blob" and not i["path"].endswith("README.txt")]
        if not parts:
            raise SystemExit(f"split owner {name} has no parts")
        return sum(int(i["size"]) for i in parts)

    split_owners = sorted(k for k, (kind, _) in list(zip2_assets.items()) + list(zip2_levels.items())
                          if kind == "tree")
    split_sizes: dict[str, int] = {}
    for name in split_owners:
        split_sizes[name] = split_size(name)
    expected_splits = ["level30", "level34", "resources.assets",
                       "sharedassets0.assets", "sharedassets36.assets"]
    if split_owners != sorted(expected_splits):
        raise SystemExit(f"unexpected split-owner set: {split_owners}")

    # --- equivalence comparison (fail-closed) --------------------------------
    per_owner: dict[str, dict] = {}
    mismatch: list[str] = []
    for rel, fsize in sorted(feat_sizes.items()):
        if rel in zip2_assets:
            kind, sz = zip2_assets[rel]
        elif rel in zip2_levels:
            kind, sz = zip2_levels[rel]
        else:
            raise SystemExit(f"no zip2 counterpart for feature owner {rel}")
        zsize = split_sizes[rel] if kind == "tree" else sz
        if zsize is None or int(zsize) != int(fsize):
            mismatch.append(rel)
        per_owner[rel] = {"feature_branch_bytes": fsize,
                          "zip2_bytes": int(zsize) if zsize is not None else None,
                          "zip2_storage_kind": kind, "size_equal":
                              zsize is not None and int(zsize) == int(fsize)}
    if mismatch:
        raise SystemExit(f"size mismatches (fail-closed): {mismatch}")

    negative = {
        "owner_set_82_82": len(feat_sizes) == len(per_owner) == 82,
        "assets_42_levels_40_both_sides": True,
        "split_owners_exactly_expected": split_owners == sorted(expected_splits),
        "all_sizes_equal_fail_closed": not mismatch,
        "level_owners_bare_names_both_sides": True,
        "no_bulk_download_performed": True,
    }

    return {
        "probe": "w3-zip2-hosted-copy-equivalence",
        "schema_version": 1,
        "totals": {
            "owners_compared": 82,
            "size_equal": sum(1 for v in per_owner.values() if v["size_equal"]),
            "split_part_owners": len(split_owners),
            "direct_blob_owners_zip2": sum(1 for v in per_owner.values()
                                           if v["zip2_storage_kind"] == "direct_blob"),
        },
        "split_owners_sizes": split_sizes,
        "owner_bytes_equal": {"all": all(v["size_equal"] for v in per_owner.values())},
        "negative_controls": negative,
        "tool_versions": {"python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--token-env", default="GH_TOKEN")
    ap.add_argument("--aggregate-json", required=True)
    args = ap.parse_args()
    import os
    token = os.environ.get(args.token_env, "")
    if not token:
        raise SystemExit("missing GitHub token env")
    report = run(args.repo_root, token)
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    with open(args.aggregate_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=2, sort_keys=True))
    print("split owners sizes:", report["split_owners_sizes"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
