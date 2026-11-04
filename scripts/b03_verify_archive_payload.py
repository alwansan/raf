#!/usr/bin/env python3
"""B03: fail-closed, byte-authenticated intake of one original ZIP2 manifest file.

Accepts exact original raw bytes, or *one* strict multipart/form-data transport
part containing exactly the pinned original byte count. Transport metadata,
filenames and outer asset hashes never substitute for the original SHA-256.

No original bytes are printed; output lives only under an isolated staging root.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

CHUNK = 1024 * 1024
HEADER_LIMIT = 16384
LINE_LIMIT = 2048
EXPECTED_HEADER = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
SHA = re.compile(r"[0-9a-f]{64}\Z")
BOUNDARY = re.compile(rb"[0-9A-Za-z'()+_,./:=?-]{1,70}\Z")


class IntakeError(ValueError):
    """Invalid or unverifiable transport; no payload may be published."""


def safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (not value or "\\" in value or "\x00" in value or ":" in value or
        path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/"))):
        raise IntakeError("unsafe_manifest_relative_path")
    return path


def manifest_record(manifest: Path, relative: str) -> tuple[int, str]:
    if manifest.is_symlink() or not manifest.is_file():
        raise IntakeError("unsafe_or_missing_manifest")
    safe_relative(relative)
    seen: set[str] = set()
    found = None
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != EXPECTED_HEADER:
            raise IntakeError("unexpected_manifest_schema")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise IntakeError("malformed_manifest_row")
            name = row["relative_path_under_Raft"]
            safe_relative(name)
            if name in seen:
                raise IntakeError("duplicate_manifest_entry")
            seen.add(name)
            if row["kind"] not in {"plain", "split"} or not SHA.fullmatch(row["sha256"]):
                raise IntakeError("malformed_manifest_pin")
            try:
                count = int(row["bytes"])
            except ValueError as exc:
                raise IntakeError("bad_manifest_size") from exc
            if count < 0 or str(count) != row["bytes"]:
                raise IntakeError("bad_manifest_size")
            if name == relative:
                found = (count, row["sha256"])
    if found is None:
        raise IntakeError("source_not_in_pinned_manifest")
    return found


def copy_exact(source, target, count: int, digest) -> None:
    remaining = count
    while remaining:
        part = source.read(min(CHUNK, remaining))
        if not part:
            raise IntakeError("truncated_source_payload")
        target.write(part)
        digest.update(part)
        remaining -= len(part)


def parse_multipart(source, target, expected_size: int, digest) -> None:
    first = source.readline(128)
    if not first.startswith(b"--") or not first.endswith(b"\r\n"):
        raise IntakeError("invalid_multipart_opening")
    boundary = first[2:-2]
    if not BOUNDARY.fullmatch(boundary):
        raise IntakeError("invalid_multipart_boundary")
    headers = {}
    total = 0
    while True:
        line = source.readline(LINE_LIMIT + 1)
        total += len(line)
        if not line or len(line) > LINE_LIMIT or total > HEADER_LIMIT or not line.endswith(b"\r\n"):
            raise IntakeError("invalid_multipart_headers")
        if line == b"\r\n":
            break
        if b":" not in line:
            raise IntakeError("invalid_multipart_headers")
        name, value = line[:-2].split(b":", 1)
        try:
            key = name.decode("ascii").lower()
            value.decode("ascii")
        except UnicodeError as exc:
            raise IntakeError("non_ascii_multipart_header") from exc
        if not re.fullmatch(r"[a-z][a-z0-9-]*", key) or key in headers:
            raise IntakeError("duplicate_or_invalid_multipart_header")
        headers[key] = value.strip()
    disposition = headers.get("content-disposition", b"")
    if not re.fullmatch(rb"form-data;[ \t]*name=\"[^\"\r\n]{1,128}\"(?:;[ \t]*filename=\"[^\"\r\n]{1,512}\")?", disposition, re.I):
        raise IntakeError("invalid_form_data_disposition")
    if set(headers) - {"content-disposition", "content-type"}:
        raise IntakeError("unsupported_multipart_header")
    if "content-type" in headers and b"\r" in headers["content-type"]:
        raise IntakeError("invalid_content_type")
    copy_exact(source, target, expected_size, digest)
    ending = b"\r\n--" + boundary + b"--"
    if source.read(len(ending)) != ending:
        raise IntakeError("multipart_payload_size_or_closing_mismatch")
    if source.read(2) not in (b"", b"\r\n") or source.read(1):
        raise IntakeError("multipart_extra_part_or_epilogue")


def ensure_safe_staging(root: Path, relative: PurePosixPath, source: Path) -> Path:
    if root.is_symlink() or any(p.is_symlink() for p in root.parents) or not root.is_dir():
        raise IntakeError("unsafe_staging_root")
    if source.resolve().is_relative_to(root.resolve()):
        raise IntakeError("input_inside_staging_root")
    folder = root
    for part in relative.parts[:-1]:
        folder = folder / part
        if folder.is_symlink():
            raise IntakeError("symlink_staging_parent")
        folder.mkdir(exist_ok=True)
        if not folder.is_dir() or folder.is_symlink():
            raise IntakeError("invalid_staging_parent")
    output = folder / relative.name
    if output.exists() or output.is_symlink():
        raise IntakeError("refuse_to_overwrite_staged_source")
    return output


def intake(input_file: Path, manifest: Path, relative: str, staging_root: Path) -> dict:
    if input_file.is_symlink() or not input_file.is_file():
        raise IntakeError("unsafe_or_missing_input")
    expected_size, expected_sha = manifest_record(manifest, relative)
    output = ensure_safe_staging(staging_root, safe_relative(relative), input_file)
    available = input_file.stat().st_size
    if available < expected_size:
        raise IntakeError("transport_shorter_than_original")
    method = "raw" if available == expected_size else "multipart-single-part"
    tmp_name = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=".b03-verified-", dir=str(output.parent))
        with os.fdopen(fd, "wb") as dest, input_file.open("rb") as original:
            digest = hashlib.sha256()
            if method == "raw":
                copy_exact(original, dest, expected_size, digest)
                if original.read(1):
                    raise IntakeError("raw_payload_overrun")
            else:
                parse_multipart(original, dest, expected_size, digest)
            dest.flush()
            os.fsync(dest.fileno())
            if digest.hexdigest() != expected_sha:
                raise IntakeError("original_manifest_sha256_mismatch")
        # Hard-link is atomic and exclusive: unlike os.replace, never clobbers a
        # concurrent recipient. Original bytes only become visible after SHA.
        os.link(tmp_name, output)
        return {"verified": True, "source_format": method,
                "original_size": expected_size, "original_sha256": expected_sha,
                "deployed_files": 1}
    finally:
        if tmp_name is not None:
            Path(tmp_name).unlink(missing_ok=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True, help="Local raw GitHub release asset download")
    ap.add_argument("--manifest", type=Path, required=True, help="Pinned ZIP2 RAFT_FILE_MANIFEST.tsv")
    ap.add_argument("--relative-path", required=True, help="Exact manifest path, never inferred from asset name")
    ap.add_argument("--stage", type=Path, required=True, help="Pre-existing, separate staging root")
    args = ap.parse_args(argv)
    try:
        result = intake(args.input, args.manifest, args.relative_path, args.stage)
    except IntakeError as exc:
        print(json.dumps({"verified": False, "error": str(exc)}))
        return 1
    except OSError:
        # Operating-system errors can embed private input/staging paths.
        print(json.dumps({"verified": False, "error": "file_io_failure"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
