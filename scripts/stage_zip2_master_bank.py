"""Reconstruct the authentic Raft MasterBank.bank from pinned ZIP2 Git chunks.

This provider is read-only and never alters the original ZIP2 or Raft trees.
The verified output is an ordinary file outside Unity Assets. The downstream
StreamingAssets stage independently checks the original LFS bank SHA/size.
Do not execute the PC game or upload the original bank as an artifact.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ZIP2_COMMIT = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
ZIP2_MANIFEST_GIT_BLOB = "4201fda426d80caba36c275ceaddb440b05c5b4e"
ORIGINAL_PATH = "Raft_Data/StreamingAssets/MasterBank.bank"
ORIGINAL_SIZE = 101_600_960
ORIGINAL_SHA256 = "10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339"
PART_BYTES = 45 * 1024 * 1024
READ_BYTES = 2 * 1024 * 1024
HEADER = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
PART_RE = re.compile(r"part-([0-9]{5})\Z")


def _is_plain(path):
    return path.is_file() and not path.is_symlink()


def _unlinked_parents(path):
    ancestor = Path(path)
    while True:
        if ancestor.is_symlink():
            return False
        if ancestor.parent == ancestor:
            return True
        ancestor = ancestor.parent


def _git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
    ).strip()


def stage(zip2_checkout, destination, *, expected_commit=ZIP2_COMMIT,
          expected_manifest_blob=ZIP2_MANIFEST_GIT_BLOB,
          expected_bytes=ORIGINAL_SIZE, expected_sha256=ORIGINAL_SHA256,
          part_bytes=PART_BYTES):
    """Verify pinned source, stream exact parts, publish atomically no-overwrite.

    expected_* arguments support independently pinned tiny synthetic fixtures;
    production CLI never accepts overrides from user input.
    """
    root, dest = Path(zip2_checkout), Path(destination)
    if (not root.is_dir() or not _unlinked_parents(root)
            or not re.fullmatch(r"[a-f0-9]{40}", expected_commit)
            or not re.fullmatch(r"[a-f0-9]{40}", expected_manifest_blob)
            or type(expected_bytes) is not int or not 1 <= expected_bytes <= 2**31
            or not re.fullmatch(r"[a-f0-9]{64}", expected_sha256)
            or type(part_bytes) is not int or not 1 <= part_bytes <= PART_BYTES):
        raise ValueError("Unsafe or unpinned ZIP2 MasterBank provider")
    if _git(root, "rev-parse", "HEAD") != expected_commit:
        raise ValueError("ZIP2 source commit identity mismatch")
    manifest = root / "RAFT_FILE_MANIFEST.tsv"
    source = root / "Raft" / "Raft_Data" / "StreamingAssets" / "MasterBank.bank"
    if (not _is_plain(manifest) or manifest.stat().st_size > 1024 * 1024
            or not source.is_dir() or not _unlinked_parents(source)):
        raise ValueError("Unsafe or missing ZIP2 original audio source")
    if _git(root, "hash-object", "--", "RAFT_FILE_MANIFEST.tsv") != expected_manifest_blob:
        raise ValueError("ZIP2 original manifest blob identity mismatch")
    with manifest.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != HEADER:
            raise ValueError("Unexpected ZIP2 manifest schema")
        hits = [line for line in reader
                if line.get("relative_path_under_Raft") == ORIGINAL_PATH]
    if len(hits) != 1 or hits[0].get("kind") != "split" or (
        hits[0].get("bytes") != str(expected_bytes)
        or hits[0].get("sha256") != expected_sha256
    ):
        raise ValueError("ZIP2 manifest does not match immutable original MasterBank")
    children = list(source.iterdir())
    parts = {}
    for entry in children:
        if entry.name == "README.txt":
            if not _is_plain(entry):
                raise ValueError("Unsafe ZIP2 source README")
            continue
        matched = PART_RE.fullmatch(entry.name)
        if not matched or not _is_plain(entry):
            raise ValueError("Unknown, linked, or non-file ZIP2 bank part")
        idx = int(matched.group(1))
        if idx in parts:
            raise ValueError("Duplicate ZIP2 bank part")
        parts[idx] = entry
    count = (expected_bytes + part_bytes - 1) // part_bytes
    if set(parts) != set(range(count)):
        raise ValueError("ZIP2 MasterBank missing/extra/out-of-range chunk")
    for i in range(count):
        expected_part = min(part_bytes, expected_bytes - i * part_bytes)
        if parts[i].stat().st_size != expected_part:
            raise ValueError("ZIP2 MasterBank split part length mismatch")
    if dest.is_symlink() or dest.exists() or not _unlinked_parents(dest.parent):
        raise ValueError("Refusing unsafe or already published MasterBank destination")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not _unlinked_parents(dest.parent):
        raise ValueError("Unsafe ZIP2 destination parent")
    written, digest, temp_name = 0, hashlib.sha256(), None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".zip2-masterbank-", suffix=".partial",
            dir=dest.parent, delete=False,
        ) as output:
            temp_name = output.name
            for i in range(count):
                with parts[i].open("rb") as chunk:
                    while True:
                        block = chunk.read(READ_BYTES)
                        if not block:
                            break
                        written += len(block)
                        if written > expected_bytes:
                            raise ValueError("ZIP2 MasterBank exceeds original size")
                        output.write(block)
                        digest.update(block)
            output.flush()
            os.fsync(output.fileno())
        if written != expected_bytes or digest.hexdigest() != expected_sha256:
            raise ValueError("ZIP2 MasterBank reconstructed SHA256/size mismatch")
        # Keep temp in the same filesystem as the output and never replace a
        # concurrent file that appeared after our initial no-overwrite check.
        os.link(temp_name, dest)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)
    return dict(source="immutable_zip2_no_lfs", original_bytes=written,
                original_sha256=digest.hexdigest(), chunks=count,
                original_game_modified=False, unity_or_phone_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip2-checkout", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    print("RAFT_A9_ZIP2_MASTERBANK " + json.dumps(
        stage(args.zip2_checkout, args.destination), sort_keys=True))


if __name__ == "__main__":
    main()
