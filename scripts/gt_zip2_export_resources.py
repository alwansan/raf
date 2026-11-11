#!/usr/bin/env python3
"""GT: restore real ZIP2 graphics originals straight into transient AssetRipper input.

No Git LFS acquisition, no modification of tracked Raft, no original game bytes
in reports. Authenticates every selected plain/split file against the pinned
ZIP2 manifest BEFORE publishing it to input/Raft_Data. Existing verified
originals are reused; only exact Git LFS pointer placeholders can be replaced.
This prepares original texture/mesh stream data for AssetRipper. It does not
constitute proof of Unity shader conversion or Android GPU rendering.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from scripts.gt_zip2_payloads import (
    MAX_BYTES, MANIFEST_BLOB, ZIP2_SHA, SourceFailure, fingerprint,
    git, manifest, safe, source_parts,
)
from scripts.gt_stage_serialized_owners import OWNERS

POINTER = re.compile(
    rb"version https://git-lfs.github.com/spec/v1\n"
    rb"oid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?\Z"
)
ENGINE_FILES = (
    "Raft_Data/Resources/unity default resources",
    "Raft_Data/Resources/unity_builtin_extra",
)
CORE = (
    "Raft_Data/globalgamemanagers.assets",
    "Raft_Data/resources.assets",
    "Raft_Data/resources.assets.resS",
    *ENGINE_FILES,
)
RUNTIME_INPUT_FILES = (
    "Raft_Data/globalgamemanagers",
    "Raft_Data/boot.config",
)
# The full Unity export intake includes scene settings and boot configuration,
# not just the 82 serialized asset owners, 48 streamed files and 2 built-ins.


def choose(records: dict, profile: str, selected: list[str] | None = None) -> list[str]:
    if profile == "core":
        names = list(CORE)
    elif profile == "full":
        owners = {"Raft_Data/" + n for n in OWNERS}
        streams = {n for n in records if n.startswith("Raft_Data/") and
                   n.endswith((".resS", ".resource"))}
        names = sorted(owners | streams | set(ENGINE_FILES) | set(RUNTIME_INPUT_FILES))
        if len(owners) != 82 or len(streams) != 48 or len(names) != 134:
            raise SourceFailure("unexpected_full_graphics_source_coverage")
        if not (owners | streams | set(ENGINE_FILES) | set(RUNTIME_INPUT_FILES)) <= set(records):
            raise SourceFailure("missing_full_graphics_source")
    elif profile == "selected":
        if not selected or len(selected) != len(set(selected)):
            raise SourceFailure("empty_or_duplicate_selected_graphics")
        allow = ({"Raft_Data/" + n for n in OWNERS} |
                 {n for n in records if n.startswith("Raft_Data/") and
                  n.endswith((".resS", ".resource"))} | set(ENGINE_FILES) | set(RUNTIME_INPUT_FILES))
        if not set(selected) <= allow:
            raise SourceFailure("selected_path_not_graphics")
        names = sorted(selected)
    else:
        raise SourceFailure("unknown_graphics_profile")
    if any(n not in records for n in names):
        raise SourceFailure("original_graphics_resource_missing_from_manifest")
    return names


def _pointer_matches(path: Path, sha: str, size: int) -> bool:
    if not path.is_file() or path.stat().st_size > 256:
        return False
    match = POINTER.fullmatch(path.read_bytes())
    return bool(match and match[1].decode() == sha and int(match[2]) == size)


def _temp_path(target: Path):
    with tempfile.NamedTemporaryFile(
        mode="wb", prefix=".gt-original-graphics-", suffix=".partial",
        dir=target.parent, delete=False
    ) as stream:
        return Path(stream.name)


def restore(zip2: Path, input_root: Path, *, profile: str = "core",
            selected: list[str] | None = None, budget: int = MAX_BYTES,
            expected_commit: str = ZIP2_SHA,
            expected_blob: str = MANIFEST_BLOB,
            min_free_reserve: int = 512 * 1024 * 1024) -> dict:
    zip2, input_root = Path(zip2).absolute(), Path(input_root).absolute()
    safe(zip2)
    safe(input_root)
    if (not zip2.is_dir() or zip2 == input_root or
        zip2.is_relative_to(input_root) or input_root.is_relative_to(zip2)):
        raise SourceFailure("unsafe_source_and_input_overlap")
    if (type(budget) is not int or budget <= 0 or budget > MAX_BYTES or
        type(min_free_reserve) is not int or min_free_reserve < 0):
        raise SourceFailure("unsafe_source_byte_budget")
    records = manifest(zip2, expected_commit=expected_commit, expected_blob=expected_blob)
    names = choose(records, profile, selected)
    planned = []
    total = 0
    required = 0
    reuse = 0
    for rel in names:
        kind, size, sha = records[rel]
        total += size
        if total > budget:
            raise SourceFailure("original_graphics_profile_exceeds_budget")
        src = zip2 / "Raft" / rel
        parts = source_parts(src, kind, size)
        dst = input_root / rel[len("Raft_Data/"):]
        safe(dst)
        status = "new"
        if dst.exists():
            if not dst.is_file():
                raise SourceFailure("nonfile_original_graphics_destination")
            if dst.stat().st_size == size and fingerprint(dst) == (size, sha):
                status = "verified"
                reuse += 1
            elif _pointer_matches(dst, sha, size):
                status = "pointer"
            else:
                raise SourceFailure("refuse_overwrite_nonoriginal_export_input")
        if status != "verified":
            required += size
        planned.append((rel, parts, dst, size, sha, status))
    # Reject insufficient disk before any output or existing pointer changes.
    ancestor = input_root
    while not ancestor.exists():
        ancestor = ancestor.parent
    free = shutil.disk_usage(ancestor).free
    if free < required + min_free_reserve:
        raise SourceFailure("insufficient_space_for_authentic_graphics_stage")

    pending = []
    replacements = 0
    try:
        for rel, parts, target, size, sha, status in planned:
            if status == "verified":
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            safe(target.parent)
            target_temp = _temp_path(target)
            pending.append((target_temp, target, sha, size, status))
            copied = 0
            h = hashlib.sha256()
            with target_temp.open("wb") as output:
                for part in parts:
                    safe(part)
                    with part.open("rb") as inp:
                        while chunk := inp.read(2 * 1024 * 1024):
                            copied += len(chunk)
                            if copied > size:
                                raise SourceFailure("original_resource_exceeds_manifest_size")
                            h.update(chunk)
                            output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            if copied != size or h.hexdigest() != sha:
                raise SourceFailure("original_resource_sha256_or_size_mismatch")
            os.chmod(target_temp, 0o644)

        if git(zip2, "rev-parse", "HEAD") != expected_commit or (
            git(zip2, "hash-object", str(zip2 / "RAFT_FILE_MANIFEST.tsv")) != expected_blob
        ):
            raise SourceFailure("zip2_reference_changed_before_commit")
        # All files are authenticated first; each install is atomic. No
        # cross-file OS transaction is claimed; errors fail the export step.
        for temporary, target, sha, size, status in pending:
            if status == "new":
                if target.exists() or target.is_symlink():
                    raise SourceFailure("original_graphics_target_appeared")
            elif not _pointer_matches(target, sha, size):
                raise SourceFailure("graphics_destination_pointer_changed")
            os.replace(temporary, target)
            replacements += status == "pointer"
        return {
            "schema": "GT_ZIP2_REAL_EXPORT_RESOURCE_RESTORATION_V1",
            "source_commit": expected_commit,
            "profile": profile,
            "original_resources_verified": len(planned),
            "source_verified_bytes": total,
            "files_newly_materialized": len(pending) - replacements,
            "files_verified_and_reused": reuse,
            "original_placeholder_pointers_replaced": replacements,
            "original_bytes_materialized_or_reused": total,
            "original_payload_sha256_and_size_verified": True,
            "git_lfs_used": False,
            "source_file_content_exported_in_report": False,
            "assetripper_input_ready_for_selected_scope": True,
            "asset_ripper_execution_proven": False,
            "unity_android_gpu_verified": False
        }
    finally:
        for temporary, *_ in pending:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip2-checkout", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path,
                        help="Temporary original AssetRipper Raft_Data directory, not repository")
    parser.add_argument("--profile", choices=("core", "full", "selected"), default="core")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--byte-budget", type=int, default=MAX_BYTES)
    parser.add_argument("--reserve-bytes", type=int, default=512*1024*1024)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if (args.profile == "selected") != bool(args.path):
        parser.error("Provide --path only with --profile selected")
    report = args.report.absolute()
    if (report.is_relative_to(args.input_root.absolute()) or
        report.is_relative_to(args.zip2_checkout.absolute())):
        raise SourceFailure("report_inside_source_or_export_input")
    result = restore(args.zip2_checkout, args.input_root, profile=args.profile,
                     selected=args.path, budget=args.byte_budget,
                     min_free_reserve=args.reserve_bytes)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("GT_ZIP2_EXPORT_INPUT_RESOURCES " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
