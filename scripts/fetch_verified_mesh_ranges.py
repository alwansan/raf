#!/usr/bin/env python3
"""Fetch checksum-pinned original Mesh byte ranges, never whole-object fallback."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

SOURCE = re.compile(r'^(?:(?:resources|sharedassets\d+)\.assets\.resS|level\d+\.resS)$')
HEX = re.compile(r'^[a-f0-9]{64}$')


def validate_manifest(manifest):
    if (type(manifest.get('format')) is not int or manifest.get('format') != 1 or
            type(manifest.get('max_chunk_bytes')) is not int or
            not 0 < manifest['max_chunk_bytes'] <= 8 * 1024 * 1024):
        raise ValueError('Unsupported Mesh range manifest')
    for name, stream in manifest['streams'].items():
        if not SOURCE.fullmatch(name) or not HEX.fullmatch(stream['sha256']):
            raise ValueError('Invalid original stream identity')
        if type(stream['size']) is not int or not 0 < stream['size'] <= 2_500_000_000:
            raise ValueError('Invalid original stream size')
        end = 0
        whole = stream.get('restore_whole', False)
        if type(whole) is not bool or not stream['chunks']:
            raise ValueError('Invalid original stream restoration policy')
        for chunk in stream['chunks']:
            offset, size = chunk['offset'], chunk['size']
            if whole and offset != end:
                raise ValueError('Whole original stream has a coverage gap')
            if (type(offset) is not int or type(size) is not int or offset < end or
                    not 0 < size <= manifest['max_chunk_bytes'] or offset + size > stream['size'] or
                    not HEX.fullmatch(chunk['sha256'])):
                raise ValueError('Unsafe, overlapping or out-of-bounds pinned range')
            end = offset + size
        if whole and end != stream['size']:
            raise ValueError('Whole original stream has an uncovered suffix')


def cache_path(cache, name, chunk):
    if not SOURCE.fullmatch(name):
        raise ValueError('Unsafe stream cache name')
    return cache / (name + '.' + str(chunk['offset']) + '.' + str(chunk['size']) + '.range')


def check_bytes(raw, chunk):
    if len(raw) != chunk['size'] or hashlib.sha256(raw).hexdigest() != chunk['sha256']:
        raise ValueError('Original range size or SHA256 mismatch')


def read_cached(path, chunk):
    if path.stat().st_size != chunk['size']:
        raise ValueError('Cached range size mismatch')
    raw = path.read_bytes()
    check_bytes(raw, chunk)
    return raw


def install_range(cache, name, chunk, raw):
    check_bytes(raw, chunk)
    target = cache_path(cache, name, chunk)
    if target.exists():
        read_cached(target, chunk)
        return
    temporary = target.with_name(target.name + '.partial')
    try:
        with temporary.open('xb') as out:
            out.write(raw)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise ValueError('Unexpected redirect in authenticated original range retrieval')


def get_download_actions(streams, repo, token, opener):
    if repo != 'alwansan/raf' or not token:
        raise ValueError('Expected authorized source repository and GitHub token')
    payload = {'operation': 'download', 'transfers': ['basic'], 'objects': [
        {'oid': stream['sha256'], 'size': stream['size']} for stream in streams.values()]}
    request = urllib.request.Request('https://github.com/' + repo + '.git/info/lfs/objects/batch',
        data=json.dumps(payload).encode(), headers={
            'Accept': 'application/vnd.git-lfs+json', 'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': 'Basic ' + base64.b64encode(('x-access-token:' + token).encode()).decode()})
    with opener.open(request, timeout=45) as response:
        raw = response.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError('Unexpected oversized LFS metadata response')
    data = json.loads(raw)
    actions = {}
    for obj in data.get('objects', []):
        if 'error' in obj or 'download' not in obj.get('actions', {}):
            raise ValueError('Original LFS download authorization unavailable')
        actions[obj['oid']] = obj['actions']['download']
    if set(actions) != {stream['sha256'] for stream in streams.values()}:
        raise ValueError('LFS response does not match requested original object identities')
    return actions


def fetch_range(action, stream, chunk, opener):
    url = urllib.parse.urlsplit(action['href'])
    if url.scheme != 'https' or url.username or url.password:
        raise ValueError('Expected HTTPS original-object download URL')
    headers = dict(action.get('header', {}))  # Never forward the GitHub batch token.
    headers.update({'Range': 'bytes=' + str(chunk['offset']) + '-' + str(chunk['offset'] + chunk['size'] - 1),
                    'Accept-Encoding': 'identity'})
    request = urllib.request.Request(action['href'], headers=headers)
    with opener.open(request, timeout=60) as response:
        if response.status != 206:
            raise ValueError('Server did not honor byte range; whole-object fallback is forbidden')
        expected = 'bytes ' + str(chunk['offset']) + '-' + str(chunk['offset'] + chunk['size'] - 1) + '/' + str(stream['size'])
        if response.headers.get('Content-Range') != expected:
            raise ValueError('Original object returned an incorrect Content-Range')
        if response.headers.get('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Unexpected content encoding for original range')
        length = response.headers.get('Content-Length')
        if length is not None and int(length) != chunk['size']:
            raise ValueError('Original range Content-Length mismatch')
        raw = response.read(chunk['size'] + 1)
    check_bytes(raw, chunk)
    return raw


def verify_source_pointer(path, stream):
    if not path.is_file() or path.stat().st_size >= 200:
        return False
    text = path.read_text(encoding='ascii')
    oid = re.search(r'(?m)^oid sha256:([a-f0-9]{64})$', text)
    size = re.search(r'(?m)^size (\d+)$', text)
    if (not text.startswith('version https://git-lfs.github.com/spec/v1\n') or not oid or not size or
            oid[1] != stream['sha256'] or int(size[1]) != stream['size']):
        raise ValueError('Checkout pointer differs from pinned original stream identity')
    return True


def fetch(manifest, source_root, cache, token, probe_stream=None):
    validate_manifest(manifest)
    cache.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(NoRedirect())
    streams = manifest['streams'] if probe_stream is None else {probe_stream: manifest['streams'][probe_stream]}
    remote, jobs, local_providers = {}, [], 0
    total_bytes = remote_bytes = 0
    for name, stream in streams.items():
        chunks = stream['chunks'] if probe_stream is None else [min(stream['chunks'], key=lambda c: c['size'])]
        source = source_root / name
        if verify_source_pointer(source, stream):
            remote[name] = stream
            for chunk in chunks:
                target = cache_path(cache, name, chunk)
                if target.exists():
                    read_cached(target, chunk)
                else:
                    jobs.append((name, stream, chunk))
                    remote_bytes += chunk['size']
                total_bytes += chunk['size']
        else:
            if not source.is_file() or source.stat().st_size != stream['size']:
                raise ValueError('Missing original stream pointer or verified full source')
            with source.open('rb') as original:
                if hashlib.file_digest(original, 'sha256').hexdigest() != stream['sha256']:
                    raise ValueError('Existing full original stream SHA256 mismatch')
                for chunk in chunks:
                    original.seek(chunk['offset'])
                    install_range(cache, name, chunk, original.read(chunk['size']))
                    total_bytes += chunk['size']
            local_providers += 1
    if jobs:
        actions = get_download_actions(remote, 'alwansan/raf', token, opener)
        def retrieve(job):
            name, stream, chunk = job
            raw = fetch_range(actions[stream['sha256']], stream, chunk, opener)
            install_range(cache, name, chunk, raw)
        with ThreadPoolExecutor(max_workers=4) as executor:
            for _ in executor.map(retrieve, jobs):
                pass
    report = {'verified_range_bytes': total_bytes, 'remote_range_bytes': remote_bytes,
              'remote_chunks': len(jobs), 'reused_full_providers': local_providers,
              'whole_object_fallback_allowed': False, 'range_sha256_verified': True}
    print('RAFT_VERIFIED_MESH_RANGE_DOWNLOAD ' + json.dumps(report, sort_keys=True))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--probe-stream', choices=['sharedassets34.assets.resS'])
    args = parser.parse_args()
    try:
        fetch(json.loads(args.manifest.read_text()), args.source_root, args.cache,
              os.environ.get('GH_TOKEN', ''), args.probe_stream)
    except Exception as exc:
        # Do not print signed URLs, tokens, HTTP bodies or authorization headers.
        detail = 'HTTP ' + str(exc.code) if isinstance(exc, urllib.error.HTTPError) else type(exc).__name__
        raise SystemExit('Original Mesh range recovery failed: ' + detail) from None

