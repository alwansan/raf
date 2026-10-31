"""Pin transient AssetRipper configuration to source export, preserving script GUID model."""
import argparse
import json
from pathlib import Path


def configure(directory):
    target = directory / 'AssetRipper.Settings.json'
    if target.exists():
        raise FileExistsError('Refusing to replace existing AssetRipper settings')
    # Pinned v1.0.1 source enum: Decompiled=0, Hybrid=1.
    settings = {'Import': {}, 'Processing': {}, 'Export': {'ScriptExportMode': 0}}
    with target.open('x', encoding='utf8') as output:
        json.dump(settings, output, indent=2)
    return settings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    configure(args.directory)
