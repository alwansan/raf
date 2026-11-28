#!/usr/bin/env python3
"""Read-only admission audit for an explicitly pinned local APK set.

Does not download, extract, install, execute, upload, or re-sign an input.
Expected hashes, package, signer and complete split list must come from
a separately trusted release record. Passing is not proof of launchability.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

ABI = {"arm64-v8a": (2, 183), "armeabi-v7a": (1, 40),
       "x86": (1, 3), "x86_64": (2, 62)}
SHA = re.compile(r"^[0-9a-f]{64}$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=90)
    require(result.returncode == 0, f"{pathlib.Path(args[0]).name} failed: {result.stderr.strip()}")
    return result.stdout


def audit(manifest_path, bt):
    manifest = json.loads(manifest_path.read_text())
    expected_package = manifest["package"]
    expected_version = str(manifest["version_code"])
    expected_signers = sorted(set(manifest["signer_sha256"]))
    expected_abi = manifest["abi"]
    require(expected_signers and all(SHA.fullmatch(x) for x in expected_signers),
            "Invalid expected certificate digest")
    require(expected_abi in ABI, "Unsupported target ABI")
    require(isinstance(manifest["files"], list) and manifest["files"], "Empty APK set")
    splits, files, reports, abis = set(), set(), [], set()
    for entry in manifest["files"]:
        path = (manifest_path.parent / entry["path"]).resolve()
        require(path.is_file() and path.suffix.lower() == ".apk", "Input must be a local APK")
        require(path not in files, "Duplicate APK path")
        files.add(path)
        expected_hash = entry["sha256"]
        require(SHA.fullmatch(expected_hash), "Missing or invalid pinned APK digest")
        actual_hash = digest(path)
        require(actual_hash == expected_hash, "APK digest mismatch")
        signature = run(str(bt / "apksigner"), "verify", "--verbose", "--print-certs", str(path))
        certs = sorted(set(re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-f]{64})\s*$",
                                     signature, re.M)))
        require(certs == expected_signers, "APK signer mismatch")
        badging = run(str(bt / "aapt2"), "dump", "badging", str(path))
        package_line = next((x for x in badging.splitlines() if x.startswith("package: ")), "")
        attrs = dict(re.findall(r"(\w+)='([^']*)'", package_line))
        require(attrs.get("name") == expected_package, "Package identifier mismatch")
        require(attrs.get("versionCode") == expected_version, "Version code mismatch")
        xml = run(str(bt / "aapt2"), "dump", "xmltree", "--file", "AndroidManifest.xml", str(path))
        split_match = re.search(r'^\s*A: split="([^"]*)"', xml, re.M)
        actual_split = attrs.get("split") or (split_match.group(1) if split_match else None)
        require(actual_split == entry["split"], "Split identity mismatch")
        require(actual_split not in splits, "Duplicate base or split identity")
        splits.add(actual_split)
        native = []
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), "Duplicate ZIP entries")
            require("AndroidManifest.xml" in names, "Missing manifest")
            for name in names:
                parts = name.split("/")
                require(not name.startswith("/") and "\\" not in name and ".." not in parts,
                        "Unsafe ZIP entry")
                if not name.startswith("lib/") or not name.endswith(".so"):
                    continue
                require(len(parts) == 3 and parts[1] in ABI, "Unexpected native library ABI/path")
                with archive.open(name) as stream:
                    header = stream.read(20)
                require(len(header) == 20 and header[:4] == b"\x7fELF" and header[5] == 1,
                        "Native library is not a little-endian ELF")
                observed = (header[4], int.from_bytes(header[18:20], "little"))
                require(observed == ABI[parts[1]], "Native library ELF machine disagrees with ABI")
                abis.add(parts[1])
                native.append({"entry": name, "elf_class": observed[0], "machine": observed[1]})
        reports.append({"name": path.name, "sha256": actual_hash, "split": actual_split,
                        "signer_sha256": certs, "native": native})
    require(None in splits, "Missing base APK")
    require(not abis or expected_abi in abis, "Requested ABI unavailable in supplied set")
    require(not manifest.get("require_native", False) or expected_abi in abis,
            "Requested native ABI was not demonstrated")
    return {"result": "passed", "package": expected_package, "version_code": expected_version,
            "requested_abi": expected_abi, "observed_abis": sorted(abis),
            "files": reports, "scope": "pinned_set_admission_not_install_or_launch"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--build-tools", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.manifest.resolve(), args.build_tools.resolve()), indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        print(f"APK_SET_REJECTED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
