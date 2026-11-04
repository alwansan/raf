"""Restore exact-name TMP 3.0.6 shaders from authenticated official Essential Resources.

Keep original exported shader paths and every existing .meta/GUID. Only replace
shader programs with the matching installed-package version; no atlas/font edits.
"""
import argparse
import hashlib
import io
from pathlib import Path
import re
import shutil
import tarfile
import urllib.request

URL='https://download.packages.unity.com/com.unity.textmeshpro/-/com.unity.textmeshpro-3.0.6.tgz'
SHA256='1ce172027b906a30be33cefe7b2ee46e1c8d35f729359b8b9785fc120d57b637'
DECL=re.compile(r'\bShader\s+"([^"\r\n]+)"')
ROOT='Assets/RaftAndroid/TMPShaderIncludes/'

# B10: GUIDs below belong ONLY to newly added vendor fallbacks, never to
# original exported shaders. Original .shader.meta bytes remain authoritative.
META_GUID = re.compile(rb'(?m)^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*\r?$')


def generated_vendor_shader_meta(name, include_root):
    """Create a deterministic Unity ShaderImporter sidecar for a NEW vendor file."""
    if not isinstance(name, str) or not name or not isinstance(include_root, str) or not include_root.startswith('Assets/'):
        raise ValueError('Invalid generated vendor Shader identity')
    identity = b'RaftAndroid/generated-vendor-shader/v1\0' + include_root.encode('utf-8') + b'\0' + name.encode('utf-8')
    guid = hashlib.sha256(identity).hexdigest()[:32]
    meta = ('fileFormatVersion: 2\n'
            'guid: ' + guid + '\n'
            'ShaderImporter:\n'
            '  externalObjects: {}\n'
            '  defaultTextures: []\n'
            '  nonModifiableTextures: []\n'
            '  userData: \n'
            '  assetBundleName: \n'
            '  assetBundleVariant: \n').encode('utf-8')
    return guid, meta


def existing_asset_guids(assets):
    """Collect original/export GUIDs without changing or publishing them."""
    seen = {}
    for meta in sorted(assets.rglob('*.meta')):
        _require_safe_vendor_asset_path(assets, meta)
        if not meta.is_file():
            raise ValueError('Unsafe existing Unity metadata')
        with meta.open('rb') as stream:
            head = stream.read(4096)
        values = META_GUID.findall(head)
        if len(values) > 1:
            raise ValueError('Ambiguous existing Unity metadata GUID')
        if not values:
            continue  # Never invent a GUID for unrelated, nonstandard source meta.
        guid = values[0].decode('ascii').lower()
        if guid in seen and seen[guid] != meta:
            raise ValueError('Duplicate existing Unity metadata GUID')
        seen[guid] = meta
    return seen



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


def rewrite_includes(source, includes, include_root=ROOT):
    return re.sub(r'(#\s*include\s+")([^"\r\n]+)(")',
        lambda m:m[1]+(include_root+m[2] if m[2] in includes else m[2])+m[3],source)



def _require_safe_vendor_asset_path(assets, target):
    """Refuse redirected Unity Assets parents and output leaves before mutation.

    The caller's Assets root must be a real directory; lexical containment
    alone does not defend against an existing directory symlink.
    """
    if assets.is_symlink() or not assets.is_dir() or not target.is_relative_to(assets):
        raise ValueError('Unsafe Unity vendor shader asset path')
    candidate = assets
    for segment in target.relative_to(assets).parts:
        candidate = candidate / segment
        if candidate.is_symlink():
            raise ValueError('Unsafe symlinked Unity vendor shader asset path')
    if not target.resolve().is_relative_to(assets.resolve()):
        raise ValueError('Unsafe redirected Unity vendor shader asset path')


def restore(project, backup, shaders, includes, license, *, shader_prefix="TextMeshPro/", include_root=ROOT, label="TMP", vendor_version="3.0.6"):
    # TMP, official PostFX and Volumetric shaders all use this shared path.
    # Stage vendor additions and original export overwrites as one recoverable
    # operation. Never remove pre-existing byte-identical dependencies.
    project = project.resolve()
    assets = project / 'Assets'
    backup = backup.resolve()
    _require_safe_vendor_asset_path(assets, assets)
    if backup.is_relative_to(project):
        raise ValueError('Shader backup must be outside Unity project')
    include_directory = project / include_root
    _require_safe_vendor_asset_path(assets, include_directory)

    plan = []
    used = set()
    for target in sorted(assets.rglob('*.shader')):
        _require_safe_vendor_asset_path(assets, target)
        # A repeated import must not call generated files original exported Shaders.
        if target.is_relative_to(include_directory):
            continue
        text = target.read_text(encoding='utf-8-sig')
        match = DECL.search(text)
        if not match or not match[1].startswith(shader_prefix):
            continue
        name = match[1]
        if name not in shaders:
            raise ValueError('Unknown original vendor shader name; no replacement invented')
        if name in used:
            raise ValueError('Ambiguous exported TMP shader identity')
        used.add(name)
        meta = Path(str(target) + '.meta')
        _require_safe_vendor_asset_path(assets, meta)
        if not meta.is_file() or target.is_symlink() or meta.is_symlink():
            raise ValueError('Missing/unsafe original TMP shader metadata')
        plan.append((target, rewrite_includes(shaders[name], includes, include_root),
                     target.read_bytes(), meta, meta.read_bytes()))
    if not plan:
        raise ValueError('No original exported vendor shader identities')

    additions = []
    for name, source in includes.items():
        if Path(name).name != name or not name.endswith('.cginc'):
            raise ValueError('Unsafe include filename')
        destination = include_directory / name
        additions.append((destination, rewrite_includes(source, includes, include_root).encode('utf-8')))

    # A stripped PC build can omit an official fallback. Add only its exact
    # verified vendor shader identity; never fabricate a substitute pass.
    missing = []
    generated_meta = {}
    for name, source in shaders.items():
        if name in used:
            continue
        filename = 'vendor-' + hashlib.sha256(name.encode()).hexdigest()[:16] + '.shader'
        destination = include_directory / filename
        content = rewrite_includes(source, includes, include_root).encode('utf-8')
        additions.append((destination, content))
        missing.append((destination, content))
        guid, metadata = generated_vendor_shader_meta(name, include_root)
        meta = Path(str(destination) + '.meta')
        if guid in generated_meta:
            raise ValueError('Collision between newly generated vendor Shader GUIDs')
        generated_meta[guid] = meta
        additions.append((meta, metadata))
    additions.append((include_directory / 'LICENSE.md', license))

    existing_guids = existing_asset_guids(assets)
    for guid, meta in generated_meta.items():
        if guid in existing_guids and existing_guids[guid] != meta:
            raise ValueError('Generated vendor Shader GUID collision with original export metadata')

    destinations = set()
    for destination, content in additions:
        _require_safe_vendor_asset_path(assets, destination)
        if destination in destinations:
            raise ValueError('Duplicate vendor shader destination')
        destinations.add(destination)
        if destination.exists() and (not destination.is_file() or destination.read_bytes() != content):
            raise ValueError('Conflicting vendor shader dependency or notice')

    # The backup directory is created exclusively and contains exact original
    # exported shader and .meta bytes. A failed backup cannot be used as if it
    # were complete, and must never mutate the live Unity project.
    backup.mkdir(parents=True, exist_ok=False)
    try:
        for target, source, original, meta, meta_bytes in plan:
            saved = backup / target.relative_to(assets)
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(original)
            Path(str(saved) + '.meta').write_bytes(meta_bytes)
    except BaseException:
        shutil.rmtree(backup)
        raise

    created = []
    replaced = []
    try:
        for destination, content in additions:
            _require_safe_vendor_asset_path(assets, destination)
            if destination.exists():
                if not destination.is_file() or destination.read_bytes() != content:
                    raise ValueError('Conflicting vendor shader dependency or notice')
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            _require_safe_vendor_asset_path(assets, destination)
            # Exclusive creation prevents replacing an include or license added
            # after the earlier preflight by another process.
            with destination.open('xb') as stream:
                created.append(destination)
                stream.write(content)

        for target, source, original, meta, meta_bytes in plan:
            _require_safe_vendor_asset_path(assets, target)
            _require_safe_vendor_asset_path(assets, meta)
            if target.read_bytes() != original or meta.read_bytes() != meta_bytes:
                raise ValueError('Original exported vendor shader or metadata changed after backup')
            # Record before the write: even a failed write may truncate bytes.
            replaced.append((target, original))
            target.write_text(source, encoding='utf-8')
            if meta.read_bytes() != meta_bytes:
                raise ValueError('Original TMP shader GUID metadata changed')
    except BaseException:
        rollback_failed = False
        for target, original in reversed(replaced):
            try:
                _require_safe_vendor_asset_path(assets, target)
                target.write_bytes(original)
            except BaseException:
                rollback_failed = True
        for destination in reversed(created):
            try:
                _require_safe_vendor_asset_path(assets, destination)
                if destination.is_file() and not destination.is_symlink():
                    destination.unlink()
            except BaseException:
                rollback_failed = True
        # Retain the *complete* external backup when publication fails, even
        # after successful rollback. It is the last recovery source if another
        # process changed files concurrently.
        if rollback_failed:
            raise RuntimeError('Vendor shader restore rollback incomplete; inspect external backup')
        raise
    print('RAFT_' + label + '_SHADER_RESTORATION originalShaders=' + str(len(plan)) +
          ' vendorFallbacksAdded=' + str(len(missing)) +
          ' originalMetasUnchanged=true fontAtlasChanged=false vendorVersion=' + vendor_version)
    return len(plan)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True);p.add_argument('--backup',type=Path,required=True);args=p.parse_args()
    with urllib.request.urlopen(URL,timeout=90) as response: raw=response.read(16*1024*1024+1)
    if len(raw)>16*1024*1024: raise ValueError('Over-limit TMP package')
    restore(args.project,args.backup,*vendor_sources(raw))

if __name__=='__main__':main()
