"""Fetch only tracked serialized/graphics LFS payloads, with a bounded authenticated plan."""
import argparse
import hashlib
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

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
    rows=plan()
    print('RAFT_FULL_GRAPHICS_PLAN objects='+str(len(rows))+' original_bytes='+str(sum(r[2] for r in rows)))
    if not args.apply: return
    subprocess.run(['git','lfs','install','--local'],check=True)
    subprocess.run(['git','lfs','fetch','origin','HEAD','--include='+','.join(r[0] for r in rows),'--exclude='],check=True)
    subprocess.run(['git','lfs','checkout']+[r[0] for r in rows],check=True)
    for name,digest,size in rows:
        path=Path(name)
        if path.is_symlink() or path.stat().st_size != size: raise ValueError('Original graphics payload size mismatch')
        with path.open('rb') as src: actual=hashlib.file_digest(src,'sha256').hexdigest()
        if actual != digest: raise ValueError('Original graphics payload digest mismatch')
    print('RAFT_FULL_GRAPHICS_VERIFIED objects='+str(len(rows))+' original_bytes='+str(sum(r[2] for r in rows))+' sha256=true')

if __name__=='__main__': main()
