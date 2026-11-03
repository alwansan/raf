"""Stage W1's four original shader owners from pinned ZIP2, without Git LFS."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ZIP2_SHA = '15964ea8f246b6e076ce26b60931ee2e1a9a2385'
PINS = {
    'Raft_Data/resources.assets': (111533516, '87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c'),
    'Raft_Data/sharedassets0.assets': (115978112, '0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3'),
    'Raft_Data/Resources/unity default resources': (4832808, '026e6d1d96dc2e28c72ece25f2419469d649a95e25b6929bc5cfc95bca529f8e'),
    'Raft_Data/Resources/unity_builtin_extra': (936628, '0eb8f0a4ea47b075a6b637abc02d0c7930d96cb9f6c5d723819eb8042cfb3886'),
}


def safe(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Redirected ZIP2 input/output')


def fingerprint(path):
    sha = hashlib.sha256()
    total = 0
    with path.open('rb') as f:
        while data := f.read(2 * 1024 * 1024):
            total += len(data)
            sha.update(data)
    return total, sha.hexdigest()


def stage(root, destination, pins=PINS):
    root, destination = Path(root).absolute(), Path(destination).absolute()
    safe(root)
    safe(destination)
    if destination.is_relative_to(root):
        raise ValueError('ZIP2 source cannot be an output')
    manifest = root / 'RAFT_FILE_MANIFEST.tsv'
    safe(manifest)
    if manifest.stat().st_size > 1024 * 1024:
        raise ValueError('Oversized ZIP2 manifest')
    with manifest.open(newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        if reader.fieldnames != ['kind', 'bytes', 'sha256', 'mode', 'relative_path_under_Raft']:
            raise ValueError('ZIP2 manifest schema drift')
        rows = list(reader)
    results = []
    for relative, pin in pins.items():
        if relative not in PINS and pins is PINS:
            raise ValueError('Unpinned source')
        hits = [r for r in rows if r['relative_path_under_Raft'] == relative]
        if len(hits) != 1 or (hits[0]['bytes'], hits[0]['sha256']) != (str(pin[0]), pin[1]):
            raise ValueError('Manifest does not match independent original pin')
        source, output = root / 'Raft' / relative, destination / relative
        safe(source)
        safe(output)
        if output.exists():
            if not output.is_file() or fingerprint(output) != pin:
                raise ValueError('Existing output conflicts with original pin')
            results.append({'verified_bytes': pin[0], 'sha256': pin[1], 'cache_hit': True})
            continue
        if hits[0]['kind'] == 'plain' and source.is_file():
            inputs = [source]
        elif hits[0]['kind'] == 'split' and source.is_dir():
            children = sorted(source.iterdir())
            inputs = [p for p in children if p.name != 'README.txt']
            if not inputs or any(p.name != 'part-%05d' % i for i, p in enumerate(inputs)):
                raise ValueError('Missing or unexpected ZIP2 chunks')
        else:
            raise ValueError('ZIP2 source kind mismatch')
        for p in inputs:
            safe(p)
            if not p.is_file():
                raise ValueError('ZIP2 chunk is not a regular file')
        if sum(p.stat().st_size for p in inputs) != pin[0]:
            raise ValueError('ZIP2 source size mismatch')
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as f:
                temporary = Path(f.name)
                for p in inputs:
                    with p.open('rb') as source_file:
                        while data := source_file.read(2 * 1024 * 1024):
                            f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if fingerprint(temporary) != pin:
                raise ValueError('Reconstructed original SHA256 mismatch')
            os.link(temporary, output)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        results.append({'verified_bytes': pin[0], 'sha256': pin[1], 'cache_hit': False})
    return {'provider_sha': ZIP2_SHA, 'owners': results,
            'verified_bytes': sum(r['verified_bytes'] for r in results), 'lfs_used': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip2-checkout', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    args = p.parse_args()
    actual = subprocess.check_output(['git', '-C', str(args.zip2_checkout), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != ZIP2_SHA:
        raise ValueError('ZIP2 checkout commit mismatch')
    print('RAFT_W1_ZIP2_STAGE ' + json.dumps(stage(args.zip2_checkout, args.destination), sort_keys=True))
