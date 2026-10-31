#!/usr/bin/env python3
"""Read selected original serialized/CIL files from a supplied RAR, verifying Git identities.

Never extract or execute Windows native programs. The private plan is populated
from an exact Git tree and its small LFS pointer blobs; no archive paths are used
as output destinations unless they exactly match the prevalidated allowlist.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from scripts.extract_raft_lfs_from_rar import open_libarchive

ALLOWED = re.compile(r'^Raft/Raft_Data/(?:(?:sharedassets\d+|resources)\.assets(?:\.resS)?|'
                     r'level\d+(?:\.resS)?|globalgamemanagers(?:\.assets)?|boot\.config|Managed/[^/]+\.dll)$')


def extraction_plan(metadata):
    pointers = {item['path']: item['pointer'] for item in metadata['pointers']}
    plan = {}
    for row in metadata['files']:
        name = row['path']
        if not ALLOWED.fullmatch(name) or '..' in PurePosixPath(name).parts or name in plan:
            raise ValueError('Unsafe, unsupported or duplicate original source path')
        if not re.fullmatch(r'[a-f0-9]{40}', row['sha']):
            raise ValueError('Invalid Git blob identity')
        if name in pointers:
            pointer = pointers[name]
            raw = pointer.encode('ascii')
            actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            if actual != row['sha'] or len(raw) != row['size']:
                raise ValueError('Pointer does not match exact Git blob identity')
            oid = re.search(r'(?m)^oid sha256:([a-f0-9]{64})$', pointer)
            size = re.search(r'(?m)^size (\d+)$', pointer)
            if not pointer.startswith('version https://git-lfs.github.com/spec/v1\n') or not oid or not size:
                raise ValueError('Malformed original LFS pointer')
            plan[name] = {'size': int(size[1]), 'digest': oid[1], 'algorithm': 'sha256'}
        else:
            plan[name] = {'size': row['size'], 'digest': row['sha'], 'algorithm': 'git-sha1'}
        if not 0 <= plan[name]['size'] <= 2_500_000_000:
            raise ValueError('Original file exceeds extraction safety bound')
    return plan


def extract(archive, metadata, destination):
    plan = extraction_plan(metadata)
    if destination.exists():
        raise FileExistsError('Private extraction destination already exists')
    destination.mkdir(parents=True)
    lib = open_libarchive()
    ar = lib.archive_read_new()
    lib.archive_read_support_filter_all(ar)
    lib.archive_read_support_format_all(ar)
    found, total = set(), 0
    try:
        if lib.archive_read_open_filename(ar, str(archive).encode(), 10240) != 0:
            raise RuntimeError(lib.archive_error_string(ar))
        while True:
            entry = ctypes.c_void_p()
            status = lib.archive_read_next_header(ar, ctypes.byref(entry))
            if status == 1:
                break
            if status < 0:
                raise RuntimeError(lib.archive_error_string(ar))
            name = lib.archive_entry_pathname(entry).decode('utf8', 'replace').replace('\\', '/')
            if name not in plan:
                if lib.archive_read_data_skip(ar) < 0:
                    raise RuntimeError(lib.archive_error_string(ar))
                continue
            if name in found:
                raise ValueError('Duplicate archive source entry')
            expected = plan[name]
            if lib.archive_entry_size(entry) != expected['size']:
                raise ValueError('Original archive size differs from repository identity')
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256() if expected['algorithm'] == 'sha256' else hashlib.sha1()
            if expected['algorithm'] == 'git-sha1':
                digest.update(b'blob ' + str(expected['size']).encode() + b'\0')
            written = 0
            buffer = ctypes.create_string_buffer(1024 * 1024)
            try:
                with target.open('xb') as out:
                    while True:
                        count = lib.archive_read_data(ar, buffer, len(buffer))
                        if count == 0:
                            break
                        if count < 0:
                            raise RuntimeError(lib.archive_error_string(ar))
                        written += count
                        if written > expected['size']:
                            raise ValueError('Extraction exceeds declared original size')
                        chunk = buffer.raw[:count]
                        digest.update(chunk)
                        out.write(chunk)
                if written != expected['size'] or digest.hexdigest() != expected['digest']:
                    raise ValueError('Original bytes do not match repository checksum')
            except Exception:
                target.unlink(missing_ok=True)
                raise
            found.add(name)
            total += written
            if len(found) % 20 == 0 or written > 90_000_000:
                print('Verified original files:', len(found), 'bytes:', total, flush=True)
        if found != set(plan):
            raise ValueError('Archive did not contain all requested original sources')
    finally:
        lib.archive_read_free(ar)
    report = {'verified_files': len(found), 'verified_bytes': total,
              'lfs_objects_recovered_without_lfs': sum(p['algorithm'] == 'sha256' for p in plan.values()),
              'native_windows_programs_executed': 0}
    print('RAFT_PRIVATE_ARCHIVE_RECOVERY ' + json.dumps(report, sort_keys=True), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    extract(args.archive, json.loads(args.metadata.read_text()), args.destination)

