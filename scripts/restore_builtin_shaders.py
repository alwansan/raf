"""Restore exact-name Unity 2021.3.45f2 built-in programs, retaining exported GUIDs.

Only names present in the authenticated runtime shader archive are eligible.
Unknown/custom game shaders and all materials/textures remain untouched.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import time
import urllib.request
import zipfile
from scripts.restore_tmp_shaders import DECL

URL = 'https://download.unity3d.com/download_unity/88f88f591b2e/builtin_shaders-2021.3.45f2.zip'
SHA256 = '5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5'
ROOT = 'Assets/RaftAndroid/BuiltinShaderSources/'
NOTICE = 'Assets/StreamingAssets/RaftAndroidNotices/unity-builtin-shaders-MIT.txt'
INCLUDE = re.compile(r'(#\s*include(?:_with_pragmas)?\s+")([^"\r\n]+)(")')
# A ShaderLab header may be preceded by a commented-out Shader name. The
# shared DECL regex also appears in other restorers; avoid changing it globally.
EXPORT_DECL = re.compile(r'^\s*Shader\s+"([^"\r\n]+)"', re.MULTILINE)
COMMENT_OR_STRING = re.compile(r'//[^\r\n]*|/\*[\s\S]*?(?:\*/|$)|"(?:\\.|[^"\\])*"')


def exported_shader_identity(source):
    """Return exactly one real ShaderLab header, ignoring quoted comment markers.

    Preserve quoted strings while blanking comments (and their line breaks), so
    Shader "Custom//Name" stays valid. Never print proprietary shader names.
    """
    def mask(match):
        token = match.group()
        if token.startswith('"'):
            return token
        return ''.join(c if c in '\r\n' else ' ' for c in token)

    stripped = COMMENT_OR_STRING.sub(mask, source)
    identities = EXPORT_DECL.findall(stripped)
    if len(identities) > 1:
        raise ValueError('Multiple real ShaderLab declarations in exported shader')
    return identities[0] if identities else None



def archive_sources(raw):
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('Unity built-in shader archive fingerprint mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        if len(infos) != 660 or sum(x.file_size for x in infos) > 4 * 1024 * 1024:
            raise ValueError('Unexpected built-in shader archive bounds')
        if len({x.filename for x in infos}) != len(infos):
            raise ValueError('Duplicate built-in shader archive entry')
        files = {}
        for entry in infos:
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename:
                raise ValueError('Unsafe built-in shader archive path')
            if entry.filename.endswith(('.shader', '.cginc', '.glslinc')):
                files[entry.filename] = archive.read(entry).decode('utf-8-sig')
        license = archive.read('license.txt')
    shaders = {}
    for path, source in files.items():
        if not path.startswith(('DefaultResources/', 'DefaultResourcesExtra/')) or not path.endswith('.shader'):
            continue
        match = DECL.search(source)
        if not match or match[1] in shaders:
            raise ValueError('Ambiguous built-in shader identity')
        shaders[match[1]] = path
    if len(shaders) != 198 or not license:
        raise ValueError('Incomplete runtime built-in shader set')
    # Validate every quoted include before any project mutation, including recursion.
    for path in files:
        rewrite(path, files)
    print('RAFT_BUILTIN_SHADER_SOURCES version=2021.3.45f2 runtimeShaders=198 archiveSHA256Verified=true deviceExecution=false')
    return shaders, files, license


def rewrite(path, files):
    dependencies = set()
    original = files[path]

    def mask_comment(match):
        token = match.group()
        if token.startswith(('//', '/*')):
            return ''.join(c if c in '\r\n' else ' ' for c in token)
        return token

    # Identify live #include tokens on a same-length comment-masked copy, then
    # preserve untouched original source including comments and quoted paths.
    clean = COMMENT_OR_STRING.sub(mask_comment, original)
    result = []
    last = 0
    for match in INCLUDE.finditer(clean):
        include = match[2]
        candidates = (posixpath.normpath(posixpath.join(posixpath.dirname(path), include)), 'CGIncludes/' + include)
        found = next((p for p in candidates if p in files and p.endswith(('.cginc', '.glslinc'))), None)
        if found is None:
            raise ValueError('Unresolved built-in shader include')
        dependencies.add(found)
        result.extend((original[last:match.start()], match[1] + ROOT + found + match[3]))
        last = match.end()
    result.append(original[last:])
    return ''.join(result), dependencies


def restore_project(project, backup, shaders, files, license):
    project = project.resolve()
    assets = project / 'Assets'
    backup = backup.resolve()
    if backup.is_relative_to(project):
        raise ValueError('Shader backup must be outside Unity project')
    plan = []
    used = set()
    dependencies = set()
    shader_files = 0
    declared_identities = 0
    unmatched_identities = 0
    for path in sorted(assets.rglob('*.shader')):
        shader_files += 1
        name = exported_shader_identity(path.read_text(encoding='utf-8-sig'))
        if name is None:
            continue
        declared_identities += 1
        if name not in shaders:
            unmatched_identities += 1
            continue
        if name in used:
            raise ValueError('Ambiguous exported built-in shader identity')
        used.add(name)
        meta = Path(str(path) + '.meta')
        if not meta.is_file() or meta.is_symlink() or path.is_symlink():
            raise ValueError('Missing/unsafe original shader metadata')
        source, required = rewrite(shaders[name], files)
        dependencies.update(required)
        plan.append((path, source.encode(), path.read_bytes(), meta, meta.read_bytes()))
    # Count-only evidence answers why a genuine export matched no trusted
    # built-in identities, without leaking original/custom shader names or
    # turning this strict authenticity gate into an optional success.
    print('RAFT_BUILTIN_EXPORT_MATCH_AUDIT ' + json.dumps({
        'shader_files': shader_files,
        'parseable_declarations': declared_identities,
        'unmatched_declarations': unmatched_identities,
        'matched_identities': len(plan),
        'unparseable_declarations': shader_files - declared_identities,
    }, sort_keys=True))
    if not plan:
        raise ValueError('No exported built-in shader identities matched; custom shaders cannot be substituted')
    additions = {project / NOTICE: license, project / ROOT / 'license.txt': license}
    pending = list(dependencies)
    done = set()
    while pending:
        path = pending.pop()
        if path in done:
            continue
        done.add(path)
        source, required = rewrite(path, files)
        additions[project / ROOT / path] = source.encode()
        pending.extend(required - done)
    for path, content in additions.items():
        if path.exists() and (path.is_symlink() or path.read_bytes() != content):
            raise ValueError('Conflicting built-in dependency or license destination')
    backup.mkdir(parents=True, exist_ok=False)
    for path, content, original, meta, metadata in plan:
        saved = backup / path.relative_to(assets)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(original)
        Path(str(saved) + '.meta').write_bytes(metadata)
    try:
        for path, content in additions.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        for path, content, original, meta, metadata in plan:
            path.write_bytes(content)
            if meta.read_bytes() != metadata:
                raise ValueError('Original built-in shader metadata changed')
    except BaseException:
        for path, content, original, meta, metadata in plan:
            path.write_bytes(original)
        raise
    print('RAFT_BUILTIN_SHADER_RESTORATION matchedShaders=' + str(len(plan)) +
          ' includes=' + str(len(done)) + ' originalMetasUnchanged=true customShadersChanged=false deviceExecution=false')
    return len(plan)


def download():
    for attempt in range(3):
        try:
            with urllib.request.urlopen(URL, timeout=45) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError('Over-limit built-in shader archive')
            return raw
        except OSError:
            if attempt == 2:
                raise
            time.sleep(1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path)
    p.add_argument('--backup', type=Path)
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    sources = archive_sources(download())
    if args.verify_only:
        return
    if not args.project or not args.backup:
        raise ValueError('Project and external backup required')
    restore_project(args.project, args.backup, *sources)


if __name__ == '__main__':
    main()
