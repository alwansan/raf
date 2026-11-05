"""T5: stage original serialized graphics owners from immutable ZIP2, without LFS.

Only original feature-branch Git LFS pointers in hydrate_render_payloads.plan()
are eligible. ZIP2's pinned Git commit/manifest and independent feature LFS
SHA256/byte lengths MUST agree before an asset is made visible. Staging occurs
outside both source checkouts; nothing is published or sent to an artifact.
This is an acquisition/integration bridge, not shader or Android pixel proof.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

from scripts.hydrate_render_payloads import PATTERN, plan as feature_lfs_plan

ZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
MANIFEST_GIT_BLOB = "4201fda426d80caba36c275ceaddb440b05c5b4e"
HEADER = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
CHUNK = 2 * 1024 * 1024
PART = 45 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_BUDGET = 10 * 1024 ** 3
PART_NAME = re.compile(r"part-[0-9]{5}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _safe(path: Path) -> None:
    if any(node.is_symlink() for node in (path, *path.parents)):
        raise ValueError("unsafe_symlinked_input_or_output")
    if path.is_file() and path.stat().st_nlink != 1:
        raise ValueError("unsafe_hardlinked_input_or_output")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def _manifest(root: Path, *, expected_blob: str) -> dict:
    source = root / "RAFT_FILE_MANIFEST.tsv"
    _safe(source)
    if not source.is_file() or source.stat().st_size > MAX_MANIFEST:
        raise ValueError("missing_or_oversized_original_manifest")
    if _git(root, "hash-object", "--", "RAFT_FILE_MANIFEST.tsv") != expected_blob:
        raise ValueError("original_manifest_git_blob_mismatch")
    records = {}
    with source.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != HEADER:
            raise ValueError("unexpected_original_manifest_schema")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("invalid_original_manifest_record")
            rel = row["relative_path_under_Raft"]
            parts = rel.split("/")
            if (not rel or "\\" in rel or ":" in rel or
                    PurePosixPath(rel).is_absolute() or
                    any(part in ("", ".", "..") for part in parts) or
                    rel in records or
                    row["kind"] not in ("plain", "split") or
                    not DIGEST.fullmatch(row["sha256"])):
                raise ValueError("invalid_original_manifest_record")
            try:
                count = int(row["bytes"])
            except ValueError as exc:
                raise ValueError("invalid_original_manifest_size") from exc
            if count < 0 or str(count) != row["bytes"]:
                raise ValueError("invalid_original_manifest_size")
            records[rel] = (row["kind"], count, row["sha256"])
    if _git(root, "hash-object", "--", "RAFT_FILE_MANIFEST.tsv") != expected_blob:
        raise ValueError("original_manifest_changed_during_read")
    return records


def _inputs(source: Path, kind: str, size: int) -> list[Path]:
    _safe(source)
    if kind == "plain":
        if not source.is_file() or source.stat().st_size != size:
            raise ValueError("missing_or_wrong_length_plain_original")
        return [source]
    if not source.is_dir():
        raise ValueError("missing_original_split_directory")
    children = sorted(source.iterdir())
    expected_count = (size + PART - 1) // PART
    names = [f"part-{index:05d}" for index in range(expected_count)]
    if sorted(p.name for p in children if p.name != "README.txt") != names:
        raise ValueError("missing_extra_or_unordered_original_parts")
    if len(children) not in (expected_count, expected_count + 1):
        raise ValueError("unexpected_original_split_entries")
    inputs = [source / name for name in names]
    for index, item in enumerate(inputs):
        _safe(item)
        expected = min(PART, size - index * PART)
        if not item.is_file() or item.stat().st_size != expected:
            raise ValueError("original_split_part_length_or_type_mismatch")
    if (source / "README.txt").exists():
        readme = source / "README.txt"
        _safe(readme)
        if not readme.is_file():
            raise ValueError("unsafe_original_split_readme")
    return inputs


def _fingerprint(path: Path) -> tuple[int, str]:
    _safe(path)
    digest, count = hashlib.sha256(), 0
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
            count += len(block)
    return count, digest.hexdigest()


def stage(zip2_checkout: Path, output_root: Path, *, owners: list[str],
          byte_budget: int = MAX_BUDGET,
          entries: list[tuple[str, str, int]] | None = None,
          expected_commit: str = ZIP2_SHA,
          expected_manifest_blob: str = MANIFEST_GIT_BLOB) -> dict:
    """Stage selected immutable graphics assets to output_root/Raft_Data/*.

    Override pins/entries only in isolated tiny synthetic fixtures, never via
    CLI or environment. Real staging uses the independent feature LFS plan.
    """
    root, output = Path(zip2_checkout).absolute(), Path(output_root).absolute()
    _safe(root)
    _safe(output)
    if not root.is_dir() or output == root or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError("unsafe_or_overlapping_source_and_output")
    if (type(byte_budget) is not int or not 1 <= byte_budget <= MAX_BUDGET or
            not re.fullmatch("[0-9a-f]{40}", expected_commit) or
            not re.fullmatch("[0-9a-f]{40}", expected_manifest_blob)):
        raise ValueError("invalid_source_pins_or_budget")
    if _git(root, "rev-parse", "HEAD") != expected_commit:
        raise ValueError("original_zip2_commit_mismatch")
    original = _manifest(root, expected_blob=expected_manifest_blob)
    rows = feature_lfs_plan() if entries is None else entries
    eligible = {}
    for pathname, digest, size in rows:
        if not PATTERN.fullmatch(pathname) or not pathname.startswith("Raft/Raft_Data/"):
            raise ValueError("unexpected_feature_graphics_pointer_path")
        rel = pathname.removeprefix("Raft/")
        if rel in eligible or not DIGEST.fullmatch(digest) or type(size) is not int or size <= 0:
            raise ValueError("duplicate_or_invalid_feature_graphics_pointer")
        eligible[rel] = (size, digest)
    if not owners or len(owners) != len(set(owners)):
        raise ValueError("empty_or_duplicate_requested_owner")
    requested = []
    total = 0
    for rel in owners:
        if rel not in eligible or rel not in original:
            raise ValueError("requested_owner_not_in_both_immutable_sources")
        size, digest = eligible[rel]
        kind, original_size, original_digest = original[rel]
        if (size, digest) != (original_size, original_digest):
            raise ValueError("original_zip2_and_feature_lfs_identity_disagree")
        total += size
        if total > byte_budget:
            raise ValueError("original_graphics_staging_budget_exceeded")
        requested.append((rel, kind, size, digest))
    output.mkdir(parents=True, exist_ok=True)
    _safe(output)
    built = cached = 0
    for rel, kind, size, digest in requested:
        source = root / "Raft" / rel
        target = output / rel
        _safe(source)
        _safe(target)
        inputs = _inputs(source, kind, size)
        if target.exists():
            if not target.is_file() or _fingerprint(target) != (size, digest):
                raise ValueError("existing_staged_original_conflicts_with_pin")
            cached += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        _safe(target.parent)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=target.parent,
                prefix=".t5-original-graphics-", suffix=".partial",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                copied = 0
                sha = hashlib.sha256()
                for part in inputs:
                    with part.open("rb") as stream:
                        while block := stream.read(CHUNK):
                            copied += len(block)
                            if copied > size:
                                raise ValueError("original_graphics_source_overflow")
                            sha.update(block)
                            handle.write(block)
                handle.flush()
                os.fsync(handle.fileno())
            if copied != size or sha.hexdigest() != digest:
                raise ValueError("original_graphics_sha256_or_size_mismatch")
            os.chmod(temporary, 0o644)
            # Never replace an existing concurrent output; unlike os.replace,
            # hard-link publication is exclusive on the Linux CI filesystem.
            os.link(temporary, target)
            built += 1
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
    return {
        "original_provider_commit": expected_commit,
        "owners_verified": len(requested), "owners_staged": built,
        "owners_cached": cached, "original_bytes_verified": total,
        "source_sha256_verified": True, "used_lfs": False,
        "editor_or_phone_executed": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--zip2-checkout", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--owner", action="append", default=[])
    ap.add_argument("--byte-budget", type=int, default=MAX_BUDGET)
    ap.add_argument("--all-graphics", action="store_true")
    args = ap.parse_args()
    if bool(args.owner) == args.all_graphics:
        ap.error("Choose explicit --owner entries OR --all-graphics")
    selected = ([row[0].removeprefix("Raft/") for row in feature_lfs_plan()]
                if args.all_graphics else args.owner)
    print("RAFT_T5_ZIP2_RENDER_STAGE " + json.dumps(
        stage(args.zip2_checkout, args.output_root,
              owners=selected, byte_budget=args.byte_budget), sort_keys=True))


if __name__ == "__main__":
    main()
