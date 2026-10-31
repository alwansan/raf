"""Stage original CIL for AssetRipper without an ambiguous PlayFab provider.

Original files are retained. Unknown duplicate CLR identities fail before copying.
This is an exporter-input correction, separate from runtime plugin selection.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil


def assembly_identity(path):
    import dnfile
    pe = dnfile.dnPE(str(path))
    try:
        if pe.net is None or not pe.net.mdtables.Assembly or len(pe.net.mdtables.Assembly.rows) != 1:
            raise ValueError('Expected an original managed assembly provider')
        row = pe.net.mdtables.Assembly.rows[0]
        return (str(row.Name), row.MajorVersion, row.MinorVersion, row.BuildNumber,
                row.RevisionNumber, str(row.Culture), bytes(row.PublicKey.value))
    finally:
        pe.close()


def select_providers(identities):
    if 'PlayFab_o.dll' in identities and (identities.get('PlayFab.dll') != identities['PlayFab_o.dll'] or
                                        identities['PlayFab_o.dll'][0] != 'PlayFab'):
        raise ValueError('Known alias does not match its canonical original CLR identity')
    groups = defaultdict(list)
    for name, identity in identities.items():
        groups[identity].append(name)
    selected, excluded = [], []
    for identity, names in groups.items():
        if len(names) == 1:
            selected.extend(names)
        elif identity[0] == 'PlayFab' and set(names) == {'PlayFab.dll', 'PlayFab_o.dll'}:
            selected.append('PlayFab.dll')
            excluded.append('PlayFab_o.dll')
        else:
            raise ValueError('Unexpected duplicate CLR assembly identity; no input staged')
    return sorted(selected), sorted(excluded)


def digest(path):
    with path.open('rb') as data:
        return hashlib.file_digest(data, 'sha256').hexdigest()


def stage(source, destination, identity_reader=assembly_identity):
    paths = sorted(source.glob('*.dll'))
    if not paths or any(p.is_symlink() or not p.is_file() for p in paths):
        raise ValueError('Original managed input is missing or unsafe')
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise FileExistsError('Exporter assembly destination must be empty')
    if source.resolve() == destination.resolve():
        raise ValueError('Cannot replace original managed providers')
    identities = {p.name: identity_reader(p) for p in paths}
    selected, excluded = select_providers(identities)
    before = {p.name: digest(p) for p in paths}
    destination.mkdir(parents=True, exist_ok=True)
    for name in selected:
        shutil.copy2(source / name, destination / name)
        if digest(destination / name) != before[name]:
            raise ValueError('Staged original managed provider changed')
    if any(digest(p) != before[p.name] for p in paths):
        raise ValueError('Original managed source changed during staging')
    report = {'original_providers': len(paths), 'staged_providers': len(selected),
              'known_duplicate_providers_excluded_from_export_input': len(excluded),
              'unexpected_duplicate_identities': 0, 'original_source_files_unchanged': True}
    print('RAFT_EXPORT_MANAGED_PROVIDERS ' + json.dumps(report, sort_keys=True), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    stage(args.source, args.destination)
