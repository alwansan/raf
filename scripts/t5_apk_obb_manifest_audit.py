#!/usr/bin/env python3
"""Read-only APK/main OBB pairing audit; never extracts game assets."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

PACKAGE = re.compile(r"^package:\s+name='([^']+)'\s+versionCode='([0-9]+)'", re.M)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def apk_identity(apk, aapt):
    proc = subprocess.run([aapt, 'dump', 'badging', str(apk)], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=45, check=False)
    if proc.returncode:
        raise RuntimeError('aapt dump badging failed: ' + proc.stderr[:300])
    match = PACKAGE.search(proc.stdout)
    if not match:
        raise RuntimeError('Cannot verify APK package/versionCode from aapt output')
    return match.group(1), int(match.group(2))


def inspect(apk, obb, aapt, expected_obb_sha=None, verify_zip=False):
    errors = []
    if not apk.is_file() or not obb.is_file():
        raise FileNotFoundError('Both APK and OBB must be readable files')
    with zipfile.ZipFile(apk) as z:
        if 'AndroidManifest.xml' not in z.namelist():
            errors.append('APK has no AndroidManifest.xml')
        if verify_zip and z.testzip() is not None:
            errors.append('APK ZIP CRC mismatch')
    package, version = apk_identity(apk, aapt)
    expected_name = f'main.{version}.{package}.obb'
    if obb.name != expected_name:
        errors.append(f'OBB filename mismatch: expected {expected_name}')
    obb_sha = sha256_file(obb)
    if expected_obb_sha and obb_sha.lower() != expected_obb_sha.lower():
        errors.append('OBB SHA256 differs from supplied trusted digest')
    if verify_zip:
        try:
            with zipfile.ZipFile(obb) as z:
                if z.testzip() is not None:
                    errors.append('OBB ZIP CRC mismatch (entry redacted)')
        except zipfile.BadZipFile:
            errors.append('OBB is not ZIP; cannot CRC-check (may be opaque)')
    return {
        'schema': 't5-apk-obb-audit-v1',
        'package': package, 'versionCode': version,
        'apk': {'filename': apk.name, 'bytes': apk.stat().st_size,
                'sha256': sha256_file(apk)},
        'obb': {'filename': obb.name, 'bytes': obb.stat().st_size,
                'sha256': obb_sha},
        'expected_main_obb_filename': expected_name,
        'signed_apk_certificate_verified': False,
        'obb_resource_load_verified': False,
        'errors': errors,
        'pair_filename_and_optional_digest_pass': not errors,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apk', type=pathlib.Path, required=True)
    p.add_argument('--obb', type=pathlib.Path, required=True)
    p.add_argument('--aapt', default='aapt')
    p.add_argument('--expected-obb-sha256', default=None)
    p.add_argument('--verify-zip-crc', action='store_true')
    args = p.parse_args(argv)
    if args.expected_obb_sha256 and not re.fullmatch('[0-9a-fA-F]{64}', args.expected_obb_sha256):
        p.error('expected OBB SHA256 must be 64 hex characters')
    try:
        result = inspect(args.apk, args.obb, args.aapt, args.expected_obb_sha256,
                         args.verify_zip_crc)
    except (OSError, RuntimeError, zipfile.BadZipFile, subprocess.TimeoutExpired) as e:
        print(json.dumps({'schema': 't5-apk-obb-audit-v1', 'error': str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not result['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
