"""Join lossless Release download parts: python reassemble.py Raft-Android-Test.xapk"""
import hashlib
import os
import json
from pathlib import Path
import shutil
import sys


def safe_name(name):
    return isinstance(name,str) and name not in ('','.','..') and Path(name).name==name and '/' not in name and '\\' not in name and ':' not in name


def reassemble(root, name):
    data=json.loads((root/'delivery.json').read_text())
    row=next((r for r in data['files'] if r['name']==name),None)
    if not row or not safe_name(name): raise ValueError('Unknown delivery file')
    parts=row['parts']
    if not parts or len({p['name'] for p in parts})!=len(parts): raise ValueError('Invalid part list')
    for part in parts:
        if not safe_name(part['name']): raise ValueError('Unsafe part name')
        path=root/part['name']
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=part['bytes']:
            raise ValueError('A required part is missing or has the wrong size')
        with path.open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()!=part['sha256']:
                raise ValueError('Download part SHA256 mismatch')
    output=root/name
    if len(parts)==1 and parts[0]['name']==name:
        if parts[0]['sha256']!=row['sha256'] or parts[0]['bytes']!=row['bytes']:
            raise ValueError('Complete-file metadata mismatch')
        return output
    # Never overwrite a pre-existing destination, including a dangling symlink.
    if output.exists() or output.is_symlink(): raise ValueError('Refusing to overwrite output')
    temporary=root/(name+'.assembling')
    # An interrupted prior assembly belongs to the user; do not delete it.
    if temporary.exists() or temporary.is_symlink():
        raise ValueError('Existing assembly temporary file')
    # A multi-gigabyte Android download must not fill the phone before discovering
    # that the complete destination cannot fit. Free space can still change later.
    if shutil.disk_usage(root).free < row['bytes']:
        raise ValueError('Insufficient free disk for assembly')
    # Android/Termux Python builds may not expose os.link at all. Keep the
    # existing hard-link path unchanged where it is available: that is the
    # only path with atomic complete-file publication. In the absent-link
    # fallback, create the final name EXCLUSIVELY, never with rename('replace').
    # A process killed without Python cleanup can leave an incomplete final
    # pathname, so this fallback is no-clobber, not atomic-visibility.
    if not callable(getattr(os, 'link', None)):
        digest = hashlib.sha256()
        size = 0
        owned_inode = None
        try:
            try:
                with output.open('xb') as target:
                    owner = os.fstat(target.fileno())
                    owned_inode = (owner.st_dev, owner.st_ino)
                    for part in parts:
                        with (root / part['name']).open('rb') as source:
                            for block in iter(lambda: source.read(1024 * 1024), b''):
                                target.write(block)
                                digest.update(block)
                                size += len(block)
                    target.flush()
                    os.fsync(target.fileno())
            except FileExistsError as exc:
                raise ValueError('Refusing to overwrite output') from exc
            if size != row['bytes'] or digest.hexdigest() != row['sha256']:
                raise ValueError('Assembled file SHA256 mismatch')
            return output
        except BaseException:
            # Remove only our own exclusive output, if its inode still matches.
            # This is best-effort cleanup, not a guarantee against power loss.
            if owned_inode is not None:
                try:
                    current = output.lstat()
                except FileNotFoundError:
                    pass
                else:
                    if (current.st_dev, current.st_ino) == owned_inode and not output.is_symlink():
                        output.unlink()
            raise

    digest=hashlib.sha256();size=0
    created=False
    try:
        with temporary.open('xb') as target:
            created=True
            for part in parts:
                with (root/part['name']).open('rb') as source:
                    for block in iter(lambda:source.read(1024*1024),b''):
                        target.write(block);digest.update(block);size+=len(block)
        if size!=row['bytes'] or digest.hexdigest()!=row['sha256']:
            raise ValueError('Assembled file SHA256 mismatch')
        if output.exists() or output.is_symlink():
            raise ValueError('Refusing to overwrite output')
        # A same-directory hard link is atomic and refuses to overwrite any
        # output published by another process after the existence check.
        # Path.rename() would clobber that output on POSIX.
        try:
            os.link(temporary, output)
        except FileExistsError as exc:
            raise ValueError('Refusing to overwrite output') from exc
        except OSError as exc:
            # Some Android shared-storage layers do not allow hard links.
            # Fail safely instead of silently replacing a signed file.
            raise OSError('Atomic publish requires a filesystem with hard-link support; reassemble in Termux home') from exc
        temporary.unlink()
    except Exception:
        if created and temporary.is_file() and not temporary.is_symlink():
            temporary.unlink()
        raise
    return output


if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: python reassemble.py <filename from delivery.json>')
    print(reassemble(Path(__file__).resolve().parent,sys.argv[1]))
