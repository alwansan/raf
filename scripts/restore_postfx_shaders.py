"""Recover exact-name Unity Post Processing v1 shader programs from pinned official blobs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.request
from scripts.restore_tmp_shaders import DECL, restore

REPO='Unity-Technologies/PostProcessing'
COMMIT='933df236f509ed64ae5763ed57af33f2342cd1c2'
PREFIX='PostProcessing/Resources/Shaders/'
INCLUDES='Assets/RaftAndroid/PostFXShaderIncludes/'


def verified_blob(row,read):
    raw=read(row['path'])
    if len(raw)!=row['bytes'] or hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=row['git_blob']:
        raise ValueError('Official PostFX source fingerprint mismatch')
    return row['path'],raw


def sources(manifest,read):
    if manifest['repository']!=REPO or manifest['commit']!=COMMIT or not 1<=len(manifest['files'])<=40:
        raise ValueError('Unexpected PostFX source manifest')
    names=set()
    for row in manifest['files']:
        path=row['path']
        if path in names or not (path=='LICENSE' or re.fullmatch(re.escape(PREFIX)+r'[A-Za-z0-9_]+\.(?:shader|cginc)',path)):
            raise ValueError('Unsafe or duplicate vendor source path')
        if not 0<row['bytes']<=128*1024 or not re.fullmatch('[a-f0-9]{40}',row['git_blob']):
            raise ValueError('Invalid source bounds/identity')
        names.add(path)
    shaders={};includes={};license=None
    with ThreadPoolExecutor(max_workers=4) as pool:
        for path,raw in pool.map(lambda row:verified_blob(row,read),manifest['files']):
            if path=='LICENSE':license=raw;continue
            text=raw.decode('utf-8-sig');name=Path(path).name
            if name.endswith('.cginc'): includes[name]=text
            else:
                match=DECL.search(text)
                if not match or match[1] in shaders:raise ValueError('Ambiguous PostFX shader identity')
                shaders[match[1]]=text
    if len(shaders)!=14 or not license:raise ValueError('Incomplete original PostFX subset')
    bloom=shaders.get('Hidden/Post FX/Bloom','')
    if len(re.findall(r'\bPass\s*\{',bloom))!=4:raise ValueError('Original Bloom pass order contract changed')
    combined=bloom+'\n'+includes.get('Bloom.cginc','')
    if not all(name in combined for name in ('_Threshold','_Curve','_SampleScale')):
        raise ValueError('Original Bloom uniform contract changed')
    print('RAFT_OFFICIAL_POSTFX_SOURCES shaders=14 bloomPasses=4 includes='+str(len(includes))+' gitBlobHashesVerified=true')
    return shaders,includes,license


def download(path):
    url='https://raw.githubusercontent.com/'+REPO+'/'+COMMIT+'/'+path
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=45) as response:raw=response.read(128*1024+1)
            if len(raw)>128*1024:raise ValueError('Over-limit vendor source')
            return raw
        except OSError:
            if attempt==2:raise
            time.sleep(1)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path);p.add_argument('--backup',type=Path);p.add_argument('--verify-only',action='store_true');p.add_argument('--manifest',type=Path,default=Path('config/postfx-v1-shader-sources.json'));args=p.parse_args()
    shader,include,license=sources(json.loads(args.manifest.read_text()),download)
    if args.verify_only:return
    if not args.project or not args.backup:raise ValueError('Project and external backup are required')
    restore(args.project,args.backup,shader,include,license,shader_prefix='Hidden/Post FX/',include_root=INCLUDES,label='POSTFX_V1',vendor_version='v1@933df236')

if __name__=='__main__':main()
