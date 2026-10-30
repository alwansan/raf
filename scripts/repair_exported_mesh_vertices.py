#!/usr/bin/env python3
"""Restore only verified vertex payload fields in an ephemeral original export.

Never copy provider .meta files or GUIDs. Refuse geometry-identity mismatches,
ambiguous exported names, unsupported fields and non-finite provider positions
before writing any target. Caller must validate the original LFS source first.
"""
import argparse
import json
from pathlib import Path
import re
import shutil

from scripts.compare_exported_mesh_geometry import positions, load_mesh_yaml


def load_mesh(text):
    return load_mesh_yaml(text)


def geometry_identity(tree):
    data = tree['m_VertexData']
    return (tree['m_Name'], data['m_VertexCount'], data['m_Channels'],
            tree.get('m_IndexFormat'), tree.get('m_IndexBuffer'), tree.get('m_SubMeshes'))


def replace_payload(text, provider):
    """Replace exactly two scalar lines inside the existing VertexData block."""
    data = provider['m_VertexData']
    encoded = data['_typelessdata']
    raw = bytes.fromhex('' if encoded is None else str(encoded))
    if not raw or data['m_DataSize'] != len(raw):
        raise ValueError('Provider vertex byte count is inconsistent')
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if re.fullmatch(r' +m_VertexData:\s*\n?', line)]
    if len(starts) != 1:
        raise ValueError('Expected one original VertexData block')
    start = starts[0]
    indentation = len(lines[start]) - len(lines[start].lstrip(' '))
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and len(line) - len(line.lstrip(' ')) <= indentation:
            break
        end += 1
    values = {'m_DataSize': str(len(raw)), '_typelessdata': raw.hex()}
    changed = {key: 0 for key in values}
    for i in range(start + 1, end):
        match = re.match(r'^( +)(m_DataSize|_typelessdata):[^\r\n]*(\r?\n)?$', lines[i])
        if match:
            key = match[2]
            if len(match[1]) != indentation + 2:
                raise ValueError('Unexpected vertex scalar nesting')
            changed[key] += 1
            lines[i] = match[1] + key + ': ' + values[key] + (match[3] or '')
    if any(count != 1 for count in changed.values()):
        raise ValueError('Expected one size and one typeless-data scalar')
    return ''.join(lines)


def index_export(project, wanted):
    result = {}
    for path in sorted((project / 'Assets/Mesh').glob('*.asset')):
        text = path.read_bytes().decode('utf8')
        tree = load_mesh(text)
        name = tree.get('m_Name')
        if name not in wanted:
            continue
        if name in result:
            raise ValueError('Ambiguous original Mesh name; cannot safely pair exports')
        result[name] = (path, text, tree)
    if set(result) != set(wanted):
        raise ValueError('Not all original Mesh names were exported')
    return result


def repair(target, provider, wanted, snapshot):
    if snapshot.exists():
        raise ValueError('Snapshot destination already exists')
    originals = index_export(target, wanted)
    providers = index_export(provider, wanted)
    plans = []
    import math
    for name in sorted(wanted):
        path, text, tree = originals[name]
        _, _, recovered = providers[name]
        if geometry_identity(tree) != geometry_identity(recovered):
            raise ValueError('Vertex layout, indices or original submesh identity changed')
        values = positions(recovered)
        if not all(all(math.isfinite(v) for v in vertex) for vertex in values):
            raise ValueError('Provider contains non-finite positions')
        modified = replace_payload(text, recovered)
        checked = load_mesh(modified)
        if geometry_identity(checked) != geometry_identity(tree) or positions(checked) != values:
            raise ValueError('Vertex-only restoration did not retain original geometry identity')
        meta = path.with_suffix('.asset.meta')
        payload = meta.read_bytes()
        plans.append((path, modified.encode('utf8'), meta, payload))
    # Every provider/target is validated before snapshot creation or asset writes.
    for path, _, meta, _ in plans:
        destination = snapshot / path.relative_to(target)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        shutil.copy2(meta, destination.with_suffix('.asset.meta'))
    for path, payload, _, _ in plans:
        path.write_bytes(payload)
    if any(meta.read_bytes() != expected for _, _, meta, expected in plans):
        raise RuntimeError('Original meta bytes changed during vertex restoration')
    report = {'restored_meshes': len(plans), 'original_meta_bytes_unchanged': True,
              'original_vertex_layout_indices_submeshes_unchanged': True,
              'copied_provider_meta_files': 0}
    print('RAFT_VERTEX_PAYLOAD_RESTORATION ' + json.dumps(report, sort_keys=True))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--provider', type=Path, required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--stream', choices=['sharedassets24.assets.resS'], required=True)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    rows = [r for p in ledger['providers'] if p['stream'] == args.stream for r in p['meshes']]
    if not rows or any(r['ambiguous_name'] for r in rows):
        raise SystemExit('Only unambiguous original source identities can be restored')
    wanted = {r['mesh_name'] for r in rows}
    repair(args.target, args.provider, wanted, args.snapshot)
