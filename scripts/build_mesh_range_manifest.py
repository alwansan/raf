#!/usr/bin/env python3
"""Build aggregate range checksums from fully verified private original streams.

The output contains source identities and byte-range digests, never game bytes,
vertices, names, paths IDs, textures or decompiled code.
"""
import argparse
from collections import defaultdict
import gc
import hashlib
import json
from pathlib import Path
from scripts.mesh_source_files import serialized_sources, owned_objects

from scripts.extract_verified_raft_sources import extraction_plan


def merged_chunks(intervals, maximum=8 * 1024 * 1024):
    if maximum <= 0:
        raise ValueError('Positive range bound required')
    merged = []
    for offset, size in sorted(intervals):
        if type(offset) is not int or type(size) is not int or offset < 0 or size <= 0:
            raise ValueError('Invalid original stream range')
        end = offset + size
        if merged and offset <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([offset, end])
    result = []
    for start, end in merged:
        while start < end:
            size = min(maximum, end - start)
            result.append((start, size))
            start += size
    return result


def sha256_file(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def build(root, metadata):
    import UnityPy
    plan = extraction_plan(metadata)
    intervals = defaultdict(list)
    headers = {}
    mesh_count = streamed = selected = 0
    for path in serialized_sources(root):
        identity = plan['Raft/Raft_Data/' + path.name]
        actual = sha256_file(path)
        if path.stat().st_size != identity['size']:
            raise ValueError('Original source header size changed')
        if identity['algorithm'] == 'sha256' and actual != identity['digest']:
            raise ValueError('Original source header SHA256 mismatch')
        if identity['algorithm'] == 'git-sha1':
            digest = hashlib.sha1(b'blob ' + str(identity['size']).encode() + b'\0')
            with path.open('rb') as source:
                for block in iter(lambda: source.read(1024 * 1024), b''):
                    digest.update(block)
            if digest.hexdigest() != identity['digest']:
                raise ValueError('Original source header Git identity mismatch')
        headers[path.name] = {'size': identity['size'], 'sha256': actual}
        environment = UnityPy.load(str(path))
        for obj in owned_objects(environment):
            if obj.type.name != 'Mesh':
                continue
            mesh_count += 1
            tree = obj.read_typetree()
            stream = tree.get('m_StreamData') or {}
            reference = stream.get('path') or stream.get('m_Path') or ''
            size = int(stream.get('size') or stream.get('m_Size') or 0)
            offset = int(stream.get('offset') if stream.get('offset') is not None else stream.get('m_Offset', 0))
            if not reference or size <= 0:
                continue
            streamed += 1
            if Path(reference).name != reference or '\\' in reference:
                raise ValueError('Unsupported original stream path')
            expected = plan.get('Raft/Raft_Data/' + reference)
            if expected is None or offset < 0 or offset + size > expected['size']:
                raise ValueError('Original stream range exceeds verified source')
            if expected['algorithm'] != 'sha256':
                continue  # Ordinary Git streams are already present in normal checkout.
            intervals[reference].append((offset, size))
            selected += 1
        del environment
        gc.collect()
    streams = {}
    for name, spans in sorted(intervals.items()):
        expected = plan['Raft/Raft_Data/' + name]
        path = root / name
        if path.stat().st_size != expected['size'] or sha256_file(path) != expected['digest']:
            raise ValueError('Full private original stream does not match Git LFS identity')
        chunks = []
        with path.open('rb') as source:
            for offset, size in merged_chunks([(0, expected['size'])] if name.startswith('level') else spans):
                source.seek(offset)
                raw = source.read(size)
                if len(raw) != size:
                    raise ValueError('Unexpected EOF in verified original stream')
                chunks.append({'offset': offset, 'size': size, 'sha256': hashlib.sha256(raw).hexdigest()})
        streams[name] = {'size': expected['size'], 'sha256': expected['digest'], 'chunks': chunks, 'restore_whole': name.startswith('level')}
        print('Verified aggregate Mesh ranges:', name, len(chunks), sum(c['size'] for c in chunks), flush=True)
    stats = {'source_headers': len(headers), 'source_meshes': mesh_count,
             'streamed_meshes': streamed, 'lfs_streamed_meshes': selected,
             'lfs_stream_providers': len(streams),
             'whole_scene_streams': sum(s['restore_whole'] for s in streams.values()),
             'verified_range_bytes': sum(c['size'] for s in streams.values() for c in s['chunks']),
             'full_source_stream_bytes': sum(s['size'] for s in streams.values())}
    return {'format': 1, 'max_chunk_bytes': 8 * 1024 * 1024,
            'headers': headers, 'streams': streams, 'statistics': stats}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.root, json.loads(args.metadata.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_MESH_RANGE_MANIFEST ' + json.dumps(result['statistics'], sort_keys=True))

