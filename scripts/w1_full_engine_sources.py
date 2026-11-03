"""Reuse authenticated ZIP2 payloads before selectively acquiring all shader owners."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import ZIP2_SHA, fingerprint, stage


def pins():
    return {'Raft_Data/' + name: pin for name, pin in SHADER_OWNERS.items()}


def acquisition_plan(destination):
    paths = ['RAFT_FILE_MANIFEST.tsv']
    missing = 0
    for relative, pin in pins().items():
        output = destination / relative
        if output.exists():
            if output.is_symlink() or fingerprint(output) != pin:
                raise ValueError('Conflicting cached original shader owner')
        else:
            paths.append('Raft/' + relative + ('/*' if pin[0] > 45 * 1024**2 else ''))
            missing += 1
    return paths, missing


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, required=True)
    p.add_argument('--zip2-checkout', type=Path)
    p.add_argument('--plan', action='store_true')
    a = p.parse_args()
    if a.plan:
        paths, missing = acquisition_plan(a.destination)
        with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
            out.write('paths<<W1_SHADER_OWNER_PATHS\n' + '\n'.join(paths) + '\nW1_SHADER_OWNER_PATHS\n')
        print('RAFT_W1_FULL_SHADER_PLAN ' + json.dumps({'owners': len(pins()), 'missing': missing,
                                                     'cached': len(pins()) - missing}))
    else:
        if a.zip2_checkout is None:
            raise ValueError('Pinned ZIP2 checkout required')
        actual = subprocess.check_output(['git', '-C', str(a.zip2_checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != ZIP2_SHA:
            raise ValueError('Pinned ZIP2 provider commit mismatch')
        result = stage(a.zip2_checkout, a.destination, pins())
        print('RAFT_W1_FULL_SHADER_SOURCE ' + json.dumps(result, sort_keys=True))
