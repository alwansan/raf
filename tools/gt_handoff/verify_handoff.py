#!/usr/bin/env python3
"""Verify preserved repository bytes and historical receipts; never run Unity."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = 'clients/GT/sessions/20261126-complete-handoff/MANIFEST.json'


def physical(relative):
    part = Path(relative)
    if part.is_absolute() or '..' in part.parts:
        raise ValueError('unsafe_handoff_path')
    path = ROOT / part
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('handoff_path_outside_repository')
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('handoff_file_missing_or_symlink: ' + relative)
    return path


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def verify(manifest):
    document = json.loads(manifest.read_text(encoding='utf-8'))
    if document.get('schema_version') != 1 or not document.get('files'):
        raise ValueError('invalid_handoff_manifest')
    paths = [row['path'] for row in document['files']]
    if len(paths) != len(set(paths)):
        raise ValueError('duplicate_handoff_paths')
    for row in document['files'] + document.get('existing_repository_references', []):
        data = physical(row['path']).read_bytes()
        if len(data) != row['bytes'] or fingerprint(data) != row['sha256']:
            raise ValueError('handoff_bytes_mismatch: ' + row['path'])
    base = manifest.parent
    log_index = json.loads((base / 'tests/historical-test-logs-manifest.json').read_text())
    archive = base / 'tests' / log_index['archive']
    if fingerprint(archive.read_bytes()) != log_index['sha256']:
        raise ValueError('historical_archive_mismatch')
    with zipfile.ZipFile(archive) as stream:
        if stream.testzip() is not None:
            raise ValueError('historical_archive_crc_error')
        if set(stream.namelist()) != {row['member'] for row in log_index['members']}:
            raise ValueError('historical_archive_population_mismatch')
        for row in log_index['members']:
            data = stream.read(row['member'])
            if len(data) != row['bytes'] or fingerprint(data) != row['sha256']:
                raise ValueError('historical_member_mismatch')
    artifact_members = 0
    for path in (base / 'evidence/actions').rglob('artifact-provenance.json'):
        for row in json.loads(path.read_text())['members']:
            data = physical(row['path']).read_bytes()
            if len(data) != row['bytes'] or fingerprint(data) != row['sha256']:
                raise ValueError('artifact_member_mismatch')
            artifact_members += 1
    missing = json.loads((base / 'inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json').read_text())
    return dict(status='AVAILABLE_HANDOFF_BYTES_VERIFIED', file_count=len(paths),
                historical_log_members=len(log_index['members']),
                preserved_action_artifact_members=artifact_members,
                declared_unavailable_historical_batches=len(missing['items']),
                unavailable_bytes_claimed_uploaded=False,
                restoration_complete=False, Unity_run_executed=False,
                XAPK_requested=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default=DEFAULT)
    args = parser.parse_args()
    print(json.dumps(verify(physical(args.manifest)), sort_keys=True))


if __name__ == '__main__':
    main()
