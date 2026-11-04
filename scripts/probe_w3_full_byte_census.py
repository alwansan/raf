#!/usr/bin/env python3
"""W3 — full byte census across the identity triangle for all 82 owners.

Phase A (fast, fail-closed, no network): feature<->local identity.
  For each of the 82 game-data owners:
    - LFS-backed owners: the committed pointer's ``oid sha256:<hex>`` must equal
      the local file's SHA-256, and the pointer's ``size`` must equal the local
      file size.
    - Direct-blob owners: ``git hash-object`` of the local file must equal the
      committed blob SHA-1 at HEAD, and sizes must match.

Phase B (heavy, streaming, resumable per owner, fail-closed): zip2<->local.
  Stream the zip2 blobs (direct or split parts in order, fresh-hasher restart
  per owner on any transport error) and compare SHA-256 against the local file.
  Completed owners are recorded in a progress file and skipped on re-runs.

Publication: aggregate JSON only - counts, booleans, owner rows keyed by public
repo file paths (which the tree already publishes). No shader/asset names, no
decompiled content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ASSETS_RE = re.compile(r"^(resources|globalgamemanagers|sharedassets\d+)\.assets$")
LEVEL_RE = re.compile(r"^level\d+$")
DATA_DIR = "Raft/Raft_Data"
PINNED_LOCAL = {
    "resources.assets": ("Raft/Raft_Data/resources.assets",
                         111_533_516,
                         "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": ("Raft/Raft_Data/sharedassets0.assets",
                             115_978_112,
                             "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}


def sha256_file(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
            size += len(chunk)
    return size, h.hexdigest()


def list_owners(repo_root: Path) -> dict[str, str]:
    """owner name -> kind ('lfs' | 'direct') from the committed feature HEAD."""
    out: dict[str, str] = {}
    tracked = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", DATA_DIR],
        cwd=repo_root, capture_output=True, text=True, check=True).stdout.splitlines()
    names = [p.split("/")[-1] for p in tracked
             if ASSETS_RE.match(p.split("/")[-1]) or LEVEL_RE.match(p.split("/")[-1])]
    if len(names) != 82:
        raise SystemExit(f"expected 82 owners at HEAD, got {len(names)}")
    for n in sorted(set(names)):
        blob = subprocess.run(["git", "cat-file", "blob", f"HEAD:{DATA_DIR}/{n}"],
                              cwd=repo_root, capture_output=True, check=True).stdout[:256]
        head = blob.decode("utf-8", errors="replace")
        out[n] = "lfs" if head.startswith("version https://git-lfs") else "direct"
    return out


def phase_a(repo_root: Path, local_root: Path, owners: dict[str, str]) -> tuple[dict, list[str]]:
    rows: dict[str, dict] = {}
    mismatches: list[str] = []
    for name, kind in owners.items():
        local = local_root / name
        if kind == "lfs":
            ptr = subprocess.run(["git", "cat-file", "blob", f"HEAD:{DATA_DIR}/{name}"],
                                 cwd=repo_root, capture_output=True, text=True,
                                 check=True).stdout
            oid = re.search(r"^oid sha256:([0-9a-f]{64})$", ptr, re.M).group(1)
            size = int(re.search(r"^size (\d+)$", ptr, re.M).group(1))
            lsize, lsha = sha256_file(local)
            ok = (oid == lsha) and (size == lsize)
        else:
            blob_sha = subprocess.run(
                ["git", "rev-parse", f"HEAD:{DATA_DIR}/{name}"],
                cwd=repo_root, capture_output=True, text=True, check=True).stdout.strip()
            local_sha = subprocess.run(
                ["git", "hash-object", str(local)],
                capture_output=True, text=True, check=True).stdout.strip()
            lsize = local.stat().st_size
            fsize = int(subprocess.run(["git", "cat-file", "-s", f"HEAD:{DATA_DIR}/{name}"],
                                       cwd=repo_root, capture_output=True, text=True,
                                       check=True).stdout)
            ok = (blob_sha == local_sha) and (fsize == lsize)
            oid = blob_sha
        rows[name] = {"feature_kind": kind, "feature_sha_or_oid": oid,
                      "local_bytes": lsize, "feature_local_match": ok}
        if not ok:
            mismatches.append(name)
    if mismatches:
        raise SystemExit(f"phase A fail-closed mismatches: {mismatches}")
    return rows, mismatches


class OwnerRestart(Exception):
    def __init__(self, name: str, attempt: int, cause: Exception):
        super().__init__(f"{name} restart {attempt}: {cause}")
        self.name = name


def stream_zip2_sha(name: str, kind: str, token: str) -> tuple[int, str]:
    h = hashlib.sha256()
    total = 0
    if kind == "blob":
        urls = [f"https://raw.githubusercontent.com/alwansan/raf/zip2/{DATA_DIR}/{name}"]
    else:
        tree_e = gh_json(
            "https://api.github.com/repos/alwansan/raf/git/trees/zip2%3A"
            + DATA_DIR.replace("/", "%2F") + "%2F" + name, token)
        blobs = [i for i in tree_e["tree"]
                 if i["type"] == "blob" and not i["path"].endswith("README.txt")]
        urls = [f"https://raw.githubusercontent.com/alwansan/raf/zip2/"
                f"{DATA_DIR}/{name}/{p}"
                for p in sorted(i["path"] for i in blobs)]
    for url in urls:
        chunk_err = None
        for attempt in range(1, 3):
            try:
                req = urllib.request.Request(
                    url, headers={"Authorization": f"token {token}"})
                got = 0
                with urllib.request.urlopen(req, timeout=180) as r:
                    while True:
                        chunk = r.read(1 << 22)
                        if not chunk:
                            break
                        h.update(chunk)
                        got += len(chunk)
                total += got
                chunk_err = None
                break
            except Exception as e:
                chunk_err = e
                time.sleep(5)
        if chunk_err is not None:
            raise OwnerRestart(name, attempt, chunk_err)
    return total, h.hexdigest()


def gh_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def zip2_storage_kinds(token: str) -> dict[str, str]:
    tree_e = gh_json(
        f"https://api.github.com/repos/alwansan/raf/git/trees/"
        f"zip2%3A" + DATA_DIR.replace("/", "%2F"), token)
    out: dict[str, str] = {}
    for e in tree_e["tree"]:
        n = e["path"]
        if ASSETS_RE.match(n) or LEVEL_RE.match(n):
            out[n] = "tree" if e["type"] == "tree" else "blob"
    if len(out) != 82:
        raise SystemExit(f"zip2 owner count {len(out)} != 82")
    return out


def run(args: argparse.Namespace) -> dict:
    token = os.environ.get(args.token_env, "")
    if not token:
        raise SystemExit("missing GitHub token env")
    repo_root = Path(args.repo_root)
    local_root = Path(args.local_root)
    progress_path = Path(args.progress or "/tmp/opencode/w3out/byte_census_progress.json")

    owners = list_owners(repo_root)
    if args.phase == "a":
        rows, mismatches = phase_a(repo_root, local_root, owners)
        return {"phase": "a", "rows": rows, "mismatches": mismatches}

    kinds = zip2_storage_kinds(token)
    progress: dict = {}
    if progress_path.exists():
        progress = json.load(open(progress_path, encoding="utf-8"))
    done: dict[str, dict] = progress.get("zip2_local", {})
    skips = 0
    for name in sorted(owners):
        if name in done and done[name].get("verified"):
            skips += 1
            continue
        local = local_root / name
        lsize, lsha = sha256_file(local)
        for attempt in range(1, args.max_owner_restarts + 2):
            try:
                zsize, zsha = stream_zip2_sha(name, kinds.get(name, "blob"), token)
                break
            except OwnerRestart as e:
                print(f"restart {name}: {e}", file=sys.stderr)
                time.sleep(10)
        else:
            raise SystemExit(f"{name}: exhausted owner restarts")
        done[name] = {"verified": (zsha == lsha) and (zsize == lsize),
                      "local_bytes": lsize, "zip2_bytes": zsize,
                      "zip2_sha256": zsha, "zip2_kind": kinds.get(name)}
        progress["zip2_local"] = done
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(progress, f)
    failures = [k for k, v in progress["zip2_local"].items() if not v.get("verified")]
    if failures:
        raise SystemExit(f"zip2<->local byte failures (fail-closed): {failures}")
    return {"phase": "b", "count_completed": len(done),
            "skipped_on_resume": skips, "all_verified": True}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--local-root", required=True)
    ap.add_argument("--token-env", default="GH_TOKEN")
    ap.add_argument("--progress", default=None)
    ap.add_argument("--phase", choices=["a", "b"], required=True)
    ap.add_argument("--max-owner-restarts", type=int, default=2)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    report = run(args)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in report if k != "rows"},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
