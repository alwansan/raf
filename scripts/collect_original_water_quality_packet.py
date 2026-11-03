"""Collect a bounded PRIVATE packet of authentic original quality settings.

Only counts, hashes and source identities may be printed. Packet bytes must be
CMS encrypted before leaving the runner; never upload the output directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

OWNER = 'resources.assets'
WANTED = {'WaterQualitySettings', 'WaterQualityLevel'}
MAX_OBJECT = 1024 * 1024
MAX_MATCHES = 16


def quality_script_identity(partial, owner, scripts):
    """Resolve an actual script pointer; do not search arbitrary object bytes."""
    ptr = partial.get('m_Script') if isinstance(partial, dict) else None
    if not isinstance(ptr, dict): return None
    file_id, path_id = ptr.get('m_FileID'), ptr.get('m_PathID')
    if type(file_id) is not int or type(path_id) is not int: return None
    if file_id == 0: basename = OWNER
    elif 1 <= file_id <= len(owner.externals):
        path = owner.externals[file_id-1].path
        if not isinstance(path, str): return None
        basename = path.replace('\\', '/').rsplit('/', 1)[-1]
        if basename != 'globalgamemanagers.assets': return None
    else: return None
    identity = scripts.get((basename,path_id))
    if not isinstance(identity, dict): return None
    if identity.get('namespace') != 'UltimateWater' or identity.get('class') != 'WaterQualitySettings': return None
    return identity


def collect(source, managed, output):
    if output.exists() or output.resolve().is_relative_to(source.resolve()) or output.resolve().is_relative_to(managed.resolve()):
        raise ValueError('Private output must be new and outside source roots')
    verify_sources(source, expected={OWNER:EXPECTED[OWNER]})
    global_path = source/'globalgamemanagers.assets'
    if global_path.is_symlink() or not global_path.is_file() or global_path.stat().st_size > 32*1024*1024:
        raise ValueError('Original script owner missing or unsafe')
    selected=[]
    for name in sorted(WANTED):
        paths=list(managed.rglob(name+'.cs'))
        if len(paths)!=1 or paths[0].is_symlink() or paths[0].stat().st_size>500000:
            raise ValueError('Original quality source identity missing or ambiguous')
        selected.append(paths[0])
    import UnityPy
    env=UnityPy.load(str(source/OWNER)); global_env=UnityPy.load(str(global_path))
    scripts={}
    for basename, original in ((OWNER,env.file),('globalgamemanagers.assets',global_env.file)):
        for obj in original.objects.values():
            if obj.type.name!='MonoScript':continue
            tree=obj.read_typetree()
            scripts[(basename,int(obj.path_id))]={'namespace':tree.get('m_Namespace'), 'class':tree.get('m_ClassName'),
                'owner':basename,'path_id':int(obj.path_id),'sha256':hashlib.sha256(obj.get_raw_data()).hexdigest()}
    matches=[]
    for obj in env.file.objects.values():
        if obj.type.name!='MonoBehaviour':continue
        partial=obj.read_typetree(check_read=False)
        identity=quality_script_identity(partial,env.file,scripts)
        if identity is None:continue
        raw=obj.get_raw_data()
        if len(raw)>MAX_OBJECT or len(matches)>=MAX_MATCHES:raise ValueError('Quality packet exceeds bounded scope')
        matches.append((obj,identity,raw))
    output.mkdir(parents=True,exist_ok=False)
    manifest={'owner':OWNER,'owner_sha256':EXPECTED[OWNER][1],
        'global_script_owner_sha256':hashlib.sha256(global_path.read_bytes()).hexdigest(),
        'files':{},'objects':[]}
    for path in selected:
        data=path.read_bytes();(output/path.name).write_bytes(data);manifest['files'][path.name]=hashlib.sha256(data).hexdigest()
    for obj,identity,raw in matches:
        filename='quality-object-'+str(int(obj.path_id))+'.bin'
        (output/filename).write_bytes(raw);digest=hashlib.sha256(raw).hexdigest();manifest['files'][filename]=digest
        manifest['objects'].append({'path_id':int(obj.path_id),'bytes':len(raw),'sha256':digest,'file':filename,
            'script_owner':identity['owner'],'script_path_id':identity['path_id'],'script_sha256':identity['sha256']})
    (output/'quality-manifest.json').write_text(json.dumps(manifest,sort_keys=True))
    return {'authenticated_original_owner':OWNER,'quality_object_count':len(matches),
        'quality_object_sizes':[len(raw) for _,_,raw in matches],
        'quality_object_sha256':[hashlib.sha256(raw).hexdigest() for _,_,raw in matches],
        'source_sha256':{p.name:manifest['files'][p.name] for p in selected},
        'serialized_values_decoded':False,'unity_or_gpu_executed':False,'plaintext_packet_published':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('source','managed-source','output'):p.add_argument('--'+arg,type=Path,required=True)
    a=p.parse_args();print('RAFT_PRIVATE_ORIGINAL_QUALITY_PACKET '+json.dumps(collect(a.source,a.managed_source,a.output),sort_keys=True))
