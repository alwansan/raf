"""Authenticate only pinned ZIP2 original local-world/save inputs (no Git LFS).

Read-only, bounded verification. This does not execute original game binaries,
decode a user save, change .rgd content, or prove Unity/Android behavior.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

ZIP2_COMMIT = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
ORIGINALS = {
    "Raft_Data/Managed/Assembly-CSharp.dll": (
        3_211_776,
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e",
    ),
    "Raft_Data/StreamingAssets/Data.rgd": (
        2_941,
        "b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba",
    ),
}
HEADER = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
READ_SIZE = 1024 * 1024
MAX_MANIFEST = 1024 * 1024


def _regular_under(path: Path, root: Path) -> bool:
    """Reject symlinks at the file or any checkout path component."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    cursor = path
    while True:
        if cursor.is_symlink():
            return False
        if cursor == root:
            break
        cursor = cursor.parent
    return path.is_file()


def verify(zip2_root: Path, *, pins=None) -> dict:
    """Return original sizes and digests, never original bytes or decoded text.

    pins is an independent test-only override; the CLI always uses ORIGINALS.
    """
    root = Path(zip2_root)
    pins = ORIGINALS if pins is None else pins
    if not root.is_dir() or root.is_symlink() or not (root / "Raft").is_dir():
        raise ValueError("Missing or unsafe ZIP2 checkout")
    if (root / "Raft").is_symlink():
        raise ValueError("Unsafe ZIP2 Raft root")
    if not isinstance(pins, dict) or not pins:
        raise ValueError("Missing independently pinned originals")
    for relative, pin in pins.items():
        if (not isinstance(relative, str) or
                not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", relative) or
                not isinstance(pin, tuple) or len(pin) != 2 or
                type(pin[0]) is not int or not 0 < pin[0] <= 16 * 1024 * 1024 or
                not isinstance(pin[1], str) or
                not re.fullmatch(r"[0-9a-f]{64}", pin[1])):
            raise ValueError("Invalid independent ZIP2 pin")
    manifest = root / "RAFT_FILE_MANIFEST.tsv"
    if not _regular_under(manifest, root) or manifest.stat().st_size > MAX_MANIFEST:
        raise ValueError("Missing or unsafe ZIP2 manifest")
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    if not rows or rows[0] != HEADER or any(len(row) != len(HEADER) for row in rows[1:]):
        raise ValueError("Unexpected ZIP2 manifest schema")
    selected = {}
    for row in rows[1:]:
        relative = row[4]
        if relative in pins:
            if relative in selected:
                raise ValueError("Duplicate pinned original in ZIP2 manifest")
            selected[relative] = row
    result = {}
    total = 0
    for relative, (expected_size, expected_sha) in sorted(pins.items()):
        row = selected.get(relative)
        if (row is None or row[0] != "plain" or
                row[1] != str(expected_size) or row[2] != expected_sha):
            raise ValueError("ZIP2 manifest conflicts with independent original pin")
        source = root / "Raft" / relative
        if not _regular_under(source, root) or source.stat().st_size != expected_size:
            raise ValueError("Missing, linked or wrong-sized ZIP2 original file")
        digest = hashlib.sha256()
        read = 0
        with source.open("rb") as stream:
            while True:
                data = stream.read(READ_SIZE)
                if not data:
                    break
                digest.update(data)
                read += len(data)
                if read > expected_size:
                    raise ValueError("ZIP2 original exceeds pinned size")
        if read != expected_size or digest.hexdigest() != expected_sha:
            raise ValueError("ZIP2 original SHA256 does not match independent pin")
        total += read
        result[relative] = {"bytes": read, "sha256": digest.hexdigest()}
    return {
        "source_provider": "zip2_plain_git_no_lfs",
        "pinned_source_commit": ZIP2_COMMIT,
        "originals": result,
        "verified_original_count": len(result),
        "verified_total_bytes": total,
        "original_data_modified": False,
        "unity_or_android_executed": False,
        "user_save_roundtrip_verified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2-checkout", required=True, type=Path)
    args = p.parse_args()
    print("RAFT_A8_ZIP2_LOCAL_ORIGINALS " +
          json.dumps(verify(args.zip2_checkout), sort_keys=True))


if __name__ == "__main__":
    main()
