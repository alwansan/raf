"""Fail-closed, CPU-only original Haptics inventory audit (never copies assets).

Pins tracked original WAV Git blobs by name, length and Git OID.
This proves repository input fidelity, not Android paths or device success.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PREFIX = 'Raft/Raft_Data/StreamingAssets/Haptics/'
SHA = re.compile(r'[0-9a-f]{40}\Z')
# Immutable Git blob SHA of the original 29-WAV reference manifest.
PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA = '88df20f0c64ae5f46f057939d4d6d96773a33ef8'


class HapticsInventoryError(ValueError):
    pass


def _git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def verify_manifest_blob(manifest_path: Path, pinned_blob_sha: str):
    """Require the original source-of-truth manifest, not a co-edited one."""
    if not isinstance(pinned_blob_sha, str) or not SHA.fullmatch(pinned_blob_sha):
        raise HapticsInventoryError('Malformed trusted Haptics manifest pin')
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise HapticsInventoryError('Unsafe or absent Haptics manifest')
    payload = manifest_path.read_bytes()
    git_blob = hashlib.sha1(
        ('blob ' + str(len(payload))).encode('ascii') + b'\0' + payload
    ).hexdigest()
    if git_blob != pinned_blob_sha:
        raise HapticsInventoryError('Original Haptics manifest provenance changed')
    return payload


def audit(repo: Path, manifest_path: Path, expected_count=None, *,
          expected_manifest_blob_sha=None):
    repo = repo.resolve(strict=True)
    if expected_manifest_blob_sha is None:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    else:
        manifest = json.loads(
            verify_manifest_blob(manifest_path, expected_manifest_blob_sha).decode('utf-8'))
    if manifest.get('schema_version') != 1 or manifest.get('path_prefix') != PREFIX:
        raise HapticsInventoryError('Unexpected Haptics manifest schema/path')
    expected = manifest.get('files')
    if not isinstance(expected, dict) or not expected:
        raise HapticsInventoryError('Empty or malformed Haptics manifest')
    if expected_count is not None and len(expected) != expected_count:
        raise HapticsInventoryError('Haptics manifest count changed')
    seen_lower = set()
    for name, item in expected.items():
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+\.wav', name):
            raise HapticsInventoryError('Unsafe Haptics manifest filename')
        if name.lower() in seen_lower:
            raise HapticsInventoryError('Haptics manifest contains case aliases')
        seen_lower.add(name.lower())
        if (not isinstance(item, dict) or set(item) != {'git_blob_sha', 'bytes'}
                or not isinstance(item['git_blob_sha'], str)
                or not SHA.fullmatch(item['git_blob_sha'])
                or type(item['bytes']) is not int or item['bytes'] <= 0):
            raise HapticsInventoryError('Malformed Haptics manifest entry')

    raw = _git(repo, 'ls-tree', '-rlz', 'HEAD', '--', PREFIX)
    found = {}
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        try:
            meta, raw_name = entry.split(b'\t', 1)
            mode, kind, oid, size = meta.decode('ascii').split()
            path = raw_name.decode('utf-8')
        except (ValueError, UnicodeDecodeError) as exc:
            raise HapticsInventoryError('Unparseable tracked Haptics entry') from exc
        if not path.startswith(PREFIX) or mode != '100644' or kind != 'blob':
            raise HapticsInventoryError('Unexpected Haptics file type/path')
        name = path[len(PREFIX):]
        if name in found:
            raise HapticsInventoryError('Duplicate tracked Haptics path')
        found[name] = (oid, int(size))
    if set(found) != set(expected):
        raise HapticsInventoryError('Tracked Haptics paths differ from original manifest')

    root = (repo / PREFIX).resolve(strict=True)
    total = 0
    for name, entry in expected.items():
        if found[name] != (entry['git_blob_sha'], entry['bytes']):
            raise HapticsInventoryError('Haptics Git blob or length differs from manifest')
        source = repo / PREFIX / name
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root):
            raise HapticsInventoryError('Unsafe or missing Haptics worktree file')
        if source.stat().st_size != entry['bytes']:
            raise HapticsInventoryError('Haptics worktree length differs from manifest')
        actual = _git(repo, 'hash-object', '--', PREFIX + name).decode('ascii').strip()
        if actual != entry['git_blob_sha']:
            raise HapticsInventoryError('Haptics worktree content differs from committed blob')
        total += entry['bytes']
    return {'tracked_wavs': len(expected), 'total_source_bytes': total,
            'original_manifest_and_worktree_match': True,
            'runtime_apk_obb_path_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--expected-count', type=int, default=29)
    parser.add_argument('--expected-manifest-blob', default=PINNED_ORIGINAL_HAPTICS_MANIFEST_BLOB_SHA,
                        help='Trusted Git object SHA for original manifest; not derived from mutable working tree')
    args = parser.parse_args()
    print('RAFT_HAPTICS_SOURCE_AUDIT ' + json.dumps(
        audit(args.repo, args.manifest, args.expected_count,
              expected_manifest_blob_sha=args.expected_manifest_blob), sort_keys=True))


if __name__ == '__main__':
    main()
