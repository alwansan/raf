"""Restore the vendor runtime Resources directory contract without changing assets/GUIDs."""
from pathlib import Path
import argparse
import hashlib
import re

NAME = re.compile(r'FMODStudioSettingsPlatform(?:_(?:[0-9]|1[0-3]))?\.asset')

def restore(project: Path, apply=False):
    root = project / 'Assets/Resources'
    target = root / 'FMODStudioSettings'
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError('Unsafe platform resource directory')
    if not (root / 'FMODStudioSettings.asset').is_file():
        raise ValueError('Original settings asset is missing')
    sources = sorted(p for p in root.glob('FMODStudioSettingsPlatform*.asset'))
    installed = sorted(target.glob('FMODStudioSettingsPlatform*.asset')) if target.exists() else []
    if not sources and len(installed) == 15:
        sources = installed
    if len(sources) != 15 or any(not NAME.fullmatch(p.name) for p in sources):
        raise ValueError('Expected exactly 15 known original platform assets')
    plan = []
    for source in sources:
        for path in (source, Path(str(source) + '.meta')):
            if not path.is_file() or path.is_symlink():
                raise ValueError('Original platform asset/meta is absent or unsafe')
            destination = target / path.name
            if destination != path and destination.exists():
                raise ValueError('Refusing existing platform resource destination')
            plan.append((path, destination, hashlib.sha256(path.read_bytes()).digest()))
    if apply:
        target.mkdir(exist_ok=True)
        moved = []
        try:
            for source, destination, digest in plan:
                if source != destination:
                    source.rename(destination)
                    moved.append((source, destination))
                if hashlib.sha256(destination.read_bytes()).digest() != digest:
                    raise ValueError('Platform resource bytes changed')
        except BaseException:
            for source, destination in reversed(moved):
                destination.rename(source)
            raise
    return {'platforms': 15, 'asset_meta_files': len(plan), 'applied': apply,
            'asset_and_meta_bytes_unchanged': True, 'settings_asset_changed': False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print('RAFT_FMOD_RESOURCE_LAYOUT', restore(args.project, args.apply))

if __name__ == '__main__':
    main()
