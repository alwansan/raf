"""Pinned original save-path portability; no save schema or identity replacement."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

ORIGINAL = 'b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb'
SUFFIX = ".Replace('\\\\', System.IO.Path.DirectorySeparatorChar)"
# Match comments too, so quoted comment text is never rewritten as an expression.
TOKENS = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"')
EXPECTED = Counter({'\\User\\User_': 2, '\\Player\\': 1, 'World\\': 1,
                    'Player\\': 1, '\\': 9, '\\User': 1, '-Latest\\': 1})


def fingerprint(text):
    return hashlib.sha256(text.replace('\r\n', '\n').encode()).hexdigest()


def adapt(text, expected=ORIGINAL, inventory=EXPECTED):
    if SUFFIX in text:
        original = text.replace(SUFFIX, '')
        result = adapt(original, expected, inventory)
        if result != text:
            raise ValueError('Unexpected existing path adaptation')
        return result
    if fingerprint(text) != expected:
        raise ValueError('Unknown original SaveAndLoad revision')
    observed = Counter()
    def replace(match):
        token = match.group()
        if not token.startswith('"'):
            return token
        value = json.loads(token)
        if '\\' not in value:
            return token
        observed[value] += 1
        return token + SUFFIX
    result = TOKENS.sub(replace, text)
    if observed != inventory:
        raise ValueError('Unexpected original path literals; no mutation permitted')
    if result.replace(SUFFIX, '') != text:
        raise ValueError('Non-path original source changed')
    return result


def apply(project, backup, write=False):
    # Both source and backup roots must be physical paths, including parents.
    # Assets.is_symlink() alone misses a symlinked project (and its descendants);
    # resolve().is_relative_to() alone misses a linked backup outside project.
    if any(node.is_symlink() for node in (project, *project.parents)):
        raise ValueError('Unsafe redirected Unity project root')
    if any(node.is_symlink() for node in (backup, *backup.parents)):
        raise ValueError('Unsafe redirected original backup root')
    # Only the decompiled game assembly is authoritative. SDKs may contain a
    # different SaveAndLoad.cs; never adapt an SDK homonym or mark it ambiguous.
    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Unsafe Unity Assets root')
    paths = [path for path in assets.rglob('SaveAndLoad.cs')
             if 'Assembly-CSharp' in path.parts]
    if len(paths) != 1:
        raise ValueError('Require one original SaveAndLoad source')
    path = paths[0]
    meta = path.with_suffix('.cs.meta')
    if path.is_symlink() or meta.is_symlink() or not path.is_file() or not meta.is_file():
        raise ValueError('Require original regular source and meta')
    parent = path.parent
    while parent != assets:
        if parent.is_symlink():
            raise ValueError('Unsafe linked original SaveAndLoad parent')
        if parent == parent.parent:
            raise ValueError('Original save source outside Assets')
        parent = parent.parent
    raw, metadata = path.read_bytes(), meta.read_bytes()
    text = raw.decode('utf-8-sig')
    result = adapt(text)
    changed = text != result
    if write and changed:
        if backup.resolve().is_relative_to(project.resolve()):
            raise ValueError('Backup must remain outside imported project')
        # A previously published backup is not ours to overwrite or delete.
        # In particular, reject even dangling backup links and empty folders.
        if backup.is_symlink() or backup.exists():
            raise ValueError('Original backup already exists; refuse overwrite')
        if backup.parent.is_symlink():
            raise ValueError('Linked original backup parent is unsafe')
        backup.parent.mkdir(parents=True, exist_ok=True)
        # Stage both original files on the backup filesystem before publishing
        # a complete backup. A failed copy must leave the original untouched
        # and must not strand a half-created backup that prevents retry.
        stage = Path(tempfile.mkdtemp(prefix='.' + backup.name + '-stage-', dir=backup.parent))
        try:
            shutil.copy2(path, stage / path.name)
            shutil.copy2(meta, stage / meta.name)
            if (stage / path.name).read_bytes() != raw or (stage / meta.name).read_bytes() != metadata:
                raise ValueError('Original backup bytes changed during staging')
            if backup.is_symlink() or backup.exists():
                raise ValueError('Original backup appeared during staging')
            stage.rename(backup)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        encoded = result.encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            encoded = b'\xef\xbb\xbf' + encoded
        try:
            path.write_bytes(encoded)
            if meta.read_bytes() != metadata or path.read_bytes() != encoded:
                raise ValueError('Installed source or original meta changed')
        except Exception:
            # Keep the complete original backup if rollback cannot be verified;
            # delete only our own new backup after full rollback succeeds.
            rolled_back = False
            try:
                path.write_bytes(raw)
                rolled_back = path.read_bytes() == raw and meta.read_bytes() == metadata
            finally:
                if rolled_back:
                    shutil.rmtree(backup)
            raise
    return dict(applied=write, changed=changed, pathExpressions=sum(EXPECTED.values()),
                originalMetaUnchanged=meta.read_bytes() == metadata,
                saveSchemaChanged=False, playerIdentityIntegrated=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--backup', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print('RAFT_ORIGINAL_SAVE_PATHS ' + json.dumps(apply(args.project, args.backup, args.apply), sort_keys=True))
