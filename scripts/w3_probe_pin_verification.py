#!/usr/bin/env python3
"""W3 — LFS pin verification probe (second-environment byte-identity evidence).

Verifies two committed byte pins against the repo's LFS-checked-out files:

  Raft/Raft_Data/resources.assets   -> 87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c (111,533,516 B)
  Raft/Raft_Data/sharedassets0.assets -> 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3 (115,978,112 B)

These are the exact pins carried by every committed W3 artifact since the
full-game inventory, which authenticated all local probes. A mismatch aborts
(exit 1) rather than emitting a degraded aggregate - fail-closed, always.

Publication: a small JSON with booleans/sizes/hashes only. No names beyond the
repo file paths (already public in the tree), no decompiled content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

PINNED = {
    "Raft/Raft_Data/resources.assets": (
        111_533_516,
        "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c",
    ),
    "Raft/Raft_Data/sharedassets0.assets": (
        115_978_112,
        "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3",
    ),
}


def sha256_file(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return size, h.hexdigest()


def run(repo_root: str) -> dict:
    root = Path(repo_root)
    results: dict[str, dict] = {}
    for rel, (exp_size, exp_sha) in sorted(PINNED.items()):
        p = root / rel
        if not p.is_file():
            raise SystemExit(f"pinned owner missing after LFS pull: {rel}")
        size, digest = sha256_file(p)
        sizes_ok = size == exp_size
        sha_ok = digest == exp_sha
        results[rel] = {
            "expected_bytes": exp_size,
            "observed_bytes": size,
            "bytes_match": sizes_ok,
            "expected_sha256": exp_sha,
            "observed_sha256": digest,
            "sha_match": sha_ok,
        }
        if not (sizes_ok and sha_ok):
            raise SystemExit(f"pin verification FAILED for {rel}")
    return {
        "probe": "w3-lfs-pin-verification",
        "schema_version": 1,
        "verification": results,
        "all_pins_verified": True,
        "tool_versions": {"python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    report = run(args.repo_root)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
