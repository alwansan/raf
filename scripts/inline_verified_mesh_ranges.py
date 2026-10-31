#!/usr/bin/env python3
"""Inline checksum-verified original Mesh buffers in staged serialized headers.

Only Mesh vertex bytes and their external stream descriptor change. Original
checkout files are not edited. Every original object/path ID, external reference,
unmodified object body and other Mesh field is checked after serialization;
all header outputs are validated before any staged source file is replaced.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
from scripts.mesh_source_files import SOURCE, owned_objects

from scripts.fetch_verified_mesh_ranges import validate_manifest, cache_path, read_cached


def assemble_range(stream_name, stream, offset, size, cache):
    if type(offset) is not int or type(size) is not int or offset < 0 or not 0 < size <= 256 * 1024 * 1024:
        raise ValueError('Unsupported original Mesh payload extent')
    result = bytearray()
    position, end = offset, offset + size
    if end > stream['size']:
        raise ValueError('Original Mesh range exceeds source extent')
    for chunk in stream['chunks']:
        start, stop = chunk['offset'], chunk['offset'] + chunk['size']
        if stop <= position:
            continue
        if start >= end:
            break
        if start > position:
            raise ValueError('Pinned ranges do not cover the entire original Mesh')
        raw = read_cached(cache_path(cache, stream_name, chunk), chunk)
        count = min(stop, end) - position
        result.extend(raw[position - start:position - start + count])
        position += count
        if position == end:
            break
    if position != end:
        raise ValueError('Original Mesh has an uncovered payload suffix')
    return bytes(result)


def mesh_identity(tree):
    cleaned = dict(tree)
    cleaned['m_VertexData'] = dict(tree['m_VertexData'])
    cleaned['m_VertexData'].pop('m_DataSize')
    cleaned.pop('m_StreamData')
    def encode(value):
        if isinstance(value, (bytes, bytearray)):
            return {'byte_sha256': hashlib.sha256(value).hexdigest(), 'byte_count': len(value)}
        raise TypeError('Unsupported original serialized value')
    return hashlib.sha256(json.dumps(cleaned, sort_keys=True, allow_nan=True,
        separators=(',', ':'), default=encode).encode()).hexdigest()


def inline_tree(tree, raw):
    stream = tree['m_StreamData']
    if set(stream) != {'path', 'offset', 'size'} or stream['size'] != len(raw):
        raise ValueError('Unexpected original Mesh stream descriptor')
    current = tree['m_VertexData']['m_DataSize']
    if current and current != raw:
        raise ValueError('Original Mesh already has conflicting inline vertex data')
    result = dict(tree)
    result['m_VertexData'] = dict(tree['m_VertexData'], m_DataSize=raw)
    result['m_StreamData'] = {'path': '', 'offset': 0, 'size': 0}
    if mesh_identity(result) != mesh_identity(tree):
        raise ValueError('Unexpected original Mesh field change')
    return result


def external_identity(file):
    return [(item.path, bytes(item.guid), item.type) for item in file.externals]


def prepare_whole_streams(root, manifest, cache, pending):
    restored = 0
    for name, stream in manifest['streams'].items():
        if not stream.get('restore_whole'):
            continue
        if not name.startswith('level'):
            raise ValueError('Whole restoration is limited to original scene streams')
        target = root / name
        if target.exists():
            with target.open('rb') as source:
                if target.stat().st_size != stream['size'] or hashlib.file_digest(source, 'sha256').hexdigest() != stream['sha256']:
                    raise ValueError('Conflicting original whole scene stream')
            continue
        temporary = target.with_name(name + '.mesh-inline-validated')
        if temporary.exists():
            raise FileExistsError('Whole-scene validation output already exists')
        pending.append((temporary, target))
        digest, written = hashlib.sha256(), 0
        with temporary.open('xb') as output:
            for chunk in stream['chunks']:
                if chunk['offset'] != written:
                    raise ValueError('Whole original scene stream has a gap')
                raw = read_cached(cache_path(cache, name, chunk), chunk)
                output.write(raw)
                digest.update(raw)
                written += len(raw)
        if written != stream['size'] or digest.hexdigest() != stream['sha256']:
            raise ValueError('Whole original scene stream identity mismatch')
        restored += 1
    return restored


def inline_headers(root, manifest, cache):
    import UnityPy
    validate_manifest(manifest)
    pending, total, verified_unchanged = [], 0, 0
    try:
        whole_streams = prepare_whole_streams(root, manifest, cache, pending)
        # Pin every original header before preparing any output.
        for name, identity in manifest['headers'].items():
            if Path(name).name != name or not SOURCE.fullmatch(name):
                raise ValueError('Unsafe serialized source header path')
            path = root / name
            if path.stat().st_size != identity['size']:
                raise ValueError('Staged original header size differs from pinned source')
            with path.open('rb') as source:
                if hashlib.file_digest(source, 'sha256').hexdigest() != identity['sha256']:
                    raise ValueError('Staged original header SHA256 mismatch')
        for name in sorted(manifest['headers']):
            path = root / name
            environment = UnityPy.load(str(path))
            file = environment.file
            original_ids = {obj.path_id: obj.type.value for obj in owned_objects(environment)}
            original_raw, modified = {}, {}
            references, version = external_identity(file), file.unity_version
            for obj in owned_objects(environment):
                original_raw[obj.path_id] = hashlib.sha256(obj.get_raw_data()).hexdigest()
                if obj.type.name != 'Mesh':
                    continue
                tree = obj.read_typetree()
                stream = tree.get('m_StreamData') or {}
                source_name = stream.get('path', '')
                if not source_name or not stream.get('size', 0):
                    continue
                if source_name not in manifest['streams']:
                    # Original ordinary-Git streams remain unchanged.
                    source = root / source_name
                    if Path(source_name).name != source_name or not source.is_file() or source.stat().st_size < 200:
                        raise ValueError('Unknown or unresolved external original Mesh stream')
                    continue
                raw = assemble_range(source_name, manifest['streams'][source_name],
                                     stream['offset'], stream['size'], cache)
                modified[obj.path_id] = {'identity': mesh_identity(tree), 'size': len(raw),
                                        'sha256': hashlib.sha256(raw).hexdigest()}
                obj.save_typetree(inline_tree(tree, raw))
            if not modified:
                verified_unchanged += len(original_raw)
                del environment, file
                gc.collect()
                continue
            temporary = path.with_name(path.name + '.mesh-inline-validated')
            if temporary.exists():
                raise FileExistsError('Staged inline-validation output already exists')
            pending.append((temporary, path))
            with temporary.open('xb') as output:
                output.write(file.save())
            check = UnityPy.load(str(temporary))
            if ({obj.path_id: obj.type.value for obj in owned_objects(check)} != original_ids or
                    external_identity(check.file) != references or check.file.unity_version != version):
                raise ValueError('Original object IDs/types/version/external references changed')
            for obj in owned_objects(check):
                if obj.path_id not in modified:
                    if hashlib.sha256(obj.get_raw_data()).hexdigest() != original_raw[obj.path_id]:
                        raise ValueError('An unmodified original serialized object changed')
                    verified_unchanged += 1
                    continue
                tree = obj.read_typetree()
                expected = modified[obj.path_id]
                data = tree['m_VertexData']['m_DataSize']
                if (mesh_identity(tree) != expected['identity'] or len(data) != expected['size'] or
                        hashlib.sha256(data).hexdigest() != expected['sha256'] or
                        tree['m_StreamData'] != {'path': '', 'offset': 0, 'size': 0}):
                    raise ValueError('Original Mesh identity or verified payload changed on round-trip')
            total += len(modified)
            print('Validated original header Mesh payloads:', name, len(modified), flush=True)
            del check, environment, file
            gc.collect()
        if total != manifest['statistics']['lfs_streamed_meshes']:
            raise ValueError('Not every pinned original LFS Mesh was restored')
        for temporary, path in pending:
            os.replace(temporary, path)
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)
    report = {'inlined_original_meshes': total, 'verified_unchanged_original_objects': verified_unchanged,
              'verified_whole_scene_streams_restored': whole_streams,
              'original_object_ids_and_external_references_unchanged': True,
              'fabricated_whole_stream_files': 0}
    print('RAFT_ORIGINAL_MESH_STREAM_INLINE ' + json.dumps(report, sort_keys=True), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    inline_headers(args.root, json.loads(args.manifest.read_text()), args.cache)

