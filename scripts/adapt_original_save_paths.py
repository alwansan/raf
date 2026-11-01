"""Pinned original save-path portability; no save schema or identity replacement."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

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
    paths = list((project / 'Assets').rglob('SaveAndLoad.cs'))
    if len(paths) != 1:
        raise ValueError('Require one original SaveAndLoad source')
    path = paths[0]
    meta = path.with_suffix('.cs.meta')
    if path.is_symlink() or meta.is_symlink() or not meta.is_file():
        raise ValueError('Require original regular source and meta')
    raw, metadata = path.read_bytes(), meta.read_bytes()
    text = raw.decode('utf-8-sig')
    result = adapt(text)
    changed = text != result
    if write and changed:
        if backup.resolve().is_relative_to(project.resolve()):
            raise ValueError('Backup must remain outside imported project')
        if any((backup / p.name).exists() for p in (path, meta)):
            raise ValueError('Refuse original backup overwrite')
        backup.mkdir(parents=True, exist_ok=True)
        for source in (path, meta):
            shutil.copy2(source, backup / source.name)
        encoded = result.encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            encoded = b'\xef\xbb\xbf' + encoded
        try:
            path.write_bytes(encoded)
            if meta.read_bytes() != metadata or path.read_bytes() != encoded:
                raise ValueError('Installed source or original meta changed')
        except Exception:
            path.write_bytes(raw)
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
