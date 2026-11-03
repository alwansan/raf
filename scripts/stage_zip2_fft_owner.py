"""Reassemble the one pinned authentic FFT ComputeShader owner from ZIP2 Git chunks.

The ZIP2 source is read-only and may be a sparse/partial git checkout.
No Git LFS fallback, Unity import, source overwrite, raw shader disclosure or
full 7.79GB file restoration. Tests may pass an independent synthetic pin.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

ORIGINAL = "Raft_Data/sharedassets0.assets"
SIZE = 115_978_112
SHA256 = "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"
PART_BYTES = 45 * 1024 * 1024
READ_BYTES = 2 * 1024 * 1024
PART_PATTERN = re.compile(r"part-([0-9]{5})\Z")
HEADER = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]


def _regular(path):
    return path.is_file() and not path.is_symlink()


def stage(zip2_root, destination, *, expected_bytes=SIZE,
          expected_sha256=SHA256, max_part_bytes=PART_BYTES):
    """Return only original length/hash/part count after atomic verified publish."""
    root = Path(zip2_root)
    dest = Path(destination)
    if (not root.is_dir() or root.is_symlink()
            or not _regular(root / "RAFT_FILE_MANIFEST.tsv")
            or not (root / "Raft").is_dir()
            or (root / "Raft").is_symlink()
            or not (root / "Raft" / "Raft_Data").is_dir()
            or (root / "Raft" / "Raft_Data").is_symlink()):
        raise ValueError("Unsafe or incomplete pinned ZIP2 checkout")
    if (type(expected_bytes) is not int or expected_bytes < 1 or
            expected_bytes > 2 * 1024 * 1024 * 1024 or
            type(expected_sha256) is not str or
            not re.fullmatch(r"[a-f0-9]{64}", expected_sha256) or
            type(max_part_bytes) is not int or
            not 1 <= max_part_bytes <= PART_BYTES):
        raise ValueError("Invalid independent original source pin")
    manifest = root / "RAFT_FILE_MANIFEST.tsv"
    if manifest.stat().st_size > 1024 * 1024:
        raise ValueError("Unsafe oversized ZIP2 manifest")
    with manifest.open("r", newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != HEADER:
            raise ValueError("Unexpected ZIP2 manifest schema")
        hits = [row for row in reader
                if row.get("relative_path_under_Raft") == ORIGINAL]
    if len(hits) != 1:
        raise ValueError("Original FFT owner not uniquely declared in ZIP2 manifest")
    row = hits[0]
    if (row.get("kind") != "split" or row.get("bytes") != str(expected_bytes)
            or row.get("sha256") != expected_sha256 or row.get("mode") is None):
        raise ValueError("ZIP2 manifest conflicts with independently pinned FFT owner")
    parts_dir = root / "Raft" / "Raft_Data" / "sharedassets0.assets"
    if not parts_dir.is_dir() or parts_dir.is_symlink():
        raise ValueError("Missing or unsafe ZIP2 FFT chunk directory")
    children = list(parts_dir.iterdir())
    parts = {}
    for child in children:
        if child.name == "README.txt":
            if not _regular(child):
                raise ValueError("Unsafe ZIP2 chunk README")
            continue
        m = PART_PATTERN.fullmatch(child.name)
        if not m or not _regular(child):
            raise ValueError("Unexpected ZIP2 chunk path or symlink")
        idx = int(m.group(1))
        if idx in parts:
            raise ValueError("Duplicate ZIP2 original chunk")
        parts[idx] = child
    expected_count = (expected_bytes + max_part_bytes - 1) // max_part_bytes
    if (not parts or len(parts) != expected_count
            or set(parts) != set(range(expected_count))):
        raise ValueError("Missing, extra or disordered ZIP2 source chunks")
    for i in range(expected_count):
        actual = parts[i].stat().st_size
        required = min(max_part_bytes, expected_bytes - i * max_part_bytes)
        if actual != required:
            raise ValueError("ZIP2 chunk size mismatch")
    if dest.is_symlink() or dest.exists():
        raise ValueError("Refusing to overwrite an original, staged or linked file")
    dest.parent.mkdir(parents=True, exist_ok=True)
    ancestor = dest.parent
    while True:
        if ancestor.is_symlink():
            raise ValueError("Unsafe ZIP2 output parent symlink")
        if ancestor == ancestor.parent:
            break
        ancestor = ancestor.parent
    temp_name = None
    digest = hashlib.sha256()
    written = 0
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".zip2-fft-", dir=dest.parent,
                                         delete=False) as output:
            temp_name = output.name
            for i in range(expected_count):
                with parts[i].open("rb") as chunk:
                    while True:
                        data = chunk.read(READ_BYTES)
                        if not data:
                            break
                        written += len(data)
                        if written > expected_bytes:
                            raise ValueError("ZIP2 source exceeded pinned original size")
                        output.write(data)
                        digest.update(data)
            output.flush()
            os.fsync(output.fileno())
        if written != expected_bytes or digest.hexdigest() != expected_sha256:
            raise ValueError("Reassembled ZIP2 original did not match pinned size/SHA256")
        # No-overwrite atomic publication on same filesystem.
        os.link(temp_name, dest)
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)
    return {
        "original_relative_path": ORIGINAL,
        "verified_bytes": written,
        "verified_sha256": digest.hexdigest(),
        "source_parts": expected_count,
        "source_provider": "pinned_zip2_git_without_lfs",
        "original_shader_bytes_reported": False,
        "game_source_mutated": False,
        "android_or_unity_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2-checkout", required=True, type=Path)
    p.add_argument("--destination", required=True, type=Path)
    args = p.parse_args()
    print("RAFT_A1_ZIP2_FFT_OWNER " + json.dumps(
        stage(args.zip2_checkout, args.destination), sort_keys=True))


if __name__ == "__main__":
    main()
