"""Stage original tracked StreamingAssets with Git/LFS identity checks.

No game data is generated, decoded, normalized or published by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

MASTER_SHA = '10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339'
BANKS = {'MasterBank.bank', 'MasterBank.strings.bank', 'VO_logs_english.bank',
         'VO_npc_english.bank', 'VO_olof_english.bank'}


def sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def stage(repo, project, report_path, apply=False):
    prefix = 'Raft/Raft_Data/StreamingAssets/'
    raw = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-rz', 'HEAD', '--', prefix])
    plan = []
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.decode('utf-8').split('\t', 1)
        mode, kind, oid = metadata.split()
        relative = name.removeprefix(prefix)
        if (mode != '100644' or kind != 'blob' or not name.startswith(prefix)
                or '..' in Path(relative).parts or '\\' in relative):
            raise ValueError('Unexpected tracked StreamingAssets layout')
        source = repo / name
        if source.is_symlink() or not source.resolve().is_relative_to((repo / prefix).resolve()):
            raise ValueError('Unsafe source StreamingAssets path')
        identity = subprocess.check_output(['git', '-C', str(repo), 'cat-file', 'blob', oid])
        size = source.stat().st_size
        digest = sha256(source)
        if identity.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
            match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize (\d+)\n?', identity)
            if (not match or relative != 'MasterBank.bank' or match[1].decode() != MASTER_SHA
                    or int(match[2]) != 101600960 or size != 101600960 or digest != MASTER_SHA):
                raise ValueError('Original bank LFS identity/size/hash mismatch')
        else:
            actual_oid = subprocess.check_output(['git', '-C', str(repo), 'hash-object', '--', name], text=True).strip()
            if actual_oid != oid:
                raise ValueError('Original Git StreamingAssets content changed')
        target = project / 'Assets/StreamingAssets' / relative
        if target.is_symlink() or not target.resolve().is_relative_to(project.resolve()):
            raise ValueError('Unsafe destination StreamingAssets path')
        if target.exists() and (not target.is_file() or target.stat().st_size != size or sha256(target) != digest):
            raise ValueError('Existing original StreamingAssets conflict; no overwrite')
        plan.append((relative, source, target, size, digest))
    names = {row[0] for row in plan}
    if not BANKS <= names or 'Data.rgd' not in names:
        raise ValueError('Incomplete original audio/data StreamingAssets selection')
    if apply:
        for _, source, target, size, digest in plan:
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            if target.stat().st_size != size or sha256(target) != digest:
                raise ValueError('Staged original StreamingAssets verification failed')
    report = dict(applied=apply, files={name: dict(bytes=size, sha256=digest)
                  for name, _, _, size, digest in plan}, original_data_modified=False)
    report_path.write_text(json.dumps(report, sort_keys=True))
    print('RAFT_ORIGINAL_STREAMING_ASSETS ' + json.dumps(dict(
        applied=apply, files=len(plan), bank_files=len(BANKS),
        source_bytes=sum(row[3] for row in plan), original_data_modified=False,
        all_source_and_staged_hashes_verified=bool(apply)), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    stage(args.repo.resolve(), args.project.resolve(), args.report, args.apply)
