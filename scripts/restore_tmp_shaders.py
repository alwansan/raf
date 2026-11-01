"""Restore exact-name TMP 3.0.6 shaders from authenticated official Essential Resources.

Keep original exported shader paths and every existing .meta/GUID. Only replace
shader programs with the matching installed-package version; no atlas/font edits.
"""
import argparse
import hashlib
import io
from pathlib import Path
import re
import tarfile
import urllib.request

URL='https://download.packages.unity.com/com.unity.textmeshpro/-/com.unity.textmeshpro-3.0.6.tgz'
SHA256='1ce172027b906a30be33cefe7b2ee46e1c8d35f729359b8b9785fc120d57b637'
DECL=re.compile(r'\bShader\s+"([^"\r\n]+)"')
ROOT='Assets/RaftAndroid/TMPShaderIncludes/'


def vendor_sources(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA256: raise ValueError('Official TMP package fingerprint mismatch')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as outer:
        inner=outer.extractfile('package/Package Resources/TMP Essential Resources.unitypackage').read()
        license=outer.extractfile('package/LICENSE.md').read()
    shaders={};includes={}
    with tarfile.open(fileobj=io.BytesIO(inner),mode='r:gz') as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.endswith('/pathname'): continue
            path=archive.extractfile(member).read().decode('utf-8-sig').strip()
            if not path.startswith('Assets/TextMesh Pro/Shaders/'): continue
            name=Path(path).name
            if name!=path.split('/Shaders/',1)[1]: raise ValueError('Unexpected nested TMP shader dependency')
            if not name.endswith(('.shader','.cginc')): continue
            content=archive.extractfile(member.name.rsplit('/',1)[0]+'/asset').read().decode('utf-8-sig')
            if name.endswith('.cginc'):
                if name in includes: raise ValueError('Ambiguous vendor include')
                includes[name]=content
            else:
                match=DECL.search(content)
                if not match or match[1] in shaders: raise ValueError('Ambiguous vendor shader identity')
                shaders[match[1]]=content
    if len(shaders)<10 or len(includes)<4: raise ValueError('Incomplete pinned TMP resource subset')
    return shaders,includes,license


def rewrite_includes(source, includes):
    return re.sub(r'(#\s*include\s+")([^"\r\n]+)(")',
        lambda m:m[1]+(ROOT+m[2] if m[2] in includes else m[2])+m[3],source)


def restore(project, backup, shaders, includes, license):
    assets=(project/'Assets').resolve();backup=backup.resolve()
    if backup.is_relative_to(project.resolve()): raise ValueError('Shader backup must be outside Unity project')
    plan=[];used=set()
    for target in sorted(assets.rglob('*.shader')):
        text=target.read_text(encoding='utf-8-sig');match=DECL.search(text)
        if not match or not match[1].startswith('TextMeshPro/'): continue
        name=match[1]
        if name not in shaders: raise ValueError('Unknown original TMP shader name; no replacement invented')
        if name in used: raise ValueError('Ambiguous exported TMP shader identity')
        used.add(name)
        meta=Path(str(target)+'.meta')
        if not meta.is_file() or target.is_symlink() or meta.is_symlink(): raise ValueError('Missing/unsafe original TMP shader metadata')
        plan.append((target,rewrite_includes(shaders[name],includes),target.read_bytes(),meta,meta.read_bytes()))
    if not plan: raise ValueError('No original exported TMP shader identities')
    dependency_plan=[]
    for name,source in includes.items():
        if Path(name).name!=name or not name.endswith('.cginc'): raise ValueError('Unsafe include filename')
        destination=project/ROOT/name
        content=rewrite_includes(source,includes).encode('utf-8')
        if destination.exists() and destination.read_bytes()!=content: raise ValueError('Conflicting shader include destination')
        dependency_plan.append((destination,content))
    # A stripped PC build can omit a vendor fallback that was never referenced.
    # Add only missing exact vendor identities so real restored shaders can resolve it.
    missing = []
    for name, source in shaders.items():
        if name in used: continue
        filename = 'vendor-' + hashlib.sha256(name.encode()).hexdigest()[:16] + '.shader'
        destination = project/ROOT/filename
        content = rewrite_includes(source, includes).encode('utf-8')
        if destination.exists() and destination.read_bytes() != content:
            raise ValueError('Conflicting vendor fallback shader destination')
        missing.append((destination, content))
    dependency_plan.extend(missing)
    license_path=project/ROOT/'LICENSE.md'
    if license_path.exists() and license_path.read_bytes()!=license: raise ValueError('Conflicting TMP notice')
    backup.mkdir(parents=True,exist_ok=False)
    for target,source,original,meta,meta_bytes in plan:
        saved=backup/target.relative_to(assets);saved.parent.mkdir(parents=True,exist_ok=True)
        saved.write_bytes(original);Path(str(saved)+'.meta').write_bytes(meta_bytes)
    try:
        for destination,content in dependency_plan+[(license_path,license)]:
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(content)
        for target,source,original,meta,meta_bytes in plan:
            target.write_text(source,encoding='utf-8')
            if meta.read_bytes()!=meta_bytes: raise ValueError('Original TMP shader GUID metadata changed')
    except BaseException:
        for target,source,original,meta,meta_bytes in plan: target.write_bytes(original)
        raise
    print('RAFT_TMP_SHADER_RESTORATION originalShaders='+str(len(plan))+' vendorFallbacksAdded='+str(len(missing))+' originalMetasUnchanged=true fontAtlasChanged=false vendorVersion=3.0.6')
    return len(plan)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True);p.add_argument('--backup',type=Path,required=True);args=p.parse_args()
    with urllib.request.urlopen(URL,timeout=90) as response: raw=response.read(16*1024*1024+1)
    if len(raw)>16*1024*1024: raise ValueError('Over-limit TMP package')
    restore(args.project,args.backup,*vendor_sources(raw))

if __name__=='__main__':main()
