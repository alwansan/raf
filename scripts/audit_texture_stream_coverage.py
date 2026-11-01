"""Verify original texture extents before export; output counts only, never pixel/source data."""
import argparse
from collections import Counter
import gc
from pathlib import Path
from scripts.mesh_source_files import serialized_sources, owned_objects


def extent(root, path, offset, size):
    if not path or size == 0: return 'inline_or_empty'
    if type(offset) is not int or type(size) is not int or offset < 0 or size < 0:
        return 'invalid_extent'
    name = path.replace('\\','/').rsplit('/',1)[-1]
    if name in ('', '.', '..') or not name.endswith(('.resS','.resource')): return 'invalid_provider'
    source = root / name
    if not source.is_file(): return 'missing_provider'
    with source.open('rb') as stream:
        if stream.read(48).startswith(b'version https://git-lfs.github.com/spec/v1'): return 'lfs_pointer'
    return 'covered' if offset + size <= source.stat().st_size else 'truncated_provider'


def audit(root):
    import UnityPy
    counts=Counter();platforms=Counter()
    for source in serialized_sources(root):
        env=UnityPy.load(str(source))
        for obj in owned_objects(env):
            if obj.type.name=='Shader':
                counts['shaders']+=1
                tree=obj.read_typetree()
                for value in tree.get('platforms', tree.get('m_Platforms', [])): platforms[str(value)]+=1
            elif obj.type.name=='ComputeShader': counts['compute_shaders']+=1
            elif obj.type.name=='Texture2D':
                counts['textures']+=1
                tree=obj.read_typetree();stream=tree.get('m_StreamData', {})
                status=extent(root,stream.get('path',''),stream.get('offset',0),stream.get('size',0))
                counts['texture_'+status]+=1
                if status=='covered': counts['texture_external_bytes']+=stream['size']
        del env
        gc.collect()
    print('RAFT_TEXTURE_SOURCE_COVERAGE counts='+str(dict(counts))+' original_shader_platform_codes='+str(dict(platforms)))
    bad=sum(counts['texture_'+key] for key in ('invalid_extent','invalid_provider','missing_provider','lfs_pointer','truncated_provider'))
    if bad or not counts['textures']: raise ValueError('Original texture payload coverage incomplete')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);args=p.parse_args();audit(args.root)
