#!/usr/bin/env python3
"""Extract one verified Git LFS resource directly from a locally supplied RAR5 archive.

No GitHub LFS downloads, external tools, Windows DLL execution, or public uploads.
Requires Linux libarchive (libarchive.so.13) and a regular Git LFS pointer file.
"""
import argparse
import ctypes
import hashlib
from pathlib import Path
import re

def open_libarchive():
    lib = ctypes.CDLL("libarchive.so.13")
    lib.archive_read_new.restype = ctypes.c_void_p
    lib.archive_read_support_filter_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_support_format_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_open_filename.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.archive_read_next_header.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    lib.archive_entry_pathname.argtypes = [ctypes.c_void_p]
    lib.archive_entry_pathname.restype = ctypes.c_char_p
    lib.archive_entry_size.argtypes = [ctypes.c_void_p]
    lib.archive_entry_size.restype = ctypes.c_int64
    lib.archive_read_data.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    lib.archive_read_data.restype = ctypes.c_ssize_t
    lib.archive_read_data_skip.argtypes = [ctypes.c_void_p]
    lib.archive_read_free.argtypes = [ctypes.c_void_p]
    lib.archive_error_string.argtypes = [ctypes.c_void_p]
    lib.archive_error_string.restype = ctypes.c_char_p
    return lib

def read_pointer(path):
    data = path.read_text(encoding="ascii")
    if not data.startswith("version https://git-lfs.github.com/spec/v1\n"):
        raise ValueError("Expected a Git LFS text pointer, not actual game data")
    sha = re.search(r"^oid sha256:([a-f0-9]{64})$", data, re.M)
    size = re.search(r"^size (\d+)$", data, re.M)
    if not sha or not size:
        raise ValueError("Malformed LFS pointer")
    return sha.group(1), int(size.group(1))

def extract(archive_path, pointer_path, target_path, destination):
    if target_path.is_absolute() or ".." in target_path.parts:
        raise ValueError("Target must be a safe relative path")
    if len(target_path.parts) < 3 or tuple(target_path.parts[:2]) != ("Raft", "Raft_Data"):
        raise ValueError("Only Raft/Raft_Data objects may be extracted")
    expected_sha, expected_size = read_pointer(pointer_path)
    if expected_size > 2_500_000_000:
        raise ValueError("Individual object exceeds 2.5GB safety limit")
    if destination.exists():
        raise FileExistsError("Destination exists; refusing to overwrite")
    if not destination.parent.is_dir():
        raise ValueError("Destination parent directory must already exist")

    lib = open_libarchive()
    ar = lib.archive_read_new()
    lib.archive_read_support_filter_all(ar)
    lib.archive_read_support_format_all(ar)
    digest = hashlib.sha256()
    found = False
    try:
        if lib.archive_read_open_filename(ar, str(archive_path).encode(), 10240) != 0:
            raise RuntimeError(lib.archive_error_string(ar))
        while True:
            entry = ctypes.c_void_p()
            rc = lib.archive_read_next_header(ar, ctypes.byref(entry))
            if rc == 1:
                break
            if rc < 0:
                raise RuntimeError(lib.archive_error_string(ar))
            name = lib.archive_entry_pathname(entry).decode("utf8", "replace").replace("\\", "/")
            if name != target_path.as_posix():
                if lib.archive_read_data_skip(ar) < 0:
                    raise RuntimeError(lib.archive_error_string(ar))
                continue
            if lib.archive_entry_size(entry) != expected_size:
                raise ValueError("RAR file size differs from tracked LFS pointer")
            buf = ctypes.create_string_buffer(1024 * 1024)
            total = 0
            try:
                with destination.open("xb") as out:
                    while True:
                        n = lib.archive_read_data(ar, buf, len(buf))
                        if n == 0:
                            break
                        if n < 0:
                            raise RuntimeError(lib.archive_error_string(ar))
                        chunk = buf.raw[:n]
                        total += n
                        if total > expected_size:
                            raise ValueError("Extracted content exceeds LFS size")
                        out.write(chunk)
                        digest.update(chunk)
                if total != expected_size or digest.hexdigest() != expected_sha:
                    raise ValueError("Extracted data does not match Git LFS size + SHA256")
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            found = True
            print("VERIFIED:", target_path.as_posix(), "bytes:", total, "sha256:", digest.hexdigest())
            break
        if not found:
            raise FileNotFoundError("Requested resource not found within RAR")
    finally:
        lib.archive_read_free(ar)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True, type=Path)
    p.add_argument("--lfs-pointer", required=True, type=Path)
    p.add_argument("--target", required=True, type=Path)
    p.add_argument("--destination", required=True, type=Path)
    a = p.parse_args()
    extract(a.archive, a.lfs_pointer, a.target, a.destination)
