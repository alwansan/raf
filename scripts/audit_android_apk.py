#!/usr/bin/env python3
"""Audit structure of a privately generated Unity IL2CPP Android APK.

Metadata-only ZIP audit: no game assets extracted, printed, uploaded or published.
The check DOES NOT prove that the APK starts, passes signature verification, or
has working rendering, physics, sound, input or persistence on the real phone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def audit(apk: Path, *, min_size: int = 25_000_000, digest: bool = True) -> dict:
    if not apk.is_file():
        raise FileNotFoundError(f"APK not found: {apk}")
    if apk.stat().st_size < min_size:
        raise ValueError("APK is suspiciously small; check genuine game build output")
    with zipfile.ZipFile(apk) as archive:
        members = archive.infolist()
        if not members:
            raise ValueError("APK ZIP archive is empty")
        names = set()
        for item in members:
            name = item.filename
            path = PurePosixPath(name)
            if (not name or name.startswith("/") or "\\" in name or ":" in name or
                    ".." in path.parts or path.is_absolute()):
                raise ValueError("Unsafe APK ZIP member path")
            if name in names:
                raise ValueError("Duplicate APK ZIP member")
            names.add(name)
        required = {"AndroidManifest.xml", "classes.dex",
                    "lib/arm64-v8a/libil2cpp.so", "lib/arm64-v8a/libunity.so"}
        missing = required - names
        if missing:
            raise ValueError("APK is missing essential Android/IL2CPP members: " +
                             ", ".join(sorted(missing)))
        data = [info for info in members
                if info.filename.startswith("assets/bin/Data/") and not info.is_dir() and info.file_size]
        if not data:
            raise ValueError("APK contains no populated Unity game Data files")
        for key in required:
            if archive.getinfo(key).file_size == 0:
                raise ValueError("Required APK ZIP member is empty: " + key)
            with archive.open(key) as stream:
                magic = stream.read(8)
                if not magic:
                    raise ValueError("Cannot read an essential APK member")
                if key == "classes.dex" and not magic.startswith(b"dex\n"):
                    raise ValueError("classes.dex does not have a DEX header")
                if key.endswith(".so") and not magic.startswith(b"\x7fELF"):
                    raise ValueError("Android ARM64 shared library has no ELF header")
        abi = sorted({item.filename.split("/")[1] for item in members
                      if item.filename.startswith("lib/") and
                      len(item.filename.split("/")) > 2})
        report = {
            "apk_bytes": apk.stat().st_size,
            "zip_members": len(members),
            "total_uncompressed_bytes": sum(x.file_size for x in members),
            "unity_data_files": len(data),
            "unity_data_uncompressed_bytes": sum(x.file_size for x in data),
            "abis": abi,
            "arm64_il2cpp": True,
            "fmod_native_library_present": any(
                x.filename.startswith("lib/arm64-v8a/") and
                "fmod" in x.filename.lower() and x.filename.endswith(".so")
                for x in members),
            "limitations": "ZIP structure only; signature, startup, original game fidelity, audio, physics and on-device tests remain unverified.",
        }
    if digest:
        h = hashlib.sha256()
        with apk.open("rb") as src:
            for block in iter(lambda: src.read(1024 * 1024), b""):
                h.update(block)
        report["apk_sha256"] = h.hexdigest()
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.apk)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print("RAFT_ANDROID_APK_STRUCTURE " + json.dumps(result, sort_keys=True))
