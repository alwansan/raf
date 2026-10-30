#!/usr/bin/env python3
"""Read-only Raft/Unity build inventory. Never executes game binaries or fetches LFS."""
from __future__ import annotations
import argparse
import collections
import json
import os
from pathlib import Path
import re
import shutil
import sys

UNITY_VERSION = re.compile(rb"(?<![0-9])(?:20(?:1[7-9]|2[0-9])|6000)\.[0-9]{1,2}\.[0-9]{1,2}[abfpc][0-9]{1,5}(?![0-9])")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
LFS_SIZE = re.compile(rb"^size ([0-9]+)$", re.MULTILINE)
WINDOWS_ONLY = ("steam_api64.dll", "UnityPlayer.dll", "OnlineFix64.dll",
                "PartyWin32.dll", "PartyXboxLiveWin32.dll", "fmodstudio.dll",
                "winmm.dll", "SteamOverlay64.dll", "StubDRM64.dll")


def inspect(root: Path) -> dict:
    if not root.is_dir():
        raise FileNotFoundError("Expected a 'Raft' game directory")
    usage = shutil.disk_usage(root)
    groups = collections.defaultdict(lambda: {"count": 0, "bytes": 0})
    all_files = []
    pointers = []
    suspect = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        suffix = path.suffix.lower() if path.suffix else "<none>"
        groups[suffix]["count"] += 1
        groups[suffix]["bytes"] += size
        all_files.append({"path": relative, "bytes_in_git_checkout": size})
        if path.name.lower() in {s.lower() for s in WINDOWS_ONLY}:
            suspect.append(relative)
        if size <= 512:
            with path.open("rb") as fh:
                data = fh.read(512)
            if data.startswith(LFS_HEADER):
                match = LFS_SIZE.search(data)
                pointers.append({"path": relative,
                                 "original_bytes": int(match.group(1)) if match else None})
    candidate = root / "Raft_Data" / "globalgamemanagers"
    unity_versions = []
    if candidate.is_file():
        with candidate.open("rb") as fh:
            chunk = fh.read(4 * 1024 * 1024)
        unity_versions = sorted({x.decode("ascii") for x in UNITY_VERSION.findall(chunk)})
    checks = {
        "mono_managed_assembly": (root / "Raft_Data/Managed/Assembly-CSharp.dll").is_file(),
        "globalgamemanagers": candidate.is_file(),
        "boot_config": (root / "Raft_Data/boot.config").is_file(),
        "project_assets_directory": (root.parent / "Assets").is_dir(),
        "project_settings_directory": (root.parent / "ProjectSettings").is_dir(),
    }
    return {
        "note": "Manifest only; game executables and DLLs were NOT executed. LFS was NOT downloaded.",
        "unity_versions_candidated_from_globalgamemanagers": unity_versions,
        "checks": checks,
        "file_count": len(all_files),
        "git_checkout_bytes": sum(f["bytes_in_git_checkout"] for f in all_files),
        "lfs_pointer_count": len(pointers),
        "lfs_original_bytes_claimed": sum(p["original_bytes"] or 0 for p in pointers),
        "lfs_pointers": pointers,
        "file_types": dict(sorted(groups.items())),
        "windows_only_or_untrusted_binary_candidates": suspect,
        "disk_free_bytes_on_runner": usage.free,
        "largest_nonpointer_files": sorted(
            [f for f in all_files if f["path"] not in {p["path"] for p in pointers}],
            key=lambda x: x["bytes_in_git_checkout"], reverse=True)[:20],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("Raft"))
    p.add_argument("--output", type=Path, default=Path("out/raft-inventory.json"))
    args = p.parse_args()
    report = inspect(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Raft build inventory (safe read-only)")
    print("files:", report["file_count"])
    print("Unity version candidates:", report["unity_versions_candidated_from_globalgamemanagers"])
    print("LFS pointers:", report["lfs_pointer_count"])
    print("LFS bytes:", report["lfs_original_bytes_claimed"])
    print("Runner free bytes:", report["disk_free_bytes_on_runner"])
    print("Unity project checks:", report["checks"])
    print("JSON manifest:", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
