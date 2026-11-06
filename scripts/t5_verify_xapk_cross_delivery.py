#!/usr/bin/env python3
"""Verify real split XAPK members against authenticated local APK/OBB records.

Read-only; never reassemble, extract, resign, or mutate a native game package.
This is a transport/content parity check, NOT APK signature or device proof.
"""
from __future__ import annotations

from bisect import bisect_right
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

from scripts.package_android_delivery import PACKAGE

APK = "Raft-Android-Test.apk"
XAPK = "Raft-Android-Test.xapk"
HEX = re.compile(r"[0-9a-f]{64}\Z")
SAFE = re.compile(r"[A-Za-z0-9_.-]+\Z")
CHUNK = 1024 * 1024
MAX_PARTS = 200
MAX_PART_BYTES = 2_147_483_647
MAX_METADATA = 100_000
MAX_XAPK_MANIFEST = 16_384


def _object(item, label):
    if type(item) is not dict:
        raise ValueError("Invalid " + label)
    return item


def _safe_name(name):
    return (type(name) is str and SAFE.fullmatch(name) is not None
            and name not in (".", ".."))


def _sha(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def _read_small(path: Path, max_bytes: int) -> bytes:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= max_bytes:
        raise ValueError("Missing/unsafe small metadata file: " + path.name)
    with path.open("rb") as stream:
        content = stream.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise ValueError("Oversized metadata file: " + path.name)
    return content


def _hash_parts(parts, expected_size: int, expected_sha: str):
    complete = hashlib.sha256()
    total = 0
    for path, size, digest in parts:
        if path.is_symlink() or not path.is_file() or path.stat().st_size != size:
            raise ValueError("Missing, linked or incorrectly sized transport part")
        observed = hashlib.sha256()
        current = 0
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK), b""):
                observed.update(block)
                complete.update(block)
                current += len(block)
                total += len(block)
        if current != size or observed.hexdigest() != digest:
            raise ValueError("Actual transport part SHA256/size differs from manifest")
    if total != expected_size or complete.hexdigest() != expected_sha:
        raise ValueError("Actual logical file SHA256/size differs from manifest")


class SplitZipReader(io.RawIOBase):
    """Seekable, bounded reader crossing .part001 boundaries without assembly."""
    def __init__(self, paths_and_sizes):
        super().__init__()
        self._paths = [path for path, _ in paths_and_sizes]
        self._bounds = [0]
        for _, length in paths_and_sizes:
            if type(length) is not int or length <= 0:
                raise ValueError("Invalid split ZIP part length")
            self._bounds.append(self._bounds[-1] + length)
        if not self._paths:
            raise ValueError("Split ZIP needs at least one part")
        self._pos = 0
        self._active = None
        self._active_index = None

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self._pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            position = offset
        elif whence == io.SEEK_CUR:
            position = self._pos + offset
        elif whence == io.SEEK_END:
            position = self._bounds[-1] + offset
        else:
            raise ValueError("Unsupported split ZIP seek mode")
        if type(position) is not int or not 0 <= position <= self._bounds[-1]:
            raise ValueError("Split ZIP seek outside boundaries")
        self._pos = position
        return position

    def read(self, size=-1):
        if self.closed:
            raise ValueError("Split ZIP reader is closed")
        if size is None or size < 0:
            size = self._bounds[-1] - self._pos
        if type(size) is not int or size < 0 or size > 8 * CHUNK:
            raise ValueError("Unbounded split ZIP read refused")
        remain = min(size, self._bounds[-1] - self._pos)
        blocks = []
        while remain:
            index = bisect_right(self._bounds, self._pos) - 1
            if index < 0 or index >= len(self._paths):
                raise ValueError("Split ZIP segment index invalid")
            if self._active_index != index:
                if self._active is not None:
                    self._active.close()
                self._active = self._paths[index].open("rb")
                self._active_index = index
            position = self._pos - self._bounds[index]
            length = min(remain, self._bounds[index + 1] - self._pos)
            self._active.seek(position)
            block = self._active.read(length)
            if len(block) != length:
                raise ValueError("Split ZIP part shortened during verification")
            blocks.append(block)
            self._pos += length
            remain -= length
        return b"".join(blocks)

    def close(self):
        try:
            if self._active is not None:
                self._active.close()
        finally:
            self._active = None
            super().close()


def _delivery(root: Path):
    try:
        data = _object(json.loads(_read_small(root / "delivery.json", MAX_METADATA)), "delivery.json")
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid local delivery manifest") from exc
    code = data.get("version_code")
    if (data.get("schema") != 1 or data.get("package") != PACKAGE
            or type(code) is not str or re.fullmatch(r"[1-9][0-9]*", code) is None
            or data.get("companion_required") is not True
            or data.get("transport_only_parts") is not True
            or data.get("device_install_verified") is not False):
        raise ValueError("Delivery identity/companion contract invalid")
    obb = "main." + code + "." + PACKAGE + ".obb"
    wanted = [APK, obb, XAPK]
    rows = data.get("files")
    if type(rows) is not list or len(rows) != 3:
        raise ValueError("Delivery must contain exactly APK, OBB, XAPK")
    expected_sums = []
    parsed = []
    all_names = set()
    for row, filename in zip(rows, wanted):
        row = _object(row, "logical output")
        if (row.get("name") != filename or type(row.get("bytes")) is not int
                or row["bytes"] <= 0 or not _sha(row.get("sha256"))):
            raise ValueError("Delivery logical record mismatch")
        inputs = row.get("parts")
        if type(inputs) is not list or not 1 <= len(inputs) <= MAX_PARTS:
            raise ValueError("Delivery part count invalid")
        assembled = []
        total = 0
        for i, part in enumerate(inputs, 1):
            part = _object(part, "transport part")
            name = filename if len(inputs) == 1 else filename + ".part" + str(i).zfill(3)
            size, digest = part.get("bytes"), part.get("sha256")
            if (part.get("name") != name or not _safe_name(name) or name in all_names
                    or type(size) is not int or not 0 < size <= MAX_PART_BYTES
                    or not _sha(digest)):
                raise ValueError("Invalid or repeated transport part metadata")
            assembled.append((root / name, size, digest))
            all_names.add(name)
            expected_sums.append(digest + "  " + name + "\n")
            total += size
        if total != row["bytes"] or (len(assembled) == 1
                                      and assembled[0][2] != row["sha256"]):
            raise ValueError("Delivery whole/part metadata inconsistent")
        parsed.append((row, assembled))
    try:
        sums = _read_small(root / "SHA256SUMS", MAX_METADATA).decode("ascii")
    except UnicodeError as exc:
        raise ValueError("Non-ASCII SHA256SUMS") from exc
    if sums != "".join(expected_sums):
        raise ValueError("SHA256SUMS differs from delivery metadata")
    return code, obb, parsed


def verify(root: Path) -> dict:
    """Verify SHA256 on every actual transport part AND nested APK/OBB bytes."""
    code, obb, records = _delivery(root)
    for row, parts in records:
        _hash_parts(parts, row["bytes"], row["sha256"])
    xapk_parts = records[2][1]
    expected = [("manifest.json", None),
                (PACKAGE + ".apk", records[0][0]),
                ("Android/obb/" + PACKAGE + "/" + obb, records[1][0])]
    with SplitZipReader([(p, length) for p, length, _ in xapk_parts]) as reader:
        try:
            with zipfile.ZipFile(reader, "r", allowZip64=True) as archive:
                entries = archive.infolist()
                if len(entries) != len(expected):
                    raise ValueError("Unexpected XAPK member count")
                for info, (wanted, _) in zip(entries, expected):
                    mode = (info.external_attr >> 16) & 0xffff
                    if (info.filename != wanted or info.is_dir()
                            or info.compress_type != zipfile.ZIP_STORED
                            or info.compress_size != info.file_size
                            or info.flag_bits & 1
                            or (info.create_system == 3 and (mode & 0o170000) == 0o120000)):
                        raise ValueError("Unexpected or unsafe XAPK member identity")
                if not 0 < entries[0].file_size <= MAX_XAPK_MANIFEST:
                    raise ValueError("XAPK manifest exceeds bound")
                manifest = _object(json.loads(archive.read(entries[0])), "XAPK manifest")
                expansion = expected[2][0]
                if (manifest.get("xapk_version") != 1
                        or manifest.get("package_name") != PACKAGE
                        or manifest.get("version_code") != code
                        or manifest.get("total_size") != records[0][0]["bytes"] + records[1][0]["bytes"]
                        or manifest.get("expansions") != [{
                            "file": expansion,
                            "install_location": "EXTERNAL_STORAGE",
                            "install_path": expansion,
                        }]):
                    raise ValueError("XAPK nested manifest differs from delivery identity")
                for info, (_, row) in zip(entries[1:], expected[1:]):
                    if info.file_size != row["bytes"]:
                        raise ValueError("Nested XAPK member length differs from loose output")
                    observed = hashlib.sha256()
                    size = 0
                    with archive.open(info, "r") as stream:
                        for block in iter(lambda: stream.read(CHUNK), b""):
                            observed.update(block)
                            size += len(block)
                    if size != row["bytes"] or observed.hexdigest() != row["sha256"]:
                        raise ValueError("Nested XAPK APK/OBB SHA256 differs from loose delivery")
        except (zipfile.BadZipFile, EOFError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid XAPK ZIP or nested manifest structure") from exc
    return {
        "package_name": PACKAGE,
        "version_code": code,
        "actual_logical_output_sha256_verified": 3,
        "actual_transport_parts_verified": sum(len(parts) for _, parts in records),
        "actual_xapk_stored_members_verified": 3,
        "nested_apk_obb_sha256_match_loose_delivery": True,
        "needs_multi_gigabyte_assembly_or_extraction": False,
        "manifest_authenticated_independently": False,
        "apk_signature_checked": False,
        "obb_mounted_on_android": False,
        "device_verified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--delivery-root", type=Path, required=True)
    args = p.parse_args()
    print("T5_XAPK_CROSS_DELIVERY " + json.dumps(verify(args.delivery_root), sort_keys=True))


if __name__ == "__main__":
    main()
