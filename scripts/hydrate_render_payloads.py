"""Fetch only tracked serialized/graphics LFS payloads, with a bounded authenticated plan."""
import argparse
import hashlib
import os
import stat
import tempfile
from pathlib import Path
import re
import subprocess

PATTERN = re.compile(r'Raft/Raft_Data/(?:resources\.assets(?:\.resS)?|sharedassets\d+\.assets(?:\.resS)?|level\d+\.resS|globalgamemanagers\.assets(?:\.resS)?)')

def pointer(data):
    text = data.decode('ascii')
    match = re.fullmatch(r'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize (\d+)\n?', text)
    if not match: raise ValueError('Unexpected Git LFS pointer')
    return match[1], int(match[2])

def plan():
    rows = []
    tree = subprocess.check_output(['git','ls-tree','-rlz','HEAD','Raft/Raft_Data'])
    for record in tree.split(b'\0'):
        if not record: continue
        meta, name = record.split(b'\t',1)
        path = name.decode()
        if not PATTERN.fullmatch(path) or int(meta.split()[-1]) > 1024: continue
        data = subprocess.check_output(['git','show','HEAD:'+path])
        if not data.startswith(b'version https://git-lfs.github.com/spec/v1'): continue
        digest, size = pointer(data)
        rows.append((path,digest,size))
    total = sum(r[2] for r in rows)
    if not rows or total > 10 * 1024**3: raise ValueError('Missing or over-budget original graphics payload plan')
    return rows

def _check_regular_path(path):
    """Reject redirects and aliased file inodes before graphics source I/O."""
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('Unsafe graphics source or destination path redirect')
    if path.exists():
        mode = path.stat().st_mode
        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            raise ValueError('Unsafe graphics source or destination file type')
        if stat.S_ISREG(mode) and path.stat().st_nlink != 1:
            raise ValueError('Unsafe hardlinked graphics payload')


def missing_payloads(rows):
    """Reuse only ordinary working files matching BOTH original size and SHA."""
    missing = []
    for name, digest, size in rows:
        path = Path(name)
        _check_regular_path(path)
        if not path.is_file() or path.stat().st_size != size:
            missing.append((name, digest, size))
            continue
        with path.open('rb') as source:
            actual = hashlib.file_digest(source, 'sha256').hexdigest()
        if actual != digest:
            missing.append((name, digest, size))
    return missing


def reuse_verified_staged_sources(rows, source_root, work_root=Path('.')):
    """Atomically reuse W1's SHA-verified ZIP2 owners when LFS pins match exactly.

    Only files in the caller's LFS-pointer plan are candidates. The source is
    checked again against the independent feature-branch LFS SHA and byte size.
    Missing cache objects are left for the original LFS route. A conflicting
    source, linked path or unexpected destination fails closed; no raw game
    asset is included in the emitted diagnostics.
    """
    source_root, work_root = Path(source_root), Path(work_root)
    _check_regular_path(source_root)
    _check_regular_path(work_root)
    if not source_root.exists():
        return 0, 0
    if not source_root.is_dir():
        raise ValueError('Staged graphics source root is not a directory')
    # Validate the entire available batch BEFORE replacing any LFS pointer.
    # Previously an invalid second owner could leave the first one hydrated.
    # This metadata-only preflight avoids a second multi-GB SHA read; each
    # source still receives full streaming SHA256 validation while copied.
    candidates = []
    for name, digest, size in rows:
        if not PATTERN.fullmatch(name):
            raise ValueError('Staged graphics source is outside original allowlist')
        source = source_root / Path(name).relative_to('Raft/Raft_Data')
        _check_regular_path(source)
        if not source.exists():
            continue
        if not source.is_file() or source.stat().st_size != size:
            raise ValueError('Staged graphics original has unexpected type or length')
        target = work_root / name
        _check_regular_path(target)
        if target.exists():
            if not target.is_file() or target.stat().st_size > 1024:
                raise ValueError('Refusing to replace nonpointer graphics destination')
            if pointer(target.read_bytes()) != (digest, size):
                raise ValueError('Original destination pointer does not match source pin')
        if not target.parent.is_dir():
            raise ValueError('Missing original graphics destination parent')
        candidates.append((source, target, digest, size))
    reused, reused_bytes = 0, 0
    for source, target, digest, size in candidates:
        _check_regular_path(source)
        _check_regular_path(target)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=target.parent, prefix='.verified-zip2-graphics-', delete=False
            ) as output:
                temporary = Path(output.name)
                copied, sha = 0, hashlib.sha256()
                with source.open('rb') as original:
                    while chunk := original.read(2 * 1024 * 1024):
                        copied += len(chunk)
                        if copied > size:
                            raise ValueError('Staged original exceeded pinned length')
                        sha.update(chunk)
                        output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            if copied != size or sha.hexdigest() != digest:
                raise ValueError('Staged original failed independent LFS SHA verification')
            os.chmod(temporary, 0o644)
            os.replace(temporary, target)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        reused += 1
        reused_bytes += size
    return reused, reused_bytes

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--release-cache',action='store_true');args=p.parse_args()
    rows=plan()
    print('RAFT_FULL_GRAPHICS_PLAN objects='+str(len(rows))+' original_bytes='+str(sum(r[2] for r in rows)))
    if not args.apply: return
    missing = missing_payloads(rows)
    # W1 has already staged authentic, independently SHA-pinned ZIP2 owners
    # at this exact runner location. Reuse only paths matching this LFS plan;
    # absent owners retain the existing Git LFS fetch/checkout fallback.
    if os.environ.get('RUNNER_TEMP'):
        source_root = Path(os.environ['RUNNER_TEMP']) / 'w1-original' / 'Raft_Data'
        reused, reused_bytes = reuse_verified_staged_sources(missing, source_root)
        print('RAFT_FULL_GRAPHICS_ZIP2_REUSED objects=' + str(reused)
              + ' original_bytes=' + str(reused_bytes) + ' sha256=true')
        missing = missing_payloads(rows)
    # Optional T5 source bridge. The caller must first reconstruct the
    # immutable ZIP2 owners into a separate directory with
    # t5_stage_zip2_render_owners; this consumer independently validates
    # against the feature-branch LFS SHA/length before replacing pointers.
    # With no explicit staging root, existing W1/LFS behavior is unchanged.
    t5_root = os.environ.get('RAFT_T5_VERIFIED_ZIP2_RENDER_ROOT')
    if t5_root:
        t5_source = Path(t5_root)
        if not t5_source.is_absolute():
            raise ValueError('T5 ZIP2 staged graphics root must be absolute')
        reused, bytes_reused = reuse_verified_staged_sources(missing, t5_source)
        print('RAFT_T5_ZIP2_RENDER_REUSED objects=' + str(reused)
              + ' original_bytes=' + str(bytes_reused) + ' sha256=true')
        missing = missing_payloads(rows)
    print('RAFT_FULL_GRAPHICS_REUSED objects='+str(len(rows)-len(missing)))
    if missing:
        subprocess.run(['git','lfs','install','--local'],check=True)
        subprocess.run(['git','lfs','fetch','origin','HEAD','--include='+','.join(r[0] for r in missing),'--exclude='],check=True)
        subprocess.run(['git','lfs','checkout']+[r[0] for r in missing],check=True)
    for name,digest,size in rows:
        path=Path(name)
        if path.is_symlink() or path.stat().st_size != size: raise ValueError('Original graphics payload size mismatch')
        with path.open('rb') as src: actual=hashlib.file_digest(src,'sha256').hexdigest()
        if actual != digest: raise ValueError('Original graphics payload digest mismatch')
    print('RAFT_FULL_GRAPHICS_VERIFIED objects='+str(len(rows))+' original_bytes='+str(sum(r[2] for r in rows))+' sha256=true')
    if args.release_cache:
        # CI-only space reclamation after every working payload was authenticated.
        # Delete only this plan's duplicate LFS cache objects, never source files.
        gitdir=Path(subprocess.check_output(['git','rev-parse','--git-dir'],text=True).strip())
        released=0
        for name,digest,size in rows:
            cached=gitdir/'lfs/objects'/digest[:2]/digest[2:4]/digest
            if cached.is_file() and not cached.is_symlink():
                released+=cached.stat().st_size
                cached.unlink()
        print('RAFT_FULL_GRAPHICS_DUPLICATE_CACHE_RELEASED bytes='+str(released)+' workingOriginalsRetained=true')


if __name__=='__main__': main()
