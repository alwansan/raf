#!/usr/bin/env python3
"""GT: acquire any pinned Raft original directly from ZIP2, never Git LFS.

Select the minimal needed original files (including .resS, .resource and
split .assets). Reassemble numbered ZIP2 parts into an isolated destination,
verify full original size + SHA256, and publish completed files atomically.
This does not import Unity, alter a tracked game file, or prove GPU rendering.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
MANIFEST_BLOB = "4201fda426d80caba36c275ceaddb440b05c5b4e"
COLUMNS = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
PART_SIZE = 45 * 1024 * 1024
READ_SIZE = 2 * 1024 * 1024
MAX_BYTES = 10 * 1024 ** 3
PIN = re.compile(r"[0-9a-f]{64}\Z")


class SourceFailure(ValueError):
    pass


def safe(path: Path):
    """Reject symlinks and linked regular files at every direct boundary."""
    if any(node.is_symlink() for node in (path, *path.parents)):
        raise SourceFailure("symlinked_original_or_stage")
    if path.is_file() and path.stat().st_nlink != 1:
        raise SourceFailure("hardlinked_original_or_stage")
    if path.exists() and not (path.is_dir() or path.is_file()):
        raise SourceFailure("unexpected_source_or_stage_kind")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args],
                                   text=True, stderr=subprocess.DEVNULL).strip()


def manifest(root: Path, *, expected_commit: str = ZIP2_SHA,
             expected_blob: str = MANIFEST_BLOB) -> dict[str, tuple[str, int, str]]:
    root = Path(root).absolute()
    safe(root)
    source = root / "RAFT_FILE_MANIFEST.tsv"
    safe(source)
    if not root.is_dir() or not source.is_file() or source.stat().st_size > 1_000_000:
        raise SourceFailure("missing_or_oversized_zip2_manifest")
    if git(root, "rev-parse", "HEAD") != expected_commit:
        raise SourceFailure("zip2_checkout_does_not_match_pinned_commit")
    if git(root, "hash-object", str(source)) != expected_blob:
        raise SourceFailure("zip2_manifest_git_blob_mismatch")
    result = {}
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream, delimiter="\t")
        if rows.fieldnames != COLUMNS:
            raise SourceFailure("original_manifest_schema_changed")
        for row in rows:
            if None in row or any(value is None for value in row.values()):
                raise SourceFailure("invalid_zip2_manifest_row")
            rel = row["relative_path_under_Raft"]
            if (not rel or rel.startswith("/") or "\\" in rel or ":" in rel or
                any(part in ("", ".", "..") for part in rel.split("/")) or rel in result):
                raise SourceFailure("invalid_or_duplicated_zip2_path")
            if row["kind"] not in ("plain", "split") or not PIN.fullmatch(row["sha256"]):
                raise SourceFailure("invalid_zip2_source_digest_or_kind")
            try:
                bytes_expected = int(row["bytes"])
            except (TypeError, ValueError) as error:
                raise SourceFailure("invalid_original_file_length") from error
            if bytes_expected < 0 or str(bytes_expected) != row["bytes"]:
                raise SourceFailure("invalid_original_file_length")
            result[rel] = (row["kind"], bytes_expected, row["sha256"])
    if git(root, "hash-object", str(source)) != expected_blob:
        raise SourceFailure("zip2_manifest_changed_during_read")
    return result


def source_parts(source: Path, kind: str, size: int) -> list[Path]:
    safe(source)
    if kind == "plain":
        if not source.is_file() or source.stat().st_size != size:
            raise SourceFailure("zip2_plain_file_missing_or_wrong_size")
        return [source]
    if not source.is_dir():
        raise SourceFailure("zip2_split_directory_missing")
    entries = list(source.iterdir())
    count = (size + PART_SIZE - 1) // PART_SIZE
    if count == 0:
        raise SourceFailure("zero_length_split_original")
    required = [f"part-{i:05d}" for i in range(count)]
    if (sorted(p.name for p in entries if p.name != "README.txt") != required or
        len(entries) not in (count, count + 1)):
        raise SourceFailure("zip2_split_parts_missing_duplicate_or_extra")
    if (source / "README.txt").exists():
        safe(source / "README.txt")
        if not (source / "README.txt").is_file():
            raise SourceFailure("unsafe_split_readme")
    parts = [source / name for name in required]
    for i, part in enumerate(parts):
        safe(part)
        if not part.is_file() or part.stat().st_size != min(PART_SIZE, size - i * PART_SIZE):
            raise SourceFailure("zip2_split_part_size_mismatch")
    return parts


def fingerprint(path: Path) -> tuple[int, str]:
    safe(path)
    h = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(READ_SIZE), b""):
            count += len(data)
            h.update(data)
    return count, h.hexdigest()


def stage(root: Path, destination: Path, paths: list[str], *,
          byte_budget: int = MAX_BYTES,
          expected_commit: str = ZIP2_SHA, expected_blob: str = MANIFEST_BLOB) -> dict:
    root, destination = Path(root).absolute(), Path(destination).absolute()
    safe(root)
    safe(destination)
    if (not root.is_dir() or root == destination or
        destination.is_relative_to(root) or root.is_relative_to(destination)):
        raise SourceFailure("unsafe_zip2_stage_overlap")
    if type(byte_budget) is not int or not 1 <= byte_budget <= MAX_BYTES:
        raise SourceFailure("unsafe_byte_budget")
    known = manifest(root, expected_commit=expected_commit, expected_blob=expected_blob)
    if not paths or len(paths) != len(set(paths)):
        raise SourceFailure("no_files_selected_or_duplicate_selection")
    planned = []
    total = 0
    for relative in paths:
        if relative not in known:
            raise SourceFailure("file_not_in_pinned_zip2_manifest")
        kind, size, sha = known[relative]
        total += size
        if total > byte_budget:
            raise SourceFailure("zip2_acquisition_exceeds_budget")
        src = root / "Raft" / relative
        dst = destination / "Raft" / relative
        safe(dst)
        chunks = source_parts(src, kind, size)
        if dst.exists() and (not dst.is_file() or fingerprint(dst) != (size, sha)):
            raise SourceFailure("existing_cached_payload_not_original")
        planned.append((relative, size, sha, chunks, dst))
    published, reused = 0, 0
    for relative, size, sha, chunks, target in planned:
        if target.exists():
            reused += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        safe(target.parent)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".gt-zip2-original-", suffix=".partial",
                dir=target.parent, delete=False
            ) as output:
                tmp = Path(output.name)
                length, h = 0, hashlib.sha256()
                for chunk in chunks:
                    with chunk.open("rb") as source:
                        for block in iter(lambda: source.read(READ_SIZE), b""):
                            length += len(block)
                            if length > size:
                                raise SourceFailure("zip2_source_exceeded_manifest_length")
                            h.update(block)
                            output.write(block)
                output.flush()
                os.fsync(output.fileno())
            if length != size or h.hexdigest() != sha:
                raise SourceFailure("zip2_reconstructed_file_sha256_mismatch")
            os.chmod(tmp, 0o644)
            # Exclusion: unlike os.replace, os.link cannot overwrite a file
            # concurrently created by another worker.
            os.link(tmp, target)
            published += 1
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
    return {
        "source_commit": expected_commit, "files_selected": len(paths),
        "original_bytes_verified": total, "newly_staged": published,
        "previously_verified_cache": reused, "git_lfs_used": False,
        "file_sha256_and_size_verified": True,
        "runtime_or_android_graphics_verified": False
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip2-checkout", type=Path, required=True)
    ap.add_argument("--destination", type=Path, required=True)
    ap.add_argument("--path", action="append", default=[],
                    help="Raft-relative manifest path e.g. Raft_Data/level0.resS")
    ap.add_argument("--all-streams", action="store_true",
                    help="All original .resS/.resource payloads; requires explicit byte budget")
    ap.add_argument("--byte-budget", type=int, default=1024 ** 3)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if bool(args.path) == args.all_streams:
        ap.error("Supply repeated --path OR --all-streams, not both")
    original = manifest(args.zip2_checkout)
    selected = ([path for path in original if path.endswith((".resS", ".resource"))]
                if args.all_streams else args.path)
    if args.report.resolve().is_relative_to(args.destination.resolve()) or args.report.resolve().is_relative_to(args.zip2_checkout.resolve()):
        raise SourceFailure("report_inside_source_or_original_stage")
    result = stage(args.zip2_checkout, args.destination, selected,
                   byte_budget=args.byte_budget)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("GT_ZIP2_ORIGINAL_PAYLOADS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
